# Microcontroller code

CircuitPython code for Pi Pico W

## Overview

Main modules

- [Manager](./manager.py) - Event loop orchestration
- [Pico](./pico.py) - The microcontroller specific driver code for Pi Pico
- [Play](./play.py) - The microcontroller independent main device control logic

Sub modules - [Web](./web.py), [Chime](./chime.py), [Flair](./flair.py)

CircuitPython entry point [code.py](./code.py)

## Build

```shell
$ make help
help:        Show help
deps:        Install dev python packages
device:      Install circuitpython packages on device
check:       Run python code checks
compile:     Build mpy files
deploy:      Deploy mpy files to device
```

## Deploy

- [Boot Pi Pico W to CircuitPython 8.x](./docs/installing-circuitpython.md)
- [Install the required CircuitPython libraries](./docs/lib-dependencies.md)
- Copy the `*.py` or `*.mpy` code to USB mounted Pi Pico W - `make deploy`

> On macOS the CircuitPython USB mount point will be `/Volumes/CIRCUITPY`

## Hardware

![Microcontroller circuit hookup diagram](./docs/hookup-diagram.png)

[PNG](./docs/hookup-diagram.png) [PDF](./docs/hookup-diagram.pdf) [SVG](./docs/hookup-diagram.svg)

| Board                                                                                                    | Chip                                                                                                                                                          | Description                           |
|----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| Raspberry Pi [Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) | Raspberry Pi [RP2040](https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html#welcome-to-rp2040)                                               | MCU                                   |
|                                                                                                          | Infineon [CYW43439](https://www.infineon.com/cms/en/product/wireless-connectivity/airoc-wi-fi-plus-bluetooth-combos/wi-fi-4-802.11n/cyw43439/?redirId=216343) | Wi-Fi, Bluetooth                      |
| Adafruit [12-Key Capacitive Touch Sensor](https://www.adafruit.com/product/4830)                         | NXP [MPR121](https://www.nxp.com/products/no-longer-manufactured/proximity-capacitive-touch-sensor-controller:MPR121)                                         | Capacitive Touch Sensor               |
| Sparkfun [Qwiic Speaker Amp](https://www.sparkfun.com/products/20690)                                    | Texas Instruments [TPA2016D2](https://www.ti.com/product/TPA2016D2)                                                                                           | Audio Amp                             |
| Cytron [Maker Pi Pico Base](https://www.cytron.io/p-maker-pi-pico-base)                                  |                                                                                                                                                               | Provides Micro SD Card and Audio Jack |

> Pi Pico W is configured with [CircuitPython 8 Firmware](https://circuitpython.org/board/raspberry_pi_pico/) using [USB UF2 bootloader](./docs/installing-circuitpython.md)


| Part                                                                                                                      | USD        |
|---------------------------------------------------------------------------------------------------------------------------|------------|
| [Raspberry Pi Pico W](https://www.sparkfun.com/products/20173)                                                            | 06.00      |  
| [Cytron Maker Pi Pico Base](https://www.adafruit.com/product/5160)                                                        | 09.95      |
| [Adafruit Capacitive Touch Sensor](https://www.adafruit.com/product/4830)                                                 | 06.95      |
| [SparkFun Qwiic Speaker Amp](https://www.sparkfun.com/products/20690)                                                     | 10.95      |
| [Speaker 3" 8 Ohm 1 Watt](https://www.adafruit.com/product/1313)                                                          | 01.95      |
| [Monk Makes Squid RGB LED](https://www.robotshop.com/products/monk-makes-squid-rgb-led-raspberry-pi)                      | 04.67      |
| [Grove to Qwiic connector](https://www.adafruit.com/product/4528)                                                         | 01.95      |
| [USB to Micro USB Cable](https://www.amazon.com/dp/B013G4EAEI)                                                            | 06.99      |
| [USB Splitter](https://www.amazon.com/Female-Splitter-Power-Extension-Adapter/dp/B07CKQSTCB)                              | 06.88      |
| [USB Jack](https://www.amazon.com/USB-Keystone-Jack-Inserts-Pack/dp/B0789FGFL8)                                           | 06.50      |
| [USB Connector](https://www.amazon.com/Terminal-Screwdriver-Soldering-Required-Connectors/dp/B09BKHPT9C)                  | 09.69      |
| [USB Adapter](https://www.amazon.com/AmazonBasics-One-Port-USB-Wall-Charger/dp/B0773JCTR5)                                | 10.81      |
| [USB Cable](https://www.amazon.com/Monoprice-Male-24AWG-Cable-Plated/dp/B009GUN1T2)                                       | 05.80      |
| [Aux Audio Cable](https://www.amazon.com/Seadream-2Pack-Headphones-iPhones-Stereos/dp/B01L0YPVOY)                         | 07.29      |
| [Micro SD Card](https://www.amazon.com/SanDisk-Ultra-microSDXC-Memory-Adapter/dp/B073JWXGNT/)                             | 09.29      |
| [Wire Cable](https://www.michaels.com/bead-landing-26-gauge-colored-copper-wire/M10105400.html)                           | 06.49      |
| [Mirror screw (Touch Button)](https://www.amazon.com/Mellewell-Decorative-Construction-Fasteners-Stainless/dp/B07CFKPFWQ) | 13.99      |
| Total (Plus taxes and shipping)                                                                                           | **126.15** |

## Device control

The capacitive touch enabled chords provide the audio playback controls.
There are also four capacitive touch control buttons on the sides for device settings.


| Button        | Action             | Mode                       | Status |
|---------------|--------------------|----------------------------|--------|
| Top right     | Selects play mode  | Touch to play chord scales | 🔵     |
|               |                    | Tap to play chord scales   | 🟣     |       
|               |                    | Tap to play custom music   | 🟠     |
| Top left      | Clock chime ON/OFF | ON                         | 🟢     |
|               |                    | OFF                        | 🔴     |
| Bottom left 1 | Volume             | UP                         | BEEP   |
| Bottom left 2 | Volume             | DOWN                       | BEEP   |

## Device status

The RGB LED shows device status during boot up.

| Status                      | LED |
|-----------------------------|-----|
| Device booting up           | ⚪   |
| Network connection failed   | 🔴  |
| Network time sync failed    | 🟠  |
| Network unknown failure     | 🔵  |
| Storage failure             | 🟡  |
| Storage and network failure | 🟣  |
| Device ready (BEEP)         | 🟢  |

## Memory handling notes

As new features were added (Wi-Fi, clock chimes etc.) had to make some changes
to fit everything into the limited microcontroller memory.

Pi Pico W has only `264kB` RAM and `2MB` Flash storage.

- Removed non-essential features saving module import memory usage
  - Logging with logging file handler, switched to simple console prints
  - Debug use of on-board buttons and neo pixel
  - Multi channel audio mixer made optional
- Switch to memory and cpu efficient `wave` files instead of `mp3` files
  - The space non-efficient `wave` files are on the SD card and not on the on-board flash storage
- Late lazy import of modules, aggressive periodic gc collection
- No object allocations in the event loop, prefer bools/ints over strings
- Compile to memory efficient `.mpy` files when deploying
- Audio LED visual effects were made optional to reduce system load

On top of the memory pressure issues the cpu load caused audio playback quality issues.
The cpu load was caused by simultaneous processing of - log writes and audio file reads
from same SD card storge, LED visual effects, event checks on GPIO pins, Wi-Fi polling.

The log writes to the SD card (which were added to debug memory issues) were removed since
the increased cpu load along with memory pressure caused random system hangs.
The audio files on the SD card were changed to read only mode to prevent file corruptions
during hard reset after a hang. A storage sanity check was added to detect any
file corruptions on system start.

## TODO

- Add detailed system status reportng - storage usage, cpu temp, versions etc.
- Extend device api for additional app controls - volume, chime on/off, mode selection
- Update to latest CircuitPython release version and update the packages
- Ambient mode with looping playback in tap to play mode
- Overlapping chord audio fade over using mixer channels if within memory constrains
- Restore console logging if within memory constrains
- Use the local app server time instead of external NTP sync
- Add automatic daylight savings adjustment on NTP sync tz offset
- Add new LED visual effects
- Add audio messages during startup and control button clicks

