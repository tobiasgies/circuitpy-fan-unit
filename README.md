# Circuit Python Code for Smart Fan Unit

![GitHub License](https://img.shields.io/github/license/uptime-industries/circuitpy-fan-unit?style=for-the-badge)
![Static Badge](https://img.shields.io/badge/circuitpython-9.2.1-blue?style=for-the-badge&logo=adafruit)

## Installation

1. Connect to USB and boot the Raspberry in UF2 Bootloader v3.0 mode (power on with BOOT button pressed)
2. Download firmware from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/) for the RPI Pico
3. Put the `adafruit-circuitpython-raspberry_pi_pico-en_US-*.uf2` (or later) file on the mounted storage.  
4. Copy `code.py` file and `./lib` folder to the mounted storage

______

console output example:

```txt
Button is not pressed
From Blade A Auto
From Blade B Auto
Blade A airflow temperature: 24 C
Blade B airflow temperature: 25.75 C
Setting fan speed to 10%
Fan speed 564.676 RPM
```