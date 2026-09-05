# Digital release checks

The included validation files record what was checked on the development computer. They should travel with the source and manual when the project is revised. Passing these checks does not replace the first-build measurements in the preceding chapter.

## Executed host software checks

The controller, bench diagnostic, servo packet and face-renderer test suite passed 34 tests. The checks exercise all three expressions over repeated control frames, joint angle and slew limits, the requirement for five sensor readings, stale and invalid measurements, a close-object hold, latched faults, physical stop polarity, lost display or servo feedback, and the one-shot spoken greeting.

Additional tests verify that the inner ring receives only white-channel data at its cap, that servo status packets have the right ID and checksum, that uncalibrated motion is refused, and that a stop uses measured position with a defined fallback when feedback cannot be refreshed. The revision B tests draw the Pi-rendered face for the optional DSI head onto an off-screen surface and check eye, blush, mouth and fault pixels for every expression, run the DSI display adapter against SDL's dummy driver, and prove that the behaviour code never imports the graphics library unless that head is selected. The simulator was exercised without activating any hardware.

## Meshes and assembly

`cad/validation.json` records STL properties from the exporter. `validation/assembly_check.json` records an independent mesh check and static boolean intersection check on the assembled printed solids of both assemblies: 30 printable types are watertight single bodies that fit a 220 mm bed; the standard assembly (37 printed instances) and the optional DSI-head assembly (35 printed instances) show no printed-part overlap above 0.5 mm³ at the indexed neutral pose. `cad/purchased_fit.json` records that the servo envelopes, the 55 mm display envelope and the measured 4-inch display envelope do not intersect any printed part in either assembly.

The intersection check is limited to the indexed neutral pose and the printed components represented in the assembly. It does not establish moving-cable clearance, exact purchased-component fit or a fully collision-free operating envelope; in particular the enclosed links' open clevis has been checked digitally only at neutral, and the 4-inch display's DSI connector position in the envelope comes from a vendor photograph. Follow the manual's supported movement check with the actual hardware before using the programmed expressions.

## PDF and media

`validation/final_report.json` records the final PDF page/bookmark count, text bounds and full decoding of each promotional MP4. The verification script also generates a contact sheet of the manual for visual review. Video metadata and frame counts verify the encoded files; the animation is a visualization of the digital design. The optional head is rendered as a still only; the films show the standard head.

## Display firmware build status

The firmware source includes the exact-board pin mapping and the vendor's two panel initialization variants with attribution. **Its cross-compilation was not completed in this environment:** the required PlatformIO compiler download did not finish, and an alternate download was truncated. No firmware binary or successful cross-compile is claimed. Run the supplied PlatformIO build on a connected development computer before flashing, and test the purchased display on the bench. The optional DSI head does not use this firmware.

## Physical work still required

Actual Raspberry Pi GPIO and USB operation, screen operation, screw engagement, motor holding ability, electrical continuity, stop-relay behavior, sensor optics, light diffusion, stability and enclosed temperatures have not been tested on a physical unit. Neither has the 800 mm DSI cable run of the optional head, nor the servo temperature inside the enclosed links. The specification-based parts and the prototype clearances are intended for a first fit-and-function build. Record the measured results and any revisions on the verification worksheet.
