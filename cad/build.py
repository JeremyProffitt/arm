"""Rebuild printable STLs, assembly transforms and measurable validation report.

Revision C writes two assemblies from the same parts: assembly.json (standard 1.85-inch head)
and assembly_dsi.json (optional Waveshare 4inch DSI LCD (C) head). Parts flagged variant
'dsi-head' are printed only for the optional head.
"""
from pathlib import Path
import json, math, subprocess, concurrent.futures, os
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent
OUT=HERE/'stl'; OUT.mkdir(exist_ok=True)
SPEC=[
 ('base_tub','Weighted base enclosure with five internal ToF mounts',1,'PETG','floor down','216 diameter; 56 high; 3 floor; 3.5 wall; five sensor apertures and 20 internal bosses','6 M3x12 lid screws; 4 M4 ballast retainers; 20 M2.5x6 sensor screws'),
 ('base_lid','Vented base lid and yaw bearing seat',1,'PETG','flat annulus down','216 diameter; bearing pocket52.15 x7; 40.8 cable/hub bore','6 M3x12'),
 ('electronics_tray','Universal electronics tray with Pi4 standoffs',1,'PETG','plate down','166 x90; Pi4 hole pitch49 x58; 2.1mm M2.5 tapping pilots','4 M2.5x6 Pi; 4 M4x25 with metal spacers'),
 ('yaw_mount','DS3218MG yaw servo rear-body cradle',1,'PETG','base down','64 x46; pocket20.7; 40.5-high rear body clamp','4 M3x12 mount; 2 M3x50 clamp'),
 ('yaw_cap','Yaw clamp keeper',1,'PETG','flat down','47 x16 x2.6; clamp hole pitch37','2 M3x50'),
 ('turntable','Bearing-supported yaw turntable for straight servo arm',1,'PETG','neck down','82 diameter; neck39.75 x14.2; two adjustable radial horn slots; tower52 x36','2 horn-arm bolts; 4 M3x16 tower'),
 ('shoulder_tower','DS3218MG shoulder body tower with idler support',1,'PETG','foot down','70 x50; pitch axis47 above foot; body pocket41.2 x20.7; M5 idler nut trap','4 M3x16; 2 M3x50 clamp; 1 M5 idler bolt and 625 bearing'),
 ('shoulder_cap','Shoulder clamp keeper',1,'PETG','flat down','46 x28 x4; clamp pitch37','2 M3x50'),
 ('upper_arm_left','Upper arm enclosed link, idler half',1,'PETG','plate down','140 pivot pitch; 62 assembled width; 5 plate; 2.4 walls26 deep; 625 bearing pocket; distal M5 idler nut trap','1 M5 idler bolt; 3 M3x60 through bolts shared with right half'),
 ('upper_arm_right','Upper arm enclosed link, driven half',1,'PETG','plate down','140 pivot pitch; 62 assembled width; two proximal horn-arm slots; cable port on inner elbow wall','2 horn-arm bolts; shared M3x60'),
 ('forearm_left','Forearm enclosed link, idler half',1,'PETG','plate down','120 pivot pitch; 62 assembled width; 625 bearing pocket; distal M5 idler nut trap','1 M5 idler bolt; 3 M3x60 through bolts shared with right half'),
 ('forearm_right','Forearm enclosed link, driven half',1,'PETG','plate down','120 pivot pitch; 62 assembled width; two proximal horn-arm slots; cable port on inner wrist wall','2 horn-arm bolts; shared M3x60'),
 ('horn_spacer','DS3218 straight-horn to driven-link spacer',3,'PETG','flat down','30 x14 x3.3; center7; adjustable radial slots12-18 and20-25','2 horn-arm bolts each'),
 ('head_yoke','Head tilt fork with driven and 625-idler ears',1,'PETG','rear mounting plate on bed; rotate180X','62 fork inside span; axis21 behind head rear; rear holes54 x30; 26 x8 centre cable slot','2 horn-arm bolts; 1 M5 idler bolt; 1 625 bearing; 4 M3x12 rear screws'),
 ('head_shell','Optical head rear enclosure',1,'PETG','rear disc down','176 diameter x36; rear thickness3; white carrier bosses radius45 top32.5; 26 x8 centre cable slot','8 M3x10 bezel; 4 M3x12 yoke'),
 ('outer_bezel','Outer RGB diffuser retaining bezel',1,'PETG','front lip down','176 diameter; window160.5; 8 holes radius83','8 M3x10'),
 ('face_center','Central optical baffle plate',1,'black PETG','flat front down','142.6 diameter x4; center68.6; screws radius60','4 M3x12 into shell bosses'),
 ('white_carrier','White ring carrier and mounting arms',1,'PETG','flat down','68 OD51 ID; 4 cardinal mounting holes radius45; 2 thick','4 M3x10'),
 ('lcd_cradle','55 mm LCD edge cradle',1,'PETG','flat base down','55.8 square pocket; 15 depth; USB19 x13 relief','4 M3x25; thin closed cell foam shims'),
 ('lcd_retainer','LCD PCB corner retaining plate',1,'black PETG','flat down','77 square x3; opening70; mounting pitch68','4 M3x25 shared'),
 ('outer_diffuser','Frosted outer RGB annular diffuser',1,'natural/translucent PETG','smooth optical face on bed','160 face OD143 ID; 165 flange; 1.2 face; 6.2 depth','captured by outer bezel/center plate'),
 ('inner_diffuser','Frosted inner RGBW light diffuser',1,'natural/translucent PETG','smooth optical face on bed','68 OD47.8 ID; 1.2 face; 5.9 depth','3 tiny neutral cure silicone retention dots'),
 ('cable_clip','Harness saddle clip',6,'PETG','flat down','18 x12 x8; cable6; screws12 pitch','2 M2.5x12 each optional'),
 ('fit_coupon','Fastener, 625 bearing and horn-slot clearance coupon',1,'PETG','flat down','3.0 /3.2 /3.4 /3.6 bores; 16.2 bearing pocket; DS3218 horn slots','none'),
 ('head_shell_dsi','Optional DSI head rear enclosure',1,'PETG','rear disc down','176 diameter x36; carrier bosses (+/-55,+/-38) top20.5; face ring bosses radius67.8 top35','8 M3x10 bezel; 4 M3x12 yoke; 4 M3x8 carrier; 4 M3x12 face ring'),
 ('lcd4_carrier','Optional 4 inch LCD carrier plate',1,'PETG','flat down','140 diameter x3; boss pads to5; LCD M4 pattern75 x75; PCB window100 x63 with connector notch','4 M4x8 into LCD case bosses; 4 M3x8 into shell bosses'),
 ('face_ring_dsi','Optional DSI face ring',1,'black PETG','flat front down','142.6 diameter x4; opening108 chamfered to116; screws radius67.8','4 M3x12 into shell bosses')]
VARIANT={'head_shell_dsi':'dsi-head','lcd4_carrier':'dsi-head','face_ring_dsi':'dsi-head'}
DSI_ONLY={'face_center','white_carrier','lcd_cradle','lcd_retainer','inner_diffuser','head_shell'}  # standard-head parts not used on the DSI head

def T(x=0,y=0,z=0):
 m=np.eye(4);m[:3,3]=[x,y,z];return m
def R(a,axis):
 return trimesh.transformations.rotation_matrix(math.radians(a),axis)
def P(a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a));m=np.eye(4);m[:3,:3]=[[0,0,1],[c,-s,0],[s,c,0]];return m
SH=np.array([0.,0.,121.]);EL=SH+P(115)[:3,:3]@np.array([140,0,0]);WR=EL+P(45)[:3,:3]@np.array([120,0,0]);H=T(*(WR+[0,21,0]))@R(180,[0,0,1])@R(90,[1,0,0])
LCD4_Z=31.67   # head Z of the vendor STEP z=0 datum: rim front (z3.83) lands at head Z35.5

# Purchased envelopes for assembly illustrations, never included in print quantities.
proxy=HERE/'visual_only';proxy.mkdir(exist_ok=True)
def boxfile(name,size):
 mesh=trimesh.creation.box(size);mesh.export(proxy/(name+'.stl'));return 'visual_only/'+name+'.stl'
def box_at(x0,x1,y0,y1,z0,z1):
 return trimesh.creation.box([x1-x0,y1-y0,z1-z0],transform=T((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cyl_at(d,z0,z1,x=0,y=0):
 return trimesh.creation.cylinder(radius=d/2,height=z1-z0,sections=64,transform=T(x,y,(z0+z1)/2))
def cyl_x_at(d,x0,x1,y=0,z=0):
 return trimesh.creation.cylinder(radius=d/2,height=x1-x0,sections=64,transform=T((x0+x1)/2,y,z)@R(90,[0,1,0]))
def tof_board_envelope():
 """Adafruit 3967 board with documented outline and mounting pattern; components are conservative."""
 pcb=box_at(-1.6,0,-12.7,12.7,-8.89,8.89)
 holes=[cyl_x_at(2.7,-2,0.4,y,z) for y in (-10.16,10.16) for z in (-6.35,6.35)]
 pcb=trimesh.boolean.difference([pcb,*holes],engine='manifold')
 components=box_at(0,3,-7.5,7.5,-5,5)
 mesh=trimesh.boolean.union([pcb,components],engine='manifold')
 mesh.export(proxy/'tof_board_envelope.stl')
 return 'visual_only/tof_board_envelope.stl'
def ds3218_envelope():
 """Miuzei drawing envelope relative to the output axis and top case face."""
 body=box_at(-30,10,-10,10,-40.5,0)
 mounting_tabs=box_at(-37.25,17.25,-10,10,-14,-11.5)
 mesh=trimesh.boolean.union([body,mounting_tabs],engine='manifold')
 mesh.export(proxy/'ds3218_envelope.stl')
 return 'visual_only/ds3218_envelope.stl'
def lcd4_envelope():
 """Waveshare 4inch DSI LCD (C) measured from the vendor STEP; LCD coordinates, +z toward the viewer."""
 solids=[cyl_at(126,-2.17,3.83)]
 for x,y in [(-37.5,-37.5),(37.5,-37.5),(-37.5,37.5),(37.5,37.5)]:solids.append(cyl_at(7.1,-6.17,-2.17,x,y))
 solids.append(box_at(-42.75,42.75,-37,28,-5.27,-3.67))                                   # PCB
 layer=box_at(-42.75,42.75,-37,28,-7.57,-5.27)                                             # general component layer
 layer=trimesh.boolean.difference([layer,*[cyl_at(9,-8,-5,x,y) for x,y in [(-37.5,-37.5),(37.5,-37.5)]]],engine='manifold')
 solids.append(layer)
 for x,y in [(-39.25,-24.5),(-39.25,24.5),(18.75,-24.5),(18.75,24.5)]:solids.append(cyl_at(5.5,-13.27,-3.77,x,y))  # Pi standoffs
 solids+= [box_at(-30.5,-18.5,-36,-27.8,-11.77,-5.27),   # HP2.0 power/touch connector
           box_at(-17.6,-12.5,-36,-31.9,-14.37,-5.27),   # 2.54mm headers
           box_at(-9.5,9.5,-36.8,-30.55,-7.64,-5.27),    # panel FPC connector
           box_at(-32.7,-23.7,21.4,29,-8.52,-5.27),      # USB-C
           box_at(13,21.2,-35.9,-29.7,-7.57,-5.22),      # switches
           box_at(-32.84,-28.3,-26.77,-22.23,-12.77,-7.27),
           box_at(36,43,-8,16,-8.5,-5.27)]               # DSI 15-pin FPC connector (position estimated from vendor photo)
 mesh=trimesh.boolean.union(solids,engine='manifold');mesh.export(proxy/'lcd4_envelope.stl');return 'visual_only/lcd4_envelope.stl'
servofile=ds3218_envelope();toffile=tof_board_envelope();lcdfile=boxfile('lcd_board_envelope',[55,55,12]);lcd4file=lcd4_envelope()

def build_parts(variant):
 parts=[]
 def add(id,name,m,material='shell',group='base',explode=(0,0,0),file=None):
  parts.append(dict(name=name,file=file or f'stl/{id}.stl',matrix=m.tolist(),material=material,group=group,explode_mm=list(explode)))
 add('base_tub','Base enclosure',T(),explode=(0,0,-35))
 for name,angle in [('front',90),('front-left',162),('rear-left',234),('rear-right',306),('front-right',18)]:
  add('',f'{name} purchased Adafruit 3967 ToF board',R(angle,[0,0,1])@T(99,0,25),'dark','base',file=toffile)
 add('base_lid','Base lid',T(z=54),explode=(0,0,20))
 add('electronics_tray','Pi and electronics tray',T(z=14),'dark',explode=(0,-120,30))
 add('yaw_mount','Yaw body clamp',T(z=9),'dark',explode=(60,0,20))
 add('yaw_cap','Yaw clamp keeper',T(z=52.5),'dark',explode=(75,0,40))
 add('turntable','Yaw rotating platform',T(z=53),'dark','yaw',(0,0,50))
 add('shoulder_tower','Shoulder tower',T(z=74),'shell','yaw',(0,0,65))
 add('shoulder_cap','Shoulder clamp keeper',T(20.6,0,101)@P(0),'dark','yaw',(50,0,65))
 for kind,pivot,angle,l,group in [('upper_arm',SH,115,140,'upper'),('forearm',EL,45,120,'forearm')]:
  frame=T(*pivot)@P(angle)
  add(kind+'_left',f'{group} idler half',frame@T(z=-31),'shell',group,(-55,0,40))
  add(kind+'_right',f'{group} driven half',frame@T(z=31)@R(180,[1,0,0]),'shell',group,(55,0,40))
  add('horn_spacer',f'{group} driven horn spacer',frame@T(z=22.7),'dark',group,(35,0,40))
 add('head_yoke','Head tilt fork',H@T(z=-36),'shell','head',(0,20,20))
 add('horn_spacer','head driven horn spacer',H@T(-22.7,0,-21)@R(-90,[0,1,0])@R(90,[0,0,1]),'dark','head',(30,0,20))
 if variant=='standard':
  for id,z,mat,ex in [('head_shell',0,'shell',(0,-40,0)),('outer_bezel',36,'shell',(0,-155,0)),('face_center',36,'dark',(0,-125,0)),('white_carrier',32.5,'dark',(0,-95,0)),('lcd_cradle',14,'dark',(0,-70,0)),('lcd_retainer',29,'dark',(0,-105,0))]:add(id,id.replace('_',' ').title(),H@T(z=z),mat,'head',ex)
  for id in ['outer_diffuser','inner_diffuser']:add(id,id.replace('_',' ').title(),H@T(z=42)@R(180,[1,0,0]),'diffuser','head',(0,-180,0))
 else:
  for id,name,z,mat,ex in [('head_shell_dsi','DSI head shell',0,'shell',(0,-40,0)),('outer_bezel','Outer Bezel',36,'shell',(0,-155,0)),('face_ring_dsi','DSI face ring',36,'dark',(0,-125,0)),('lcd4_carrier','4 inch LCD carrier',20.5,'dark',(0,-70,0))]:add(id,name,H@T(z=z),mat,'head',ex)
  add('outer_diffuser','Outer Diffuser',H@T(z=42)@R(180,[1,0,0]),'diffuser','head',(0,-180,0))
 for p in parts:
  if p['group']=='head' and not p['name'].startswith('rear'):
   p['explode_mm'][1]=abs(p['explode_mm'][1])
 for name,m,group in [('yaw',T(0,0,52.5)@R(90,[0,0,1]),'base'),('shoulder',T(*SH)@P(90)@T(z=20.25),'yaw'),('elbow',T(*EL)@P(115)@T(z=20.25),'upper'),('wrist',T(*WR)@P(45)@T(z=20.25),'forearm')]:add('',name+' inventory Miuzei DS3218MG',m,'dark',group,file=servofile)
 if variant=='standard':
  add('','Purchased LCD envelope',H@T(z=23),'dark','head',file=lcdfile)
  face=dict(center_mm=(H@np.array([0,0,31.2,1]))[:3].tolist(),normal=[0,1,0],up=[0,0,1],radius_mm=22.84)
 else:
  add('','Purchased 4inch DSI LCD (C) envelope',H@T(z=LCD4_Z),'dark','head',(0,95,0),file=lcd4file)
  face=dict(center_mm=(H@np.array([0,0,LCD4_Z+3.58,1]))[:3].tolist(),normal=[0,1,0],up=[0,0,1],radius_mm=50.76)
 return parts,face

ASSEMBLIES={'standard':('assembly.json','assembly.scad','assembled_reference_DO_NOT_PRINT.stl'),
            'dsi-head':('assembly_dsi.json','assembly_dsi.scad','assembled_reference_dsi_DO_NOT_PRINT.stl')}
assemblies={}
for variant,(jsonname,scadname,refname) in ASSEMBLIES.items():
 parts,face=build_parts(variant)
 assembly=dict(units='mm',variant=variant,parts=parts,joints=[dict(name=n,pivot_mm=list(p),axis=a) for n,p,a in [('yaw',[0,0,66],[0,0,1]),('shoulder',SH,[1,0,0]),('elbow',EL,[1,0,0]),('wrist',WR,[1,0,0])]],face=face,group_chains={'base':[],'yaw':['yaw'],'upper':['yaw','shoulder'],'forearm':['yaw','shoulder','elbow'],'head':['yaw','shoulder','elbow','wrist']},neutral=dict(shoulder_world_deg=115,forearm_world_deg=45,head_normal=[0,1,0]),notes='Purchased envelope meshes are visual-only. Explode offsets are illustrative, not insertion paths. Four DS3218MG servos drive straight horns on the driven side; three 625 bearings support the opposite pitch-joint sides.'+(' Optional 4inch DSI head variant: same base, arm and yoke as the standard assembly.' if variant!='standard' else ''))
 (HERE/jsonname).write_text(json.dumps(assembly,indent=2))
 preview=['// Full assembled STL preview ('+variant+'); regenerate with build.py. Units mm.']
 for p in parts:
  color={'shell':[.80,.83,.81],'dark':[.08,.11,.12],'diffuser':[.87,.95,.94]}.get(p['material'],[.6,.6,.6])
  preview.append('color('+str(color)+') multmatrix('+str(p['matrix'])+') import("'+p['file']+'");')
 (HERE/scadname).write_text('\n'.join(preview))
 assemblies[variant]=(parts,refname)
(HERE/'assembly_preview.scad').write_text((HERE/'assembly.scad').read_text())
manifest=[dict(id=p[0],name=p[1],qty=p[2],material=p[3],orientation=p[4],dimensions=p[5],fasteners=p[6],file=f'stl/{p[0]}.stl',variant=VARIANT.get(p[0],'standard'),layer_mm=.15 if 'diffuser' in p[0] else .2,walls=3 if 'diffuser' in p[0] else 6 if ('arm' in p[0] and p[0]!='lcd4_carrier') else 4,infill_percent=100 if 'diffuser' in p[0] else 40 if ('arm' in p[0] and p[0]!='lcd4_carrier') else 25) for p in SPEC]
features={
 'base_tub':'M4 clearance4.4 at (+/-45,+/-35). Yaw bolts3.4 at (+/-26,-36) and (+/-26,-8). Six lid pilots2.8 at radius99, angles42/66/126/198/258/342deg. Five 10x10 wall apertures at18/90/162/234/306deg, Z25. Each board has four2.1 blind pilots on20.32x12.70 at tangent radius99. Rear ports occupy270/282deg.',
 'base_lid':'Six3.4 holes radius99 at42/66/126/198/258/342deg. Bearing52.15 bore by7 depth. STL bottom datum is2mm below principal lid underside.',
 'electronics_tray':'M4 holes (+/-45,+/-35). Pi M2.5 pilots2.1 at X=-81,-32 and Y=-20,38. Central rounded36x54 clearance centered(0,-13). Four7mm tool apertures at yaw bolts.',
 'yaw_mount':'Four3.4 floor holes (+/-26,-36/-8). Keeper bolts at (+/-18.5,-27). DS3218 shaft atXY(0,0), output case plane Z43.5 in part coordinates.',
 'yaw_cap':'Two3.4 holes (+/-18.5,-27). Keeper center(0,-30); thickness2.6.',
 'turntable':'Straight-horn center clearance7 with radial3.4 slots12-18 and20-25 in3mm web. Tower4x3.4 at(+/-26,+/-18). Top central tool aperture22.',
 'shoulder_tower':'Foot4x3.4 at(+/-26,+/-18). Clamp holes alongX atY+/-18.5,Z29. Pitch axis47 abovefoot. Left idler M5 clearance and captive nut in20mm boss.',
 'shoulder_cap':'Two3.4 holes (+/-18.5,0). Printedface46x28.',
 'upper_arm_left':'Proximal 625 pocket16.2. Through bolt3.4 at(35,0); block bolts at(115,+/-18.5). DS3218 pocket41.2x20.7; walls fromX28; distal M5 nut trap atX140; cable port21x9 centredX87.',
 'upper_arm_right':'Driven side has center7 and radial3.4 slots12-18 and20-25. Same clamp-bolt pattern as left; cable port remains on the inner elbow wall after assembly.',
 'forearm_left':'Proximal 625 pocket16.2. Through bolt3.4 at(35,0); block bolts at(95,+/-18.5). DS3218 pocket41.2x20.7; distal M5 nut trap atX120; cable port21x9 centredX67.',
 'forearm_right':'Driven side has center7 and radial3.4 slots12-18 and20-25. Same clamp-bolt pattern as left; cable port remains on the inner wrist wall after assembly.',
 'horn_spacer':'Center7; radial3.4 slots12-18 and20-25; thickness3.3; one driven-side spacer per pitch joint.',
 'head_yoke':'Back bolts3.4 XY(+/-27,+/-15); attachmentplaneZ36. AxisX atY0,Z15; one625 pocket16.2 and one tangential straight-horn interface; fork inside width52. Centre cable slot26x8.',
 'head_shell':'Rear bolts(+/-27,+/-15); LCDpilots(+/-34,+/-34),top14. Whitecarrierpilotsradius45 cardinal,top32.5. Facebossradius60 angles45+90n,top35. Bezelradius83 angles22.5+45n,top35. Centre cable slot26x8. No sensor penetrations.',
 'outer_bezel':'Eight3.4 holes radius83 angles22.5+45n. Rearflangerecessdiameter165.5 by1.4 deep; facewindow160.5.',
 'face_center':'Four3.4 holesradius60 angles45+90n. No sensor penetrations.',
 'white_carrier':'Four3.4 holes at(+/-45,0),(0,+/-45). Allarmsandring2mmthick.',
 'lcd_cradle':'Four3.4 holes(+/-34,+/-34). Inner55.8square cavity. Rear49squareaccess. USBopening19wide at-Y.',
 'lcd_retainer':'Four3.4 holes(+/-34,+/-34). Diameter70centeropening retainsPCBcorners, not roundglass.',
 'outer_diffuser':'FaceOD160 ID143. RearflangesOD165/ID158.8 andOD144.2/ID141. M3edgeclearancenotchesradius83.',
 'inner_diffuser':'OD68 ID47.8; skin1.2; depth5.9. No sensorwindowmaterial.',
 'cable_clip':'Two2.5holes(+/-6,0); cablebore6 alongY centeredZ4.',
 'fit_coupon':'Bolt bores3.0,3.2,3.4,3.6; 625 bearing pocket16.2; straight-horn center7 and radial slots12-18 and20-25.',
 'head_shell_dsi':'Rear bolts(+/-27,+/-15). Carrier pilots2.8 at(+/-55,+/-38) top20.5. Face ring pilots2.8 radius67.8 angles45+90n top35. Bezel radius83 angles22.5+45n top35. Centre cable slot26x8. No sensor penetrations.',
 'lcd4_carrier':'M4 clearance4.4 at(+/-37.5,+/-37.5) on5mm pads. Shell screws3.4 at(+/-55,+/-38). Face ring boss clearance8.5 radius67.8. PCB window X-44..56 Y-33..30 plus connector notch X-32..11 Y-41..-31.',
 'face_ring_dsi':'Four3.4 holes radius67.8 angles45+90n. Rear opening108 chamfered to116 at the front. Rear flange recess145/140.5 by1.4.'}
for p in manifest:p['critical_holes']=features[p['id']]
(HERE/'part_manifest.json').write_text(json.dumps(manifest,indent=2))
def export(p):
 id=p[0]; dest=OUT/(id+'.stl')
 command=[os.environ.get('OPENSCAD','C:/Program Files/OpenSCAD/openscad.com'),'-o',str(dest),'-D',f'part="{id}"',str(HERE/'luma.scad')]
 if id=='electronics_tray':command[1:1]=['-D','$fn=32']
 res=subprocess.run(command,capture_output=True,text=True)
 (HERE/(id+'.log')).write_text(res.stderr)
 if res.returncode or not dest.exists():return {'id':id,'error':res.stderr}
 mesh=trimesh.load_mesh(dest);ext=mesh.extents
 result=dict(id=id,watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),positive_volume=bool(mesh.volume>0),bodies=body_count(mesh),bounds_mm=mesh.bounds.tolist(),size_mm=ext.tolist(),volume_cm3=round(mesh.volume/1000,3),triangles=len(mesh.faces),fits_220_bed=bool(ext[0]<=220 and ext[1]<=220))
 print(id,result['watertight'],result['bodies'],flush=True);return result
def body_count(mesh):
 parent=list(range(len(mesh.faces)))
 def root(i):
  while parent[i]!=i:
   parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b in mesh.face_adjacency:
  a,b=root(int(a)),root(int(b))
  if a!=b:parent[b]=a
 return len({root(i) for i in range(len(parent))})
def export_reference_assembly():
 for variant,(parts,refname) in assemblies.items():
  meshes=[]
  for p in parts:
   m=trimesh.load_mesh(HERE/p['file']);m.apply_transform(np.asarray(p['matrix']));meshes.append(m)
  trimesh.util.concatenate(meshes).export(proxy/refname)
if __name__=='__main__':
 import sys
 only=set(sys.argv[1:])
 todo=[p for p in SPEC if not only or p[0] in only]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(export,todo))
 if only:
  previous={r['id']:r for r in json.loads((HERE/'validation.json').read_text())} if (HERE/'validation.json').exists() else {}
  previous.update({r['id']:r for r in results});results=[previous[p[0]] for p in SPEC if p[0] in previous]
 (HERE/'validation.json').write_text(json.dumps(results,indent=2))
 for row in manifest:
  match=next((r for r in results if r['id']==row['id']),{})
  row.update({k:match[k] for k in ['size_mm','volume_cm3'] if k in match})
 (HERE/'part_manifest.json').write_text(json.dumps(manifest,indent=2))
 export_reference_assembly()
 failures=[r for r in results if not r.get('watertight') or not r.get('positive_volume')]
 print('Failures:',failures)
 raise SystemExit(bool(failures))
