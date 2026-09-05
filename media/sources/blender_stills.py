"""Optional physically lit renderer. Blender 4.5 LTS, run with -b -P this_file.

Uses exactly the assembly and display geometry in render_media.py. This is an
optional higher-quality renderer; the software pipeline remains self-contained.
"""
import sys, types, math, json, hashlib
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
# The shared CAD/kinematic model does not need Pillow inside Blender.
pil=types.ModuleType('PIL')
for name in ['Image','ImageDraw','ImageFont','ImageFilter','ImageChops']:setattr(pil,name,types.ModuleType(name))
sys.modules['PIL']=pil
sys.path.insert(0,str(HERE))
from render_media import Assembly, PALETTE

def material(name):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    srgb=np.asarray(PALETTE[name])/255
    rgb=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=.43
    if name in ['dark','servo','pcb']:
        p.inputs['Roughness'].default_value=.68
        p.inputs['Specular IOR Level'].default_value=.24
    if name in ['metal','fastener']:
        p.inputs['Metallic'].default_value=.7;p.inputs['Roughness'].default_value=.28
    if name in ['rgb','white','diffuser','eye']:
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=1.5 if name!='eye' else 2
        p.inputs['Roughness'].default_value=.6
    if name=='screen':p.inputs['Roughness'].default_value=.17
    return m

def mesh_object(name,tri,mat):
    mesh=bpy.data.meshes.new(name)
    vertices=(tri.reshape(-1,3)*.001).tolist()
    mesh.from_pydata(vertices,[],[(i,i+1,i+2) for i in range(0,len(vertices),3)])
    mesh.update();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def point(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()

def area(name,location,energy,color,size,target):
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.color=color;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(ob);ob.location=location;point(ob,target)

def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    a=Assembly(ROOT/'cad'/'assembly.json'); mats={n:material(n) for n in PALETTE}
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene['assembly_manifest_sha256']=hashlib.sha256((ROOT/'cad'/'assembly.json').read_bytes()).hexdigest()
    scene['prototype_visualization']=True
    scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=6
    scene.render.resolution_x=1800;scene.render.resolution_y=1600;scene.render.resolution_percentage=50 if '--preview' in sys.argv else 100
    if '--preview' in sys.argv:scene.cycles.samples=12
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.world.color=(.19,.22,.24)
    scene.view_settings.view_transform='AgX'
    scene.use_nodes=True;tree=scene.node_tree;tree.nodes.clear()
    layers=tree.nodes.new('CompositorNodeRLayers')
    comp=tree.nodes.new('CompositorNodeComposite');tree.links.new(layers.outputs['Image'],comp.inputs['Image'])
    stage=bpy.data.materials.new('warm studio');stage.diffuse_color=(.74,.78,.76,1)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));plane=bpy.context.object;plane.data.materials.append(stage)
    area('Key',(-.5,-.5,.85),40,(1,.91,.80),.6,(0,.1,.16))
    area('Soft fill',(.55,-.20,.45),17,(.76,.87,1),.45,(0,.1,.16))
    area('Rim',(-.2,.5,.60),32,(.69,1,.91),.4,(0,.1,.20))
    cam=bpy.data.cameras.new('Camera');cob=bpy.data.objects.new('Camera',cam);bpy.context.collection.objects.link(cob);scene.camera=cob
    cam.type='ORTHO';cam.ortho_scale=.46
    output=ROOT/'media'/'renders';output.mkdir(exist_ok=True,parents=True)
    views=['hero'] if '--preview' in sys.argv or '--hero-only' in sys.argv else ['exploded'] if '--exploded-only' in sys.argv else ['hero','exploded']
    for view in views:
        plane.location.z=-.002 if view=='hero' else -.080
        items=[]
        for i,(tri,mat) in enumerate(a.triangles('hero',0,view=='exploded')):
            name=a.parts[i]['name'] if i<len(a.parts) else f'Display graphic {i-len(a.parts)+1}'
            items.append(mesh_object(name,tri,mats[mat]))
        target=(0,.065 if view=='hero' else .095,.190 if view=='hero' else .205)
        cob.location=(.53,.86,.43) if view=='hero' else (1.0,.65,.54);point(cob,target)
        cam.ortho_scale=.56 if view=='hero' else .65
        scene.render.filepath=str(output/f'{view}_cycles.png')
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'media'/'sources'/f'luma_{view}.blend'))
        bpy.ops.render.render(write_still=True)
        for ob in items:
            mesh=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(mesh)

if __name__=='__main__':main()
