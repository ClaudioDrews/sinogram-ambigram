"""Offline smoke tests for fixed-cohort source-level PRC reproduction."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "code"))
import replay_prc_v116 as replay  # noqa: E402
import prc_construct as pc  # noqa: E402


class TestPrCEvidenceReplay(unittest.TestCase):
    def test_unpinned_source_rejected_before_outputs(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            source = root / "graphics.txt"
            source.write_text('{"character":"一","strokes":[],"medians":[]}\n', encoding="utf8")
            result = root / "out"
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                replay.replay(source, root, result, False)
            self.assertFalse(result.exists())

    def test_archived_m1_is_deterministic(self):
        stroke = pc.Stroke(
            median=np.array([[30., 30.], [60., 30.], [75., 75.]]),
            half_width=np.array([5., 5., 5.])
        )
        masks = pc.sector_masks()
        kernel = pc.gaussian_kernel(3.0)
        a, wa = replay.historic_m1([stroke], masks, kernel)
        b, wb = replay.historic_m1([stroke], masks, kernel)
        np.testing.assert_allclose(wa, wb, atol=0)
        np.testing.assert_allclose(a[0].half_width, b[0].half_width, atol=0)
        self.assertEqual(wa.shape, (9,))
        self.assertTrue(np.all(wa >= 1.0))
        self.assertTrue(np.all(wa <= 1.4))

    def test_replay_uses_source_glyph(self):
        fixture = {"一": {"character": "一", "strokes": [
            "M 150 700 L 800 700 L 800 680 L 150 680 Z"],
            "medians": [[[150, 690], [800, 690]]]
        }}
        item = replay.centre_case("一", "一", fixture)
        self.assertEqual((item["a"], item["b"]), ("一", "一"))
        self.assertIn("centre_only", item)
        self.assertIn("with_rules", item)
        self.assertTrue(0 <= item["box"] <= 1.0)
        self.assertTrue(0 <= item["final"] <= 1.0)

    def test_rejects_mixed_or_wrapped_cohort(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "cohort.csv"
            p.write_text("index,source,target\n0,一,一\n", encoding="utf8")
            with self.assertRaisesRegex(ValueError, "Noncanonical"):
                replay.cohort(p, replay.CENTRE_COLUMNS, 1)


if __name__ == "__main__":
    unittest.main()
