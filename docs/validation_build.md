# First-build verification and maintenance

## Verify before enclosing

Power and exercise the display, rings and each pedestal sensor on the bench. Confirm that the large ring shows the intended colors, the small ring uses only its white channel during lamp operation, and every wall direction is associated with its labeled multiplexer port.

Connect one unloaded DS3218MG at a time to its fused6V feed and PCA9685 channel. Use the bounded one-channel command in the software guide to center it at1500µs, then remove power before attaching the horn. Save each measured neutral pulse and direction with the assembled unit. PWM servos have no readable shaft position.

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
| Pitch idlers | Three625 bearings square in their pockets; M5 smooth shanks load only inner races; captive nuts seated; no axial bind or play. |
| Pedestal sensors | Five boards on four screws each; component face outward; apertures open; one strain-relieved STEMMA QT cable per board. |
| Enclosed links | DS3218 case seated in the41.2 ×20.7mm pocket; halves meet without crushing it; harness has slack; horn, idler and servo tab clear the commissioned travel. |
| Optional DSI head | Carrier pads bear on all four display bosses; face ring bears on the foam rim only, never on the glass; FFC bend radius above 10 mm at every turn; picture stable at full backlight for 30 minutes with the arm closed. |

## Electrical and motion acceptance

Start with the arm supported and a single joint enabled at reduced speed. Move a few degrees about the calibrated neutral position, verify the sign of rotation, then return to neutral. Repeat for each joint before a coordinated expression. A wrong sign or zero offset must be corrected before enlarging the motion range.

Confirm that the hardware motor-power disconnect removes the regulated6V rail independently of software. Support the head when testing a power cut. Verify the software fault response for a missing sensor, invalid range, lost PCA9685 communication and lost display connection. A live PCA9685 does not prove that a servo moved.

Run the normal white-light and RGB settings with the head assembled. Record temperatures at5,15 and30 minutes at the LED support, screen,6V regulator and most heavily loaded servo. The DS3218 gives no telemetry, so measure accessible surfaces directly. Use45°C on a printed enclosure surface as a conservative investigation threshold for the first PETG build, not as a product certification.

Verify front, front-left, rear-left, rear-right and front-right with a matte target at several distances. Record ranges and reject invalid readings rather than treating them as open space. Check for wall-edge reflections. These five horizontal cones do not cover every direction or arm pinch point.

## Verification worksheet

| Measurement | First-build result |
| --- | --- |
| Build date / builder | __________________________________ |
| Printer and filament | __________________________________ |
| Component revisions | __________________________________ |
| Completed head mass | __________________________________ |
| Base / ballast mass | __________________________________ |
| Motor supply at motion peak | __________________________________ |
| Regulated servo rail / PCA9685 check | __________________________________ |
| LED supply at normal brightness | __________________________________ |
| Pi undervoltage check | __________________________________ |
| Maximum observed enclosure / servo / regulator temperature | __________________________________ |
| Mechanical travel limits and neutral pulse widths | __________________________________ |
| Sensor directions and valid range test | __________________________________ |
| Hardware power-cut test | __________________________________ |

## Care and service

Inspect the horn screws, bearing mounts and cable strain relief after the first hour of motion and again after the first week. Stop using a printed part if a layer crack, whitening around a fastener or increasing joint play appears. Correct the cause before replacing the part.

Clean the diffuser with a soft damp cloth. Keep solvents away from printed surfaces and the display. Dust near a time-of-flight aperture can change measurements; remove it without pushing debris onto the optical package.

For service, shut down the Pi, disconnect the low-voltage supplies and support the arm before opening a joint or loosening the head. Store the final calibration, BOM revision and any dimensional changes with the project so the next printed replacement matches the machine.
