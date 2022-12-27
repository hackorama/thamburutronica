import gc
import os

import board
from adafruit_mpr121 import MPR121
from adafruit_rgbled import RGBLED
from adafruit_tpa2016 import TPA2016
from audiocore import WaveFile
from audiopwmio import PWMAudioOut
from busio import I2C, SPI
from sdcardio import SDCard
from storage import VfsFat, mount

from config import CONFIG


class Pico:  # pylint: disable=too-many-instance-attributes
    """
    The MCU specific driver implementation for Pi Pico W

      - Process events from click and touch input
      - Activate Pi Pico controlled functionalities
        - Play audio, Change audio gain, Activate LED, Sleep/Wake device etc.

    This interface can be ported to support other MCUs like Arduino
    """

    NEO_PIXEL_PIN = board.GP28  # NOTE: Shared with rgb LED
    AUDIO_PIN = board.GP18

    LED_RED_PIN = board.GP16
    LED_GREEN_PIN = board.GP17
    LED_BLUE_PIN = board.GP28  # NOTE: Shared with on-board neo pixel
    LED_COMMON_ANODE = False

    # AMP and TOUCH devices on different I2C bus
    # AMP on bus 0 and TOUCH on bus 1

    TOUCH_CLOCK_PIN = board.GP7  # SCL1 I2C bus 1
    TOUCH_DATA_PIN = board.GP6  # SDA1 I2C bus1

    AMP_CLOCK_PIN = board.GP9  # SCL0 I2C bus 0
    AMP_DATA_PIN = board.GP8  # SDA0 I2C bus 0
    AMP_MONO = True  # Enable only Left channel
    AMP_SHUTDOWN_ON_SLEEP = False

    SD_CLOCK_PIN = board.GP10  # CLK SCK1
    SD_MAIN_OUT_PIN = board.GP11  # CMS SDO1
    SD_MAIN_IN_PIN = board.GP12  # DAT0 SDI1
    SD_CHIP_SELECT_PIN = board.GP15  # CD/DAT3 CSn1

    BUTTON_PINS = [board.GP20, board.GP21, board.GP22]
    BUTTON_ACTIVE_LOW_PULL_DOWN = True

    def __init__(self, silent=False, debug=False):
        self.sd_mounted = False
        self.rgb_led = None
        self.led_color_r = 0
        self.led_color_g = 0
        self.led_color_b = 0
        self.audio_out = None
        self.touch_i2c = None
        self.touch_mpr121 = None
        self.amp_i2c = None
        self.amp_tpa = None
        self.silent = silent
        self.debug = debug
        self.buffer = None

        self.__init_audio()
        gc.collect()
        self.__init_touch()
        gc.collect()
        gc.collect()
        self.__mount_sdcard()
        gc.collect()
        self.__init_led()
        gc.collect()
        self.__init_amp()
        gc.collect()

    def __init_touch(self):
        if not self.touch_i2c:
            self.touch_i2c = I2C(self.TOUCH_CLOCK_PIN, self.TOUCH_DATA_PIN)
        if not self.touch_mpr121:
            self.touch_mpr121 = MPR121(
                self.touch_i2c
            )  # Using address MPR121(i2c, address=0x91)

    def __init_rgb_led(self):
        if not self.rgb_led:
            try:
                self.rgb_led = RGBLED(
                    self.LED_RED_PIN,
                    self.LED_GREEN_PIN,
                    self.LED_BLUE_PIN,
                    self.LED_COMMON_ANODE,
                )
            except Exception as e:
                print(
                    f"LED failed on pins {self.LED_RED_PIN}, {self.LED_GREEN_PIN}, {self.LED_BLUE_PIN}",
                    e,
                )

    def __init_led(self):
        self.__init_rgb_led()

    def __init_audio(self):
        if CONFIG.AUDIO_BUFFER_SIZE_BYTES:
            self.buffer = bytearray(CONFIG.AUDIO_BUFFER_SIZE_BYTES)
        if not self.audio_out:
            # quiescent_value 0x0000 0 = 0%, 0x8000 32768 = 100%, 0xFFFF 65535 = 200%
            self.audio_out = PWMAudioOut(self.AUDIO_PIN, quiescent_value=0)

    def __init_amp(self):
        if not self.amp_i2c:
            self.amp_i2c = I2C(self.AMP_CLOCK_PIN, self.AMP_DATA_PIN)
        if not self.amp_tpa:
            self.amp_tpa = TPA2016(self.amp_i2c)
            if self.AMP_MONO:
                self.amp_tpa.speaker_enable_r = False
            self.set_gain(CONFIG.AUDIO_GAIN_DEFAULT_DB)

    def __mount_sdcard(self):
        if self.sd_mounted:
            return
        # TODO SD_CLOCK_PIN, MOSI=SD_MAIN_IN_PIN, MISO=SD_MAIN_OUT_PIN
        spi = SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
        sd = SDCard(spi, self.SD_CHIP_SELECT_PIN)
        vfs = VfsFat(sd)
        mount(vfs, CONFIG.SD_MOUNT)
        if self.debug:
            print(os.listdir(CONFIG.SD_MOUNT))
        self.sd_mounted = True

    def set_led(self, r=0, g=0, b=0):
        if self.rgb_led:
            self.led_color_r = r
            self.led_color_g = g
            self.led_color_b = b
            self.rgb_led.color = (self.led_color_r, self.led_color_g, self.led_color_b)

    def set_led_rgb(self, rgb=(0, 0, 0)):
        self.set_led(rgb[0], rgb[1], rgb[2])

    def get_led(self):
        return self.led_color_r, self.led_color_g, self.led_color_b

    def beep(self, audio_file=None):
        if self.silent:
            return
        if not audio_file:
            audio_file = CONFIG.AUDIO_BEEP_FILE
        self.play(self.__resolve_storage_path(audio_file))

    def set_gain(self, db):
        if self.amp_tpa:
            self.amp_tpa.fixed_gain = db

    def __play_audio(self, file, sample, count=1):
        for i in range(count):
            print(f"Playing: {file} {i+1}/{count}")
            self.audio_out.play(sample)
            # Wait to finish if playing more than once
            while count > 1 and self.audio_out.playing:
                pass

    def play_wave(self, audio_file, count=1):
        if self.buffer:
            wave = WaveFile(audio_file, self.buffer)
        else:
            wave = WaveFile(audio_file)
        self.__play_audio(audio_file, wave, count)

    @staticmethod
    def __file_exists(path):
        try:
            os.stat(path)
            return True
        except Exception:
            pass
        return False

    def __resolve_storage_path(self, file):
        on_board_path = f"{file}"
        if self.__file_exists(on_board_path):
            return on_board_path
        sd_path = f"{CONFIG.SD_MOUNT}/{file}"
        if self.__file_exists(sd_path):
            return sd_path
        print(f"ERROR: File not found on on-board storage or on sd card: {file}")
        return None

    def play(self, audio_file, count=1):
        self.stop()
        if audio_file.lower().endswith(".wav"):
            file_path = self.__resolve_storage_path(audio_file)
            if file_path:
                self.play_wave(file_path, count)
            else:
                print(f"ERROR: Cannot play missing audio fle {audio_file}")
        else:
            print(f"ERROR: Skipping unknown audio file type {audio_file}")

    def stop(self):
        if self.audio_out.playing:
            print("Stopping audio")
            self.audio_out.stop()

    def get_touches(self):
        touches = [False] * CONFIG.TOUCH_BUTTON_COUNT
        for i in range(CONFIG.TOUCH_BUTTON_COUNT):
            touches[i] = self.touch_mpr121[i].value
        return touches

    @staticmethod
    def check_storage(files):
        result = True
        sd_files = os.listdir(CONFIG.SD_MOUNT)
        for file in files:
            if file not in sd_files:
                print(f"ERROR: {file} not found in {CONFIG.SD_MOUNT}")
                result = False
        return result

    def sleep(self):
        self.amp_tpa.speaker_enable_l = False
        self.amp_tpa.speaker_enable_r = False
        if self.AMP_SHUTDOWN_ON_SLEEP:
            self.amp_tpa.amplifier_shutdown = True

    def wake(self):
        if self.AMP_SHUTDOWN_ON_SLEEP:
            self.amp_tpa.amplifier_shutdown = False
        self.amp_tpa.speaker_enable_l = True
        if not self.AMP_MONO:
            self.amp_tpa.speaker_enable_r = True

    def audio_playing(self):
        return self.audio_out.playing
