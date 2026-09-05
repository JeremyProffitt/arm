"""Consolidate source CSVs, preserving exact purchasing specifications."""
from pathlib import Path
import csv
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"deliverables"


def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))


def esc(s):return str(s).replace("|","/").replace("\n"," ")


def main():
    OUT.mkdir(exist_ok=True)
    purchased=read_csv(ROOT/"electronics/bom_electronics.csv")+read_csv(ROOT/"cad/bom_mechanical.csv")
    fields=["ref","quantity","manufacturer","model","description","critical_spec","verification","source","budget_usd_each"]
    with (OUT/"LUMA_Purchased_Parts.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");writer.writeheader();writer.writerows(purchased)
    total=sum(float(p.get("quantity",0))*float(p.get("budget_usd_each") or 0) for p in purchased)
    lines=["# Parts and purchasing","",f"Planning allowance for the purchased items below: **US ${total:,.2f}** before shipping and tax. Figures are budgeting allowances, not checked-out prices. Filament and any workshop tools are included only where explicitly listed. Reuse of existing supplies can change the total substantially.","",
      "Order the exact display and voltage variant specified. Generic fasteners, connector harnesses, relay contacts and wire must meet the listed dimensions and electrical ratings. Buy the servo horns and their screws with the servos; verify their actual thread and engagement before ordering extras.",""]
    for title,rows in (("Controller, sensing, lights and power",[p for p in purchased if p["ref"].startswith("E")]),
                       ("Mechanical hardware and consumables",[p for p in purchased if not p["ref"].startswith("E")])):
        lines.extend(["## "+title,"","| Ref / qty | Item | Required specification | Budget / each |","| --- | --- | --- | --- |"])
        for p in rows:
            name=" ".join(filter(None,[p.get("manufacturer"),p.get("model")])) or p["description"]
            link=f'[{esc(name)}]({p["source"]})' if p.get("source") else esc(name)
            spec=esc(p.get("critical_spec",""))
            if p.get("description") and p["description"] not in name:spec=esc(p["description"])+". "+spec
            lines.append(f'| {p["ref"]} / {p["quantity"]} | {link} | {spec} | ${float(p.get("budget_usd_each") or 0):.2f} |')
        lines.append("")
    manifest=json.loads((ROOT/"cad/part_manifest.json").read_text())
    lines.extend(["## Printable part schedule","",f'{len(manifest)} unique STL files; {sum(p["qty"] for p in manifest)} printed pieces including the fit coupon and optional cable clips. Quantities control the print run. The drawing index uses the same part order.',"",
                  "| Drawing / qty | STL identifier | Material / print orientation |","| --- | --- | --- |"])
    printrows=[]
    for i,p in enumerate(manifest,1):
        lines.append(f'| P{i:02d} / {p["qty"]} | `{p["id"]}` | {esc(p["material"])}; {esc(p["orientation"])} |')
        printrows.append({"drawing":f"P{i:02d}","quantity":p["qty"],"stl":p["file"],"name":p["name"],"material":p["material"],"orientation":p["orientation"],
                         "layer_mm":p["layer_mm"],"walls":p["walls"],"infill_percent":p["infill_percent"]})
    (ROOT/"docs/parts.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    with (OUT/"LUMA_Print_Schedule.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(printrows[0]));w.writeheader();w.writerows(printrows)
    wiring=read_csv(ROOT/"electronics/wiring.csv")
    lines=["# Point-to-point wiring schedule","","Use these connection names together with the electrical chapter. Physical Raspberry Pi header numbers and BCM GPIO numbers are explicitly distinguished. Disconnect the supplies while changing wiring.","",
           "| Net | From → to | Cable / connection detail |","| --- | --- | --- |"]
    for p in wiring:
        route=f'{p["from"]}: {p["from_pin"]} → {p["to"]}: {p["to_pin"]}'
        lines.append(f'| {esc(p["net"])} | {esc(route)} | {esc(p["wire_or_cable"])}. {esc(p["notes"])} |')
    (ROOT/"docs/wiring_schedule.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    (OUT/"bom_summary.json").write_text(json.dumps({"purchase_line_items":len(purchased),"budget_usd":round(total,2),
                     "unique_prints":len(manifest),"print_quantity":sum(p["qty"] for p in manifest)},indent=2),encoding="utf-8")
    print(f"BOM: {len(purchased)} purchase lines, ${total:,.2f}; {len(manifest)} printable types")


if __name__=="__main__":main()
