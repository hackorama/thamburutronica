"""Common utility functions used by all classes"""
import gc
import os
import time

import microcontroller
from config import CONFIG

MCU_RAM_BYTES = 264000  # 264kB SRAM
MCU_DISK_BYTES = 2000000  # 2MBB Flash


def isnumeric(value):  # CircuitPython string do not support isnumeric
    try:
        _ = int(value)
    except:  # pylint: disable=bare-except
        return False  # expected
    return True


def path_exists(path):
    try:
        # using stat exception, CircuitPython do not have os.path.exists()
        os.stat(path)
        return True
    except Exception:  # pylint: disable=broad-except
        pass
    return False


def disk_size_mb(path="/"):
    fs_stat = os.statvfs(path)
    return fs_stat[0] * fs_stat[2] / 1024 / 1024


def free_disk_size_mb(path="/"):
    fs_stat = os.statvfs(path)
    return fs_stat[0] * fs_stat[3] / 1024 / 1024


def log(msg):
    # TODO switch to adafruit_logging on boards with no memory constrains
    log_line = console_log(msg)
    file_log(log_line)


def console_log(msg):
    local_time = time.localtime()
    log_msg = "{year}-{month:02d}-{day:02d}T{hour:02d}:{minutes:02d}:{seconds:02d} {msg}"  # ISO 8601
    log_line = log_msg.format(
        year=local_time.tm_year,
        month=local_time.tm_mon,
        day=local_time.tm_mday,
        hour=local_time.tm_hour,
        minutes=local_time.tm_min,
        seconds=local_time.tm_sec,
        msg=msg,
    )
    print(log_line)
    return log_line


def file_log(msg):
    if CONFIG.LOG_FILE:
        if (
            not CONFIG.LOG_PATH_MOUNTED
        ):  # wait for card mounting and minimise path check
            CONFIG.LOG_PATH_MOUNTED = path_exists(CONFIG.SD_MOUNT)
            console_log(
                f"Log file {CONFIG.LOG_FILE} is {'ready' if CONFIG.LOG_PATH_MOUNTED else 'not ready'}"
            )

        if CONFIG.LOG_PATH_MOUNTED:
            try:
                with open(CONFIG.LOG_FILE, mode="a", encoding="utf-8") as file:
                    file.write(f"{msg}\n")
            except Exception as error:  # pylint: disable=broad-except
                console_log(
                    f"ERROR Failed writing logs to file {CONFIG.LOG_PATH_MOUNTED}, {error}"
                )
                CONFIG.LOG_FILE = None


def memory_sweep():
    """Force memory garbage collection and log memory usage

    On memory constrained MCU like Pi Pico call the garbage collector early and often
    Refer: https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython
    """
    if not CONFIG.RESTRICT_MEMORY:
        return
    # TODO no-member: check CircuitPython lib stub issue ?
    free_before = gc.mem_free()  # pylint: disable=no-member

    gc.collect()

    free = gc.mem_free()  # pylint: disable=no-member
    used = gc.mem_alloc()  # pylint: disable=no-member
    available = used + free
    change = free - free_before
    used_pct = int((used / available) * 100) if available else 0
    free_pct = int((free / available) * 100) if available else 0
    change_pct = int((change / free) * 100) if free else 0

    log(
        f"MEM Bytes: {available} available, {used} {used_pct}% used, {free} {free_pct}% free ({change} {change_pct}% change)"
    )


def os_summary():
    return f"OS: {os.uname().machine} {os.uname().sysname} CircuitPython {os.uname().version}"


def cpu_temp():
    return microcontroller.cpu.voltage


def cpu_summary():
    return f"CPU: {microcontroller.cpu.frequency / 1000000} MHz, {cpu_temp()} V, {microcontroller.cpu.temperature} \u00B0C"


def disk_summary():
    total = disk_size_mb()
    free = free_disk_size_mb()
    free_pct = round(int((free / total) * 100), 2) if total else 0
    return f"Disk / MB: {total} total, {free} {free_pct}% free"


def sd_card_summary():
    total = disk_size_mb(CONFIG.SD_MOUNT)
    free = free_disk_size_mb(CONFIG.SD_MOUNT)
    free_pct = round(int((free / total) * 100), 2) if total else 0
    return f"Disk {CONFIG.SD_MOUNT} MB: {total} total, {free} {free_pct}% free"


def memory_summary():
    # TODO no-member: check CircuitPython lib stub issue ?
    used = gc.mem_alloc()  # pylint: disable=no-member
    free = gc.mem_free()  # pylint: disable=no-member
    available = used + free
    available_pct = int((available / MCU_RAM_BYTES) * 100) if MCU_RAM_BYTES else 0
    used_pct = int((used / available) * 100) if available else 0
    free_pct = int((free / available) * 100) if available else 0

    return f"MEM Bytes: {MCU_RAM_BYTES} SRAM: {available} {available_pct}% available, {used} {used_pct}% used, {free} {free_pct}% free"


def sysinfo(self, memory):
    log(cpu_summary())
    log(os_summary())
    log(memory_summary())
    log(disk_summary())
    log(sd_card_summary())
