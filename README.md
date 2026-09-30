# Agentic World · editable World Lobby

Bilingual static research journal rebuilt from frozen local sources. Figure 3 uses one local Three.js renderer/camera/full viewport for split comparison of M1–M4 with GT. Figure 4 switches among 25 hash-verified source images. All viewer dependencies are local, with no CDN.

The build copies the unchanged `scene.glb`/`scene.blend` pairs, downloads and verifies `GT.glb`, copies five local Three.js modules, applies registrations only at runtime, and records provenance in `data/scene_comparison.json`.

```bash
python scripts/build.py --source ../world_lobby_four_trajectory_20260929
python scripts/validate.py
python -m http.server 8765
python scripts/browser_qa.py --url http://127.0.0.1:8765/
```
