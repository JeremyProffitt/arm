"""Decode every completed film and record useful delivery facts."""
import hashlib, json, subprocess, sys, re
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'media'/'.tools'/'python'))
import imageio_ffmpeg

def main():
    reports=[];ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for p in sorted((ROOT/'media'/'videos').glob('*.mp4')):
        decoded=subprocess.run([ffmpeg,'-hide_banner','-i',str(p),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
        video=re.search(r'Video: h264[^\n]*?(\d{3,5})x(\d{3,5})[^\n]*?([\d.]+) fps',decoded.stderr)
        duration=re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)',decoded.stderr)
        duration_s=sum(float(v)*factor for v,factor in zip(duration.groups(),[3600,60,1])) if duration else None
        frames=re.findall(r'frame=\s*(\d+)',decoded.stderr)
        properties={'width':int(video[1]) if video else None,'height':int(video[2]) if video else None,
                    'fps':float(video[3]) if video else None,'duration_seconds':duration_s,
                    'decoded_video_frames':int(frames[-1]) if frames else None,
                    'aac_audio':bool(re.search(r'Audio: aac',decoded.stderr))}
        reports.append({'file':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        **properties,
                        'full_audio_video_decode_passed':decoded.returncode==0,
                        'ffmpeg_report':decoded.stderr})
        if decoded.returncode:raise RuntimeError(decoded.stderr)
        if properties!={'width':1920,'height':1080,'fps':24.0,'duration_seconds':9.0,'decoded_video_frames':216,'aac_audio':True}:
            raise RuntimeError(f'Unexpected movie properties: {properties}')
    if len(reports)!=3:raise RuntimeError('Expected exactly three completed films')
    stills=[]
    for p in sorted((ROOT/'media'/'renders').glob('*.png')):
        with Image.open(p) as im:stills.append({'file':str(p.relative_to(ROOT)).replace('\\','/'),'size':list(im.size)})
    out={'prototype_animation':True,'design_geometry':'cad/assembly.json and referenced STL files',
         'spoken_greeting':'Windows Microsoft Zira Desktop: Hi!',
         'sound_design':'Original synthesized tones; no external music','films':reports,'stills':stills}
    path=ROOT/'media'/'validation.json';path.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({'films':len(reports),'all_decoded':all(x['full_audio_video_decode_passed'] for x in reports),'stills':len(stills),'report':str(path)},indent=2))

if __name__=='__main__':main()
