"""Bilingual narrative and demo additions around the frozen research article."""

SITE_TITLE = "Agentic World Simulation and Mapping"
BASE_URL = "https://phygital-ai.github.io/agentic-world-simulation-and-mapping/"

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
            "tldr": "Our goal is a persistent, editable spatial representation that connects reconstruction, map-based navigation, memory, interaction, and simulation. We study its geometric foundation through four frozen reconstruction routes, then show robots executing a reception-desk task using the reconstructed map. The experiments measure scene fidelity; the demo illustrates map-based execution; multimodal memory and long-term updates define the next research steps.",
            "intro1": "A room that looks convincing is not yet a map an embodied agent can rely on. The agent needs to know where a destination is, how objects and free space relate, and which route its body can follow. Those answers should refer to the same space—not to separate, incompatible reconstructions for rendering, planning, and simulation.",
            "motivation_title": "A shared spatial foundation for embodied agents",
            "motivation1": "Consider the instruction: ‘Send the drone to the reception desk and have the robots line up there.’ The reception desk is a destination in the reconstructed map; a route is specified in that map, then controllers execute it. This is map-based navigation: reconstruction, target selection, route planning, and control share a spatial reference. An editable scene becomes an interface between a task and its execution.",
            "motivation2": "Our ambition is to turn captured spaces into persistent spatial representations: maps for navigation, references for multimodal retrieval, editable objects for interaction, and environments for simulation. More faithful reconstruction can reduce one source of mismatch between the map and the original space. Reaching a dependable, general-purpose system also requires localization, uncertainty, dynamics, and updates to remain consistent. The frozen study below examines the geometric foundation of that ambition.",
            "positioning": "SLAM and visual-inertial estimation provide essential pose, registration, and metric constraints; geometric models such as ViPE and Depth Anything 3 provide complementary observations. Agentic Real2Sim systems such as AHa-3D show how tools can turn observations into editable scenes. We build on these directions rather than replace SLAM: the goal is to carry geometric evidence into a persistent, object-centric representation that agents can query, edit, navigate with, and simulate.",
        })
        copy["limits"].extend([
            "The reception-desk demo is map-based simulation execution, not a controlled comparison of navigation across M1–M4. Routes are predefined, localization uses simulator pose, and the recorded run has unresolved audit failures; see its protocol.",
            "Multimodal memory, long-term map maintenance, and reduced policy sim-to-real gap are research goals, not measured outcomes of the four-robot demo. The Office Café corner observation has no matched-view quantitative GT measurement here.",
            "Historical downstream documentation describes the same M4 Blend hash using a different depth frontend. The frozen tables and assets are retained unchanged; their upstream naming needs reconciliation before attributing historical task outcomes to DA3. See the provenance note.",
        ])
        copy["office1"] += " An author-observed failure—a curved real-world corner simplified into a square one—motivates separating local shape from global scale. A correct scale alone cannot repair that shape error; this is a qualitative observation, not another measured benchmark."
    else:
        copy.update({
            "tldr": "我们希望构建一种持久、可编辑的空间表示，连接场景重建、地图导航、空间记忆、交互与仿真。本文用四条冻结重建路径研究它的几何基础，再展示机器人依据重建地图执行前台任务：实验回答场景有多忠实，demo 展示地图如何用于行动，多模态记忆与长期更新则是下一步研究方向。",
            "intro1": "一个看起来令人信服的房间，还不是具身 agent 可以依赖的地图。Agent 需要知道目标在哪里、物体与自由空间如何分布，以及自己的身体可以沿哪条路线通过。这些答案应当指向同一个空间，而不是渲染、规划与仿真各自维护一套互不一致的表示。",
            "motivation_title": "具身 agent 需要一个共享的空间基础",
            "motivation1": "考虑这样一条任务指令：“让无人机去前台，并让机器人在那里排好队。”前台是重建地图中的目标，路线在地图上设定，再由控制器执行。这就是基于地图的导航：重建、目标选择、路线规划和运动控制共享一个空间参照，可编辑场景由此成为任务与执行之间的接口。",
            "motivation2": "我们的目标是把采集到的空间变成可以持续使用的空间表示：导航使用的地图、多模态检索的空间参照、可交互的对象，以及可编辑的仿真环境。重建越忠实，地图与原空间之间的一类误差就越小；要成为稳定、通用的具身基础，还需要定位、不确定性、动力学和长期更新保持一致。下文的冻结实验研究的正是这一愿景的几何基础。",
            "positioning": "SLAM 与视觉惯性估计提供重要的位姿、配准与米制约束，ViPE、Depth Anything 3 等几何模型提供互补观测，AHa-3D 等 agentic Real2Sim 系统展示如何用工具把观测组织成可编辑场景。我们的方向不是替代 SLAM，而是在这些能力之上，让几何证据进入持久、对象化的空间表示，供 agent 查询、编辑、导航和仿真共同使用。",
        })
        copy["limits"].extend([
            "前台 demo 展示基于地图的仿真执行，不是 M1–M4 的受控导航对比。路线预先设定，定位使用仿真器位姿，所展示 run 仍有未通过的审计项；详见演示条件。",
            "多模态空间记忆、长期地图维护与策略 sim-to-real 差距的降低是研究目标，不是这段四机器人视频已量化的结果。本页也没有 Office Café 拐角的同视角 GT 定量测量。",
            "历史下游文档对同一 M4 Blend 哈希使用了不同的深度前端描述。本页冻结表格与资产保持不变；将旧任务收益归因于 DA3 之前，需要核对上游方法命名，详见来源说明。",
        ])
        copy["office1"] += " 作者观察到的一类失败是：真实的弯曲转角被简化成方正结构。它提醒我们区分局部形状与全局尺度——尺度正确并不能自动修复形状错误；这里将其作为定性观察，而非另一组定量结果。"


def demo_section(en):
    title = "A reconstructed map. A destination. Robots in motion." if en else "一张重建地图，一个目标，一次具身执行。"
    lead = (
        "The reception desk is marked in the navigation map, routes are specified, and a drone, humanoid, quadruped, and wheeled robot execute the task. The same spatial reference connects a destination, route constraints, and motion control: a scene to inspect becomes a map to act with."
        if en else
        "导航地图中标出前台，在地图上设定路线，再让无人机、人形、四足和轮式机器人执行任务。同一个空间参照连接目标、路径约束与运动控制：从可以查看的重建场景，走向可以用于行动的地图。"
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
        '<p>The 235.2-second film is unchanged at 1× speed: 18 seconds of scene/reconstruction/route presentation, followed by the recorded execution from run <code>20260930-144825</code>. The ground robots reach their final formation. The independent audit records clearance-envelope and waypoint failures, and incomplete flight-task closure. An envelope violation is not itself a measured physical contact.</p>'
        '<p>This demo does not evaluate online visual localization, learned instruction understanding, memory retrieval, or real-robot transfer. Those are separate capabilities; the map-based execution shown here remains the intended demonstration.</p>'
        if en else
        '<p>上方指令说明任务意图，不代表本次演示实现了语言到计划的自动解析。路线人工设定，并同时参考 M4 重建地图和原始几何筛选；这不是只依赖重建图的规划 benchmark。</p>'
        '<p>原片保持 1×、235.2 秒不变：前 18 秒为场景／重建／路线展示，其后为 <code>20260930-144825</code> 的执行录像。地面机器人到达最终队形；独立审计仍记录了净空包络、航点及飞行任务闭环方面的失败。几何包络违反不等于已检测到真实接触。</p>'
        '<p>本 demo 不评测在线视觉定位、学习型指令理解、记忆检索或真实机器人迁移。这些是独立能力，不改变本演示所表达的“利用重建地图执行导航任务”。</p>'
    )
    return f'''<section id="embodied-demo" class="embodied-demo">
<p class="section-tag">DEMO / MAP-BASED EMBODIED EXECUTION</p><h2>{title}</h2><p>{lead}</p>
<blockquote class="mission-command"><span>{"Task intent" if en else "任务意图"}</span>“{command}”</blockquote>
<ol class="mission-flow" aria-label="{"Task workflow" if en else "任务流程"}">{steps}</ol>
<figure class="demo-film"><video controls playsinline preload="none" poster="assets/embodied-demo/poster.jpg" width="1280" height="720" aria-label="{"Four-robot map-based navigation demonstration" if en else "四机器人地图导航演示"}"><source src="assets/embodied-demo/world-lobby-four-robots.mp4" type="video/mp4">{"Your browser cannot play this video. Use the download link below." if en else "浏览器无法播放此视频，请使用下方下载链接。"}</video><figcaption>{caption}</figcaption></figure>
<div class="demo-links"><a href="assets/embodied-demo/world-lobby-four-robots.mp4" download>{"Download full demo" if en else "下载完整演示"} · 12.24 MB · 3:55</a><a href="data/embodied_demo.json">{"Run &amp; media record" if en else "运行与视频记录"} ↗</a></div>
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
        title = "Beyond a navigation map: a persistent world agents can use"
        intro = "The long-term opportunity is a shared spatial foundation, not simply a more attractive mesh. Localization and mapping remain essential; an object-centric scene can connect their outputs to memory, interaction, and simulation. These are research directions extending the present reconstruction study and map-based demo—not additional completed experiments."
        cards = [
            ("Navigate", "Use destinations, free space, and body-specific clearance in a shared geometric frame. Better reconstruction can reduce map mismatch; reliable navigation also needs localization and current observations."),
            ("Remember & retrieve", "Link object identities and locations to source views so language, images, and past observations can refer to the same place. Retrieval and safe arrival should be evaluated separately."),
            ("Interact & maintain", "Edit object properties and relationships, revisit changed areas, and preserve evidence and versions. Persistent memory must distinguish observed geometry, inferred completion, and unknown space."),
            ("Simulate & learn", "Reuse the scene for task rehearsal, scenario variation, and training. Geometric fidelity may reduce the geometric part of sim-to-real mismatch; materials, dynamics, sensors, and policy transfer still need calibration and testing."),
        ]
        closing = "A full mesh is not required for every retrieval task: Memory Over Maps uses posed RGB-D keyframes for on-demand localization, while 3D-Mem and task-oriented scene graphs explore complementary memory and representation choices. Our proposed direction is hybrid: preserve visual evidence, refine task-relevant geometry, and build editable simulation assets where they add value. The next question is when an agent has enough evidence to act—and when it should observe again and update its map."
        label = "RESEARCH DIRECTION"
    else:
        title = "不止是一张导航地图，而是 agent 可以持续使用的世界"
        intro = "长期机会是一种共享的空间基础，而不只是更漂亮的 mesh。定位和建图仍然重要；对象化场景则把它们的输出连接到记忆、交互与仿真。以下是从当前重建实验和地图导航 demo 延伸出的研究方向，不是新增的已完成实验。"
        cards = [
            ("导航", "在同一几何坐标中表达目标、自由空间与不同机器人的通行净空。更忠实的重建可以减少地图失配，可靠导航还需要定位与实时观测。"),
            ("记忆与多模态检索", "将对象身份、位置和源视图关联，让语言、图像与过去的观察指向同一个地点。检索到对象与安全到达对象，需要分别评测。"),
            ("交互与长期维护", "编辑对象属性与关系，重访变化区域，保留证据和版本。持久记忆应区分实际观察、推断补全和未知空间，而非把所有生成内容都当作事实。"),
            ("仿真与学习", "同一场景用于任务预演、环境变体和训练。几何忠实度有望缩小 sim-to-real 的几何差距；材质、动力学、传感器与策略迁移仍需单独标定和验证。"),
        ]
        closing = "并非每次寻物都需要完整网格：Memory Over Maps 用带位姿 RGB-D 关键帧按需定位，3D-Mem 与任务相关场景图也探索了不同记忆和表示方式。我们主张混合路线：保留视觉证据，细化任务相关几何，在有价值的地方构建可编辑仿真资产。下一步的关键问题是：什么时候证据已经足够支持行动，什么时候 agent 应重新观察并更新地图？"
        label = "研究方向"
    items = "".join(f'<div><h4>{name}</h4><p>{text}</p></div>' for name, text in cards)
    return f'''<div id="spatial-foundation" class="analysis-block spatial-foundation"><p class="section-tag">{label}</p><h3>{title}</h3><p>{intro}</p><div class="capability-grid">{items}</div><p>{closing}</p><p class="inline-sources"><a href="https://arxiv.org/abs/2603.20530" target="_blank" rel="noopener">Memory Over Maps</a> · <a href="https://arxiv.org/abs/2411.17735" target="_blank" rel="noopener">3D-Mem</a> · <a href="https://arxiv.org/abs/2404.13696" target="_blank" rel="noopener">Clio</a> · <a href="https://arxiv.org/abs/2404.06609" target="_blank" rel="noopener">GOAT-Bench</a></p></div>'''


def editorial_page(page, en):
    page = page.replace('<link rel="stylesheet" href="style.css">', '<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="editorial.css">')
    if en:
        page = page.replace(f'<link rel="canonical" href="{BASE_URL}index.html">', f'<link rel="canonical" href="{BASE_URL}">')
    page = page.replace(f'hreflang="zh-CN" href="{BASE_URL}index.html"', f'hreflang="zh-CN" href="{BASE_URL}zh.html"')
    page = page.replace(f'hreflang="en" href="{BASE_URL}en.html"', f'hreflang="en" href="{BASE_URL}"')
    page = page.replace('</head>', f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}"></head>')
    page = page.replace('<a href="index.html" ', '<a href="zh.html" ', 1)
    page = page.replace('<a href="en.html" ', '<a href="index.html" ', 1)
    page = page.replace('<a class="brand" href="index.html">ASTRA / WORLD MODELS</a>', '<a class="brand" href="index.html">PHYGITAL AI / AGENTIC WORLD</a>')
    page = page.replace('RESEARCH ESSAY · EDITABLE WORLD MODELS', 'GEOMETRY-GROUNDED AGENTIC SCENE RECONSTRUCTION AND MAPPING' if en else '几何锚定的智能体场景重建与建图')
    page = page.replace('<section id="motivation">', demo_section(en) + '\n<section id="motivation">', 1)
    page = page.replace('</section>\n<section id="workflow">', grounding_section(en) + '</section>\n<section id="workflow">', 1)
    page = page.replace('</section>\n<section id="limitations">', outlook_section(en) + '</section>\n<section id="limitations">', 1)
    page = page.replace('href="#motivation">', 'href="#embodied-demo">' + ('Embodied demo' if en else '具身演示') + '</a><a href="#motivation">', 1)
    evidence_link = '<p><a href="evidence/provenance-note.md">' + ('Version and provenance note' if en else '版本与资产来源说明') + ' ↗</a></p>'
    page = page.replace('</section>\n<section id="citation">', evidence_link + '</section>\n<section id="citation">', 1)
    return page.replace('Agentic World · frozen evidence, editable outputs', 'Phygital AI · Agentic World · frozen evidence, editable outputs')
