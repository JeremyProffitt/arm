# Printing and finishing

## Prepare one interface before a full print run

Use a 0.4 mm nozzle as the baseline. Print the fit coupon supplied with the CAD, measure its holes and pockets with calipers and test the actual fasteners and bearings. This is especially useful for horizontal holes, which can print smaller than their modeled diameters. Keep the slicer at 100% scale; compensate holes locally or revise the relevant CAD clearance rather than scaling the complete machine.

The part manifest gives quantities, material and orientation. The STL orientation is the manufacturing orientation when the manifest identifies it as such. The assembled model is for viewing and should not be sliced as a single object. Check that each sliced part has continuous perimeters and that screw holes remain open.

## Structural material

Use PETG for the first functional build. For arm links and load-carrying brackets, start with 0.20 mm layers, five perimeters, six top/bottom layers and 40% gyroid infill. Increase local solid infill around fasteners if your slicer supports modifier volumes. Print link plates flat so their length lies in the XY plane.

For non-load-bearing covers, start with four perimeters, 0.20 mm layers and 20% infill. Use the orientation and support notes specific to each part. Remove supports without gouging bearing seats or the surfaces that locate circuit boards.

PLA can be useful for quick dimension checks, but warm motors, LED boards and sustained joint loads make it a poor default for the final load-carrying structure. A material change also changes shrinkage and fit; repeat the coupon.

## Frosted light covers

Print both annular diffusers in natural translucent PETG. The small ring covers the white LEDs and the large ring covers the RGB LEDs. Use 0.12–0.16 mm layers and a continuous solid optical face. Preserve the modeled thin wall; do not replace it with sparse infill that leaves a visible lattice in the illuminated area.

Make a small test of the intended wall thickness before committing both rings. Translucent filaments vary greatly in pigment and light transmission. A nominal 1.2 mm optical face is a starting point, not a measured optical specification.

Wet-sand the outside very lightly with 600–1000 grit abrasive to obtain a uniform matte surface. Wash and dry the part before installation. Do not sand the locating lip so far that the diffuser becomes loose. Check the result at the firmware's normal brightness limit with the head closed: rings that look uniform in room light can reveal hotspots when lit.

Keep the opaque separator between the two light paths. A black or charcoal separator helps prevent RGB light washing across the face. Leave an air gap between LEDs and diffuser as defined by the head stack. Avoid adhesives that touch the LED emitters or the LCD glass.

## Fasteners and tolerance

Use the specified metal nuts, washers and servo horns. Deburr holes before insertion. A bolt should enter a clearance hole by hand without driving threads into the plastic. Seat the head and washer firmly, then stop before the printed layers visibly deform. Tighten opposing fasteners alternately to prevent distorting a PCB cradle or joint bracket.

If a heat-set insert is specified, test the insert type and soldering-iron temperature on scrap from the same filament. Support the boss while inserting it, allow it to cool completely, and confirm the insert is perpendicular. Do not add heat-set inserts to a design location intended for a through-bolt and captive nut.

Press bearing outer races squarely into their stated seats. Apply force to the race being fitted. A bearing that becomes rough after installation is a sign of an undersized or distorted seat; correct the seat before assembling the joint.

## Harness preparation

Make a service loop at each joint, and move the unpowered mechanism through its intended travel while watching the loop. The wire must not become taut, rub a sharp printed edge, enter a gear/horn gap or prevent the joint from reaching its limit. Fit the provided cable guides and add soft sleeving where the harness moves against a surface.

Use flexible stranded wire for moving runs. Keep the I2C wiring short, route power and motor wiring away from it where practical, and retain the sensor cables so their small connectors do not take bending loads. A STEMMA QT connector is a signal interconnect, not a high-current power distribution connector.

## Record the first print

Record printer, nozzle, material brand, layer height, wall count, infill, measured coupon hole sizes and any CAD clearance change. Weigh the completed head with its display, sensors, screws and wiring. Use the measured head mass when reviewing the arm torque calculation.

Estimated print duration and filament mass depend on the slicer and printer. The CAD validation report includes geometric volume; the slicer's estimate after applying the actual walls and infill is the useful production estimate.
