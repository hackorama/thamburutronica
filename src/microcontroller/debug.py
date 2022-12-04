import time

import board
import busio
from adafruit_espatcontrol import adafruit_espatcontrol

from config import CONFIG

if CONFIG.MCU_SUPPORTS_WIFI:
    from web import get_web_instance

from secrets import secrets

from pico import Pico
from wifi_esp import Client


def wifi_diag(connect=False):
    client = Client(secrets, debug=True)

    if connect:
        client.reset()
        client.connect()
        if client.ping("192.168.1.163"):
            client.get(
                "http://192.168.1.163/chord"
            )  # http://wifitest.adafruit.com/testwifi/index.html

    client.sleep()


def test_wifi():
    uart = busio.UART(board.GP16, board.GP17, receiver_buffer_size=2048)
    esp = adafruit_espatcontrol.ESP_ATcontrol(uart, 115200, debug=True)
    esp.soft_reset()
    for ap in esp.scan_APs():
        print(f"\t{ap}")
    esp.connect(secrets)
    print(esp.local_ip)
    print(esp.version)
    esp.ping("192.168.1.163")


def check_web_clicks():
    web = get_web_instance()
    web.get_server().poll()
    if not web.__device_registered():
        print("Register device ...")
        web.register_device()
    web_click = web.get_click()
    if web_click is not None:  # 0 is valid for unclick chord
        print(f"chord {web_click}")
    return web_click


def test_web_server():
    time_tracker = 0
    time_duration_secs = 0.25
    print("Test NTP ...")

    web = get_web_instance()
    web.sync_time()

    print("Start web server loop ...")

    while True:
        try:
            if time.monotonic() - time_tracker > time_duration_secs:
                time_tracker = time.monotonic()
                check_web_clicks()
        except KeyboardInterrupt:
            print("Exiting event loop and shutting down device")
            break


def test():
    pico = Pico()
    print(pico.diag())
    pico.set_led(20, 0, 0)


def test_gain():
    pico = Pico()
    pico.set_gain(16)
    pico.play_mp3("beep.mp3")
    time.sleep(3)
    pico.set_gain(30)
    pico.play_mp3("beep.mp3")
    time.sleep(3)
    pico.set_gain(1)
    pico.play_mp3("beep.mp3")
    time.sleep(3)
    pico.set_gain(0)
    pico.play_mp3("beep.mp3")
    time.sleep(3)
    pico.stop()


def test_mixer(music_file, drum_file, pin=board.GP18, wave=False):
    import audiocore
    import audiomixer
    import audiomp3
    import audiopwmio

    print("Testing audio mixer ...")

    a = audiopwmio.PWMAudioOut(pin)

    if wave:
        music = audiocore.WaveFile(open(music_file, "rb"))
        drum = audiocore.WaveFile(open(drum_file, "rb"))
    else:
        music_file = open(music_file, "rb")
        drum_file = open(drum_file, "rb")
        music = audiomp3.MP3Decoder(music_file)
        drum = audiomp3.MP3Decoder(drum_file)

    mixer = audiomixer.Mixer(
        voice_count=2,
        sample_rate=16000,
        channel_count=1,
        bits_per_sample=16,
        samples_signed=True,
    )
    a.play(mixer)
    mixer.voice[0].play(music)
    while mixer.playing:
        mixer.voice[1].play(drum)
        time.sleep(1)

    print("Done")
