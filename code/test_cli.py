"""Execute real CLI entry points on minimal, synthetic KanjiVG fixtures.

These tests require no downloaded KanjiVG catalogue and do not modify project data.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CODE = Path(__file__).resolve().parent
SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 109 109">'
    '<path d="M 10,10 L 89,10 L 89,89 M 10,89 L 89,89"/></svg>'
)


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.glyphs = self.root / "glyphs"
        self.glyphs.mkdir()
        for ch in ("甲", "由"):
            (self.glyphs / f"{ord(ch):05x}.svg").write_text(SVG, encoding="utf-8")
        self.env = os.environ.copy()
        for key in ("ROTG_ROOT", "ROTG_DATA", "ROTG_LISTS", "ROTG_CACHE"):
            self.env.pop(key, None)
        self.env["ROTG_KANJI_DIR"] = str(self.glyphs)
        self.env["ROTG_OUT"] = str(self.root / "results")

    def run_cli(self, name, *args):
        return subprocess.run(
            [sys.executable, str(CODE / name), *args],
            cwd=self.root,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=20,
        )

    def test_ambigram_cli_generates_png(self):
        result = self.run_cli("make_ambigram.py", "甲", "由")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.root / "results" / "preview" / "ambigram_甲_由.png"
        self.assertTrue(output.is_file())
        self.assertGreater(output.stat().st_size, 100)

    def test_ambigram_cli_rejects_invalid_arg_count(self):
        for args in ((), ("甲",), ("甲", "由", "日")):
            with self.subTest(args=args):
                result = self.run_cli("make_ambigram.py", *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Usage:", result.stderr)

    def test_render_cli_generates_png(self):
        result = self.run_cli("render.py", "甲", "由")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.root / "results" / "preview" / "check.png"
        self.assertTrue(output.is_file())
        self.assertGreater(output.stat().st_size, 100)


    def test_full_grid_export_has_distinct_metric_names(self):
        import csv
        import gzip
        import json
        import numpy as np

        cache = self.root / "cache"
        cache.mkdir()
        (cache / "meta.json").write_text(
            json.dumps([{"char": "甲"}, {"char": "由"}], ensure_ascii=False),
            encoding="utf-8",
        )
        dtype = [("a", "i4"), ("b", "i4"), ("haus", "f4"),
                 ("mean", "f4"), ("rms", "f4"),
                 ("iou2", "f4"), ("iou3", "f4"), ("iou4", "f4")]
        rows = np.array([(1, 1, 5, 3, 4, .4, .5, .6),
                         (0, 1, 11, 7, 8, .7, .8, .9)], dtype=dtype)
        np.save(cache / "pairs3.npy", rows)
        self.env["ROTG_CACHE"] = str(cache)
        result = self.run_cli("export_full_grid.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = self.root / "results" / "catalog" / "rotation_pairs_full_grid.csv.gz"
        with gzip.open(archive, "rt", encoding="utf-8", newline="") as stream:
            data = list(csv.DictReader(stream))
        self.assertEqual(len(data), 2)
        self.assertEqual((data[0]["a"], data[0]["b"]), ("甲", "由"))
        self.assertAlmostEqual(float(data[0]["hausdorff_grid"]), 11 / 109, places=7)
        self.assertEqual(data[1]["self"], "True")


if __name__ == "__main__":
    unittest.main()
