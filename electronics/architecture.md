# LUMA electrical design, revision A

The Raspberry Pi 4 is the only behavior and motion master. It reads exactly five Adafruit 3967 VL53L1X STEMMA QT sensors, commands four ST3215 position servos, selects face expressions, produces local speech, and drives both light rings. The Waveshare board is a wired display coprocessor; its Wi-Fi, touch, microphone and battery circuitry are unused.

The selected display is the **Waveshare ESP32-S3-Touch-LCD-1.85, SKU 28514, without B or C suffix**. This is a 360 × 360 TFT LCD, not OLED. Its 55 × 55 mm circuit assembly and ST77916 QSPI interface are vendor documented. USB serial avoids presenting the bare QSPI panel as a directly compatible Pi display. Do not substitute a visually similar 1.85B/1.85C: their pin assignments and revisions differ. Reserve a 15 mm rear right-angle plug/cable clearance as a design assumption, then measure the purchased cable and board before final printing. See [Waveshare documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.85).

```
Pi4 USB ─┬─ Waveshare ESP32-S3 1.85 LCD / face firmware
         ├─ Bus Servo Adapter A ─ DATA ─ ID1 yaw ─ ID2 shoulder ─ ID3 elbow ─ ID4 wrist
         └─ USB speaker / local espeak-ng speech
Pi I2C ─ PCA9548/TCA9548A-compatible mux ─ ports0..4 ─ five VL53L1X
Pi BCM10 SPI MOSI ─ 74AHCT125 +330Ω ─ 60RGB outer ring
Pi BCM18 PWM0    ─ 74AHCT125 +330Ω ─ 24RGBW inner ring (white only)
Pi BCM27        ─ isolated NC stop contact ─ GND
```

## Optional 4-inch DSI head

The optional head replaces the USB display with a **Waveshare 4inch DSI LCD (C)** (round 720 × 720 IPS, DSI, 126 mm case). The Raspberry Pi drives it directly from its DSI connector and renders the face itself with the `display_kind: "dsi"` software path; there is no coprocessor, no USB link and no serial heartbeat. The display needs three connections: the 15-pin 1.0 mm DSI FPC (data, plus the DSI connector's I2C for touch and backlight control, `I2C_bus=10` in the vendor overlay), and 5 V/GND to its HP2.0 4-pin socket from Pi header pins 4 and 39. Leave the socket's SDA/SCL contacts empty so the display's touch controller never shares the sensor mux bus. Touch is not used.

The FPC runs about 800 mm from the tray through the turntable aperture, the two enclosed links and the fork slot. MIPI DSI over an 800 mm unshielded FFC is outside the length the vendor supplies (50 mm cables are included; 150 mm is sold for compute modules) and must be proven on the bench before the arm is closed: a display that blanks, tears or shows a shifted image is a cable problem before it is a software problem. Keep the FFC away from the servo power leads inside the links. The display's backlight draws from the Pi's 5 V rail in place of the USB display, so the Pi supply budget is unchanged in kind; measure the actual current at full backlight. This head has no 24-pixel RGBW ring: `WHITE_DATA5V` and `LED_WHITE_POWER` are left unconnected and the software's white-channel output goes nowhere, while the halo provides white light at its capped brightness. [Vendor page](https://www.waveshare.com/4inch-dsi-lcd-c.htm).

## Power and physical wiring

Use the official Pi 5.1 V/3 A USB-C supply. Use an external enclosed Mean Well GST220A12-R7B 12 V/15 A supply for the actuators and the LED buck converter. All grounds share one DC star point; the Pi 5 V rail and LED 5 V rail are never joined. The enclosure contains DC only. The chosen supply uses a locking R7B power DIN, not a standard small barrel plug. Order a correctly rated mating harness and wire all parallel contacts exactly as the supply drawing specifies. [Mean Well specification](https://www.meanwell.com/Upload/PDF/GST220A/GST220A-SPEC.PDF).

Each 12 V ST3215 can draw 2.7 A stalled. Four together can demand 10.8 A; that is an abnormal transient design load, not a permissible continuous duty point. A 15 A main DC fuse protects a 16 AWG input trunk. A normally-open 12 V coil relay with a contact rating of at least 15 A at 12 VDC disconnects the four motor feeds. A latching stop's first NC contact interrupts the fused relay coil supply; its second, electrically isolated NC contact grounds BCM27 in the normal state. Fit a coil flyback diode with stripe to coil positive. **The stop must work with the Pi disconnected.** Match actual connector, relay and wire ratings; the generic accessories in the BOM are procurement specifications, not falsely verified exact products. [Servo electrical specifications](https://www.waveshare.com/product/modules/st3215-servo.htm).

Distribute motor V+ and GND as four separate 18 AWG feeds with 3 A time-delay fuses on V+. Do not route all motor current through one servo lead or the USB adapter's barrel jack. The adapter gets its own 1 A fused supply; its DATA and GND join the servo signal harness while its V+ is disconnected from the motor harness. Observe the markings on the actual servo connector; do not rely only on red/black/white wire conventions. The stop disconnects motor V+, while Pi, face and lights remain powered to report the stop.

The Pololu D24V50F5 converts 12 V to LED 5 V through a 2 A input fuse and 3 A output fuse. Its advertised 5 A output is thermally limited. Software caps the outer RGB ring at 20%. The outer RGB worst-case allowance at that cap is approximately 60 × 60 mA × 0.2 = 0.72 A. The inner ring uses only white with RGB forced to zero and W limited to192/255; approximately 24 × 20 mA × 192/255 = 0.36 A, or1.8W electrical LED input. Exact LED revisions differ, so measure assembled current. Uncapped all-channel full white would be about 5.52 A across the rings and is not an allowed operating mode. This first prototype is an expressive accent/task-area lamp; lux, CRI and lumen output are not validated and are not equivalent to the reference commercial lamp. [Pololu specification](https://www.pololu.com/product/2851).

Use two channels of a **74AHCT125**, powered at LED 5 V, to shift BCM10 and BCM18. HC125 alone is not the same input threshold. Pin-by-pin connections are in `wiring.csv`. Put a 330 Ω resistor at each LED data input, a 1000 µF/10 V polarized capacitor across each ring supply, and a 100 nF ceramic across DIP pins14/7. The four outer quadrants require a structural backing, not just soldered joints. Solder DATA through only three joints; leave the last DOUT open. The RGB and RGBW streams remain separate. [NeoPixel ring documentation](https://www.adafruit.com/product/1768), [RGBW ring](https://www.adafruit.com/product/2862).

## Five sensors and bus allocation

Mux address is 0x70; each sensor remains at its default 0x29 on a separate channel. Port0 is front, port1 left, port2 right, port3 rear, port4 down, using the lamp's own left/right. A rear hand gesture requests a wink. The mux is Adafruit5626 PCA9548, electrically compatible with TCA9548A and the same Python driver. Upstream I2C uses Pi physical3/5 (BCM2/3); logic power is Pi3.3V. Do not power the upstream pull-ups at 5 V. [Mux documentation](https://www.adafruit.com/product/5626), [sensor pinout](https://learn.adafruit.com/adafruit-vl53l1x/pinouts).

Place the mux in the head to keep the five branch cables short. Keep the Pi-to-head trunk about 500 mm or shorter at 100 kHz and separate it from motor power. A longer bus requires a measured signal integrity check or a differential I2C extender. The mux isolates addresses, not optical beams: software ranges one sensor at a time at a 33 ms timing budget in short mode. A normal sweep is roughly 0.25–0.4 seconds including overhead. Out-of-range/no-return measurements are invalid, never assumed clear. Short mode is intentionally conservative for indoor interactions; it does not promise the device's headline4m maximum.

Remove shipping films. Each ranging aperture must remain open or use a specifically characterized IR window. **Do not put the frosted print over a ToF sensor.** The down sensor must see a nominal desk distance above100mm throughout the allowed pose range; if the support surface is closer, reposition the sensor before commissioning. An object below100mm, missing sensor, invalid range, or reading older than650ms latches a hold. These are interaction interlocks, not a safety-rated collision detector, and five narrow cones do not cover all pinch points.

## Motion indexing and feedback

Set servo IDs individually with the vendor tool before making the bus:1 yaw,2 shoulder,3 elbow,4 wrist. Set position mode and1Mbps. Mount horns at encoder2048 with the mechanical neutral pose: upper link115° measured from the+Y horizontal direction, forearm45° from+Y, and head face vertical facing+Y. The relative elbow angle is−70°. The shoulder pivot remains atZ115mm and the wrist is approximatelyY25.69mm/Z326.74mm in the CAD reference. Initial software limits are yaw±25°, shoulder±10°, elbow±10°, wrist±10°. `joint_signs` must be measured against the mechanical axes; the shipped all+1 values are calibration defaults, not verified motor handedness.

At startup hardware motion stays disabled unless both `calibrated=true` and `--arm` are supplied. Before torque enable, all feedback must be valid and within3° of indexed neutral. Runtime checks encoder range,9.0–12.6V feedback, temperature below65°C and serial checksums; targets are limited to12°/s. A detected interaction fault sends the most recently measured hold position once and latches; it does not resume after a hand moves away. Restart requires clear sensors and an explicit arm command. Servo status feedback does not establish joint structural strength or torque capacity.

On normal exit the servos keep holding their final position; lights turn off. A power cut releases holding torque. Support the arm before pressing the physical motor stop or removing power. Fit the mechanical support/prop during calibration. If the Pi hangs, feedback checks cannot execute; the independent physical motor stop is the available intervention. No watchdog or safety-rated stop controller is claimed.

## Bench commissioning sequence

1. Keep the arm supported and all motor V+ feeds disconnected. Check DC polarity and continuity; verify3.3V logic,5VLED and12V motor rails independently.
2. Flash and test the exact display with `PING`/`PONG`, then `FACE wink`, `FACE hi`, `FACE happy`. Confirm the canvas is centered and colors are correct before fitting the bezel.
3. Install the Pi software and enable I2C/SPI. With motors supported and stopped, check that channels0–4 each show one0x29 sensor. Cover each aperture individually and confirm the intended channel changes.
4. Test outerRGB at20% or lower and innerW at192/255 or lower. Verify that the inner ring emits white only, and the outer ring has60 independently drivenRGB pixels. Check the diffuser for hot spots and measure surface/LED/CPU temperatures during a30-minute run.
5. Program one servo at a time to IDs1–4, position mode,1Mbps. With the power stop in reach, read neutral positions while supported. Index horns and signs to the CAD reference. Do not substitute uncalibrated encoder2048 for a mechanically checked pose.
6. Verify that the physical stop removes motor voltage even if the Pi is unplugged. Check BCM27 reports stop when either NC2 wire is removed. Release the stop with the arm supported.
7. Set actual persistent USB device paths and measured joint signs/neutral ticks in `config.json`. Set `calibrated=true` only after the previous checks. Use hardware mode without `--arm` first, then run one supported6-second scene with `--arm`.
8. Check full allowed motion for cable clearance, head/arm/base collisions, stability and servo temperature/current. Measure actual load; reduce travel or redesign counterbalance if any servo cannot sustain the pose. Only remove the support after those checks pass.

## Evidence and limits

The host behavior/packet tests are executable and were run in a desktop simulator. Electrical continuity, servo torque, USB power budget, optical ranging and thermal behavior require the physical prototype. Vendor dimensions and electrical ratings are cited above; mounting clearances, wire lengths, fuse coordination and unknown board revisions require fit checks. Budget figures in the CSV are planning allowances, not quotations or stock promises.
