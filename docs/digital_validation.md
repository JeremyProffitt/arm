# Digital release checks

The included validation files record what was checked on the development computer. They should travel with the source and manual when the project is revised. Passing these checks does not replace the first-build measurements in the preceding chapter.

## Executed host software checks

The controller, bench diagnostic, PWM and face-renderer suite passed38 tests. It exercises all three expressions, angle/slew limits, the five pedestal channel names and order, stale/invalid/near ranges, latched faults, stop polarity, lost display or PCA9685 communication, and the one-shot greeting.

Additional tests verify the500-2500µs/270° conversion, a known PCA9685 duty value, one-channel commissioning with the other channels disabled, neutral calibration gating, and white-channel limits. Face tests render the optional DSI output off-screen and check expression/fault pixels. The simulator and tests activate no physical hardware.

## Meshes and assembly

`cad/validation.json` records exporter mesh properties. `validation/assembly_check.json` covers27 printable types and reports zero printed-part overlaps above0.5mm³ in the standard24-instance and DSI21-instance assemblies. `cad/purchased_fit.json` reports no intersection for four DS3218MG case/tab envelopes, five Adafruit3967 pedestal-board envelopes, and either display envelope.

The intersection check is limited to the indexed pose. It excludes real horns/splines,625 bearings, screws and moving cables. It cannot prove the supplied straight-horn hole pattern, physical sensor alignment, or a collision-free moving envelope. The4-inch DSI connector position remains estimated from a vendor photograph.

## PDF and media

`validation/final_report.json` records the final PDF page/bookmark count, text bounds and full decoding of each promotional MP4. The verification script also generates a contact sheet of the manual for visual review. Video metadata and frame counts verify the encoded files; the animation is a visualization of the digital design. The optional head is rendered as a still only; the films show the standard head.

## Display firmware build status

The firmware source includes the exact-board pin mapping and the vendor's two panel initialization variants with attribution. **Its cross-compilation was not completed in this environment:** the required PlatformIO compiler download did not finish, and an alternate download was truncated. No firmware binary or successful cross-compile is claimed. Run the supplied PlatformIO build on a connected development computer before flashing, and test the purchased display on the bench. The optional DSI head does not use this firmware.

## Physical work still required

Actual Raspberry Pi GPIO/I2C/USB operation, PCA9685 output,6V regulator cooling, horn/idler fit, servo holding ability, electrical continuity, stop behavior, sensor optics, light diffusion, stability and enclosed temperatures have not been tested on a physical unit. The DS3218 servos expose no position/current/temperature telemetry. The800mm optional DSI cable is also untested. Record all first-build results on the worksheet.
