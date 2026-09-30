# Publication scope and provenance — 30 September 2026

## This revision

The Phygital AI edition changes the bilingual narrative and adds the reception-desk embodied demo. It retains the seven frozen experiment tables, six original figures, model files, registration transforms, and fixed-view images from upstream commit `3c5f27ca16fffca03f9e071f70bcc234e34739ee` of `wentingw/agentic-world-blog`.

The demo expresses map-based navigation: the destination is marked on the reconstructed map, routes are specified, and robot controllers execute them. It is not presented as an online visual-localization experiment. The task wording describes the intent, not a demonstrated language-to-plan parser.

Video bytes remain unchanged (SHA-256 `7427552e2234614eff778c7fe724a3903e10300feeef358aff9a78eb79060c6c`). Run conditions and unresolved audit items are recorded in `data/embodied_demo.json` and `evidence/embodied-demo-audit.json`. The clip is identified by run ID, not as the latest successful experiment.

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
