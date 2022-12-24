import gc
import ipaddress
import json
import os
import time

import adafruit_ntp
import adafruit_requests
import rtc
import socketpool
import wifi
from adafruit_datetime import datetime
from adafruit_httpserver import HTTPResponse, HTTPServer, HTTPStatus
from util import disk_size_mb, free_disk_size_mb, isnumeric, log, memory_sweep

import microcontroller
from config import CONFIG

web = None  # pylint: disable=invalid-name


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
    """

    RESTART_ON_WIFI_ERROR = False
    WIFI_RESTART_WAIT_SECS = 5

    def __init__(self, ssid=None, password=None):
        # web clicks queue filled by POST route handler and drained by get_click()
        #
        # Web clicks format:
        #     0              Stop play
        #     1,2,3,4        Play chords
        #     CC1,CC0        Chime on/off
        #     CM1,CM2,CM3    Modes
        #     CV1 ... CV100  Volume 1 to 100
        #
        self.web_clicks = []
        self.ssid = ssid or os.getenv(CONFIG.WIFI_SSID_ENV)
        self.password = password or os.getenv(CONFIG.WIFI_PASSWORD_ENV)

        # latest play state as a compact csv string
        # LED=r:g:b,GAIN=0...10,AUDIO=name,PLAY_MODE=n,CHIME=0|1    Ex: 0:255:0,5,BEEP,2,1
        self.__play_state = "0:0:0,0,,1,0"
        self.__device_registered = False
        self.__connected = False
        self.pool = None
        self.server = None

        if not self.ssid or not self.password:
            log(
                f"ERROR: Please export {CONFIG.WIFI_SSID_ENV}, {CONFIG.WIFI_PASSWORD_ENV} using .env file"
            )
        else:
            try:
                memory_sweep()
                self.pool = self.__init_wifi()
                memory_sweep()
                self.server = self.__init_server()
                memory_sweep()
                self.__connected = True
            except Exception as error:  # pylint: disable=broad-except
                if self.pool:
                    log(f"Failed starting server on ssid {self.ssid} {error}")
                else:
                    log(f"Failed connecting to ssid {self.ssid} {error}")

    def __init_wifi(self):
        log(f"Connecting to {self.ssid} ...")
        wifi.radio.connect(self.ssid, self.password)
        log(f"Connected to {self.ssid} with IP {wifi.radio.ipv4_address}")
        return socketpool.SocketPool(wifi.radio)  # TODO Check arg

    def __init_server(self):
        http_server = HTTPServer(self.pool)
        try:
            log(f"Starting server on {wifi.radio.ipv4_address} ...")
            http_server.start(str(wifi.radio.ipv4_address))
            log(f"Listening on http://{wifi.radio.ipv4_address}:80")
        except OSError as error:
            log(f"Failed starting server {error}")
            if self.RESTART_ON_WIFI_ERROR:
                log(f"Restarting in {self.WIFI_RESTART_WAIT_SECS} secs ...")
                time.sleep(self.WIFI_RESTART_WAIT_SECS)
                microcontroller.reset()
        return http_server

    @property
    def play_state(self):
        return self.__play_state

    @play_state.setter
    def play_state(self, state):
        self.__play_state = state

    @property
    def device_registered(self):
        return self.__device_registered

    @property
    def connected(self):
        return self.__connected

    @staticmethod
    def ping(host):
        ipv4 = ipaddress.ip_address(host)
        ping_ms = wifi.radio.ping(ipv4) * 1000
        log(f"Ping {host}: {ping_ms} ms")

    def get(self, url):
        log(f"GET {url} ...")
        requests = adafruit_requests.Session(self.pool)
        response = None
        try:
            response = requests.get(url)
            log(f"GET {url} -> {response.text}")
            return response.text
        except Exception as error:  # pylint: disable=broad-except
            log(f"Failed connecting to {url} {error}")
        finally:
            if response:
                response.close()
        return None

    def get_click(self):
        if self.web_clicks:
            return self.web_clicks.pop()
        return None

    def put_click(self, web_click):
        self.web_clicks.append(web_click)

    def register_device(self):
        app_server = os.getenv(CONFIG.APP_API_SERVER_ENV)
        if not app_server:
            log(
                f"ERROR: Cannot register device, please export {CONFIG.APP_API_SERVER_ENV} using .env"
            )
            return
        url = f"http://{app_server}/device/register/{wifi.radio.ipv4_address}"
        try:
            response = self.get(url)
            if response and "ok" in response.lower():
                self.__device_registered = True
                log(f"Device {wifi.radio.ipv4_address} registered on {app_server}")
            else:
                log(f"Device registering failed with response = {response}")
        except Exception as error:  # pylint: disable=broad-except
            log(f"Device registering failed with error {error}")

    def get_server(self):
        return self.server

    def get_device_metrics(self):
        """
        Fetch the device metrics as a compact memory efficient string

        Metrics csv string format:
          CPU_TEMP,TOTAL_RAM_BYTES,AVAILABLE_RAM_PCT,MEM_USED_PCT, \
          DISK_SIZE,DISK_USED_PCT,SD_CARD_SIZE,SD_CARD_USED_PCT, \
          LED_R:LED_G:LED_B,AUDIO_GAIN,AUDIO_NAME,PLAY_MODE,CHIME_MODE

        :return: the metrics string
        """
        cpu_temp = microcontroller.cpu.temperature or 0

        # TODO no-member: check CircuitPython lib stub issue ?
        mem_used = gc.mem_alloc()  # pylint: disable=no-member
        mem_free = gc.mem_free()  # pylint: disable=no-member
        mem_available = mem_used + mem_free
        mem_available_pct = (
            int((mem_available / CONFIG.MCU_RAM_BYTES) * 100)
            if CONFIG.MCU_RAM_BYTES
            else 0
        )
        mem_used_pct = int((mem_used / mem_available) * 100) if mem_available else 0

        disk_size = disk_size_mb()
        disk_free = free_disk_size_mb()
        disk_free_pct = int((disk_free / disk_size) * 100) if disk_size else 0

        sd_size = disk_size_mb(CONFIG.SD_MOUNT)
        sd_free = free_disk_size_mb(CONFIG.SD_MOUNT)
        sd_free_pct = int((sd_free / sd_size) * 100) if sd_size else 0

        return f"{cpu_temp},{CONFIG.MCU_RAM_BYTES},{mem_available_pct},{mem_used_pct},{disk_size},{100 - disk_free_pct},{sd_size},{100 - sd_free_pct},{self.play_state}"

    def sync_time(self, max_retries=1):
        retries = max_retries
        while retries:
            retries -= 1
            log(f"Trying NTP sync {max_retries - retries}/{max_retries} ...")
            try:
                ntp = adafruit_ntp.NTP(
                    self.pool,
                    tz_offset=CONFIG.NTP_TZ_OFFSET,
                    socket_timeout=CONFIG.NTP_TIMEOUT_SECS,
                )
                rtc.RTC().datetime = ntp.datetime
                # if time sync failed time will reset to chip epoch
                return int(datetime.now().year) > CONFIG.MCU_CHIP_EPOCH_YEAR
            except Exception as error:  # pylint: disable=broad-except
                log(f"Failed NTP sync with error {error}")


def get_web_instance():
    # Using a global instance since HTTPServer routes has to be defined
    # outside the class using server member variable from the Web class
    global web  # pylint: disable=global-statement, invalid-name
    if not web:
        web = Web()
    return web


web = get_web_instance()
server = get_web_instance().get_server()

# Minimal route handlers with limited validation and error handling for private API
# within the limited features of adafruit_httpserver
#
# GET  /ping
# GET  /diag
# POST /chord/0|1|2|3|4


@server.route("/")
def index(request):  # pylint: disable=unused-argument
    return HTTPResponse(content_type="text/html", body=CONFIG.PROJECT_NAME)


@server.route("/ping")
def ping(request):  # pylint: disable=unused-argument
    log("Received app ping")
    return HTTPResponse(content_type="text/html", body="pong")


@server.route("/diag")
def diag(request):  # pylint: disable=unused-argument
    return HTTPResponse(
        content_type="text/html", body=json.dumps(web.get_device_metrics())
    )


@server.route("/chord/0", "POST")
def chord_0(request):  # pylint: disable=unused-argument
    web.put_click(0)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/1", "POST")
def chord_1(request):  # pylint: disable=unused-argument
    web.put_click(1)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/2", "POST")
def chord_2(request):  # pylint: disable=unused-argument
    web.put_click(2)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/3", "POST")
def chord_3(request):  # pylint: disable=unused-argument
    web.put_click(3)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/4", "POST")
def chord_4(request):  # pylint: disable=unused-argument
    web.put_click(4)
    return HTTPResponse(content_type="text/html", body="ok")


# The routes below do not work with adafruit_httpserver 0.5x
#
# TODO: adafruit_httpserver 0.5.x do not support request params
#       switch to adafruit_httpserver 1.x.x
#       on 0.8.x CircuitPython when stable
#       and does not have higher memory use that 0.5.x
#
# POST /chords?click=0|1|2|3|4  0...4
# POST /mode?id=0|1|2           CM0,CM1,CM2
# POST /volume?pct=0...100      CV0...CV100
# POST /chime/on                CC1
# POST /chime/off               CC0


@server.route("/chords", "POST")
def chord(request):
    if "click" in request.query_params:
        param = request.query_params["click"]
        if isnumeric(param):
            click = int(param)
            if 0 <= click <= 4:
                web.put_click(click)
                return HTTPResponse(content_type="text/html", body="ok")
    return HTTPResponse(
        content_type="text/html",
        status=HTTPStatus(400, "Invalid, valid values are click=0,1,2,3,4"),
        body="invalid",
    )


@server.route("/volume", "POST")
def volume(request):
    if "pct" in request.query_params:
        param = request.query_params["pct"]
        if isnumeric(param):
            volume_pct = int(param)
            if 0 <= volume_pct <= 100:
                web.put_click(f"CV{volume_pct}")
                return HTTPResponse(content_type="text/html", body="ok")
    return HTTPResponse(
        content_type="text/html",
        status=HTTPStatus(400, "Invalid, valid values are pct=CV1 ... CV100"),
        body="invalid",
    )


@server.route("/mode", "POST")
def mode(request):
    if "id" in request.query_params:
        param = request.query_params["id"]
        if isnumeric(param):
            mode_id = int(param)
            if 0 <= mode_id <= 2:
                web.put_click(f"CM{mode_id}")
                return HTTPResponse(content_type="text/html", body="ok")
    return HTTPResponse(
        content_type="text/html",
        status=HTTPStatus(400, "Invalid, valid values are id=CM0,CM1,CM2"),
        body="invalid",
    )


@server.route("/chime/on", "POST")
def chime_on(request):  # pylint: disable=unused-argument
    web.put_click("CC1")
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chime/off", "POST")
def chime_of(request):  # pylint: disable=unused-argument
    web.put_click("CC0")
    return HTTPResponse(content_type="text/html", body="ok")
