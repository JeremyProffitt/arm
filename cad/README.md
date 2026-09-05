# LUMA CAD files

Open `assembly.scad` in OpenSCAD to view the entire assembled lamp. It imports the supplied meshes with the positions and colors in `assembly.json`; `assembly_preview.scad` is an equivalent copy. Edit individual part geometry in `luma.scad` and select its `part` parameter using an ID from `part_manifest.json`.

Print the27 files in `stl/` in the quantities from `part_manifest.json` (52 physical pieces total). Read the print orientation for each piece, especially the head fork. Do not print anything from `visual_only/`: it contains purchased-component envelopes and a complete assembled reference model for viewing.

The exact OpenSCAD executable location defaults to `C:/Program Files/OpenSCAD/openscad.com`; override it with the `OPENSCAD` environment variable if needed. Run `python cad/build.py` from the project root with NumPy and trimesh installed to regenerate the assets. The hidden electronics tray uses32 facets to keep exports practical; all dimensions remain the same. `cad/refresh_validation.py` measures existingSTLs without re-exporting them.

`ballast_plate.dxf` contains a180mm steel disc outline and eight drill circles in millimetres. Its thickness is6mm; theDXF is2D, not an instruction to print the ballast. The dimensioned SVG drill template is on a250x230mm page, suitable for an actual-size A3 print.

`validation.json` records mesh integrity, connected bodies, dimensions and solid volume. `purchased_fit.json` records a static conservative servo/LCD-envelope fit check; `../validation/assembly_check.json` records printed-part intersections at indexed neutral. These reports do not replace a physical fit, load, thermal or motion test.

`mechanical.md` provides the assembly instructions and assumptions. `bom_mechanical.csv` lists metal, hardware and printing consumables; the complete projectBOM also includes the electronics list. Vendor STEP/DXF/PDF reference files are stored separately in `references/` and remain their vendors' material.
