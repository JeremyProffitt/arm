"""Build the illustrated LUMA manual from the checked-in source chapters.

Run from the project root with: .venv\\Scripts\\python docs\\build_manual.py
The source list is docs/manual_sections.json; no online service is needed.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, KeepTogether, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
INK = colors.HexColor("#17313D")
MUTED = colors.HexColor("#506672")
TEAL = colors.HexColor("#007F80")
PALE = colors.HexColor("#EDF6F5")
LINE = colors.HexColor("#D6E3E6")
PAGE_W, PAGE_H = A4
CONTENT_W = PAGE_W - 36 * mm


def register_fonts():
    base = Path("C:/Windows/Fonts")
    fonts = {"Luma": "segoeui.ttf", "Luma-Bold": "segoeuib.ttf",
             "Luma-Italic": "segoeuii.ttf", "Luma-Mono": "consola.ttf"}
    fallback = Path("/usr/share/fonts/truetype/dejavu")
    for name, filename in fonts.items():
        file = base / filename
        if not file.exists():
            file = fallback / {"Luma": "DejaVuSans.ttf", "Luma-Bold": "DejaVuSans-Bold.ttf",
                               "Luma-Italic": "DejaVuSans-Oblique.ttf", "Luma-Mono": "DejaVuSansMono.ttf"}[name]
        pdfmetrics.registerFont(TTFont(name, str(file)))
    pdfmetrics.registerFontFamily("Luma", normal="Luma", bold="Luma-Bold", italic="Luma-Italic")


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("BodyL", fontName="Luma", fontSize=9.1, leading=13.4,
                        textColor=INK, spaceAfter=7, splitLongWords=True))
    s.add(ParagraphStyle("H1L", fontName="Luma-Bold", fontSize=23, leading=28,
                        textColor=INK, spaceBefore=8, spaceAfter=15, keepWithNext=True))
    s.add(ParagraphStyle("H2L", fontName="Luma-Bold", fontSize=12, leading=16,
                        textColor=TEAL, spaceBefore=13, spaceAfter=6, keepWithNext=True))
    s.add(ParagraphStyle("H3L", parent=s["H2L"], fontSize=10.1, leading=14, spaceBefore=9))
    s.add(ParagraphStyle("SmallL", parent=s["BodyL"], fontSize=7.4, leading=10.4, textColor=MUTED))
    s.add(ParagraphStyle("CellL", parent=s["BodyL"], fontSize=7.6, leading=10.6, spaceAfter=0))
    s.add(ParagraphStyle("CellHeadL", parent=s["CellL"], fontName="Luma-Bold", textColor=colors.white))
    s.add(ParagraphStyle("BulletL", parent=s["BodyL"], leftIndent=13, firstLineIndent=-10))
    s.add(ParagraphStyle("CodeL", fontName="Luma-Mono", fontSize=7.1, leading=10,
                        backColor=PALE, borderPadding=8, textColor=INK, spaceBefore=4, spaceAfter=10))
    s.add(ParagraphStyle("TOCL", parent=s["BodyL"], fontSize=10.2, leading=16, spaceBefore=6))
    return s


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<link href="{html.escape(html.unescape(m[2]), quote=True)}" color="#007F80">{m[1]}</link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="Luma-Mono" size="8">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


class Architecture(Flowable):
    """Original vector drawing: data interfaces and separate power paths."""
    def __init__(self):
        super().__init__()
        self.width, self.height = CONTENT_W, 310

    def draw(self):
        c = self.canv
        boxes = {}
        def box(key, x, y, w, h, title, sub="", fill=PALE):
            boxes[key] = (x, y, w, h)
            c.setFillColor(fill); c.setStrokeColor(LINE)
            c.roundRect(x, y, w, h, 7, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont("Luma-Bold", 9)
            c.drawCentredString(x+w/2, y+h-18, title)
            c.setFont("Luma", 7.2)
            for i, line in enumerate(sub.split("\n")):
                c.drawCentredString(x+w/2, y+h-32-i*10, line)
        def link(a, b, label="", dashed=False):
            x,y,w,h=boxes[a]; xx,yy,ww,hh=boxes[b]
            if yy > y+h:
                p=(x+w/2,y+h); q=(xx+ww/2,yy)
            elif yy+hh < y:
                p=(x+w/2,y); q=(xx+ww/2,yy+hh)
            elif xx > x:
                p=(x+w,y+h/2); q=(xx,yy+hh/2)
            else:
                p=(x,y+h/2); q=(xx+ww,yy+hh/2)
            c.setStrokeColor(TEAL if not dashed else MUTED); c.setLineWidth(1)
            c.setDash(3,2) if dashed else c.setDash()
            c.line(*p,*q); c.setDash()
            if label:
                c.setFillColor(MUTED); c.setFont("Luma", 6.7)
                c.drawCentredString((p[0]+q[0])/2,(p[1]+q[1])/2+3,label)
        box("pi",183,128,126,64,"Raspberry Pi 4","Behavior + motion master")
        box("lcd",0,234,150,61,"Round face","ESP32-S3 / USB graphics")
        box("mux",0,128,150,64,"I2C multiplexer","Five separate ToF channels\nFront · left · right · rear · down")
        box("bus",183,234,126,61,"USB bus adapter","ST3215 motor data")
        box("motors",347,234,CONTENT_W-347,61,"4 servo joints","Yaw / shoulder\nElbow / wrist")
        box("rings",347,128,CONTENT_W-347,64,"Two light rings","60 RGB + 24 RGBW\nSeparate level-shifted data")
        box("pipsu",183,26,126,56,"Official Pi supply","5.1V USB-C")
        box("power",0,26,150,56,"External 12V supply","Fused motor-power disconnect")
        box("buck",347,26,CONTENT_W-347,56,"5V LED regulator","Separate fused LED rail")
        link("pi","lcd","USB"); link("pi","bus","USB")
        link("bus","motors","TTL data"); link("pi","mux","I2C")
        link("pi","rings","SPI / PWM"); link("pipsu","pi","Power",True)
        link("buck","rings","Power",True)
        c.setStrokeColor(MUTED); c.setLineWidth(1); c.setDash(3,2)
        # The switched motor branch and regulator share the external supply,
        # while the Pi USB-C positive rail remains independent.
        c.lines([(75,82,75,99),(75,99,330,99),(330,99,330,265),(330,265,347,265),
                 (330,99,410,99),(410,99,410,82)])
        c.setDash(); c.setFont("Luma",6.7); c.setFillColor(MUTED)
        c.drawString(90,102,"12V fused distribution")
        c.setFillColor(MUTED); c.setFont("Luma",7.0)
        c.drawString(0,5,"Solid: data. Dashed: power. Wiring chapter defines grounds, fuses and the motor feed.")


def picture(path, max_h=245):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w,h=im.size
    scale=min(CONTENT_W/w, max_h/h)
    return Image(str(path), width=w*scale, height=h*scale)


class Manual(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(str(filename), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                         topMargin=20*mm, bottomMargin=18*mm,
                         title="LUMA — Illustrated build manual", author="LUMA project",
                         subject="Digital prototype: printable arm, assembly drawings, electronics and software")
        self.addPageTemplates(PageTemplate(id="main", frames=[Frame(18*mm,18*mm,CONTENT_W,PAGE_H-38*mm,
                                  leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)], onPage=self.page))
        self._bookmark_counter=0

    def beforeDocument(self):
        self._bookmark_counter=0

    def page(self,c,doc):
        c.saveState()
        c.setFillColor(TEAL); c.rect(0,PAGE_H-6*mm,PAGE_W,6*mm,fill=1,stroke=0)
        c.setFont("Luma-Bold",8); c.setFillColor(INK)
        c.drawString(18*mm,PAGE_H-13*mm,"LUMA  /  BUILD MANUAL")
        c.setFont("Luma",7); c.setFillColor(MUTED)
        c.drawRightString(PAGE_W-18*mm,PAGE_H-13*mm,"REV B · 05 SEP 2026")
        c.setStrokeColor(LINE); c.line(18*mm,13*mm,PAGE_W-18*mm,13*mm)
        c.drawString(18*mm,8.5*mm,"Digital prototype · dimensions in mm · physical validation required")
        c.drawRightString(PAGE_W-18*mm,8.5*mm,f"{doc.page:02d}")
        c.restoreState()

    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name=="H1L":
            self._bookmark_counter+=1
            text=flowable.getPlainText(); key=f"chapter_{self._bookmark_counter}"
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(text,key,0,False)
            self.notify("TOCEntry",(0,text,self.page,key))


def markdown(path,s):
    lines=path.read_text(encoding="utf-8-sig").splitlines()
    out=[]; i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:
            i+=1; continue
        if line.startswith("```"):
            code=[]; i+=1
            while i<len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i+=1
            out.append(Preformatted("\n".join(code),s["CodeL"],maxLineLength=99,splitChars=" /,")); i+=1; continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                cells=[cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+",cell or " ") for cell in cells): rows.append(cells)
                i+=1
            n=max(map(len,rows)); rows=[r+[""]*(n-len(r)) for r in rows]
            if n==2: widths=[CONTENT_W*.31,CONTENT_W*.69]
            elif n==3: widths=[CONTENT_W*.23,CONTENT_W*.27,CONTENT_W*.5]
            else:
                weights=[max(8,min(45,max(len(r[j]) for r in rows))) for j in range(n)]
                widths=[CONTENT_W*w/sum(weights) for w in weights]
            data=[[Paragraph(inline(v),s["CellHeadL"] if j==0 else s["CellL"]) for v in row] for j,row in enumerate(rows)]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),INK),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,PALE]),
                ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),
                ("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),6),
                ("BOTTOMPADDING",(0,0),(-1,-1),6),("LINEBELOW",(0,0),(-1,0),.5,TEAL)]))
            out.extend([table,Spacer(1,9)]); continue
        if line.startswith("#"):
            h=re.match(r"(#+)\s*(.*)",line); level=min(len(h[1]),3)
            out.append(Paragraph(inline(h[2]),s[f"H{level}L"])); i+=1; continue
        if line.startswith("!["):
            m=re.match(r"!\[([^]]*)\]\(([^)]+)\)",line)
            if m:
                p=(path.parent/m[2]).resolve()
                if p.exists():
                    out.extend([picture(p),Paragraph(inline(m[1]),s["SmallL"])])
                else: raise FileNotFoundError(p)
            i+=1; continue
        if re.match(r"^(- |\* |\d+\. )",line):
            line=re.sub(r"^[-*] ","• ",line)
            out.append(Paragraph(inline(line),s["BulletL"])); i+=1; continue
        para=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r"^(#|\||```|[-*] |\d+\. |!\[)",lines[i].strip()):
            para.append(lines[i].strip()); i+=1
        out.append(Paragraph(inline(" ".join(para)),s["BodyL"]))
    return out


def main():
    register_fonts(); s=styles(); OUT.mkdir(exist_ok=True)
    cfg=json.loads((ROOT/"docs/manual_sections.json").read_text(encoding="utf-8"))
    chapters=[ROOT/p for p in cfg["chapters"]]
    for p in chapters:
        if not p.exists(): raise FileNotFoundError(f"Manual source not finished: {p}")
    story=[Spacer(1,18),Paragraph("LUMA",ParagraphStyle("Cover",fontName="Luma-Bold",fontSize=52,leading=59,textColor=INK)),
           Paragraph("A little light. A lot of personality.",s["H2L"]),
           Paragraph("Printable robotic desk companion",s["BodyL"]),Spacer(1,14)]
    hero=ROOT/cfg["hero"]
    if not hero.exists(): raise FileNotFoundError(hero)
    story.extend([picture(hero,330),Spacer(1,14),Paragraph("Illustrated assembly manual + engineering drawings",s["H2L"]),
       Paragraph("Raspberry Pi 4 · four moving joints in enclosed arms · round animated LCD (1.85-inch, or optional 4-inch DSI head) · five distance sensors · white light + RGB halo",s["BodyL"]),
       Paragraph("Revision B / September 2026 / Digital prototype release",s["SmallL"]),PageBreak(),
       Paragraph("Inside the build",s["H1L"])])
    toc=TableOfContents(); toc.levelStyles=[s["TOCL"]]; story.extend([toc,PageBreak()])
    for i,p in enumerate(chapters):
        if i: story.append(PageBreak())
        story.extend(markdown(p,s))
        if p.name=="overview.md":
            story.extend([PageBreak(),Paragraph("System at a glance",s["H1L"]),Architecture(),Spacer(1,12),
                Paragraph("The Pi supplies control commands. Dedicated motor and LED power paths keep the actuator load off the Pi's supply. The detailed wiring chapter is authoritative for the power-disconnect circuit and common grounds.",s["BodyL"])])
    story.extend([PageBreak(),Paragraph("Component source register",s["H1L"]),
                  Paragraph("Vendor information checked for this digital release. Order by exact part number and verify the revision supplied. Prices in the BOM are budgeting references, not quotations.",s["BodyL"])])
    for source in json.loads((ROOT/"docs/sources.json").read_text(encoding="utf-8")):
        title=html.escape(source["title"]); url=html.escape(source["url"],quote=True)
        story.append(Paragraph(f'<b>{source["id"]}</b> · <link href="{url}" color="#007F80">{title}</link><br/>{html.escape(source["use"])}',s["BodyL"]))
    doc=Manual(OUT/"LUMA_Manual_Text.pdf"); doc.multiBuild(story)
    import fitz
    merged=fitz.open(OUT/"LUMA_Manual_Text.pdf")
    toc=merged.get_toc()
    for relative in cfg.get("append_pdfs",[]):
        p=ROOT/relative
        if not p.exists(): raise FileNotFoundError(p)
        extra=fitz.open(p); start=merged.page_count
        merged.insert_pdf(extra)
        toc.append([1,"Engineering drawings",start+1])
        for level,title,page in extra.get_toc(): toc.append([min(level+1,2),title,start+page])
        extra.close()
    merged.set_toc(toc); merged.set_metadata({"title":"LUMA — Complete assembly manual and drawings","author":"LUMA project","subject":"Revision B digital prototype"})
    merged.save(OUT/"LUMA_Assembly_Manual.pdf",garbage=4,deflate=True)
    pages=merged.page_count; merged.close()
    print(f"Manual: {pages} pages -> deliverables/LUMA_Assembly_Manual.pdf")


if __name__=="__main__": main()
