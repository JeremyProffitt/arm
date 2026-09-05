"""Create a portable deliverable and SHA-256 inventory from completed assets."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
REQUIRED = ["README.md", "START_HERE.html", "deliverables/LUMA_Assembly_Manual.pdf",
            "media/videos/01_wink.mp4", "media/videos/02_hi.mp4", "media/videos/03_happy.mp4"]
EXCLUDED_DIRS = {".venv", ".tools", ".pio", "__pycache__", ".git", "vendor"}


def include(path):
    rel = path.relative_to(ROOT)
    if any(p in EXCLUDED_DIRS for p in rel.parts): return False
    if rel.parts[0] == "references": return False  # inspection-only commercial product image
    if path.suffix.lower() in (".zip", ".pyc", ".log", ".tmp"): return False
    if path.name in ("LUMA_Manual_Text.pdf", "SHA256SUMS.txt", "package_inventory.json", "fetch_display_reference.py"): return False
    if path.name.endswith("-page.html"): return False
    if ("preview" in path.name.lower() or "proof" in path.name.lower()) and path.suffix != ".scad": return False
    return path.is_file()


def main():
    OUT.mkdir(exist_ok=True)
    for p in REQUIRED:
        file = ROOT / p
        if not file.exists() or not file.stat().st_size:
            raise RuntimeError(f"Required deliverable missing or empty: {p}")
    stls = sorted(ROOT.glob("cad/stl/*.stl"))
    if not stls: raise RuntimeError("No printable meshes found")
    print_zip = OUT / "LUMA_Printable_STLs.zip"
    with zipfile.ZipFile(print_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in stls:
            z.write(path, "stl/"+path.name)
        for rel in ("deliverables/LUMA_Print_Schedule.csv", "cad/part_manifest.json", "docs/printing.md"):
            z.write(ROOT / rel, Path(rel).name)
    with zipfile.ZipFile(print_zip) as z:
        if z.testzip(): raise RuntimeError("Printable STL archive integrity failure")
    files = sorted(p for p in ROOT.rglob("*") if include(p))
    inventory = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        inventory.append({"file": rel, "bytes": path.stat().st_size, "sha256": sha})
    invpath = OUT / "package_inventory.json"
    invpath.write_text(json.dumps({"revision": "A", "files": inventory}, indent=2), encoding="utf-8")
    sums = OUT / "SHA256SUMS.txt"
    sums.write_text("\n".join(f'{r["sha256"]}  {r["file"]}' for r in inventory)+"\n", encoding="utf-8")
    target = OUT / "LUMA_Complete_Project.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in [*files, invpath, sums]:
            z.write(path, "LUMA/"+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as z:
        bad = z.testzip()
        if bad: raise RuntimeError(f"Archive integrity failure: {bad}")
    print(f"Packaged {len(files)+2} files, {target.stat().st_size/1e6:.1f} MB: {target}")
    print(f"Printable-only archive: {len(stls)} STLs, {print_zip.stat().st_size/1e6:.1f} MB: {print_zip}")


if __name__ == "__main__": main()
