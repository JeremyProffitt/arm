# LUMA mechanical assembly, revision C

The editable geometry is `cad/luma.scad`. `cad/build.py` exports printable parts, two assembly manifests, purchased-part envelopes, and mesh measurements. Open `cad/assembly.scad` for the standard head or `cad/assembly_dsi.scad` for the optional4-inch DSI head. Files under `cad/visual_only` are not printable parts.

Revision C moves all five Adafruit3967 VL53L1X boards from external head pods to direct mounts behind the pedestal wall. It removes the pod, retainer, and DSI brow-bracket parts and closes the old head penetrations. It also replaces four dual-output ST3215 bus servos with four inventory Miuzei DS3218MG 270-degree PWM servos. The links and yoke are wider, each pitch joint has a625 bearing opposite its single driven horn, and the pedestal/yaw stack is6mm taller. Link pitches, indexed angles, displays, and light-ring geometry remain unchanged.

The indexed neutral has the upper link115° and forearm45° counterclockwise from forward+Y. The relative elbow angle is−70°. Pitch axes run alongX and yaw runs alongZ. Dimensions are: base diameter216mm and wall height56mm; shoulder axisZ121mm; upper pitch140mm; forearm pitch120mm; head diameter176mm and optical depth42mm. The rear head plane center is aboutY46.7mm/Z332.7mm, and the housing top is about420.7mm. Rubber feet add5mm.

## Purchased geometry and fit datums

The Miuzei DS3218 datasheet specifies a40 × 20 × 40.5mm body, 4.8-6.8V PWM control, and a300mm lead. The model uses a conservative body envelope fromX−30..10 relative to the shaft, Y±10, and Z−40.5..0 from the output-side case plane. The mounting-tab envelope is54.5mm long at the datasheet's27.7mm height datum. The included straight metal arm and25T spline stay purchased parts. Its attachment-hole positions and thread are not dimensioned, so the printed driven interfaces use a7mm center clearance and two3.4mm radial slots at12-18mm and20-25mm. Measure the actual horn before selecting bolts. Source: https://images-na.ssl-images-amazon.com/images/I/81Lbgu%2BnG6L.pdf .

Each pitch joint is supported on both sides. The driven plate attaches to the straight metal servo arm through a3.3mm printed spacer. The opposite plate carries a625-2RS bearing, 5mm bore ×16mm OD ×5mm wide. An M5 precision-shank or shoulder bolt clamps only the bearing inner race to a captive M5 nut in the parent idler boss. Use thin thrust washers that do not touch the outer race. The yaw platform remains independently supported by one6808-2RS bearing, 40 ×52 ×7mm.

The Adafruit3967 board outline and four plated holes come from Adafruit's Eagle board file. The board is25.40 ×17.78mm. Its2.5mm holes form a20.32 ×12.70mm pattern centered on the optical package. The pedestal uses four6mm bosses with2.1mm blind pilots per board. The board's component face points outward and its sensor looks through a10 ×10mm open wall aperture. Source: https://github.com/adafruit/Adafruit-VL53L1X-PCB .

The standard display remains the55 ×55mm Waveshare ESP32-S3-Touch-LCD-1.85. It uses a55.8mm edge pocket and foam shims; no guessed board holes. The optional Waveshare4inch DSI LCD(C) remains a round720 ×720 panel in aØ126mm case with four M4 bosses on a75 ×75mm square. Its controller-board/connector envelope is measured from the vendor STEP. Verify every purchased connector and glass projection before tightening.

## Print settings and fit coupon

Print all units in millimeters at100%. The216 ×216mm base leaves only2mm per edge on a220mm bed. Use PETG,0.20mm layers, four walls for general parts, and six walls/40% gyroid for the four link halves and joint supports. The link halves print with their5mm outer plates on the bed. The head yoke prints on its rear mounting plate, rotated180° aboutX, with supports under the fork ears. The removed sensor pods, retainers, and brow bracket are not part of revision C.

Print `fit_coupon` first. It carries3.0/3.2/3.4/3.6mm bores, the16.2mm 625 pocket, and the DS3218 straight-horn slots. Tune only the affected CAD clearance; never scale the full mechanism. A625 bearing must seat squarely without force through its inner race. Clear through-holes by hand. The2.1mm base sensor and Pi pilots are for carefully started M2.5 screws. Do not force a screw or bend a PCB.

Print the light diffusers in natural/translucent PETG at0.15mm layers, three perimeters, and100% infill. Preserve the1.2mm optical skin. Do not put printed plastic, frosting, adhesive, or an untested IR window over any ToF aperture.

## Prepare metal parts

1. Make theØ180 ×6mm mild-steel ballast from `cad/ballast_plate.dxf` or the dimensioned SVG. Drill fourØ4.4 holes at(±45,±35) and fourØ3.4 holes at(±26,−36/−8). Deburr and protect it from corrosion. Keep the center solid.
2. Confirm the6808 bearing is40 ×52 ×7mm and all three625 bearings are5 ×16 ×5mm. Test the printed pockets before assembly.
3. Inspect all four inventory DS3218MG units and straight25T arms. Confirm the servo is the270° position variant, not a continuous-rotation unit. Measure the metal-arm hole diameter, spacing, thickness, center-screw engagement, and clearance over the case. Dry-fit each printed radial slot before power is applied.
4. Test each M5 idler stack outside the arm. The smooth bolt section must span the bearing inner race. The washer and printed plate must not touch the rotating outer race. The captive nut must seat without splitting its boss.

## Assemble the pedestal sensors and weighted base

5. Put the steel disc on the3mm base floor. Attach the yaw cradle atZ9 with fourM3x16 bolts through the asymmetric pattern. Keep all underside hardware above the rubber-foot contact plane.
6. Identify front as+Y. The five sensor centers are front90°, front-left162°, rear-left234°, rear-right306°, and front-right18°. Insert oneM2.5x6 screw through each board hole from the PCB's inner side. Put the component face toward its wall opening and start all four screws into the matching blind pilots. Tighten in a cross pattern only until the board cannot rock. Confirm the optical package is centered and unobstructed. Connect one side STEMMA QT socket and strain-relieve the cable inside the wall.
7. Place the yaw DS3218MG with its shaft vertical, its body toward−Y, its case bottom atZ12, and its output-side case plane atZ52.5. The rear-body cradle avoids the servo's mounting ears. Fit the yaw keeper atZ52.5 with twoM3x50 bolts atX±18.5/Y−27. Tighten only enough to secure the case.
8. Mount the electronics tray atZ14 on four5mm metal spacers with fourM4x25 bolts through base, ballast, spacer, and tray. Mount the Pi on its standoffs. Use the universal tray slots for the PCA9685, sensor mux,6V regulator, and insulated distribution hardware; their exact board revisions are not assigned guessed hole coordinates. Keep the regulator ventilated. Keep the external AC adapter and any oversized high-current enclosure outside the compact base.
9. Use the round rear wall port at270° and rectangular port at282° for external power/USB. Add grommets and strain relief. The six lid posts sit at42/66/126/198/258/342° between the sensor sectors and rear ports.
10. Seat the6808 in the lid's52.15mm pocket. The turntable's39.75mm neck passes through its40mm bore. Below the lid, attach the3mm tangential horn web to the yaw servo's straight metal arm through the adjustable slots. The web stays below the lid disk and the neck carries load through the bearing. Verify free±25° yaw before fitting sixM3x12 lid screws. The turntable top and shoulder-tower datum areZ74.

## Assemble the shoulder and enclosed links

Each link has an idler half and a driven half. LocalX runs from proximal pivot to distal servo shaft:140mm for the upper link and120mm for the forearm. The5mm plates occupy assembled Z−31..−26 and+26..+31. Each half has26mm-deep walls that meet atZ0. The DS3218 rear-case pocket is41.2mm across the axis and20.7mm across the body. The walls start atX28, leaving the proximal clevis open. A21 ×9mm cable port remains on the inner wall. ThreeM3x70 bolts close each link: one atX35 and two around the distal block atY±18.5.

The idler half has a16.2mm bearing pocket at its proximal pivot and an M5 captive-nut boss at its distal servo axis. The driven half has the two straight-horn slots at its proximal pivot. The parent servo output-side case plane sits at localZ+20.25. Its metal arm and the3.3mm spacer fill the gap to the driven plate inner face atZ+26. The opposite case face clears the idler boss by0.35mm. These are digital nominal clearances and require a physical fit check.

11. Bolt the shoulder tower to the turntable with fourM3x16 bolts. Fit the shoulder DS3218MG with its shaft atZ121 and its output side toward the driven link half. Install the keeper with twoM3x60 bolts. Insert the first M5 captive nut into the tower idler boss before the upper link blocks access.
12. Press one625 bearing into the proximal pocket of `upper_arm_left`. Put the inner race against the shoulder idler boss with its thrust washers and M5 axle. Do not tighten the outer race. With the shoulder servo centered and unpowered, index the link at115° and attach `upper_arm_right` to the straight metal arm through one printed spacer and two measured horn fasteners.
13. Seat the elbow DS3218MG in the upper-link distal pocket with its shaft atX140. Put its output toward the driven half and cable toward the rear relief. Route its lead and the remaining head harness through the inner wall port. Insert the distal M5 captive nut. Close the two halves with threeM3x70 bolts without crushing the case.
14. Assemble the forearm the same way. Its idler625/M5 stack attaches at the elbow, and its driven half attaches to the elbow's straight horn at−70° relative angle. Seat the wrist servo atX120, route its lead, insert the last M5 captive nut, and close with threeM3x70 bolts.
15. The head yoke has one625 idler ear and one tangential straight-horn ear. Attach its bearing side to the forearm idler boss, then attach its driven side to the centered wrist horn through the last3.3mm spacer. At neutral, the broad head plate faces+Y and lies21mm forward of the wrist axis. Verify that the servo mounting tab clears the yoke notch.
16. Pass the head harness through the26 ×8mm yoke slot, over each servo case, and through both link ports. Leave a slack service loop at every joint. No moving wire may enter a horn, bearing, idler bolt, or clamshell seam.

## Assemble the standard 1.85-inch head

Head-localZ starts at the rear face and increases toward the viewer. The shell floor isZ0-3 and rim ends atZ36. There are no sensor mounts or apertures in the revision C head.

17. Attach `head_shell` to the yoke with fourM3x12 bolts on the54 ×30mm pattern. Bring only display, LED, and optional DSI wiring through the center slot.
18. Join four Adafruit1768 RGB quarter-rings into one60-pixel circle. Dry-fit the158mm OD/145mm ID board on the radius76 posts. Retain the PCB mechanically; solder bridges are electrical joints only.
19. Put the standard LCD cradle on its four headZ14 pillars. Place the55mm board in the55.8mm pocket with thin edge foam and its low-profile USB plug in the19mm relief. Fit the retainer atZ29 with fourM3x25 screws. Do not load the glass.
20. Fit the white-ring carrier on the radius45 bosses atZ32.5 with fourM3x10 screws. Attach the24-pixel RGBW ring without covering LEDs or loading solder joints.
21. Put1mm shims on the four radius60 face bosses and eight radius83 bezel bosses. Fit the outer diffuser, center baffle, and outer bezel without squeezing the optical skin. Secure the center with fourM3x12 and bezel with eightM3x10. Retain the inner diffuser with three small removable neutral-cure silicone dots.

## Assemble the optional 4-inch DSI head

This variant replaces `head_shell`, `face_center`, `white_carrier`, `inner_diffuser`, `lcd_cradle`, and `lcd_retainer` with `head_shell_dsi`, `lcd4_carrier`, and `face_ring_dsi`. It keeps the yoke, outer bezel, outer diffuser, and60-pixel halo. It has no brow bracket or head-mounted sensors and no separate white ring.

22. Attach `head_shell_dsi` to the yoke with fourM3x12 bolts. Fit the RGB halo on its radius76 posts.
23. Attach `lcd4_carrier` to the display's four M4 bosses with M4x8 screws. Do not use longer screws. Confirm the PCB, Pi standoffs, power connector, USB-C, and DSI FPC all clear the carrier window.
24. Lower the carrier onto the shell bosses at(±55,±38). Route the800mm DSI FPC and5V/GND lead through the26 ×8mm floor/yoke slots. Secure the carrier with fourM3x8 screws.
25. Put0.5mm foam on the display rim and1mm shims on the face/bezel bosses. Fit the outer diffuser, `face_ring_dsi`, and bezel. Tighten evenly without pressing the active glass. Configure and test the display before closing the base.

## Bring-up and limits

26. With every horn disconnected from the links, center one servo at a time using the bounded PCA9685 command in `software/README.md`. Mark its1500µs position. Power off before installing a horn. Set `neutral_pulse_us` and `joint_signs` from the actual indexed mechanism; the default values are not physical calibration.
27. Support the head and move each unpowered joint through the intended small range. Check the625 stacks, open clevises, servo tabs, cable loops, and straight horns. Initial commanded limits remain yaw±25° and shoulder/elbow/wrist±10° at12°/s. The supplied digital collision check covers only the indexed pose.
28. Verify the physical motor stop before armed motion. Run one joint and then one complete scene while supported. A PCA9685 check proves controller communication only. The DS3218 provides no position, current, load, or temperature feedback. Measure6V droop, regulator temperature, each accessible servo-case temperature, and joint holding behavior.
29. Recheck clamp, horn, idler, and link fasteners after the first short motion run and first thermal cycle. Stop on noise, binding, rising temperature, visible deflection, or lost PWM control. Physical fit, proof load, drop, fatigue, thermal, optical, and cable-flex tests remain first-build work.

## Load and stability calculations

The documented21.5kg-cm DS3218 stall torque at6.8V is about2.11N·m. Torque at the selected6V rail and continuous safe torque are not documented. Never treat stall torque as a holding-duty rating. A conservative folded standard-head estimate remains about0.40N·m at the shoulder; the optional DSI head estimate remains about0.48N·m. Wider link shells and actual wiring change mass, so weigh the build and repeat the calculation.

With a0.32m horizontal head moment arm, the standard0.40kg head alone produces about1.26N·m; the optional0.50kg head produces about1.57N·m, before link mass and acceleration. That is too close to the servo's6.8V stall rating for claimed continuous operation, and the project runs at6V. The restricted folded pose is deliberate. Reduce reach, add counterbalance, or change the actuator architecture before extended duty.

The1.19kg ballast alone gives a nominal1.26N·m restoring moment about the108mm base radius. This excludes dynamics, cable pulls, foot friction, and the raised center of mass. Use a commercial padded desk clamp if the measured build exceeds the validated stable envelope. This is not a lifting arm.

## Drawing and verification limits

Assembly matrices are row-major4×4 in millimeters. Right-side link halves are rotated180° about their length axis for assembly. Purchased horns, bearings, screws, wiring, and exact PCA9685 geometry are not printable substitutes. `validation/assembly_check.json` covers printable solids at the indexed pose. `cad/purchased_fit.json` covers conservative static DS3218, sensor-board, and display envelopes. Neither report certifies moving clearance, strength, electrical safety, or physical fit.
