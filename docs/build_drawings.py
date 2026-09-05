"""Generate dimensioned A3 vector drawing sheets directly from the final STLs.

Views use projected mesh surfaces with feature edges. Dimensions and interface
notes supplement the editable solid model; they are not machining tolerances.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import textwrap

import numpy as np
import trimesh
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm

from build_manual import register_fonts

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
OUT = ROOT / "deliverables"
W,H=landscape(A3)
INK=colors.HexColor("#17313D")
MUTED=colors.HexColor("#506672")
TEAL=colors.HexColor("#007F80")
LINE=colors.HexColor("#D0DEDF")
VIEWS={"TOP / XY":np.eye(3),"FRONT / XZ":np.array([[1,0,0],[0,0,1],[0,-1,0]]),
       "RIGHT / YZ":np.array([[0,1,0],[0,0,1],[1,0,0]])}
ISO=np.array([[1,1,0],[-1,1,2],[1,-1,1]],float)
ISO/=np.linalg.norm(ISO,axis=1)[:,None]


def text(c,x,y,value,size=9,font="Luma",color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,str(value))


def border(c,title,number,subtitle=""):
    c.setFillColor(colors.white);c.rect(0,0,W,H,stroke=0,fill=1)
    c.setStrokeColor(INK);c.setLineWidth(.7);c.rect(25,25,W-50,H-50)
    c.setFillColor(TEAL);c.rect(25,H-45,W-50,20,stroke=0,fill=1)
    text(c,40,H-39,"LUMA / ENGINEERING DRAWINGS",9,"Luma-Bold",colors.white)
    text(c,40,H-75,title,21,"Luma-Bold")
    text(c,40,H-95,subtitle,8.6,color=MUTED)
    c.setStrokeColor(LINE);c.line(25,82,W-25,82)
    c.line(W-260,25,W-260,82)
    text(c,40,63,"UNITS mm  ·  THIRD-ANGLE PART VIEWS  ·  NUMERICAL DIMENSIONS CONTROL",8,"Luma-Bold")
    text(c,40,47,"Views fitted to sheet. Do not measure this PDF. Digital prototype; check physical fit before batch printing.",7.4,color=MUTED)
    text(c,W-246,62,number,15,"Luma-Bold")
    text(c,W-246,43,"REV A  |  04 SEP 2026  |  A3",8,color=MUTED)
    c.bookmarkPage(number);c.addOutlineEntry(f"{number} — {title}",number,0,False)


def dim_h(c,x0,x1,y,label):
    c.setLineWidth(.5);c.setStrokeColor(TEAL)
    c.line(x0,y,x1,y)
    for x in (x0,x1):c.line(x,y-4,x,y+6)
    c.setFillColor(TEAL);c.setFont("Luma",8)
    c.drawCentredString((x0+x1)/2,y-12,label)


def dim_v(c,x,y0,y1,label):
    c.setLineWidth(.5);c.setStrokeColor(TEAL);c.line(x,y0,x,y1)
    for y in (y0,y1):c.line(x-4,y,x+6,y)
    c.saveState();c.translate(x-8,(y0+y1)/2);c.rotate(90)
    c.setFillColor(TEAL);c.setFont("Luma",8);c.drawCentredString(0,0,label);c.restoreState()


def project(c,mesh,view,rect,title,dimensions=True,shaded=False):
    x,y,w,h=rect
    verts=np.asarray(mesh.vertices)@view.T
    lo,hi=verts.min(axis=0),verts.max(axis=0)
    span=np.maximum(hi-lo,1e-6)
    fitlo, fithi=lo[:2].copy(),hi[:2].copy()
    datum=title=="TOP / XY"
    if datum:
        fitlo=np.minimum(fitlo,0);fithi=np.maximum(fithi,0)
    fitspan=np.maximum(fithi-fitlo,1e-6)
    scale=min((w-70)/fitspan[0],(h-63)/fitspan[1])
    origin=np.array([x+w/2,y+h/2+5])-(fitlo+fithi)/2*scale
    points=verts[:,:2]*scale+origin
    normals=np.asarray(mesh.face_normals)@view.T
    faces=np.asarray(mesh.faces)
    active=normals[:,2]>1e-7
    sharp=set()
    if len(mesh.face_adjacency):
        adj=mesh.face_adjacency
        silhouette=active[adj[:,0]]!=active[adj[:,1]]
        include=(mesh.face_adjacency_angles>math.radians(8))|silhouette
        for a,b in mesh.face_adjacency_edges[include]:sharp.add((min(a,b),max(a,b)))
    ordering=np.argsort(verts[faces,2].mean(axis=1))
    light=np.array([-.25,-.35,1.0]);light/=np.linalg.norm(light)
    for fidx in ordering:
        if not active[fidx]:continue
        f=faces[fidx];p=points[f]
        if shaded:
            luminance=.77+.19*max(0,float(normals[fidx]@light))
            c.setFillColorRGB(luminance,luminance+.008,luminance+.012)
            c.setStrokeColorRGB(luminance,luminance+.008,luminance+.012)
        else:
            c.setFillColorRGB(.975,.983,.984)
            c.setStrokeColorRGB(.975,.983,.984)
        path=c.beginPath();path.moveTo(*p[0]);path.lineTo(*p[1]);path.lineTo(*p[2]);path.close()
        c.setLineWidth(.07)
        c.drawPath(path,fill=1,stroke=1)
        c.setLineWidth(.38);c.setStrokeColor(INK)
        for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
            if (min(a,b),max(a,b)) in sharp:c.line(*points[a],*points[b])
    text(c,x+8,y+h-7,title,9,"Luma-Bold",TEAL)
    bbox0=lo[:2]*scale+origin;bbox1=hi[:2]*scale+origin
    if dimensions:
        dim_h(c,bbox0[0],bbox1[0],bbox0[1]-15,f"{span[0]:.2f}")
        dim_v(c,bbox0[0]-16,bbox0[1],bbox1[1],f"{span[1]:.2f}")
    if datum:
        ox,oy=origin
        c.setStrokeColor(TEAL);c.setLineWidth(.55);c.setDash(3,2)
        c.lines([(ox-7,oy,ox+24,oy),(ox,oy-7,ox,oy+24)])
        c.setDash()
        text(c,ox+25,oy-2,"X",6.8,color=TEAL)
        text(c,ox+3,oy+24,"Y",6.8,color=TEAL)
        text(c,ox+4,oy-10,"0,0",6.4,color=TEAL)
    return (scale,origin,span)


def notes(c,content,x=45,y=167,width=145,lineheight=11):
    for para in content:
        for line in textwrap.wrap(str(para),width=width,break_long_words=False):
            text(c,x,y,line,8.0,color=MUTED);y-=lineheight
    return y


def mesh_for(file):
    mesh=trimesh.load_mesh(CAD/file,process=True)
    if not isinstance(mesh,trimesh.Trimesh): raise TypeError(file)
    return mesh


def assembly_mesh(assembly,group=None,explode=False):
    meshes=[]
    for item in assembly["parts"]:
        if group and item["group"]!=group:continue
        mesh=mesh_for(item["file"])
        matrix=np.array(item["matrix"],float)
        if explode:matrix[:3,3]+=np.array(item.get("explode_mm",[0,0,0]))
        mesh.apply_transform(matrix);meshes.append(mesh)
    return trimesh.util.concatenate(meshes)


def main():
    register_fonts();OUT.mkdir(exist_ok=True)
    manifest=json.loads((CAD/"part_manifest.json").read_text())
    assembly=json.loads((CAD/"assembly.json").read_text())
    target=OUT/"LUMA_Engineering_Drawings.pdf"
    c=canvas.Canvas(str(target),pagesize=(W,H),pageCompression=1)
    c.setTitle("LUMA — Dimensioned engineering drawing set, revision A")
    c.setAuthor("LUMA project")
    full=assembly_mesh(assembly)
    face_normal=np.array(assembly['face']['normal'],float)
    up=np.array(assembly['face']['up'],float)
    right=np.cross(up,face_normal);right/=np.linalg.norm(right)
    face_view=np.array([right,up,face_normal])
    head_iso=ISO if face_normal[1]<0 else np.array([[-1,1,0],[-1,-1,2],[1,1,1]],float)
    head_iso/=np.linalg.norm(head_iso,axis=1)[:,None]
    border(c,"Finished assembly / indexed neutral pose","G01","Assembled geometry from the same STL files supplied for printing. Purchased parts are simplified envelopes.")
    project(c,full,face_view,(55,225,390,475),"FRONT / LCD FACING VIEW")
    project(c,full,VIEWS["RIGHT / YZ"],(450,225,350,475),"RIGHT SIDE / NEUTRAL POSE")
    project(c,full,VIEWS["TOP / XY"],(820,355,305,345),"TOP / FOOTPRINT")
    p=assembly["joints"]
    notes(c,["Four axes: yaw about Z; shoulder, elbow and wrist about local X. Datum is the base underside at Z=0.",
             "Nominal linkage pitches: shoulder–elbow 140 mm; elbow–wrist 120 mm. The illustrated height is a pose dimension, not a motion envelope.",
             f"Neutral: shoulder link {assembly['neutral']['shoulder_world_deg']}° above horizontal; forearm {assembly['neutral']['forearm_world_deg']}° above horizontal; face directed toward {'+Y' if face_normal[1]>0 else '-Y'}. Follow indexed calibration in the manual.",
             "Do not infer screw lengths from the illustration. Fasteners and service loops are specified in the assembly chapter."],y=164)
    c.showPage()
    border(c,"Head / layered assembly study","G02","Exploded positions expose the optical parts; displacements are illustrative and are not insertion paths.")
    head=assembly_mesh(assembly,"head",True)
    head_scale,head_origin,_=project(c,head,head_iso,(50,210,710,490),"EXPLODED HEAD / MODEL-DERIVED VIEW",dimensions=False,shaded=True)
    headitems=[item for item in assembly["parts"] if item["group"]=="head" and "ToF" not in item["name"]]
    text(c,800,676,"LAYER REFERENCES",11,"Luma-Bold",TEAL)
    y=650
    for i,item in enumerate(headitems,1):
        mesh=mesh_for(item['file']);transform=np.array(item['matrix'],float)
        transform[:3,3]+=np.array(item.get('explode_mm',[0,0,0]))
        mesh.apply_transform(transform)
        center=mesh.bounds.mean(axis=0)@head_iso.T
        point=center[:2]*head_scale+head_origin
        c.setStrokeColor(TEAL);c.setLineWidth(.4)
        c.line(*point,782,y+2);c.setFillColor(TEAL);c.circle(*point,2,stroke=0,fill=1)
        for line in textwrap.wrap(f'{i:02d}  {item["name"]}',37):text(c,800,y,line,8.4);y-=15
    notes(c,["Central LCD board is behind the inner white ring. Keep all optical components at their documented axial heights.",
             "Use natural PETG for both light diffusers and opaque PETG for the optical baffle. Leave LCD glass and all ToF apertures clear.",
             "The four outer ring PCB quarters require continuous mechanical support. Solder joints are electrical connections only.",
             "Refer to the head assembly chapter for screw order, spacers, wire relief and board retention. Purchased LEDs are not printable parts."],y=164)
    c.showPage()
    schematic=ROOT/'electronics/wiring_overview.svg'
    schematic_count=0
    if schematic.exists():
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        border(c,"Electrical connections / system wiring","E01","Follow the point-to-point wiring schedule for connector pins, polarity and conductor ratings.")
        drawing=svg2rlg(str(schematic))
        ratio=min((W-100)/drawing.width,(H-210)/drawing.height)
        drawing.scale(ratio,ratio)
        renderPDF.draw(drawing,c,(W-drawing.width*ratio)/2,95)
        c.showPage();schematic_count=1
    border(c,"Steel ballast plate / fabrication drawing","F01","Purchased/custom-fabricated metal part M01. This sheet is not a printable-plastic substitute.")
    cx,cy=340,420
    c.setStrokeColor(INK);c.setLineWidth(.8);c.circle(cx,cy,90*mm,stroke=1,fill=0)
    c.setStrokeColor(TEAL);c.setLineWidth(.45);c.setDash(5,3)
    c.lines([(cx-95*mm,cy,cx+95*mm,cy),(cx,cy-95*mm,cx,cy+95*mm)]);c.setDash()
    for x in (-45,45):
        for y in (-35,35):
            c.setStrokeColor(INK);c.circle(cx+x*mm,cy+y*mm,2.2*mm,stroke=1,fill=0)
    for x in (-26,26):
        for y in (-36,-8):
            c.setStrokeColor(INK);c.circle(cx+x*mm,cy+y*mm,1.7*mm,stroke=1,fill=0)
    dim_h(c,cx-90*mm,cx+90*mm,715,"Ø180.00")
    dim_h(c,cx-45*mm,cx+45*mm,cy-35*mm-19,"90.00")
    dim_v(c,cx+45*mm+18,cy-35*mm,cy+35*mm,"70.00")
    dim_h(c,cx-26*mm,cx+26*mm,cy-36*mm-55,"52.00")
    dim_v(c,cx+26*mm+14,cy-36*mm,cy-8*mm,"28.00")
    text(c,cx+5,cy+7,"DATUM 0,0",8,"Luma-Bold",TEAL)
    text(c,cx+95*mm+5,cy,"+X",8,color=TEAL)
    text(c,cx+5,cy+95*mm,"+Y / FORWARD",8,color=TEAL)
    text(c,725,680,"MATERIAL + INTERFACES",12,"Luma-Bold",TEAL)
    notes(c,["Material: mild steel; finished thickness6.00mm.","Outer diameter180.00mm; deburr all edges and holes.",
             "Datum origin is the disc center. All hole axes normal to plate.","4 × Ø4.40 through: X=±45.00, Y=±35.00.",
             "4 × Ø3.40 through: X=±26.00, Y=-36.00 and-8.00.",
             "Do not add a center hole. Rear yaw bolt pattern points-Y.",
             "Nominal mass before drilling:1.19kg at steel density7.85g/cm³.",
             "Fit to printed base floor before final coating. Inspect burrs and screw-head clearance.",
             "Suggested workshop positional allowance±0.20mm; confirm actual printed mating pattern before drilling."],x=725,y=650,width=65,lineheight=14)
    text(c,725,240,"SIDE VIEW / THICKNESS",10,"Luma-Bold",TEAL)
    c.setStrokeColor(INK);c.rect(725,194,340,6*mm,stroke=1,fill=0)
    dim_v(c,1086,194,194+6*mm,"6.00")
    c.showPage()
    for index,part in enumerate(manifest,1):
        mesh=mesh_for(part["file"])
        code=f"P{index:02d}"
        border(c,part["name"],code,f'{part["id"]}.stl  |  PRINT QUANTITY {part["qty"]}  |  {part["material"]}')
        project(c,mesh,VIEWS["TOP / XY"],(65,445,440,265),"TOP / XY")
        project(c,mesh,VIEWS["FRONT / XZ"],(65,245,440,175),"FRONT / XZ")
        project(c,mesh,VIEWS["RIGHT / YZ"],(625,245,440,175),"RIGHT / YZ")
        project(c,mesh,ISO,(625,445,440,265),"ISOMETRIC / REFERENCE",dimensions=False,shaded=True)
        info=[f'Interfaces: {part["dimensions"]}.',f'Fasteners / retention: {part["fasteners"]}.',
              f'Print orientation: {part["orientation"]}. Layers {part["layer_mm"]} mm; {part["walls"]} walls; {part["infill_percent"]}% infill baseline.']
        critical=part.get("critical_holes") or part.get("critical_features")
        if critical:info.append("Feature locations: "+(critical if isinstance(critical,str) else json.dumps(critical)))
        info.append("General fit: inspect and deburr holes; check the fit coupon and actual hardware. No unlisted machining tolerances are implied.")
        notes(c,info,y=210,lineheight=10.5)
        c.showPage()
        print(f"Drawing {code}: {part['id']}",flush=True)
    c.save()
    print(f"{3+schematic_count+len(manifest)} vector sheets -> {target}")


if __name__=="__main__":main()
