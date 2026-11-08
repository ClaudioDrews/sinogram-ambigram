"""Smoke-test the two independent material tracks in the native-reader lab.

Tests cover static provenance, track exclusivity logic, export-schema fields
and manifest guards. A full browser perceptual evaluation is still required.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "evaluation" / "recognition" / "index.html"


class TestNativeReaderRecognitionLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_exclusive_entry_choice_and_3_languages(self):
        self.assertIn('name="sourceTrack" value="cn"', self.html)
        self.assertIn('name="sourceTrack" value="jp"', self.html)
        self.assertIn('role="radiogroup"', self.html)
        self.assertIn('data-lang="en"', self.html)
        self.assertIn('data-lang="zh"', self.html)
        self.assertIn('data-lang="ja"', self.html)
        self.assertIn("track=chosen.value", self.html)
        self.assertIn("if(which==='jp')", self.html)
        self.assertIn("}else if(which==='cn')", self.html)
        self.assertIn("items=sample;track=which", self.html)
        self.assertIn("track,respondent", self.html)

    def test_pinned_source_provenance_and_no_post_request(self):
        self.assertIn("fetch('../items.json'", self.html)
        self.assertIn("fetch('../../prc/catalog.json'", self.html)
        self.assertIn("prc-public-coarse-catalog-v1", self.html)
        self.assertIn("source_forms_certified!==false", self.html)
        self.assertIn("bddc96d41bef78427ed0e034e9f7e31d71fd1b92", self.html)
        self.assertIn("native-reader-exploratory-v1", self.html)
        self.assertIn("source-overlay-diagnostic", self.html)
        self.assertIn("constructed-pilot", self.html)
        self.assertNotRegex(self.html, r"fetch\\s*\\([^)]*method\\s*:\\s*['\\\"]POST")

    def test_blind_then_reveal_and_manual_exports(self):
        self.assertIn("expected_a:it.a", self.html)
        self.assertIn("expected_b:it.b", self.html)
        self.assertIn("if(phase==='relation')", self.html)
        self.assertIn("if(status===0&&!reading)", self.html)
        self.assertIn("download('sinogram-reader-' +", self.html.replace("download('sinogram-reader-'+", "download('sinogram-reader-' +"))
        self.assertIn("track==='jp'?", self.html)
        self.assertIn('id="summary"', self.html)


if __name__ == "__main__":
    unittest.main()
