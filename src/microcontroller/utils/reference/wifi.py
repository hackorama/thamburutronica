import time

import adafruit_espatcontrol.adafruit_espatcontrol_socket as socket
import adafruit_requests as requests
import board
import busio
from adafruit_espatcontrol import adafruit_espatcontrol
from util import log


class Client:
    """
    NOTE: Only used if the MCU do not have on-board Wi-Fi support.

    Connects to specified Wi-Fi SSID using external ESP32 board:
      - Creates an HTTP client

    Uses the SSID configured in secrets.py file:
      secrets = {
          "ssid": "ssid",
          "password": "password",
      }
    """

    tx_pin = board.GP16
    rx_pin = board.GP17
    uart = None
    esp = None

    secrets = {}

    not_connected = True

    wifi_init_max_retry_duration_secs = 90
    wifi_init_retry_throttle_duration_secs = 0
    wifi_init_max_retries = 3

    request_connect_timeout_secs = 10
    request_max_retry_duration_secs = 30
    request_retry_throttle_duration_secs = 0
    request_max_retries = 3

    debug = False

    def __init__(self, secrets, debug=False):
        self.secrets = secrets
        self.debug = debug
        self.__init_esp()

    def __init_esp(self):
        log("Starting wifi module ...")
        self.uart = busio.UART(self.tx_pin, self.rx_pin, receiver_buffer_size=2048)
        self.esp = adafruit_espatcontrol.ESP_ATcontrol(self.uart, 115200, debug=False)
        requests.set_socket(socket, self.esp)

    @staticmethod
    def wait(duration_secs):
        if duration_secs:
            time_tracker = time.monotonic()
            while time.monotonic() - time_tracker > duration_secs:
                break

    @staticmethod
    def __is_within_duration(start, duration):
        return time.monotonic() - start < duration

    def __connect_wifi(self):
        retry_counter = self.wifi_init_max_retries
        retry_duration_start_sec = time.monotonic()
        while (
            self.not_connected
            and retry_counter
            and self.__is_within_duration(
                retry_duration_start_sec, self.wifi_init_max_retry_duration_secs
            )
        ):
            try:
                if self.debug:
                    log("Scanning wifi access points ...")
                    for ap in self.esp.scan_APs():  # pylint: disable=invalid-name
                        log(f"\t{ap}")
                log(f"Connecting to wifi ssid {self.secrets['ssid']} ...")
                self.esp.connect(self.secrets)
                log(f"Wifi IP {self.esp.local_ip}")
                log(f"Wifi version: {self.esp.version}")
                log(f"Wifi connected: {self.esp.is_connected}")
                self.not_connected = False
            except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as error:
                log(
                    f"Failed accessing wifi ssid {self.secrets['ssid']}, retrying {self.wifi_init_max_retries - retry_counter + 1}/{self.wifi_init_max_retries}: {error}"
                )
                self.wait(self.wifi_init_retry_throttle_duration_secs)
            retry_counter -= 1
        log(f"Wifi connected: {self.esp.is_connected}")

    def ping(self, host):
        log(f"ping {host} ...")
        try:
            msecs = self.esp.ping(host)
            log(f"Pinged {host} in {msecs} ms")
            return msecs
        except Exception as error:  # pylint: disable=broad-except
            log(f"Failed ping {host} {error}")
        return None

    def get(self, url):
        retry_counter = self.request_max_retries
        retry_duration_start_sec = time.monotonic()
        while retry_counter and self.__is_within_duration(
            retry_duration_start_sec, self.request_max_retry_duration_secs
        ):
            try:
                log(f"Connecting to {url} ...")
                response = requests.get(url, timeout=self.request_connect_timeout_secs)
                log(f"{url} -> {response.text}")
                return response.text
            except Exception as error:  # pylint: disable=broad-except
                log(
                    f"Failed accessing {url}, retrying {self.request_max_retries - retry_counter + 1}/{self.request_max_retries}: {error}"
                )
                self.wait(self.request_retry_throttle_duration_secs)
            retry_counter -= 1

    def sleep(self, duration_ms=0):
        if not duration_ms:
            log("Turning off wifi module, deep sleep")
        else:
            log(f"Turning off wifi module for {duration_ms} ms, deep sleep")
        self.esp.deep_sleep(duration_ms)

    def reset(self):
        log("Resetting wifi module ...")
        self.esp.soft_reset()

    def connect(self):
        log("Connecting wifi module ...")
        self.__connect_wifi()

    @staticmethod
    def device_status():
        return bool(Client.esp)

    @staticmethod
    def connection_status():
        return not Client.not_connected

    @staticmethod
    def device_version():
        if Client.esp:
            return Client.esp.version
        return None

    @staticmethod
    def device_ip():
        if Client.esp:
            return Client.esp.local_ip
        return None
