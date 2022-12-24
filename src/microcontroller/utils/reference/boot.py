# Must be named boot.py in CIRCUITPY root mount point
# https://learn.adafruit.com/welcome-to-circuitpython/renaming-circuitpy

import storage

NAME = "PICO"  # Must be < 11 characters, renames CIRCUIT_PY to this name

storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = NAME
storage.remount("/", readonly=True)
storage.enable_usb_drive()
