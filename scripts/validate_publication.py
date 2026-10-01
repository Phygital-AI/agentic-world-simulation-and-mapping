#!/usr/bin/env python3
"""Validate a publication checkout without access to its original sources."""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from copy import deepcopy
from collections import Counter
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit
from unittest.mock import patch

from editorial import narrative_copy, reconstruction_reductions
from site_builder_interactive import academic_page


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "en.html", "zh.html")
TITLE = "AWSM: Agentic World Simulation and Mapping — Phygital AI"
CANONICAL_ROOT = "https://phygital-ai.github.io/agentic-world-simulation-and-mapping/"
VIDEO = "assets/embodied-demo/four-robots-214924-156s-phone.mp4"
POSTER = "assets/embodied-demo/navigation-214924-poster.png"
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Document(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: list[str] = []
        self.references: list[tuple[str, str, str]] = []
        self.canonicals: list[str] = []
        self.titles: list[str] = []
        self.videos: list[dict] = []
        self._video: dict | None = None
        self.section_text: dict[str, list[str]] = {}
        self._title_depth = 0
        self._sections: list[str] = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id is not None:
            self.ids.append(element_id)
        if tag == "section":
            self._sections.append(element_id or "")
            if element_id:
                self.section_text.setdefault(element_id, [])
        if tag == "title":
            self._title_depth += 1
        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value:
                self.references.append((tag, attribute, value))
        rel = (attributes.get("rel") or "").split()
        if tag == "link" and "canonical" in rel:
            self.canonicals.append(attributes.get("href") or "")
        if tag == "video":
            self._video = {
                "attributes": attributes,
                "section": self._sections[-1] if self._sections else "",
                "sources": [],
            }
            self.videos.append(self._video)
        elif tag == "source" and self._video is not None and attributes.get("src"):
            self._video["sources"].append(attributes["src"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._title_depth -= 1
        if tag == "video":
            self._video = None
        if tag == "section" and self._sections:
            self._sections.pop()

    def handle_data(self, data: str) -> None:
        if self._title_depth:
            self.titles.append(data)
        for section_id in self._sections:
            if section_id:
                self.section_text[section_id].append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.titles).split())

    def text_for(self, section_id: str) -> str:
        return " ".join("".join(self.section_text.get(section_id, [])).split())


class PublicationValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_json("data/source_contract.json")
        cls.manifest = load_json("evidence/publication_manifest.json")
        cls.demo = load_json("data/embodied_demo.json")
        cls.documents = {name: Document(ROOT / name) for name in PAGES}

    def assert_hashed_file(self, relative_path: str, expected_sha: str, expected_bytes=None) -> None:
        self.assertIsInstance(relative_path, str)
        self.assertTrue(relative_path, "empty published path")
        self.assertRegex(expected_sha, HEX_SHA256)
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing file: {relative_path}")
        self.assertEqual(sha256(path), expected_sha, relative_path)
        if expected_bytes is not None:
            self.assertEqual(path.stat().st_size, expected_bytes, relative_path)

    def test_source_contract_published_hashes(self) -> None:
        records = list(self.contract["figures"].values())
        for model in self.contract["models"].values():
            records.extend(model.values())
        records.extend(self.contract["vendor"].values())
        records.append(self.contract["gt_asset"])
        for record in records:
            self.assert_hashed_file(record["published"], record["sha256"], record.get("bytes"))

    def test_tables_and_figures_exist_in_both_languages(self) -> None:
        required = {f"table-{number}" for number in (1, 2, 3, 6, 7)}
        required |= {f"figure-{number}" for number in range(1, 6)}
        self.assertEqual([row["number"] for row in self.contract["tables"]], list(range(1, 8)))
        for name, document in self.documents.items():
            self.assertTrue(required <= set(document.ids), f"{name}: missing {sorted(required - set(document.ids))}")
            self.assertFalse({"table-4", "table-5"} & set(document.ids), f"{name}: removed appearance tables returned")

    def test_editorial_preserves_experiment_copy(self) -> None:
        protected = (
            "intro2", "method1", "method2", "workflow", "finding1_title", "finding1", "finding2_title", "finding2",
            "finding3_title", "discussion1_title", "discussion1",
            "discussion2_title", "discussion2", "discussion3_title", "discussion3",
            "metric1", "metric1_label", "metric2", "metric2_label", "metric3", "metric3_label",
        )

        def check_copy(copy, english):
            original = deepcopy(copy)
            narrative_copy(copy, english)
            for key in protected:
                self.assertEqual(copy[key], original[key], f"{english}: {key}")
            self.assertEqual(copy["limits"][:len(original["limits"])], original["limits"])
            self.assertEqual(len(copy["contributions"]), 3)

        with patch("site_builder_interactive.narrative_copy", side_effect=check_copy):
            academic_page(True)
            academic_page(False)

    def test_narrative_roles_and_scope(self) -> None:
        sections = ["results", "motivation", "workflow", "more-results", "embodied-demo", "related-work", "limitations", "citation", "references"]
        for name, document in self.documents.items():
            self.assertEqual([element for element in document.ids if element in sections], sections)
            markup = (ROOT / name).read_text(encoding="utf-8")
            toc = re.search(r'<aside class="toc">(.*?)</aside>', markup, re.S).group(1)
            self.assertEqual(re.findall(r'href="#([^"]+)"', toc), sections)
            chinese = name == "zh.html"
            results = document.text_for("results")
            self.assertTrue(results.startswith("01 / OVERVIEW"))
            self.assertNotIn("01 / RESULTS", markup)
            self.assertIn('<a href="#results">' + ("概览" if chinese else "Overview") + '</a>', toc)
            self.assertIn('<a href="#more-results">' + ("结果与分析" if chinese else "Results & analysis") + '</a>', toc)
            self.assertTrue(document.text_for("more-results").startswith("04 / RESULTS AND ANALYSIS"))
            self.assertIn("大模型智能体" if chinese else "large-model agents", results)
            self.assertIn("agentic", results.lower())
            self.assertIn("NVIDIA Isaac Sim", results)
            self.assertNotIn("No universal winner", results)
            self.assertNotIn("PSNR, SSIM, and LPIPS disagree", results)
            self.assertLess(markup.index('id="figure-2"'), markup.index('id="figure-3"'))
            self.assertLess(markup.index('id="figure-3"'), markup.index('id="figure-4"'))
            for suffix in ("?lang=en", "shake?lang=en"):
                self.assertIn(f'href="https://office-cafe-vipe.hiwtishere.chatgpt.site/{suffix}"', markup)
            self.assertIn("可复用的仿真就绪" if chinese else "reusable simulation-ready", results)
            self.assertIn("控制器承担另一种角色" if chinese else "controllers have a separate role", document.text_for("workflow"))
            self.assertIn("而非学习得到的动力学预测模型" if chinese else "not a learned dynamics predictor", document.text_for("motivation"))
            self.assertIn("特定场景的仿真集成" if chinese else "scene-specific simulation integration", document.text_for("related-work"))

    def test_ids_links_and_anchors(self) -> None:
        for name, document in self.documents.items():
            duplicates = sorted(item for item, count in Counter(document.ids).items() if count > 1)
            self.assertFalse(duplicates, f"{name}: duplicate ids {duplicates}")
            for _tag, _attribute, reference in document.references:
                parsed = urlsplit(reference)
                if parsed.scheme or parsed.netloc or reference.startswith("//"):
                    continue
                if any(marker in reference for marker in ("{{", "}}", "${")):
                    continue
                if parsed.path:
                    relative = Path(unquote(parsed.path.lstrip("/")))
                    target = (ROOT / relative) if parsed.path.startswith("/") else (document.path.parent / relative)
                    target = target.resolve()
                    self.assertTrue(target.is_relative_to(ROOT), f"{name}: path escapes publication: {reference}")
                    self.assertTrue(target.exists(), f"{name}: broken local reference: {reference}")
                else:
                    target = document.path
                if parsed.fragment:
                    self.assertEqual(target.suffix.lower(), ".html", f"{name}: fragment targets non-HTML: {reference}")
                    target_document = self.documents.get(target.name) or Document(target)
                    self.assertIn(unquote(parsed.fragment), target_document.ids, f"{name}: broken anchor: {reference}")

    def test_manifest_files_match_bytes_and_hashes(self) -> None:
        seen: set[str] = set()
        for record in self.manifest["files"]:
            relative_path = record["path"]
            self.assertNotIn(relative_path, seen, f"duplicate manifest path: {relative_path}")
            seen.add(relative_path)
            self.assert_hashed_file(relative_path, record["sha256"], record["bytes"])

    def test_sha256sums_matches_manifest_and_files(self) -> None:
        sums: dict[str, str] = {}
        for line_number, line in enumerate((ROOT / "evidence/SHA256SUMS").read_text(encoding="utf-8").splitlines(), 1):
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            self.assertIsNotNone(match, f"SHA256SUMS:{line_number}: invalid line")
            expected_sha, relative_path = match.groups()
            self.assertNotIn(relative_path, sums, f"SHA256SUMS duplicate: {relative_path}")
            sums[relative_path] = expected_sha
            self.assert_hashed_file(relative_path, expected_sha)
        manifest_sums = {record["path"]: record["sha256"] for record in self.manifest["files"]}
        manifest_path = "evidence/publication_manifest.json"
        expected_sums = dict(manifest_sums)
        expected_sums[manifest_path] = sha256(ROOT / manifest_path)
        self.assertEqual(sums, expected_sums)

    def test_embodied_demo_metadata_and_media(self) -> None:
        media = self.demo["media"]
        self.assertEqual(media["video"], VIDEO)
        self.assertEqual(media["poster"], POSTER)
        self.assertIsInstance(media["duration_s"], (int, float))
        self.assertGreater(media["duration_s"], 0)
        self.assertIsInstance(self.demo["run_id"], str)
        self.assertTrue(self.demo["run_id"].strip())
        self.assertEqual(self.demo["audit"]["status"], "FAILED")
        self.assertEqual(self.demo["navigation"]["localization"], "simulator_pose")
        self.assertEqual(self.demo["navigation"]["route"], "predefined")
        self.assert_hashed_file(media["video"], media["sha256"], media["bytes"])
        self.assertEqual(media["duration_s"], 156.0)
        self.assertEqual(media["frame_count"], 4680)
        self.assertEqual(self.demo["run_id"], "sceneweft-walljourney-20260930-214924")
        self.assert_hashed_file(media["poster"], media["poster_sha256"])
        self.assert_hashed_file(media["hd"]["video"], media["hd"]["sha256"], media["hd"]["bytes"])
        self.assert_hashed_file(media["map"]["image"], media["map"]["sha256"], media["map"]["bytes"])
        self.assertEqual(self.demo["audit"]["measured_terminal_hold_s"], 7.994999821297824)
        audit = load_json("evidence/embodied-demo-audit.json")
        self.assertEqual(audit["run_id"], self.demo["run_id"])
        self.assertEqual([check["check"] for check in audit["failed_checks"]], ["measured_terminal_health_and_formation_hold"])
        delivery = load_json("evidence/embodied-demo-delivery.json")
        self.assertEqual(delivery["run_id"], self.demo["run_id"])
        for binding in delivery["asset_bindings"]:
            self.assert_hashed_file(binding["published"], binding["sha256"])

    def test_embodied_demo_markup_and_bilingual_copy(self) -> None:
        navigation_terms = {
            "index.html": ("navigation", "simulation"),
            "en.html": ("navigation", "simulation"),
            "zh.html": ("导航", "仿真"),
        }
        for name, document in self.documents.items():
            self.assertIn("embodied-demo", document.ids, f"{name}: missing embodied-demo section")
            matching_videos = [
                video for video in document.videos
                if video["section"] == "embodied-demo" and video["sources"] == [VIDEO]
            ]
            self.assertEqual(len(matching_videos), 1, f"{name}: expected one embodied demo video")
            self.assertEqual(
                sum(VIDEO in video["sources"] for video in document.videos),
                1,
                f"{name}: demo source must belong to exactly one video",
            )
            video = matching_videos[0]["attributes"]
            self.assertNotIn("src", video)
            self.assertEqual(video.get("poster"), POSTER)
            self.assertIn(video.get("preload", "metadata").lower(), {"none", "metadata"})
            self.assertIn("controls", video)
            self.assertIn("playsinline", video)
            self.assertNotIn("autoplay", video)
            section_text = document.text_for("embodied-demo").lower()
            for term in navigation_terms[name]:
                self.assertIn(term, section_text, f"{name}: embodied demo must state {term!r}")
            self.assertIn("20260930-214924", section_text)
            self.assertIn("2:36", section_text)
            self.assertNotIn("235.2", section_text)
            self.assertIn("demo-route-map", document.ids)

    def test_title_and_language_specific_canonical(self) -> None:
        expected = {
            "index.html": CANONICAL_ROOT,
            "en.html": CANONICAL_ROOT,
            "zh.html": CANONICAL_ROOT + "zh.html",
        }
        for name, document in self.documents.items():
            self.assertEqual(document.title, "AWSM：智能体世界仿真与建图 — Phygital AI" if name == "zh.html" else TITLE)
            self.assertEqual(document.canonicals, [expected[name]])
            markup = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('<html lang="zh-CN">' if name == "zh.html" else '<html lang="en">', markup)
            self.assertIn(f'hreflang="zh-CN" href="{CANONICAL_ROOT}zh.html"', markup)
            self.assertIn(f'hreflang="en" href="{CANONICAL_ROOT}"', markup)
            self.assertIn(f'hreflang="x-default" href="{CANONICAL_ROOT}"', markup)
            self.assertIn('<a href="zh.html"', markup)
            self.assertIn('<a href="index.html"', markup)
        self.assertEqual((ROOT / "index.html").read_bytes(), (ROOT / "en.html").read_bytes())

    def test_awsm_header(self) -> None:
        for name in PAGES:
            markup = (ROOT / name).read_text(encoding="utf-8")
            header = markup.split('<header>', 1)[1].split('</header>', 1)[0]
            chinese = name == "zh.html"
            title_name = '智能体世界仿真与建图' if chinese else 'Agentic World Simulation and Mapping'
            self.assertIn(f'<p class="title-name">{title_name}</p>', header)
            self.assertIn(f'<h1 aria-label="AWSM: {title_name}">AWSM</h1>', header)
            self.assertLess(header.index('class="title-name"'), header.index('class="title-lockup"'))
            subtitle = '把真实空间，变成虚实融合智能体可以使用的世界。' if chinese else 'From real spaces to worlds phygital agents can use.'
            lead = re.search(r'<p class="lead">(.*?)</p>', header).group(1)
            self.assertEqual(re.sub(r'<[^>]+>', '', lead), subtitle)
            emphasis = '虚实融合智能体可以使用的世界。' if chinese else 'worlds phygital agents can use.'
            self.assertIn(f'<strong class="tagline-emphasis">{emphasis}</strong>', lead)
            self.assertIn(f'<meta name="description" content="{subtitle}">', markup)
            self.assertNotIn('class="brand-tagline"', header)
            pronunciation = '读作 “awesome”' if chinese else 'pronounced “awesome”'
            self.assertIn(f'<p class="pronunciation">{pronunciation}</p>', header)
            brand_note = 'Phygital = physical（物理）+ digital（数字），即虚实融合。' if chinese else 'Phygital = physical + digital.'
            self.assertIn(f'<p class="brand-note">{brand_note}</p>', header)
            self.assertNotIn(')Phygital', header)
            self.assertNotIn('class="eyebrow"', header)
            self.assertNotIn('class="meta"', header)
            self.assertIn('@misc{awsm_2026,', markup)
            self.assertIn('title        = {{AWSM}: Agentic World Simulation and Mapping}', markup)
            self.assertNotIn('@misc{agentic_world_2026,', markup)
            self.assertIn('<time datetime="2026-10-01">', header)
            self.assertIn('2026年10月1日' if chinese else 'October 1, 2026', header)

    def test_viewer_sources_and_concurrent_work(self) -> None:
        from site_builder_interactive import SCENE_JS
        self.assertEqual((ROOT / "scene-compare.js").read_text().strip(), SCENE_JS.strip())
        manifest = json.loads((ROOT / "data/scene_comparison.json").read_text())
        self.assertGreater(manifest["camera"]["position"][1], 20)
        self.assertNotIn("mirror", manifest["display_cutaway"]["keep_name_pattern"])
        for name in PAGES:
            markup = (ROOT / name).read_text(encoding="utf-8")
            for asset in ("app.js", "scene-compare.js", "office-models.js"):
                self.assertIn(f'src="{asset}?v={sha256(ROOT / asset)[:12]}"', markup)
            self.assertIn('同期工作 AHa-3D' if name == 'zh.html' else 'Concurrent work AHa-3D', markup)
            self.assertIn('剖切视图' if name == 'zh.html' else 'Toggle Cutaway', markup)

    def test_editorial_stylesheet_cache_version(self) -> None:
        expected = f'editorial.css?v={sha256(ROOT / "editorial.css")[:12]}'
        for name in PAGES:
            markup = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(f'<link rel="stylesheet" href="{expected}">', markup)
            self.assertNotIn('href="editorial.css"', markup)

    def test_downloadable_citation(self) -> None:
        citation = (ROOT / "data/awsm.bib").read_text(encoding="utf-8")
        self.assertIn('author       = {{Phygital AI}}', citation)
        self.assertIn(f'url          = {{{CANONICAL_ROOT}}}', citation)
        for name in PAGES:
            markup = (ROOT / name).read_text(encoding="utf-8")
            rendered = re.search(r'<pre class="citation-block"><code>(.*?)</code></pre>', markup, re.S).group(1)
            self.assertEqual(unescape(rendered), citation.rstrip())
            self.assertIn('href="data/awsm.bib" download="awsm.bib"', markup)

    def test_revision_presentation_and_review_scope(self) -> None:
        for name in PAGES:
            markup = (ROOT / name).read_text()
            nav = re.search(r'<nav>(.*?)</nav>', markup, re.S).group(1)
            self.assertIn('href="https://github.com/wentingw/AWSM"', nav)
            self.assertIn('GitHub ↗', nav)
            self.assertNotIn('DATA ↗', nav)
            self.assertEqual(re.findall(r'<figure[^>]*id="figure-(\d+)"', markup), list('12345'))
            for number in range(1, 6):
                self.assertEqual(markup.count(f'Figure {number}.'), 1)
            self.assertIn('<figure id="figure-2"><img loading="lazy" src="assets/fixed_five_view_comparison_m1_m4.jpg"', markup)
            self.assertIn('class="scene-comparison" id="figure-3"', markup)
            self.assertIn('class="fixed-comparison" id="figure-4"', markup)
            self.assertIn('class="hero" id="overview-video"', markup)
            self.assertNotIn('figure-1-caption', markup)
            self.assertNotIn('AWSM: from real spaces to worlds phygital agents can use.', markup)
            for phrase in ('7.994999821', 'unresolved audit failures', 'did not pass every task-audit', 'We discuss it as a parallel effort', '前置工作', '未通过的审计项', '尚未通过全部任务审计', '源运行报告飞行任务'):
                self.assertNotIn(phrase, markup)
            self.assertIn('让机器人前往前台，并在那里排成一列。' if name=='zh.html' else 'Send the robots to the reception desk and have them line up there.', markup)
            self.assertIn('已完成人工审阅' if name=='zh.html' else 'manually reviewed', markup)
            self.assertIn('不改变其原始判定' if name=='zh.html' else 'does not revise their recorded verdicts', markup)
            self.assertEqual(markup.count('data-office-external='), 2)
            self.assertIn('并非外站页面截图' if name=='zh.html' else 'not screenshots of the external website', markup)
        self.assertEqual(self.demo['audit']['status'], 'FAILED')

    def test_tldr_reductions_and_task_scope(self) -> None:
        surface, depth = reconstruction_reductions()
        self.assertAlmostEqual(surface, 80.95096, places=3)
        self.assertAlmostEqual(depth, 53.77076, places=3)
        for name, document in self.documents.items():
            markup = (ROOT / name).read_text()
            chinese = name == 'zh.html'
            summary = re.search(r'<aside class="tldr"><strong>TL;DR</strong><p>(.*?)</p>', markup).group(1)
            for term in ('IMU', 'M1', 'M4', '81%', '54%'):
                self.assertIn(term, summary)
            self.assertIn('真值位姿条件' if chinese else 'GT-pose-conditioned', summary)
            self.assertIn('预设路线' if chinese else 'predefined routes', summary)
            self.assertIn('180 个评估视角' if chinese else '180 evaluation views', document.text_for('results'))
            self.assertEqual(markup.count('class="metric-reduction"'), 2)
            self.assertNotIn('180 度', document.text_for('results'))
            self.assertIn('相对降低约 81%' if chinese else '≈81% relative reduction', markup)
            self.assertIn('相对降低约 54%' if chinese else '≈54% relative reduction', markup)


if __name__ == "__main__":
    unittest.main(verbosity=2)
