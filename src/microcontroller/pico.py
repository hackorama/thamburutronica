import array
import gc
import math
import os
import sys
import time

import adafruit_mpr121
import adafruit_rgbled
import adafruit_tpa2016
import audiocore
import audiomixer
import audiomp3
import audiopwmio
import board
import busio
import digitalio
import microcontroller
import sdcardio
import simpleio
import storage

from config import CONFIG


class Pico:
    """
    The MCU specific driver implementation for Pico W MCU

      - Process events from click and touch input
      - Activate MCU connected functions
      - Play audio, Change audio gain, Activate LED, Sleep/Wake device etc.

    This interface can be ported to support other MCU like Arduino
    """

    NEO_PIXEL_PIN = board.GP28  # NOTE: shared with rgb LED
    AUDIO_PIN = board.GP18

    LED_RED_PIN = board.GP16
    LED_GREEN_PIN = board.GP17
    LED_BLUE_PIN = board.GP28  # NOTE: shared with on-board neo pixel
    LED_COMMON_ANODE = False

    # AMP and TOUCH devices on different I2C bus
    # AMP on bus 0 and TOUCH on bus 1

    TOUCH_CLOCK_PIN = board.GP7  # SCL1 I2C bus 1
    TOUCH_DATA_PIN = board.GP6  # SDA1 I2C bus1

    AMP_CLOCK_PIN = board.GP9  # SCL0 I2C bus 0
    AMP_DATA_PIN = board.GP8  # SDA0 I2C bus 0
    AMP_INITIAL_GAIN = CONFIG.GAIN_DEFAULT
    AMP_MAX_GAIN = CONFIG.GAIN_MAX
    AMP_MONO = True  # Enable only Left channel
    AMP_SHUTDOWN_ON_SLEEP = False

    USE_MIXER = False  # Level gain control only in mixer

    SD_CLOCK_PIN = board.GP10  # CLK SCK1
    SD_MAIN_OUT_PIN = board.GP11  # CMS SDO1
    SD_MAIN_IN_PIN = board.GP12  # DAT0 SDI1
    SD_CHIP_SELECT_PIN = board.GP15  # CD/DAT3 CSn1

    BUTTON_PINS = [board.GP20, board.GP21, board.GP22]
    BUTTON_ACTIVE_LOW_PULL_DOWN = True

    TOUCH_INPUT_RANGE = CONFIG.TOUCH_BUTTON_COUNT
    TOUCH_SCAN_DELAY_SECS = CONFIG.EVENT_LOOP_SECS
    SD_MOUNT = "/sd"
    BEEP_MP3_FILE = "beep.mp3"  # on board storage, not SD
    INIT_MP3_FILE = BEEP_MP3_FILE  # on board storage, not SD
    BEEP_DURATION_SECS = 1
    BEEP_TONE_FREQ = CONFIG.BEEP_FREQ  # Note C
    BEEP_USING_BUZZER = False

    def __init__(self, silent=False, debug=False):
        self.sd_mounted = False
        self.neo_pixel = None
        self.rgb_led = None
        self.led_color_r = 0
        self.led_color_g = 0
        self.led_color_b = 0
        self.audio_out = None
        self.mp3_decoder = None
        # TODO Use an array of decoders to support multiple secondary channels
        self.mp3_decoder_secondary = None
        self.mixer = None
        self.touch_i2c = None
        self.touch_mpr121 = None
        self.amp_i2c = None
        self.amp_tpa = None
        self.silent = silent
        self.debug = debug
        self.switches = []

        self.__init_audio()
        gc.collect()
        self.__init_touch()
        gc.collect()
        self.__init_switches()
        gc.collect()
        self.__mount_sdcard()
        gc.collect()
        self.__init_led()
        gc.collect()
        self.__init_amp()
        gc.collect()

    def __init_touch(self):
        if not self.touch_i2c:
            self.touch_i2c = busio.I2C(self.TOUCH_CLOCK_PIN, self.TOUCH_DATA_PIN)
        if not self.touch_mpr121:
            self.touch_mpr121 = adafruit_mpr121.MPR121(
                self.touch_i2c
            )  # Using address MPR121(i2c, address=0x91)

    def __init_neopixel(self):
        if not CONFIG.RESTRICT_MEMORY and not self.neo_pixel:
            import neopixel  # Late import to save memory

            self.neo_pixel = neopixel.NeoPixel(
                self.NEO_PIXEL_PIN, 1, brightness=0.5, auto_write=True
            )

    def __init_rgb_led(self):
        if not self.rgb_led:
            try:
                self.rgb_led = adafruit_rgbled.RGBLED(
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
        if not self.rgb_led:  # fall back to on board led
            self.__init_neopixel()

    def __init_audio(self):
        if not self.audio_out:
            # quiescent_value 0x0000 0 = 0%, 0x8000 32768 = 100%, 0xFFFF 65535 = 200%
            self.audio_out = audiopwmio.PWMAudioOut(self.AUDIO_PIN, quiescent_value=0)
        if not self.mp3_decoder:
            # pre init decoder with any mp3 once and reuse
            mp3 = open(self.INIT_MP3_FILE, "rb")
            self.mp3_decoder = audiomp3.MP3Decoder(mp3)  # TODO buffer
        if CONFIG.AUDIO_CHANNELS > 1 and not self.mp3_decoder_secondary:
            # pre init decoder with any mp3 once and reuse
            mp3 = open(self.INIT_MP3_FILE, "rb")
            self.mp3_decoder_secondary = audiomp3.MP3Decoder(mp3)  # TODO buffer
        if self.USE_MIXER and not self.mixer:
            self.mixer = audiomixer.Mixer(
                voice_count=2,
                sample_rate=16000,
                channel_count=1,
                bits_per_sample=16,
                samples_signed=True,
            )

    def __init_amp(self):
        if not self.amp_i2c:
            self.amp_i2c = busio.I2C(self.AMP_CLOCK_PIN, self.AMP_DATA_PIN)
        if not self.amp_tpa:
            self.amp_tpa = adafruit_tpa2016.TPA2016(self.amp_i2c)
            if self.AMP_MONO:
                self.amp_tpa.speaker_enable_r = False
            self.set_gain(self.AMP_INITIAL_GAIN)

    def __init_switches(self):
        for pin in self.BUTTON_PINS:
            switch = digitalio.DigitalInOut(pin)
            self.switches.append(switch)

    def __mount_sdcard(self):
        if self.sd_mounted:
            return
        # TODO SD_CLOCK_PIN, MOSI=SD_MAIN_IN_PIN, MISO=SD_MAIN_OUT_PIN
        spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
        sd = sdcardio.SDCard(spi, self.SD_CHIP_SELECT_PIN)
        vfs = storage.VfsFat(sd)  # TODO Check type
        storage.mount(vfs, self.SD_MOUNT)
        if self.debug:
            print(os.listdir(self.SD_MOUNT))
        self.sd_mounted = True

    def set_led(self, r=0, g=0, b=0):
        if self.rgb_led:
            self.led_color_r = r
            self.led_color_g = g
            self.led_color_b = b
            self.rgb_led.color = (self.led_color_r, self.led_color_g, self.led_color_b)
        if self.neo_pixel:
            # TODO FIXME Better normalising of color values for rgb LED and neopixel
            self.led_color_r = r / 10
            self.led_color_g = g / 10
            self.led_color_b = b / 10
            self.neo_pixel[0] = (self.led_color_r, self.led_color_g, self.led_color_b)
            self.neo_pixel.show()

    def get_led(self):
        return self.led_color_r, self.led_color_g, self.led_color_b

    def beep(self, duration_secs=None, tone_freq=None, mp3_file=None):
        if self.silent:
            return
        if self.BEEP_USING_BUZZER:
            if not duration_secs:
                duration_secs = self.BEEP_DURATION_SECS
            if not tone_freq:
                tone_freq = self.BEEP_TONE_FREQ
            simpleio.tone(self.AUDIO_PIN, tone_freq, duration_secs)
        else:
            if not mp3_file:
                mp3_file = self.BEEP_MP3_FILE
            self.play_mp3(mp3_file)

    def set_gain(self, db, channel=None):
        if self.USE_MIXER:
            # Max db is AMP_MAX_GAIN for tpa. Map (0 - AMP_MAX_GAIN) to 0 to 1
            level = 1 / (self.AMP_MAX_GAIN / db) if db else 0
            if channel is not None:
                self.mixer.voice[channel].level = level
            else:  # set all channels
                for i in range(CONFIG.AUDIO_CHANNELS - 1):
                    self.mixer.voice[i].level = level

        if self.amp_tpa:
            self.amp_tpa.fixed_gain = db

    def __play_audio(self, file, sample, channel=0, count=1):
        for i in range(count):
            print(f"Playing: {file} {i}/{count}")
            if self.USE_MIXER:
                self.audio_out.play(self.mixer)
                self.mixer.voice[channel].play(sample)
                # wait to finish if playing more than once
                while count > 1 and self.mixer.voice[channel].playing:
                    pass
            else:
                self.audio_out.play(sample)
                # wait to finish if playing more than once
                while count > 1 and self.audio_out.playing:
                    pass

    def play_mp3(self, audio_file, channel=0, count=1):
        if channel == 0:  # primary channel
            self.mp3_decoder.file = open(audio_file, "rb")
        else:  # TODO support multiple secondary channels using array of decoders
            self.mp3_decoder_secondary.file = open(audio_file, "rb")
        self.__play_audio(audio_file, self.mp3_decoder, channel, count)

    def play_wave(self, audio_file, channel=0, count=1):
        wave_file = open(audio_file, "rb")
        wave = audiocore.WaveFile(wave_file)  # TODO buffer
        self.__play_audio(audio_file, wave, channel, count)

    @staticmethod
    def __file_exists(path):
        try:
            os.stat(path)
            return True
        except Exception:
            pass
        return False

    def __resolve_storage_path(self, file):
        on_board_path = f"/{file}"
        if self.__file_exists(on_board_path):
            return on_board_path
        sd_path = f"{self.SD_MOUNT}/{file}"
        if self.__file_exists(sd_path):
            return sd_path
        print(f"ERROR: File not found on on-board storage or on sd card: {file}")
        return file

    def play(self, audio_file, channel=0, count=1):
        self.stop(channel)
        if audio_file.lower().endswith(".mp3"):
            self.play_mp3(self.__resolve_storage_path(audio_file), channel, count)
        elif audio_file.lower().endswith((".wav", ".wave")):
            self.play_wave(self.__resolve_storage_path(audio_file), channel, count)
        else:
            print(f"ERROR: Skipping unknown audio file type {audio_file}")

    def stop(self, channel=0):
        if self.USE_MIXER:
            if self.mixer.voice[channel].playing:
                print(f"Stopping audio on channel {channel}")
                self.mixer.voice[channel].stop()
        if self.audio_out.playing:
            print("Stopping audio")
            self.audio_out.stop()

    def play_generated_wave(self, duration_secs=1):
        frequency = 440
        length = 8000 // frequency
        tone_volume = 0.1
        sine_wave = array.array("H", [0] * length)
        for i in range(length):
            sine_wave[i] = int(
                math.sin(math.pi * 2 * i / length) * tone_volume * (2**15) + 2**15
            )
        sine_wave = audiocore.RawSample(sine_wave, sample_rate=8000)
        self.audio_out.play(sine_wave)
        time.sleep(duration_secs)  # TODO use non-blocking time.monotonic
        self.stop()

    def get_touches(self):
        touches = [False] * self.TOUCH_INPUT_RANGE
        for i in range(self.TOUCH_INPUT_RANGE):
            touches[i] = self.touch_mpr121[i].value
        return touches

    @staticmethod
    def __invert(value):
        return not value

    def get_clicks(self):
        clicks = [False] * len(self.switches)
        for i, switch in enumerate(self.switches):
            clicks[i] = switch.value

        if self.BUTTON_ACTIVE_LOW_PULL_DOWN:  # True == not pressed, False == pressed
            clicks = list(map(self.__invert, clicks))

        return clicks

    def check_storage(self, files):
        sd_files = os.listdir(self.SD_MOUNT)
        for file in files:
            if file not in sd_files:
                print(f"ERROR: {file} not found in {self.SD_MOUNT}")

    @staticmethod
    def __disk_size_mb(fs="/"):
        fs_stat = os.statvfs(fs)
        return fs_stat[0] * fs_stat[2] / 1024 / 1024

    @staticmethod
    def __free_disk_size_mb(fs="/"):
        fs_stat = os.statvfs(fs)
        return fs_stat[0] * fs_stat[3] / 1024 / 1024

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

    def mp3_level(self):
        if self.mp3_decoder:
            return self.mp3_decoder.rms_level
        return 0

    def diag(self):
        pins = dir(board)
        if "__class__" in pins:
            pins.remove("__class__")
        if "__name__" in pins:
            pins.remove("__name__")
        cpu_temp_degrees = microcontroller.cpu.temperature * (9 / 5) + 32
        mpr121_status = "ON" if self.touch_mpr121 else "OFF"
        tpa2016_status = "ON" if self.amp_tpa else "OFF"
        led_status = "OFF" if self.rgb_led else "OFF"
        result = {
            "Board id": board.board_id,
            "Board": os.uname().machine,
            "Chip": os.uname().sysname,
            "CircuitPython Release version": os.uname().version,
            "CPU temperature": cpu_temp_degrees,
            "Board pins": pins,
            "Board disk size MB": self.__disk_size_mb(),
            "Board disk free MB": self.__free_disk_size_mb(),
            "SD disk size MB": self.__disk_size_mb(self.SD_MOUNT),
            "SD disk free MB": self.__free_disk_size_mb(self.SD_MOUNT),
            "MPR121 touch sensor": mpr121_status,
            "TPA2016 audio amp module": tpa2016_status,
            "LED status": led_status,
            "LED config": f"R={self.LED_RED_PIN}, G={self.LED_GREEN_PIN}, B={self.LED_BLUE_PIN} COMMON ANODE={self.LED_COMMON_ANODE}",
        }
        if self.amp_tpa:
            result["TPA2016 audio amp gain"] = self.amp_tpa.fixed_gain
            result["TPA2016 audio amp max gain"] = self.amp_tpa.max_gain
            result[
                "TPA2016 audio amp compression_ratio"
            ] = self.amp_tpa.compression_ratio
            result["TPA2016 audio amp left"] = str(self.amp_tpa.speaker_enable_l)
            result["TPA2016 audio amp right"] = str(self.amp_tpa.speaker_enable_r)
            result["TPA2016 audio amp shutdown"] = str(self.amp_tpa.amplifier_shutdown)
        result["CircuitPython Modules"] = list(sys.modules.keys())
        return result
