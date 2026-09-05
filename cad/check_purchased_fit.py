"""Static fit smoke test of purchased conservative envelopes against printed parts."""
from pathlib import Path
import json
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'assembly.json').read_text())
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
report={'scope':'Static neutral conservative rectangular servo and LCD board envelopes only; excludes horns, screws, connectors, glass projection and moving cables. Zero result is not physical fit proof.','intersections':results}
(HERE/'purchased_fit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
