# LUMA revision C - pedestal sensors and inventory servos

Single source of truth for revision C. A fresh run must be able to resume from this file alone.

Repository root: `C:\dev\arm`.
Branch: `main`.
Python: `C:\dev\arm\.venv\Scripts\python.exe` (3.13.14).
OpenSCAD: `C:\Program Files\OpenSCAD\openscad.com` (2021.01).
The repository has no Git remote, so this run commits locally and records that no push target exists.

## Locked decisions (user-confirmed; do not revisit)

- 2026-09-07 - user: "a number of things to fix and update, add holes for the VL53L1X adafuit board and mounting holes on the inside of the base to mount them.  change out the servos for the ones listed in inventory."
- 2026-09-07 - user: "yes, the peddestal.  all 5 sensors should be in the wall"
- 2026-09-07 - user: "use this board for pwm PCA9685"
- 2026-09-07 - available positional-servo inventory includes eight `Miuzei DS3218MG` 20 kg digital servos with 270-degree control. The other listed inventory consists of two continuous-rotation `SPT5525LV-360`, four `MG996R`, four 180-degree `MG995`, and fifteen `SG90` servos.
- Existing revision B decisions remain in force unless revision C explicitly changes them. Revision B is committed at `205a69b`.

## Design decisions taken by the run (defaults; report at completion)

- Use four matching Miuzei DS3218MG 270-degree positional servos, one for yaw, shoulder, elbow, and wrist. Do not use the continuous-rotation SPT5525LV-360 units because the joints require commanded positions. Do not mix MG995, MG996R, or SG90 units into the four-axis chain.
- Use the user-selected PCA9685 board at I2C address `0x40`, upstream of the existing TCA9548A-compatible sensor mux at `0x70`. Use channels 0 through 3 for yaw through wrist and 50 Hz PWM.
- Replace the 12 V ST3215 motor rail with a regulated 6 V rail. Four DS3218 units have a documented combined stall current of 8.8 A at 6.8 V; specify a 6 V regulator with at least 10 A continuous capability and retain one fused branch per servo. The existing 12 V external supply remains the upstream source.
- The PCA9685 controls pulse position but provides no joint-position, current, or temperature feedback. Software must fail on PCA9685 communication errors and must not claim physical feedback. Physical commissioning must use supported motion, measured PWM calibration, restricted travel, the existing independent motor-power stop, and visual checks.
- Put all five sensor boards behind the 216 mm pedestal wall. Use five equal 72-degree sectors, with the front sensor centered at `+Y`: front at 90 degrees, front-left at 162, rear-left at 234, rear-right at 306, and front-right at 18. This leaves the rear center at 270 degrees clear for the two existing cable ports.
- Each Adafruit 3967 board mounts directly to four internal bosses through its documented 2.5 mm holes on a 20.32 x 12.70 mm pattern. The board outline is 25.40 x 17.78 mm. Each wall position gets one open optical aperture; no printed optical window is used.
- Remove the external head sensor pods, their retainers, the DSI brow bracket, and all obsolete head pod holes. The existing head/display/light variants and arm pivot pitches remain otherwise unchanged.
- Raise the pedestal wall and yaw stack by 6 mm so the 40.5 mm DS3218 case clears the ballast and lid. The shoulder axis moves from Z115 to Z121; the 140 mm and 120 mm linkage pitches and indexed angles do not change.
- Support the three pitch joints on both sides. The driven side uses the supplied straight 25T servo arm through two adjustable radial slots. The opposite side uses a 625-2RS bearing, M5 axle bolt, and captive M5 nut. Widen the fork and enclosed links from 44 mm to 52 mm between plates to clear the DS3218 case and idler hardware.
- Rename the five physical channels to `front`, `front_left`, `rear_left`, `rear_right`, and `front_right`. The rear gesture uses either rear sensor. The side gesture uses either front-side sensor. All five remain mandatory obstruction inputs.
- Revision label becomes `Rev C / 07 Sep 2026` in source and generated deliverables.

## Verified facts

- 2026-09-07 - `git status --short --branch` returned only `## main`; the worktree was clean before revision C.
- 2026-09-07 - `git remote -v` returned no rows. There is no configured push or CI target.
- 2026-09-07 - drive C had 289,149,521,920 free bytes before work began.
- 2026-09-07 - the Miuzei DS3218 product datasheet at `https://images-na.ssl-images-amazon.com/images/I/81Lbgu%2BnG6L.pdf` specifies a 40 x 20 x 40.5 mm body, 4.8-6.8 V operation, 18 kg-cm and 1.8 A stall at 5 V, 21.5 kg-cm and 2.2 A stall at 6.8 V, 500-2500 us PWM, 1500 us neutral, 50-330 Hz, and a 180- or 270-degree variant.
- 2026-09-07 - the official Adafruit Eagle board file `Adafruit VL53L1X.brd` at `https://github.com/adafruit/Adafruit-VL53L1X-PCB` defines a 25.40 x 17.78 mm rounded board and four plated 2.5 mm mounting holes at `(2.54,2.54)`, `(22.86,2.54)`, `(2.54,15.24)`, and `(22.86,15.24)`, giving a 20.32 x 12.70 mm pattern centered on the board.
- 2026-09-07 - Adafruit documents the PCA9685 as a 16-channel I2C PWM controller and requires separate servo V+ power. The board logic supply does not power the servos. Source: `https://learn.adafruit.com/16-channel-pwm-servo-driver/hooking-it-up`.
- 2026-09-07 - Pololu D42V110F6 item 5673 is a documented 6 V, nominal 11 A regulator with a 6-60 V input range. Source: `https://www.pololu.com/product/5673`.
- Revision B uses external printable `sensor_pod` and `sensor_retainer` parts, head-shell pod holes, a DSI `brow_bracket`, four Waveshare ST3215 serial bus servos, and `software/luma/servo_bus.py`. These paths are replaced, not retained in parallel.
- Revision B checks passed at commit `205a69b`: 34 host tests, watertight printable meshes, and zero indexed-pose printed-part intersections for both head variants.

## Preconditions

- [x] Repository, branch, worktree state, disk space, Python, and OpenSCAD were checked with non-interactive commands.
- [x] Primary-source dimensions for the Adafruit sensor board and Miuzei servo were checked.
- [x] The operator selected the PCA9685 and confirmed all five sensors belong in the pedestal wall.
- [x] No deployment, external audience, destructive data operation, or scheduled automation is part of this run.

## Stop conditions (only these)

- An OpenSCAD export for a changed part fails deterministically after three geometry corrections.
- The new single-output servo joints cannot be given a mechanically supported opposite-side pivot without changing the locked linkage pitches or head interface.
- Required credentials or an external resource become necessary. There is currently no remote, deployment, or hardware bench in scope.

All other failures are classified, changed before retry, capped as stated below, recorded in the execution log, and worked around while independent work continues.

## Workstreams

### sensor-relocation - five direct-mounted boards in the pedestal wall

- [x] pedestal-geometry - Add five wall apertures and four internal M2.5 pilot bosses per board to `cad/luma.scad`; remove conflicting wall vents while preserving lid ventilation and rear cable ports. Remove head pod apertures and obsolete pod/bracket parts. Definition of done: `python cad/build.py base_tub head_shell face_center head_shell_dsi` exits 0 and each changed mesh is watertight, positive-volume, one body, and within the 220 mm bed limit.
- [x] sensor-assembly - Place five visual-only board envelopes behind the pedestal wall in both assembly manifests and remove all head pod instances. Definition of done: `python cad/check_purchased_fit.py` reports no sensor/printed-part intersections except the intentional board-to-standoff contacts excluded by the checker, and `python validation/check_assembly.py` reports zero overlaps above 0.5 mm3.
- [ ] sensor-docs - Update CAD, electronics, wiring, software channel names, assembly instructions, and validation text for the five perimeter directions. Definition of done: `python docs/build_bom.py` exits 0 and `rg -n "sensor_pod|sensor_retainer|TOF_DOWN|down sensor|downward sensor" cad docs electronics software README.md START_HERE.html` returns no live revision C instructions.

### inventory-servo-conversion - four DS3218MG joints controlled by PCA9685

- [x] servo-mechanics - Replace ST3215 body clamps, dual-horn assumptions, horn interfaces, and purchased envelopes with DS3218 geometry plus an opposite-side supported pivot for each pitch joint; keep the existing 6808-supported yaw. Definition of done: focused CAD export exits 0, purchased-fit check reports zero unintended intersections, and assembly check reports zero printed-part overlaps above 0.5 mm3.
- [ ] servo-electronics - Replace ST3215/Bus Adapter A rows and 12 V motor branches with four inventory DS3218MG units, PCA9685 control, regulated 6 V power, branch fusing, and required bulk capacitance. Definition of done: generated BOM and wiring schedule contain PCA9685/DS3218/6 V data and contain no live ST3215 or bus-adapter route.
- [ ] servo-software - Replace the serial bus driver with a PCA9685 PWM driver; use config-defined channels, calibrated neutral pulses, pulse limits, and angle span; report controller communication health without claiming servo feedback. Extend the existing control tests. Definition of done: `C:\dev\arm\.venv\Scripts\python.exe -m unittest discover -s tests -v`, run in `C:\dev\arm\software`, exits 0.

### release-regeneration - revision C user-facing artifacts

Depends on both workstreams above.

- [ ] cad-release - Run the full CAD build and both geometry checks. Retry policy: classify each failure; correct geometry before rerun; maximum three focused corrections per changed part. Definition of done: `python cad/build.py`, `python cad/check_purchased_fit.py`, and `python validation/check_assembly.py` all exit 0.
- [ ] media-release - Regenerate standard and DSI stills and the three clips so no obsolete external sensor pods or ST3215 envelopes remain. Watcher/restart policy: each foreground command reports nonzero exit; retry once only after a deterministic fix or once after a transient renderer failure. Definition of done: `python media/sources/validate_media.py` exits 0 and the standard and DSI hero images show pedestal apertures with clean heads.
- [ ] document-release - Regenerate the BOM, engineering drawings, manual, index, and verification report with revision C labels. Definition of done: `python validation/verify_project.py` exits 0 with `failures: []`.
- [ ] package-release - Rebuild both archives and hash inventory. Definition of done: `python docs/package_project.py` exits 0 and both ZIP integrity checks pass inside that command.
- [ ] review-release - Run the repository code-review skill against revision B commit `205a69b`, fix in-scope findings, rerun focused verification, inspect the final diff, commit only revision C files, and attempt push only if a remote appears. Definition of done: clean `git status --short`, a focused revision C commit on `main`, and either a successful push or a logged confirmation that no remote exists.

## Execution log

- 2026-09-07 - Read the implementation skill. It requires focused tests, a final full test run, code review, and a commit.
- 2026-09-07 - Inspected `plan.md`, CAD source/build/fit checks, assembly checks, BOM and wiring sources, controller/config/tests, document generators, current renders, and revision B history. Confirmed the revision B implementation uses external head pods and ST3215 serial bus servos.
- 2026-09-07 - Verified clean `main`, no Git remote, Python 3.13.14, OpenSCAD 2021.01, and 289,149,521,920 bytes free on drive C.
- 2026-09-07 - Read the official Adafruit Eagle board geometry and Miuzei DS3218 datasheet. Selected four matching DS3218MG units and direct four-hole sensor mounting as the minimum coherent use of the confirmed inventory.
- 2026-09-07 - User confirmed the 216 mm pedestal, all five sensors in its wall, and PCA9685 PWM control. Revision C plan started.
- 2026-09-07 - Focused sensor exports: `python cad/build.py base_tub head_shell face_center head_shell_dsi` returned `Failures: []`; all four changed meshes were watertight single bodies. A rendered base preview exposed conflicts with a lid post and rear rectangular port. Moved lid posts to 42/66/126/198/258/342 degrees and grouped the cable ports at 270/282 degrees. `python cad/build.py base_tub base_lid` then returned `Failures: []`.
- 2026-09-07 - Replaced the ST3215 dual-output geometry with four DS3218MG envelopes, straight-horn slots on the driven sides, and 625/M5 idler interfaces on the opposite sides. Raised the base/yaw stack 6 mm and widened the pitch-joint plate spacing to 52 mm. The first complete check identified five deterministic placement/clearance errors. Corrected the turntable web height/shape, shoulder flange and keeper clearances, wrist tab notch, and head-spacer orientation.
- 2026-09-07 - Focused final CAD checks: `python cad/build.py head_yoke horn_spacer` returned both parts `True 1` and `Failures: []`; `python cad/check_purchased_fit.py` returned empty intersection lists for `standard` and `dsi_head`; `python validation/check_assembly.py` returned `standard: 24 instances, 0 overlaps above0.5mm3; dsi_head: 21 instances, 0 overlaps above0.5mm3`.
