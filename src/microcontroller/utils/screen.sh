# https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux

BOARD_NAME = "usbmodem14401"
BAUD = "115200"

ls /dev/tty.*
screen /dev/tty.$BOARD_NAME $BAUD
