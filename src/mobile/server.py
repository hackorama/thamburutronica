import logging
from typing import Dict, List, Optional

import requests
import uvicorn
from fastapi import FastAPI, Response, status
from fastapi.staticfiles import StaticFiles

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEVICE_HOST_ENV = "DEVICE_HOST"
DEVICE_HOST_FILE = "DEVICE_HOST"
REQUEST_TIMEOUT_SECS = 30
CHORD_COUNT = 4
DEFAULT_METRICS = ["0", "0", "0", "0", "0", "0", "0", "0", "0:0:0", "0", "", "0", "0"]

DATA_STORE: Dict[str, str] = {}  # in memory store, use with single worker process

app = FastAPI()

"""
Simple REST API server for:
 - Device can register the device IP
 - Web UI can send the chord clicks
 - Proxies the chord clicks from web UI to the device
 - Also serves the web UI static resources to the browser

NOTE: No HTTPS and auth enabled since both the device and server
      are on trusted local 192.168.0.0/16 network.
      Please enable them as required if deploying on external network
"""


def get_value(key: str) -> Optional[str]:
    return DATA_STORE.get(key)


def set_value(key: str, value: str) -> None:
    DATA_STORE[key] = value


def get_env_device_host() -> Optional[str]:
    return get_value(DEVICE_HOST_ENV)


def set_env_device_host(host: str) -> None:
    set_value(DEVICE_HOST_ENV, host)


def store_device_host(host: str) -> None:
    set_env_device_host(host)
    try:
        with open(DEVICE_HOST_FILE, "w", encoding="utf-8") as file:
            logger.info(f"write {host} -> {DEVICE_HOST_FILE}")
            file.write(host)
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"Failed writing device host {host} to {DEVICE_HOST_FILE}")


def read_device_host() -> Optional[str]:
    host = get_env_device_host()
    if host:
        return host
    try:
        with open(DEVICE_HOST_FILE, "r+", encoding="utf-8") as file:
            host = file.read()
            set_env_device_host(host)
            logger.info(f"read {DEVICE_HOST_FILE} -> {host}")
            return host
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"Failed reading device host from {DEVICE_HOST_FILE}")
    return None


def device_post(path: str) -> str:
    host = read_device_host()
    if not host:
        return "No device registered"
    url = f"http://{host}/{path}"
    try:
        logger.info(f"Device POST {url}")
        response = requests.post(url, timeout=REQUEST_TIMEOUT_SECS)
        logger.debug(response.text)
        logger.debug(response.status_code)
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"POST failed connecting to device {host}")
        return "No device connection"
    return response.text


def device_get(path: str) -> str:
    host = read_device_host()
    if not host:
        return "No device registered"
    url = f"http://{host}/{path}"
    try:
        logger.info(f"Device GET {url}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECS)
        logger.debug(response.text)
        logger.debug(response.status_code)
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"GET failed connecting to device {host}")
        return "No device connection"
    return response.text


def rgb_as_hex(rgb: str) -> str:
    values = rgb.split(":")
    return f"{int(values[0]):02x}{int(values[1]):02x}{int(values[2]):02x}"


def format_device_memory_status(usage_pct: str) -> str:
    pct = int(float(usage_pct.strip('"')))
    set_value("MEM_MIN", str(min(pct, int(get_value("MEM_MIN") or pct))))
    set_value("MEM_MAX", str(max(pct, int(get_value("MEM_MAX") or pct))))
    return f"Memory Usage {pct}% {get_value('MEM_MIN') or pct}-{get_value('MEM_MAX') or pct}"


def format_device_status(metrics: List[str]) -> str:
    #
    cpu = round(float(metrics[0].strip('"')), 2)
    disk_usage = round(float(metrics[5]))
    sd_usage = round(float(metrics[7]))
    rgb_hex = rgb_as_hex(metrics[8])
    vol = round(float(metrics[9]))
    file = metrics[10]
    chime = "ON" if int(metrics[12]) > 0 else "OFF"
    return (
        f"CPU {cpu}\u00B0C MEM {metrics[3]}% DISK {disk_usage}% SD {sd_usage}%"
        f'</br>LED <font style="color: #{rgb_hex};">&#9679</font> VOL {vol}% MODE {metrics[11]} CHIME {chime} '
        f"</br>{file}"
    )


@app.get("/health", status_code=200)
async def health() -> str:
    return "OK"


@app.get("/device/register/{host}", status_code=200)
async def device_register(host: str) -> str:
    store_device_host(host)
    return f"{host} ok"


@app.get("/device/ping", status_code=200)
async def device_ping(response: Response) -> str:
    device_response = device_get("ping") or "error"
    logger.info(f"device ping -> {device_response}")
    if device_response != "pong":
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
    return device_response


@app.get("/device/diag", status_code=200)
async def device_diag(response: Response) -> str:
    device_response = device_get("diag") or "error"
    logger.info(f"device diag -> {device_response}")
    if device_response == "error":
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
        return "DEVICE NOT RESPONDING"
    if device_response == "null":
        return "STATUS NOT AVAILABLE"
    metrics = device_response.strip('"').split(",")
    if len(metrics) == 1 and str(metrics[0]).isnumeric():
        return format_device_memory_status(metrics[0])
    if len(metrics) == len(DEFAULT_METRICS):
        return format_device_status(metrics)
    return device_response


@app.get("/chord/{click}", status_code=200)
async def chord_click(click: int, response: Response) -> str:
    if click > CHORD_COUNT:
        response.status_code = status.HTTP_400_BAD_REQUEST
        device_response = "invalid"
    else:
        # TODO update when device http server stack supports request params
        # device_response = device_post(f"chord?click={click}") or "error"
        device_response = device_post(f"chord/{click}") or "error"
    logger.info(f"device chord {click} -> {device_response}")
    if "ok" not in device_response:
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
    return device_response


# TODO The routes below will start working only after
#      the device http server stack is updated with request params support


@app.get("/volume/{pct}", status_code=200)
async def volume_pct(pct: int, response: Response) -> str:
    if pct < 0 or pct > 100:
        response.status_code = status.HTTP_400_BAD_REQUEST
        device_response = "invalid"
    else:
        device_response = device_post(f"volume?pct={pct}") or "error"
    logger.info(f"device volume {pct} -> {device_response}")
    if "ok" not in device_response:
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
    return device_response


@app.get("/mode/{mid}", status_code=200)
async def mode_id(mid: int, response: Response) -> str:
    if mid < 0 or mid > 2:
        response.status_code = status.HTTP_400_BAD_REQUEST
        device_response = "invalid"
    else:
        device_response = device_post(f"mode?id={mid}") or "error"
    logger.info(f"device mode {mid} -> {device_response}")
    if "ok" not in device_response:
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
    return device_response


@app.get("/chime/{mode}", status_code=200)
async def chime_mode(mode: int, response: Response) -> str:
    if mode == 0:
        device_response = device_post("chime/off") or "error"
    elif mode == 1:
        device_response = device_post("chime/on") or "error"
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        device_response = "invalid"
    logger.info(f"device chime {mode} -> {device_response}")
    if "ok" not in device_response:
        response.status_code = status.HTTP_424_FAILED_DEPENDENCY
    return device_response


app.mount("/", StaticFiles(directory="static", html=True), name="static")


def start():
    # In memory data store works with single worker which is enough for expected app usage
    uvicorn.run("server:app", host="0.0.0.0", port=80, workers=1)


if __name__ == "__main__":
    start()
