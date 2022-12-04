import gc
import ipaddress
import json
import os
import time

import adafruit_ntp
import adafruit_requests
import microcontroller
import rtc
import socketpool
from adafruit_httpserver import HTTPResponse, HTTPServer

import wifi
from config import CONFIG

web = None


class Web:
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
    TZ_OFFSET_PDT = -7

    def __init__(self, ssid=None, password=None):
        # Queue filled by POST route handler and drained by get_click()
        self.web_clicks = []
        self.__device_registered = False
        self.__connected = False

        self.diag_data = None
        self.ssid = ssid or os.getenv(CONFIG.WIFI_SSID_ENV)
        self.password = password or os.getenv(CONFIG.WIFI_PASSWORD_ENV)
        self.server = None

        if not self.ssid or not self.password:
            print(
                f"ERROR: Please export {CONFIG.WIFI_SSID_ENV}, {CONFIG.WIFI_PASSWORD_ENV} using .env file"
            )
        else:
            try:
                gc.collect()
                self.pool = self.__init_wifi()
                gc.collect()
                self.server = self.__init_server()
                gc.collect()
                self.__connected = True
            except Exception as e:
                if self.pool:
                    print(f"Failed starting server on ssid {self.ssid}", e)
                else:
                    print(f"Failed connecting to ssid {self.ssid}", e)

    def set_diag(self, diag_data):
        self.diag_data = diag_data

    def __init_wifi(self):
        print(f"Connecting to {self.ssid} ...")
        wifi.radio.connect(self.ssid, self.password)
        print(f"Connected {self.ssid}")
        print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
        print("My IP address is", wifi.radio.ipv4_address)
        return socketpool.SocketPool(wifi.radio)  # TODO Check arg

    def __init_server(self):
        http_server = HTTPServer(self.pool)
        try:
            print(f"Starting server on {wifi.radio.ipv4_address} ...")
            http_server.start(str(wifi.radio.ipv4_address))
            print(f"Listening on http://{wifi.radio.ipv4_address}:80")
        except OSError as e:
            print(f"Failed starting server ...", e)
            if self.RESTART_ON_WIFI_ERROR:
                print(f"Restarting in {self.WIFI_RESTART_WAIT_SECS} secs ...")
                time.sleep(self.WIFI_RESTART_WAIT_SECS)
                microcontroller.reset()
        return http_server

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
        print(f"Ping google.com: {ping_ms} ms")

    def get(self, url):
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

    def get_click(self):
        if self.web_clicks:
            return self.web_clicks.pop()

    def put_click(self, web_click):
        self.web_clicks.append(web_click)

    def register_device(self):
        app_server = os.getenv(CONFIG.APP_API_SERVER_ENV)
        if not app_server:
            print(
                f"ERROR: Cannot register device, please export {CONFIG.APP_API_SERVER_ENV} using .env"
            )
            return
        url = f"http://{app_server}/device/register/{wifi.radio.ipv4_address}"
        r = self.get(url)
        if r and "ok" in r.lower():
            self.__device_registered = True

    def get_server(self):
        return self.server

    def get_diag_data(self):
        return self.diag_data

    def sync_time(self):
        try:
            print(time.localtime())
            ntp = adafruit_ntp.NTP(self.pool, tz_offset=self.TZ_OFFSET_PDT)
            rtc.RTC().datetime = ntp.datetime
            print(time.localtime())
        except Exception as e:
            print("Failed syncing time", e)


def get_web_instance():
    # Using a global instance
    # since HTTPServer routes has to defined outside the class
    # using server member variable from the Web class
    global web
    if not web:
        web = Web()
    return web


web = get_web_instance()
server = get_web_instance().get_server()


@server.route("/")
def index(request):
    return HTTPResponse(content_type="text/html", body="thamburu")


@server.route("/ping")
def index(request):
    print("ping")
    return HTTPResponse(content_type="text/html", body="pong")


@server.route("/diag")
def diag(request):
    return HTTPResponse(content_type="text/html", body=json.dumps(web.get_diag_data()))


@server.route("/chord/0", "POST")
def click(request):
    web.put_click(0)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/1", "POST")
def click(request):
    web.put_click(1)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/2", "POST")
def click(request):
    web.put_click(2)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/3", "POST")
def click(request):
    web.put_click(3)
    return HTTPResponse(content_type="text/html", body="ok")


@server.route("/chord/4", "POST")
def click(request):
    web.put_click(4)
    return HTTPResponse(content_type="text/html", body="ok")
