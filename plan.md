# LUMA revision B — enclosed arms and optional 4-inch DSI head

Single source of truth for the revision B work. A fresh run must be able to resume from this file alone.
Repository root: `C:\dev\arm`. Python: `C:\dev\arm\.venv\Scripts\python.exe` (3.13). OpenSCAD 2021.01 at `C:/Program Files/OpenSCAD/openscad.com`. Blender 4.5.9 at `C:\dev\arm\media\.tools\blender\blender-4.5.9-windows-x64\blender.exe`.

## Locked decisions (user-confirmed; do not revisit)

- 2026-09-05 — user: "this is great but the arms need to be more enclosed". The revision A ladder arms (two flat rails, cylindrical cross spacers, exposed servo cassette) are replaced by closed links.
- 2026-09-05 — user: "add an optional head for this lcd https://www.waveshare.com/4inch-dsi-lcd-c.htm". The Waveshare 4inch DSI LCD (C) round 720×720 display gets an optional head variant. The revision A head with the 1.85-inch display stays the default build.

## Design decisions taken by the run (defaults; not user-confirmed; reported in the final summary)

- `arm-enclosure`: each link becomes two mirror-image channel halves (left and right) printed plate-down. Each half = 5 mm side plate + 2.4 mm perimeter walls 22 mm deep, meeting the other half at the link mid-plane. The side profile tapers from a Ø32 boss at the proximal pivot to a 46 mm tall block at the distal (servo) end. The servo pocket is integral (replaces `servo_cassette` + `cassette_cap`); through-bolt half-bosses are integral (replace `cross_spacer`). Horn interface (PCD 14, 3.3 mm spacer, plates at ±22..27 mm, 44 mm inside width), pivot pitches 140/120 mm, the M3x60 bolt stack and all kinematics stay identical, so `assembly.json` joints, software limits and torque calculations are unchanged. Walls start 28 mm from the proximal pivot; the proximal clevis stays open so the previous joint's servo body (which protrudes 10.11 mm past its shaft axis) and its block can rotate through it. One cable port (26 × 9 mm, rounded) sits on the −y wall behind the servo block; the service loop at each joint passes on the inside of the joint. Three M3x60 bolts per link (x=35 boss, two servo-block ears) instead of four.
- `dsi-head`: the variant reuses `head_yoke`, `outer_bezel`, `outer_diffuser`, five `sensor_pod`/`sensor_retainer`, and the outer 60-RGB halo. New parts: `head_shell_dsi`, `lcd4_carrier`, `face_ring_dsi`, `brow_bracket`. Omitted on the variant: `face_center`, `white_carrier`, `inner_diffuser`, `lcd_cradle`, `lcd_retainer`, the 24-RGBW inner ring and the 1.85-inch display. The white lamp function on the variant comes from the outer halo at its capped brightness; this trade-off is documented. The front ToF pod moves to a forward-facing brow bracket on the top rim because the 126 mm display case leaves only 8.5 mm of face ring between it and the halo diffuser.
- Head cable exit (both variants): a 26 × 8 mm slot through the yoke plate and the shell floor at the head centre replaces the Ø12 floor hole (the revision A yoke plate had no through-path).
- `dsi-software`: `config.json` gains `display_kind`: `"usb_serial"` (default, ESP32 display over USB) or `"dsi"` (Pi renders the face with pygame-ce on the DSI framebuffer). `DsiDisplay` exposes the same `update(now, face) -> bool` contract as `Display`; a frame is "ok" if drawn within 1.5 s. Faces replicate the ESP32 firmware drawing at 2× scale (720 × 720).
- Wiring (variant): 15-pin 1.0 mm pitch DSI FFC, same-side contacts, 800 mm, from the Pi DSI connector through the arm ports to the LCD; 5 V and GND from Pi header pins 4 and 39 to the LCD HP2.0 4-pin connector; SDA/SCL of that connector left unconnected (touch and backlight use the DSI connector I2C, `I2C_bus=10`).
- Revision label becomes "Rev B / 05 Sep 2026" in the manual, drawings, README, START_HERE and package inventory.
- Git: the folder had no repository. The run creates one (`git init`, default branch `main`) and commits at milestone boundaries. There is no remote, so nothing is pushed.

## Verified facts (confirmed by reading files, running commands, or vendor data)

- Vendor drawing `https://www.waveshare.com/img/devkit/LCD/4inch-DSI-LCD-C/4inch-DSI-LCD-C-details-size.jpg` (saved to `cad/references/4inch-DSI-LCD-C-details-size.jpg`): outline Ø126.00; active area Ø101.52; case 6.00 thick; 17.00 overall depth; PCB 85.00 × 65.00; Pi standoff pattern 58.00 × 49.00; M4 case mounting holes.
- Vendor STEP `https://files.waveshare.com/upload/d/db/4inch_DSI_LCD_%28C%29_3D.zip` (`4inch-DSI-LCD_C.stp`, saved to `cad/references/`), measured with trimesh after conversion with cascadio (LCD coordinates, +z toward the viewer): case disc Ø126 from z −2.17 (rear plate face) to 3.83 (rim front; glass surface 3.58); rear edge chamfered to r 62.17; four M4 tapped bosses Ø7.1 × 4.0 mm tall at (±37.5, ±37.5), ends at z −6.17; PCB 85.5 × 65 × 1.6 at x ±42.75, y −37..28, z −5.27..−3.67; components below the PCB down to z −14.37 (2.54 mm headers at x −17.6..−12.5, y −36..−33.5), Pi standoffs Ø5.5 at (−39.25, ±24.5) and (18.75, ±24.5) to z −13.27, HP2.0 4-pin power/touch connector x −30.5..−18.5, y −36..−27.8, z to −11.77, USB-C x −32.7..−23.7, y 21.4..29, panel FPC connector x ±9.5, y −36.8..−30.55, tallest general component layer to z −7.57. The DSI 15-pin FPC connector is on the PCB +x edge (vendor photo), cable exits toward +x.
- Software setup (Waveshare guide via spotpear mirror): `dtoverlay=WS_xinchDSI_Screen,SCREEN_type=10,I2C_bus=10` and `dtoverlay=WS_xinchDSI_Touch,I2C_bus=10`; package includes two 50 mm 15-pin FPC cables; CM boards need `DSI-Cable-15cm`.
- Revision A interfaces from `cad/luma.scad` and `cad/build.py`: plates at link z ∈ [−27,−22] ∪ [22,27]; rail profile capsule 30 wide ending 38 mm before the distal pivot, distal block 21 × 46 centred at l−28; cassette 26 × 46 × 39.8 with pocket 30 × 25.4 from floor 4.2; servo body 45.22 × 24.72 × 35 with shaft axis 10.11 mm from the front end (`servo_back=35.11`); cross bolts at x=35 and l−52; cassette bolts at (l−25, ±18.5); horn spacer 3.3 at z −22..−18.7 and 18.7..22; head transform `H = T(WR+[0,21,0]) R(180,z) R(90,x)`; shell bosses: yoke (±27,±15), LCD pillars (±34,±34) top 14, white carrier r45 top 32.5, face r60 (45+90n) top 35, bezel r83 (22.5+45n) top 35, RGB posts r76 Ø8 Z3–24, ribs r82–88 at 0/90/180/270, wall pod mounts at angles 0/180/270 Z14.
- Toolchain: `C:\dev\arm\.venv` has trimesh 5.1.0, manifold3d 3.5.2, numpy 2.5.2, pillow 12.3.0, pymupdf 1.28.2, reportlab 5.0.1, svglib 2.2.0; installed today: pygame-ce 2.5.8, scipy, shapely, cascadio. `media/.tools/python` has moderngl 5.12.0 and imageio_ffmpeg 0.6.0. Blender 4.5.9 present. OpenSCAD 2021.01 present. Chrome extension not connected; waveshare.com blocks WebFetch (curl with a browser user agent works).
- Existing checks: `python -m unittest discover -s tests -v` (software) passes 18 tests at revision A; `validation/check_assembly.py` reports 0 intersections at revision A.

## Stop conditions (only these)

- An OpenSCAD export for one part fails deterministically after three geometry fixes.
- Blender or the GL renderer cannot run at all on this machine (crash on start) after one retry.
Anything else is worked around, marked `[!]`, and reported at the end.

## Workstreams

### arm-enclosure — closed tapered clamshell links replacing the ladder rails
- [ ] arm-scad — `luma.scad` gains `arm_half(l)`, `upper_arm_left/right`, `forearm_left/right`; removes `upper_rail`, `forearm_rail`, `servo_cassette`, `cassette_cap`, `cross_spacer`. Done when `python cad/build.py` exits 0 and `cad/validation.json` shows all four arm parts watertight, one body, within the bed.
- [ ] arm-assembly — `build.py` places the four halves (right halves rotated 180° about x at z=27) and drops the cassette/cap/spacer instances; features/manifest text updated. Done when `python validation/check_assembly.py` prints 0 overlaps above 0.5 mm³ for `assembly.json`.
- [ ] arm-docs — `cad/mechanical.md` arm steps, `docs/printing.md`, `cad/bom_mechanical.csv` (M11 quantity 6), `cad/README.md`. Done when `python docs/build_bom.py` exits 0.

### dsi-head — optional head variant for the Waveshare 4inch DSI LCD (C)
depends on: arm-enclosure (shared `luma.scad`/`build.py`; sequential edits)
- [ ] dsi-scad — `head_shell_dsi`, `lcd4_carrier`, `face_ring_dsi`, `brow_bracket`; centre cable slot in `head_yoke` and both shells; `visual_only/lcd4_envelope.stl` built from the measured vendor geometry. Done when `python cad/build.py` exits 0 with the new parts watertight.
- [ ] dsi-assembly — `build.py` writes `assembly_dsi.json` and `assembly_dsi.scad` (head group swapped, front pod on the brow bracket, LCD envelope at head Z 31.67 offset); `validation/check_assembly.py`, `cad/check_purchased_fit.py` and `validation/verify_project.py` check both assemblies. Done when `python validation/check_assembly.py` and `python cad/check_purchased_fit.py` report 0 intersections for both assemblies.
- [ ] dsi-docs — `cad/mechanical.md` chapter "Optional 4-inch DSI head", `docs/parts.md` optional section (via `build_bom.py` handling refs starting with `D`), `electronics/wiring.csv` DSI rows, `electronics/architecture.md`, `docs/overview.md`, `docs/sources.json`, `docs/validation_build.md`. Done when `python docs/build_bom.py` exits 0 and the optional subtotal appears in `docs/parts.md`.

### dsi-software — Pi-rendered face for the DSI head
independent of the CAD workstreams
- [ ] face-renderer — `software/luma/face.py`: `draw_face(surface, face, t, offline)` and `DsiDisplay`; `hardware.py`/`bench.py`/`app.py` select by `display_kind`; `config.json` and `pyproject.toml` (`dsi` extra). Done when `python -m unittest discover -s tests -v` passes with the new face tests (run from `C:\dev\arm\software`).
- [ ] software-docs — `software/README.md` DSI section, `software/VERIFICATION.md` test count. Done when the README documents `display_kind`, the config.txt overlays and the SDL driver.

### media-regen — renders and films from the revision B geometry
depends on: arm-enclosure, dsi-head
- [ ] gl-stills — `python media/sources/render_media.py --stills` (standard) and `--manifest cad/assembly_dsi.json --suffix _dsi --stills` (variant). Done when `media/renders/hero.png`, `side.png`, `top.png`, `front.png`, `exploded.png`, `hero_dsi.png` are regenerated (timestamps today).
- [ ] cycles-stills — `blender -b -P media/sources/blender_stills.py` (hero + exploded) and `-- --manifest cad/assembly_dsi.json --suffix _dsi --hero-only`; copy `*_cycles.png` over the manual images. Restart policy: kill after 25 min, re-run once with `--preview`; if that fails, keep the GL stills and mark `[!]`.
- [ ] films — `python media/sources/render_media.py --clip all`; `python media/sources/validate_media.py`. Restart policy: kill after 40 min, re-run once per clip.

### deliverables — manual, drawings, archive
depends on: all of the above
- [ ] drawings — `docs/build_drawings.py` adds sheet G03 (DSI head) and the Rev B header; `python docs/build_drawings.py` exits 0.
- [ ] manual — `python docs/build_manual.py` exits 0; `python validation/verify_project.py` exits 0 (failures list empty).
- [ ] package — `README.md`, `START_HERE.html`, `python docs/package_project.py` exits 0.
- [ ] commit — git commits at each milestone; final commit "LUMA revision B".

## Execution log

(appended as work lands)
