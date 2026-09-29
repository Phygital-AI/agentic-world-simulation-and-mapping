<div class="opening"><span class="section-kicker">THE FINDING</span><p>轨迹估计更准确，后续深度就一定更准确吗？这轮实验给出的答案是：<strong>还不够。</strong>从相机运动到米制深度，再到可编辑的场景程序，每一次表示转换都需要独立验证。</p></div>

<div class="number-strip"><div><strong>0.1205<span> m</span></strong><p>ORB-SLAM3 · 最低轨迹 ATE</p></div><div><strong>21.62<span>%</span></strong><p>ViPE + DA3 · 500 帧 AbsRel</p></div><div><strong>180 + 500</strong><p>建模输入 / 非重叠深度评测帧</p></div></div>

## 我们希望地图最终能做什么？ {#question}

一张地图可以告诉机器人“哪里有表面”。一个场景程序还能表达“这里是一张桌子，它由桌面和支腿组成，旁边留有可通行空间”。对象、关系、材质与碰撞表示可以共同支持修改、渲染、查询和任务执行。

[上一轮 Astra × Blender 博客](https://wentingw.github.io/astra-world-model-blog/#_2)探索了这一入口：由视觉与几何观测驱动 agent 编写 Blender 程序，将场景转成可操作的对象。新一轮沿用这个问题，重新检查其几何基础：**相机是否定位准确？深度是否保持米制尺度？这些观测能否支撑可信的场景程序？**

本文使用 2026 年 9 月 29 日的新会话与 9 月 30 日完成的深度结果。已完成的是轨迹对比、DA3 深度评测和建模输入核验。四组 Astra / Blender 模型仍在制作，尚无本轮冻结模型及其独立 GT 评分，因此本文报告到建模输入这一阶段。旧文的模型、TSDF、外观与机器人成功率不作为本轮结果。

## 从同一段观测出发 {#protocol}

新会话长约 **179.92 秒**，包含 **4,499 张 RGB** 和 **44,999 个 IMU 样本**，相机 / IMU 频率为 25 / 250 Hz。原图 1280 × 960，公共针孔内参为 `fx = fy = 762.8, cx = 640, cy = 480`。这是一段仿真大厅采集，不能代替实景或跨场景验证。

轨迹图包含 GT、ORB-SLAM3、ViPE default 和 OpenVINS。三个估计器在 **4,254 个精确匹配的原生时间戳**上统一评分，源帧为 245–4498；缺失位姿不插值、不外推。每条估计轨迹仅拟合一次全局 SE(3)，缩放固定为 1。

<div class="pipeline" role="img" aria-label="同一 RGB 与 IMU 会话经过轨迹估计、DA3 深度预测、输入核验，进入尚未完成的 Astra Blender 建模与冻结后评测"><div><small>01 · CAPTURE</small><b>RGB + IMU</b><span>4,499 原生图像</span></div><i>→</i><div><small>02 · MEASURE</small><b>轨迹 → DA3</b><span>180 / 500 独立分组</span></div><i>→</i><div><small>03 · BUILD</small><b>Astra → Blender</b><span>净化输入已就绪</span></div><i>→</i><div class="pending"><small>04 · VERIFY</small><b>冻结后 GT 评测</b><span>模型完成后执行</span></div></div>

### 四条轨迹，不等于四个建模方法

轨迹诊断集合与 M1–M4 的定义需要分开阅读。**OpenVINS 仅参加轨迹对比；M1 是纯视觉路线。** 历史 M3 的 OpenVINS + MapAnything 已替换为 ORB-SLAM3 + DA3，M2–M4 的建模深度统一采用 DA3-GIANT。

| 路线 | 提供给 Astra 的观测 | 尺度与本轮状态 |
|---|---|---|
| M1 · RGB-only + Astra | 相同 180 张 RGB、帧身份、公共内参 | 无外部位姿 / 深度；尺度为假设；输入已核验 |
| M2 · ViPE + DA3 + Astra | 180 RGB + ViPE 原生位姿 + 对应 DA3 深度 | 保留原生米制尺度；深度与输入包完成 |
| M3 · ORB-SLAM3 + DA3 + Astra | 180 RGB + ORB-SLAM3 原生位姿 + 对应 DA3 深度 | 保留原生米制尺度；深度与输入包完成 |
| M4 · GT pose + DA3 + Astra | 180 RGB + 允许的 GT 相机位姿 + 对应 DA3 深度 | 仅提供 GT 相机，不提供 GT 深度 / 场景几何；输入包完成 |

180 张建模帧从共同有效区间均匀选取；500 张深度评测帧从剩余帧中确定性选取，两者交集为零。两组分别构建推理窗口。**500 帧的 RGB 本身会输入 DA3 进行深度预测**，所以它衡量非建模帧上的深度估计，不是冻结 Blender 模型的未见视角渲染能力，也不是新场景泛化。

## 轨迹：ORB-SLAM3 最准，但尺度仍值得检查 {#trajectory}

<p class="table-caption">TABLE 1 · 相同 4,254 时间戳的轨迹误差；覆盖率以全部 4,499 帧为分母</p>

{{POSE_TABLE}}

ORB-SLAM3 的主指标 ATE RMSE 为 **0.1205 m**，低于 ViPE 的 **0.1668 m** 和 OpenVINS 的 **0.6721 m**。覆盖率则是另一件事：ORB-SLAM3 缺少开头 245 帧，而 ViPE 覆盖全部原生帧。主误差表在共同帧上比较精度，覆盖率保留整个会话的输出完整性。

<figure class="wide"><img src="assets/trajectory_comparison.png" width="2880" height="1980" loading="lazy" alt="本轮四条轨迹与三个估计器的逐帧平移、旋转误差"><figcaption><span>02 / TRAJECTORY</span> 同一次全局刚体配准下的轨迹与误差曲线。GT 是参考轨迹。</figcaption></figure>

<div class="interactive-panel" id="trajectory-explorer"><div class="panel-heading"><div><span class="section-kicker">EXPLORE THE PATH</span><h3>切换轨迹投影</h3></div><label>坐标平面 <select id="projection"><option value="0,1">X / Y</option><option value="0,2">X / Z</option><option value="1,2">Y / Z</option></select></label></div><div class="legend"><span style="--swatch:#253a45">GT</span><span style="--swatch:#d37646">ORB-SLAM3</span><span style="--swatch:#247978">ViPE</span><span style="--swatch:#8174ad">OpenVINS</span></div><svg id="trajectory-svg" viewBox="0 0 760 360" role="img" aria-label="轨迹投影，单位米"></svg><p class="fine">展示每 8 帧抽取一点并保留末帧；所有轨迹共用坐标与等比例坐标轴。评分仍使用完整 4,254 帧。</p><noscript>启用 JavaScript 可切换投影；上方静态图保留完整结果。</noscript></div>

SE(3) 只改变方向和位置，不能修正尺度；Sim(3) 额外允许统一缩放。诊断性缩放后，三者 ATE 分别降到 **0.0259 / 0.0283 / 0.0580 m**。这说明全局尺度分量能够解释相当一部分位置误差，但 Sim(3) 使用 GT 拟合，不能作为原生米制精度。尤其 OpenVINS 的缩放为 0.885078，偏离 1 较多。

这也是新结果需要单独报告的原因：本轮采集、轨迹与采样协议均已改变，不能把旧会话的 OpenVINS 失败数值当作这次结果，也不能通过跨会话数值差异宣称某个单独改动的因果收益。

## 深度：更好的位姿没有自动带来更好的结果 {#depth}

三条深度路线共享 **DA3-GIANT、4 视图窗口、2 帧重叠、392 处理分辨率**，并启用 `align_to_input_ext_scale=True`。M2 / M3 使用未经 GT 对齐的原生轨迹；M4 使用 GT 相机位姿。重叠帧保留窗口中心性最高的观测，平局选较早窗口。

评测以 Blender BVH 从 GT 场景直接射线求交得到 **camera optical-Z**，即相机前向轴深度。它与沿射线的欧氏距离不同。每帧固定 160 × 120 网格，共 19,200 条射线；按处理后内参将预测深度映射到同一组原图射线并双线性采样。

<div class="interactive-panel" id="depth-explorer"><div class="panel-heading"><div><span class="section-kicker">READ THE MEASUREMENTS</span><h3>同一指标，切换采样集合</h3></div></div><div class="controls"><div class="segmented" role="group" aria-label="深度评测集合"><button type="button" data-split="modeling_180" aria-pressed="false">180 建模帧</button><button type="button" data-split="eval_500" aria-pressed="true">500 评测帧</button></div><label>指标 <select id="depth-metric"><option value="absrel">AbsRel ↓</option><option value="rmse_m">RMSE (m) ↓</option><option value="missing_penalty_mae_m">缺失惩罚 MAE (m) ↓</option><option value="valid_coverage">覆盖率 ↑</option><option value="delta1">δ1 ↑</option></select></label></div><div id="depth-bars" aria-live="polite"></div><p class="fine" id="depth-chart-note">主结果不进行 GT 尺度拟合。</p><noscript>完整数值见下方静态表格。</noscript></div>

<p class="table-caption">TABLE 2 · 180 张建模输入帧的原生 DA3 深度；无 GT 尺度拟合</p>

{{DEPTH_180}}

<p class="table-caption">TABLE 3 · 500 张非建模帧的原生 DA3 深度；无 GT 尺度拟合</p>

{{DEPTH_500}}

500 帧上，M2 的 RMSE / AbsRel 为 **2.8562 m / 21.62%**，M3 为 **3.2678 m / 25.82%**，M4 为 **2.9699 m / 21.95%**。M4 的 δ1 最高，但覆盖率最低；M2 的缺失惩罚 MAE 最低。**“哪条路线最好”必须连同指标与有效域一起说明。** M1 没有原生深度，故不出现在这些表里。

### 覆盖率与误差必须一起读

固定 GT 域为有限且在 `[0.1, 30] m` 内的 optical-Z。当前评测实现也要求预测值有限、处于 `[0.1, 30] m` 且通过采样有效性检查，才计为可用；范围外预测计入缺失。MAE、RMSE、AbsRel 与 δ 指标计算在双方有效交集上。覆盖率分母始终保留全部有效 GT 射线，180 / 500 组分别为 3,456,000 / 9,600,000 个位置。

缺失惩罚 MAE 在固定 GT 域上计算：有预测时取绝对误差，无预测时计 30 m。AbsRel 是 `mean(|ẑ − z| / z)`；δ1 是 `max(ẑ/z, z/ẑ) < 1.25` 的比例。表格聚合全部有效像素，**不是逐帧 RMSE 的平均**。覆盖率高只说明有可用预测，不说明几何正确。

<figure><img src="assets/depth_distribution.svg" width="1200" height="400" loading="lazy" alt="500 帧逐帧 AbsRel 与累积分布，三种方法均有局部误差峰值"><figcaption><span>03 / DISTRIBUTION</span> 逐帧误差保留局部失败；累积分布以全部 500 帧为分母。M4 的采样 37、38 没有有效预测，未画成零误差。</figcaption></figure>

原始报告还包含按帧配对 bootstrap（2,000 次，seed=20260930）。500 帧逐帧 AbsRel 差值 M2−M3 的均值为 −4.58 个百分点，95% 区间为 [−6.28, −2.97]；M2−M4 在双方可比较的 498 帧上为 −2.09 个百分点，区间 [−3.83, −0.72]。这里平均的是**逐帧差值**，与表 3 的像素聚合差值不同。连续视频帧有相关性，这些区间只是本会话帧间变化的诊断，不能解释为独立重复实验或跨场景置信度。

## 尺度诊断：形状接近，不代表米制深度可靠 {#scale}

如果用 GT 为每帧拟合一个中值缩放，500 帧的 RMSE 会降至约 0.54 m，AbsRel 降至约 3%。三条路线在这项诊断下非常接近。

<p class="table-caption">TABLE 4 · 500 帧的 GT 辅助逐帧尺度诊断；不参与主排序</p>

{{DIAGNOSTIC_TABLE}}

这是局部尺度不稳定的重要线索，但诊断中使用了 GT，缩放系数的 P05–P95 范围也很宽。更要注意：评测程序在缩放后重新应用 `[0.1, 30] m` 有效性条件，覆盖率因此发生变化。**误差下降同时包含尺度校正与有效交集变化，不能据此把全部误差归因于某一种机制。**

GT 位姿提供了相机运动条件，并没有提供真实深度。DA3 的预测形状、局部基线、尺度对齐与有效性过滤仍会影响结果。ViPE 轨迹误差偶然补偿网络尺度偏差是一种可能解释；当前实验未独立验证这种因果解释，也不能据此认为估计位姿优于 GT。

还有一个具体边界条件：M4 的最后两个名义窗口相机中心完全静止。运行记录显示，窗口 247、248 使用同一评测集合内的锚帧 276 替换一个窗口帧，形成约 **14.54 m** 的非零基线。该回退没有读取 GT 深度，但改变了这两个窗口的视图组成，需要与常规四视图窗口一起披露。它与前述无有效预测的采样 37、38 是不同事件。

## 让几何测量进入场景程序 {#agentic}

这一轮最值得继续检验的问题，是 agent 能否把带误差和不确定性的观测变成可检查的对象。预定流程是：查看输入、测量与拆解对象，编写 `bpy` 从空场景创建模型，在固定输入视角渲染对照，再经独立审查、修订和冻结，最后才进入 GT 评分。

<blockquote><p>一个有名字的椅子模型可以被编辑；只有位置、尺寸、支撑与可通行空间也经过测量，它才可能成为可靠的任务环境。</p></blockquote>

本轮已完成四份方法专属输入包的准备与核验：**680 张 RGB 哈希、540 份建模几何**通过检查，180 / 500 集互斥。输入采用实体复制与方法专属上下文；审计明确记录没有操作系统强制的读取沙箱，不能把约定等同于完全隔离证明。

四组共同预算为最多 5 个完整场景版本、60 张视觉检查渲染，固定检查采样 0、45、90、135、179；M2–M4 最多 3 次全量输入深度检查。计划要求独立初审和最终复审，输出场景、对象、碰撞体、相机、测量与访问记录。**这些是建模契约，不是已经完成的产物数量。**

| 阶段 | 截至本次发布的证据 |
|---|---|
| 轨迹冻结与统一评测 | 完成；3 个估计器、4,254 共同时间戳 |
| DA3 深度与独立 GT 射线评测 | 完成；3 条路线 × (180 + 500) 帧 |
| Astra 输入包核验 | 完成；4 份方法专属输入包 |
| M1–M4 语义模型、最终审查与冻结 | 进行中；未发现四组完整冻结场景 |
| 模型深度 / 外观 / 下游任务 | 本轮尚无完成结果 |

后续评测会继续区分三种量：**原生 DA3 深度对 GT、冻结模型深度对 GT、模型对自身输入深度的一致性**。它们回答不同问题。逼近 DA3 不能自动证明逼近真实场景；物体有标签也不能代替语义对应准确率。

M2 / M3 的模型评测计划仅允许一次 scale=1 的全局刚体配准；M4 沿用 GT 相机坐标关系。M1 无外部米制尺度，若冻结相机足以配准，将单列为“GT 相机辅助 Sim(3) 后的形状诊断”，不与原生米制结果混排。未来 500 帧模型评测也仍然是同场景测试。

## 这轮实验改变了什么认识？ {#discussion}

**位姿、深度、场景和任务是连续的工程链条，但指标不会自动传递。** ORB-SLAM3 在当前轨迹主表领先，不意味着其 pose-conditioned 深度必然领先；GT 相机也没有绕过深度网络的尺度与缺失问题。

**可编辑性是表示能力，可信度需要逐层测量。** 场景程序的价值在于让对象与修改可检查。下一步应把尺度不确定性、低基线窗口和缺失区域保留下来，检验建模是否修正这些问题，或只是用看起来完整的几何掩盖它们。

本文提供的是单场景、单会话的工程证据。它尚未证明本轮场景建模完成、机器人任务成功或人工工作量下降。将这些问题逐一变成可复核的实验，才是从观测走向 agentic world 的下一步。

## 证据、版本与复现 {#evidence}

本页表格由冻结 JSON 自动生成，图表来自本轮数据；旧博客仅作为研究问题与文章组织的参考。发布目录保留选定原始证据的逐字节副本与 SHA256，不包含完整原始视频、全部深度数组或尚未完成的模型。

<div class="evidence-grid"><a href="data/summary.json"><b>统一数据</b><span>页面图表与汇总 JSON ↗</span></a><a href="evidence/evaluation/metrics.json"><b>轨迹报告</b><span>对齐、覆盖率、逐方法指标 ↗</span></a><a href="evidence/evaluation/depth/metrics/modeling_180/metrics.json"><b>180 帧深度</b><span>原生指标、逐帧与诊断 ↗</span></a><a href="evidence/evaluation/depth/metrics/eval_500/metrics.json"><b>500 帧深度</b><span>原生指标、配对差值与诊断 ↗</span></a><a href="evidence/astra_blender/provenance/input_audit.json"><b>输入审计</b><span>哈希核验、分组与隔离说明 ↗</span></a><a href="data/source_manifest.json"><b>来源清单</b><span>源路径、文件大小与 SHA256 ↗</span></a></div>

[轨迹逐帧 CSV](evidence/evaluation/per_frame_errors.csv) · [深度逐帧 CSV](evidence/evaluation/depth/metrics/eval_500/per_frame_metrics.csv) · [评测实现](evidence/code/evaluate_da3_depth.py) · [深度有效域与公式](evidence/code/depth_pipeline.py) · [建模契约](evidence/astra_blender/configs/run_contract.json) · [后续建模计划](evidence/plan_astra_blender.md) · [本地构建与发布说明](README.md)

方法背景：[ViPE](https://github.com/nv-tlabs/vipe) · [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) · [OpenVINS](https://docs.openvins.com/) · [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3) · [Blender Python API](https://docs.blender.org/api/current/)
