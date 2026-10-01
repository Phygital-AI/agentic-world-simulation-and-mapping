# AWSM: Agentic World Simulation and Mapping

From real spaces to worlds phygital agents can use.

AWSM is pronounced “awesome”; phygital means physical + digital.

The bilingual masthead follows the supplied title reference: a small full name, a large serif AWSM wordmark with an adjacent pronunciation note, and a green-accented tagline. It shares a responsive, left-aligned content width with Figure 1, the supplied `assets/awsm-promo-v5.mp4` (copied without re-encoding). Its one-time entrance animation respects reduced-motion preferences. Citation text and the downloadable `data/awsm.bib` are generated from the same BibTeX source in `scripts/editorial.py`.

The generated pages version `editorial.css` and `app.js` by their content hashes so returning visitors request the updated styling and table text after a deployment. Table 1 body translations and the M1–M4 short method names used in the visible tables live in `app.js`; the frozen numerical table data remains unchanged.

Bilingual research article by Phygital AI: geometry-grounded agentic scene reconstruction, map-based embodied execution, and a research agenda for persistent spatial memory, interaction, and simulation.

The narrative distinguishes the tool-using reconstruction agent from downstream embodied agents. Geometry grounding is the approach, the four-route study supplies reconstruction evidence, and the demo illustrates map-based use. Persistent memory and maintenance, reusable simulation-ready generation, and deeper phygital-agent integration remain research directions. Narrative edits must preserve the measured findings, method-specific inputs, evaluation caveats, and supplied media.

The homepage (`index.html`) defaults to English. Chinese is at `zh.html`, titled **AWSM：智能体世界仿真与建图**. The existing `en.html` URL remains an English alias with the homepage as its canonical URL.

The page displays five experiment tables (Tables 1–3, 6–7); appearance Tables 4–5 are omitted. The frozen JSON retains all seven source tables. The six figures, frozen `scene.glb`/`scene.blend` pairs, and interactive comparisons are preserved from `wentingw/agentic-world-blog` at `3c5f27c`. Figure 4 shares a camera and viewport with GT; Figure 5 uses 25 hash-verified source images. All viewer dependencies are local.

The reconstruction results precede the embodied demo. The original five-view overview is now Figure 3, the interactive model comparison is Figure 4, and the fixed-view selector is Figure 5; captions, anchors, CSS, and runtime selectors use these numbers. The World Lobby scene and the embodied simulation are identified as NVIDIA Isaac Sim content.

The authors confirm that the reception-desk demonstration has been manually reviewed. Presentation copy distinguishes that review from historical automated checks; the original audit JSON, logs, recorded verdicts, and experiment/media hashes are not edited to imply an automated PASS.

Office Café includes original-app links, on-demand embedded views requesting `lang=en`, and labeled local content previews from the published videos. The external host controls actual language and availability. Both external routes returned Cloudflare HTTP 403 during the 1 October 2026 check, so the local previews are explicitly not described as captures of the external website. The verified code-repository URL is `https://github.com/wentingw/AWSM` (`wentingw/sceneweft` redirects there); it is currently private. Publication still uses the separate `phygital` remote, `Phygital-AI/agentic-world-simulation-and-mapping`.

The reception-desk demo illustrates map-based navigation using predefined routes and simulator-pose feedback. The 156-second delivery from run `20260930-214924` provides a mobile playback version, HD download, and a full-resolution planned-route map. Supplied media are copied without re-encoding; protocol and audit status are in `data/embodied_demo.json`. Read `evidence/provenance-note.md` for edit boundaries, upstream naming discrepancies, and source-record hashes.

## Office Café video playback

The three synchronized videos load MP4 files from `assets/office-cafe/` on the same GitHub Pages origin. The web editions use H.264 Constrained Baseline with fast-start MP4 metadata, a 4 Mbps rate cap and fast decoding; all three retain 960×540, 30 fps, 2,103 frames and 70.1 seconds. Original files remain in the `office-media-20261001` release. Source and playback-file hashes are recorded separately in `data/office_video_media.json`.

The player waits for all three videos, corrects drift, retries transient play cancellations, and reloads failed sources when the shared play button is pressed.

## Edit and validate

`scripts/editorial.py` holds the bilingual narrative additions; `scripts/site_builder_interactive.py` retains the frozen article template. The standard build only regenerates pages and publication hashes. It never rebuilds models, changes experiment data, downloads source assets, or removes directories.

```bash
python scripts/build.py
python scripts/render.py --check
python scripts/validate.py
python -m http.server 8765
python scripts/browser_qa.py --url http://127.0.0.1:8765/
```

Browser QA requires the packages in `requirements.txt` and a Playwright Chromium installation. The separate historical `site_builder.py` / `site_validator.py` scripts require the original source dataset and are not part of the publication build.

## Publish

Repository: https://github.com/Phygital-AI/agentic-world-simulation-and-mapping

Website: https://phygital-ai.github.io/agentic-world-simulation-and-mapping/

Authenticate GitHub CLI outside this repository, commit the reviewed changes, then run `python scripts/publish.py`. The publisher checks the organization, repository, clean worktree, frozen assets, and non-force push. It uses the CLI credential store; never place access tokens in this repository or remote URLs.
