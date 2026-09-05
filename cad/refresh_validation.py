"""Re-measure existing exports without running OpenSCAD again."""
from pathlib import Path
import json
import trimesh
HERE=Path(__file__).resolve().parent
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
manifest=json.loads((HERE/'part_manifest.json').read_text())
results=[]
for row in manifest:
    mesh=trimesh.load_mesh(HERE/row['file'])
    result=dict(id=row['id'],watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),positive_volume=bool(mesh.volume>0),bodies=body_count(mesh),bounds_mm=mesh.bounds.tolist(),size_mm=mesh.extents.tolist(),volume_cm3=round(float(mesh.volume)/1000,3),triangles=len(mesh.faces),fits_220_bed=bool(max(mesh.extents[:2])<=220))
    results.append(result)
    row['size_mm']=result['size_mm'];row['volume_cm3']=result['volume_cm3']
(HERE/'part_manifest.json').write_text(json.dumps(manifest,indent=2))
(HERE/'validation.json').write_text(json.dumps(results,indent=2))
failures=[r for r in results if not all((r['watertight'],r['winding_consistent'],r['positive_volume'],r['bodies']==1,r['fits_220_bed']))]
print(f'{len(results)} printable types; {sum(p["qty"] for p in manifest)} physical printed pieces; failures={failures}')
raise SystemExit(bool(failures))
