# Publication scope and provenance — 30 September 2026

## This revision

The Phygital AI edition changes the bilingual narrative and adds the reception-desk embodied demo. It retains the seven frozen experiment tables, six original figures, model files, registration transforms, and fixed-view images from upstream commit `3c5f27ca16fffca03f9e071f70bcc234e34739ee` of `wentingw/agentic-world-blog`.

The demo expresses map-based navigation: the destination is marked on the reconstructed map, routes are specified, and robot controllers execute them. It is not presented as an online visual-localization experiment. The task wording describes the intent, not a demonstrated language-to-plan parser.

The demo now uses the supplied `20260930-four-robot-demo-final-156s` delivery, copied without re-encoding. The mobile edition is 11,648,571 bytes (SHA-256 `b9008c7b754f994d30a740a632b70ea0f693f3917fcf11820e64902ddbd13596`); the HD edition is 49,687,378 bytes (SHA-256 `f83dbb49e3aa97fd3f5f9c54ed79ed8624bac75dbd7e4cdddc4dc414b76ed222`). Both are 156 seconds, 1280×720, 30 fps, at 1× playback speed. The package's original planned-route PNG and navigation screenshot are copied unchanged as the standalone map and video poster.

The first 18 seconds present Scene, Reconstruction, and Planned route; the remaining 138 seconds show native RGB execution from run `sceneweft-walljourney-20260930-214924`. The package omits 12.32 seconds of opening waiting and truncates later footage, including terminal formation hold. The static map is a planned-route design, not a measured execution trace. These are presentation edits, not additional experiments.

The new source run reports completed flight and formation. Unlike the superseded `144825` run, its independent audit passes map and inter-robot clearance, waypoint traversal, and closure checks. The total verdict remains FAILED because measured terminal health/formation hold is 7.994999821297824 seconds against an unchanged 8.0-second requirement. Media export checks do not establish physical or film acceptance. The old run's clearance, waypoint, and flight-closure failures are not attributed to this new run. Current conditions and audit details are recorded in `data/embodied_demo.json` and `evidence/embodied-demo-audit.json`; source-receipt hashes are in `evidence/embodied-demo-delivery.json`. Full production records and raw frames remain in the local delivery, rather than uploading the 2.61 GB package to the blog.

## Upstream naming discrepancy

The frozen M4 Blend SHA-256 is `cc6cb605246a255d94e36b9dc3f8b91d5a292b047470bc0ff75b8a5c404b0cfe`.

- The current upstream table describes M4 as GT camera poses with pose-conditioned DA3 depth.
- Historical downstream documentation dated 24 September 2026 describes that same Blend hash as GT camera poses with pose-conditioned MapAnything depth.
- Historical M3 documentation also names OpenVINS, whereas the current frozen table names ORB-SLAM3.

This may reflect documentation or pipeline-version drift. The asset hash establishes identical output, not which upstream description is correct. This publication does not silently change the frozen data or infer a causal result from that discrepancy. Resolving it requires the original input packets and modeling-run records. Historical retrieval/navigation outcomes are not combined with this demo or attributed to DA3.

## Scope

The reconstruction measurements, map-based execution demonstration, and longer-term spatial-memory/simulation research agenda are separate evidence levels. More faithful geometry can reduce geometric mismatch; dependable real-world navigation and policy transfer also depend on localization, physical properties, dynamics, sensing, and change handling. No real-robot transfer or reduction in training sim-to-real gap is measured here.

## 中文说明

本轮仅调整叙事并加入前台导航 demo，保留上游七张实验表、六张原图、模型和配准。Demo 表达“目标在重建地图中标出—路线在地图上设定—机器人执行”，并非在线视觉定位或语言自动规划实验。

新旧文档对同一 M4 模型的深度前端，以及 M3 的位姿前端，存在命名差异；需要用原始输入包和运行记录核对。本页不更改冻结结果，也不把旧检索任务收益直接归因于新版方法名称。多模态记忆、长期维护及降低 sim-to-real 差距作为研究方向呈现。
