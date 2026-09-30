#!/usr/bin/env python3
"""Render narrative-only updates without rebuilding any frozen experiment asset."""

import argparse
import hashlib
import json
from pathlib import Path

from site_builder_interactive import academic_page


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT_FILES = (".nojekyll", "index.html", "en.html", "style.css", "editorial.css", "app.js", "scene-compare.js")
PUBLIC_DIRECTORIES = ("assets", "data", "evidence", "models", "vendor")
GENERATED_MANIFESTS = ("evidence/publication_manifest.json", "evidence/SHA256SUMS")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publication_records():
    paths = [ROOT / name for name in PUBLIC_ROOT_FILES]
    for directory in PUBLIC_DIRECTORIES:
        paths.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    return [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in sorted(paths)
        if path.relative_to(ROOT).as_posix() not in GENERATED_MANIFESTS
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated pages and hashes without writing")
    args = parser.parse_args()
    for name, english in (("index.html", False), ("en.html", True)):
        content = academic_page(english) + "\n"
        target = ROOT / name
        if args.check:
            if target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale generated page: {name}")
        else:
            target.write_text(content, encoding="utf-8")
    records = publication_records()
    manifest = json.dumps({"schema_version": 2, "source_contract": "data/source_contract.json", "files": records}, ensure_ascii=False, indent=2) + "\n"
    manifest_path = ROOT / GENERATED_MANIFESTS[0]
    if args.check:
        if manifest_path.read_text(encoding="utf-8") != manifest:
            raise SystemExit("Stale publication manifest")
    else:
        manifest_path.write_text(manifest, encoding="utf-8")
    sums = "\n".join(f'{record["sha256"]}  {record["path"]}' for record in records)
    sums += f"\n{sha256(manifest_path)}  {GENERATED_MANIFESTS[0]}\n"
    if args.check:
        if (ROOT / GENERATED_MANIFESTS[1]).read_text(encoding="utf-8") != sums:
            raise SystemExit("Stale SHA256SUMS")
    else:
        (ROOT / GENERATED_MANIFESTS[1]).write_text(sums, encoding="utf-8")
    print(json.dumps({"status": "CHECKED" if args.check else "RENDERED", "pages": 2, "published_files": len(records), "frozen_experiment_assets_rebuilt": False}))


if __name__ == "__main__":
    main()
