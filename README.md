# Agentic World · 当地图成为程序

Bilingual research article based on `world_lobby_four_trajectory_20260929`.

- Website: https://wentingw.github.io/agentic-world-blog/
- Repository: https://github.com/wentingw/agentic-world-blog
- Reference article: https://wentingw.github.io/astra-world-model-blog/
- Snapshot: 2026-09-30. Pose and native depth results are complete; the new Astra / Blender scenes are still in progress.

## Read and reproduce

`index.html` is Chinese; `en.html` is English. No build tool or CDN is required to serve the generated site. Interactive charts use local JSON. Static figures and tables remain available without JavaScript.

```bash
python -m http.server 8765 --directory .
```

Open http://localhost:8765/. Authoring sources are `content/article.zh.md` and `content/article.en.md`; styling and interaction are in `style.css` and `app.js`.

To rebuild from the original workspace:

```bash
python -m pip install -r requirements.txt
python scripts/build.py --source ../world_lobby_four_trajectory_20260929
python scripts/validate.py
```

The builder reads the original experiment without changing it. Tables derive from the metric JSON, and original evidence is copied byte for byte. It stops if final model artifacts appear, because the editorial status then needs review. The source directory includes captured RGB required for the hero; those full inputs are not bundled here. This repository reproduces the article, not the full estimation, model inference or simulator run. `evidence/code` and the experimental commands document those stages but need the original environment, inputs and dependencies.

`data/source_manifest.json` records each copied source's relative path, size and SHA256; `evidence/SHA256SUMS` verifies the copied evidence. Historical absolute paths inside original JSON and scripts are retained as provenance, not downloadable links. Check evidence hashes from `evidence/` with `sha256sum -c SHA256SUMS`.

## Interpretation

- Pose metrics use 4,254 exact common timestamps and one global scale=1 SE(3) alignment per estimator. Coverage uses the full 4,499-frame capture.
- DA3 metrics concern predicted optical-Z on 180 modelling frames and 500 disjoint non-modelling frames. The 500 RGB images are inputs to depth inference.
- Prediction validity is finite depth in [0.1, 30] metres plus sampling validity. Intersection errors and coverage / fixed-domain missing penalties are distinct.
- Per-frame GT scale diagnostics change both scale and validity; they are not primary metric results.
- Frame bootstrap summaries are not evidence of cross-scene significance. M4 has two evaluation frames without valid predictions.
- No new frozen Blender model, appearance score or robot task score is claimed. The previous article's results are not reused as this run's evidence.

## Publishing

GitHub Pages serves `/` on branch `main`, using `.nojekyll`. Publishing uses normal commits and non-force pushes. Credentials are retrieved from the existing desktop Secret Service helper; no token is written into this repository or a remote URL.

```bash
python scripts/publish.py
```

The publisher checks the account is `wentingw`, creates only `wentingw/agentic-world-blog` if missing, pushes the current clean committed revision and configures branch-based Pages. It never requests broader scopes or modifies the previous blog. A desktop login keyring must be available for authentication. Use a new commit for each reviewed revision.

Browser verification:

```bash
python -m pip install playwright
python scripts/browser_qa.py --url http://127.0.0.1:8765/
```

The QA script uses local Google Chrome, checks both languages at desktop and mobile sizes, verifies charts and images, and saves screenshots under ignored `qa/`.
