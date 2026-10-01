# AWSM: Agentic World Simulation and Mapping

From real spaces to worlds phygital agents can use.

AWSM is pronounced “awesome”; phygital means physical + digital.

The bilingual masthead follows the supplied title reference: a small full name, a large serif AWSM wordmark with an adjacent pronunciation note, and a green-accented tagline. It shares a responsive, left-aligned content width with Figure 1, the supplied `assets/awsm-promo-v5.mp4` (copied without re-encoding). Its one-time entrance animation respects reduced-motion preferences. Citation text and the downloadable `data/awsm.bib` are generated from the same BibTeX source in `scripts/editorial.py`.

The generated pages version `editorial.css` and `app.js` by their content hashes so returning visitors request the updated styling and table text after a deployment. Table 1 body translations and the M1–M4 short method names used in all seven tables live in `app.js`; the frozen numerical table data remains unchanged.

Bilingual research article by Phygital AI: geometry-grounded agentic scene reconstruction, map-based embodied execution, and a research agenda for persistent spatial memory, interaction, and simulation.

The narrative distinguishes the tool-using reconstruction agent from downstream embodied agents. Geometry grounding is the approach, the four-route study supplies reconstruction evidence, and the demo illustrates map-based use. Persistent memory and maintenance, reusable simulation-ready generation, and deeper phygital-agent integration remain research directions. Narrative edits must preserve the measured findings, method-specific inputs, evaluation caveats, and supplied media.

The homepage (`index.html`) defaults to English. Chinese is at `zh.html`, titled **AWSM：智能体世界仿真与建图**. The existing `en.html` URL remains an English alias with the homepage as its canonical URL.

The original structure, seven experiment tables, six figures, frozen `scene.glb`/`scene.blend` pairs, and interactive comparisons are preserved from `wentingw/agentic-world-blog` at `3c5f27c`. Figure 3 shares a camera and viewport with GT; Figure 4 uses 25 hash-verified source images. All viewer dependencies are local.

The reception-desk demo illustrates map-based navigation using predefined routes and simulator-pose feedback. The 156-second delivery from run `20260930-214924` provides a mobile playback version, HD download, and a full-resolution planned-route map. Supplied media are copied without re-encoding; protocol and audit status are in `data/embodied_demo.json`. Read `evidence/provenance-note.md` for edit boundaries, upstream naming discrepancies, and source-record hashes.

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
