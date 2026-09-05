"""Final digital checks for the deliverable. No hardware is activated."""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import sys

import pymupdf

ROOT=Path(__file__).resolve().parents[1]


def main():
    report={"release":"LUMA Rev A","scope":"Digital asset checks only; no physical prototype available."}
    report["display_firmware"]={"cross_compile_verified":False,"binary_included":False,
                                "reason":"Required compiler downloads did not complete; see software/VERIFICATION.md."}
    report["physical_validation"]={"performed":False,
                                   "required":"Fit, wiring, supported motion, stop behavior, stability, optics and thermal tests."}
    host=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT/"software",capture_output=True,text=True)
    report["host_tests"]={"exit_code":host.returncode,"log":host.stdout+host.stderr}
    pdf=ROOT/"deliverables/LUMA_Assembly_Manual.pdf"
    doc=pymupdf.open(pdf)
    text_outside=[];short_pages=[]
    for i,page in enumerate(doc):
        if len(page.get_text().strip())<60:short_pages.append(i+1)
        for b in page.get_text("blocks"):
            if b[6]!=0:continue
            if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
                text_outside.append({"page":i+1,"box":list(b[:4]),"sample":b[4][:70]})
    report["manual"]={"pages":len(doc),"bookmarks":len(doc.get_toc()),"bytes":pdf.stat().st_size,
                      "text_outside_page":text_outside,"suspiciously_empty_pages":short_pages}
    # Produce a compact contact sheet from every page for visual review.
    from PIL import Image,ImageDraw
    thumb_w=190;cell_h=300;cols=6;rows=(len(doc)+cols-1)//cols
    sheet=Image.new("RGB",(cols*thumb_w,rows*cell_h),(217,226,227));draw=ImageDraw.Draw(sheet)
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=pymupdf.Matrix(thumb_w/page.rect.width,thumb_w/page.rect.width),alpha=False)
        im=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
        im.thumbnail((thumb_w-8,cell_h-25))
        x=(i%cols)*thumb_w+(thumb_w-im.width)//2;y=(i//cols)*cell_h+18
        sheet.paste(im,(x,y));draw.text(((i%cols)*thumb_w+7,(i//cols)*cell_h+3),str(i+1),fill=(23,49,61))
    sheet.save(ROOT/"validation/manual_contact_sheet.jpg",quality=88)
    doc.close()
    executables=list(ROOT.glob("media/.tools/python/imageio_ffmpeg/binaries/ffmpeg*.exe"))
    if not executables:
        import shutil
        found=shutil.which("ffmpeg")
        if not found:raise RuntimeError("FFmpeg required to verify videos")
        ffmpeg=found
    else:ffmpeg=str(executables[0])
    videos=[]
    for name in ("01_wink.mp4","02_hi.mp4","03_happy.mp4"):
        path=ROOT/"media/videos"/name
        result=subprocess.run([ffmpeg,"-hide_banner","-i",str(path),"-progress","pipe:1","-nostats","-f","null","-"],capture_output=True,text=True)
        log=result.stderr
        video=next((l.strip() for l in log.splitlines() if "Video:" in l),"")
        audio=next((l.strip() for l in log.splitlines() if "Audio:" in l),"")
        duration=re.search(r"Duration:\s*([0-9:.]+)",log)
        frames=re.findall(r"^frame=(\d+)",result.stdout,re.M)
        videos.append({"file":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,"decode_exit_code":result.returncode,
                       "duration":duration[1] if duration else None,"decoded_frames":int(frames[-1]) if frames else None,"video":video,"audio":audio})
    report["videos"]=videos
    report["static_assembly"]=json.loads((ROOT/"validation/assembly_check.json").read_text())
    failures=[]
    if host.returncode:failures.append("host tests")
    if text_outside or short_pages:failures.append("PDF page content")
    for p in report["static_assembly"]["parts"]:
        if not(p["watertight"] and p["positive_volume"] and p["fits_220_bed_xy"] and p.get("connected_bodies")==1):failures.append("mesh "+p["id"])
    if report["static_assembly"]["intersections"]:failures.append("static printed-part intersections")
    for video in videos:
        if video["decode_exit_code"] or not video["audio"] or not video["decoded_frames"]:failures.append(video["file"])
    report["failures"]=failures
    (ROOT/"validation/final_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"pdf":report["manual"],"videos":videos,"failures":failures},indent=2))
    if failures:sys.exit(1)


if __name__=="__main__":main()
