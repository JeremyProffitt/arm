# LUMA — printable robotic desk companion

Open [START_HERE.html](START_HERE.html) for the illustrated project browser and three promotional videos. The complete build reference is [LUMA_Assembly_Manual.pdf](deliverables/LUMA_Assembly_Manual.pdf).

This original prototype is inspired by the [Autonomous Lamp](https://www.autonomous.ai/lamp). It has a Raspberry Pi 4 master controller, four articulated servo joints in enclosed printed arm links, five Adafruit VL53L1X STEMMA QT sensors, a circular animated display, a white light ring, and a larger RGB halo with printable frosted covers.

Revision B (5 September 2026) encloses both arm links and adds an optional head. The standard head uses the **Waveshare ESP32-S3-Touch-LCD-1.85, SKU 28514**, a 360 × 360 IPS LCD (not an OLED) whose integrated ESP32-S3 is a USB graphics peripheral; the Pi remains the behavior and motion controller. The optional head uses the **Waveshare 4inch DSI LCD (C)**, a round 720 × 720 display driven directly from the Pi's DSI connector and rendered by the Pi itself. Use the exact boards specified in the BOM.

## Deliverables

| File or folder | Contents |
| --- | --- |
| `deliverables/LUMA_Assembly_Manual.pdf` | Illustrated instructions, BOM, wiring, calibration, verification worksheet and engineering sheets |
| `deliverables/LUMA_Engineering_Drawings.pdf` | Standalone A3 drawing set, with model-derived views and interface dimensions, including the optional head sheet |
| `deliverables/LUMA_Purchased_Parts.csv` | Consolidated purchased parts, quantities, supplier links and budget allowances (`D` rows are the optional head) |
| `deliverables/LUMA_Print_Schedule.csv` | Printable part quantities, materials, orientations and variant (`standard` or `dsi-head`) |
| `cad/stl/` | Individual printable STL files, in millimeters |
| `cad/luma.scad`, `cad/build.py` | Editable parametric source and export script |
| `cad/assembly.scad`, `cad/assembly_dsi.scad` | Open in OpenSCAD for the complete assembled model, standard or optional head |
| `cad/assembly.json`, `cad/assembly_dsi.json` | Exact assembly placements, articulation axes and indexed neutral pose |
| `cad/ballast_plate.dxf`, `cad/ballast_plate.svg` | Steel ballast profile and dimensioned drilling template |
| `cad/visual_only/` | Purchased-component envelopes for visualization; do not print these |
| `electronics/` | Electrical architecture, wiring diagram, pin-to-pin CSV and source BOM |
| `software/` | Pi controller, simulation, tests, setup, exact-board face firmware and the Pi-rendered face for the DSI head |
| `media/videos/01_wink.mp4` | Winking promotional animation |
| `media/videos/02_hi.mp4` | Greeting promotional animation with spoken “Hi!” |
| `media/videos/03_happy.mp4` | Happy promotional animation |
| `media/renders/` | Finished, exploded, orthographic and promotional images, plus `hero_dsi.png` for the optional head |
| `media/sources/` | Editable rendering and animation sources |
| `validation/` | Mesh/intersection, software, PDF and video verification records |
| `plan.md` | Revision B work plan and execution log |

`deliverables/LUMA_Complete_Project.zip` is the portable archive. Extract it before opening the HTML index. Development tool downloads, virtual environments and intermediate previews are excluded. The archive contains a SHA-256 inventory.

`deliverables/LUMA_Printable_STLs.zip` is the smaller print-only download, including the quantity schedule and printing notes. Consult the assembly manual before printing or purchasing parts.

## Before printing

Read the mechanical assembly chapter and exact part list. Print the fit coupon first. The largest base parts have a 216 mm footprint, so a 220 mm bed needs careful placement and little or no brim; a larger bed provides more margin. Structural parts use PETG. Both light covers use natural translucent PETG, with a thin solid face that can be lightly frosted after printing. Each arm link is a left and a right half; print both, plate-down, and assemble the servo and harness inside before closing the link.

The initial folded pose reduces reach: upper link 115° and forearm 45° above the +Y horizontal, head facing +Y. Motion commands are small offsets around this indexed pose. The uncalibrated default configuration does not arm the motors.

The full STL assemblies are for viewing. Print the individual files and apply the schedule quantities. Purchased bearings, metal servo horns, steel ballast, electronics and fasteners are not printed replacements. The optional 4-inch head prints four extra files and omits six standard-head files; the print schedule lists both sets.

## Run the simulator

Python 3.11 or newer is sufficient; no Pi hardware is activated:

```console
cd software
python -m luma.app --scene wink
python -m luma.app --scene hi
python -m luma.app --scene happy
python -m unittest discover -s tests -v
```

The simulator prints timestamped expression, light and pose events. The software README gives the separate Raspberry Pi installation, display firmware build, the optional DSI-head display setup and supported first-motion procedure.

## Rebuild documents and checks

Create a Python environment and install `docs/requirements.txt`. Install OpenSCAD for the CAD exports; consult `cad/build.py` and the mechanical notes for platform paths and selectors. The media README describes the video/rendering dependencies.

From the project root, once the CAD, media and source chapters are present:

```console
python cad/build.py
python cad/check_purchased_fit.py
python validation/check_assembly.py
python docs/build_bom.py
python media/sources/render_media.py --stills
python media/sources/render_media.py --manifest cad/assembly_dsi.json --suffix _dsi --stills --views hero
python docs/build_drawings.py
python docs/build_manual.py
python validation/verify_project.py
python docs/package_project.py
```

The static intersection check compares assembled printed solids at the indexed neutral pose for both assemblies. It does not certify the full motion envelope, purchased hardware fit, wiring clearance, strength, balance or temperature. The final verification report distinguishes executed digital checks from untested hardware and records the display cross-compilation status separately.

## Release status

Revision B is a digital prototype, not a physically built or certified product. The promotional clips are rendered animations of the CAD design. Physical fitting, supported commissioning, load/stability checks and thermal/optical measurements remain part of building the first unit. The manual includes specific records for those checks. No measured lumen/CRI output or autonomous collision-avoidance capability is claimed. The 800 mm DSI cable run of the optional head is a bench-verification item.

Vendor specifications and third-party display initialization provenance are linked in the manual and firmware notices. The appearance-reference image used during research is not redistributed in the package.
