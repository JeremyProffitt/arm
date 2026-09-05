# First-build verification and maintenance

## Verify before enclosing

Power and exercise the display, rings and each sensor on the bench. Confirm that the large ring shows the intended colors, the small ring uses only its white channel during lamp operation and every sensor is associated with its labeled multiplexer port. This makes a reversed ring or swapped cable easy to locate while it is still accessible.

Connect each motor individually to set its unique ID. Confirm the servo voltage variant and the expected operating mode before attaching the horn. Mark the calibrated neutral pose on the fixed and moving brackets. Save the calibration with the assembled unit rather than assuming a replacement motor will have the same zero offset.

## Mechanical acceptance record

| Check | Acceptance and record |
| --- | --- |
| Printed interfaces | Actual purchased boards and horns seat without forced deflection; record component revision. |
| Fasteners | Required washers/nuts present, rotating surfaces free and wires not under screw heads. |
| Bearings and joints | Free motion when unpowered; no binding, visible cracks or loose axial play. |
| Cable routing | Slack remains throughout allowed travel; no pinched insulation or tight connector bends. |
| Stability | Base secured as specified; verify measured mass and center of gravity at the maximum allowed reach. |
| Head mass | Weigh the completed head and replace assumed mass in the torque calculation. |
| Horns | Metal horns secured with the servo's correct center screw; no printed spline substitutes. |
| Enclosed links | Servo seated on the pocket floor with its rear connector in the notch; halves meet at the mid-plane without crushing the case; harness passes the wall port with slack; open clevis clears the previous block and keeper through the commissioned travel. |
| Optional DSI head | Carrier pads bear on all four display bosses; face ring bears on the foam rim only, never on the glass; FFC bend radius above 10 mm at every turn; picture stable at full backlight for 30 minutes with the arm closed. |

## Electrical and motion acceptance

Start with the arm supported and a single joint enabled at reduced speed. Move a few degrees about the calibrated neutral position, verify the sign of rotation, then return to neutral. Repeat for each joint before a coordinated expression. A wrong sign or zero offset must be corrected before enlarging the motion range.

Confirm that the hardware motor-power disconnect removes motor power independently of software. Support the head when testing a power cut: these joints are not self-locking. Verify the software fault response for a missing sensor, invalid range, lost motor connection and lost display connection using the documented tests and a controlled bench check.

Run the normal white-light and RGB settings with the head assembled. Record temperatures at 5, 15 and 30 minutes at the LED support, near the screen and at the most heavily loaded servo. For the first PETG build, use 45 °C on an accessible printed enclosure surface as a conservative investigation threshold; it is a project test criterion, not a material or product certification. If temperature continues to rise, reduce brightness or load and improve the relevant airflow before extending the test.

Verify the five optical directions with a matte target at several distances. Record ranges and reject invalid readings rather than treating them as open space. Check for reflections from the diffuser, desk and nearby arm components. These five sensors do not cover every direction around the mechanism, and the behavior must stay inside the commissioned motion envelope.

## Verification worksheet

| Measurement | First-build result |
| --- | --- |
| Build date / builder | __________________________________ |
| Printer and filament | __________________________________ |
| Component revisions | __________________________________ |
| Completed head mass | __________________________________ |
| Base / ballast mass | __________________________________ |
| Motor supply at motion peak | __________________________________ |
| LED supply at normal brightness | __________________________________ |
| Pi undervoltage check | __________________________________ |
| Maximum observed enclosure temperature | __________________________________ |
| Mechanical travel limits and zero offsets | __________________________________ |
| Sensor directions and valid range test | __________________________________ |
| Hardware power-cut test | __________________________________ |

## Care and service

Inspect the horn screws, bearing mounts and cable strain relief after the first hour of motion and again after the first week. Stop using a printed part if a layer crack, whitening around a fastener or increasing joint play appears. Correct the cause before replacing the part.

Clean the diffuser with a soft damp cloth. Keep solvents away from printed surfaces and the display. Dust near a time-of-flight aperture can change measurements; remove it without pushing debris onto the optical package.

For service, shut down the Pi, disconnect the low-voltage supplies and support the arm before opening a joint or loosening the head. Store the final calibration, BOM revision and any dimensional changes with the project so the next printed replacement matches the machine.
