"""Offline tests for PRC median ingestion; source asset not needed."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import stage12_prc_ingest as ingest


def specimen(char: str, strokes: int = 1) -> dict:
    return {"character": char, "strokes": ["M 0 0 L 1 1"] * strokes,
            "medians": [[[0, 900], [1024, -124]]] * strokes}


class TestPrcIngest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.graphics = self.root / "graphics.txt"
        # Input order intentionally differs from Unicode order.
        rows = [specimen("骨", strokes=9), specimen("一")]
        self.graphics.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n",
                                 encoding="utf-8")
        self.expected = ingest.sha256(self.graphics)

    def test_coordinate_mapping(self):
        pts = ingest._medians(specimen("一"), 1)[0]
        np.testing.assert_allclose(pts[0], [0, 0])
        np.testing.assert_allclose(pts[-1], [109, 109])

    def test_deterministic_and_structurally_compatible(self):
        a, b = self.root / "cache1", self.root / "cache2"
        sa = ingest.build(self.graphics, a, self.expected)
        sb = ingest.build(self.graphics, b, self.expected)
        self.assertEqual(sa, sb)
        self.assertEqual(sa["glyphs"], 2)
        self.assertFalse(sa["regional_ranking_ready"])
        for name in ("points.npy", "offsets.npy", "dt.npy", "meta.json"):
            self.assertEqual((a / name).read_bytes(), (b / name).read_bytes(), name)
        points = np.load(a / "points.npy")
        offsets = np.load(a / "offsets.npy")
        dt = np.load(a / "dt.npy")
        meta = json.loads((a / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta[0]["char"], "一")
        self.assertEqual(meta[1]["char"], "骨")
        self.assertEqual(offsets.tolist(), [0, meta[0]["n_points"], len(points)])
        self.assertEqual(points.shape[1], 2)
        self.assertEqual(points.dtype, np.float32)
        self.assertEqual(dt.shape, (2, 109, 109))
        self.assertEqual(dt.dtype, np.float32)
        self.assertEqual(float(dt[0, 0, 0]), 0.0)
        self.assertEqual(meta[0]["source_sha256"], self.expected)
        self.assertEqual(meta[0]["region"], "unassigned")

    def test_japanese_divergence_is_only_stroke_count_evidence(self):
        jp = self.root / "jp.json"
        jp.write_text(json.dumps([{"char": "骨", "n_strokes": 10}]), encoding="utf-8")
        ingest.build(self.graphics, self.root / "cache", self.expected, jp)
        m = json.loads((self.root / "cache/meta.json").read_text(encoding="utf-8"))
        self.assertTrue(m[1]["jp_stroke_count_diff"])
        self.assertEqual(m[1]["jp_n_strokes"], 10)
        self.assertIsNone(m[0]["jp_stroke_count_diff"])

    def test_wrong_pin_fails_before_outputs(self):
        target = self.root / "invalid"
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            ingest.build(self.graphics, target, "0" * 64)
        self.assertFalse(target.exists())

    def test_duplicate_rejected(self):
        self.graphics.write_text(json.dumps(specimen("一")) + "\n" +
                                 json.dumps(specimen("一")) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            ingest.build(self.graphics, self.root / "invalid", ingest.sha256(self.graphics))

    def test_unpaired_medians_rejected(self):
        row = specimen("一")
        row["medians"] = []
        self.graphics.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            ingest.build(self.graphics, self.root / "invalid", ingest.sha256(self.graphics))

    def test_nonfinite_medians_rejected(self):
        row = specimen("一")
        row["medians"] = [[[0, 900], [float("nan"), 20]]]
        self.graphics.write_text(json.dumps(row) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid median coordinates"):
            ingest.build(self.graphics, self.root / "invalid", ingest.sha256(self.graphics))

    def test_pinned_source_is_formatted(self):
        self.assertEqual(len(ingest.pinned_sha()), 64)
        self.assertEqual(ingest.pinned_sha(),
                         "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee")


if __name__ == "__main__":
    unittest.main()
