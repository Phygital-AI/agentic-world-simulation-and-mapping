#!/usr/bin/env python3
"""Validate structure, provenance, links, hashes, and publication wording."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/"world_lobby_four_trajectory_20260929"
METHODS=["M1","M2","M3","M4"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class Doc(HTMLParser):
    def __init__(self,path):
        super().__init__(); self.path=path; self.ids=set(); self.links=[]; self.images=[]; self.models=[]; self.meta=[]; self.canon=[]
        self.feed(path.read_text(encoding="utf-8"))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:
            assert a["id"] not in self.ids, f"duplicate id {a['id']} in {self.path.name}"
            self.ids.add(a["id"])
        for key in ("href","src"):
            if key in a: self.links.append(a[key])
        if tag=="img": self.images.append(a.get("src"))
        if tag=="model-viewer": self.models.append(a.get("src"))
        if tag=="meta" and (a.get("property","").startswith("og:")): self.meta.append(a.get("property"))
        if tag=="link" and a.get("rel")=="canonical": self.canon.append(a.get("href"))

tables=json.loads((ROOT/"data/tables_1_5.json").read_text())
assert list(tables["tables"])==[f"table{i}" for i in range(1,6)], "must have exactly Table 1–5"
for key,rows in tables["tables"].items():
    assert len(rows)==4 and [r["method"] for r in rows]==METHODS, f"{key} must be M1–M4"
assert "five manual camera associations" in tables["m1_notice"]
assert all(k in tables["protocols"] for k in ("table2","table3","table4","table5"))

docs={name:Doc(ROOT/name) for name in ("index.html","en.html")}
required_ids={"question","pose-depth","editable","geometry","appearance","novel-depth","limitations",
              *{f"table-{i}" for i in range(1,6)},*{f"figure-{i}" for i in range(1,4)}}
for name,doc in docs.items():
    assert required_ids <= doc.ids, f"missing anchors in {name}: {required_ids-doc.ids}"
    assert len(doc.models)==4 and doc.models==[f"models/M{i}/scene.glb" for i in range(1,5)]
    assert len(doc.canon)==1 and doc.canon[0].startswith("https://")
    assert {"og:title","og:description","og:image","og:url"} <= set(doc.meta)
    assert ("en.html" if name=="index.html" else "index.html") in doc.links
    for link in doc.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        target=(ROOT/unquote(u.path)).resolve() if u.path else ROOT/name
        assert target.is_relative_to(ROOT) and target.exists(), f"broken local link {link}"
        if u.fragment and target.suffix==".html":
            target_doc=docs.get(target.name) or Doc(target)
            assert unquote(u.fragment) in target_doc.ids, f"broken anchor {link}"

contract=json.loads((ROOT/"data/source_contract.json").read_text())
assert contract["old_site_baseline"]=="ae69dbe"
src_table=SOURCE/contract["table_source"]["path"]
assert sha(src_table)==contract["table_source"]["sha256"]==sha(ROOT/"data/tables_1_5.json")
for published,item in contract["figures"].items():
    assert sha(ROOT/published)==item["sha256"]==sha(SOURCE/item["source"]), published
for method,files in contract["models"].items():
    for ext,item in files.items():
        assert sha(ROOT/item["published"])==item["sha256"]==sha(SOURCE/item["source"])
assert len(list((ROOT/"models").glob("M*/scene.glb")))==4
assert len(list((ROOT/"models").glob("M*/scene.blend")))==4

manifest=json.loads((ROOT/"evidence/publication_manifest.json").read_text())
for row in manifest["files"]: assert sha(ROOT/row["path"])==row["sha256"], row["path"]
for line in (ROOT/"evidence/SHA256SUMS").read_text().splitlines():
    expected,rel=line.split("  ",1); assert sha(ROOT/rel)==expected, rel

all_text="\n".join(p.read_text(errors="ignore") for p in ROOT.rglob("*")
    if p.is_file() and ".git" not in p.parts and "scripts" not in p.parts and p.suffix in (".html",".json",".js",".css",".md"))
for forbidden in ("模型未完成","model is unfinished","Models are not yet published","scene_blend_present"):
    assert forbidden.lower() not in all_text.lower(), f"old-site residue: {forbidden}"
assert "rev4 尚无完整独立视觉复审" in (ROOT/"index.html").read_text()
assert "5 个手工相机关联" in (ROOT/"index.html").read_text()
assert "Native depth AbsRel" in (ROOT/"en.html").read_text()
assert len(re.findall(r'data-table-key="table[1-5]"',(ROOT/"index.html").read_text()))==5
print(json.dumps({"status":"PASS","tables":5,"methods_per_table":4,"pages":2,
                  "checks":["links/anchors","OG/canonical","source identity","SHA256","old-copy scan"]},ensure_ascii=False))
