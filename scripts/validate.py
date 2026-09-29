#!/usr/bin/env python3
"""Check evidence identity, published numbers, local links and asset references."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.links, self.ids = path, [], set()
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate ID {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ['src', 'href']:
            if key in attrs: self.links.append(attrs[key])

pages = {p.name:Page(p) for p in [ROOT/'index.html',ROOT/'en.html']}
for page in pages.values():
    for link in page.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        target=(page.path.parent/unquote(u.path)).resolve() if u.path else page.path
        assert target.is_relative_to(ROOT) and target.exists(), f'Broken local link: {link}'
        if u.fragment and target.suffix == '.html':
            doc=pages.get(target.name) or Page(target)
            assert unquote(u.fragment) in doc.ids, f'Broken anchor: {link}'
    assert '{{' not in page.path.read_text(), 'Unexpanded template'
for row in json.loads((ROOT/'data/source_manifest.json').read_text()):
    p=ROOT/row['published_path']
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], p
summary=json.loads((ROOT/'data/summary.json').read_text())
for lang in ['zh','en']:
    source=(ROOT/f'article.{lang}.md').read_text()
    for split in ['modeling_180','eval_500']:
        for method in summary['depth'][split]['methods'].values():
            m=method['primary_no_scale_fit']
            for text in [f'{m["rmse_m"]:.4f}',f'{m["absrel"]*100:.2f}%',f'{m["valid_coverage"]*100:.2f}%',f'{m["missing_penalty_mae_m"]:.4f}']:
                assert text in source, f'Missing numerical value {text}'
for p in ROOT.rglob('*'):
    if not p.is_file() or any(part in ['.git','qa','__pycache__'] for part in p.parts):continue
    if p.suffix in ['.md','.html','.json','.js','.py','.css']:
        s=p.read_text()
        assert not re.search(r'(?:github_pat_[A-Za-z0-9_]{25,}|gh[pousr]_[A-Za-z0-9_]{25,})',s), f'Credential pattern: {p}'
        assert p.stat().st_size < 10_000_000, f'Oversized text asset: {p}'
print(json.dumps({'status':'PASS','pages':len(pages),'evidence_files':len(json.loads((ROOT/'data/source_manifest.json').read_text())),'checks':['local links and anchors','evidence SHA256','numerical values','credential scan']}))
