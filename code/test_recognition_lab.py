"""Regression checks for the minimal native-reader gallery.

Static structural assertions and JS parsing cannot substitute for testing rotation,
visual glyph readability, and download behavior in real browsers.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "evaluation" / "recognition" / "index.html"
ITEMS = ROOT / "evaluation" / "items.json"


class TestRecognitionGallery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_only_two_language_choices_and_no_profile_form(self):
        h = self.html
        self.assertIn('id="choose-cn"', h)
        self.assertIn('id="choose-jp"', h)
        self.assertEqual(h.count('class="language-card"'), 2)
        self.assertNotIn('id="proficiency"', h)
        self.assertNotIn('id="native"', h)
        for code in ('en','zh','ja'):
            self.assertIn(f'data-intro-lang="{code}"', h)
        self.assertEqual(h.count('data-intro-lang="'), 3)
        self.assertIn('id="introLangs"', h)
        self.assertIn("setIntroLanguage('en')", h)
        self.assertIn("button.dataset.introLang===code", h)
        self.assertIn("id!=='home'", h)
        self.assertIn("track==='cn'?'zh-Hans':'ja'", h)
        self.assertIn("function setIntroLanguage(code)", h)
        self.assertIn("start('cn')", h)
        self.assertIn("start('jp')", h)

    def test_same_static_svg_animated_on_user_tap(self):
        h = self.html
        self.assertIn('id="rotate"', h)
        self.assertEqual(h.count('id="glyph"'), 1)
        self.assertIn("'rotate('+degrees+'deg)'", h)
        self.assertIn("turns+=1", h)
        self.assertIn("180*turns", h)
        self.assertIn("transition:transform 950ms", h)
        self.assertIn("addEventListener('click',rotate)", h)
        self.assertIn("if(turns<1)", h)
        self.assertNotIn("animateTransform", h)
        self.assertNotIn("prefers-reduced-motion", h)
        self.assertIn("background:var(--sheet)", h)

    def test_exactly_three_meaning_answers_and_one_note(self):
        h = self.html
        self.assertIn('id="choices"', h)
        self.assertIn('name=\'assessment\'', h)
        self.assertIn('id="note"', h)
        self.assertIn("value=String(2-index)", h)
        self.assertIn("meaning_orientations:Number(answer.value)", h)
        self.assertIn("t.choices.forEach((label,index)", h)
        self.assertIn("$('method-value').textContent=methodText(item.method)", h)

    def test_curated_sources_and_methods_are_provenance_distinct(self):
        h = self.html
        self.assertIn("fetch('stimuli.json')", h)
        self.assertIn("fetch('../../prc/catalog.json')", h)
        self.assertIn("prc-public-coarse-catalog-v1", h)
        self.assertIn("human_readability_validated!==false", h)
        self.assertIn("function composite(pathsA,pathsB)", h)
        self.assertIn("function single(paths)", h)
        self.assertIn("getAttribute('fill')==='lightgray'", h)
        self.assertIn("bddc96d41bef78427ed0e034e9f7e31d71fd1b92", h)
        self.assertIn("jpPoints(d)", h)
        self.assertIn("jpProximity(", h)
        self.assertIn("if(row.method==='jp-shared'&&ratio<.35)return", h)

        curated = json.loads((PAGE.parent / 'stimuli.json').read_text(encoding="utf-8"))
        self.assertEqual(curated['schema'], 'sinogram-reader-curated-methods-v2')
        self.assertEqual(len(curated['jp']), 20)
        self.assertEqual(len(curated['cn']), 9)
        self.assertEqual(
            {row['method'] for row in curated['jp']},
            {'jp-natural-self', 'jp-natural-pair', 'jp-overlay',
             'jp-salience', 'jp-shared', 'jp-c2-blend',
             'jp-gpt-raster-iou', 'jp-glm-translated-iou', 'jp-claude-skeleton-f1',
             'jp-claude-w1-warp', 'jp-kimi-fft-iou', 'jp-mistral-medians', 'jp-minimax-rotgraph'}
        )
        self.assertEqual(
            {row['method'] for row in curated['cn']},
            {'cn-natural-self', 'cn-natural-pair', 'cn-source-union'}
        )
        # Historical audit records remain in the manifest for provenance.
        self.assertEqual(len(curated['cn_unillustrated']), 7)
        self.assertIn("fetch('generated/manifest.json')", h)
        self.assertIn("item.url||svgData(item.svg)", h)
        self.assertIn("selected_center", h)
        self.assertTrue(all('KanjiVG' in row['source'] for row in curated['jp']))
        self.assertTrue(all('Make Me a Hanzi' in row['source'] for row in curated['cn']))
        self.assertTrue(all(curated['jp_glyphs'].get(row['a']) for row in curated['jp']))
        self.assertTrue(all(curated['jp_glyphs'].get(row['b']) for row in curated['jp']))
        self.assertTrue(all(row['type'] in ('natural-self','natural-pair','constructed','search-illustration')
                            for row in curated['jp'] + curated['cn']))
        self.assertFalse(any(row['method'] in {m['id'] for m in curated['cn_unillustrated']}
                             for row in curated['cn']))

        # Keep the original, independently defined 48-item human-evaluation pilot untouched.
        historic = json.loads(ITEMS.read_text(encoding='utf-8'))['items']
        self.assertEqual(len(historic), 48)
        self.assertTrue(all('<svg' in row['construction_svg'] for row in historic))

    def test_method_and_status_are_visible_and_exported(self):
        h = self.html
        self.assertIn('id="type-value"', h)
        self.assertIn('id="method-inventory-link"', h)
        self.assertIn("status:item.status", h)
        self.assertIn("type:item.type", h)
        self.assertIn("'method','type','status','source','svg_sha256'", h)
        self.assertIn("methodLabels[track][method]", h)

    def test_csv_and_txt_are_optional_local_downloads(self):
        h = self.html
        self.assertIn('id="download-csv"', h)
        self.assertIn('id="download-txt"', h)
        self.assertIn("new Blob([body]", h)
        self.assertIn("URL.createObjectURL(blob)", h)
        self.assertIn("link.click()", h)
        self.assertNotIn("fetch('/submit'", h)
        self.assertNotIn('type="email"', h)

    def test_js_parses_with_node_if_available(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js not installed")
        scripts = re.findall(r"<script>(.*?)</script>", self.html, re.DOTALL)
        self.assertEqual(len(scripts), 1)
        with tempfile.TemporaryDirectory() as tmp:
            js = Path(tmp) / "gallery.js"
            js.write_text(scripts[0], encoding="utf-8")
            result = subprocess.run([node, "--check", str(js)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
