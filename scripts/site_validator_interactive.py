#!/usr/bin/env python3
"""Validate interactive publication structure, provenance, and hashes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/"world_lobby_four_trajectory_20260929"
METHODS=("M1","M2","M3","M4"); FRAMES=(0,36,72,108,144)
GT_SHA="6c28ab067c63c5b1fce19c6a972f3d66c7ac4d9bd9ce3b5a57e2e18f5641fe8f"
GT_BYTES=24816108
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(a,b): return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

class Doc(HTMLParser):
    def __init__(self,path):
        super().__init__(); self.path=path; self.ids=set(); self.links=[]; self.tags=[]; self.meta=[]; self.canon=[]
        self.feed(path.read_text(encoding="utf-8"))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags.append(tag)
        if "id" in a:
            assert a["id"] not in self.ids, f"duplicate id {a['id']}"; self.ids.add(a["id"])
        for key in ("href","src"):
            if key in a: self.links.append(a[key])
        if tag=="meta" and a.get("property","").startswith("og:"): self.meta.append(a["property"])
        if tag=="link" and a.get("rel")=="canonical": self.canon.append(a.get("href"))

tables=json.loads((ROOT/"data/tables_1_7.json").read_text())
assert list(tables["tables"])==[f"table{i}" for i in range(1,8)]
for key,rows in tables["tables"].items(): assert [r["method"] for r in rows]==list(METHODS),key
m4_table2=next(row for row in tables["tables"]["table2"] if row["method"]=="M4")
assert m4_table2["ate_m"]=="-" and m4_table2["rotation_deg"]=="-"
docs={name:Doc(ROOT/name) for name in ("index.html","en.html")}
required={"introduction","motivation","method","results","interactive","discussion","limitations","office-cafe",
          "model-select","scene-mode","scene-reset","scene-split","scene-retry","compare-method","compare-frame",
          *{f"table-{i}" for i in range(1,8)},*{f"figure-{i}" for i in range(1,7)}}
for name,doc in docs.items():
    assert required<=doc.ids,f"{name}: missing {required-doc.ids}"
    assert "model-viewer" not in doc.tags and "model-viewer" not in (ROOT/name).read_text().lower()
    assert len(doc.canon)==1 and doc.canon[0].startswith("https://")
    assert {"og:title","og:description","og:image","og:url"}<=set(doc.meta)
    for link in doc.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        target=(ROOT/unquote(u.path)).resolve() if u.path else ROOT/name
        assert target.is_relative_to(ROOT) and target.exists(),f"broken link {name}: {link}"
        if u.fragment and target.suffix==".html":
            target_doc=docs.get(target.name) or Doc(target)
            assert unquote(u.fragment) in target_doc.ids,f"broken anchor {link}"
    html=(ROOT/name).read_text()
    assert all(f"Figure {i}." in html for i in range(1,7))
    assert html.index('id="table-2"') < html.index('id="figure-2"')
    assert html.index('id="figure-4"') < html.index('id="figure-5"')
    assert 'assets/fixed_views/GT/000.png' in html and 'assets/fixed_views/M1/000.png' in html
    assert 'src="https://office-cafe-vipe.hiwtishere.chatgpt.site/"' in html
    assert 'href="https://office-cafe-vipe.hiwtishere.chatgpt.site/shake.html"' in html
    assert 'type="importmap"' in html and 'scene-compare.js' in html
    assert 'name="twitter:card" content="summary_large_image"' in html
    assert 'name="twitter:image" content="https://wentingw.github.io/agentic-world-blog/assets/teaser_originals.png"' in html

assert not (ROOT/"vendor/model-viewer-4.1.0.min.js").exists()
published_runtime="\n".join((ROOT/name).read_text(errors="ignore")
    for name in ("index.html","en.html","app.js","scene-compare.js","style.css"))
assert "model-viewer" not in published_runtime.lower()
zh=(ROOT/"index.html").read_text()
en=(ROOT/"en.html").read_text()
assert "M4 revision 4 尚未完成完整独立视觉复审" in zh
assert "运行时配准与显示选择不会修改可下载的冻结 GLB 或 Blend 文件" in zh
assert "runtime registration and display choices do not modify the downloadable frozen glb or blend files" in en.lower()
assert "100 视角检查衡量一致性，而不是未见视角泛化" in zh
assert "the 100-view check measures consistency, not unseen-view generalization" in en.lower()
assert "一个场景可以看起来合理，却在空间上是错的" in zh
assert "a scene can look plausible and still be spatially wrong" in en.lower()

contract=json.loads((ROOT/"data/source_contract.json").read_text())
assert contract["presentation"]["table3_hidden_columns"]==["model_sha256","alignment"]
assert contract["presentation"]["table2_hidden_columns"]==["alignment"]
assert contract["presentation"]["figure1_layout"]=="single supplied teaser image"
assert contract["external_embed"]["office_cafe"]["retained_features"]==[
    "model","scan_to_model","source_video_to_model","source_camera_trajectory_playback",
    "shake_control","shake_gentle","shake_strong"]
src_table=SOURCE/contract["table_source"]["path"]
assert sha(src_table)==contract["table_source"]["sha256"]==sha(ROOT/"data/tables_1_7.json")
for published,item in contract["figures"].items():
    assert sha(ROOT/published)==item["sha256"]==sha(SOURCE/item["source"])
for method,files in contract["models"].items():
    for item in files.values():
        assert sha(ROOT/item["published"])==item["sha256"]==sha(SOURCE/item["source"])
assert len(list((ROOT/"models").glob("M*/scene.glb")))==4
assert len(list((ROOT/"models").glob("M*/scene.blend")))==4

gt=ROOT/"assets/comparison/GT.glb"
assert gt.stat().st_size==GT_BYTES and sha(gt)==GT_SHA
scene=json.loads((ROOT/"data/scene_comparison.json").read_text())
assert scene["gt_asset"]["source_url"]=="https://wentingw.github.io/astra-world-model-blog/assets/comparison/GT.glb"
assert scene["gt_asset"]["sha256"]==GT_SHA and scene["gt_asset"]["bytes"]==GT_BYTES
assert scene["camera"]=={"target":[18,1.2,-21],"position":[18,10,-3],"fov":42,"near":0.05,"far":500}
c=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]]; ci=[[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]
assert scene["coordinate_conversion"]["C_mapping"]=="[x,y,z] -> [x,z,-y]"
assert scene["display_cutaway"]["hide_name_pattern"]=="ceiling|roof|wall|facade"
assert scene["display_cutaway"]["keep_name_pattern"]=="mirror|emblem|art|grass|metal"
for method in METHODS:
    reg=scene["registrations"][method]
    assert reg["formula"]=="C * GT_from_model * C^-1"
    if method=="M4":
        assert reg["source"]["rule"]=="identity" and reg["source"]["path"] is None
    else:
        expected=f"astra_blender2/evaluation/reference_style_figures/registration_{method}.json"
        source=SOURCE/expected; raw=json.loads(source.read_text())
        assert reg["source"]["path"]==expected and reg["source"]["sha256"]==sha(source)
        assert reg["source"]["transform_direction"]=="GT_from_model"
        assert reg["GT_from_model_blender_z_up"]==raw["transform"]
    assert reg["runtime_matrix_gltf_y_up"]==mm(mm(c,reg["GT_from_model_blender_z_up"]),ci)
assert "diagnostic only" in scene["m1_diagnostic_caveat"].lower()

fixed=json.loads((ROOT/"data/fixed_views.json").read_text())
source_views=SOURCE/fixed["source_manifest"]
assert fixed["source_manifest_sha256"]==sha(source_views)
source_data=json.loads(source_views.read_text())["rgb_figure"]["inputs"]
expected={(x["method"],x["frame"]):x["sha256"] for x in source_data}
assert len(fixed["images"])==25 and len(expected)==25
assert {(x["method"],x["frame"]) for x in fixed["images"]}=={(m,f) for m in (*METHODS,"GT") for f in FRAMES}
for item in fixed["images"]:
    assert item["sha256"]==expected[(item["method"],item["frame"])]==sha(ROOT/item["published"])
    assert not Path(item["source"]).is_absolute(), item["source"]

assert all(not Path(item["source"]).is_absolute() for item in contract["vendor"].values())

for rel in ("three.module.js","three.core.js","loaders/GLTFLoader.js","controls/OrbitControls.js",
            "environments/RoomEnvironment.js","utils/BufferGeometryUtils.js"):
    assert (ROOT/"vendor/three"/rel).is_file(),rel
js=(ROOT/"scene-compare.js").read_text()
assert "setScissor(" in js and "singleCamera:true" in js and "singleViewport:true" in js
assert "runtime_matrix_gltf_y_up" in js and "applyMatrix4" in js
assert "hiddenCutaway" in js and "ceiling|roof|wall|facade" in js
app=(ROOT/"app.js").read_text()
assert '2:new Set(["alignment"])' in app
assert '3:new Set(["model_sha256","alignment"])' in app
assert 'document.createElement("strong")' in app
assert "fixedPreloads" not in app
assert 'method.disabled=false;frame.disabled=false;' in app
style=(ROOT/"style.css").read_text()
assert "#figure-5,#figure-6{width:100%;margin:30px 0}" in style
for name in ("index.html","en.html"):
    html=(ROOT/name).read_text()
    assert '<figure class="hero" id="figure-1"><img src="assets/teaser_originals.png"' in html

manifest=json.loads((ROOT/"evidence/publication_manifest.json").read_text())
for row in manifest["files"]: assert sha(ROOT/row["path"])==row["sha256"],row["path"]
for line in (ROOT/"evidence/SHA256SUMS").read_text().splitlines():
    expected_sha,rel=line.split("  ",1); assert sha(ROOT/rel)==expected_sha,rel
print(json.dumps({"status":"PASS","tables":7,"models":4,"fixed_views":25,"figures":6,
                  "checks":["links/anchors","GT SHA256","fixed-view SHA256","registration provenance","original GLB identity","no model-viewer"]},ensure_ascii=False))
