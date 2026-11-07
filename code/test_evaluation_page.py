"""Exercise the real, offline reading-evaluation page builder."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / 'evaluation'

class TestEvaluationPage(unittest.TestCase):
    def test_built_page_contains_48_renders_and_multilingual_copy(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'test.html'
            result=subprocess.run([sys.executable,str(EVAL/'build_page.py'), '--out',str(dest)],cwd=ROOT,capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            html=dest.read_text(encoding='utf8')
            self.assertIn('"pilot-048"',html)
            self.assertNotIn('"items":[]',html)
            self.assertIn('"ja":',html)
            self.assertIn('"en":',html)
            self.assertNotIn('。=参加',html)
            self.assertNotIn('您的評価',html)
            self.assertEqual(len(json.loads((EVAL/'items.json').read_text(encoding='utf8'))['items']),48)
    def test_public_page_equals_build_product(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'test.html'
            subprocess.run([sys.executable,str(EVAL/'build_page.py'), '--out',str(dest)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
            self.assertEqual(dest.read_bytes(),(EVAL/'index.html').read_bytes())

if __name__=='__main__':unittest.main()