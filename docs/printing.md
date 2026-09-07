# Printing and finishing

## Prepare one interface before a full print run

Use a 0.4 mm nozzle as the baseline. Print the fit coupon supplied with the CAD, measure its holes and pockets with calipers and test the actual fasteners and bearings. This is especially useful for horizontal holes, which can print smaller than their modeled diameters. Keep the slicer at 100% scale; compensate holes locally or revise the relevant CAD clearance rather than scaling the complete machine.

The part manifest gives quantities, material and orientation. The STL orientation is the manufacturing orientation when the manifest identifies it as such. The assembled model is for viewing and should not be sliced as a single object. Check that each sliced part has continuous perimeters and that screw holes remain open.

## Structural material

Use PETG for the first functional build. For the four enclosed arm halves and load-carrying brackets, start with0.20mm layers, six perimeters, six top/bottom layers and40% gyroid infill. Print each half with its5mm plate on the bed. The26mm walls, servo block and through-bolt boss then rise vertically. The idler halves include16.2mm 625 pockets and distal captive-nut bosses; inspect their slicer paths and use local solid infill. Print one idler half and one driven half per link.

For non-load-bearing covers, start with four perimeters, 0.20 mm layers and 20% infill. Use the orientation and support notes specific to each part. Remove supports without gouging bearing seats or the surfaces that locate circuit boards.

The optional4-inch DSI head adds three files: `head_shell_dsi`, `lcd4_carrier` and `face_ring_dsi`. Print them only for that head and omit the six standard-head parts listed in the schedule. Revision C has no `brow_bracket`, `sensor_pod` or `sensor_retainer` print.

PLA can be useful for quick dimension checks, but warm motors, LED boards and sustained joint loads make it a poor default for the final load-carrying structure. A material change also changes shrinkage and fit; repeat the coupon.

## Frosted light covers

Print both annular diffusers in natural translucent PETG. The small ring covers the white LEDs and the large ring covers the RGB LEDs. Use 0.12–0.16 mm layers and a continuous solid optical face. Preserve the modeled thin wall; do not replace it with sparse infill that leaves a visible lattice in the illuminated area.

Make a small test of the intended wall thickness before committing both rings. Translucent filaments vary greatly in pigment and light transmission. A nominal 1.2 mm optical face is a starting point, not a measured optical specification.

Wet-sand the outside very lightly with 600–1000 grit abrasive to obtain a uniform matte surface. Wash and dry the part before installation. Do not sand the locating lip so far that the diffuser becomes loose. Check the result at the firmware's normal brightness limit with the head closed: rings that look uniform in room light can reveal hotspots when lit.

Keep the opaque separator between the two light paths. A black or charcoal separator helps prevent RGB light washing across the face. Leave an air gap between LEDs and diffuser as defined by the head stack. Avoid adhesives that touch the LED emitters or the LCD glass.

## Fasteners and tolerance

Use the specified metal nuts, washers,625 bearings and servo horns. Deburr holes before insertion. Test the16.2mm pocket and horn slots on `fit_coupon`. A bolt must enter a clearance hole by hand. The M5 idler bolt must clamp the bearing inner race without rubbing the outer race. Tighten opposing fasteners alternately and stop before printed layers or a PCB deform.

If a heat-set insert is specified, test the insert type and soldering-iron temperature on scrap from the same filament. Support the boss while inserting it, allow it to cool completely, and confirm the insert is perpendicular. Do not add heat-set inserts to a design location intended for a through-bolt and captive nut.

Press bearing outer races squarely into their stated seats. Apply force to the race being fitted. A bearing that becomes rough after installation is a sign of an undersized or distorted seat; correct the seat before assembling the joint.

## Harness preparation

Make a service loop at each joint, and move the unpowered mechanism through its intended travel while watching the loop. The wire must not become taut, rub a sharp printed edge, enter a gear/horn gap or prevent the joint from reaching its limit. Fit the provided cable guides and add soft sleeving where the harness moves against a surface.

Use flexible stranded wire for moving runs. The five short sensor branches remain fixed in the pedestal. Keep their I2C wiring away from the6V servo distribution and strain-relieve each small connector. A STEMMA QT connector is a signal interconnect, not a high-current power connector.

## Record the first print

Record printer, nozzle, material brand, layer height, wall count, infill, measured coupon hole sizes and any CAD clearance change. Weigh the completed head with its display, lights, screws and wiring. Use the measured head mass when reviewing the arm torque calculation; record the five fixed pedestal sensors with the base mass.

Estimated print duration and filament mass depend on the slicer and printer. The CAD validation report includes geometric volume; the slicer's estimate after applying the actual walls and infill is the useful production estimate.
