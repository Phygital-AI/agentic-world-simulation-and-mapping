#!/usr/bin/env python3
"""Validate a publication checkout without access to its original sources."""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "en.html", "zh.html")
TITLE = "Agentic World Simulation and Mapping — Phygital AI"
CANONICAL_ROOT = "https://phygital-ai.github.io/agentic-world-simulation-and-mapping/"
VIDEO = "assets/embodied-demo/world-lobby-four-robots.mp4"
POSTER = "assets/embodied-demo/poster.jpg"
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
        required = {f"table-{number}" for number in range(1, 8)}
        required |= {f"figure-{number}" for number in range(1, 7)}
        self.assertEqual([row["number"] for row in self.contract["tables"]], list(range(1, 8)))
        for name, document in self.documents.items():
            self.assertTrue(required <= set(document.ids), f"{name}: missing {sorted(required - set(document.ids))}")

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

    def test_title_and_language_specific_canonical(self) -> None:
        expected = {
            "index.html": CANONICAL_ROOT,
            "en.html": CANONICAL_ROOT,
            "zh.html": CANONICAL_ROOT + "zh.html",
        }
        for name, document in self.documents.items():
            self.assertEqual(document.title, "智能体世界仿真与建图 — Phygital AI" if name == "zh.html" else TITLE)
            self.assertEqual(document.canonicals, [expected[name]])
            markup = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('<html lang="zh-CN">' if name == "zh.html" else '<html lang="en">', markup)
            self.assertIn(f'hreflang="zh-CN" href="{CANONICAL_ROOT}zh.html"', markup)
            self.assertIn(f'hreflang="en" href="{CANONICAL_ROOT}"', markup)
            self.assertIn(f'hreflang="x-default" href="{CANONICAL_ROOT}"', markup)
            self.assertIn('<a href="zh.html"', markup)
            self.assertIn('<a href="index.html"', markup)
        self.assertEqual((ROOT / "index.html").read_bytes(), (ROOT / "en.html").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
