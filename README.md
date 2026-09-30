# Agentic World · editable World Lobby

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
