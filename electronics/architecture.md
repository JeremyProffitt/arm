# LUMA electrical design, revision C

The Raspberry Pi 4 is the behavior and motion master. It reads five Adafruit 3967 VL53L1X STEMMA QT sensors through an I2C mux, commands four inventory Miuzei DS3218MG servos through the user-selected PCA9685 PWM board, selects face expressions, produces local speech, and drives both light rings.

The standard head uses the **Waveshare ESP32-S3-Touch-LCD-1.85, SKU 28514, without B or C suffix**. It is a 360 × 360 TFT LCD, not OLED. Its ESP32-S3 is a USB graphics peripheral; its Wi-Fi, touch, microphone, and battery functions are unused. Do not substitute a visually similar 1.85B, 1.85C, AMOLED, or bare panel. See [Waveshare documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.85).

```
Pi4 USB ─┬─ Waveshare ESP32-S3 1.85 LCD / face firmware
         └─ USB speaker / local espeak-ng speech
Pi I2C ──┬─ PCA9685 address0x40 ─ PWM channels0..3 ─ four DS3218MG
         └─ PCA9548/TCA9548A-compatible mux address0x70 ─ ports0..4 ─ five VL53L1X
Pi BCM10 SPI MOSI ─ 74AHCT125 +330Ω ─ 60RGB outer ring
Pi BCM18 PWM0    ─ 74AHCT125 +330Ω ─ 24RGBW inner ring (white only)
Pi BCM27        ─ isolated NC stop contact ─ GND
12V relay output ─ 7.5A fuse ─ 6V/11A regulator ─ four fused servo feeds
```

## Optional 4-inch DSI head

The optional head replaces the USB display with a **Waveshare 4inch DSI LCD (C)**. It is a round 720 × 720 IPS panel in a 126 mm case. The Pi renders the face directly with `display_kind: "dsi"`; there is no display coprocessor or serial heartbeat. Connect its 15-pin 1.0 mm DSI FPC and connect 5 V/GND from Pi header pins4/39 to the display's HP2.0 socket. Leave that socket's SDA/SCL contacts empty. Touch and backlight control use `I2C_bus=10` on the DSI connector, and LUMA does not read touch input.

The FPC run through the arm is about800 mm. That is longer than the vendor-supplied50mm cables and must be proven on the bench before the links close. Keep it away from the moving 6 V servo feeds. This head omits the24-pixel RGBW ring; the outer halo supplies capped white output. [Vendor page](https://www.waveshare.com/4inch-dsi-lcd-c.htm).

## Power, stop, and servo distribution

Use the official Pi5.1 V/3 A USB-C supply. Use the external Mean Well GST220A12-R7B 12 V/15 A supply for the LED buck converter and the servo regulator. The enclosure contains DC only. All grounds meet at one DC star. Pi5 V and LED5 V remain separate. Wire the locking R7B connector exactly as its drawing specifies. [Mean Well specification](https://www.meanwell.com/Upload/PDF/GST220A/GST220A-SPEC.PDF).

The four Miuzei DS3218MG units are 4.8-6.8 V PWM position servos. The vendor datasheet gives 2.2 A stall current and21.5 kg-cm stall torque at6.8 V. Four can therefore demand8.8 A at once. This is an abnormal design transient, not a permitted continuous operating point. Use the Pololu D42V110F6 fixed6 V regulator. Its nominal rating is11 A, while its actual continuous output depends on input voltage, cooling, and load. Verify6 V polarity and loaded voltage before connecting a servo. [DS3218 datasheet](https://images-na.ssl-images-amazon.com/images/I/81Lbgu%2BnG6L.pdf), [regulator specification](https://www.pololu.com/product/5673).

A15 A main fuse protects the12 V trunk. A normally-open12 V relay interrupts only the servo regulator input. A latching stop's first NC contact interrupts the fused relay coil. Its second isolated NC contact grounds BCM27 in the normal state. Add the coil flyback diode with its stripe at coil positive. **The stop must remove servo power with the Pi disconnected.** Pi, display, sensing, and lights stay powered so they can report a stopped motor rail.

Feed the regulator through its own7.5 A time-delay fuse. Put a2200 µF/10 V or higher low-ESR capacitor across the6 V star. Feed each servo from that star through its own3 A time-delay fuse and18 AWG V+/GND pair. Do not send the possible8.8 A group current through a generic PCA9685 terminal block or PCB trace. At the PCA9685, connect only each servo's signal and ground; route V+ from the fused star. Confirm actual connector polarity instead of relying only on wire color.

Power PCA9685 VCC from Pi3.3 V. Connect SDA/SCL to Pi physical pins3/5, connect its ground to the DC star, and hold active-low `/OE` low. The PCA9685 address is0x40 and the sensor mux address is0x70. Software uses channels0,1,2,3 for yaw, shoulder, elbow, wrist at50 Hz. The documented DS3218 pulse range is500-2500 µs with1500 µs nominal neutral over the270-degree variant. The PWM board reports I2C communication only. It cannot report servo shaft position, load, current, or temperature. [PCA9685 guide](https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up).

The Pololu D24V50F5 still converts12 V to the separate LED5 V rail through its2 A input and3 A output fuses. Software caps the outer RGB ring at20%. The outer ring allowance at that cap is about0.72 A. The inner ring uses RGB=0 and W no higher than192/255, about0.36 A. Put a1000 µF/10 V capacitor at each ring and a100 nF ceramic at the74AHCT125. Exact current and temperature require measurement.

## Five pedestal sensors and I2C allocation

All five Adafruit3967 boards mount behind open apertures in the216 mm pedestal wall. Looking down with the face aimed toward+Y, their centers are front90°, front-left162°, rear-left234°, rear-right306°, and front-right18°. Mux ports0 through4 use that same order. The two rear sectors can request a wink. The two front-side sectors can request the happy gesture. Every sector is also a mandatory obstruction input.

Each board remains at address0x29 on its own mux channel. The mux is the Adafruit5626 PCA9548, which uses the TCA9548A-compatible driver. Both the mux and PCA9685 share the upstream Pi I2C bus at3.3 V logic. Put the mux on the electronics tray in the pedestal. The five branch cables now remain in the fixed base and do not pass through yaw or the arm.

Software ranges only one emitter at a time with a33 ms short-mode timing budget. A normal five-channel sweep is about0.25-0.4 seconds. A missing sensor, invalid/no-return value, reading older than650 ms, or valid range below100 mm latches a motion hold. The five narrow horizontal cones do not cover every pinch point and are not a safety-rated perimeter.

Remove each shipping film. Keep every10 × 10 mm wall aperture open; no frosted plastic or uncharacterized IR window belongs in front of the sensor. Mount each25.40 × 17.78 mm board component-side toward its opening using fourM2.5x6 screws on its20.32 × 12.70 mm hole pattern. Tighten only until the PCB is stable. Leave side clearance for one STEMMA QT plug and add strain relief inside the base.

## Motion indexing without joint feedback

The DS3218MG has one25T output spline and no readable position channel. Yaw remains supported by the6808 bearing. Each pitch joint uses the servo's straight metal arm on the driven side and a625 bearing/M5 axle on the opposite side. The supplied metal arm's attachment holes are not dimensioned in the datasheet, so the printed interface has two radial slots. Measure each actual horn and select fasteners before applying load.

Center each disconnected, unloaded servo at1500 µs before installing its horn. The mechanical neutral pose is upper link115° from+Y horizontal, forearm45° from+Y, relative elbow−70°, and face vertical toward+Y. The shoulder axis isZ121 mm after the6 mm pedestal increase. Initial command limits remain yaw±25° and shoulder/elbow/wrist±10°. Calibrate each `neutral_pulse_us` and `joint_signs` value from the real mechanism; all1500/all+1 values are only starting values.

Hardware motion stays off unless both `calibrated=true` and `--arm` are supplied. Arming verifies fresh sensor data, display health, a closed motor stop, and PCA9685 communication, then sends the four calibrated neutral pulses. It cannot verify the physical starting angles. Support the complete arm before arming because a wrong pulse or horn index can cause immediate motion.

A behavior fault stops target updates and leaves the PCA9685 at its last commanded pulse widths. A PCA9685 I2C failure also stops new commands, but the controller or servo can retain its last output. Use the independent physical motor stop for unexpected motion. A motor-power cut releases holding torque. No software watchdog, encoder feedback, current feedback, thermal feedback, or safety-rated stop controller is claimed.

## Bench commissioning sequence

1. Keep all four horns disconnected from the links. Open the motor stop. Verify12 V input, LED5 V, Pi3.3 V logic, and the regulated6 V servo output separately. Confirm the2200 µF capacitor polarity.
2. With servo V+ still disconnected, run `i2cdetect -y 1`. Confirm PCA9685 at0x40 and the mux at0x70. Check every PCA9685 signal lead and all five mux branches against `wiring.csv`.
3. Test the five sensors with `.venv/bin/python -m luma.bench sensors --seconds 10`. Cover one pedestal aperture at a time and confirm the reported port/name order.
4. Connect one unloaded servo and one3 A fused branch. With the stop in reach, run `.venv/bin/python -m luma.bench servo --joint yaw --pulse-us 1500 --seconds 2 --confirm-unloaded`, changing `--joint` for each channel. The command disables the other three PWM channels and removes the selected PWM pulse when the bounded check ends. Mark the resulting physical neutral.
5. Power off. Fit each straight metal arm to its indexed servo. Dry-fit its two printed radial slots and the opposite625/M5 support. Confirm free rotation, bearing alignment, smooth-shank contact at the inner race, and no bolt contact with the servo case.
6. Test the standard or DSI display and both LED rings. Verify that outer RGB is at20% or less and inner W is at192/255 or less. Measure LED, regulator, Pi, and enclosure temperatures during a30-minute run.
7. Verify that the physical stop removes voltage at the6 V star with the Pi unplugged. Verify BCM27 reports stop when either NC2 wire is removed. Reset only while the head is supported.
8. Enter measured neutral pulses and joint signs in `config.json`. Set `calibrated=true` only after every unloaded joint moves in the correct direction. Run hardware mode without `--arm`, then one supported6-second scene with `--arm`.
9. Check the complete limited motion for cable clearance, collision, stability, servo/regulator temperature, and loaded6 V droop. Reduce travel or redesign the counterbalance if any joint cannot sustain the pose.

## Evidence and limits

Host behavior and PWM-conversion tests run without hardware. The CAD uses the vendor's body envelope and the Adafruit board's published mounting coordinates. Physical servo fit, horn-hole fit, PCA9685 board revision, regulator cooling, electrical continuity, holding torque, optical range, and thermal behavior remain first-build checks. Budget figures are planning allowances, not quotations.
