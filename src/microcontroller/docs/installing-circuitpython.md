

- Download stable UF2 from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/)
  - `7.x.x` is current stable, install `8.x.x` (now in beta) when released
  - `adafruit-circuitpython-raspberry_pi_pico-en_US-7.3.3.uf2`
  - `adafruit-circuitpython-raspberry_pi_pico-en_US-8.0.0-beta.1.uf2`
- Install using steps from [adfruit.com](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython)
  - Holding `BOOTSEL` button connect Pico using USB cable
  - Pico will be mounted as a new USB drive `RP1-RP2`
  - Copy the UF2 file to `RP1-RP2`
  - `$ cp ~/Downloads/adafruit-circuitpython-raspberry_pi_pico-en_US-7.3.3.uf2 /Volumes/RP1-RP2`
  - `RP1-RP2` will be replaced by a new USB drive named `CIRCUITPY`
- Verify the circuitpy install
  - Thonny -> Preferences : Interpreter : Port
  - `$ ls /dev/tty.*`
  - Add `code.py` to `CIRCUITPY` and list GPIO pins

```python
import board
dir(board)
```
