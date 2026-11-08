"""Static regression checks for the public research-method inventory.

These assertions verify provenance and navigation, not human readability or
pixel-level equivalence of the experimental geometric renderers.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'href' in d:
            self.hrefs.append(d['href'])
        if 'id' in d:
            self.ids.append(d['id'])


class TestResearchSiteInventory(unittest.TestCase):
    def test_methods_page_is_trilingual_and_syntactically_valid(self):
        html = (ROOT / 'methods' / 'index.html').read_text(encoding='utf-8')
        self.assertIn("draw('en')", html)
        for lang in ('en', 'zh', 'ja'):
            self.assertIn('data-lang="' + lang + '"', html)
        for group in ('jp-search', 'jp-visual', 'cn-search', 'cn-build'):
            self.assertIn('id="' + group + '"', html)
        self.assertIn('R-ODD', html)
        self.assertIn('Harmonic', html)
        self.assertIn('A/B stroke fusion', html)
        self.assertIn('MiniMax', html)
        self.assertIn('Concept', html)
        self.assertIn('Negative / null result', html)

        node = shutil.which('node')
        if node:
            scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
            self.assertEqual(len(scripts), 1)
            with tempfile.TemporaryDirectory() as tmp:
                js = Path(tmp) / 'methods.js'
                js.write_text(scripts[0], encoding='utf-8')
                proc = subprocess.run([node, '--check', str(js)],
                                      capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_site_navigation_resolves_and_ids_are_unique(self):
        for relative in ('index.html', 'methods/index.html', 'prc/index.html',
                         'demo/c2/index.html', 'evaluation/recognition/index.html'):
            path = ROOT / relative
            self.assertTrue(path.exists(), relative)
            links = Links()
            links.feed(path.read_text(encoding='utf-8'))
            self.assertEqual(len(links.ids), len(set(links.ids)), relative)
            for href in links.hrefs:
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or href.startswith('#'):
                    continue
                target = unquote(parsed.path)
                if not target:
                    continue
                local = (path.parent / target).resolve()
                self.assertTrue(local.is_relative_to(ROOT), f'{relative}: {href}')
                self.assertTrue(local.exists(), f'{relative}: {href}')

    def test_research_inventory_and_readmes_expose_two_tracks(self):
        root = (ROOT / 'README.md').read_text(encoding='utf-8')
        audit = (ROOT / 'methods/RESEARCH_TRACKS.md').read_text(encoding='utf-8')
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        for method in ('GPT', 'GLM', 'Claude v1', 'Claude v2', 'Kimi',
                       'Mistral', 'MiniMax', 'R-ODD', 'harmonic', 'A/B fusion',
                       'rotation-centre', 'thickness'):
            self.assertIn(method.lower(), (root + audit).lower())
        self.assertIn('7', root)
        self.assertIn('Chinese', root)
        self.assertIn('Japanese', root)
        self.assertIn('2,770', home)
        self.assertIn('6,763', home)
        self.assertIn('href="methods/"', home)
        self.assertIn('methods/index.html', root)
        self.assertIn('v1-top', audit)
        for relative in ('docs/zh/README.md', 'docs/ja/README.md'):
            self.assertIn('/methods/', (ROOT / relative).read_text(encoding='utf-8'))

    def test_all_24_method_pages_have_real_examples_or_honest_input_illustrations(self):
        catalog = json.loads((ROOT / 'methods/catalog.json').read_text('utf-8'))
        methods = catalog['methods']
        self.assertEqual(len(methods), 24)
        self.assertEqual(sum(m['track'] == 'jp' for m in methods), 13)
        self.assertEqual(sum(m['track'] == 'cn' for m in methods), 11)
        index = (ROOT / 'methods/index.html').read_text('utf-8')
        detail = (ROOT / 'methods/detail.js').read_text('utf-8')
        self.assertIn('methodSlugs=', index)
        self.assertIn('requestAnimationFrame', detail)
        for method in methods:
            page = ROOT / 'methods' / method['slug'] / 'index.html'
            self.assertTrue(page.exists(), method['slug'])
            html = page.read_text('utf-8')
            self.assertIn('data-method="' + method['slug'] + '"', html)
            self.assertIn('id="rotation"', html)
            self.assertIn('id="play"', html)
            self.assertIn('id="visual"', html)
            self.assertIn('detail.js', html)
        jp = json.loads((ROOT/'evaluation/recognition/stimuli.json').read_text('utf-8'))['jp']
        cn = json.loads((ROOT/'evaluation/recognition/generated/manifest.json').read_text('utf-8'))['items']
        represented = {x['method'] for x in jp + cn}
        self.assertEqual(represented, {x['slug'] for x in methods})
        node = shutil.which('node')
        if node:
            proc = subprocess.run([node, '--check', str(ROOT/'methods/detail.js')],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_gallery_does_not_mislabel_unimplemented_methods(self):
        data = json.loads((ROOT / 'evaluation/recognition/stimuli.json').read_text('utf-8'))
        self.assertEqual(data['schema'], 'sinogram-reader-curated-methods-v2')
        self.assertTrue(data['jp_source_pin'].startswith('KanjiVG'))
        self.assertTrue(data['cn_source_pin'].startswith('skishore'))
        unshown = {x['id'] for x in data['cn_unillustrated']}
        shown = {x['method'] for x in data['cn']}
        self.assertFalse(unshown & shown)
        self.assertEqual(shown, {'cn-natural-self', 'cn-natural-pair', 'cn-source-union'})
        built = json.loads((ROOT/'evaluation/recognition/generated/manifest.json').read_text('utf-8'))
        self.assertEqual(built['schema'], 'sinogram-prc-method-examples-v1')
        self.assertEqual(len(built['items']), 22)
        self.assertEqual(len({x['method'] for x in built['items']}), 11)
        for item in built['items']:
            self.assertTrue((ROOT/'evaluation/recognition/generated'/item['file']).exists(), item['id'])
        self.assertEqual({x['type'] for x in data['jp']},
                         {'natural-self', 'natural-pair', 'constructed', 'search-illustration'})
        self.assertIn('no native reader', data['evidence'].lower())
        self.assertEqual(len(json.loads((ROOT / 'evaluation/items.json').read_text('utf-8'))['items']), 48)


if __name__ == '__main__':
    unittest.main()
