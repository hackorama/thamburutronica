import logging
import os
from typing import Optional

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


def get_env_device_host() -> Optional[str]:
    return os.environ.get(DEVICE_HOST_ENV)


def set_env_device_host(host: str) -> None:
    os.environ[DEVICE_HOST_ENV] = host


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
        return "no device"
    url = f"http://{host}/{path}"
    try:
        response = requests.post(url, timeout=REQUEST_TIMEOUT_SECS)
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"POST failed connecting to device {host}")
        return "no device connection"
    return response.text


def device_get(path: str) -> str:
    host = read_device_host()
    if not host:
        return "no device"
    url = f"http://{host}/{path}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECS)
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"GET failed connecting to device {host}")
        return "no device connection"
    return response.text


@app.get("/device/register/{host}", status_code=200)
async def device_register(host: str) -> str:
    store_device_host(host)
    return f"{host} ok"


@app.get("/device/ping", status_code=200)
async def device_ping(response: Response) -> str:
    device_response = device_get("ping") or "error"
    logger.info(f"device ping -> {device_response}")
    if device_response != "pong":
        response.status_code = status.HTTP_404_NOT_FOUND
    return device_response


@app.get("/chord/{click}", status_code=200)
async def chord_click(click: int, response: Response) -> str:
    if click > CHORD_COUNT:
        device_response = "invalid"
    else:
        device_response = device_post(f"chord/{click}") or "error"
    logger.info(f"device chord {click} -> {device_response}")
    if "ok" not in device_response:
        response.status_code = status.HTTP_404_NOT_FOUND
    return device_response


@app.get("/health", status_code=200)
async def health() -> str:
    return "OK"


app.mount("/", StaticFiles(directory="static", html=True), name="static")


def start():
    uvicorn.run("server:app", host="0.0.0.0", port=80, workers=3)


if __name__ == "__main__":
    start()
