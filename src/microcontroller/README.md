# Microcontroller code

CircuitPython code for Pi Pico W

## Overview

Main modules

- [Manager](./manager.py) - Event loop orchestration
- [Pico](./pico.py) - The microcontroller specific driver code for Pi Pico
- [Play](./play.py) - The microcontroller independent main device control logic

Sub modules - [Web](./web.py), [Chime](./chime.py), [Flair](./flair.py)

CircuitPython entry point [code.py](./code.py)

## Deploying

- [Boot Pi Pico W to CircuitPython 8.x](./docs/installing-circuitpython.md)
- [Install the required CircuitPython libraries](./docs/lib-dependencies.md)
- Copy the `*.py` code to Pi Pico W using USB

> On macOS the CircuitPython USB mount point will be `/Volumes/CIRCUITPY`

## Hardware

| Board                                                                                                    | Chip                                                                                                                                                          | Description                                |
|----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| Raspberry Pi [Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) | Raspberry Pi [RP2040](https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html#welcome-to-rp2040)                                               | MCU                                        |
|                                                                                                          | Infineon [CYW43439](https://www.infineon.com/cms/en/product/wireless-connectivity/airoc-wi-fi-plus-bluetooth-combos/wi-fi-4-802.11n/cyw43439/?redirId=216343) | Wi-Fi, Bluetooth                           |
| Adafruit [12-Key Capacitive Touch Sensor](https://www.adafruit.com/product/4830)                         | NXP [MPR121](https://www.nxp.com/products/no-longer-manufactured/proximity-capacitive-touch-sensor-controller:MPR121)                                         | Proximity Capacitive Touch                 |
| Sparkfun [Qwiic Speaker Amp](https://www.sparkfun.com/products/20690)                                    | Texas Instruments [TPA2016D2](https://www.ti.com/product/TPA2016D2)                                                                                           | Audio amp                                  |
| Cytron [Maker Pi Pico Base](https://www.cytron.io/p-maker-pi-pico-base)                                  |                                                                                                                                                               | Base for micro SD card slot and audio jack |

Programmed using [CircuitPython](https://circuitpython.org/board/raspberry_pi_pico/) 8

