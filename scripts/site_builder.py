#!/usr/bin/env python3
"""Deterministically rebuild the bilingual static publication from frozen sources."""
from pathlib import Path
import argparse, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "world_lobby_four_trajectory_20260929"
TABLE_SOURCE = "astra_blender2/report/space/results/blog_tables_1_5/tables_1_5.json"
METHODS = ("M1", "M2", "M3", "M4")
FIGURES = ("figure14_abc.png", "fixed_five_view_comparison_m1_m4.jpg",
           "model_depth_error_five_views_m1_m4.png")
BASE_URL = "https://wentingw.github.io/agentic-world-blog/"

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
def dump(path, value): write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")
def copy(source, src_rel, dst_rel):
    src, dst = source / src_rel, ROOT / dst_rel
    if not src.is_file(): raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    return {"source": src_rel, "published": dst_rel, "sha256": digest(src), "bytes": src.stat().st_size}

def clean():
    for name in ("assets", "data", "evidence", "models", "vendor", "qa", "content"):
        if (ROOT/name).exists(): shutil.rmtree(ROOT/name)
    for name in ("index.html","en.html","app.js","style.css","article.zh.md","article.en.md",
                 ".publication.json"):
        (ROOT/name).unlink(missing_ok=True)

def page(en=False):
    L = {
      "title": "Four paths to an editable world" if en else "四条路径，重建一个可编辑世界",
      "desc": ("A measured comparison of four Astra–Blender reconstructions: pose, native and model depth, geometry, appearance, and novel-view depth."
               if en else "对四种 Astra–Blender 重建的克制比较：位姿、原生与模型深度、几何、外观和同场景新视角深度。"),
      "sections": (["Question & four methods","Pose and native/model depth","Editable M1–M4","Geometry","Appearance","Same-scene novel-view depth","Limits & evidence"]
                   if en else ["问题与四种方法","位姿与原生/模型深度","可编辑 M1–M4","几何","外观","同场景新视角深度","局限与证据"])
    }
    current, other = ("en.html","index.html") if en else ("index.html","en.html")
    ids=("question","pose-depth","editable","geometry","appearance","novel-depth","limitations")
    toc="".join(f'<a href="#{i}">{t}</a>' for i,t in zip(ids,L["sections"]))
    methods = ("M1 uses 180 sampled RGB images and infers an unmeasured layout. M2 uses RGB-only ViPE poses and pose-conditioned DA3 depth. "
      "M3 uses monocular-inertial ORB-SLAM3 poses and pose-conditioned DA3 depth. M4 uses GT camera poses and pose-conditioned DA3 depth; GT mesh and depth are not modelling inputs."
      if en else "M1 只用 180 张采样 RGB，布局没有测量尺度；M2 使用 RGB-only ViPE 位姿与 pose-conditioned DA3 深度；M3 使用 ORB-SLAM3 单目惯性位姿与 pose-conditioned DA3 深度；M4 使用 GT 相机位姿与 pose-conditioned DA3 深度，建模时不读取 GT 网格或 GT 深度。")
    intro = ("M4 is strongest overall in this case, but individual metrics are not monotonic. This single-scene engineering study does not establish general superiority."
      if en else "M4 在本案例中综合最好，但单项数值并不单调；单场景工程实验不能证明一般性优势。")
    depth = ("Native depth AbsRel evaluates upstream depth in its native camera/pose pipeline. Model depth AbsRel ray-casts the frozen Blender scene from evaluation cameras and therefore measures final scene geometry."
      if en else "原生深度 AbsRel 评估上游深度在其原生相机/位姿链路中的输出；模型深度 AbsRel 从评测相机向冻结 Blender 场景投射射线，衡量最终场景几何。")
    m1 = ("M1 model-space metrics use one frozen GT-assisted Sim(3) from five manual camera associations. They are diagnostic only and do not represent native metric recovery."
      if en else "M1 的模型空间指标使用由 5 个手工相机关联得到、冻结不变的 GT-assisted Sim(3)；仅作诊断显示，不表示原生 metric recovery。")
    m4 = ("M4 is revision 4: 74 semantic objects, 37 static AABB colliders, and 180 cameras. The independent reviewer examined revision 2 only. Revisions 3–4 fixed identified issues, but revision 4 has not received a complete independent visual re-review; final visual approval is not claimed."
      if en else "M4 为 revision 4：74 个 semantic objects、37 个 static AABB colliders、180 台 cameras。独立 reviewer 只审阅了 rev2；rev3/4 修复了已指出的问题，但 rev4 尚无完整独立视觉复审，因此不声称最终视觉通过。")
    def table_block(n):
        return f'<figure class="table-figure" id="table-{n}" data-table-key="table{n}"><figcaption><span>Table {n}.</span> <span class="table-title"></span></figcaption><div class="table-scroll table-mount" role="region" tabindex="0" aria-label="Table {n}"></div></figure>'
    cards="".join(f'<article class="model-card"><h3>{m}</h3><model-viewer src="models/{m}/scene.glb" camera-controls interaction-prompt="none" loading="lazy" alt="{m} editable reconstruction"></model-viewer><p><a href="models/{m}/scene.blend" download>scene.blend ↓</a> · <a href="models/{m}/scene.glb" download>scene.glb ↓</a> · <a href="evidence/{m}/manifest.json">manifest ↗</a></p></article>' for m in METHODS)
    return f'''<!doctype html><html lang="{"en" if en else "zh-CN"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{L["title"]} — Agentic World</title><meta name="description" content="{L["desc"]}"><meta property="og:type" content="article"><meta property="og:title" content="{L["title"]}"><meta property="og:description" content="{L["desc"]}"><meta property="og:image" content="{BASE_URL}assets/fixed_five_view_comparison_m1_m4.jpg"><meta property="og:url" content="{BASE_URL}{current}"><link rel="canonical" href="{BASE_URL}{current}"><link rel="alternate" hreflang="zh-CN" href="{BASE_URL}index.html"><link rel="alternate" hreflang="en" href="{BASE_URL}en.html"><link rel="stylesheet" href="style.css"><script type="module" src="vendor/model-viewer-4.1.0.min.js"></script><script src="app.js" defer></script></head>
<body data-lang="{"en" if en else "zh"}"><a class="skip" href="#main">{"Skip to article" if en else "跳到正文"}</a><nav><a class="brand" href="index.html">ASTRA / WORLD MODELS</a><div><a href="index.html" {"aria-current='page'" if not en else ""}>中文</a><a href="en.html" {"aria-current='page'" if en else ""}>EN</a><a href="data/source_contract.json">DATA ↗</a></div></nav>
<header><p class="eyebrow">RESEARCH JOURNAL · 30 SEPTEMBER 2026</p><h1>{L["title"]}</h1><p class="lead">{L["desc"]}</p><div class="meta"><span>1 scene</span><span>4 editable models</span><span>5 frozen tables</span></div></header>
<figure class="hero" id="figure-1"><img src="assets/fixed_five_view_comparison_m1_m4.jpg" alt="M1 to M4 and input GT across five fixed views"><figcaption><span>Figure 1.</span> {"M1–M4 and input GT across five fixed views." if en else "M1–M4 与输入 GT 在五个固定视角下的并排比较。"}</figcaption></figure>
<div class="layout"><aside class="toc"><p>ON THIS PAGE</p>{toc}</aside><main id="main">
<section id="question"><p class="section-tag">01 / QUESTION</p><h2>{L["sections"][0]}</h2><p class="standfirst">{intro}</p><p>{methods}</p>{table_block(1)}</section>
<section id="pose-depth"><p class="section-tag">02 / MEASUREMENT</p><h2>{L["sections"][1]}</h2><p>{depth}</p><p>{"Table 2 uses 180 fixed views and 19,200 optical-Z samples per view on the GT-valid domain, with no per-view fitting. M4 reaches the lowest model-depth AbsRel (7.60%), while native-depth errors remain much closer across M2–M4." if en else "Table 2 在 180 个固定视角上、每视角使用 19,200 个 optical-Z 样本，只评估 GT 有效域且不逐帧拟合。M4 的模型深度 AbsRel 最低（7.60%），但 M2–M4 的原生深度误差彼此接近得多。"}</p><aside class="notice"><strong>M1 diagnostic limitation.</strong> {m1}</aside><figure id="figure-2"><img loading="lazy" src="assets/figure14_abc.png" alt="Figure 14 a b c composite"><figcaption><span>Figure 2.</span> {"Figure 14(a)(b)(c), retained as one composite." if en else "Figure 14(a)(b)(c) 保持为一张完整大图。"}</figcaption></figure>{table_block(2)}</section>
<section id="editable"><p class="section-tag">03 / EDITABLE ASSETS</p><h2>{L["sections"][2]}</h2><p>{m4}</p><div class="model-grid">{cards}</div></section>
<section id="geometry"><p class="section-tag">04 / GEOMETRY</p><h2>{L["sections"][3]}</h2><p>{"Bidirectional surface distances use 100,000 seeded samples per side and exact nearest triangles under the declared alignment; no mesh ICP is fitted. M4 gives the lowest two-way means (0.0687 m and 0.0745 m), with M3 close on model→GT." if en else "双向表面距离每侧使用 100,000 个固定随机种子样本，在已声明配准下计算精确最近三角形距离；不额外拟合 mesh ICP。M4 的双向均值最低（0.0687 m、0.0745 m），M3 在模型→GT 方向很接近。"}</p>{table_block(3)}</section>
<section id="appearance"><p class="section-tag">05 / APPEARANCE</p><h2>{L["sections"][4]}</h2><p>{"Five full 640×480 views (0, 36, 72, 108, 144), with no crop, mask, or fitting. The ranking is not monotonic: M2 has the highest PSNR, M3 the highest SSIM, while M2 and M4 have nearly identical LPIPS." if en else "五个完整 640×480 视角（0、36、72、108、144），不裁剪、不遮罩、不拟合。排序并不单调：M2 的 PSNR 最高，M3 的 SSIM 最高，而 M2 与 M4 的 LPIPS 几乎相同。"}</p>{table_block(4)}</section>
<section id="novel-depth"><p class="section-tag">06 / NOVEL VIEWS</p><h2>{L["sections"][5]}</h2><p>{"Twenty same-scene views, 5,000 rays per view (seed 23), exact BVH optical-Z, GT-valid 0.1–30 m. M4 has the lowest AbsRel and penalized MAE, but M3 has a slightly lower RMSE—another reason not to reduce quality to one number." if en else "20 个同场景视角，每视角 5,000 条射线（seed 23），精确 BVH optical-Z，GT 有效范围 0.1–30 m。M4 的 AbsRel 与缺失惩罚 MAE 最低，但 M3 的 RMSE 略低——不能用一个数字概括全部质量。"}</p><figure id="figure-3"><img loading="lazy" src="assets/model_depth_error_five_views_m1_m4.png" alt="Model depth error for M1 to M4"><figcaption><span>Figure 3.</span> {"Model-depth error over five views; teal denotes missing or invalid samples." if en else "M1–M4 五视角模型深度误差；青绿色表示缺失或无效样本。"}</figcaption></figure>{table_block(5)}<noscript>JavaScript is required to render data/tables_1_5.json.</noscript></section>
<section id="limitations"><p class="section-tag">07 / LIMITS & EVIDENCE</p><h2>{L["sections"][6]}</h2><p>{"One synthetic scene and one run per route are insufficient for broad claims. Input budgets and revision effort are not a controlled ablation." if en else "单一合成场景、每条路线一次工程运行，不足以支持广泛结论；输入预算与修订投入也不是严格受控消融。"}</p><p><a href="data/tables_1_5.json">Tables JSON</a> · <a href="data/source_contract.json">Source contract</a> · <a href="evidence/publication_manifest.json">Manifest</a> · <a href="evidence/SHA256SUMS">SHA256</a></p></section>
</main></div><footer>Agentic World · frozen local publication · <a href="{other}">{"中文" if en else "English"}</a></footer></body></html>'''

STYLE=''':root{--paper:#f7f6f1;--white:#fffefa;--ink:#182c29;--muted:#60706a;--green:#196451;--line:#d9dfd7;--gold:#b87e40}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.8 Inter,"Noto Sans CJK SC",system-ui,sans-serif}a{color:var(--green);text-underline-offset:4px}img{display:block;max-width:100%;height:auto}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:white;padding:8px;z-index:5}nav{max-width:1420px;margin:auto;padding:22px 4vw;display:flex;justify-content:space-between;border-bottom:1px solid var(--line);font-size:12px;letter-spacing:.09em}nav div{display:flex;gap:20px}.brand{font-weight:750;text-decoration:none}header{max-width:1120px;margin:56px auto 36px;padding:0 32px}.eyebrow,.section-tag{font-size:11px;letter-spacing:.16em;color:var(--green);font-weight:700}h1,h2{font-family:Georgia,"Noto Serif CJK SC",serif;font-weight:500}h1{font-size:clamp(46px,7vw,88px);line-height:1.12;letter-spacing:-.035em;margin:18px 0}.lead{max-width:800px;color:var(--muted);font-size:20px}.meta{display:flex;gap:24px;flex-wrap:wrap;font-size:12px;color:var(--muted)}.hero{max-width:1320px;margin:35px auto 68px;padding:0 28px}.hero img,figure>img{width:100%;background:#e8ebe5}figcaption{font-size:12px;color:var(--muted);margin-top:10px}figcaption span{font-weight:700;color:var(--green)}.layout{max-width:1300px;margin:auto;padding:0 30px;display:grid;grid-template-columns:190px minmax(0,920px);gap:60px;justify-content:center}.toc{position:sticky;top:24px;align-self:start;display:flex;flex-direction:column;gap:9px;font-size:12px}.toc a{text-decoration:none;color:var(--muted)}main{min-width:0}section{padding:28px 0 38px;border-top:1px solid var(--line)}section:first-child{border-top:0}.standfirst{font-size:23px;line-height:1.55;color:var(--green)}h2{font-size:32px;margin:7px 0 22px}.notice{border-left:3px solid var(--gold);padding:10px 18px;margin:24px 0;color:var(--muted);background:#fff9}.model-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.model-card{border:1px solid var(--line);background:var(--white);padding:14px}.model-card h3{margin:0}.model-card p{font-size:12px}model-viewer{display:block;width:100%;height:330px;background:#e9ede5}.table-figure{margin:30px 0}.table-scroll{overflow:auto;border:1px solid var(--line);background:var(--white);margin-top:9px}table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:12px;font-variant-numeric:tabular-nums}th,td{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:#edf0e9;color:var(--muted)}td.wrap{white-space:normal;min-width:240px}footer{max-width:1120px;margin:70px auto 0;padding:30px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}@media(max-width:950px){.layout{grid-template-columns:1fr}.toc{position:static;display:grid;grid-template-columns:1fr 1fr}.model-grid{grid-template-columns:1fr}}@media(max-width:600px){body{font-size:16px}nav{padding:17px 18px}.brand{font-size:10px}nav div{gap:12px}header{padding:0 20px;margin-top:35px}h1{font-size:43px}.lead{font-size:17px}.hero{padding:0 12px;margin-bottom:40px}.layout{padding:0 20px}.toc{grid-template-columns:1fr}.standfirst{font-size:20px}h2{font-size:27px}model-viewer{height:300px}}'''

APP='''const C={zh:{t:["输入与建模路线","位姿、原生深度与模型深度","冻结模型几何","固定视角外观","同场景新视角深度"],l:{method:"方法",allowed_inputs:"允许输入",geometry_source:"几何来源",modeling_role:"建模角色",ate_m:"ATE (m) ↓",rotation_deg:"旋转误差 (°) ↓",native_depth_absrel:"原生深度 AbsRel ↓",model_depth_absrel:"模型深度 AbsRel ↓",alignment:"配准 / 限制",model_to_gt_mean_m:"模型→GT 均值 (m) ↓",observed_gt_to_model_mean_m:"观测 GT→模型均值 (m) ↓",model_sha256:"模型 SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"覆盖率 ↑",penalized_mae_m:"缺失惩罚 MAE (m) ↓"}},en:{t:["Inputs and modelling routes","Pose, native depth, and model depth","Frozen-model geometry","Fixed-view appearance","Same-scene novel-view depth"],l:{method:"Method",allowed_inputs:"Allowed inputs",geometry_source:"Geometry source",modeling_role:"Modelling role",ate_m:"ATE (m) ↓",rotation_deg:"Rotation (°) ↓",native_depth_absrel:"Native depth AbsRel ↓",model_depth_absrel:"Model depth AbsRel ↓",alignment:"Alignment / limitation",model_to_gt_mean_m:"Model→GT mean (m) ↓",observed_gt_to_model_mean_m:"Observed GT→model mean (m) ↓",model_sha256:"Model SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"Coverage ↑",penalized_mae_m:"Penalized MAE (m) ↓"}}};const fmt=(k,v)=>v===null?"—":typeof v!=="number"?String(v):["native_depth_absrel","model_depth_absrel","absrel","coverage"].includes(k)?(100*v).toFixed(2)+"%":v.toFixed(4);fetch("data/tables_1_5.json").then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(d=>{const c=C[document.body.dataset.lang];[1,2,3,4,5].forEach(i=>{const f=document.querySelector("#table-"+i),rows=d.tables["table"+i],keys=Object.keys(rows[0]);f.querySelector(".table-title").textContent=c.t[i-1];const t=document.createElement("table"),h=t.createTHead().insertRow();keys.forEach(k=>{const x=document.createElement("th");x.scope="col";x.textContent=c.l[k]||k;h.append(x)});const b=t.createTBody();rows.forEach(r=>{const tr=b.insertRow();keys.forEach((k,j)=>{const x=document.createElement(j?"td":"th");if(!j)x.scope="row";if(["allowed_inputs","geometry_source","modeling_role","alignment"].includes(k))x.className="wrap";x.textContent=fmt(k,r[k]);tr.append(x)})});f.querySelector(".table-mount").append(t)})}).catch(e=>{document.querySelectorAll(".table-mount").forEach(x=>x.textContent="Table load failed: "+e.message);console.error(e)});'''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,default=DEFAULT_SOURCE); source=ap.parse_args().source.resolve()
    clean()
    table_src=source/TABLE_SOURCE; tables=json.loads(table_src.read_text())
    if list(tables["tables"]) != [f"table{i}" for i in range(1,6)]: raise ValueError("exactly table1..table5 required")
    for key,rows in tables["tables"].items():
        if [r["method"] for r in rows] != list(METHODS): raise ValueError(f"{key}: exactly M1..M4 required")
    sources={}
    for name in FIGURES: sources[f"assets/{name}"]=copy(source,f"astra_blender2/report/space/assets/{name}",f"assets/{name}")
    sources["vendor/model-viewer-4.1.0.min.js"]=copy(source,"astra_blender2/report/space/vendor/model-viewer-4.1.0.min.js","vendor/model-viewer-4.1.0.min.js")
    models={}
    for m in METHODS:
        models[m]={}
        for ext in ("glb","blend"):
            item=copy(source,f"astra_blender/models/{m}/scene.{ext}",f"models/{m}/scene.{ext}"); models[m][ext]=item; sources[item["published"]]=item
        dump(ROOT/f"evidence/{m}/manifest.json",{"schema_version":1,"method":m,"files":models[m],"table_rows":{k:next(r for r in v if r["method"]==m) for k,v in tables["tables"].items()}})
    (ROOT/"data").mkdir(parents=True,exist_ok=True)
    shutil.copy2(table_src,ROOT/"data/tables_1_5.json")
    contract={"schema_version":1,"old_site_baseline":"ae69dbe","source_root_name":source.name,
      "table_source":{"path":TABLE_SOURCE,"sha256":digest(table_src),"published_url":"data/tables_1_5.json"},
      "figures":{k:v for k,v in sources.items() if k.startswith("assets/")},"models":models,
      "vendor":sources["vendor/model-viewer-4.1.0.min.js"],
      "tables":[{"number":i,"key":f"table{i}","methods":list(METHODS),
                 "columns":list(tables["tables"][f"table{i}"][0]),"url":f"index.html#table-{i}",
                 "english_url":f"en.html#table-{i}"} for i in range(1,6)],
      "protocols":tables["protocols"],"m1_notice":tables["m1_notice"]}
    dump(ROOT/"data/source_contract.json",contract); write(ROOT/"style.css",STYLE+"\n"); write(ROOT/"app.js",APP+"\n")
    write(ROOT/"index.html",page()+"\n"); write(ROOT/"en.html",page(True)+"\n"); (ROOT/".nojekyll").touch()
    write(ROOT/"README.md",'''# Agentic World · editable World Lobby

Bilingual static research journal rebuilt from frozen local sources. `index.html` is Chinese and `en.html` is English. Tables 1–5 are rendered directly from `data/tables_1_5.json`; four local `model-viewer` cards use no CDN.

## Build, validate, and serve

```bash
python scripts/build.py --source ../world_lobby_four_trajectory_20260929 && python scripts/validate.py && python -m http.server 8765
```

Open http://127.0.0.1:8765/. Optional browser QA (desktop and mobile screenshots go to a temporary directory by default):

```bash
python scripts/browser_qa.py --url http://127.0.0.1:8765/
```

If Playwright or its browser is unavailable, browser QA reports `SKIP` with installation guidance. Source identity and publication hashes are recorded in `data/source_contract.json`, `evidence/publication_manifest.json`, and `evidence/SHA256SUMS`.
''')
    write(ROOT/"requirements.txt","playwright>=1.40,<2\n")
    write(ROOT/".gitignore","__pycache__/\nqa/\n.venv/\n.publication.json\n")
    files=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in (".git","scripts") or rel.name in ("SHA256SUMS","publication_manifest.json") or rel.as_posix() in ("README.md","requirements.txt",".gitignore"): continue
        files.append({"path":rel.as_posix(),"sha256":digest(p),"bytes":p.stat().st_size})
    dump(ROOT/"evidence/publication_manifest.json",{"schema_version":1,"source_contract":"data/source_contract.json","files":files})
    sums=[f'{digest(ROOT/r["path"])}  {r["path"]}' for r in files]
    sums.append(f'{digest(ROOT/"evidence/publication_manifest.json")}  evidence/publication_manifest.json')
    write(ROOT/"evidence/SHA256SUMS","\n".join(sums)+"\n")
    print(json.dumps({"status":"BUILT","tables":5,"models":4,"files":len(files)}))
if __name__=="__main__": main()
