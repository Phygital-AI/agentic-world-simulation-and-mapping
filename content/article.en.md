<div class="opening"><span class="section-kicker">THE FINDING</span><p>Do more accurate camera poses necessarily produce more accurate depth? This experiment says: <strong>there is another step to verify.</strong> Camera motion, metric depth and editable scene programs each need their own measurements.</p></div>

<div class="number-strip"><div><strong>0.1205<span> m</span></strong><p>ORB-SLAM3 · lowest trajectory ATE</p></div><div><strong>21.62<span>%</span></strong><p>ViPE + DA3 · 500-frame AbsRel</p></div><div><strong>180 + 500</strong><p>Modelling inputs / separate depth evaluation</p></div></div>

## What should a map be able to do? {#question}

A surface map describes where geometry lies. A scene program can also describe a table, its top and legs, and the space around it. Objects, relationships, materials and collision representations can support editing, rendering, queries and execution.

Our [previous Astra × Blender experiment](https://wentingw.github.io/astra-world-model-blog/en.html) explored an agent writing Blender programs from visual and geometric observations. This new run revisits the foundations: **Are the cameras accurate? Does depth retain metric scale? Are the observations reliable enough to support a scene program?**

This article uses the new capture from 29 September 2026 and the depth results completed on 30 September. Trajectory evaluation, DA3 depth evaluation and modelling input audits are complete. The four Astra / Blender scenes remain in progress, with no complete frozen scene set or independent model scores in this snapshot. The previous article's models, TSDF results, appearance scores and robot success rates are not results of this run.

## Start from the same observations {#protocol}

The new simulated lobby capture spans approximately **179.92 seconds**, with **4,499 RGB images** and **44,999 IMU samples**, at 25 / 250 Hz. Images are 1280 × 960 with shared pinhole intrinsics `fx = fy = 762.8, cx = 640, cy = 480`. This is one synthetic scene and session; it does not establish real-world or cross-scene performance.

We compare GT, ORB-SLAM3, ViPE default and OpenVINS trajectories. The three estimators are scored at **4,254 exact common native timestamps**, source frames 245–4498. Missing poses are neither interpolated nor extrapolated. Each estimated trajectory receives one global SE(3) alignment, with scale fixed to 1.

<div class="pipeline" role="img" aria-label="RGB and IMU capture to trajectories and DA3 depth, then audited inputs for ongoing Astra Blender modelling and future frozen model evaluation"><div><small>01 · CAPTURE</small><b>RGB + IMU</b><span>4,499 native images</span></div><i>→</i><div><small>02 · MEASURE</small><b>Pose → DA3</b><span>Separate 180 / 500 splits</span></div><i>→</i><div><small>03 · BUILD</small><b>Astra → Blender</b><span>Audited inputs ready</span></div><i>→</i><div class="pending"><small>04 · VERIFY</small><b>Frozen model → GT</b><span>Pending completed models</span></div></div>

### Four trajectories and four modelling routes are different sets

**OpenVINS participates only in trajectory diagnostics. M1 is the RGB-only route.** The historical M3, OpenVINS + MapAnything, is replaced by ORB-SLAM3 + DA3. Modelling depth for M2–M4 now uses the same DA3-GIANT model.

| Route | Observations provided to Astra | Scale and current status |
|---|---|---|
| M1 · RGB-only + Astra | Same 180 RGB frames, frame identity and shared intrinsics | No external poses or depth; assumed scale; inputs audited |
| M2 · ViPE + DA3 + Astra | 180 RGB, native ViPE poses and corresponding DA3 depth | Native metric scale; depth and input packet complete |
| M3 · ORB-SLAM3 + DA3 + Astra | 180 RGB, native ORB-SLAM3 poses and corresponding DA3 depth | Native metric scale; depth and input packet complete |
| M4 · GT pose + DA3 + Astra | 180 RGB, permitted GT camera poses and corresponding DA3 depth | GT cameras only, no GT depth or scene geometry; packet complete |

The 180 modelling frames are sampled uniformly from the common interval. Another 500 frames are selected deterministically from the remaining frames, with zero overlap. Inference windows are built separately. **DA3 observes the RGB images of the 500 evaluation frames themselves.** These results measure depth estimation on non-modelling frames, not novel-view rendering by a frozen Blender scene or generalization to a new scene.

## Trajectory: ORB-SLAM3 leads, with scale still visible {#trajectory}

<p class="table-caption">TABLE 1 · Errors on the same 4,254 timestamps; coverage uses all 4,499 frames</p>

{{POSE_TABLE}}

ORB-SLAM3 has the lowest primary ATE RMSE at **0.1205 m**, compared with **0.1668 m** for ViPE and **0.6721 m** for OpenVINS. Coverage answers a separate question: ORB-SLAM3 misses the first 245 frames, while ViPE covers the full sequence. Accuracy is compared on the common timestamps; coverage preserves full-session completeness.

<figure class="wide"><img src="assets/trajectory_comparison.png" width="2880" height="1980" loading="lazy" alt="Four trajectories with per-frame translation and rotation errors for the new session"><figcaption><span>02 / TRAJECTORY</span> Trajectories and errors after one global rigid alignment per estimator. GT is the reference.</figcaption></figure>

<div class="interactive-panel" id="trajectory-explorer"><div class="panel-heading"><div><span class="section-kicker">EXPLORE THE PATH</span><h3>Inspect another projection</h3></div><label>Coordinate plane <select id="projection"><option value="0,1">X / Y</option><option value="0,2">X / Z</option><option value="1,2">Y / Z</option></select></label></div><div class="legend"><span style="--swatch:#253a45">GT</span><span style="--swatch:#d37646">ORB-SLAM3</span><span style="--swatch:#247978">ViPE</span><span style="--swatch:#8174ad">OpenVINS</span></div><svg id="trajectory-svg" viewBox="0 0 760 360" role="img" aria-label="Trajectory projection in metres"></svg><p class="fine">Display samples every eighth frame and retains the final frame. Shared coordinates and equal axis scales; all 4,254 frames remain in the evaluation.</p><noscript>Enable JavaScript to switch projections; the static figure above retains the results.</noscript></div>

SE(3) changes rotation and translation, but not scale. Sim(3) additionally allows a uniform scale. Under that diagnostic, ATE drops to **0.0259 / 0.0283 / 0.0580 m**, respectively. A global scale component therefore explains a substantial part of the position error, but GT-fitted Sim(3) is not native metric accuracy. OpenVINS has the largest scale departure here, at 0.885078.

The capture, trajectories and sampling protocol differ from the previous experiment. Historical OpenVINS failure values do not describe this run, and differences across sessions cannot isolate the causal effect of a single change.

## Depth: better poses do not automatically win {#depth}

All three depth routes use **DA3-GIANT, four-view windows, two-frame overlap and processing resolution 392**, with `align_to_input_ext_scale=True`. M2 / M3 receive their native trajectories without GT alignment; M4 receives GT camera poses. Overlapping predictions are selected by maximum window centrality, breaking ties in favour of the earlier window.

Blender BVH ray casting against the GT scene provides **camera optical-Z**, the depth along the camera's forward axis, rather than Euclidean distance along a ray. Every frame uses a fixed 160 × 120 grid, or 19,200 rays. Predictions are mapped through their processed intrinsics and bilinearly sampled at the corresponding original-image rays.

<div class="interactive-panel" id="depth-explorer"><div class="panel-heading"><div><span class="section-kicker">READ THE MEASUREMENTS</span><h3>Switch the split and metric</h3></div></div><div class="controls"><div class="segmented" role="group" aria-label="Depth evaluation split"><button type="button" data-split="modeling_180" aria-pressed="false">180 modelling</button><button type="button" data-split="eval_500" aria-pressed="true">500 evaluation</button></div><label>Metric <select id="depth-metric"><option value="absrel">AbsRel ↓</option><option value="rmse_m">RMSE (m) ↓</option><option value="missing_penalty_mae_m">Penalized MAE (m) ↓</option><option value="valid_coverage">Coverage ↑</option><option value="delta1">δ1 ↑</option></select></label></div><div id="depth-bars" aria-live="polite"></div><p class="fine" id="depth-chart-note">Primary results use no GT scale fitting.</p><noscript>Complete values remain available in the static tables below.</noscript></div>

<p class="table-caption">TABLE 2 · Native DA3 depth on 180 modelling frames; no GT scale fitting</p>

{{DEPTH_180}}

<p class="table-caption">TABLE 3 · Native DA3 depth on 500 non-modelling frames; no GT scale fitting</p>

{{DEPTH_500}}

On 500 frames, RMSE / AbsRel are **2.8562 m / 21.62%** for M2, **3.2678 m / 25.82%** for M3, and **2.9699 m / 21.95%** for M4. M4 has the highest δ1 but the lowest coverage; M2 has the lowest penalized MAE. **A ranking needs its metric and validity domain.** M1 has no native depth, so it is absent from these tables.

### Read coverage with error

The fixed GT domain includes finite optical-Z in `[0.1, 30] m`. The implementation also requires predictions to be finite, inside `[0.1, 30] m` and supported by valid sampling; predictions outside this range count as missing. MAE, RMSE, AbsRel and δ scores use the jointly valid intersection. Coverage retains the full GT denominator: 3,456,000 / 9,600,000 positions for the 180 / 500 splits.

Penalized MAE uses the fixed GT domain: absolute error for valid predictions, 30 m for missing predictions. AbsRel is `mean(|ẑ − z| / z)`; δ1 is the fraction with `max(ẑ/z, z/ẑ) < 1.25`. Tables pool all valid pixels; **pooled RMSE is not the mean of per-frame RMSEs**. Coverage measures available output, not correct geometry.

<figure><img src="assets/depth_distribution.svg" width="1200" height="400" loading="lazy" alt="Per-frame AbsRel and cumulative distributions across 500 frames, showing local failures"><figcaption><span>03 / DISTRIBUTION</span> Per-frame errors retain local failures. The cumulative distribution uses all 500 frames as its denominator. M4 samples 37 and 38 have no valid predictions and are not plotted as zero error.</figcaption></figure>

The reports include paired frame bootstrap diagnostics: 2,000 repeats, seed 20260930. For 500-frame per-frame AbsRel, the mean M2−M3 difference is −4.58 percentage points, with a 95% interval [−6.28, −2.97]. M2−M4 uses 498 mutually comparable frames and gives −2.09 points, [−3.83, −0.72]. These average **frame-level differences**, unlike the pooled pixel scores in Table 3. Video frames are correlated; the intervals describe variation within this session, not independent experiment repetitions or cross-scene confidence.

## Scale diagnostics: similar shape is not reliable metric depth {#scale}

If each frame receives a GT-assisted median scale correction, 500-frame RMSE falls to approximately 0.54 m and AbsRel to approximately 3%. The three routes become very close in this diagnostic.

<p class="table-caption">TABLE 4 · GT-assisted per-frame scale diagnostic on 500 frames; excluded from primary ranking</p>

{{DIAGNOSTIC_TABLE}}

This is evidence consistent with unstable local scale, but the correction uses GT and the P05–P95 scale ranges are wide. The evaluator also reapplies the `[0.1, 30] m` prediction validity rule after scaling, changing coverage. **The improvement combines scale correction and a changed valid intersection; it cannot attribute every error to one mechanism.**

GT poses supply camera geometry, not true depth. Predicted shape, local baseline, scale alignment and validity filtering still affect the output. ViPE trajectory errors could partly compensate for depth scale bias, but this causal explanation has not been independently established; the results do not make estimated poses more correct than GT.

A concrete boundary case occurs in M4's final two nominal windows, whose camera centres are stationary. Windows 247 and 248 replace one view with anchor sample 276 from the same evaluation split, introducing approximately **14.54 m** of baseline. The fallback reads no GT depth, but changes the view composition and must be disclosed. This event is distinct from the invalid predictions at samples 37 and 38.

## Bring measurements into the scene program {#agentic}

The next question is whether an agent can turn imperfect observations into inspectable objects. The modelling contract calls for inspecting inputs, measuring and decomposing objects, writing `bpy` from an empty scene, rendering fixed input views, independent review, revision and freezing, followed by GT evaluation.

<blockquote><p>A named chair can be edited. Its position, dimensions, support and surrounding free space also need measurements before it can serve as a reliable task environment.</p></blockquote>

Four method-specific input packages have been prepared and audited: **680 RGB hashes and 540 modelling geometry files** passed checks, and the 180 / 500 splits are disjoint. Isolation uses physical copies and method-specific contexts. The audit explicitly records that there is no operating-system-enforced read sandbox; access rules alone are not proof of complete isolation.

The shared budget allows at most five complete scene versions and 60 visual check renders, using fixed sample indices 0, 45, 90, 135 and 179. M2–M4 allow up to three full input-depth checks. Initial and final independent reviews are required, alongside scene, object, collider, camera, measurement and access records. **These are contract limits, not completed output counts.**

| Stage | Evidence at this publication snapshot |
|---|---|
| Frozen trajectories and common evaluation | Complete; 3 estimators, 4,254 common timestamps |
| DA3 depth and independent GT ray evaluation | Complete; 3 routes × (180 + 500) frames |
| Astra input package audit | Complete; 4 method-specific packages |
| M1–M4 semantic scenes, final review and freeze | In progress; no complete frozen scene set found |
| Model depth, appearance and downstream tasks | No completed results for this run |

Future evaluation will keep three quantities separate: **native DA3 depth versus GT, frozen model depth versus GT, and model consistency with its own input depth**. Matching DA3 is not proof of matching the true scene; naming objects is not a semantic correspondence score.

The planned M2 / M3 model evaluation permits one global rigid alignment at scale 1. M4 retains its GT camera coordinate relationship. M1 has no external metric scale; if its frozen cameras support registration, it will be reported separately as a “GT-camera-assisted Sim(3) shape diagnostic.” Future model evaluation on 500 frames will still be a same-scene test.

## What does this run teach us? {#discussion}

**Pose, depth, scenes and tasks form an engineering chain, but accuracy does not transfer automatically.** ORB-SLAM3 leads the trajectory table without leading pose-conditioned depth. GT cameras do not bypass depth scale and missing-output problems.

**Editability is a representation capability; reliability needs measurements at every stage.** A scene program makes objects and revisions inspectable. The next experiment should preserve scale uncertainty, low-baseline windows and missing regions, then test whether modelling resolves those problems or covers them with plausible geometry.

This is evidence from one scene and one capture. It does not yet establish completed modelling, robot task success or reduced human effort for the new run. Those remain concrete questions for the next stage.

## Evidence, versions and reproduction {#evidence}

Tables are generated from frozen JSON, and figures use this run's data. The previous blog supplies the research context and editorial reference. Selected original evidence is copied byte for byte with SHA256 hashes. The site does not bundle the full video, all depth arrays or unfinished models.

<div class="evidence-grid"><a href="data/summary.json"><b>Unified data</b><span>Charts and summary JSON ↗</span></a><a href="evidence/evaluation/metrics.json"><b>Trajectory report</b><span>Alignment, coverage and metrics ↗</span></a><a href="evidence/evaluation/depth/metrics/modeling_180/metrics.json"><b>180-frame depth</b><span>Native, per-frame and diagnostic results ↗</span></a><a href="evidence/evaluation/depth/metrics/eval_500/metrics.json"><b>500-frame depth</b><span>Metrics and paired differences ↗</span></a><a href="evidence/astra_blender/provenance/input_audit.json"><b>Input audit</b><span>Hashes, splits and isolation limits ↗</span></a><a href="data/source_manifest.json"><b>Source manifest</b><span>Paths, sizes and SHA256 hashes ↗</span></a></div>

[Trajectory per-frame CSV](evidence/evaluation/per_frame_errors.csv) · [Depth per-frame CSV](evidence/evaluation/depth/metrics/eval_500/per_frame_metrics.csv) · [Evaluator](evidence/code/evaluate_da3_depth.py) · [Depth validity and formulas](evidence/code/depth_pipeline.py) · [Modelling contract](evidence/astra_blender/configs/run_contract.json) · [Modelling plan](evidence/plan_astra_blender.md) · [Build and publication instructions](README.md)

Method references: [ViPE](https://github.com/nv-tlabs/vipe) · [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) · [OpenVINS](https://docs.openvins.com/) · [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3) · [Blender Python API](https://docs.blender.org/api/current/)
