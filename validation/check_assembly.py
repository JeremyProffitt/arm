"""Read-only mesh/interference diagnostics. Does not modify CAD or its manifest."""
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/"cad"


def body_count(mesh):
    parents=list(range(len(mesh.faces)))
    def find(n):
        while parents[n]!=n:
            parents[n]=parents[parents[n]]
            n=parents[n]
        return n
    for a,b in mesh.face_adjacency:
        a,b=find(int(a)),find(int(b))
        if a!=b:parents[b]=a
    return len({find(i) for i in range(len(parents))})


def main():
    assembly=json.loads((CAD/"assembly.json").read_text())
    manifest=json.loads((CAD/"part_manifest.json").read_text())
    stats=[]
    for p in manifest:
        m=trimesh.load_mesh(CAD/p["file"],process=True)
        ext=np.asarray(m.extents)
        stats.append({"id":p["id"],"quantity":p["qty"],"watertight":bool(m.is_watertight),
                      "positive_volume":bool(m.volume>0),"volume_cm3":round(m.volume/1000,3),
                      "connected_bodies":body_count(m),
                      "size_mm":np.round(ext,3).tolist(),"triangles":len(m.faces),
                      "fits_220_bed_xy":bool(max(ext[:2])<=220)})
    instances=[]
    for p in assembly["parts"]:
        if "visual_only" in p["file"]:continue
        m=trimesh.load_mesh(CAD/p["file"],process=True)
        m.apply_transform(np.asarray(p["matrix"],float))
        instances.append((p["name"],m))
    intersections=[]
    for i,(name,a) in enumerate(instances):
        for nameb,b in instances[i+1:]:
            overlap=np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])
            if np.any(overlap<=0.03):continue
            try:
                result=trimesh.boolean.intersection([a,b],engine="manifold")
                volume=float(result.volume) if result is not None else 0
                if volume>0.5:
                    item={"a":name,"b":nameb,"intersection_mm3":round(volume,2)}
                    intersections.append(item);print(item,flush=True)
            except Exception as e:
                intersections.append({"a":name,"b":nameb,"error":str(e)})
    result={"scope":"Static indexed-neutral printed-part intersections only. Not a dynamic collision, fastener, cable or physical-fit certification.",
            "parts":stats,"printed_instances":len(instances),"intersections":intersections}
    output=ROOT/"validation/assembly_check.json"
    output.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(f"Checked {len(stats)} printable types and {len(instances)} assembled printed instances; {len(intersections)} overlaps above0.5mm3")


if __name__=="__main__":main()
