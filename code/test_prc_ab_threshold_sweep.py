"""Offline synthetic gates for the frozen A/B threshold-sensitivity protocol."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
import numpy as np

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
for folder in (CODE, ROOT / "tools"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
import prc_construct as pc
import prc_ab_fusion as ab
import ab_fusion_threshold_sweep as study


class ThresholdStudyTests(unittest.TestCase):
    @staticmethod
    def line(start=(20, 40), end=(50, 40)):
        return pc.Stroke(np.asarray([start, end], dtype=float),
                         np.asarray([2., 2.], dtype=float))

    def test_predeclared_thresholds_and_cohort(self):
        self.assertEqual(study.THRESHOLDS, (2., 4., 8., 12., 16.))
        self.assertEqual(study.POOL_SIZE, 128)
        self.assertEqual(study.PAIRS_PER_ARM, 16)
        self.assertEqual(len(study.PILOT), 9)
        self.assertEqual(len(study.ANCHORS), 2)

    def test_rms_zero_for_exact_half_turn(self):
        a = [self.line()]
        b = ab.rotate_strokes(a, study.CENTRE)
        rb = ab.rotate_strokes(b, study.CENTRE)
        self.assertAlmostEqual(study.minimum_spine_rms(a, rb), 0., places=10)
        self.assertEqual(len(ab.match_strokes(a, rb, threshold=2.)), 1)

    def test_rms_detects_separated_strokes(self):
        a = [self.line()]
        rb = [self.line((20, 50), (50, 50))]
        self.assertAlmostEqual(study.minimum_spine_rms(a, rb), 10., places=10)
        self.assertEqual(len(ab.match_strokes(a, rb, threshold=4.)), 0)
        self.assertEqual(len(ab.match_strokes(a, rb, threshold=12.)), 1)

    def test_match_counts_nondecreasing_on_simple_unambiguous_pair(self):
        a = [self.line()]
        rb = [self.line((20, 50), (50, 50))]
        n = [len(ab.match_strokes(a, rb, threshold=t))
             for t in study.THRESHOLDS]
        self.assertEqual(n, [0, 0, 0, 1, 1])

    def test_distinguish_four_possible_mechanistic_outcomes(self):
        self.assertEqual(study.classify(0, 0, 10, 10), "no_match")
        self.assertEqual(study.classify(1, 0, 10, 10),
                         "matched_rejected_or_union")
        self.assertEqual(study.classify(1, 0, 9, 10),
                         "accepted_pixel_identical")
        self.assertEqual(study.classify(1, 8, 9, 10), "changed_pixels")

    def test_unchanged_union_is_reproduced_when_no_match(self):
        a = [self.line((12, 20), (25, 20))]
        b = [self.line((12, 90), (25, 90))]
        case = {"arm": "previous_pilot", "case": "synthetic",
                "a": "a", "b": "b", "source_ink_iou": 0.0}
        result = study.measure(case, {"a": a, "b": b}, 2.0)
        self.assertEqual(result["matched_strokes"], 0)
        self.assertEqual(result["changed_pixels"], 0)
        self.assertEqual(result["status"], "no_match")
        self.assertEqual(result["delta_joint_f1"], 0.)
        self.assertEqual(result["delta_min_f1"], 0.)

    def test_source_digest_rejected_before_reading_graphics(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graphics.txt"
            path.write_bytes(b"wrong-source")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                study.run(path, Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
