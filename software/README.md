# LUMA Pi4 controller and face firmware

The project includes a deterministic simulator and Raspberry Pi adapters for five pedestal ranging sensors, four Miuzei DS3218MG servos through a PCA9685, two independent LED rings, USB face display and local spoken Hi. The simulation needs Python3.11 or later.

```console
cd software
python -m luma.app --scene wink
python -m luma.app --scene hi
python -m luma.app --scene happy
python -m unittest discover -s tests -v
```

Simulation prints timestamped pose/light/face events as JSON. It advances deterministically without sleeping. `--seconds` sets duration. Scenes last6seconds, then return to idle. The three promotional scenes remain within the initial CAD travel envelope; they are repeatable face/motion scripts and do not require a cloud service.

## Raspberry Pi installation

Use Raspberry Pi OS Bookworm64bit on Pi4. The following setup commands affect only a Pi used for this project; do not execute them on the development Windows computer.

```console
sudo apt update
sudo apt install python3-venv python3-pip python3-dev i2c-tools espeak-ng alsa-utils
sudo raspi-config
```

In Interface Options enable I2C and SPI. In `/boot/firmware/config.txt`, confirm `dtparam=i2c_arm=on`, `dtparam=i2c_arm_baudrate=100000`, and `dtparam=spi=on`. Set `dtparam=audio=off` because BCM18's PWM peripheral drives theRGBW ring and analog audio conflicts. USB audio is separate. Reboot after these settings.

```console
cd software
python3 -m venv .venv
.venv/bin/pip install -e '.[hardware]'
ls -l /dev/serial/by-id/
aplay -l
```

Enter the actual display `/dev/serial/by-id/` path in `config.json`. The PCA9685 is I2C address64 (`0x40`), with yaw/shoulder/elbow/wrist on channels0/1/2/3. Select the USB speaker as the ALSA output or set `audio_device` to the identifier from `aplay -L`. The standard display and speaker share Pi4 USB power; use a powered hub if measurement requires it. Motors and LEDs never take power from Pi USB or GPIO.

Before connecting motor power, test the sensor chain and display independently. These commands do not instantiate the PCA9685 or LED drivers and do not require calibrated joints:

```console
.venv/bin/python -m luma.bench sensors --seconds 10
.venv/bin/python -m luma.bench display --port /dev/serial/by-id/YOUR_DISPLAY_DEVICE --scene all --seconds 10
```

The sensor check reports millimeters, age and mux channel in front/front-left/rear-left/rear-right/front-right order. Present a matte target at each pedestal aperture. `near` means a valid value below100mm: communication can pass, but armed motion would fault. The display check cycles idle/wink/Hi/happy and checks firmware replies. Inspect the pixels yourself. Exit status0 is pass,1 fail and130 interrupted. I2C normally needs membership in the `i2c` group; USB serial normally needs `dialout`.

Center only one disconnected, unloaded servo at a time. Keep its straight horn off the arm and keep the physical stop in reach. The command is capped at10seconds, disables the other three PCA9685 channels, and removes the selected PWM pulse when it exits:

```console
.venv/bin/python -m luma.bench servo --joint yaw --pulse-us 1500 --seconds 2 --confirm-unloaded
```

Repeat with `shoulder`, `elbow` and `wrist`. Power off before installing each horn. The DS3218 datasheet gives500-2500µs over270° with1500µs nominal neutral. Record the actual mechanical neutral in `neutral_pulse_us`; do not use this command on a loaded joint.

The PWM-backed NeoPixel library normally requires root on Pi4, so the full hardware command uses the virtual environment interpreter with sudo. Leave `calibrated=false` while wiring/testing. Hardware mode without `--arm` requires PCA9685 communication but leaves all four PWM outputs disabled; the separate6V motor rail can remain off.

```console
sudo .venv/bin/python -m luma.app --hardware --scene hi --seconds 6
```

Complete the commissioning procedure in `../electronics/architecture.md`, including unloaded neutral indexing, polarity/sign checks, physical stop tests and five valid pedestal ranges. Only then set `calibrated=true`. Support the arm in its indexed pose before every armed start; software cannot read its physical angles:

```console
sudo .venv/bin/python -m luma.app --hardware --arm --scene happy --seconds 6
```

Any fault latches for that process. It stops new targets and leaves the PCA9685 at the last pulse widths. Inspect the reason, support the arm, remove the cause and restart explicitly. PCA9685 health proves I2C communication only, not servo movement or position. The physical motor stop removes6V holding power. There is no unattended boot or auto-arm service.

## Display firmware

`display_firmware/` targets **ESP32-S3-Touch-LCD-1.85 SKU28514 only**. It uses USB serial115200, an ST77916 QSPI controller on CS21/SCK40/D046/D145/D242/D341, and a TCA9554 at0x20 over SDA11/SCL10 for LCD resetEXIO2/P1. Backlight is GPIO5. This pin mapping is from the [Waveshare board documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.85) and schematic. Firmware reads panel register0x04 and chooses one of the exact two vendor initialization tables: ID00-7F-7F-7F or00-02-7F-7F. Unknown IDs produce an error and do not advertise READY. Register command/data/delay values were converted from the vendor's April2025 demo to [Arduino_GFX](https://github.com/moononournation/Arduino_GFX/tree/v1.6.5) operations. A successful compile does not prove physical display operation; verify the purchased panel on the bench.

Install PlatformIO and build/flash the connected board:

```console
python -m pip install platformio
cd display_firmware
python -m platformio run
python -m platformio run --target upload --upload-port YOUR_SERIAL_PORT
python -m platformio device monitor --port YOUR_SERIAL_PORT --baud 115200
```

Commands are newline-delimited ASCII. `PING` replies `PONG`. `FACE idle`, `FACE wink`, `FACE hi`, `FACE happy`, and `FACE fault` reply `OK <name>`. Startup announces `READY LUMA1`. Invalid or overlong commands reply `ERR`. After1.5seconds without a host command/heartbeat the display shows WAITING. The host sends heartbeat every250ms and latches a motion hold if replies stop. No touch/audio/SD/battery functions are enabled on the display board; speech is generated on the Pi and played by the USB speaker.

## Optional 4-inch DSI head (Pi-rendered face)

Instead of the ESP32 face board, LUMA can use a Waveshare 4inch DSI LCD (C) — a round720x720 panel wired directly to the Pi's DSI port. There is no coprocessor for this head: the Pi itself renders the face every frame with `luma/face.py`, which reproduces `paint()` from `display_firmware/src/main.cpp` in Python (same colors, same shapes, same scene timing) scaled from the firmware's360x360 canvas up to the panel's720x720 resolution.

Select this head by setting `"display_kind": "dsi"` in `config.json` (leave `display_port` alone; it is ignored for this kind). Install the extra dependency alongside the existing hardware group:

```console
.venv/bin/pip install -e '.[hardware,dsi]'
```

Add these lines to `/boot/firmware/config.txt` for the Waveshare4inch DSI LCD(C):

```
dtoverlay=WS_xinchDSI_Screen,SCREEN_type=10,I2C_bus=10
dtoverlay=WS_xinchDSI_Touch,I2C_bus=10
```

Both overlays are the vendor's documented setup; LUMA's software never reads touch events — the lamp has no touch-driven behavior. If the picture is upside down for the mounted orientation (connectors at the bottom), rotate it with the vendor's documented `display_lcd_rotate`/Wayland rotation setting rather than in LUMA.

Running outside a desktop session (the normal case for an unattended lamp) needs pygame's KMS/DRM backend. `sudo` drops environment variables, so pass the driver through `env`:

```console
sudo env SDL_VIDEODRIVER=kmsdrm .venv/bin/python -m luma.app --hardware --scene hi --seconds 6
```

Bench-check the head on its own, the same way as the USB face board:

```console
.venv/bin/python -m luma.bench display --kind dsi --scene all --seconds 10
```

`--port` is not required (and is ignored) when `--kind dsi`; it stays required for the default `--kind usb_serial`. There is no serial heartbeat to a coprocessor for this head, so `Hardware`/`bench.display`'s notion of "heartbeat" becomes "a frame was drawn within the last1.5seconds" — `DsiDisplay.update()` returns that boolean the same way `Display.update()` returns the USB PONG heartbeat, so the rest of the control/fault-latching logic in `luma/control.py` is unaffected by which head is attached.

## Source/verification notes

`luma/servo_pwm.py` uses the maintained Adafruit CircuitPython PCA9685 library at50Hz. It converts calibrated angles through the DS3218's documented500-2500µs/270° range, starts with all four outputs disabled, and checks controller registers over I2C. The bounded bench path enables one unloaded channel only. Tests cover the duty conversion, channel isolation, config validation, scene limits, five renamed sensor inputs and fault behavior. Hardware paths have not been exercised on a physical Pi/arm.

The pinned firmware toolchain is self-contained in `platformio.ini`; downloaded SDK/toolchain caches are development artifacts and do not need redistribution. Python hardware dependency versions are bounded for installation flexibility, not a physical acceptance-tested lockfile. Record actual installed versions with `pip freeze` when commissioning the Pi.
