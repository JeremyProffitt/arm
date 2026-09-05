# LUMA promotional media

Three 9-second films show the proposed lamp winking, greeting the viewer with an
audible “Hi!”, and moving happily. Each final MP4 is 1920 × 1080, H.264 with AAC
stereo sound and actual 24 fps CAD animation. A restrained camera push brings
each expression closer while keeping the titles stable.

These are **prototype animations**, not footage of a built or tested device.
All mechanical surfaces are rendered from the project's assembly STL files;
the screen graphics, illumination and motion are illustrative. No AI concept
images, stock footage, external music or unlicensed character assets are used.

## Rebuild

Install Python 3.13, Pillow, NumPy, ModernGL and imageio-ffmpeg. Generate the CAD
assembly first, then run from the project directory:

```powershell
python -m pip install -r media/requirements.txt
powershell -ExecutionPolicy Bypass -File media/sources/synthesize_hi.ps1
python media/sources/render_media.py --stills --clip all
```

The speech source uses the installed Windows Microsoft Zira Desktop voice.
The greeting WAV is included so rebuilding the films does not require Windows
speech synthesis. Original sound-design tones are synthesized by the renderer.

`sources/render_media.py` is the editable scene, camera, lighting, motion,
face-animation, typography and sound source. The assembly JSON supplies the
manufactured geometry and kinematic pivots. The final films use a depth-buffered
OpenGL renderer with 4× antialiasing. A basic software renderer is included as a
fallback. Blender is optional, via `sources/blender_stills.py`, for physically
lit still images.

The supplied hero and exploded `.blend` files use Blender 4.5.9 LTS. That optional
portable application was downloaded from the official Blender release archive
and verified against its published SHA-256 checksum. It is not included in the
project ZIP. Run `blender -b -P media/sources/blender_stills.py` to rebuild those
images, then use the resulting `*_cycles.png` files in the manual.

`renders/hero.png`, `exploded.png` and three orthographic PNGs support the PDF
manual. `renders/hero_dsi.png` shows the optional 4-inch DSI head; make it with
`python media/sources/render_media.py --manifest cad/assembly_dsi.json --suffix _dsi --stills --views hero`
(or `blender -b -P media/sources/blender_stills.py -- --manifest cad/assembly_dsi.json --suffix _dsi --hero-only`
for the physically lit version). The face graphics scale with the active display
radius in the assembly JSON. `renders/promotional_contact_sheet.jpg` samples the
films. `videos/` contains the deliverable MP4s; `audio/` contains the original and
mixed sound.

The `.tools/` directory, if present, is only a local dependency cache and is not
part of the design deliverables.
