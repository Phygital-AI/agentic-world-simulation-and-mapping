"""Bilingual narrative and demo additions around the frozen research article."""

from hashlib import sha256
from pathlib import Path

SITE_TITLE = "AWSM: Agentic World Simulation and Mapping"
BASE_URL = "https://phygital-ai.github.io/agentic-world-simulation-and-mapping/"
BIBTEX = r"""@misc{awsm_2026,
  title        = {{AWSM}: Agentic World Simulation and Mapping},
  author       = {{Phygital AI}},
  year         = {2026},
  howpublished = {Interactive research article},
  url          = {https://phygital-ai.github.io/agentic-world-simulation-and-mapping/},
  note         = {Reconstruction benchmarks, editable scene assets, and map-based embodied demonstration}
}
"""

REFERENCES = [
    ("Qin et al. VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator. TRO, 2018.", "https://arxiv.org/abs/1708.03852"),
    ("Keetha et al. MapAnything: Universal Feed-Forward Metric 3D Reconstruction. 2025.", "https://arxiv.org/abs/2509.13414"),
    ("Zhou et al. Memory Over Maps: 3D Object Localization Without Reconstruction. 2026.", "https://arxiv.org/abs/2603.20530"),
    ("Yang et al. 3D-Mem: 3D Scene Memory for Embodied Exploration and Reasoning. 2024.", "https://arxiv.org/abs/2411.17735"),
    ("Khanna et al. GOAT-Bench: A Benchmark for Multi-Modal Lifelong Navigation. CVPR, 2024.", "https://arxiv.org/abs/2404.06609"),
    ("ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning. ICRA, 2024.", "https://arxiv.org/abs/2309.16650"),
    ("Clio: Real-time Task-Driven Open-Set 3D Scene Graphs. RA-L, 2024.", "https://arxiv.org/abs/2404.13696"),
]


def narrative_copy(copy, en):
    if en:
        copy.update({
            "tldr": "Large-model agents can build editable 3D scenes from visual observations, but plausible appearance does not guarantee spatial fidelity. AWSM explores grounding this reconstruction process in geometric evidence so the resulting scenes can serve as maps and simulation assets. Four reconstruction routes test scene fidelity; a multi-robot demo illustrates map-based execution. Next steps are higher efficiency and accuracy, reusable simulation-ready scene generation, and deeper integration with phygital agents—toward persistent spatial memory and interaction.",
            "intro1": "Agentic reconstruction uses a large model to inspect observations, call modeling tools, and iteratively build and check an editable scene. The challenge is not only to produce a convincing room, but to preserve the scale, shape, and spatial relationships that make it useful beyond rendering. AWSM asks how geometric evidence can constrain this process so that its outputs become more faithful spatial references for downstream agents.",
            "motivation_title": "From plausible reconstruction to a usable spatial reference",
            "motivation1": "A reconstruction agent can assemble a plausible room while getting a corner, distance, or passage wrong. For an embodied agent, those are not merely visual defects: they change where a destination lies and which route a body can follow. Geometry grounding means constraining the modeling process with pose, depth, and metric evidence where available, rather than relying on visual plausibility alone. The question is how those constraints survive the conversion from observations into editable objects.",
            "motivation2": "The reception-desk task makes this connection concrete: mark a destination in the reconstructed map, specify routes, and execute them with robot controllers. We use ‘scene representation’ for the editable objects and geometry, ‘map’ for their navigation role, and ‘simulation assets’ for their integration into a simulator. The ‘world’ in AWSM refers to this reusable spatial environment, not a learned dynamics predictor. A persistent spatial foundation connecting navigation, memory, interaction, and simulation is the longer-term goal; the experiments and demo examine its geometric basis and one downstream use.",
            "contributions": [
                "A four-route study of geometry-grounded agentic reconstruction, keeping the scene, 180 RGB identities, modeling objective, and editable output format fixed while comparing complete pipelines with different geometric evidence.",
                "An evaluation protocol that separates trajectory error, native depth, final-scene depth, surface geometry, and rendered appearance, with frozen Blend/GLB assets, reproducible evaluation subsets, public hashes, and interactive comparisons.",
                "A map-based multi-robot simulation example connecting a reconstructed scene to destination marking, predefined routes, and controller execution. It illustrates downstream use rather than a controlled navigation comparison across reconstruction routes.",
            ],
            "method_title": "One agentic workflow, four reconstruction routes",
            "interactive_title": "Inspect the reconstructed scenes, not just aggregate scores",
            "discussion_title": "What geometric grounding changes—and what it does not",
            "positioning": "AWSM connects two roles: an agent that constructs an editable scene, and downstream agents that use it as a spatial reference. SLAM and visual-inertial estimation supply pose and metric constraints; ViPE and Depth Anything 3 contribute geometric observations. Concurrent work AHa-3D explores video-driven, tool-based Real2Sim, including camera and 3D-reference estimation from video. We discuss it as a parallel effort, not a precursor to AWSM. Our emphasis is geometric grounding: bringing additional physical measurements, especially IMU-informed visual-inertial pose and metric constraints, into agentic scene construction rather than relying on video-derived evidence alone. The four-route comparison tests reconstruction systems, not the isolated effect of IMU; the demo illustrates a map-based application, not a complete autonomous embodied system.",
        })
        copy["method_intro"] = "The reconstruction agent follows a shared observe–build–verify loop: inspect the available evidence, write Blender Python to construct objects, render review views, and revise the scene before freezing it for evaluation. This tool-using modeling process is what ‘agentic’ describes here; the downstream robot controllers have a separate role."
        copy["limits"].extend([
            "The reception-desk demo is map-based simulation execution, not a controlled comparison of navigation across M1–M4. Routes are predefined, localization uses simulator pose, and the recorded run has unresolved audit failures; see its protocol.",
            "Multimodal memory, long-term map maintenance, and reduced policy sim-to-real gap are research goals, not measured outcomes of the four-robot demo. The Office Café corner observation has no matched-view quantitative GT measurement here.",
            "Historical downstream documentation describes the same M4 Blend hash using a different depth frontend. The frozen tables and assets are retained unchanged; their upstream naming needs reconciliation before attributing historical task outcomes to DA3. See the provenance note.",
        ])
        copy["office1"] += " An author-observed failure—a curved real-world corner simplified into a square one—motivates separating local shape from global scale. A correct scale alone cannot repair that shape error; this is a qualitative observation, not another measured benchmark."
    else:
        copy.update({
            "tldr": "大模型智能体可以从视觉观察构建可编辑的 3D 场景，但视觉上合理并不等于空间上忠实。AWSM 探索用几何证据约束这一 agentic 重建过程，让生成的场景可作为地图与仿真资产使用。四条重建路径检验场景忠实度，多机器人 demo 展示基于地图的执行。下一步是提升效率与精度、形成可复用的仿真就绪场景生成流程，并进一步与虚实融合智能体（phygital agents）集成，走向持久空间记忆与交互。",
            "intro1": "Agentic 重建由大模型检查观测、调用建模工具，并迭代构建和验证可编辑场景。挑战不只是生成一个令人信服的房间，还在于保留尺度、形状与空间关系，让结果在渲染之外仍然有用。AWSM 研究如何用几何证据约束这一过程，让输出成为下游智能体更忠实的空间参照。",
            "motivation_title": "从看起来合理的重建，到可以使用的空间参照",
            "motivation1": "负责重建的智能体可以搭建一个看似合理的房间，却重建错转角、距离或通道。对具身智能体而言，这些不只是视觉缺陷，还会改变目标的位置与身体可以通过的路线。几何锚定，是在信息可用时以位姿、深度与米制证据约束建模过程，而非仅依赖视觉合理性。关键问题是：这些约束如何在观测转化为可编辑对象的过程中得到保留？",
            "motivation2": "前台任务让这种联系变得具体：在重建地图中标记目标、设定路线，再由机器人控制器执行。本文用“场景表示”指可编辑的对象与几何，用“地图”描述它在导航中的作用，用“仿真资产”描述它与仿真器的集成。AWSM 中的“世界”指这种可复用的空间环境，而非学习得到的动力学预测模型。连接导航、记忆、交互与仿真的持久空间基础是长期目标；当前实验和 demo 分别研究其几何基础，并展示一种下游用途。",
            "contributions": [
                "对几何锚定的 agentic 重建开展四路线研究：固定场景、同一组 180 帧 RGB 输入、建模目标与可编辑输出格式，比较具有不同几何证据的完整管线。",
                "将轨迹误差、原生深度、最终场景深度、表面几何和渲染外观分开评测，并提供冻结 Blend/GLB 资产、可复现评测子集、公开哈希与交互式对照。",
                "通过基于地图的多机器人仿真示例，将重建场景连接到目标标记、预设路线和控制器执行；它展示下游用途，而非不同重建路线之间的受控导航对比。",
            ],
            "method_title": "一个 agentic 工作流，四条重建路线",
            "interactive_title": "不只看汇总指标，也检查重建场景",
            "discussion_title": "几何锚定改变了什么，又没有解决什么",
            "positioning": "AWSM 连接两类角色：负责构建可编辑场景的智能体，以及将它作为空间参照使用的下游智能体。SLAM 与视觉惯性估计提供位姿和米制约束，ViPE 与 Depth Anything 3 提供几何观测。同期工作 AHa-3D 探索视频驱动、工具辅助的 Real2Sim，包括从视频估计相机与三维参照；我们将其作为并行探索讨论，而非 AWSM 的前置工作。我们的重点是几何锚定：将额外的物理测量，尤其是融合 IMU 的视觉惯性位姿与米制约束，引入智能体场景构建，而不只依赖视频推断的证据。四路线对比评估的是重建系统，并非 IMU 独立作用的消融实验；demo 展示的是地图应用，而不是完整的自主具身系统。",
        })
        copy["method_intro"] = "负责重建的智能体遵循共同的“观察—构建—验证”循环：检查可用证据，编写 Blender Python 构建对象，渲染检查视图，并在冻结评测前迭代修改。这里的 agentic 指这种工具驱动的建模过程；下游机器人控制器承担另一种角色。"
        copy["limits"].extend([
            "前台 demo 展示基于地图的仿真执行，不是 M1–M4 的受控导航对比。路线预先设定，定位使用仿真器位姿，所展示 run 仍有未通过的审计项；详见演示条件。",
            "多模态空间记忆、长期地图维护与策略 sim-to-real 差距的降低是研究目标，不是这段四机器人视频已量化的结果。本页也没有 Office Café 拐角的同视角 GT 定量测量。",
            "历史下游文档对同一 M4 Blend 哈希使用了不同的深度前端描述。本页冻结表格与资产保持不变；将旧任务收益归因于 DA3 之前，需要核对上游方法命名，详见来源说明。",
        ])
        copy["office1"] += " 作者观察到的一类失败是：真实的弯曲转角被简化成方正结构。它提醒我们区分局部形状与全局尺度——尺度正确并不能自动修复形状错误；这里将其作为定性观察，而非另一组定量结果。"


def demo_section(en):
    title = "A reconstructed map. A destination. Robots in motion." if en else "一张重建地图，一个目标，一次具身执行。"
    lead = (
        "The demo connects reconstruction to downstream use in NVIDIA Isaac Sim. The reception desk is marked in the navigation map, routes are specified, and a drone, humanoid, quadruped, and wheeled robot execute the task. The same spatial reference connects a destination, route constraints, and motion control: a scene to inspect becomes a map to act with."
        if en else
        "这个 demo 在 NVIDIA Isaac Sim 中将重建连接到下游使用：在导航地图中标出前台，设定路线，再让无人机、人形、四足和轮式机器人执行任务。同一个空间参照连接目标、路径约束与运动控制：从可以查看的重建场景，走向可以用于行动的地图。"
    )
    command = "Send the drone to the reception desk and have the robots line up there." if en else "让无人机去前台，并让机器人在那里排好队。"
    labels = ("Task instruction", "Locate the reception desk", "Set routes on the map", "Execute with controllers") if en else ("任务指令", "地图上定位前台", "设定导航路线", "控制器执行")
    steps = "".join(f'<li><span>{index:02d}</span>{label}</li>' for index, label in enumerate(labels, 1))
    caption = (
        "Map-based navigation in simulation · predefined routes · simulator-pose feedback. This recorded run illustrates execution; it did not pass every task-audit criterion."
        if en else
        "基于重建地图的仿真导航 · 预设路线 · 仿真器位姿反馈。本录像用于展示执行流程，所示 run 尚未通过全部任务审计。"
    )
    details = (
        '<p>The instruction above describes the intended task, not a demonstrated language-to-plan parser. Routes were manually specified and screened against both the M4 reconstructed map and original geometry. This is not a reconstruction-only planning benchmark.</p>'
        '<p>The 156-second presentation edit plays at 1×: Scene (0–6s), Reconstruction (6–12s), Planned route (12–18s), and Navigation (18–156s). Navigation uses the new run <code>20260930-214924</code>; the opening 12.32 seconds of waiting are omitted, and the later terminal hold is outside this cut. The map is a static route design, not a measured execution trace.</p>'
        '<p>The source run reports completed flight and ground formation. Its independent audit passes the map-clearance, inter-robot-clearance, waypoint, and closure checks, but remains FAILED: measured terminal health/formation hold is 7.994999821 seconds against the unchanged 8.0-second requirement. Media export checks passed; independent physical and film acceptance are not claimed.</p>'
        '<p>This demo does not evaluate online visual localization, learned instruction understanding, memory retrieval, or real-robot transfer. Those are separate capabilities; the map-based execution shown here remains the intended demonstration.</p>'
        if en else
        '<p>上方指令说明任务意图，不代表本次演示实现了语言到计划的自动解析。路线人工设定，并同时参考 M4 重建地图和原始几何筛选；这不是只依赖重建图的规划 benchmark。</p>'
        '<p>成片为 156 秒、1× 原速：场景（0–6秒）、重建（6–12秒）、路线设计（12–18秒）、导航（18–156秒）。导航来自新运行 <code>20260930-214924</code>，略去开头等待的 12.32 秒，后续终点保持过程不在本剪辑中。地图是静态路线设计图，不是实测执行轨迹。</p>'
        '<p>源运行报告飞行任务与地面队形完成。独立审计中的地图净空、机器人间净空、航点及闭环检查已通过，但总判定仍为 FAILED：终点健康／队形保持实测 7.994999821 秒，未达到原定 8.0 秒要求。媒体导出检查通过，不据此宣称独立物理或影片验收通过。</p>'
        '<p>本 demo 不评测在线视觉定位、学习型指令理解、记忆检索或真实机器人迁移。这些是独立能力，不改变本演示所表达的“利用重建地图执行导航任务”。</p>'
    )
    return f'''<section id="embodied-demo" class="embodied-demo">
<p class="section-tag">DEMO / MAP-BASED EMBODIED EXECUTION</p><h2>{title}</h2><p>{lead}</p>
<blockquote class="mission-command"><span>{"Task intent" if en else "任务意图"}</span>“{command}”</blockquote>
<ol class="mission-flow" aria-label="{"Task workflow" if en else "任务流程"}">{steps}</ol>
<figure class="demo-film"><video controls playsinline preload="none" poster="assets/embodied-demo/navigation-214924-poster.png" width="1280" height="720" aria-label="{"Four-robot map-based navigation demonstration" if en else "四机器人地图导航演示"}"><source src="assets/embodied-demo/four-robots-214924-156s-phone.mp4" type="video/mp4">{"Your browser cannot play this video. Use the download link below." if en else "浏览器无法播放此视频，请使用下方下载链接。"}</video><figcaption>{caption}</figcaption></figure>
<div class="demo-links"><a href="assets/embodied-demo/four-robots-214924-156s-phone.mp4" download>{"Download mobile edition" if en else "下载手机版"} · 11.65 MB · 2:36</a><a href="assets/embodied-demo/four-robots-214924-156s-hd.mp4" download>{"Download HD edition" if en else "下载高清版"} · 49.69 MB · 2:36</a><a href="data/embodied_demo.json">{"Run &amp; media record" if en else "运行与视频记录"} ↗</a></div>
<figure class="demo-map" id="demo-route-map"><a href="assets/embodied-demo/planned-route-156s.png" target="_blank" rel="noopener"><img loading="lazy" src="assets/embodied-demo/planned-route-156s.png" width="1920" height="1080" alt="{"Planned routes for four robots, with the reception desk and waypoints marked; static design, not execution trajectories" if en else "标出前台与航点的四机器人路线设计图；静态设计，非执行轨迹"}"></a><figcaption><span>{"Navigation map." if en else "导航地图。"}</span> {"The reception desk and planned routes share the reconstructed scene. This is a static design preview, not a recorded trajectory. Open the image to inspect the full-resolution map." if en else "在重建场景中标出前台与规划路线。这是静态设计图，而非实跑轨迹；点击查看原尺寸地图。"}</figcaption></figure>
<details class="demo-protocol"><summary>{"Demo protocol and scope" if en else "演示条件与范围"}</summary>{details}<p><a href="evidence/embodied-demo-audit.json">{"Independent audit summary" if en else "独立审计摘要"} ↗</a></p></details>
</section>'''


def grounding_section(en):
    if en:
        return '''<div id="scale-and-sensors" class="analysis-block grounding-block"><h3>Geometry grounding: scale is necessary, but not sufficient</h3>
<p>Monocular projection geometry leaves a global scale ambiguity; learned metric depth adds a useful prior, not an independent measurement of every real-world dimension. Calibrated RGB-D, a known baseline or length, and visual-inertial estimation can supply metric constraints. IMU fusion can recover metric motion under sufficient excitation and reliable initialization, bias estimation, synchronization, and calibration. An IMU is not a direct distance sensor, and its presence alone does not guarantee accurate scale.</p>
<p>Scale, local shape, camera pose, and navigable connectivity must be checked separately. A curved corner simplified into a square cannot be repaired by rescaling alone. Pose-conditioned depth can improve reconstruction, but neither the DA3 ablation nor our M2/M3 results imply that every depth metric improves monotonically. The four routes below are system comparisons, not an isolated IMU ablation.</p>
<p class="inline-sources"><a href="https://arxiv.org/abs/1708.03852" target="_blank" rel="noopener">VINS-Mono</a> · <a href="https://arxiv.org/html/2511.10647v1#S7.SS2.SSS3" target="_blank" rel="noopener">DA3 pose-conditioning ablation</a></p></div>'''
    return '''<div id="scale-and-sensors" class="analysis-block grounding-block"><h3>几何锚定：真实尺度是必要约束，但不是全部答案</h3>
<p>纯单目投影几何存在全局尺度歧义；学习型米制深度提供有用先验，却不是对每个真实尺寸的独立测量。标定 RGB-D、已知基线或长度，以及视觉惯性估计，都可以提供米制约束。IMU 融合能在运动激励充分、初始化、偏置估计、时间同步与标定可靠时恢复米制运动；IMU 不是直接测距传感器，“带 IMU”不等于“尺度一定准确”。</p>
<p>尺度、局部形状、相机位姿和可通行连通性需要分别检查。弯曲转角被简化成直角，不能只靠缩放修复。位姿条件可以改善深度重建，但 DA3 消融和本文 M2/M3 的结果都不支持“所有深度指标必然同步改善”；下文四条路线是完整系统比较，而非只切换 IMU 的单变量实验。</p>
<p class="inline-sources"><a href="https://arxiv.org/abs/1708.03852" target="_blank" rel="noopener">VINS-Mono</a> · <a href="https://arxiv.org/html/2511.10647v1#S7.SS2.SSS3" target="_blank" rel="noopener">DA3 位姿条件消融</a></p></div>'''


def outlook_section(en):
    if en:
        title = "Toward persistent spaces for phygital agents"
        intro = "The current outputs are editable scene snapshots, and the demo shows a scene-specific simulation integration. The longer-term goal is to make geometry-grounded agentic reconstruction a reusable process for building and maintaining spaces that phygital agents can use. Saving an editable asset is a starting point, not a demonstration of lifelong map maintenance. The directions below extend the present evidence."
        cards = [
            ("Navigate", "Use destinations, free space, and body-specific clearance in a shared geometric frame. Better reconstruction can reduce map mismatch; reliable navigation also needs localization and current observations."),
            ("Remember & retrieve", "Link object identities and locations to source views so language, images, and past observations can refer to the same place. Retrieval and safe arrival should be evaluated separately."),
            ("Interact & maintain", "Edit object properties and relationships, revisit changed areas, and preserve evidence and versions. Persistent memory must distinguish observed geometry, inferred completion, and unknown space."),
            ("Simulate & learn", "Move from the current scene-specific integration to reusable simulation-ready exports with checked scale, collision geometry, and physical parameters. These can support task rehearsal, scenario variation, and training; reduced policy sim-to-real gap remains a separate question to test."),
        ]
        closing = "A full mesh is not required for every retrieval task: Memory Over Maps uses posed RGB-D keyframes for on-demand localization, while 3D-Mem and task-oriented scene graphs explore complementary memory and representation choices. Our proposed direction is hybrid: preserve visual evidence, refine task-relevant geometry, and build editable simulation assets where they add value. The next question is when an agent has enough evidence to act—and when it should observe again and update its map."
        next_steps = "The immediate agenda is higher reconstruction efficiency and accuracy, reusable simulation-ready scene generation, and deeper integration with phygital agents. Together, these steps connect the reconstruction agent’s modeling and revision loop to the downstream agent’s navigation, memory, and interaction needs."
        label = "RESEARCH DIRECTION"
    else:
        title = "走向虚实融合智能体可持续使用的空间"
        intro = "当前输出是可编辑的场景快照，demo 展示了针对特定场景的仿真集成。长期目标是把几何锚定的 agentic 重建发展为可复用流程，构建并维护虚实融合智能体能够使用的空间。保存可编辑资产是起点，不等于已经验证长期地图维护；以下方向是在当前证据基础上的延伸。"
        cards = [
            ("导航", "在同一几何坐标中表达目标、自由空间与不同机器人的通行净空。更忠实的重建可以减少地图失配，可靠导航还需要定位与实时观测。"),
            ("记忆与多模态检索", "将对象身份、位置和源视图关联，让语言、图像与过去的观察指向同一个地点。检索到对象与安全到达对象，需要分别评测。"),
            ("交互与长期维护", "编辑对象属性与关系，重访变化区域，保留证据和版本。持久记忆应区分实际观察、推断补全和未知空间，而非把所有生成内容都当作事实。"),
            ("仿真与学习", "从当前特定场景的集成，走向可复用的仿真就绪导出流程，检查尺度、碰撞几何与物理参数。它可支持任务预演、场景变体和训练；是否降低策略 sim-to-real 差距，仍需单独检验。"),
        ]
        closing = "并非每次寻物都需要完整网格：Memory Over Maps 用带位姿 RGB-D 关键帧按需定位，3D-Mem 与任务相关场景图也探索了不同记忆和表示方式。我们主张混合路线：保留视觉证据，细化任务相关几何，在有价值的地方构建可编辑仿真资产。下一步的关键问题是：什么时候证据已经足够支持行动，什么时候 agent 应重新观察并更新地图？"
        next_steps = "近期重点是提升重建效率与精度、形成可复用的仿真就绪场景生成流程，以及进一步与虚实融合智能体集成，让重建智能体的建模与修正循环连接到下游智能体的导航、记忆和交互需求。"
        label = "研究方向"
    items = "".join(f'<div><h4>{name}</h4><p>{text}</p></div>' for name, text in cards)
    return f'''<div id="spatial-foundation" class="analysis-block spatial-foundation"><p class="section-tag">{label}</p><h3>{title}</h3><p>{intro}</p><div class="capability-grid">{items}</div><p>{closing}</p><p>{next_steps}</p><p class="inline-sources"><a href="https://arxiv.org/abs/2603.20530" target="_blank" rel="noopener">Memory Over Maps</a> · <a href="https://arxiv.org/abs/2411.17735" target="_blank" rel="noopener">3D-Mem</a> · <a href="https://arxiv.org/abs/2404.13696" target="_blank" rel="noopener">Clio</a> · <a href="https://arxiv.org/abs/2404.06609" target="_blank" rel="noopener">GOAT-Bench</a></p></div>'''


def editorial_page(page, en):
    page = page.replace('01 / RESULTS', '01 / OVERVIEW')
    page = page.replace('04 / MORE RESULTS AND ANALYSIS', '04 / RESULTS AND ANALYSIS')
    style_version = sha256((Path(__file__).resolve().parents[1] / "editorial.css").read_bytes()).hexdigest()[:12]
    page = page.replace('<link rel="stylesheet" href="style.css">', f'<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="editorial.css?v={style_version}">')
    office_version = sha256((Path(__file__).resolve().parents[1] / "office.css").read_bytes()).hexdigest()[:12]
    page = page.replace('</head>', f'<link rel="stylesheet" href="office.css?v={office_version}"></head>')
    for asset in ("app.js", "scene-compare.js", "office-models.js"):
        version = sha256((Path(__file__).resolve().parents[1] / asset).read_bytes()).hexdigest()[:12]
        page = page.replace(f'src="{asset}"', f'src="{asset}?v={version}"')
    if en:
        page = page.replace(f'<link rel="canonical" href="{BASE_URL}index.html">', f'<link rel="canonical" href="{BASE_URL}">')
    page = page.replace(f'hreflang="zh-CN" href="{BASE_URL}index.html"', f'hreflang="zh-CN" href="{BASE_URL}zh.html"')
    page = page.replace(f'hreflang="en" href="{BASE_URL}en.html"', f'hreflang="en" href="{BASE_URL}"')
    page = page.replace('</head>', f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}"></head>')
    page = page.replace('<a href="index.html" ', '<a href="zh.html" ', 1)
    page = page.replace('<a href="en.html" ', '<a href="index.html" ', 1)
    page = page.replace('<a class="brand" href="index.html">ASTRA / WORLD MODELS</a>', '<a class="brand" href="index.html">PHYGITAL AI / AWSM</a>')
    subtitle = 'From real spaces to <strong class="tagline-emphasis">worlds phygital agents can use.</strong>' if en else '把真实空间，变成<strong class="tagline-emphasis">虚实融合智能体可以使用的世界。</strong>'
    pronunciation = 'pronounced “awesome”' if en else '读作 “awesome”'
    brand_note = 'Phygital = physical + digital.' if en else 'Phygital = physical（物理）+ digital（数字），即虚实融合。'
    before_header, header_start, remainder = page.partition('<header>')
    old_header, header_end, after_header = remainder.partition('</header>')
    title_name = "Agentic World Simulation and Mapping" if en else "智能体世界仿真与建图"
    heading = f'<p class="title-name">{title_name}</p><div class="title-lockup"><h1 aria-label="AWSM: {title_name}">AWSM</h1><p class="pronunciation">{pronunciation}</p></div>'
    publication = 'Published <time datetime="2026-10-01">October 1, 2026</time>' if en else '发布于 <time datetime="2026-10-01">2026年10月1日</time>'
    page = before_header + header_start + heading + f'<p class="lead">{subtitle}</p><p class="brand-note">{brand_note}</p><p class="publication-date">{publication}</p>' + header_end + after_header
    page = page.replace('</head>', '<meta property="article:published_time" content="2026-10-01"></head>')
    download_label = "Download BibTeX" if en else "下载 BibTeX 引用"
    page = page.replace('</code></pre></section>', f'</code></pre><a class="citation-download" href="data/awsm.bib" download="awsm.bib">{download_label} <span aria-hidden="true">↓</span></a></section>', 1)
    page = page.replace('<section id="related-work">', demo_section(en) + '\n<section id="related-work">', 1)
    page = page.replace('</section>\n<section id="workflow">', grounding_section(en) + '</section>\n<section id="workflow">', 1)
    page = page.replace('</section>\n<section id="limitations">', outlook_section(en) + '</section>\n<section id="limitations">', 1)
    page = page.replace('href="#related-work">', 'href="#embodied-demo">' + ('Embodied demo' if en else '具身演示') + '</a><a href="#related-work">', 1)
    evidence_link = '<p><a href="evidence/provenance-note.md">' + ('Version and provenance note' if en else '版本与资产来源说明') + ' ↗</a></p>'
    page = page.replace('</section>\n<section id="citation">', evidence_link + '</section>\n<section id="citation">', 1)
    return page.replace('Agentic World · frozen evidence, editable outputs', 'Phygital AI · AWSM · frozen evidence, editable outputs')
