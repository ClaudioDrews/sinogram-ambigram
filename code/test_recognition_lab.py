"""Static and source-level regression checks for the native-reader recognition lab.

These checks cannot certify visual appearance, upstream network availability,
human readability or the correctness of real participants' semantic reports.
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
PILOT = ROOT / "evaluation" / "items.json"


class TestNativeReaderRecognitionLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_exclusive_track_selection_and_localisation(self):
        html = self.html
        self.assertIn('name="sourceTrack" value="cn"', html)
        self.assertIn('name="sourceTrack" value="jp"', html)
        self.assertIn('role="radiogroup"', html)
        for locale in ('en', 'zh', 'ja'):
            self.assertIn(f'data-lang="{locale}"', html)
        self.assertIn("track=chosen.value", html)
        self.assertIn("if(which==='jp')", html)
        self.assertIn("}else if(which==='cn')", html)
        self.assertIn("items=sample;track=which", html)

    def test_chinese_fused_geometry_without_animated_external_images(self):
        html = self.html
        self.assertIn("fetch('../../prc/catalog.json'", html)
        self.assertIn('prc-public-coarse-catalog-v1', html)
        self.assertIn('source_forms_certified!==false', html)
        self.assertIn('bddc96d41bef78427ed0e034e9f7e31d71fd1b92', html)
        self.assertIn("function sourceOutline(ch)", html)
        self.assertIn("function chineseComposite(item,animated)", html)
        self.assertIn("getAttribute('fill')==='lightgray'", html)
        self.assertIn("kind:'source-union-diagnostic'", html)
        self.assertIn("method:'prc-source-vector-union'", html)
        self.assertNotIn("id=\"cnArt\"", html)
        self.assertNotIn("id=\"cnA\"", html)
        self.assertNotIn("id=\"cnB\"", html)
        self.assertEqual(html.count('id="drawing"'), 1)

    def test_japanese_committed_pilot_survives_optional_geometry_failure(self):
        html = self.html
        self.assertIn("fetch('../items.json'", html)
        self.assertIn("sample.length<12", html)
        self.assertIn("Optional Rotation Lab example unavailable", html)
        self.assertIn("[...pathsA,...pathsB].forEach(p=>svg.appendChild(p))", html)
        self.assertIn("svg.removeAttribute('style')", html)
        data = json.loads(PILOT.read_text(encoding="utf-8"))
        samples = [
            item for stratum in ('v1-top', 'v2-top', 'self', 'control')
            for item in [r for r in data['items'] if r['stratum'] == stratum][:3]
        ]
        self.assertEqual(len(samples), 12)
        self.assertTrue(all(s['construction_svg'].startswith('<svg') for s in samples))

    def test_construction_then_single_image_rotates_and_dark_mode_contrast(self):
        html = self.html
        self.assertIn(".stage{background:#fcfaf4;", html)
        self.assertIn(".compare figure{margin:0;background:#fcfaf4;", html)
        self.assertIn("shownItemId!==it.id", html)
        self.assertIn("im.src=toData(reduced?it.svg:(it.animatedSvg||it.svg))", html)
        self.assertIn("im.style.transform='rotate(180deg)'", html)
        self.assertIn("view.src=toData(it.svg)", html)
        self.assertIn("animationBusy", html)
        self.assertIn("matchMedia('(prefers-reduced-motion: reduce)')", html)

    def test_independent_meaning_judgments_and_exports(self):
        html = self.html
        self.assertIn('id="meaningOptions"', html)
        self.assertIn('id="meaningGloss"', html)
        self.assertIn("if(status!==2&&meaning===null)", html)
        self.assertIn("both_meaningful_reported:", html)
        self.assertIn("schema:'native-reader-exploratory-v2'", html)
        self.assertIn("'meaning_gloss_a'", html)
        self.assertIn("'meaning_gloss_b'", html)
        self.assertIn("expected_a:it.a", html)
        self.assertIn("expected_b:it.b", html)
        self.assertIn("download('sinogram-reader-'+", html)
        self.assertNotIn('method: "POST"', html)

    def test_javascript_syntax_if_node_available(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js not present (static assertions still run)')
        html = self.html
        scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
        self.assertEqual(len(scripts), 1)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'recognition.js'
            path.write_text(scripts[0], encoding='utf-8')
            process = subprocess.run([node, '--check', str(path)],
                                     capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)


if __name__ == '__main__':
    unittest.main()
