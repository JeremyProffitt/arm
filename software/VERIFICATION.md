# Verification record

Date:2026-09-07. Development host:Windows, Python3.13.14.

`python -m unittest discover -s tests -v`: **37 tests passed**. Coverage includes three-scene joint limits and12°/s slew, all five pedestal sensor names/order, stale/NaN/no-return/near faults, paired rear and front-side gestures, latched holds, motor-stop polarity, display/PCA9685 communication faults, one-shot speech, and RGBW white-only limits.

PWM tests cover the DS3218's500-2500µs/270° conversion, a known50Hz PCA9685 duty value, four unique configured channels, calibrated neutral gating, neutral command on arm, last-command hold semantics, and a one-channel commissioning command that disables the other three outputs. The PCA9685 driver is imported only when hardware is opened. Tests do not claim real PWM timing or servo motion.

Face tests draw the standard expression logic for the optional720×720 DSI head onto an off-screen surface and check eye, blush, mouth, offline and fault pixels. `DsiDisplay` is exercised with SDL's dummy driver. Importing the main hardware module does not import pygame unless the DSI path is selected.

`python -m luma.app --scene hi --seconds 1` is the non-hardware simulator check. It prints one Hi event, bounded joint motion, W192 and no fault. The test suite also runs the wink/happy trajectories for500 frames each.

The Raspberry Pi, PCA9685, DS3218MG servos,6V regulator, sensors, stop relay, screens and light rings were not present in this development workspace. No physical I2C, PWM, position, current, torque, optical or thermal result is claimed. The PCA9685 can report controller communication but the selected servos provide no readable shaft, load, current or temperature feedback.

The standard display source targets Waveshare SKU28514 and contains both documented panel initialization tables. **Cross-compilation remains unverified.** The earlier PlatformIO compiler download did not complete and an alternate download was truncated. No firmware binary or physical display test is claimed.

The optional Waveshare4inch DSI LCD(C) path remains digitally verified only through pygame's dummy driver. Actual `kmsdrm` output, vendor overlays, panel rotation, touch/backlight control and the800mm DSI FPC run require the physical Pi and display.

Run the one-channel servo check only with the horn disconnected from the arm:

```console
.venv/bin/python -m luma.bench servo --joint yaw --pulse-us 1500 --seconds 2 --confirm-unloaded
```

The command is bounded to10seconds, disables all non-selected channels, and removes the selected PWM pulse on exit. It does not limit motor current or detect shaft motion. Use the independent motor stop and the regulated fused6V rail described in the electrical chapter.
