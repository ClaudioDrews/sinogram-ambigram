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
        self.assertNotIn('data-lang="en"', h)
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

    def test_sources_are_constructed_and_track_specific(self):
        h = self.html
        self.assertIn("fetch('../items.json')", h)
        self.assertIn("['v1-top','v2-top']", h)
        self.assertIn("selected.length!==12", h)
        self.assertIn("fetch('../../prc/catalog.json')", h)
        self.assertIn("prc-public-coarse-catalog-v1", h)
        self.assertIn("human_readability_validated!==false", h)
        self.assertIn("function composite(pathsA,pathsB)", h)
        self.assertIn("getAttribute('fill')==='lightgray'", h)
        self.assertIn("bddc96d41bef78427ed0e034e9f7e31d71fd1b92", h)
        items=json.loads(ITEMS.read_text(encoding="utf-8"))['items']
        chosen=[r for group in ('v1-top','v2-top') for r in [it for it in items if it['stratum']==group][:6]]
        self.assertEqual(len(chosen), 12)
        self.assertTrue(all('<svg' in item['construction_svg'] for item in chosen))

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
