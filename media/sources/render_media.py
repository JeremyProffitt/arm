"""LUMA deterministic CAD renderer and 1080p promotional film builder.

No generated concept imagery: every mechanical surface comes from the exported
assembly STLs. An orthographic OpenGL renderer makes the project reproducible
on integrated graphics; a basic CPU fallback is included. Units are millimetres.
"""
from __future__ import annotations
import argparse, json, math, os, struct, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'media' / '.tools' / 'python'))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

OUT = ROOT / 'media'
FONT = Path('C:/Windows/Fonts/bahnschrift.ttf')
FONT_LIGHT = Path('C:/Windows/Fonts/segoeuil.ttf')
TAU = math.tau

def font(size, light=False):
    p = FONT_LIGHT if light and FONT_LIGHT.exists() else FONT
    return ImageFont.truetype(str(p), size) if p.exists() else ImageFont.load_default(size=size)

def unit(v):
    v = np.asarray(v, dtype=float)
    return v / max(np.linalg.norm(v), 1e-12)

def rotation(axis, angle, pivot=(0,0,0)):
    x,y,z = unit(axis); a=math.radians(angle); c=math.cos(a); s=math.sin(a); C=1-c
    r=np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],
                [y*x*C+z*s,c+y*y*C,y*z*C-x*s],
                [z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
    m=np.eye(4); m[:3,:3]=r; p=np.asarray(pivot); m[:3,3]=p-r@p
    return m

def transform(tri, m):
    return tri @ np.asarray(m)[:3,:3].T + np.asarray(m)[:3,3]

def read_stl(path):
    raw=Path(path).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0] if len(raw)>=84 else 0
    if len(raw)==84+count*50:
        dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
        return np.frombuffer(raw, dtype=dtype, offset=84)['v'].astype(float)
    import re
    values=re.findall(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)', raw)
    return np.asarray(values,dtype=float).reshape(-1,3,3)

def cylinder(radius, depth, segments=96):
    t=np.arange(segments+1)*TAU/segments; x=np.cos(t)*radius; y=np.sin(t)*radius
    v=[]
    for i in range(segments):
        a=(x[i],y[i],0); b=(x[i+1],y[i+1],0)
        c=(x[i],y[i],depth); d=(x[i+1],y[i+1],depth)
        v += [[(0,0,depth),c,d],[(0,0,0),b,a],[a,b,d],[a,d,c]]
    return np.asarray(v,float)

def disc_patch(points, depth=0):
    pts=np.array([(x,y,depth) for x,y in points],float)
    center=pts.mean(axis=0)
    return np.array([[center,pts[i],pts[(i+1)%len(pts)]] for i in range(len(pts))])

def rounded_line(points, width, depth=0):
    tri=[]
    for (x1,y1),(x2,y2) in zip(points[:-1],points[1:]):
        dx=x2-x1; dy=y2-y1; r=math.hypot(dx,dy); ox=-dy/r*width/2; oy=dx/r*width/2
        tri.extend(disc_patch([(x1+ox,y1+oy),(x1-ox,y1-oy),(x2-ox,y2-oy),(x2+ox,y2+oy)],depth))
    for x,y in points:
        tri.extend(disc_patch([(x+math.cos(i*TAU/16)*width/2,y+math.sin(i*TAU/16)*width/2) for i in range(16)],depth))
    return np.asarray(tri)

def ellipse(cx,cy,rx,ry,depth=0):
    return disc_patch([(cx+math.cos(i*TAU/40)*rx,cy+math.sin(i*TAU/40)*ry) for i in range(40)],depth)

def smooth_pulse(t,start,end):
    if t<start or t>end: return 0.0
    return math.sin(math.pi*(t-start)/(end-start))**2

PALETTE={
 'shell':(218,220,211), 'dark':(37,46,52), 'metal':(124,141,150),
 'fastener':(109,125,133), 'diffuser':(203,250,240), 'rgb':(93,245,211),
 'white':(255,235,192), 'screen':(7,17,22), 'eye':(200,255,239),
 'pcb':(38,111,83), 'servo':(41,50,58), 'cable':(47,52,59),
}

def infer_material(name, supplied=''):
    if supplied in PALETTE and supplied!='diffuser':return supplied
    s=(supplied+' '+name).lower()
    if 'outer' in s and 'diffus' in s:return 'rgb'
    if 'inner' in s and 'diffus' in s:return 'white'
    if any(x in s for x in ('rgb','outer_diffus')):return 'rgb'
    if any(x in s for x in ('inner_diffus','white_diffus')):return 'white'
    if 'diffus' in s:return 'diffuser'
    if any(x in s for x in ('washer','screw','bearing','bolt','shaft','nut','axle')):return 'metal'
    if any(x in s for x in ('sensor','board','pcb','pi_')):return 'pcb'
    if any(x in s for x in ('screen','glass','lcd','display')):return 'screen'
    if 'servo' in s:return 'servo'
    if any(x in s for x in ('rubber','foot','dark','charcoal','gasket','cable')):return 'dark'
    return 'shell'

class Assembly:
    def __init__(self, manifest):
        self.manifest_path=Path(manifest)
        data=json.loads(self.manifest_path.read_text(encoding='utf-8-sig'))
        self.data=data; self.parts=[]
        for entry in data['parts']:
            p=entry.get('file',entry.get('stl',entry.get('path','')))
            path=Path(p)
            if not path.is_absolute():
                candidates=[self.manifest_path.parent/path, ROOT/path, ROOT/'cad'/path]
                path=next((p for p in candidates if p.exists()),candidates[0])
            tri=read_stl(path)
            if 'matrix' in entry:m=np.asarray(entry['matrix'],float).reshape(4,4)
            elif 'matrix_world' in entry:m=np.asarray(entry['matrix_world'],float).reshape(4,4)
            else:
                m=np.eye(4)
                for axis,angle in zip([(1,0,0),(0,1,0),(0,0,1)],entry.get('rotation_deg',[0,0,0])):
                    m=rotation(axis,angle)@m
                m[:3,3]=entry.get('translation_mm',entry.get('translation',[0,0,0]))
            self.parts.append({'name':entry.get('name',path.stem),'tri':transform(tri,m),
                               'material':infer_material(entry.get('name',path.stem),entry.get('material','')),
                               'group':entry.get('group','base'),'entry':entry})
        self.joints=data.get('joints',[])
        if isinstance(self.joints,dict):self.joints=[dict(v,name=k) for k,v in self.joints.items()]
        self.face=data.get('face',{'center_mm':[0,147,258],'normal':[0,-1,0],'up':[0,0,1],'radius_mm':22.84})
        self.groups=data.get('group_chains',{
            'base':[], 'yaw':['yaw'], 'shoulder':['yaw','shoulder'],
            'upper':['yaw','shoulder'],'upper_arm':['yaw','shoulder'],
            'elbow':['yaw','shoulder','elbow'], 'forearm':['yaw','shoulder','elbow'],
            'lower_arm':['yaw','shoulder','elbow'], 'wrist':['yaw','shoulder','elbow','wrist'],
            'head':['yaw','shoulder','elbow','wrist']})

    def pose(self,clip,t):
        fade=min(1,t/1.2)*min(1,(9-t)/1.2)
        if clip=='wink':
            p=smooth_pulse(t,1.4,3.2)+smooth_pulse(t,5.0,6.6)
            return {'yaw':-4*p,'shoulder':2*p,'elbow':-3*p,'wrist':-7*p},p
        if clip=='hi':
            p=smooth_pulse(t,1.6,2.7)+smooth_pulse(t,2.8,3.9)
            return {'yaw':4*math.sin(t*.9)*fade,'shoulder':2*p,'elbow':-3*p,'wrist':8*p},0
        if clip=='happy':
            w=math.sin(t*TAU/2.5)*fade
            return {'yaw':8*w,'shoulder':3*abs(w),'elbow':-4*abs(w),'wrist':-5*w},0
        return {},0

    def group_matrix(self,group,angles):
        m=np.eye(4)
        for name in self.groups.get(group, self.groups['head'] if 'head' in group else []):
            j=next((j for j in self.joints if j.get('name')==name),None)
            if j:
                axis=j.get('axis',j.get('axis_world',[0,0,1] if name=='yaw' else [1,0,0]))
                p=j.get('pivot_mm',j.get('pivot_world_mm',j.get('pivot',[0,0,0])))
                m=m@rotation(axis,angles.get(name,0),p)
        return m

    def face_matrix(self):
        f=self.face
        center=np.asarray(f.get('center_mm',f.get('center',[0,147,258])),float)
        normal=unit(f.get('normal',[0,-1,0])); up=unit(f.get('up',[0,0,1])); right=unit(np.cross(up,normal))
        # local +Z points out of the LCD, +Y points up.
        m=np.eye(4);m[:3,0]=right;m[:3,1]=up;m[:3,2]=normal;m[:3,3]=center
        return m

    def triangles(self,clip='hero',t=0,exploded=False):
        angles,wink=self.pose(clip,t); meshes=[]
        for i,p in enumerate(self.parts):
            tri=transform(p['tri'],self.group_matrix(p['group'],angles))
            if exploded:
                off=p['entry'].get('explode_mm',p['entry'].get('exploded_offset_mm'))
                if off is None:
                    g=p['group']; off={'base':[0,0,-25],'yaw':[0,0,12],'upper':[0,0,30],
                        'forearm':[0,20,55],'head':[0,-25,80]}.get(g,[0,0,0])
                tri=tri+np.asarray(off)
            meshes.append((tri,p['material']))
        if not exploded:
            disc=self.group_matrix('head',angles)@self.face_matrix()
            # The circle is the active display area; enclosure geometry comes from CAD.
            meshes.append((transform(cylinder(self.face.get('radius_mm',22.84),.5),disc),'screen'))
            # Face graphics are authored for the 45.68 mm screen and scale with the active radius.
            fm=disc@np.diag([self.face.get('radius_mm',22.84)/22.84]*2+[1,1])
            if clip=='happy':
                for x in [-8,8]:
                    pts=[(x+5*math.cos(a),3+5*math.sin(a)) for a in np.linspace(.1,math.pi-.1,20)]
                    meshes.append((transform(rounded_line(pts,2.7,.9),fm),'eye'))
                pts=[(8*math.cos(a),-3+7*math.sin(a)) for a in np.linspace(math.pi+.15,TAU-.15,24)]
                meshes.append((transform(rounded_line(pts,2.7,.9),fm),'eye'))
            else:
                blink=smooth_pulse(t,.65,.96)*.94 + smooth_pulse(t,7.05,7.34)*.94
                for i,x in enumerate([-8,8]):
                    h=max(.8,5.0*(1-blink)*(1-wink*.96 if i==1 else 1))
                    meshes.append((transform(ellipse(x,4,3.2,h,.9),fm),'eye'))
                pts=[(6*math.cos(a),-3+4.4*math.sin(a)) for a in np.linspace(math.pi+.2,TAU-.2,22)]
                if clip=='hi' and 1.8<t<2.6:
                    meshes.append((transform(ellipse(0,-7,3.3,4.0,.9),fm),'eye'))
                else:meshes.append((transform(rounded_line(pts,1.7,.9),fm),'eye'))
        return meshes

class Renderer:
    def __init__(self,width=1920,height=1080,light=False,view='hero',product_only=False,forward_sign=1):
        self.w=width;self.h=height;self.light=light;self.view=view
        look={'hero':([530,forward_sign*860,430],[0,65,190]),'front':([0,forward_sign*1000,205],[0,65,205]),
              'side':([1000,65,205],[0,65,205]),'top':([0,65,1200],[0,65,190]),
              'exploded':([1000,forward_sign*650,540],[0,95,205])}
        eye,target=look.get(view,look['hero']); self.target=np.asarray(target,float)
        self.forward=unit(np.array(target)-eye)
        up=unit([0,1,0] if view=='top' else [0,0,1])
        self.right=unit(np.cross(self.forward,up));self.up=np.cross(self.right,self.forward)
        self.basis=np.array([self.right,self.up,self.forward])
        self.scale=min(width/540,height/505) if product_only else height/535
        if view=='exploded':self.scale*=.86
        self.center=np.array([width*.5 if product_only else width*.685,height*(.51 if product_only else .49)])
        self.lightdirs=[unit([-1,2,4]),unit([2,1,2]),unit([-2,-2,1])]

    def project(self,tri):
        v=(tri-self.target)@self.basis.T
        v[...,:2]*=[self.scale,-self.scale]
        v[...,:2]+=self.center
        return v

    def background(self):
        yy,xx=np.mgrid[0:self.h,0:self.w]
        if self.light:
            base=np.ones((self.h,self.w,3))*[243,244,240]
            v=(yy/self.h)[...,None]*np.array([7,7,6])
            return Image.fromarray(np.uint8(np.clip(base-v,0,255))).convert('RGB')
        a=np.exp(-(((xx-self.w*.70)/(self.w*.44))**2+((yy-self.h*.43)/(self.h*.70))**2))
        bg=np.array([11,22,30])+a[...,None]*np.array([19,23,22])
        return Image.fromarray(np.uint8(bg)).convert('RGB')

    def render(self,meshes):
        img=self.background()
        # Project the actual silhouette to a ground plane, then blur it for a broad studio key.
        shadow=Image.new('L',(self.w//3,self.h//3));sd=ImageDraw.Draw(shadow)
        alltri=[];materials=[]
        for tri,mat in meshes:
            if len(tri)==0:continue
            alltri.append(tri);materials.extend([mat]*len(tri))
        tri=np.concatenate(alltri);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-9)
        for part,mat in meshes:
            if mat in ('eye','rgb','white','diffuser'):continue
            s=part[::max(1,len(part)//1500)].copy()
            s[:,:,0]-=s[:,:,2]*.16;s[:,:,1]+=s[:,:,2]*.10;s[:,:,2]=0
            xy=self.project(s)[:,:,:2]/3
            for poly in xy:sd.polygon([tuple(p) for p in poly],fill=170)
        shadow=shadow.filter(ImageFilter.GaussianBlur(11)).resize(img.size,Image.Resampling.BILINEAR)
        img.paste((172,180,177) if self.light else (0,4,9),(0,0,self.w,self.h),shadow)
        p=self.project(tri)
        visible=(norm@(-self.forward)>.00001)
        visible &= (p[:,:,0].max(axis=1)>0)&(p[:,:,0].min(axis=1)<self.w)&(p[:,:,1].max(axis=1)>0)&(p[:,:,1].min(axis=1)<self.h)
        ids=np.where(visible)[0];ids=ids[np.argsort(p[ids,:,2].mean(axis=1))[::-1]]
        bases=np.array([PALETTE[m] for m in materials],float)
        lighting=.43 + .52*np.clip(norm@self.lightdirs[0],0,1) + .13*np.clip(norm@self.lightdirs[1],0,1)
        lighting += .11*np.clip(norm@self.lightdirs[2],0,1)
        # Broad cool specular highlights, restrained enough to retain printable surfaces.
        half=unit(self.lightdirs[0]-self.forward)
        spec=(np.maximum(0,norm@half)**34)*16
        cols=np.clip(bases*lighting[:,None]+spec[:,None],0,255).astype(np.uint8)
        draw=ImageDraw.Draw(img)
        glow=Image.new('RGB',img.size,(0,0,0));gd=ImageDraw.Draw(glow)
        isglow=np.array([m in ('rgb','white','diffuser','eye') for m in materials])
        # Opaque surfaces also clear occluded emission from the glow matte.
        for i in ids:
            xy=[tuple(x) for x in p[i,:,:2]]
            if isglow[i]:
                c=tuple(int(x) for x in bases[i]);draw.polygon(xy,fill=c);gd.polygon(xy,fill=c)
            else:
                draw.polygon(xy,fill=tuple(int(x) for x in cols[i]));gd.polygon(xy,fill=(0,0,0))
        if not self.light:
            g=np.asarray(glow.filter(ImageFilter.GaussianBlur(12)),float)*.21
            g+=np.asarray(glow.filter(ImageFilter.GaussianBlur(35)),float)*.13
            img=Image.fromarray(np.uint8(np.clip(np.asarray(img,dtype=float)+g,0,255)))
        return img

class GLRenderer(Renderer):
    """GPU depth-buffered renderer with 4x edge antialiasing.

    Unlike painter ordering, the depth buffer correctly resolves a recessed
    display, bores, and thin overlapping manufactured components.
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        import moderngl
        self.gl=moderngl;self.ctx=moderngl.create_standalone_context(require=330)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.depth_func='<='
        self.program=self.ctx.program(vertex_shader='''#version 330
            in vec3 in_pos; in vec3 in_normal; in vec3 in_color; in float in_emit;
            uniform vec3 cam_right, cam_up, cam_forward, cam_target;
            uniform vec2 viewport, image_center; uniform float pixel_scale;
            out vec3 normal; out vec3 color; out float emissive;
            void main() {
                vec3 p=in_pos-cam_target;
                float x=dot(p,cam_right)*pixel_scale+image_center.x;
                float y=-dot(p,cam_up)*pixel_scale+image_center.y;
                gl_Position=vec4(2.0*x/viewport.x-1.0,1.0-2.0*y/viewport.y,dot(p,cam_forward)/1500.0,1.0);
                normal=in_normal;color=in_color;emissive=in_emit;
            }
            ''',fragment_shader='''#version 330
            in vec3 normal; in vec3 color; in float emissive;
            uniform vec3 view_direction; out vec4 fragColor;
            void main() {
                vec3 n=normalize(normal);
                vec3 key=normalize(vec3(-1.0,2.0,4.0));
                vec3 fill=normalize(vec3(2.0,1.0,2.0));
                vec3 rim=normalize(vec3(-2.0,-2.0,1.0));
                float light=0.40+0.54*max(0.0,dot(n,key))+0.12*max(0.0,dot(n,fill))+0.11*max(0.0,dot(n,rim));
                vec3 halfdir=normalize(key+view_direction);
                float spec=pow(max(0.0,dot(n,halfdir)),40.0)*0.065;
                vec3 result=emissive>0.5 ? color : color*light+spec;
                fragColor=vec4(result,1.0);
            }
            ''')
        for k,v in [('cam_right',self.right),('cam_up',self.up),('cam_forward',self.forward),
                    ('cam_target',self.target),('viewport',(self.w,self.h)),('image_center',self.center),
                    ('view_direction',-self.forward)]:self.program[k].value=tuple(v)
        self.program['pixel_scale'].value=self.scale
        self.fbo=self.ctx.framebuffer(color_attachments=[self.ctx.renderbuffer((self.w,self.h),components=4,samples=4)],
                                      depth_attachment=self.ctx.depth_renderbuffer((self.w,self.h),samples=4))
        self.resolve=self.ctx.simple_framebuffer((self.w,self.h),components=4)
        self._stage=None

    def stage(self,meshes):
        if self._stage is not None:return self._stage.copy()
        img=self.background();shadow=Image.new('L',(self.w//3,self.h//3));sd=ImageDraw.Draw(shadow)
        for part,mat in meshes:
            if mat in ('eye','rgb','white','diffuser') or len(part)==0:continue
            s=part[::max(1,len(part)//1000)].copy()
            s[:,:,0]-=s[:,:,2]*.16;s[:,:,1]-=s[:,:,2]*.10;s[:,:,2]=0
            xy=self.project(s)[:,:,:2]/3
            for poly in xy:sd.polygon([tuple(p) for p in poly],fill=140)
        shadow=shadow.filter(ImageFilter.GaussianBlur(12)).resize(img.size,Image.Resampling.BILINEAR)
        img.paste((166,176,171) if self.light else (0,4,9),(0,0,self.w,self.h),shadow)
        self._stage=img.copy();return img

    def render(self,meshes):
        packed=[]
        for tri,mat in meshes:
            if len(tri)==0:continue
            norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
            norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-9)
            data=np.empty((len(tri),3,10),np.float32)
            data[:,:,:3]=tri;data[:,:,3:6]=norm[:,None,:]
            data[:,:,6:9]=np.asarray(PALETTE[mat])/255
            data[:,:,9]=float(mat in ('rgb','white','diffuser','eye'))
            packed.append(data.reshape(-1,10))
        vertices=np.concatenate(packed)
        buffer=self.ctx.buffer(vertices.tobytes())
        vao=self.ctx.vertex_array(self.program,[(buffer,'3f 3f 3f 1f','in_pos','in_normal','in_color','in_emit')])
        self.fbo.use();self.fbo.clear(0,0,0,0,depth=1.0);vao.render()
        self.ctx.copy_framebuffer(self.resolve,self.fbo)
        raw=self.resolve.read(components=4,alignment=1)
        object_image=Image.frombytes('RGBA',(self.w,self.h),raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img=Image.alpha_composite(self.stage(meshes).convert('RGBA'),object_image).convert('RGB')
        if not self.light:
            red,green,blue,alpha=object_image.split()
            bright=green.point(lambda x:255 if x>210 else 0,mode='1')
            teal=ImageChops.logical_and(bright,ImageChops.subtract(green,red).point(lambda x:255 if x>25 else 0,mode='1'))
            warm=ImageChops.logical_and(red.point(lambda x:255 if x>245 else 0,mode='1'),bright)
            warm=ImageChops.logical_and(warm,blue.point(lambda x:255 if x<215 else 0,mode='1'))
            mask=ImageChops.logical_or(teal,warm).convert('L')
            emission=Image.new('RGB',img.size);emission.paste(object_image.convert('RGB'),mask=mask)
            glow=emission.resize((self.w//4,self.h//4),Image.Resampling.BILINEAR)
            near=glow.filter(ImageFilter.GaussianBlur(3)).resize(img.size,Image.Resampling.BILINEAR).point(lambda x:int(x*.16))
            far=glow.filter(ImageFilter.GaussianBlur(9)).resize(img.size,Image.Resampling.BILINEAR).point(lambda x:int(x*.10))
            img=ImageChops.add(ImageChops.add(img,near),far)
        vao.release();buffer.release()
        return img

def make_renderer(*args,**kwargs):
    try:return GLRenderer(*args,**kwargs)
    except (ImportError,RuntimeError,ValueError) as exc:
        print('GPU renderer unavailable; using software:',exc,flush=True)
        return Renderer(*args,**kwargs)

def text_width(text,f):return f.getlength(text)

def promo_layout(img,clip,t):
    # A small orthographic camera push brings the expression forward, preserving
    # the complete product and keeping the subsequently typeset titles stable.
    push=1+.045*smooth_pulse(t,1.1,5.4)
    if push>1.0001:
        iw,ih=img.size;cx,cy=iw*.685,ih*.51
        enlarged=img.resize((round(iw*push),round(ih*push)),Image.Resampling.BICUBIC)
        x=round(cx*(push-1));y=round(cy*(push-1))
        img=enlarged.crop((x,y,x+iw,y+ih))
    d=ImageDraw.Draw(img);w,h=img.size;f=lambda s:font(round(s*w/1920))
    left=112*w/1920
    d.rounded_rectangle((left,86,left+310,123),radius=18,fill=(39,63,67))
    d.text((left+19,93),'A DESK COMPANION',font=f(18),fill=(159,216,207))
    d.text((left,162),'LUMA',font=f(52),fill=(222,237,229),stroke_width=0)
    titles={'wink':['A little light.','A little wink.'],'hi':['Say hello','to LUMA.'],'happy':['Made to','brighten your day.']}
    for i,line in enumerate(titles[clip]):
        fs=70 if clip!='happy' else 66
        d.text((left,285+i*88),line,font=f(fs),fill=(237,239,226))
    sub={'wink':['A familiar face.','An unexpected spark.'],'hi':['A glance. A nod. A friendly “Hi!”','Your workspace, with personality.'],
         'happy':['Expressive by design.','Happy to be here.']}[clip]
    for i,line in enumerate(sub):d.text((left,514+i*37),line,font=f(25),fill=(144,172,175))
    # A quiet expression cue is synchronized with the motion.
    label={'wink':'01 / WINK','hi':'02 / HELLO','happy':'03 / HAPPY'}[clip]
    d.line((left,646,left+67,646),fill=(96,226,196),width=3)
    d.text((left,668),label,font=f(18),fill=(130,203,190))
    if clip=='hi' and 1.65<t<4.8:
        # Promotional speech bubble; face display itself remains correctly sized.
        a=max(0,min(1,(t-1.65)/.25,(4.8-t)/.25));bubble=Image.new('RGBA',img.size)
        bd=ImageDraw.Draw(bubble);x=1490;y=176
        bd.rounded_rectangle((x,y,x+184,y+105),radius=34,fill=(190,245,226,round(255*a)))
        bd.polygon([(x+30,y+96),(x+4,y+131),(x+68,y+99)],fill=(190,245,226,round(255*a)))
        bd.text((x+41,y+13),'Hi!',font=f(55),fill=(17,56,55,round(255*a)))
        img=Image.alpha_composite(img.convert('RGBA'),bubble).convert('RGB');d=ImageDraw.Draw(img)
    d.line((left,952,w-112,952),fill=(56,76,80),width=1)
    d.text((left,979),'RASPBERRY PI 4  /  5× TIME-OF-FLIGHT  /  PRINTABLE ENCLOSURES',font=f(17),fill=(133,157,159))
    end='PROTOTYPE ANIMATION'
    d.text((w-112-text_width(end,f(16)),981),end,font=f(16),fill=(109,137,140))
    # Exposure ease makes the film loop softly without hiding the product.
    return img

def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def make_audio(clip,duration=9,sr=48000):
    t=np.arange(int(duration*sr))/sr
    a=np.zeros_like(t)
    # Original synthesized sound design: warm sine plucks and a soft final sparkle.
    notes={'wink':[(.8,659,.10),(1.9,988,.13),(5.4,784,.11),(7.25,1318,.08)],
           'hi':[(.8,523,.10),(1.05,659,.09),(3.5,784,.08),(7.3,1047,.09)],
           'happy':[(.7,523,.09),(1.05,659,.10),(1.4,784,.11),(2.1,1047,.09),(3.1,784,.09),(4.2,659,.08),(5.4,1047,.1),(7.25,1318,.08)]}
    for start,hz,vol in notes[clip]:
        tt=np.maximum(0,t-start);env=(1-np.exp(-tt*90))*np.exp(-tt*4.5)*(t>=start)
        a+=vol*env*(np.sin(TAU*hz*tt)+.18*np.sin(TAU*hz*2*tt))
    if clip=='hi':
        source=OUT/'audio'/'hi.wav'
        with wave.open(str(source),'rb') as wav:
            channels=wav.getnchannels();rate=wav.getframerate();width=wav.getsampwidth()
            raw=wav.readframes(wav.getnframes())
        if width!=2:raise ValueError('Expected 16-bit synthesized speech')
        speech=np.frombuffer(raw,dtype='<i2').astype(float)/32768
        if channels>1:speech=speech.reshape(-1,channels).mean(axis=1)
        speech=np.interp(np.arange(round(len(speech)*sr/rate))*rate/sr,np.arange(len(speech)),speech)
        # Cut the Windows voice's leading silence while preserving a short natural onset.
        active=np.flatnonzero(np.abs(speech)>.008)
        if len(active):
            speech=speech[max(0,int(active[0]-.025*sr)):min(len(speech),int(active[-1]+.12*sr))]
        start=int(1.93*sr);a[start:start+len(speech)]+=speech[:len(a)-start]*1.5
    fade=np.minimum(1,t/.07)*np.minimum(1,(duration-t)/.3)
    a=np.clip(a*fade,-.94,.94)
    stereo=np.stack([a*.99,a],axis=1)
    path=OUT/'audio'/f'{clip}_mix.wav'
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(sr);wav.writeframes((stereo*32767).astype('<i2').tobytes())
    return path

def build_video(assembly,clip,fps=24,duration=9):
    names={'wink':'01_wink.mp4','hi':'02_hi.mp4','happy':'03_happy.mp4'}
    path=OUT/'videos'/names[clip];path.parent.mkdir(parents=True,exist_ok=True)
    audio=make_audio(clip,duration)
    cmd=[ffmpeg_exe(),'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1920x1080',
         '-r',str(fps),'-i','-','-i',str(audio),'-filter:v','fps=24','-c:v','libx264','-preset','fast',
         '-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(duration),str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    renderer=make_renderer()
    samples={int(fps*x) for x in [0,2.25,5.5,7.5]}
    for n in range(round(duration*fps)):
        t=n/fps;img=promo_layout(renderer.render(assembly.triangles(clip,t)),clip,t)
        proc.stdin.write(img.tobytes())
        if n in samples:img.save(OUT/'renders'/f'{clip}_{n:03d}.jpg',quality=94)
        if n%fps==0:print(f'{clip}: {n//fps}/{duration} seconds',flush=True)
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
    return path

def stills(assembly,views=None,suffix=''):
    paths=[]
    variant=assembly.data.get('variant','standard')
    tag='LUMA / OPTIONAL 4-INCH DSI HEAD' if variant!='standard' else 'LUMA'
    for view in views or ['hero','exploded','front','side','top']:
        size=(1800,1600) if view in ('hero','exploded') else (1500,1300)
        r=make_renderer(*size,light=True,view=view,product_only=True)
        img=r.render(assembly.triangles('hero',0,view=='exploded'))
        d=ImageDraw.Draw(img)
        labels={'hero':tag+' / FINISHED ASSEMBLY','exploded':tag+' / EXPLODED ASSEMBLY','front':'FRONT VIEW','side':'RIGHT VIEW','top':'TOP VIEW'}
        d.text((62,48),labels[view],font=font(25),fill=(62,86,91))
        d.text((62,size[1]-57),'CAD-BASED PROTOTYPE VISUALIZATION · DIMENSIONS IN THE BUILD MANUAL',font=font(17),fill=(101,122,125))
        path=OUT/'renders'/f'{view}{suffix}.png';img.save(path);paths.append(str(path))
        print('Saved',path,flush=True)
    return paths

def contact_sheet():
    rows=[]
    for clip in ['wink','hi','happy']:
        files=sorted((OUT/'renders').glob(f'{clip}_*.jpg'))
        files=files[:3]
        if len(files)!=3:continue
        rows.append([Image.open(f).resize((640,360),Image.Resampling.LANCZOS) for f in files])
    result=Image.new('RGB',(1920,360*len(rows)),(15,25,30))
    for y,row in enumerate(rows):
        for x,img in enumerate(row):result.paste(img,(x*640,y*360))
    if rows:result.save(OUT/'renders'/'promotional_contact_sheet.jpg',quality=95)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',default=str(ROOT/'cad'/'assembly.json'))
    ap.add_argument('--stills',action='store_true');ap.add_argument('--clip',choices=['wink','hi','happy','all'])
    ap.add_argument('--fps',type=int,default=24);ap.add_argument('--contact',action='store_true')
    ap.add_argument('--suffix',default='',help='appended to still file names, e.g. _dsi for the optional head assembly')
    ap.add_argument('--views',nargs='*',help='subset of hero exploded front side top')
    a=ap.parse_args();(OUT/'renders').mkdir(parents=True,exist_ok=True)
    if a.contact:contact_sheet();return
    assembly=Assembly(a.manifest)
    if a.stills:stills(assembly,a.views or None,a.suffix)
    if a.clip:
        for clip in ['wink','hi','happy'] if a.clip=='all' else [a.clip]:build_video(assembly,clip,a.fps)
        contact_sheet()

if __name__=='__main__':main()
