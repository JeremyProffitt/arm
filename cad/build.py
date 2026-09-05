"""Rebuild printable STLs, assembly transforms and measurable validation report.

Revision B writes two assemblies from the same parts: assembly.json (standard 1.85-inch head)
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
 ('base_tub','Weighted base enclosure',1,'PETG','floor down','216 diameter; 50 high; 3 floor; 3.5 wall','6 M3x12 lid screws; 4 M4 ballast retainers'),
 ('base_lid','Vented base lid and yaw bearing seat',1,'PETG','flat annulus down','216 diameter; bearing pocket52.15 x7; 40.8 cable/hub bore','6 M3x12'),
 ('electronics_tray','Universal electronics tray with Pi4 standoffs',1,'PETG','plate down','166 x90; Pi4 hole pitch49 x58; 2.1mm M2.5 tapping pilots','4 M2.5x6 Pi; 4 M4x25 with metal spacers'),
 ('yaw_mount','Yaw servo rear body cradle',1,'PETG','base down','64 x46; pocket25.4; rear body clamp','4 M3x12 mount; 2 M3x45 clamp'),
 ('yaw_cap','Yaw clamp keeper',1,'PETG','flat down','47 x16 x2.6; clamp hole pitch37','2 M3x45'),
 ('turntable','Bearing supported yaw turntable',1,'PETG','neck down','82 diameter; neck39.75 x14.2; horn PCD14; tower52 x36','4 nominal M3x6 horn screws; 4 M3x16 tower'),
 ('shoulder_tower','Shoulder servo body tower',1,'PETG','foot down','64 x50; pitch axis47 above foot; body35.6 x25.4','4 M3x16; 2 M3x50 clamp'),
 ('shoulder_cap','Shoulder clamp keeper',1,'PETG','flat down','46 x28 x4; clamp pitch37','2 M3x50'),
 ('upper_arm_left','Upper arm enclosed link, left half',1,'PETG','plate down','140 pivot pitch; 54 assembled width; 32 to46 tapered height; 5 plate; 2.4 walls22 deep; integral servo pocket','4 nominal M3x10 horn; 3 M3x60 through bolts shared with right half'),
 ('upper_arm_right','Upper arm enclosed link, right half',1,'PETG','plate down','Mirror of left half; 140 pivot pitch; cable port on the inner elbow wall','4 nominal M3x10 horn; shared M3x60'),
 ('forearm_left','Forearm enclosed link, left half',1,'PETG','plate down','120 pivot pitch; 54 assembled width; 32 to46 tapered height; 5 plate; 2.4 walls22 deep; integral servo pocket','4 nominal M3x10 horn; 3 M3x60 through bolts shared with right half'),
 ('forearm_right','Forearm enclosed link, right half',1,'PETG','plate down','Mirror of left half; 120 pivot pitch; cable port on the inner wrist wall','4 nominal M3x10 horn; shared M3x60'),
 ('horn_spacer','Metal horn to link stand off',6,'PETG','flat down','20 diameter x3.3; PCD14; center6.5','shared nominal M3x10 horn screws'),
 ('head_yoke','Head tilt fork and rear mount',1,'PETG','rear mounting plate on bed; rotate180X','54 fork span; axis21 behind head rear; rear holes54 x30; 26 x8 centre cable slot','8 nominal M3 horn screws; 4 M3x12 rear screws'),
 ('head_shell','Optical head rear enclosure',1,'PETG','rear disc down','176 diameter x36; rear thickness3; white carrier bosses radius45 top32.5; 26 x8 centre cable slot','8 M3x10 bezel; 4 M3x12 yoke'),
 ('outer_bezel','Outer RGB diffuser retaining bezel',1,'PETG','front lip down','176 diameter; window160.5; 8 holes radius83','8 M3x10'),
 ('face_center','Central optical baffle plate',1,'black PETG','flat front down','142.6 diameter x4; center68.6; screws radius60','4 M3x12 into shell bosses'),
 ('white_carrier','White ring carrier and mounting arms',1,'PETG','flat down','68 OD51 ID; 4 cardinal mounting holes radius45; 2 thick','4 M3x10'),
 ('lcd_cradle','55 mm LCD edge cradle',1,'PETG','flat base down','55.8 square pocket; 15 depth; USB19 x13 relief','4 M3x25; thin closed cell foam shims'),
 ('lcd_retainer','LCD PCB corner retaining plate',1,'black PETG','flat down','77 square x3; opening70; mounting pitch68','4 M3x25 shared'),
 ('outer_diffuser','Frosted outer RGB annular diffuser',1,'natural/translucent PETG','smooth optical face on bed','160 face OD143 ID; 165 flange; 1.2 face; 6.2 depth','captured by outer bezel/center plate'),
 ('inner_diffuser','Frosted inner RGBW light diffuser',1,'natural/translucent PETG','smooth optical face on bed','68 OD47.8 ID; 1.2 face; 5.9 depth','3 tiny neutral cure silicone retention dots'),
 ('sensor_pod','Open optical ToF sensor body',5,'PETG','rear flange down','40 x30 x10; PCB26.1 x18.1; mount pitch34; two side QT plug windows','2 M3x10; 2 M2x14 each; two 18x2x6mm foam edge strips compressed to5.4mm'),
 ('sensor_retainer','ToF board edge retaining frame',5,'PETG','flat down','32 x24 x2; unobscured aperture24.9 x16.9','2 M2x14 each'),
 ('cable_clip','Harness saddle clip',6,'PETG','flat down','18 x12 x8; cable6; screws12 pitch','2 M2.5x12 each optional'),
 ('fit_coupon','Horn and bolt clearance coupons',1,'PETG','flat down','3.0 /3.2 /3.4 /3.6 bores; horn socket19.55','none'),
 ('head_shell_dsi','Optional DSI head rear enclosure',1,'PETG','rear disc down','176 diameter x36; carrier bosses (+/-55,+/-38) top20.5; face ring bosses radius67.8 top35; four wall pod mounts','8 M3x10 bezel; 4 M3x12 yoke; 4 M3x8 carrier; 4 M3x12 face ring'),
 ('lcd4_carrier','Optional 4 inch LCD carrier plate',1,'PETG','flat down','140 diameter x3; boss pads to5; LCD M4 pattern75 x75; PCB window100 x63 with connector notch','4 M4x8 into LCD case bosses; 4 M3x8 into shell bosses'),
 ('face_ring_dsi','Optional DSI face ring',1,'black PETG','flat front down','142.6 diameter x4; opening108 chamfered to116; screws radius67.8','4 M3x12 into shell bosses'),
 ('brow_bracket','Optional forward sensor brow bracket',1,'PETG','base plate down','40 x33 x30; wall holes pitch34 at Z14; pod holes pitch34; cable groove12 wide','2 M3x10 through shell wall; 2 M3x10 pod')]
VARIANT={'head_shell_dsi':'dsi-head','lcd4_carrier':'dsi-head','face_ring_dsi':'dsi-head','brow_bracket':'dsi-head'}
DSI_ONLY={'face_center','white_carrier','lcd_cradle','lcd_retainer','inner_diffuser','head_shell'}  # standard-head parts not used on the DSI head

def T(x=0,y=0,z=0):
 m=np.eye(4);m[:3,3]=[x,y,z];return m
def R(a,axis):
 return trimesh.transformations.rotation_matrix(math.radians(a),axis)
def P(a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a));m=np.eye(4);m[:3,:3]=[[0,0,1],[c,-s,0],[s,c,0]];return m
SH=np.array([0.,0.,115.]);EL=SH+P(115)[:3,:3]@np.array([140,0,0]);WR=EL+P(45)[:3,:3]@np.array([120,0,0]);H=T(*(WR+[0,21,0]))@R(180,[0,0,1])@R(90,[1,0,0])
LCD4_Z=31.67   # head Z of the vendor STEP z=0 datum: rim front (z3.83) lands at head Z35.5

# Purchased envelopes for assembly illustrations, never included in print quantities.
proxy=HERE/'visual_only';proxy.mkdir(exist_ok=True)
def boxfile(name,size):
 mesh=trimesh.creation.box(size);mesh.export(proxy/(name+'.stl'));return 'visual_only/'+name+'.stl'
def box_at(x0,x1,y0,y1,z0,z1):
 return trimesh.creation.box([x1-x0,y1-y0,z1-z0],transform=T((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def cyl_at(d,z0,z1,x=0,y=0):
 return trimesh.creation.cylinder(radius=d/2,height=z1-z0,sections=64,transform=T(x,y,(z0+z1)/2))
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
servofile=boxfile('servo_envelope',[45.22,24.72,35]);lcdfile=boxfile('lcd_board_envelope',[55,55,12]);lcd4file=lcd4_envelope()

def build_parts(variant):
 parts=[]
 def add(id,name,m,material='shell',group='base',explode=(0,0,0),file=None):
  parts.append(dict(name=name,file=file or f'stl/{id}.stl',matrix=m.tolist(),material=material,group=group,explode_mm=list(explode)))
 add('base_tub','Base enclosure',T(),explode=(0,0,-35))
 add('base_lid','Base lid',T(z=48),explode=(0,0,20))
 add('electronics_tray','Pi and electronics tray',T(z=14),'dark',explode=(0,-120,30))
 add('yaw_mount','Yaw body clamp',T(z=9),'dark',explode=(60,0,20))
 add('yaw_cap','Yaw clamp keeper',T(z=47),'dark',explode=(75,0,40))
 add('turntable','Yaw rotating platform',T(z=47.8),'dark','yaw',(0,0,50))
 add('shoulder_tower','Shoulder tower',T(z=68),'shell','yaw',(0,0,65))
 add('shoulder_cap','Shoulder clamp keeper',T(17.8,0,91)@P(0),'dark','yaw',(50,0,65))
 for kind,pivot,angle,l,group in [('upper_arm',SH,115,140,'upper'),('forearm',EL,45,120,'forearm')]:
  frame=T(*pivot)@P(angle)
  add(kind+'_left',f'{group} left half',frame@T(z=-27),'shell',group,(-55,0,40))
  add(kind+'_right',f'{group} right half',frame@T(z=27)@R(180,[1,0,0]),'shell',group,(55,0,40))
  for side,z in [('left',-22),('right',18.7)]:
   add('horn_spacer',f'{group} {side} horn spacer',frame@T(z=z),'dark',group,(-35 if z<0 else 35,0,40))
 add('head_yoke','Head tilt fork',H@T(z=-36),'shell','head',(0,20,20))
 for side,x in [('left',-22),('right',18.7)]:add('horn_spacer',f'head {side} horn spacer',H@T(x,0,-21)@R(90,[0,1,0]),'dark','head',(-30 if x<0 else 30,0,20))
 if variant=='standard':
  for id,z,mat,ex in [('head_shell',0,'shell',(0,-40,0)),('outer_bezel',36,'shell',(0,-155,0)),('face_center',36,'dark',(0,-125,0)),('white_carrier',32.5,'dark',(0,-95,0)),('lcd_cradle',14,'dark',(0,-70,0)),('lcd_retainer',29,'dark',(0,-105,0))]:add(id,id.replace('_',' ').title(),H@T(z=z),mat,'head',ex)
  for id in ['outer_diffuser','inner_diffuser']:add(id,id.replace('_',' ').title(),H@T(z=42)@R(180,[1,0,0]),'diffuser','head',(0,-180,0))
  pods=[('front',T(0,54,40)),('rear',T(0,54,0)@R(180,[1,0,0])),('left',T(-88,0,14)@R(-90,[0,1,0])@R(90,[0,0,1])),('right',T(88,0,14)@R(90,[0,1,0])@R(90,[0,0,1])),('down',T(0,-88,14)@R(90,[1,0,0]))]
 else:
  for id,name,z,mat,ex in [('head_shell_dsi','DSI head shell',0,'shell',(0,-40,0)),('outer_bezel','Outer Bezel',36,'shell',(0,-155,0)),('face_ring_dsi','DSI face ring',36,'dark',(0,-125,0)),('lcd4_carrier','4 inch LCD carrier',20.5,'dark',(0,-70,0))]:add(id,name,H@T(z=z),mat,'head',ex)
  add('outer_diffuser','Outer Diffuser',H@T(z=42)@R(180,[1,0,0]),'diffuser','head',(0,-180,0))
  add('brow_bracket','Front sensor brow bracket',H@T(0,88,-1)@R(180,[0,0,1])@R(90,[1,0,0]),'dark','head',(0,-30,45))
  pods=[('front',T(0,103,32)),('rear',T(0,54,0)@R(180,[1,0,0])),('left',T(-88,0,14)@R(-90,[0,1,0])@R(90,[0,0,1])),('right',T(88,0,14)@R(90,[0,1,0])@R(90,[0,0,1])),('down',T(0,-88,14)@R(90,[1,0,0]))]
 for name,m in pods:
  add('sensor_pod',f'{name} ToF pod',H@m,'dark','head',(0,-30,0))
  add('sensor_retainer',f'{name} ToF edge retainer',H@m@T(z=10),'dark','head',(0,-40,0))
 for p in parts:
  if p['group']=='head' and not p['name'].startswith('rear'):
   p['explode_mm'][1]=abs(p['explode_mm'][1])
 for name,m,group in [('yaw',T(0,-12.5,29.5)@R(90,[0,0,1]),'base'),('shoulder',T(*SH)@P(90)@T(-12.5,0,0),'yaw'),('elbow',T(*EL)@P(115)@T(-12.5,0,0),'upper'),('wrist',T(*WR)@P(45)@T(-12.5,0,0),'forearm')]:add('',name+' purchased ST3215',m,'dark',group,file=servofile)
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
 assembly=dict(units='mm',variant=variant,parts=parts,joints=[dict(name=n,pivot_mm=list(p),axis=a) for n,p,a in [('yaw',[0,0,60],[0,0,1]),('shoulder',SH,[1,0,0]),('elbow',EL,[1,0,0]),('wrist',WR,[1,0,0])]],face=face,group_chains={'base':[],'yaw':['yaw'],'upper':['yaw','shoulder'],'forearm':['yaw','shoulder','elbow'],'head':['yaw','shoulder','elbow','wrist']},neutral=dict(shoulder_world_deg=115,forearm_world_deg=45,head_normal=[0,1,0]),notes='Purchased envelope meshes are visual-only. Explode offsets are illustrative, not insertion paths.'+(' Optional 4inch DSI head variant: same base, arm and yoke as the standard assembly.' if variant!='standard' else ''))
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
 'base_tub':'M4 clearance4.4 at (+/-45,+/-35). Yaw bolts3.4 at (+/-26,-36) and (+/-26,-8). Six lid pilots2.8 at radius99 angles30+60n deg.',
 'base_lid':'Six3.4 holes radius99 angles30+60n deg. Bearing52.15 bore by7 depth. STL bottom datum is2mm below principal lid underside.',
 'electronics_tray':'M4 holes (+/-45,+/-35). Pi M2.5 pilots2.1 at X=-81,-32 and Y=-20,38. Central rounded36x54 clearance centered(0,-13). Four7mm tool apertures at yaw bolts.',
 'yaw_mount':'Four3.4 floor holes (+/-26,-36/-8). Keeper bolts at (+/-18.5,-25). Servo shaft atXY(0,0).',
 'yaw_cap':'Two3.4 holes (+/-18.5,-25). Keeper center(0,-30); thickness2.6.',
 'turntable':'Horn4x3.3 at (0,+/-7),(+/-7,0); center6.5 in3mm web. Tower4x3.4 at(+/-26,+/-18). Top central tool aperture22.',
 'shoulder_tower':'Foot4x3.4 at(+/-26,+/-18). Clamp holes alongX atY+/-18.5,Z23. Pitch axis47 abovefoot.',
 'shoulder_cap':'Two3.4 holes (+/-18.5,0). Printedface46x28.',
 'upper_arm_left':'Proximal horn4x3.3 at(0,+/-7),(+/-7,0). Through bolt3.4 at(35,0); servo block bolts at(115,+/-18.5). Pocket floor4.2 above plate; walls fromX28; cable port21x9 centred X87 on the -Y wall at the mid-plane. Distal shaft140 from proximal.',
 'upper_arm_right':'Mirror image of upper_arm_left about its length; same hole pattern. Assembled with the plate outward, walls meeting the left half at the link mid-plane.',
 'forearm_left':'Proximal horn4x3.3 at(0,+/-7),(+/-7,0). Through bolt3.4 at(35,0); servo block bolts at(95,+/-18.5). Pocket floor4.2 above plate; walls fromX28; cable port21x9 centred X67 on the -Y wall. Distal shaft120 from proximal.',
 'forearm_right':'Mirror image of forearm_left about its length; same hole pattern.',
 'horn_spacer':'PCD14 four3.3 holes; center6.5; thickness3.3.',
 'head_yoke':'Back bolts3.4 XY(+/-27,+/-15); attachmentplaneZ36. HornaxesX atY0,Z15, PCD14. Forkinsidewidth44. Centre cable slot26x8 through the plate.',
 'head_shell':'Rear bolts(+/-27,+/-15); LCDpilots(+/-34,+/-34),top14. Whitecarrierpilotsradius45 cardinal,top32.5. Facebossradius60 angles45+90n,top35. Bezelradius83 angles22.5+45n,top35. Centre cable slot26x8.',
 'outer_bezel':'Eight3.4 holes radius83 angles22.5+45n. Rearflangerecessdiameter165.5 by1.4 deep; facewindow160.5.',
 'face_center':'Four3.4 holesradius60 angles45+90n. Frontpodholes(+/-17,54); cablehole(0,54)diameter12.',
 'white_carrier':'Four3.4 holes at(+/-45,0),(0,+/-45). Allarmsandring2mmthick.',
 'lcd_cradle':'Four3.4 holes(+/-34,+/-34). Inner55.8square cavity. Rear49squareaccess. USBopening19wide at-Y.',
 'lcd_retainer':'Four3.4 holes(+/-34,+/-34). Diameter70centeropening retainsPCBcorners, not roundglass.',
 'outer_diffuser':'FaceOD160 ID143. RearflangesOD165/ID158.8 andOD144.2/ID141. M3edgeclearancenotchesradius83.',
 'inner_diffuser':'OD68 ID47.8; skin1.2; depth5.9. No sensorwindowmaterial.',
 'sensor_pod':'Mount3.4 at(+/-17,0). M2holes2.2 at(+/-13.7,8.9). SideQTplugreliefs on +/-X, width8inY, Z3.5to10.',
 'sensor_retainer':'M2holes2.2 at(+/-13.7,8.9). Opticalopening24.9x16.9.',
 'cable_clip':'Two2.5holes(+/-6,0); cablebore6 alongY centeredZ4.',
 'fit_coupon':'Bolt bores3.0,3.2,3.4,3.6 atX=-24,-8,8,24; hornsocket19.55 centeredY26.',
 'head_shell_dsi':'Rear bolts(+/-27,+/-15). Carrier pilots2.8 at(+/-55,+/-38) top20.5. Face ring pilots2.8 radius67.8 angles45+90n top35. Bezel radius83 angles22.5+45n top35. Wall pod mounts at0,90,180,270 deg Z14. Centre cable slot26x8.',
 'lcd4_carrier':'M4 clearance4.4 at(+/-37.5,+/-37.5) on5mm pads. Shell screws3.4 at(+/-55,+/-38). Face ring boss clearance8.5 radius67.8. PCB window X-44..56 Y-33..30 plus connector notch X-32..11 Y-41..-31.',
 'face_ring_dsi':'Four3.4 holes radius67.8 angles45+90n. Rear opening108 chamfered to116 at the front. Rear flange recess145/140.5 by1.4.',
 'brow_bracket':'Wall bolts3.4 at(+/-17,15) through the base plate. Pod bolts3.4 at(+/-17) and21x12 cable opening centred15 above the base on the front plate. Cable groove12 wide fromY9 to the front plate.'}
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
