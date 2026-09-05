"""Static fit smoke test of purchased conservative envelopes against printed parts, both assemblies."""
from pathlib import Path
import json
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
report={'scope':'Static neutral conservative servo and LCD envelopes only (rectangular ST3215 boxes, the 55 mm board box, and the 4inch DSI LCD (C) case/PCB/connector envelope measured from the vendor STEP); excludes horns, screws, cables, glass projection and moving cables. Zero result is not physical fit proof.','assemblies':{}}
for key,file in (('standard','assembly.json'),('dsi_head','assembly_dsi.json')):
    data=json.loads((HERE/file).read_text())
    instances=[]
    for part in data['parts']:
        mesh=trimesh.load_mesh(HERE/part['file'])
        mesh.apply_transform(np.asarray(part['matrix']))
        instances.append((part,mesh))
    results=[]
    for p,a in instances:
        if 'visual_only' not in p['file']:continue
        for q,b in instances:
            if p is q or 'visual_only' in q['file']:continue
            if np.any(np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])<.03):continue
            try:
                overlap=trimesh.boolean.intersection([a,b],engine='manifold')
                if overlap.volume>.5:results.append({'purchased':p['name'],'printed':q['name'],'volume_mm3':round(float(overlap.volume),3)})
            except ValueError as error:results.append({'purchased':p['name'],'printed':q['name'],'error':str(error)})
    report['assemblies'][key]={'file':file,'intersections':results}
report['intersections']=[dict(assembly=k,**r) for k,v in report['assemblies'].items() for r in v['intersections']]
(HERE/'purchased_fit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
