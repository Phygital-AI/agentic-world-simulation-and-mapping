#!/usr/bin/env python3
"""Build the article from frozen experiment reports; never modifies experiments."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import shutil
import sys

import markdown
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=ROOT.parent / 'world_lobby_four_trajectory_20260929')
args = parser.parse_args()
SOURCE = args.source.resolve()
for directory in ['assets', 'data', 'evidence']:
    (ROOT / directory).mkdir(exist_ok=True)

def read(path):
    return json.loads((SOURCE / path).read_text())

def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

pose = read('evaluation/metrics.json')
depth = {s: read(f'evaluation/depth/metrics/{s}/metrics.json') for s in ['modeling_180', 'eval_500']}
splits = {s: read(f'data/depth_samples/{s}.json') for s in depth}
assert len({f['source_index'] for f in splits['modeling_180']['frames']} & {f['source_index'] for f in splits['eval_500']['frames']}) == 0
assert pose['common_frames'] == 4254
assert all(d['status'] == 'COMPLETE' and not d['primary_scale_fit'] for d in depth.values())

files = ['evaluation/metrics.json', 'evaluation/REPORT.md', 'evaluation/per_frame_errors.csv',
         'verification.json', 'evaluation/depth/verification.json', 'data/depth_samples/summary.json',
         'data/depth_samples/modeling_180.json', 'data/depth_samples/eval_500.json',
         'astra_blender/provenance/input_audit.json', 'astra_blender/configs/run_contract.json',
         'contract.json', 'plan_astra_blender.md', 'plan_depth.md', 'COMMANDS.md',
         'code/depth_pipeline.py', 'code/evaluate_da3_depth.py', 'code/evaluate_and_plot.py',
         'code/run_da3_depth.py', 'code/prepare_depth_samples.py', 'code/generate_gt_depth_blender.py',
         'code/verify_depth_pipeline.py', 'code/verify_results.py', 'code/test_depth_pipeline.py']
for split in depth:
    files += [f'evaluation/depth/metrics/{split}/metrics.json', f'evaluation/depth/metrics/{split}/per_frame_metrics.csv']
for i in [247, 248]:
    files.append(f'depth/m4_gt/eval_500/windows/window_{i:04d}/manifest.json')
manifest = []
for name in files:
    src, dst = SOURCE / name, ROOT / 'evidence' / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    manifest.append({'source_relative_path': name, 'published_path': 'evidence/' + name,
                     'sha256': hashlib.sha256(src.read_bytes()).hexdigest(), 'bytes': src.stat().st_size})
for name in ['trajectory_comparison.png', 'figure14a_camera_trajectories.png']:
    shutil.copyfile(SOURCE / 'evaluation' / name, ROOT / 'assets' / name)

summary = {'snapshot_date': '2026-09-30', 'source_directory': SOURCE.name,
           'pose': pose, 'depth': {}, 'model_status': {}, 'source_manifest': manifest}
for split, d in depth.items():
    summary['depth'][split] = {k:v for k,v in d.items() if k not in ['methods', 'gt_cache']}
    summary['depth'][split]['methods'] = {
        k:{a:b for a,b in v.items() if a not in ['per_frame', 'prediction_manifest']} for k,v in d['methods'].items()}
for method in ['M1','M2','M3','M4']:
    p = SOURCE / 'astra_blender/models' / method
    summary['model_status'][method] = {'scene_blend_present': (p / 'scene.blend').is_file(),
        'scene_glb_present': (p / 'scene.glb').is_file(),
        'modelling_manifest_present': (p / 'modelling_manifest.json').is_file()}
if any(any(v.values()) for v in summary['model_status'].values()):
    sys.exit('Model artifacts have changed. Review article status before rebuilding this snapshot.')
dump('data/summary.json', summary)

z = np.load(SOURCE / 'evaluation/aligned_common_trajectories.npz')
take = np.unique(np.r_[np.arange(0,4254,8),4253])
dump('data/trajectories.json', {key: z[key][take].round(6).tolist() for key in z.files if key.endswith('position')})

# A source-image hero: every panel is from this session, without generated imagery.
indices = [0,45,90,135]
hero = Image.new('RGB',(1600,680),'#111d23')
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for col, index in enumerate(indices):
    frame = splits['modeling_180']['frames'][index]
    src = Image.open(frame['image']).convert('RGB')
    thumb = src.resize((800,600),Image.Resampling.LANCZOS)
    # Preserve full 4:3 frame, two-by-two grid.
    thumb = thumb.resize((800,600),Image.Resampling.LANCZOS)
    x, y = (col % 2)*800, (col // 2)*340
    thumb.thumbnail((780,292),Image.Resampling.LANCZOS)
    hero.paste(thumb,(x+(800-thumb.width)//2,y+8))
    ImageDraw.Draw(hero).text((x+20,y+310),f'RGB {index:03d} / source {frame["source_index"]:04d}',font=font,fill='#d5e1df')
hero.save(ROOT/'assets/hero.webp',quality=90)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
colors = {'M2':'#247978','M3':'#d37646','M4':'#8174ad'}
fig, axes = plt.subplots(1,2,figsize=(12,4.0),layout='constrained')
for method, color in colors.items():
    frames = depth['eval_500']['methods'][method]['per_frame']
    values = np.array([np.nan if f['absrel'] is None else f['absrel']*100 for f in frames])
    axes[0].plot(np.arange(500),values,label=method,color=color,linewidth=1,alpha=.85)
    finite = np.sort(values[np.isfinite(values)])
    axes[1].plot(finite,np.arange(1,len(finite)+1)/500*100,label=method,color=color,linewidth=2)
axes[0].set(xlabel='Evaluation sample index',ylabel='Per-frame AbsRel (%)',title='Errors vary sharply across frames')
axes[1].set(xlabel='Per-frame AbsRel (%)',ylabel='Share of all 500 frames (%)',title='Two M4 frames have no valid prediction',xscale='log')
for ax in axes:
    ax.grid(alpha=.16)
    ax.legend(frameon=False)
fig.savefig(ROOT/'assets/depth_distribution.svg')
fig.savefig(ROOT/'assets/depth_distribution.png',dpi=180)
plt.close(fig)

def pose_table(en):
    headers = ['Estimator','Coverage / 4,499','SE(3) ATE ↓ (m)','Rotation RMSE ↓ (°)','Sim(3) scale','Sim(3) ATE (m)'] if en else ['估计器','覆盖率 / 4,499','SE(3) ATE ↓ (m)','旋转 RMSE ↓ (°)','Sim(3) 缩放','Sim(3) ATE (m)']
    rows=[]
    for name,d in pose['methods'].items():
        rows.append([name,f'{100*d["coverage"]:.2f}%',f'{d["se3"]["translation_m"]["rmse"]:.4f}',f'{d["se3"]["rotation_deg"]["rmse"]:.4f}',f'{d["sim3_diagnostic"]["scale"]:.6f}',f'{d["sim3_diagnostic"]["translation_m"]["rmse"]:.4f}'])
    return table(headers,rows)

def table(headers,rows):
    return '<div class="table-scroll"><table><thead><tr>'+''.join('<th scope="col">'+html.escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+html.escape(str(v))+('</th>' if i==0 else '</td>') for i,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'

def depth_table(split,en):
    headers=['Method','MAE ↓ (m)','RMSE ↓ (m)','AbsRel ↓','δ1 ↑','Coverage ↑','Penalized MAE ↓ (m)'] if en else ['方法','MAE ↓ (m)','RMSE ↓ (m)','AbsRel ↓','δ1 ↑','覆盖率 ↑','缺失惩罚 MAE ↓ (m)']
    rows=[]
    for method,v in depth[split]['methods'].items():
        d=v['primary_no_scale_fit']
        rows.append([method,f'{d["mae_m"]:.4f}',f'{d["rmse_m"]:.4f}',f'{d["absrel"]*100:.2f}%',f'{d["delta1"]*100:.2f}%',f'{d["valid_coverage"]*100:.2f}%',f'{d["missing_penalty_mae_m"]:.4f}'])
    return table(headers,rows)

def diagnostic_table(en):
    rows=[]
    for method,v in depth['eval_500']['methods'].items():
        d=v['median_scale_diagnostic']; m=d['metrics']
        rows.append([method,f'{v["primary_no_scale_fit"]["rmse_m"]:.4f}',f'{m["rmse_m"]:.4f}',f'{m["absrel"]*100:.2f}%',f'{d["scale_p05"]:.3f} – {d["scale_p95"]:.3f}',f'{m["valid_coverage"]*100:.2f}%'])
    return table(['Method' if en else '方法','Native RMSE (m)' if en else '原生 RMSE (m)','GT-scaled RMSE (m)' if en else 'GT 校正后 RMSE (m)','GT-scaled AbsRel' if en else 'GT 校正后 AbsRel','Scale P05–P95' if en else '缩放系数 P05–P95','Coverage' if en else '校正后覆盖率'],rows)

for lang in ['zh','en']:
    en=lang=='en'
    text=(ROOT/f'content/article.{lang}.md').read_text()
    for token,value in {'{{POSE_TABLE}}':pose_table(en),'{{DEPTH_180}}':depth_table('modeling_180',en),'{{DEPTH_500}}':depth_table('eval_500',en),'{{DIAGNOSTIC_TABLE}}':diagnostic_table(en)}.items():
        text=text.replace(token,value)
    (ROOT/f'article.{lang}.md').write_text(text)
    article=markdown.markdown(text,extensions=['tables','fenced_code','toc','attr_list'],extension_configs={'toc':{'permalink':False}})
    title='When a map becomes a program' if en else '当地图成为程序'
    subtitle='Better poses are only the beginning.' if en else '更准的位姿，只是起点。'
    lead='Four camera trajectories, one depth model, and a measurable path toward editable worlds. A new World Lobby experiment.' if en else '四条相机轨迹，一个深度模型，以及通向可编辑世界的可测量路径。World Lobby 新一轮实验。'
    nav=[('question','Question' if en else '问题'),('protocol','Protocol' if en else '实验'),('trajectory','Trajectory' if en else '轨迹'),('depth','Depth' if en else '深度'),('agentic','Agentic world' if en else '场景程序'),('evidence','Evidence' if en else '证据')]
    page=f'''<!doctype html>
<html lang="{'en' if en else 'zh-CN'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Agentic World</title><meta name="description" content="{lead}"><meta name="theme-color" content="#f5f3ed">
<meta property="og:title" content="{title} · {subtitle}"><meta property="og:description" content="{lead}"><meta property="og:type" content="article"><meta property="og:image" content="https://wentingw.github.io/agentic-world-blog/assets/hero.webp">
<link rel="canonical" href="https://wentingw.github.io/agentic-world-blog/{'en.html' if en else ''}"><link rel="alternate" hreflang="zh" href="index.html"><link rel="alternate" hreflang="en" href="en.html">
<link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head><body data-lang="{lang}">
<a class="skip" href="#article">{'Skip to article' if en else '跳到正文'}</a><div class="progress" aria-hidden="true"></div>
<nav class="topbar"><a class="brand" href="index.html"><span class="brand-mark">a/w</span> AGENTIC WORLD</a><div class="nav-right"><a href="index.html" {'aria-current="page"' if not en else ''}>中文</a><a href="en.html" {'aria-current="page"' if en else ''}>EN</a><a href="https://github.com/wentingw/agentic-world-blog">GitHub ↗</a></div></nav>
<header class="hero-heading"><p class="eyebrow">RESEARCH JOURNAL &nbsp; / &nbsp; 30 SEPTEMBER 2026 &nbsp; / &nbsp; 01</p><h1>{title}</h1><p class="hero-subtitle">{subtitle}</p><p class="lead">{lead}</p><div class="tags"><span>WORLD LOBBY</span><span>POSE → DEPTH → PROGRAM</span><span>{'Pose & depth results' if en else '轨迹与深度实测'}</span></div></header>
<figure class="hero-figure"><img src="assets/hero.webp" width="1600" height="680" alt="{'Four actual RGB frames from the new World Lobby capture' if en else '本轮 World Lobby 采集中的四张原始 RGB 图像'}"><figcaption><span>01 / OBSERVATION</span> {'Input RGB, modelling samples 0, 45, 90 and 135. All figures in this article use the new session.' if en else '原始 RGB，建模采样序号 0、45、90、135。本文图表均来自新会话。'}</figcaption></figure>
<div class="article-layout"><aside class="toc"><p>IN THIS NOTE</p>{''.join(f'<a href="#{anchor}">{label}</a>' for anchor,label in nav)}<a class="download" href="article.{lang}.md">Markdown ↓</a></aside><main id="article">{article}</main></div>
<footer><div class="brand">AGENTIC WORLD</div><p>{'An engineering experiment, with its measurements and limits intact.' if en else '保留测量、失败与适用边界的一次工程实验。'}</p><div><a href="https://wentingw.github.io/astra-world-model-blog/">{'Previous experiment' if en else '上一轮博客'} ↗</a><a href="data/summary.json">JSON ↗</a><a href="evidence/SHA256SUMS">SHA256 ↗</a><a href="README.md">{'Reproduce' if en else '复现说明'} ↗</a></div></footer></body></html>'''
    (ROOT/('en.html' if en else 'index.html')).write_text(page)

dump('data/source_manifest.json',manifest)
(ROOT/'evidence/SHA256SUMS').write_text(''.join(f'{r["sha256"]}  {r["published_path"].removeprefix("evidence/")}\n' for r in manifest))
(ROOT/'.nojekyll').touch()
print(json.dumps({'status':'BUILT','evidence_files':len(manifest),'source':SOURCE.name,'languages':['zh','en']}))
