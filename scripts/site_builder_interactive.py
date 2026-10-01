#!/usr/bin/env python3
"""Build the interactive bilingual publication from frozen sources."""
from pathlib import Path
from urllib.request import Request, urlopen
import argparse, hashlib, html, json, shutil, tempfile
from editorial import BASE_URL, BIBTEX, SITE_TITLE, REFERENCES, narrative_copy, editorial_page

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "world_lobby_four_trajectory_20260929"
REFERENCE = ROOT.parent / "world_model_blog/private_repo/sceneweft_sync_20260925/blog"
TABLE_SOURCE = "astra_blender2/evaluation/blog_extended_100_20260930/tables_1_7.json"
VIEW_SOURCE = "astra_blender2/report/space/results/blog_tables_1_5/reference_style_figures.json"
REG_DIR = "astra_blender2/evaluation/reference_style_figures"
METHODS, FRAMES = ("M1", "M2", "M3", "M4"), (0, 36, 72, 108, 144)
GT_URL = "https://wentingw.github.io/astra-world-model-blog/assets/comparison/GT.glb"
GT_SHA = "6c28ab067c63c5b1fce19c6a972f3d66c7ac4d9bd9ce3b5a57e2e18f5641fe8f"
GT_BYTES = 24816108
OFFICE_URL = "https://office-cafe-vipe.hiwtishere.chatgpt.site/"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
def dump(path, value): write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")
def copy_checked(src, dst, expected=None, source_label=None):
    if not src.is_file(): raise FileNotFoundError(src)
    actual = sha(src)
    if expected and actual != expected: raise ValueError(f"SHA256 mismatch: {src}: {actual} != {expected}")
    dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    return {"source": source_label or str(src), "published": dst.relative_to(ROOT).as_posix(),
            "sha256": actual, "bytes": src.stat().st_size}
def mm(a, b): return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def clean():
    assets = ROOT / "assets"
    if assets.exists():
        for path in assets.iterdir():
            if path.name != "office-cafe":
                shutil.rmtree(path) if path.is_dir() else path.unlink()
    for name in ("data", "evidence", "models", "vendor", "qa", "content"):
        if (ROOT/name).exists(): shutil.rmtree(ROOT/name)
    for name in ("index.html","en.html","app.js","scene-compare.js","style.css",
                 "article.zh.md","article.en.md",".publication.json"):
        (ROOT/name).unlink(missing_ok=True)

def download_gt():
    target=ROOT/"assets/comparison/GT.glb"; target.parent.mkdir(parents=True,exist_ok=True)
    request=Request(GT_URL,headers={"User-Agent":"agentic-world-blog-builder/2"})
    with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as temp:
        tmp=Path(temp.name)
        with urlopen(request,timeout=180) as response: shutil.copyfileobj(response,temp)
    try:
        if tmp.stat().st_size != GT_BYTES: raise ValueError(f"GT bytes: {tmp.stat().st_size} != {GT_BYTES}")
        if sha(tmp) != GT_SHA: raise ValueError(f"GT SHA256: {sha(tmp)} != {GT_SHA}")
        tmp.replace(target)
    finally: tmp.unlink(missing_ok=True)
    return {"source_url":GT_URL,"published":"assets/comparison/GT.glb","sha256":GT_SHA,"bytes":GT_BYTES}

def table(n):
    return f'<figure class="table-figure" id="table-{n}" data-table-key="table{n}"><figcaption><span>Table {n}.</span> <span class="table-title"></span></figcaption><div class="table-scroll table-mount" role="region" tabindex="0" aria-label="Table {n}"></div></figure>'

def hero_figure(en):
    caption = "AWSM: from real spaces to worlds phygital agents can use." if en else "AWSM：把真实空间变成虚实融合智能体可以使用的世界。"
    label = "AWSM introduction video" if en else "AWSM 介绍视频"
    resources_label = "AWSM project resources" if en else "AWSM 项目资源"
    links = f'''<div class="project-links" role="group" aria-label="{resources_label}"><a class="project-resource" href="https://github.com/wentingw/AWSM" target="_blank" rel="noopener noreferrer"><img src="assets/icons/github.svg" width="24" height="24" alt="">GitHub</a><span class="project-resource"><img src="assets/icons/huggingface.svg" width="24" height="24" alt="">Hugging Face</span></div>'''
    return f'''<figure class="hero" id="figure-1"><video controls playsinline preload="metadata" poster="assets/awsm-promo-v5-poster.jpg" aria-label="{label}" aria-describedby="figure-1-caption"><source src="assets/awsm-promo-v5.mp4" type="video/mp4"><a href="assets/awsm-promo-v5.mp4">{label}</a></video><figcaption><div id="figure-1-caption"><span>Figure 1.</span> {caption}</div>{links}</figcaption></figure>'''

def overview_figure(en):
    return f'''<figure id="figure-5"><img loading="lazy" src="assets/fixed_five_view_comparison_m1_m4.jpg" alt="M1 to M4 and input GT across five fixed views"><figcaption><span>Figure 5.</span> {"M1–M4 and input GT across five fixed views." if en else "M1–M4 与输入 GT 在五个固定视角下的并排比较。"}</figcaption></figure>'''

def scene_figure(en):
    options="".join(f'<option value="{m}"{" selected" if m=="M4" else ""}>{m}</option>' for m in METHODS)+'<option value="GT">GT</option>'
    return f'''<figure class="scene-comparison" id="figure-3" data-state="idle"><h3>{"Rotate, zoom, and inspect the frozen scenes" if en else "旋转、缩放，检查冻结场景"}</h3>
<div class="scene-toolbar"><label class="method-control">{"Reconstruction / GT" if en else "重建方法 / GT"}<select id="model-select">{options}</select></label><label>{"Display" if en else "显示方式"}<select id="scene-mode"><option value="compare">{"Split comparison with GT" if en else "中轴线对比 GT"}</option><option value="single">{"View selected scene alone" if en else "单独查看所选场景"}</option></select></label><button id="scene-reset" type="button">{"Reset view" if en else "重置视角"}</button></div>
<div class="scene-stage"><span class="scene-label scene-label-left">M4</span><span class="scene-label scene-label-right">GT</span><button class="scene-divider" type="button" role="slider" aria-label="Comparison divider" aria-valuemin="2" aria-valuemax="98" aria-valuenow="50"></button><input id="scene-split" class="scene-split" type="range" min="2" max="98" value="50" aria-label="Comparison split"><p class="scene-status">{"Scroll here to load the 3D comparison." if en else "滚动到此处加载三维对比。"}</p></div><button id="scene-retry" class="scene-retry" type="button">{"Retry" if en else "重试"}</button>
<figcaption><span>Figure 3.</span> {"One camera and one full viewport compare the selected frozen model with GT. Ceilings and surrounding walls are hidden at runtime for the same cutaway-style inspection; source files remain unchanged." if en else "所选冻结模型与 GT 共用同一相机和完整 viewport；网页运行时隐藏顶棚与四周墙体，以相同剖视方式检查，源模型文件保持不变。"}</figcaption></figure>'''

def fixed_figure(en):
    methods="".join(f'<option value="{m}">{m}</option>' for m in METHODS)
    frames="".join(f'<option value="{f}">{f}</option>' for f in FRAMES)
    return f'''<figure class="fixed-comparison" id="figure-4"><div class="controlrow"><label>{"Method" if en else "方法"}<select id="compare-method" disabled>{methods}</select></label><label>{"Fixed view" if en else "固定视角"}<select id="compare-frame" disabled>{frames}</select></label></div><div class="compare-pair"><div><img id="compare-pred" src="assets/fixed_views/M1/000.png" alt="Selected frozen model rendering"><p id="compare-label" class="compare-subcaption">M1 / {"VIEW" if en else "视角"} 0</p></div><div><img id="compare-gt" src="assets/fixed_views/GT/000.png" alt="Input GT RGB"><p class="compare-subcaption">INPUT / GT RGB</p></div></div><figcaption><span>Figure 4.</span> {"Frozen-model rendering and input GT RGB from exactly the same view." if en else "同一所选视角下的冻结模型渲染与输入 GT RGB。"}</figcaption></figure>'''

def downloads():
    return '<div class="asset-downloads">'+"".join(f'<p><strong>{m}</strong> <a href="models/{m}/scene.blend" download>scene.blend ↓</a> · <a href="models/{m}/scene.glb" download>scene.glb ↓</a> · <a href="evidence/{m}/manifest.json">manifest ↗</a></p>' for m in METHODS)+'</div>'

def office_videos(en):
    media_root = "https://github.com/Phygital-AI/agentic-world-simulation-and-mapping/releases/download/office-media-20261001"
    titles = ("Input video", "Procedural model", "Point cloud") if en else ("输入视频", "程序化模型", "点云")
    descriptions = ("Original phone walkthrough.", "Model rendered along the source-camera trajectory.", "Scan rendered along the same trajectory.") if en else ("原始手机拍摄视频。", "沿原视频相机轨迹渲染的模型。", "沿相同轨迹渲染的扫描点云。")
    cards = "".join(
        f'<figure class="office-video-card"><video data-synced-video muted preload="metadata" playsinline poster="assets/office-cafe/{stem}-poster.jpg" src="{media_root}/{stem}.mp4" aria-label="{title}"></video><figcaption><strong>{title}</strong><span>{description}</span></figcaption></figure>'
        for stem, title, description in zip(("office-input", "office-pmodel", "office-scan"), titles, descriptions)
    )
    return f'''<div class="office-video-grid office-video-sync">{cards}</div>
<div class="office-video-controls"><button class="office-video-play" type="button" aria-label="{"Play all three videos" if en else "播放全部三个视频"}" aria-pressed="false">▶</button><input class="office-video-progress" type="range" min="0" max="1000" value="0" aria-label="{"Shared video progress" if en else "三个视频的共同播放进度"}"><output class="office-video-time">00:00 / 01:10</output><p class="office-video-status" role="status" aria-live="polite">{"Shared playback · 70.1 seconds · 30 fps" if en else "同步播放 · 70.1 秒 · 30 fps"}</p></div>'''


def office_case(en):
    if en:
        return f'''<div id="office-cafe" class="analysis-block external-case"><h3>Beyond the lobby: what survives in a phone-captured space?</h3><p>Office Café is not a second run of the World Lobby benchmark and is not quantitative validation under the same protocol. It is an external, real-capture case study showing how an object-centric scene, a solved source-camera trajectory, video-to-model comparison, and physics replays can coexist in one inspectable artifact. An author-observed failure—a curved real-world corner simplified into a square one—motivates separating local shape from global scale. A correct scale alone cannot repair that shape error; this is a qualitative observation, not another measured benchmark.</p><p class="office-links"><a href="https://office-cafe-vipe.hiwtishere.chatgpt.site/?lang=en" target="_blank" rel="noopener">Open full-screen model ↗</a><a href="https://office-cafe-vipe.hiwtishere.chatgpt.site/shake?lang=en" target="_blank" rel="noopener">Open shake experiment ↗</a></p><div class="office-model-grid"><figure class="office-model-card"><div class="office-model-stage" data-src="assets/office-cafe/scene.glb" aria-label="Interactive Office Café ViPE model"></div><figcaption><strong>Current model</strong><span>Video plus estimated depth as input; drag to orbit, right-drag to pan, and scroll to zoom.</span></figcaption></figure><figure class="office-model-card"><div class="office-model-stage" data-src="assets/office-cafe/atlas-scene.glb" aria-label="Interactive legacy Office Café model"></div><figcaption><strong>Legacy model</strong><span>Video-only input; this legacy layout was not recalibrated against the ViPE scan.</span></figcaption></figure></div><p class="office-model-note">Both models open in an elevated cutaway view: upper geometry is clipped only for display to expose the interior. Toggle Cutaway to inspect the complete model; Reset view restores the overview. Authored coordinates, materials, and model files are unchanged. Linked orbit controls compare layouts, not registered geometry.</p>{office_videos(en)}<div class="office-video-grid"><figure class="office-video-card office-video-card-wide"><video controls preload="metadata" playsinline poster="assets/office-cafe/office-shake-heavy-poster.jpg" src="assets/office-cafe/office-shake-heavy.mp4"></video><figcaption><strong>Strong earthquake effect</strong><span>Every object in the scene is interactable, and cabinet doors can open; this replay shows the physical response under strong shaking.</span></figcaption></figure></div><script type="module" src="office-models.js"></script></div>'''
    return f'''<div id="office-cafe" class="analysis-block external-case"><h3>走出仿真大厅：手机采集空间中还剩下什么？</h3><p>Office Café 不是 World Lobby 基准的第二次运行，也不构成同协议的定量验证。它是一个真实采集的外部案例，用于展示对象化场景、求解后的原视频相机轨迹、视频—模型对照与物理回放如何组合成一个可检查的空间产物。作者观察到的一类失败是：真实的弯曲转角被简化成方正结构。它提醒我们区分局部形状与全局尺度——尺度正确并不能自动修复形状错误；这里将其作为定性观察，而非另一组定量结果。</p><p class="office-links"><a href="https://office-cafe-vipe.hiwtishere.chatgpt.site/?lang=en" target="_blank" rel="noopener">全屏打开模型 ↗</a><a href="https://office-cafe-vipe.hiwtishere.chatgpt.site/shake?lang=en" target="_blank" rel="noopener">打开摇晃实验 ↗</a></p><div class="office-model-grid"><figure class="office-model-card"><div class="office-model-stage" data-src="assets/office-cafe/scene.glb" aria-label="可旋转查看的 Office Café 原有模型"></div><figcaption><strong>原有模型</strong><span>输入为视频与估计深度；拖动旋转、右键平移、滚轮缩放。</span></figcaption></figure><figure class="office-model-card"><div class="office-model-stage" data-src="assets/office-cafe/atlas-scene.glb" aria-label="可旋转查看的 Office Café 旧模型"></div><figcaption><strong>旧模型</strong><span>输入仅为视频；该旧版布局未按 ViPE 扫描重新标定。</span></figcaption></figure></div><p class="office-model-note">两个模型默认采用俯视剖切视图，仅在显示时裁去上部遮挡，以展示室内布局；点击“剖切视图”可切换完整模型，“重置视角”可恢复总览。原始坐标、材质和模型文件保持不变。联动旋转用于观察布局，不代表几何配准。</p>{office_videos(en)}<div class="office-video-grid"><figure class="office-video-card office-video-card-wide"><video controls preload="metadata" playsinline poster="assets/office-cafe/office-shake-heavy-poster.jpg" src="assets/office-cafe/office-shake-heavy.mp4"></video><figcaption><strong>较强地震效果</strong><span>场景中的物体均可交互，柜门可以打开；此段展示较强摇晃下的物理响应。</span></figcaption></figure></div><script type="module" src="office-models.js"></script></div>'''

def office_section(en):
    return f'''<section id="office-cafe"><p class="section-tag">08 / OFFICE CAFÉ</p><h2>{"From a phone walkthrough to an interactive twin" if en else "从手机视频到可交互空间"}</h2><p>{"The complete Office Café viewer is embedded below. It retains model-only, scan ↔ model, and source-video ↔ model comparison modes; playback follows all 2,103 solved source-camera poses. The linked shake experiment retains control, gentle, and strong MuJoCo replays." if en else "下方嵌入完整 Office Café 查看器：保留“模型”“扫描 ↔ 模型”“原视频 ↔ 模型”三种对照方式，并可沿 2,103 个求解后的原视频相机位姿播放。摇晃实验继续提供零摇晃、轻度和较强三组 MuJoCo 回放。"}</p><p class="office-links"><a href="{OFFICE_URL}" target="_blank" rel="noopener">{"Open full viewer" if en else "全屏打开模型"} ↗</a><a href="{OFFICE_URL}shake.html" target="_blank" rel="noopener">{"Open shake experiment" if en else "打开摇晃实验"} ↗</a></p><div class="office-cafe-embed"><iframe src="{OFFICE_URL}" title="Office Café interactive spatial twin" loading="lazy" allow="fullscreen" allowfullscreen></iframe></div></section>'''

def legacy_page(en=False):
    title="Four paths to an editable world" if en else "四条路径，重建一个可编辑世界"
    desc=("A measured comparison of four Astra–Blender reconstructions: pose, depth, geometry, appearance, and novel-view depth." if en else "对四种 Astra–Blender 重建的克制比较：位姿、深度、几何、外观和同场景新视角深度。")
    sections=(["Question & four methods","Pose and native/model depth","Editable M1–M4","Geometry","Appearance","Same-scene novel-view depth","Limits & evidence","Office Café twin"] if en else ["问题与四种方法","位姿与原生/模型深度","可编辑 M1–M4","几何","外观","同场景新视角深度","局限与证据","Office Café 模型"])
    ids=("question","pose-depth","editable","geometry","appearance","novel-depth","limitations","office-cafe")
    toc="".join(f'<a href="#{i}">{t}</a>' for i,t in zip(ids,sections)); current,other=("en.html","index.html") if en else ("index.html","en.html")
    methods=("M1 uses sampled RGB and an unmeasured layout. M2 uses RGB-only ViPE poses and pose-conditioned DA3 depth. M3 uses monocular-inertial ORB-SLAM3 poses and pose-conditioned DA3 depth. M4 uses GT camera poses and pose-conditioned DA3 depth; GT mesh and depth are not modelling inputs." if en else "M1 使用采样 RGB 与无测量尺度的布局；M2 使用 RGB-only ViPE 位姿与 pose-conditioned DA3 深度；M3 使用 ORB-SLAM3 单目惯性位姿与 pose-conditioned DA3 深度；M4 使用 GT 相机位姿与 pose-conditioned DA3 深度，建模时不读取 GT 网格或 GT 深度。")
    m1=("M1 uses one frozen GT-assisted Sim(3) from five manual camera associations. It is diagnostic only and does not represent native metric recovery." if en else "M1 使用由 5 个手工相机关联得到、冻结不变的 GT-assisted Sim(3)；仅作诊断，不表示原生 metric recovery。")
    m4=("M4 is revision 4: 74 semantic objects, 37 static AABB colliders, and 180 cameras. The independent reviewer examined revision 2 only. Revisions 3–4 fixed identified issues, but revision 4 has not received a complete independent visual re-review; final visual approval is not claimed." if en else "M4 为 revision 4：74 个 semantic objects、37 个 static AABB colliders、180 台 cameras。独立 reviewer 只审阅了 rev2；rev3/4 修复了已指出的问题，但 rev4 尚无完整独立视觉复审，因此不声称最终视觉通过。")
    copy_notice=("These display copies and runtime registrations do not alter the frozen models. M1's alignment is diagnostic only." if en else "这些展示副本和运行时配准不改变冻结模型；M1 配准仅作诊断。")
    return f'''<!doctype html><html lang="{"en" if en else "zh-CN"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — Agentic World</title><meta name="description" content="{desc}"><meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="{BASE_URL}assets/fixed_five_view_comparison_m1_m4.jpg"><meta property="og:url" content="{BASE_URL}{current}"><link rel="canonical" href="{BASE_URL}{current}"><link rel="alternate" hreflang="zh-CN" href="{BASE_URL}index.html"><link rel="alternate" hreflang="en" href="{BASE_URL}en.html"><link rel="stylesheet" href="style.css"><script type="importmap">{{"imports":{{"three":"./vendor/three/three.module.js"}}}}</script><script src="app.js" defer></script><script type="module" src="scene-compare.js"></script></head>
<body data-lang="{"en" if en else "zh"}"><a class="skip" href="#main">{"Skip to article" if en else "跳到正文"}</a><nav><a class="brand" href="index.html">ASTRA / WORLD MODELS</a><div><a href="index.html" {"aria-current='page'" if not en else ""}>中文</a><a href="en.html" {"aria-current='page'" if en else ""}>EN</a><a href="data/source_contract.json">DATA ↗</a></div></nav><header><p class="eyebrow">RESEARCH JOURNAL · 30 SEPTEMBER 2026</p><h1>{title}</h1><p class="lead">{desc}</p><div class="meta"><span>1 scene</span><span>4 editable models</span><span>7 frozen tables</span></div></header>
{hero_figure(en)}<div class="layout"><aside class="toc"><p>ON THIS PAGE</p>{toc}</aside><main id="main">
<section id="question"><p class="section-tag">01 / QUESTION</p><h2>{sections[0]}</h2><p class="standfirst">{"M4 is strongest overall in this case, but this single-scene study does not establish general superiority." if en else "M4 在本案例中综合最好，但单场景工程实验不能证明一般性优势。"}</p><p>{methods}</p>{table(1)}</section>
<section id="pose-depth"><p class="section-tag">02 / MEASUREMENT</p><h2>{sections[1]}</h2><p>{"Native depth evaluates the upstream pipeline. Model depth ray-casts the final frozen Blender scene." if en else "原生深度评估上游链路；模型深度从评测相机向最终冻结 Blender 场景投射射线。"}</p><aside class="notice"><strong>M1 diagnostic limitation.</strong> {m1}</aside>{table(2)}<figure id="figure-2"><img loading="lazy" src="assets/figure14_abc.png" alt="Trajectory and depth composite"><figcaption><span>Figure 2.</span> {"Trajectory, native depth, and model depth." if en else "轨迹、原生深度与模型深度。"}</figcaption></figure></section>
<section id="editable"><p class="section-tag">03 / EDITABLE ASSETS</p><h2>{sections[2]}</h2><p>{m4}</p><p>{copy_notice}</p>{overview_figure(en)}{scene_figure(en)}{fixed_figure(en)}{downloads()}</section>
<section id="geometry"><p class="section-tag">04 / GEOMETRY</p><h2>{sections[3]}</h2><p>{"Bidirectional distances use 100,000 seeded samples per side under the declared global alignment; no mesh ICP is fitted." if en else "双向表面距离每侧使用 100,000 个固定随机种子样本，并采用已声明的全局配准；不额外拟合 mesh ICP。"}</p>{table(3)}</section>
<section id="appearance"><p class="section-tag">05 / APPEARANCE</p><h2>{sections[4]}</h2><p>{"Table 4 uses the five fixed 640×480 checks (0, 36, 72, 108, 144). Table 5 uses one seeded set of 100 views sampled from the other 175 modeling frames. These 100 views are new evaluation views relative to the fixed-five check, but they were still available as modeling RGB inputs. No crop, mask, or per-view fitting is used." if en else "Table 4 使用 5 个固定 640×480 检查视角（0、36、72、108、144）。Table 5 从其余 175 张建模帧中按固定随机种子抽取同一组 100 个视角；它们只相对于固定 5 帧是新的检查视角，仍属于建模 RGB 输入，并非未见输入。全部评测均不裁剪、不遮罩、不逐视角拟合。"}</p>{table(4)}{table(5)}</section>
<section id="novel-depth"><p class="section-tag">06 / NOVEL VIEWS</p><h2>{sections[5]}</h2><p>{"Table 6 evaluates model optical-Z on the five fixed reference views. Table 7 uses exactly the same seeded 100-view set as Table 5 and aggregates all GT-valid pixels." if en else "Table 6 在固定 5 个参考视角上评测模型 optical-Z；Table 7 使用与 Table 5 完全相同的固定随机 100 视角，并在全部 GT 有效像素上汇总。"}</p><figure id="figure-6"><img loading="lazy" src="assets/model_depth_error_five_views_m1_m4.png" alt="Model depth error for M1 to M4"><figcaption><span>Figure 6.</span> {"Model-depth error over five fixed views; teal denotes missing or invalid samples." if en else "M1–M4 五个固定视角的模型深度误差；青绿色表示缺失或无效样本。"}</figcaption></figure>{table(6)}{table(7)}<noscript>JavaScript is required for the tables and interactive figures.</noscript></section>
<section id="limitations"><p class="section-tag">07 / LIMITS & EVIDENCE</p><h2>{sections[6]}</h2><p>{"One synthetic scene and one run per route are insufficient for broad claims." if en else "单一合成场景、每条路线一次工程运行，不足以支持广泛结论。"}</p><p><a href="data/tables_1_7.json">Tables JSON</a> · <a href="data/scene_comparison.json">Scene manifest</a> · <a href="data/fixed_views.json">Fixed views</a> · <a href="evidence/publication_manifest.json">Manifest</a> · <a href="evidence/SHA256SUMS">SHA256</a></p></section>{office_section(en)}</main></div><footer>Agentic World · frozen local publication · <a href="{other}">{"中文" if en else "English"}</a></footer></body></html>'''

STYLE=r''':root{--paper:#f7f6f1;--white:#fffefa;--ink:#182c29;--muted:#60706a;--green:#196451;--line:#d9dfd7;--gold:#b87e40}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.8 Inter,"Noto Sans CJK SC",system-ui,sans-serif}a{color:var(--green);text-underline-offset:4px}img{display:block;max-width:100%;height:auto}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:white;padding:8px;z-index:9}nav{max-width:1420px;margin:auto;padding:22px 4vw;display:flex;justify-content:space-between;border-bottom:1px solid var(--line);font-size:12px;letter-spacing:.09em}nav div{display:flex;gap:20px}.brand{font-weight:750;text-decoration:none}header{max-width:1120px;margin:56px auto 36px;padding:0 32px}.eyebrow,.section-tag{font-size:11px;letter-spacing:.16em;color:var(--green);font-weight:700}h1,h2{font-family:Georgia,"Noto Serif CJK SC",serif;font-weight:500}h1{font-size:clamp(46px,7vw,88px);line-height:1.12;letter-spacing:-.035em;margin:18px 0}.lead{max-width:800px;color:var(--muted);font-size:20px}.meta{display:flex;gap:24px;flex-wrap:wrap;font-size:12px;color:var(--muted)}.hero{max-width:1320px;margin:35px auto 68px;padding:0 28px}.hero img,figure>img{width:100%;background:#e8ebe5}.hero-pair-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px;background:var(--ink)}.hero-pair-grid img{width:100%;aspect-ratio:4/3;object-fit:cover}.hero-pair-grid p{margin:0;padding:7px 12px;background:var(--ink);color:#f7f6f1;font-size:10px;letter-spacing:.11em}figcaption{font-size:12px;color:var(--muted);margin-top:10px}figcaption span{font-weight:700;color:var(--green)}.layout{max-width:1300px;margin:auto;padding:0 30px;display:grid;grid-template-columns:190px minmax(0,920px);gap:60px;justify-content:center}.toc{position:sticky;top:24px;align-self:start;display:flex;flex-direction:column;gap:9px;font-size:12px}.toc a{text-decoration:none;color:var(--muted)}main{min-width:0}section{padding:28px 0 38px;border-top:1px solid var(--line)}section:first-child{border-top:0}.standfirst{font-size:23px;line-height:1.55;color:var(--green)}h2{font-size:32px;margin:7px 0 22px}.notice{border-left:3px solid var(--gold);padding:10px 18px;margin:24px 0;color:var(--muted);background:#fff9}.table-figure{margin:30px 0}.table-scroll{overflow:auto;border:1px solid var(--line);background:var(--white);margin-top:9px}table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:12px;font-variant-numeric:tabular-nums}th,td{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:#edf0e9;color:var(--muted)}td.wrap{white-space:normal;min-width:240px}.scene-comparison,.fixed-comparison{margin:34px 0;padding:20px;border:1px solid var(--line);border-radius:6px;background:var(--white)}.scene-comparison h3{margin:0 0 18px}.scene-toolbar,.controlrow{display:flex;gap:14px 20px;align-items:end;flex-wrap:wrap}.scene-toolbar label,.controlrow label{display:flex;flex-direction:column;font-size:12px;color:var(--muted)}.method-control{flex:1 1 280px}select,button{font:inherit}.scene-toolbar button,.scene-retry{font-size:13px;padding:9px 13px;color:var(--green);border:1px solid var(--line);border-radius:3px;background:var(--paper);cursor:pointer}.scene-stage{position:relative;height:540px;width:100%;background:#e9ede5;margin-top:18px;overflow:hidden;border-radius:4px;--split:50%}.scene-stage canvas{display:block;width:100%;height:100%;touch-action:none}.scene-label{position:absolute;top:12px;z-index:3;padding:4px 8px;background:#fffde;color:var(--ink);font-size:11px;pointer-events:none}.scene-label-left{left:12px}.scene-label-right{right:12px}.scene-divider{position:absolute;z-index:4;left:var(--split);top:0;width:3px;height:100%;padding:0;border:0;background:white;box-shadow:0 0 0 1px #182c2955;transform:translateX(-50%);cursor:ew-resize;touch-action:none}.scene-divider:after{content:"↔";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:30px;height:30px;line-height:27px;border-radius:50%;background:white;color:var(--green);border:1px solid var(--line)}.scene-split{position:absolute;width:1px;height:1px;opacity:0}.scene-status{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);padding:9px 12px;background:#fffef0;z-index:5;font-size:13px}.scene-status.error{color:#8d251d}.scene-retry{display:none;margin-top:10px}.scene-comparison[data-state=error] .scene-retry{display:inline-block}.scene-comparison:not(.is-comparing) .scene-divider{display:none}.compare-pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}.compare-pair img{width:100%;aspect-ratio:4/3;object-fit:contain;background:#e9ede5}.compare-subcaption{margin:6px 0 0;font-size:11px;color:var(--muted);letter-spacing:.04em}.asset-downloads{display:grid;grid-template-columns:1fr 1fr;gap:0 20px;font-size:12px}.asset-downloads p{margin:4px 0}.office-cafe-embed{margin-top:24px;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#111}.office-cafe-embed iframe{display:block;width:100%;height:min(880px,85vh);min-height:680px;border:0;background:#111}.office-links{display:flex;gap:18px;flex-wrap:wrap;font-size:12px}footer{max-width:1120px;margin:70px auto 0;padding:30px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}@media(max-width:950px){.layout{grid-template-columns:1fr}.toc{position:static;display:grid;grid-template-columns:1fr 1fr}}@media(max-width:600px){body{font-size:16px}nav{padding:17px 18px}.brand{font-size:10px}nav div{gap:12px}header{padding:0 20px;margin-top:35px}h1{font-size:43px}.lead{font-size:17px}.hero{padding:0 12px;margin-bottom:40px}.layout{padding:0 20px}.toc{grid-template-columns:1fr}.standfirst{font-size:20px}h2{font-size:27px}.scene-comparison,.fixed-comparison{padding:12px}.scene-stage{height:360px}.compare-pair,.asset-downloads{grid-template-columns:1fr}.office-cafe-embed iframe{height:760px;min-height:620px}}'''

APP=r'''const C={zh:{t:["输入与建模路线","位姿、原生深度与模型深度","冻结模型几何","固定 5 视角外观","同场景 100 视角外观","固定 5 视角模型深度","同场景 100 视角模型深度"],view:"视角",l:{method:"方法",allowed_inputs:"允许输入",geometry_source:"几何来源",modeling_role:"建模角色",ate_m:"ATE (m) ↓",rotation_deg:"旋转误差 (°) ↓",native_depth_absrel:"原生深度 AbsRel ↓",model_depth_absrel:"模型深度 AbsRel ↓",alignment:"配准 / 限制",model_to_gt_mean_m:"模型→GT 均值 (m) ↓",observed_gt_to_model_mean_m:"观测 GT→模型均值 (m) ↓",bidirectional_mean_m:"双向平均 (m) ↓",model_sha256:"模型 SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"覆盖率 ↑",penalized_mae_m:"缺失惩罚 MAE (m) ↓"}},en:{t:["Inputs and modelling routes","Pose, native depth, and model depth","Frozen-model geometry","Fixed-five appearance","Same-scene 100-view appearance","Fixed-five model depth","Same-scene 100-view model depth"],view:"VIEW",l:{method:"Method",allowed_inputs:"Allowed inputs",geometry_source:"Geometry source",modeling_role:"Modelling role",ate_m:"ATE (m) ↓",rotation_deg:"Rotation (°) ↓",native_depth_absrel:"Native depth AbsRel ↓",model_depth_absrel:"Model depth AbsRel ↓",alignment:"Alignment / limitation",model_to_gt_mean_m:"Model→GT mean (m) ↓",observed_gt_to_model_mean_m:"Observed GT→model mean (m) ↓",bidirectional_mean_m:"Bidirectional mean (m) ↓",model_sha256:"Model SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"Coverage ↑",penalized_mae_m:"Penalized MAE (m) ↓"}}};const c=C[document.body.dataset.lang],directions={ate_m:"min",rotation_deg:"min",native_depth_absrel:"min",model_depth_absrel:"min",model_to_gt_mean_m:"min",observed_gt_to_model_mean_m:"min",bidirectional_mean_m:"min",psnr_db:"max",ssim:"max",lpips_alex_v01:"min",absrel:"min",rmse_m:"min",coverage:"max",penalized_mae_m:"min"},hidden={2:new Set(["alignment"]),3:new Set(["model_sha256","alignment"])},fmt=(k,v)=>v===null?"—":typeof v!=="number"?String(v):["native_depth_absrel","model_depth_absrel","absrel","coverage"].includes(k)?(100*v).toFixed(2)+"%":v.toFixed(4);fetch("data/tables_1_7.json").then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(d=>{[1,2,3,4,5,6,7].forEach(i=>{const f=document.querySelector("#table-"+i);if(!f)return;const rows=d.tables["table"+i],keys=Object.keys(rows[0]).filter(k=>!hidden[i]?.has(k)),best={};keys.forEach(k=>{if(!directions[k])return;const values=rows.map(r=>r[k]).filter(v=>typeof v==="number"&&Number.isFinite(v));if(values.length)best[k]=(directions[k]==="max"?Math.max:Math.min)(...values)});f.querySelector(".table-title").textContent=c.t[i-1];const t=document.createElement("table"),h=t.createTHead().insertRow();keys.forEach(k=>{const x=document.createElement("th");x.scope="col";x.textContent=c.l[k]||k;h.append(x)});const b=t.createTBody();rows.forEach(r=>{const tr=b.insertRow();keys.forEach((k,j)=>{const x=document.createElement(j?"td":"th");if(!j)x.scope="row";if(["allowed_inputs","geometry_source","modeling_role","alignment"].includes(k))x.className="wrap";const text=fmt(k,r[k]);if(typeof r[k]==="number"&&r[k]===best[k]){const strong=document.createElement("strong");strong.textContent=text;x.append(strong)}else x.textContent=text;tr.append(x)})});f.querySelector(".table-mount").append(t)})}).catch(e=>{document.querySelectorAll(".table-mount").forEach(x=>x.textContent="Table load failed: "+e.message);console.error(e)});const fixedPreloads=[];for(const m of ["M1","M2","M3","M4","GT"])for(const f of [0,36,72,108,144]){const image=new Image();image.src=`assets/fixed_views/${m}/${String(f).padStart(3,"0")}.png`;fixedPreloads.push(image)}const method=document.querySelector("#compare-method"),frame=document.querySelector("#compare-frame");function refresh(){const id=String(frame.value).padStart(3,"0"),m=method.value;document.querySelector("#compare-pred").src=`assets/fixed_views/${m}/${id}.png`;document.querySelector("#compare-gt").src=`assets/fixed_views/GT/${id}.png`;document.querySelector("#compare-label").textContent=`${m} / ${c.view} ${frame.value}`;document.querySelector("#figure-4").dataset.method=m;document.querySelector("#figure-4").dataset.frame=frame.value}method?.addEventListener("change",refresh);frame?.addEventListener("change",refresh);refresh();'''

SCENE_JS=r'''import * as THREE from 'three';import {GLTFLoader} from './vendor/three/loaders/GLTFLoader.js';import {OrbitControls} from './vendor/three/controls/OrbitControls.js';import {RoomEnvironment} from './vendor/three/environments/RoomEnvironment.js';
const panel=document.querySelector('#figure-3');if(panel){const stage=panel.querySelector('.scene-stage'),select=panel.querySelector('#model-select'),mode=panel.querySelector('#scene-mode'),slider=panel.querySelector('#scene-split'),divider=panel.querySelector('.scene-divider'),status=panel.querySelector('.scene-status'),left=panel.querySelector('.scene-label-left'),right=panel.querySelector('.scene-label-right'),zh=document.documentElement.lang.startsWith('zh');let started=false,active=false,renderer,camera,controls,environment,manifest,selectedScene,truthScene,resizeObserver,split=.5,version=0;const cache=new Map();const setStatus=(text,error=false)=>{status.textContent=text;status.hidden=!text;status.classList.toggle('error',error);panel.dataset.state=error?'error':text?'loading':'ready'};
function render(){if(!renderer||!selectedScene)return;const w=stage.clientWidth,h=stage.clientHeight;renderer.setScissorTest(false);renderer.setViewport(0,0,w,h);renderer.clear();if(mode.value==='single'||select.value==='GT'||!truthScene){renderer.render(selectedScene,camera);return}const x=Math.round(w*split);renderer.setScissorTest(true);renderer.setScissor(0,0,x,h);renderer.render(selectedScene,camera);renderer.setScissor(x,0,w-x,h);renderer.render(truthScene,camera);renderer.setScissorTest(false)}
function updateMode(){const comparing=mode.value==='compare'&&select.value!=='GT';panel.classList.toggle('is-comparing',comparing);slider.disabled=!comparing;divider.hidden=!comparing;right.hidden=!comparing;left.textContent=select.value;render()}function updateSplit(value){split=Math.max(.02,Math.min(.98,Number(value)/100));slider.value=String(Math.round(split*100));stage.style.setProperty('--split',`${split*100}%`);divider.setAttribute('aria-valuenow',slider.value);render()}
function resetCamera(){if(!camera||!manifest)return;const v=manifest.camera;controls.target.fromArray(v.target);camera.position.fromArray(v.position).sub(controls.target).multiplyScalar(Math.max(1,1.5/(stage.clientWidth/stage.clientHeight))).add(controls.target);camera.near=v.near;camera.far=v.far;camera.fov=v.fov;camera.updateProjectionMatrix();controls.update();render()}function resize(){if(!renderer)return;const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);const oldFit=Math.max(1,1.5/camera.aspect);camera.aspect=w/h;if(controls)camera.position.sub(controls.target).multiplyScalar(Math.max(1,1.5/camera.aspect)/oldFit).add(controls.target);camera.updateProjectionMatrix();render()}
function loadScene(id){if(!cache.has(id)){const promise=new GLTFLoader().loadAsync(manifest.models[id].url).then(gltf=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#e9ede5');scene.environment=environment;scene.add(new THREE.HemisphereLight(0xffffff,0x68746b,2));const sun=new THREE.DirectionalLight(0xffffff,2.3);sun.position.set(12,25,18);scene.add(sun);let hiddenCutaway=0;if(id!=='GT'){const rows=manifest.models[id].runtime_matrix_gltf_y_up;gltf.scene.applyMatrix4(new THREE.Matrix4().set(...rows.flat()));gltf.scene.traverse(node=>{const name=node.name||'',isShell=/(ceiling|roof|wall|facade)/i.test(name),isDetail=/(emblem|art|grass|metal)/i.test(name);if(isShell&&!isDetail){node.visible=false;hiddenCutaway++}})}scene.add(gltf.scene);const bounds=new THREE.Box3().setFromObject(gltf.scene);scene.userData.method=id;scene.userData.hiddenCutaway=hiddenCutaway;scene.userData.bounds={min:bounds.min.toArray(),max:bounds.max.toArray()};return scene}).catch(e=>{cache.delete(id);throw e});cache.set(id,promise)}return cache.get(id)}
async function selectScene(){if(!manifest)return;const request=++version,id=select.value;setStatus(zh?`正在加载 ${id}…`:`Loading ${id}…`);try{const [model,gt]=await Promise.all([loadScene(id),loadScene('GT')]);if(request!==version)return;selectedScene=model;truthScene=gt;setStatus('');updateMode();panel.dataset.loadedModel=id;panel.dataset.gtLoaded='true'}catch(e){if(request!==version)return;console.error('Scene asset load failed',e);setStatus(zh?'场景加载失败，请重试。':'Scene loading failed. Retry.',true)}}
async function start(){if(started)return;started=true;try{setStatus(zh?'正在加载对比场景…':'Loading comparison scenes…');const response=await fetch('data/scene_comparison.json', {cache:'no-store'});if(!response.ok)throw Error(`manifest HTTP ${response.status}`);manifest=await response.json();renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.domElement.setAttribute('aria-label',zh?'重建与 GT 三维场景':'Reconstruction and GT 3D scene');renderer.domElement.tabIndex=0;stage.prepend(renderer.domElement);camera=new THREE.PerspectiveCamera(42,1,.05,500);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=1;controls.maxDistance=200;controls.addEventListener('change',render);const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();environment=pmrem.fromScene(room,.04).texture;room.dispose();pmrem.dispose();resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);resize();resetCamera();panel.sceneDiagnostics=()=>({selected:select.value,loaded:selectedScene?.userData.method,gtLoaded:!!truthScene,hiddenCutaway:selectedScene?.userData.hiddenCutaway||0,bounds:selectedScene?.userData.bounds,camera:camera.position.toArray(),target:controls.target.toArray(),split,mode:mode.value,singleCamera:true,singleViewport:true,coordinateConversion:manifest.coordinate_conversion,cachedModels:[...cache.keys()]});await selectScene()}catch(e){console.error('Scene comparison initialization failed',e);resizeObserver?.disconnect();controls?.dispose();environment?.dispose();renderer?.dispose();renderer?.domElement.remove();renderer=camera=controls=environment=manifest=undefined;selectedScene=truthScene=undefined;cache.clear();started=false;setStatus(zh?'无法启动三维场景，请重试。':'Unable to start 3D viewer. Retry.',true)}}
select.addEventListener('change',()=>{updateMode();selectScene()});mode.addEventListener('change',updateMode);slider.addEventListener('input',()=>updateSplit(slider.value));panel.querySelector('#scene-reset').addEventListener('click',resetCamera);panel.querySelector('#scene-retry').addEventListener('click',()=>manifest&&renderer?selectScene():start());divider.addEventListener('pointerdown',e=>{e.preventDefault();active=true;divider.setPointerCapture(e.pointerId);if(controls)controls.enabled=false});divider.addEventListener('pointermove',e=>{if(!active)return;const b=stage.getBoundingClientRect();updateSplit((e.clientX-b.left)/b.width*100)});const stop=()=>{active=false;if(controls)controls.enabled=true};divider.addEventListener('pointerup',stop);divider.addEventListener('pointercancel',stop);divider.addEventListener('keydown',e=>{const d={ArrowLeft:-2,ArrowRight:2,PageDown:-10,PageUp:10};if(e.key in d){e.preventDefault();updateSplit(split*100+d[e.key])}});updateSplit(50);updateMode();const lazy=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){lazy.disconnect();start()}},{rootMargin:'300px'});lazy.observe(panel)}'''

def academic_page(en=False):
    current, other = ("index.html", "zh.html") if en else ("zh.html", "index.html")
    if en:
        title = SITE_TITLE
        desc = "From real spaces to worlds phygital agents can use."
        sections = [
            ("results", "Overview"),
            ("motivation", "Motivation"),
            ("workflow", "Workflow"),
            ("more-results", "Results & analysis"),
            ("related-work", "Related work"),
            ("limitations", "Limitations"),
            ("citation", "Citation"),
            ("references", "References"),
        ]
        copy = {
            "hook": "A scene can look plausible and still be spatially wrong.",
            "tldr": "We isolate how camera pose and depth evidence propagate through an agentic Blender reconstruction pipeline. Stronger geometric evidence consistently improves the frozen scene’s geometry and model depth, but appearance metrics remain split—showing that spatial fidelity and visual similarity are distinct objectives.",
            "intro1": "Image synthesis rewards a convincing frame. A spatial system has a harder obligation: scale, location, occlusion, and object boundaries must remain coherent when the camera moves—and the result must still be editable after rendering ends.",
            "intro2": "We reconstruct World Lobby, a simulated scene in NVIDIA Isaac Sim, through four complete engineering routes, from RGB-only modeling to ground-truth-pose-conditioned modeling. Each route produces a frozen Blender scene, not merely a point cloud or a novel-view renderer. The experiment asks what additional geometric evidence buys, where it fails to help, and which errors survive object-centric reconstruction.",
            "contributions": [
                "A controlled four-route study that keeps the scene, 180 RGB identities, modeling objective, and editable output format fixed while varying the geometric evidence.",
                "A measurement contract that separates trajectory error, native depth, frozen-scene depth, surface geometry, and rendered appearance instead of collapsing them into one score.",
                "Frozen Blend/GLB assets, deterministic evaluation subsets, public hashes, and interactive comparisons that let readers inspect where aggregate metrics agree—and where they do not.",
            ],
            "metric1": "0.376 → 0.072 m",
            "metric1_label": "bidirectional surface error",
            "metric2": "16.44% → 7.60%",
            "metric2_label": "180-view model-depth AbsRel",
            "metric3": "No universal winner",
            "metric3_label": "PSNR, SSIM, and LPIPS disagree",
            "motivation_title": "From a good-looking render to a usable spatial representation",
            "motivation1": "An editable world model is useful because its objects can be selected, moved, hidden, assigned materials, queried for collisions, and revisited from known cameras. Those affordances matter for design, robotics, and simulation. They also expose errors that a single attractive image can conceal.",
            "motivation2": "Our working hypothesis is that measurement does not replace generative reasoning; it constrains it. Pose and depth should reduce the space of plausible layouts, while the modeling system converts noisy observations into a compact semantic scene. That conversion can regularize noise, but it is also lossy: omitted surfaces and simplified materials do not reappear simply because the camera trajectory improves.",
            "positioning": "ViPE estimates camera motion and near-metric geometry from RGB video; ORB-SLAM3 provides a classical visual-inertial trajectory; Depth Anything 3 predicts pose-conditioned multi-view depth. These systems produce measurements, not editable objects. Concurrent work AHa-3D explores video-driven agentic Real2Sim; we discuss it as a parallel effort, not a precursor to AWSM. Our emphasis is additional physical evidence, including IMU-informed visual-inertial constraints, for geometric grounding. Our question is complementary and deliberately narrower: when the modeling objective is held fixed, which measurement channel changes the final editable world—and which errors remain downstream?",
            "method_title": "Four routes, one frozen evaluation contract",
            "method1": "All routes receive the same 180 RGB identities and the same Astra–Blender modeling objective. M1 tests how far visual priors can go without metric measurements. M2 adds RGB-only ViPE poses and pose-conditioned DA3 depth. M3 uses monocular-inertial ORB-SLAM3 poses with the same class of DA3 observations. M4 supplies ground-truth camera poses to diagnose the remaining modeling error; it does not receive the GT mesh or GT depth as modeling input.",
            "workflow": [
                ("Observe", "Inspect all 180 RGB frames and, where allowed, pose-conditioned DA3 geometry."),
                ("Build", "Write Blender Python that decomposes the room into named objects, materials, cameras, and collision proxies."),
                ("Verify", "Compare paired RGB and optical-Z renders at fixed review cameras; revise within a fixed version budget."),
                ("Freeze", "Export Blend/GLB, manifests, semantic IDs, and hashes before any GT score is visible to the author."),
                ("Evaluate", "Measure pose, native depth, model depth, surface distance, and appearance under one frozen protocol."),
            ],
            "method2": "Ground truth is introduced only after the scenes are frozen. M2 and M3 are evaluated under one global SE(3) alignment with scale fixed to one; no mesh ICP or per-view fitting is used. M1 has no native metric trajectory, so its model-space numbers use one frozen GT-assisted Sim(3) from five manual camera associations and remain diagnostic rather than evidence of metric recovery.",
            "results_title": "Three findings matter more than a leaderboard",
            "finding1_title": "1. Better pose does not mechanically imply better native depth",
            "finding1": "M3 improves trajectory accuracy over M2—ATE falls from 0.167 m to 0.121 m and rotation error from 0.31° to 0.19°. Yet its native DA3 AbsRel is slightly worse (20.38% versus 19.06%). After modeling, the ordering reverses: M3 reaches 8.37% model-depth AbsRel versus 9.29% for M2. Upstream metrics and downstream scene fidelity are related, but they are not interchangeable.",
            "finding2_title": "2. Geometric evidence turns a plausible layout into a more faithful space",
            "finding2": "Under the declared alignment and without mesh ICP, bidirectional surface error falls from 0.376 m for the RGB-only diagnostic baseline to 0.118 m with ViPE, 0.082 m with ORB-SLAM3, and 0.072 m with GT poses. M4 is strongest on geometry in this case, while M3 closes most of the gap using an estimated trajectory.",
            "finding3_title": "3. Qualitative comparison",
            "interactive_title": "Do not trust the aggregate alone—inspect the frozen worlds",
            "interactive1": "Use the shared camera to compare each reconstruction with GT. Start with M1 to see how a semantically plausible room can drift in metric layout; compare M2 and M3 to find regions where geometry improves without a matching gain in RGB similarity; then inspect M4 to isolate errors that remain even when camera pose is no longer the bottleneck.",
            "interactive2": "The browser hides ceilings and surrounding walls only for cutaway inspection. Runtime registration and display choices do not modify the downloadable frozen GLB or Blend files.",
            "discussion_title": "What this case suggests about editable world models",
            "discussion1_title": "Modeling behaves like a structured—and lossy—regularizer",
            "discussion1": "For M2–M4, the final scene depth is substantially closer to GT than native DA3 depth on the shared 180-view protocol: AbsRel falls by roughly 51–60%. One plausible interpretation is that object-level aggregation suppresses inconsistent local predictions. This is a hypothesis, not a controlled causal result: the same abstraction can also erase real surfaces and fine geometry.",
            "discussion2_title": "Measurement constrains generation; it does not solve appearance",
            "discussion2": "The strongest geometric route does not dominate PSNR or SSIM. Pose removes one source of uncertainty, but appearance still depends on material estimation, lighting, object detail, and renderer mismatch. Evaluating only RGB would miss spatial progress; evaluating only geometry would miss perceptual failure.",
            "discussion3_title": "The 100-view check measures consistency, not unseen-view generalization",
            "discussion3": "Table 7 uses a seeded set of 100 cameras drawn from the 175 modeling frames outside the fixed-five check. These are additional evaluation views relative to that check, but their RGB images were available during modeling. On this set, M4 has the lowest depth AbsRel (7.47%), while M3 has the lowest RMSE (1.090 m).",
            "limits_title": "The boundaries are part of the result",
            "limits": [
                "One synthetic scene and one engineering run per route do not establish general superiority or statistical significance.",
                "The four routes are complete systems, not a strict single-variable ablation; M2 versus M3 cannot be attributed to IMU alone.",
                "M4 uses GT camera poses and is a diagnostic route, not a deployable baseline or a theoretical upper bound.",
                "M1 model-space metrics rely on GT-assisted Sim(3) and must not be ranked as native metric recovery.",
                "The 100-view appearance and depth sets contain modeling RGB inputs; they are not a held-out novel-view benchmark.",
                "Appearance metrics mix geometry, material, illumination, and rendering error. M4 revision 4 has not received a complete independent visual re-review.",
            ],
            "evidence": "Every table is generated from frozen assets. The public manifests expose model hashes, registrations, fixed views, and the exact seeded evaluation indices.",
            "office_title": "Beyond the lobby: what survives in a phone-captured space?",
            "office1": "Office Café is not a second run of the World Lobby benchmark and is not quantitative validation under the same protocol. It is an external, real-capture case study showing how an object-centric scene, a solved source-camera trajectory, video-to-model comparison, and physics replays can coexist in one inspectable artifact.",
            "open_viewer": "Open full viewer",
            "open_shake": "Open shake experiment",
        }
    else:
        title = "AWSM：智能体世界仿真与建图"
        desc = "把真实空间，变成虚实融合智能体可以使用的世界。"
        sections = [
            ("results", "概览"),
            ("motivation", "研究动机"),
            ("workflow", "工作流"),
            ("more-results", "结果与分析"),
            ("related-work", "相关工作"),
            ("limitations", "局限性"),
            ("citation", "引用"),
            ("references", "参考文献"),
        ]
        copy = {
            "hook": "一个场景可以看起来合理，却在空间上是错的。",
            "tldr": "我们研究相机位姿与深度证据如何穿过 agentic Blender 重建流程，最终影响冻结场景。更强的几何证据持续改善模型几何与模型深度，但外观指标依然分化——空间忠实度与视觉相似度是两类不同目标。",
            "intro1": "图像生成奖励一张令人信服的画面；空间系统承担更严格的义务：当相机移动时，尺度、位置、遮挡与物体边界仍需保持一致，而且渲染结束后，结果还必须能够被编辑。",
            "intro2": "我们对 NVIDIA Isaac Sim 中的 World Lobby 仿真场景，沿四条完整工程路径进行重建：从纯 RGB 建模，逐步加入估计位姿、深度与真实相机位姿。每条路径交付的是冻结的 Blender 场景，而不只是点云或新视角渲染器。实验关注的不是谁生成了最漂亮的单帧，而是几何证据究竟带来了什么、没有解决什么，以及哪些误差会穿过对象化建模继续存在。",
            "contributions": [
                "一项受控的四路径研究：固定场景、180 张 RGB 身份、建模目标与可编辑交付格式，只改变可用的几何证据。",
                "一份分解式测量契约：分别评估轨迹、原生深度、冻结场景深度、表面几何与渲染外观，而不是把它们压缩成一个总分。",
                "可下载的冻结 Blend/GLB、确定性评测子集、公开哈希与交互对照，使读者能够检查平均指标在哪些区域成立、又在哪里失效。",
            ],
            "metric1": "0.376 → 0.072 m",
            "metric1_label": "双向表面误差",
            "metric2": "16.44% → 7.60%",
            "metric2_label": "180 视角模型深度 AbsRel",
            "metric3": "没有单一赢家",
            "metric3_label": "PSNR、SSIM 与 LPIPS 结论分化",
            "motivation_title": "从“看起来不错”到“可以使用”的空间表示",
            "motivation1": "可编辑世界模型的价值，在于其中的对象能够被选择、移动、隐藏、赋予材质、查询碰撞，并从已知相机重新访问。这些能力服务于设计、机器人与仿真，也会暴露一张漂亮图片可以掩盖的空间错误。",
            "motivation2": "我们的工作假设是：测量不是生成推理的替代品，而是它的约束。位姿与深度应当缩小合理布局的解空间，建模系统则把噪声观测压缩为语义场景。这种转换可能正则化噪声，但同样是有损的：遗漏的表面、近似的材质，不会仅仅因为相机轨迹更准确而自动恢复。",
            "positioning": "ViPE 从 RGB 视频估计相机运动与近米制几何，ORB-SLAM3 提供经典的视觉—惯性轨迹，Depth Anything 3 预测位姿条件下的多视图深度；它们输出的是测量，而不是可编辑对象。同期工作 AHa-3D 探索视频驱动的 agentic Real2Sim；我们将其作为并行探索，而非 AWSM 的前置工作。我们强调利用额外物理证据，尤其是融合 IMU 的视觉惯性约束，进行几何锚定。本文的问题与之互补且更窄：当建模目标保持不变时，哪一种测量通道真正改变了最终可编辑世界，哪些误差仍会留在下游？",
            "method_title": "四条路径，一份冻结评测契约",
            "method1": "四条路径使用相同的 180 张 RGB 身份和相同的 Astra–Blender 建模目标。M1 检验没有米制测量时视觉先验能走多远；M2 加入 RGB-only ViPE 位姿与 pose-conditioned DA3 深度；M3 使用 ORB-SLAM3 单目惯性位姿与同类 DA3 观测；M4 提供 GT 相机位姿，用于诊断剩余建模误差，但建模时不读取 GT 网格或 GT 深度。",
            "workflow": [
                ("观察", "检查全部 180 张 RGB；在允许的方法中读取位姿条件下的 DA3 几何。"),
                ("建模", "编写 Blender Python，将房间拆解为命名对象、材质、相机与碰撞代理。"),
                ("验证", "在固定修订相机上比较成对 RGB 与 optical-Z 渲染，并在固定版本预算内修改。"),
                ("冻结", "在作者看到任何 GT 评分前，导出 Blend/GLB、manifest、语义 ID 与哈希。"),
                ("评测", "在同一冻结协议下分别测量位姿、原生深度、模型深度、表面距离与外观。"),
            ],
            "method2": "所有场景冻结后才引入真值。M2/M3 只使用一次全局 SE(3) 配准，尺度固定为 1；不进行 mesh ICP 或逐视角拟合。M1 没有原生米制轨迹，其模型空间指标使用由 5 个手工相机关联得到、冻结不变的 GT-assisted Sim(3)，因此只能解释形状与显示误差，不能视为米制恢复。",
            "results_title": "比排行榜更重要的三个发现",
            "finding1_title": "1. 更好的位姿不会机械地带来更好的原生深度",
            "finding1": "M3 的轨迹优于 M2：ATE 从 0.167 m 降至 0.121 m，旋转误差从 0.31° 降至 0.19°；但 M3 的原生 DA3 AbsRel 反而略差（20.38% 对 19.06%）。经过建模后，排序再次反转：M3 的模型深度 AbsRel 为 8.37%，优于 M2 的 9.29%。上游指标与最终场景忠实度相关，却不能彼此替代。",
            "finding2_title": "2. 几何证据把“合理布局”约束成更忠实的空间",
            "finding2": "在声明配准且不使用 mesh ICP 的条件下，双向表面误差从纯 RGB 诊断基线的 0.376 m，依次降至 ViPE 的 0.118 m、ORB-SLAM3 的 0.082 m 与 GT 位姿的 0.072 m。M4 在本案例中拥有最强几何，而 M3 依靠估计轨迹已经缩小了大部分差距。",
            "finding3_title": "3. 定性比较",
            "interactive_title": "不要只相信平均值——亲自检查冻结场景",
            "interactive1": "在共享相机中将每个重建与 GT 对照：先从 M1 观察语义上合理的房间如何偏离米制布局；再比较 M2/M3，寻找几何改善但 RGB 相似度未同步提升的区域；最后检查 M4，把相机位姿不再是瓶颈后仍然存在的建模与材质误差分离出来。",
            "interactive2": "网页只在运行时隐藏顶棚与四周墙体，以便剖视检查；运行时配准与显示选择不会修改可下载的冻结 GLB 或 Blend 文件。",
            "discussion_title": "这个案例对可编辑世界模型意味着什么",
            "discussion1_title": "建模像一种结构化、同时有损的正则化",
            "discussion1": "在共享的 180 视角协议下，M2–M4 的最终场景深度都显著接近 GT：相较原生 DA3，AbsRel 约下降 51–60%。一种可能解释是，对象级聚合抑制了局部不一致预测；但这仍是假说，而非受控因果结论。同一种抽象也可能删除真实表面与细节。",
            "discussion2_title": "测量约束生成，却不会自动解决外观",
            "discussion2": "几何最强的路径并未统治 PSNR 或 SSIM。位姿消除了一类不确定性，外观仍受材质估计、照明、物体细节与渲染器差异支配。只评 RGB 会漏掉空间进步，只评几何也会漏掉感知失败。",
            "discussion3_title": "100 视角检查衡量一致性，而不是未见视角泛化",
            "discussion3": "Table 7 使用一组固定随机种子的 100 个相机，它们从固定 5 帧之外的 175 张建模帧中抽取。这些视角相对固定检查是额外视角，但其 RGB 在建模阶段可见。在该集合上，M4 的深度 AbsRel 最低（7.47%），M3 的 RMSE 最低（1.090 m）。",
            "limits_title": "边界本身也是结果的一部分",
            "limits": [
                "一个合成场景、每条路径一次工程运行，不能建立一般优越性或统计显著性。",
                "四条路径是完整系统，而非严格的单变量消融；M2 与 M3 的差异不能只归因于 IMU。",
                "M4 使用 GT 相机位姿，是诊断路线，不是可部署基线，也不是理论上界。",
                "M1 模型空间指标依赖 GT-assisted Sim(3)，不能与原生米制恢复混为一谈。",
                "100 视角外观与深度集合包含建模 RGB 输入，不是 held-out novel-view benchmark。",
                "外观指标混合了几何、材质、照明与渲染误差；M4 revision 4 尚未完成完整独立视觉复审。",
            ],
            "evidence": "所有表格都由冻结资产生成；公开 manifest 提供模型哈希、配准、固定视角与固定随机评测索引。",
            "office_title": "走出仿真大厅：手机采集空间中还剩下什么？",
            "office1": "Office Café 不是 World Lobby 基准的第二次运行，也不构成同协议的定量验证。它是一个真实采集的外部案例，用于展示对象化场景、求解后的原视频相机轨迹、视频—模型对照与物理回放如何组合成一个可检查的空间产物。",
            "open_viewer": "全屏打开模型",
            "open_shake": "打开摇晃实验",
        }
    narrative_copy(copy, en)
    toc = "".join(f'<a href="#{anchor}">{label}</a>' for anchor, label in sections)
    limits = "".join(f"<li>{item}</li>" for item in copy["limits"])
    contributions = "".join(f"<li>{item}</li>" for item in copy["contributions"])
    workflow = "".join(
        f'<div><strong>{index:02d} · {name}</strong><span>{description}</span></div>'
        for index, (name, description) in enumerate(copy["workflow"], 1)
    )
    related_links = (
        '<span class="inline-sources">'
        '<a href="https://research.nvidia.com/labs/toronto-ai/vipe/" target="_blank" rel="noopener">ViPE</a> · '
        '<a href="https://arxiv.org/abs/2007.11898" target="_blank" rel="noopener">ORB-SLAM3</a> · '
        '<a href="https://arxiv.org/abs/2511.10647" target="_blank" rel="noopener">Depth Anything 3</a> · '
        '<a href="https://kevinxu02.github.io/real2sim-indoor-site/" target="_blank" rel="noopener">AHa-3D</a>'
        '</span>'
    )
    citation = html.escape(BIBTEX.rstrip())
    references = [
        ('AHa-3D: Agentic Tool Use for Real2Sim with GPT-6 Astra.',
         'https://kevinxu02.github.io/real2sim-indoor-site/'),
        ('ViPE: Video Pose Engine for camera motion and near-metric geometry.',
         'https://arxiv.org/abs/2508.10934'),
        ('Campos et al. ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual–Inertial, and Multimap SLAM. IEEE Transactions on Robotics, 2021.',
         'https://arxiv.org/abs/2007.11898'),
        ('Depth Anything 3: Recovering the Visual Space from Any Views.',
         'https://arxiv.org/abs/2511.10647'),
        ('Wang et al. Image Quality Assessment: From Error Visibility to Structural Similarity. IEEE Transactions on Image Processing, 2004.',
         'https://doi.org/10.1109/TIP.2003.819861'),
        ('Zhang et al. The Unreasonable Effectiveness of Deep Features as a Perceptual Metric. CVPR, 2018.',
         'https://arxiv.org/abs/1801.03924'),
        ('Blender Foundation. Blender: Free and Open Source 3D Creation Suite.',
         'https://www.blender.org/'),
    ]
    references.extend(REFERENCES)
    reference_list = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener">{text}</a></li>'
        for text, url in references
    )
    page = f'''<!doctype html><html lang="{"en" if en else "zh-CN"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — Phygital AI</title><meta name="description" content="{desc}"><meta property="og:type" content="article"><meta property="og:locale" content="{"en_US" if en else "zh_CN"}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="{BASE_URL}assets/teaser_originals.png"><meta property="og:url" content="{BASE_URL}{current}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{BASE_URL}assets/teaser_originals.png"><link rel="canonical" href="{BASE_URL}{current}"><link rel="alternate" hreflang="zh-CN" href="{BASE_URL}index.html"><link rel="alternate" hreflang="en" href="{BASE_URL}en.html"><link rel="stylesheet" href="style.css"><script type="importmap">{{"imports":{{"three":"./vendor/three/three.module.js"}}}}</script><script src="app.js" defer></script><script type="module" src="scene-compare.js"></script></head>
<body data-lang="{"en" if en else "zh"}"><a class="skip" href="#main">{"Skip to article" if en else "跳到正文"}</a><nav><a class="brand" href="index.html">ASTRA / WORLD MODELS</a><div><a href="index.html" {"aria-current='page'" if not en else ""}>中文</a><a href="en.html" {"aria-current='page'" if en else ""}>EN</a><a href="data/source_contract.json">DATA ↗</a></div></nav><header><p class="eyebrow">RESEARCH ESSAY · EDITABLE WORLD MODELS</p><h1>{title}</h1><p class="lead">{desc}</p><div class="meta"><span>{"1 controlled scene" if en else "1 个受控场景"}</span><span>{"4 reconstruction routes" if en else "4 条重建路径"}</span><span>{"editable Blender outputs" if en else "可编辑 Blender 交付"}</span></div></header>
{hero_figure(en)}<div class="layout"><aside class="toc"><p>ON THIS PAGE</p>{toc}</aside><main id="main">
<section id="results"><p class="section-tag">01 / RESULTS</p><aside class="tldr"><strong>TL;DR</strong><p>{copy["tldr"]}</p></aside><h2>{copy["hook"]}</h2><p class="standfirst">{copy["intro1"]}</p><p>{copy["intro2"]}</p><div class="insight-strip"><div><strong>{copy["metric1"]}</strong><span>{copy["metric1_label"]}</span></div><div><strong>{copy["metric2"]}</strong><span>{copy["metric2_label"]}</span></div></div><p class="metric-caveat">{"M1 values use a diagnostic GT-assisted Sim(3); all claims are scoped to this frozen single-scene study." if en else "M1 数值使用诊断性的 GT-assisted Sim(3)；所有结论仅适用于本次冻结的单场景研究。"}</p></section>
<section id="motivation"><p class="section-tag">02 / MOTIVATION</p><h2>{copy["motivation_title"]}</h2><p>{copy["motivation1"]}</p><p>{copy["motivation2"]}</p><aside class="claim"><strong>{"Research question" if en else "研究问题"}</strong><p>{"How does progressively stronger geometric evidence change the fidelity—and the remaining failure modes—of an editable object-centric world?" if en else "逐步增强的几何证据，如何改变一个对象化可编辑世界的忠实度，以及它仍然保留的失败模式？"}</p></aside><h3>{"Contributions" if en else "本文贡献"}</h3><ol class="contributions">{contributions}</ol></section>
<section id="workflow"><p class="section-tag">03 / WORKFLOW</p><h2>{copy["method_title"]}</h2><p>{copy["method_intro"]}</p><p>{copy["method1"]}</p>{table(1)}<h3>{"Agentic reconstruction loop" if en else "Agentic 重建闭环"}</h3><div class="workflow-strip">{workflow}</div><p>{copy["method2"]}</p><aside class="notice"><strong>M1 diagnostic limitation.</strong> {"Its Sim(3)-aligned geometry and depth numbers describe shape after GT-assisted display alignment, not native metric recovery." if en else "其 Sim(3) 配准后的几何与深度数值描述 GT-assisted 显示配准后的形状，不代表原生米制恢复。"}</aside></section>
<section id="more-results"><p class="section-tag">04 / MORE RESULTS AND ANALYSIS</p><h2>{copy["results_title"]}</h2><article class="finding"><p class="finding-kicker">FINDING 01</p><h3>{copy["finding1_title"]}</h3><p>{copy["finding1"]}</p></article>{table(2)}<figure id="figure-2"><img loading="lazy" src="assets/figure14_abc.png" alt="Trajectory, native depth, and model depth"><figcaption><span>Figure 2.</span> {"The upstream trajectory and native-depth ranking does not map one-to-one onto frozen-scene depth." if en else "上游轨迹与原生深度的排序，并不会一一映射为冻结场景的深度排序。"}</figcaption></figure><article class="finding"><p class="finding-kicker">FINDING 02</p><h3>{copy["finding2_title"]}</h3><p>{copy["finding2"]}</p></article>{table(3)}<article class="finding"><p class="finding-kicker">FINDING 03</p><h3>{copy["finding3_title"]}</h3></article><div class="analysis-block"><h3>{copy["interactive_title"]}</h3><p>{copy["interactive1"]}</p>{overview_figure(en)}{scene_figure(en)}{fixed_figure(en)}<p>{copy["interactive2"]}</p></div><div class="analysis-block"><h3>{copy["discussion_title"]}</h3><h4>{copy["discussion1_title"]}</h4><p>{copy["discussion1"]}</p><h4>{copy["discussion2_title"]}</h4><p>{copy["discussion2"]}</p><h4>{copy["discussion3_title"]}</h4><p>{copy["discussion3"]}</p><figure id="figure-6"><img loading="lazy" src="assets/model_depth_error_five_views_m1_m4.png" alt="Model-depth error at five fixed evaluation views"><figcaption><span>Figure 6.</span> {"Model-depth error at the fixed-five check; teal marks missing or invalid predictions." if en else "固定 5 视角检查中的模型深度误差；青绿色表示缺失或无效预测。"}</figcaption></figure>{table(6)}{table(7)}</div>{office_case(en)}</section>
<section id="related-work"><p class="section-tag">05 / RELATED WORK</p><h2>{"From geometric measurement to editable Real2Sim" if en else "从几何测量到可编辑 Real2Sim"}</h2><p>{copy["positioning"]}</p><p>{"Our evaluation therefore spans both sides of the interface: upstream systems are judged as measurement pipelines, while the Blender outputs are judged as persistent spatial artifacts. This differs from evaluating pose, depth, or novel-view synthesis in isolation." if en else "因此，我们的评测同时覆盖接口两端：上游系统作为测量管线接受检验，Blender 输出则作为持久化空间产物接受检验；这不同于孤立地评估位姿、深度或新视角合成。"}</p>{related_links}</section>
<section id="limitations"><p class="section-tag">06 / LIMITATIONS</p><h2>{copy["limits_title"]}</h2><ul class="limits-list">{limits}</ul><p>{copy["evidence"]}</p>{downloads()}<p class="evidence-links"><a href="data/tables_1_7.json">Tables JSON</a> · <a href="data/scene_comparison.json">Scene manifest</a> · <a href="data/fixed_views.json">Fixed views</a> · <a href="evidence/publication_manifest.json">Publication manifest</a> · <a href="evidence/SHA256SUMS">SHA256</a></p></section>
<section id="citation"><p class="section-tag">07 / CITATION</p><h2>{"Cite this work" if en else "引用本文"}</h2><p>{"If this controlled study, its frozen assets, or its evaluation protocol supports your work, please cite the interactive article below." if en else "如果本研究的受控实验、冻结资产或评测协议对你的工作有帮助，请引用下面的交互式研究文章。"}</p><pre class="citation-block"><code>{citation}</code></pre></section>
<section id="references"><p class="section-tag">08 / REFERENCES</p><h2>{"References" if en else "参考文献"}</h2><ol class="references-list">{reference_list}</ol></section><noscript>JavaScript is required for tables and interactive figures.</noscript></main></div><footer>Agentic World · frozen evidence, editable outputs · <a href="{other}">{"中文" if en else "English"}</a></footer></body></html>'''


    return editorial_page(page, en)


README='''# Agentic World Simulation and Mapping

Bilingual static research journal rebuilt from frozen local sources. Figure 3 uses one local Three.js renderer/camera/full viewport for split comparison of M1–M4 with GT. Figure 4 switches among 25 hash-verified source images. All viewer dependencies are local, with no CDN.

The build copies the unchanged `scene.glb`/`scene.blend` pairs, downloads and verifies `GT.glb`, copies five local Three.js modules, applies registrations only at runtime, and records provenance in `data/scene_comparison.json`.

```bash
python scripts/build.py --source ../world_lobby_four_trajectory_20260929
python scripts/validate.py
python -m http.server 8765
python scripts/browser_qa.py --url http://127.0.0.1:8765/
```
'''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    source=ap.parse_args().source.resolve(); clean()
    table_src=source/TABLE_SOURCE; tables=json.loads(table_src.read_text())
    if list(tables["tables"]) != [f"table{i}" for i in range(1,8)]: raise ValueError("exactly table1..table7 required")
    for key,rows in tables["tables"].items():
        if [r["method"] for r in rows] != list(METHODS): raise ValueError(f"{key}: exactly M1..M4 required")
    assets={}
    for name in ("figure14_abc.png","fixed_five_view_comparison_m1_m4.jpg","model_depth_error_five_views_m1_m4.png"):
        rel=f"astra_blender2/report/space/assets/{name}"; assets[f"assets/{name}"]=copy_checked(source/rel,ROOT/f"assets/{name}",source_label=rel)
    teaser_rel="teaser_originals.png"
    assets["assets/teaser_originals.png"]=copy_checked(source/teaser_rel,ROOT/"assets/teaser_originals.png",source_label=teaser_rel)
    models={}
    for method in METHODS:
        models[method]={}
        for ext in ("glb","blend"):
            rel=f"astra_blender/models/{method}/scene.{ext}"; models[method][ext]=copy_checked(source/rel,ROOT/f"models/{method}/scene.{ext}",source_label=rel)
        dump(ROOT/f"evidence/{method}/manifest.json",{"schema_version":2,"method":method,"files":models[method],"table_rows":{k:next(r for r in v if r["method"]==method) for k,v in tables["tables"].items()}})
    gt=download_gt()
    vendor={}
    for rel in ("three.module.js","three.core.js","loaders/GLTFLoader.js","controls/OrbitControls.js","environments/RoomEnvironment.js","utils/BufferGeometryUtils.js"):
        label=(REFERENCE/"vendor/three"/rel).relative_to(ROOT.parent).as_posix()
        vendor[rel]=copy_checked(REFERENCE/"vendor/three"/rel,ROOT/"vendor/three"/rel,source_label=label)
    c=[[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]]; ci=[[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]
    scene_models={"GT":{"url":"assets/comparison/GT.glb","sha256":GT_SHA,"bytes":GT_BYTES,"registration":"identity"}}
    registrations={}
    for method in METHODS:
        if method=="M4":
            blender=[[1 if i==j else 0 for j in range(4)] for i in range(4)]
            src={"path":None,"sha256":None,"transform_direction":"GT_from_model","rule":"identity_world; source GLB retains Blender Z-up axes"}
            gltf=c
            formula="C (axis conversion only; GT_from_model is identity)"
        else:
            rel=f"{REG_DIR}/registration_{method}.json"; p=source/rel; reg=json.loads(p.read_text())
            if reg.get("transform_direction")!="GT_from_model": raise ValueError(f"{method}: wrong direction")
            blender=reg["transform"]; src={"path":rel,"sha256":sha(p),"transform_direction":"GT_from_model","status":reg.get("status"),"scope":reg.get("scope"),"limitations":reg.get("limitations")}
            gltf=mm(mm(c,blender),ci)
            formula="C * GT_from_model * C^-1"
        registrations[method]={"source":src,"GT_from_model_blender_z_up":blender,"runtime_matrix_gltf_y_up":gltf,"formula":formula,"diagnostic_caveat":("M1 only: GT-assisted Sim(3) from five manual camera associations; diagnostic only; not native metric recovery." if method=="M1" else None)}
        scene_models[method]={"url":f"models/{method}/scene.glb","sha256":models[method]["glb"]["sha256"],"bytes":models[method]["glb"]["bytes"],"runtime_matrix_gltf_y_up":gltf,"source_registration":src["path"]}
    dump(ROOT/"data/scene_comparison.json",{"schema_version":2,"models":scene_models,"camera":{"target":[18,1.2,-21],"position":[24,23,-5],"fov":42,"near":.05,"far":500},"coordinate_conversion":{"reason":"glTF is Y-up while registration is Blender Z-up","C_mapping":"[x,y,z] -> [x,z,-y]","C":c,"C_inverse":ci,"runtime_formula":"C * T * C^-1"},"registrations":registrations,"display_cutaway":{"scope":"runtime display only; frozen GLB/Blend bytes remain unchanged","hide_name_pattern":"ceiling|roof|wall|facade","keep_name_pattern":"emblem|art|grass|metal","applies_to":list(METHODS),"gt_asset":"already exported as a cutaway display model"},"immutability":"Display copies and runtime registration do not alter frozen source GLB bytes.","m1_diagnostic_caveat":"M1 registration is diagnostic only and is not native metric recovery.","gt_asset":gt})
    view_src=source/VIEW_SOURCE; inputs=json.loads(view_src.read_text())["rgb_figure"]["inputs"]
    if len(inputs)!=25: raise ValueError("fixed-view input count is not 25")
    fixed=[]
    for item in inputs:
        if item["method"] not in (*METHODS,"GT") or item["frame"] not in FRAMES: raise ValueError(item)
        source_path=Path(item["path"])
        source_label=source_path.relative_to(ROOT.parent).as_posix()
        copied=copy_checked(source_path,ROOT/f"assets/fixed_views/{item['method']}/{item['frame']:03d}.png",item["sha256"],source_label=source_label)
        fixed.append({"method":item["method"],"frame":item["frame"],"source":source_label,"published":copied["published"],"sha256":item["sha256"],"bytes":copied["bytes"]})
    if {(x["method"],x["frame"]) for x in fixed}!={(m,f) for m in (*METHODS,"GT") for f in FRAMES}: raise ValueError("fixed-view matrix incomplete")
    dump(ROOT/"data/fixed_views.json",{"schema_version":1,"source_manifest":VIEW_SOURCE,"source_manifest_sha256":sha(view_src),"frames":list(FRAMES),"methods":[*METHODS,"GT"],"images":fixed})
    (ROOT/"data").mkdir(parents=True,exist_ok=True); shutil.copy2(table_src,ROOT/"data/tables_1_7.json")
    dump(ROOT/"data/source_contract.json",{"schema_version":2,"old_site_baseline":"ae69dbe","source_root_name":source.name,"table_source":{"path":TABLE_SOURCE,"sha256":sha(table_src),"published_url":"data/tables_1_7.json"},"figures":assets,"models":models,"gt_asset":gt,"fixed_views_manifest":"data/fixed_views.json","scene_comparison_manifest":"data/scene_comparison.json","office_cafe_case_study":{"office_cafe":{"source_url":OFFICE_URL,"presentation":"local_models_and_synchronized_original_videos","included_assets":["original_model","legacy_model","input_video","procedural_model_video","scan_video","strong_shake"],"video_manifest":"data/office_video_media.json"}},"vendor":vendor,"tables":[{"number":i,"key":f"table{i}","methods":list(METHODS),"columns":list(tables["tables"][f"table{i}"][0]),"url":f"index.html#table-{i}","english_url":f"en.html#table-{i}"} for i in range(1,8)],"presentation":{"table2_hidden_columns":["alignment"],"table3_hidden_columns":["model_sha256","alignment"],"figure1_layout":"single supplied teaser image","metric_best_values":"bold, raw-value comparison"},"protocols":tables["protocols"],"m1_notice":tables["m1_notice"]})
    academic_style=r'''#figure-5,#figure-6{width:100%;margin:30px 0}#figure-5>img,#figure-6>img{width:100%;background:var(--paper)}main h3{font-family:Georgia,"Noto Serif CJK SC",serif;font-size:23px;font-weight:500;line-height:1.4;margin:32px 0 10px}main h4{font:500 18px/1.45 Georgia,"Noto Serif CJK SC",serif;margin:28px 0 8px}.tldr{margin:0 0 34px;padding:20px 24px;border-left:4px solid var(--green);background:#edf3ee}.tldr strong{font-size:11px;letter-spacing:.16em;color:var(--green)}.tldr p{margin:5px 0 0;font:500 19px/1.65 Georgia,"Noto Serif CJK SC",serif}.contributions{padding-left:24px}.contributions li{margin:10px 0;padding-left:5px}.inline-sources{display:block;margin-top:12px;font-size:13px}.workflow-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;margin:22px 0 34px;border:1px solid var(--line);background:var(--line)}.workflow-strip div{display:flex;min-height:180px;padding:18px 15px;background:var(--white);flex-direction:column}.workflow-strip strong{margin-bottom:14px;font-size:12px;letter-spacing:.08em;color:var(--green)}.workflow-strip span{font-size:13px;line-height:1.6;color:var(--muted)}.insight-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;margin:34px 0 12px;background:var(--line);border:1px solid var(--line)}.insight-strip div{display:flex;min-height:125px;padding:22px 18px;background:var(--white);flex-direction:column;justify-content:space-between}.insight-strip strong{font:500 25px/1.15 Georgia,serif;color:var(--green);letter-spacing:-.02em}.insight-strip span{font-size:11px;line-height:1.45;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}.metric-caveat{margin:8px 0 0;color:var(--muted);font-size:12px}.claim{margin:30px 0;padding:20px 24px;border:1px solid var(--line);background:var(--white)}.claim strong,.finding-kicker{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--green)}.claim p{margin:8px 0 0;font:500 21px/1.55 Georgia,"Noto Serif CJK SC",serif}.finding{margin:42px 0 18px;padding:0 0 22px;border-bottom:1px solid var(--line)}.finding h3{margin:5px 0 12px}.finding p:last-child{margin-bottom:0}.analysis-block{margin-top:58px;padding-top:12px;border-top:1px solid var(--line)}.external-case{margin-bottom:10px}.limits-list{padding-left:22px}.limits-list li{margin:10px 0}.evidence-links{font-size:12px;margin-top:25px}.citation-block{overflow:auto;margin:22px 0;padding:22px;border:1px solid var(--line);background:var(--white);font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace}.references-list{padding-left:24px}.references-list li{margin:13px 0;padding-left:6px}.references-list a{color:var(--ink)}@media(max-width:900px){.workflow-strip{grid-template-columns:1fr 1fr}.workflow-strip div{min-height:130px}}@media(max-width:700px){.insight-strip,.workflow-strip{grid-template-columns:1fr}.insight-strip div{min-height:98px}.workflow-strip div{min-height:auto}.claim p{font-size:18px}.tldr{padding:17px 19px}.tldr p{font-size:17px}.citation-block{padding:15px;font-size:11px}}'''
    eager_preload='const fixedPreloads=[];for(const m of ["M1","M2","M3","M4","GT"])for(const f of [0,36,72,108,144]){const image=new Image();image.src=`assets/fixed_views/${m}/${String(f).padStart(3,"0")}.png`;fixedPreloads.push(image)}'
    controls='const method=document.querySelector("#compare-method"),frame=document.querySelector("#compare-frame");'
    if eager_preload not in APP or controls not in APP: raise ValueError("Figure 4 app template changed")
    app_source=APP.replace(eager_preload,"").replace(controls,controls+"method.disabled=false;frame.disabled=false;")
    write(ROOT/"style.css",STYLE+academic_style+"\n"); write(ROOT/"app.js",app_source+"\n"); write(ROOT/"scene-compare.js",SCENE_JS+"\n"); write(ROOT/"index.html",academic_page()+"\n"); write(ROOT/"en.html",academic_page(True)+"\n"); write(ROOT/"README.md",README); write(ROOT/"requirements.txt","playwright>=1.40,<2\n"); write(ROOT/".gitignore","__pycache__/\nqa/\n.venv/\n.publication.json\n"); (ROOT/".nojekyll").touch()
    files=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] in (".git","scripts") or rel.name in ("SHA256SUMS","publication_manifest.json") or (len(rel.parts)==1 and rel.name.startswith("office-") and rel.suffix==".mp4") or rel.as_posix() in ("README.md","requirements.txt",".gitignore"): continue
        files.append({"path":rel.as_posix(),"sha256":sha(p),"bytes":p.stat().st_size})
    dump(ROOT/"evidence/publication_manifest.json",{"schema_version":2,"source_contract":"data/source_contract.json","files":files})
    sums=[f'{sha(ROOT/r["path"])}  {r["path"]}' for r in files]; sums.append(f'{sha(ROOT/"evidence/publication_manifest.json")}  evidence/publication_manifest.json'); write(ROOT/"evidence/SHA256SUMS","\n".join(sums)+"\n")
    print(json.dumps({"status":"BUILT","tables":7,"models":4,"fixed_views":25,"files":len(files)}))
if __name__=="__main__": main()
