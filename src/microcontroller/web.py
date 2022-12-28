import gc
import ipaddress
import json
import os
import time

try:
    from typing import List, Optional
except ImportError:
    pass  # No typing on device CircuitPython

import adafruit_ntp
import adafruit_requests
import rtc
import socketpool
import wifi
from adafruit_datetime import datetime
from adafruit_httpserver import HTTPResponse, HTTPServer

import microcontroller
from config import CONFIG

web = None


class Web:  # pylint: disable=too-many-instance-attributes
    """
    - Connects to specified Wi-Fi SSID:
       - Starts an HTTP server
       - Creates an HTTP client
       - Does NTP time sync and set RTC clock
    - Allows to register device IP with app server
    - Provides API endpoints for chord clicks from web UI

    Uses the SSID and app server host configured in .env file:
      WIFI_SSID = 'ssid'
      WIFI_PASSWORD = 'password'
      APP_API_SERVER = '192.168.x.y'

    NOTE: No HTTPS and auth enabled since both the device and server
          are on trusted local 192.168.0.0/16 network.
          Please enable them as required if deploying on external network

    TODO: Using http_server 0.5.4 with limited features and low memory use
          Switch to newer version with request params support when stable
    """

    def __init__(
        self,
        ssid: Optional[str] = None,
        password: Optional[str] = None,
        retries: int = 1,
    ) -> None:
        # Queue filled by POST route handler and drained by get_click()
        self.web_clicks: List[str] = []
        self.__device_registered = False
        self.__connected = False

        self.ssid = ssid or os.getenv(CONFIG.WIFI_SSID_ENV)
        self.password = password or os.getenv(CONFIG.WIFI_PASSWORD_ENV)
        self.server = None
        self.pool = None
        if not self.ssid or not self.password:
            print(
                f"ERROR: Please export {CONFIG.WIFI_SSID_ENV}, {CONFIG.WIFI_PASSWORD_ENV} using .env file"
            )
        else:
            try:
                self.pool = self.__init_wifi(retries)
                if self.pool:
                    self.server = self.__init_server(retries)
                if self.server:
                    self.__connected = True
            except Exception as e:
                if self.pool:
                    print(f"ERROR: Failed starting server on ssid {self.ssid}", e)
                else:
                    print(f"ERROR: Failed connecting to ssid {self.ssid}", e)

    def __init_wifi(self, max_retries: int = 1) -> Optional[socketpool.SocketPool]:
        retries = max_retries
        while retries:
            retries -= 1
            gc.collect()  # Wi-Fi init requires memory
            print(
                f"Connecting to {self.ssid} {max_retries - retries}/{max_retries} ..."
            )
            try:
                wifi.radio.connect(self.ssid, self.password)
                print(f"Connected as {wifi.radio.ipv4_address}")
                return socketpool.SocketPool(wifi.radio)
            except Exception as error:
                print(f"ERROR: Failed starting Wi-Fi on ssid {self.ssid}", error)
        return None

    def __init_server(self, max_retries: int = 1) -> Optional[HTTPServer]:
        retries = max_retries
        while retries:
            retries -= 1
            gc.collect()  # Wi-Fi init requires memory
            try:
                http_server = HTTPServer(self.pool)
                print(
                    f"Starting server on {wifi.radio.ipv4_address} {max_retries - retries}/{max_retries} ..."
                )
                http_server.start(str(wifi.radio.ipv4_address))
                print(f"Server listening on http://{wifi.radio.ipv4_address}:80")
                return http_server
            except Exception as error:
                print(f"ERROR: Failed starting server on ssid {self.ssid}", error)
                if CONFIG.WIFI_SYSTEM_RESTART_ON_ERROR:
                    print(
                        f"Restarting in {CONFIG.WIFI_SYSTEM_RESTART_WAIT_SECS} secs ..."
                    )
                    time.sleep(CONFIG.WIFI_SYSTEM_RESTART_WAIT_SECS)
                    # TODO FIXME Rename microcontroller package
                    microcontroller.reset()  # pylint: disable=no-member
                del http_server  # GC collection hint
        return None

    @property
    def device_registered(self) -> bool:
        return self.__device_registered

    @property
    def connected(self) -> bool:
        return self.__connected

    @staticmethod
    def ping(host: str) -> None:
        ipv4 = ipaddress.ip_address(host)
        ping_ms = wifi.radio.ping(ipv4) * 1000
        print(f"Ping google.com: {ping_ms} ms")

    def get(self, url: str) -> Optional[str]:
        print(f"GET {url} ...")
        requests = adafruit_requests.Session(self.pool)
        r = None
        try:
            r = requests.get(url)
            print(f"GET {url} -> {r.text}")
            return r.text
        except Exception as e:
            print(f"Failed connecting to {url}", e)
        finally:
            if r:
                r.close()
        return None

    def get_click(self) -> Optional[str]:
        if self.web_clicks:
            return self.web_clicks.pop()
        return None

    def put_click(self, web_click: str) -> None:
        self.web_clicks.append(web_click)

    def register_device(self) -> None:
        app_server = os.getenv(CONFIG.APP_API_SERVER_ENV)
        if not app_server:
            print(
                f"ERROR: Cannot register device, please export {CONFIG.APP_API_SERVER_ENV} using .env"
            )
            return
        url = f"http://{app_server}/device/register/{wifi.radio.ipv4_address}"
        try:
            response = self.get(url)
            if response and "ok" in response.lower():
                self.__device_registered = True
                print(f"Device {wifi.radio.ipv4_address} registered on {app_server}")
            else:
                print(f"Device registering failed with response = {response}")
        except Exception as error:
            print(f"Device registering failed with error {error}")

    def get_server(self) -> Optional[HTTPServer]:
        return self.server

    @staticmethod
    def get_device_metrics() -> int:
        # TODO no-member: Check CircuitPython lib stub issue ?
        mem_used = (
            gc.mem_alloc()  # type: ignore[attr-defined] # pylint: disable=no-member
        )
        mem_free = (
            gc.mem_free()  # type: ignore[attr-defined] # pylint: disable=no-member
        )
        mem_available = mem_used + mem_free
        mem_used_pct = int((mem_used / mem_available) * 100) if mem_available else 0
        return mem_used_pct

    def sync_time(self, max_retries: int = 1) -> bool:
        retries = max_retries
        tz_offset = int(os.getenv(CONFIG.NTP_TZ_OFFSET_ENV, "0"))  # Defaults to UTC/GM
        while retries:
            retries -= 1
            print(
                f"Trying NTP sync with {tz_offset} tz offset {max_retries - retries}/{max_retries} ..."
            )
            try:
                ntp = adafruit_ntp.NTP(
                    self.pool,
                    tz_offset=tz_offset,
                    socket_timeout=CONFIG.NTP_TIMEOUT_SECS,
                )
                rtc.RTC().datetime = ntp.datetime
                # IF time sync failed time will reset to chip epoch
                return int(datetime.now().year) > CONFIG.MCU_CHIP_EPOCH_YEAR
            except Exception as error:  # pylint: disable=broad-except
                print(f"Failed NTP sync with error {error}")
        return False


def get_web_instance() -> Optional[Web]:
    # Using a global instance since HTTPServer routes has to be defined
    # outside the class using server member variable from the Web class
    global web  # pylint: disable=global-statement
    if not web:
        web = Web(retries=CONFIG.WIFI_MAX_RETRIES)
    return web


web = get_web_instance()
server = get_web_instance().get_server()  # type: ignore[union-attr]


@server.route("/")  # type: ignore[union-attr]
def index(request):  # pylint: disable=unused-argument
    return HTTPResponse(content_type="text/html", body="thamburu")


@server.route("/ping")  # type: ignore[union-attr]
def ping(request):  # pylint: disable=unused-argument
    print("ping")
    return HTTPResponse(content_type="text/html", body="pong")


@server.route("/diag")  # type: ignore[union-attr]
def diag(request):  # pylint: disable=unused-argument
    return HTTPResponse(
        content_type="text/html", body=json.dumps(web.get_device_metrics())
    )


@server.route("/chord/0", "POST")  # type: ignore[union-attr]
def chord_zero(request):  # pylint: disable=unused-argument
    web.put_click(0)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/1", "POST")  # type: ignore[union-attr]
def chord_one(request):  # pylint: disable=unused-argument
    web.put_click(1)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/2", "POST")  # type: ignore[union-attr]
def chord_two(request):  # pylint: disable=unused-argument
    web.put_click(2)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/3", "POST")  # type: ignore[union-attr]
def chord_three(request):  # pylint: disable=unused-argument
    web.put_click(3)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/4", "POST")  # type: ignore[union-attr]
def chord_four(request):  # pylint: disable=unused-argument
    web.put_click(4)
    return HTTPResponse(content_type="text/html", body="ok")
