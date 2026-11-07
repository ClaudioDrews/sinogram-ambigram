"""Synthetic tests of A/B registration and construction."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import prc_construct as pc
import prc_ab_fusion as ab


class ABTests(unittest.TestCase):
    def test_identical_half_turn_pair_is_deduplicated(self):
        centre = (54.5, 54.5)
        a = [pc.Stroke(np.array([[20., 40.], [50., 40.]]),
                       np.array([2., 2.]))]
        b = ab.rotate_strokes(a, centre)
        out, report = ab.construct(a, b, centre)
        self.assertEqual(report["matched_strokes"], 1)
        self.assertEqual(len(out), 1)
        self.assertGreater(report["metrics"]["minimum_f1"], 0.95)

    def test_unmatched_strokes_are_retained(self):
        centre = (54.5, 54.5)
        a = [pc.Stroke(np.array([[12., 20.], [25., 20.]]),
                       np.array([1., 1.]))]
        b = [pc.Stroke(np.array([[12., 90.], [25., 90.]]),
                       np.array([1., 1.]))]
        out, report = ab.construct(a, b, centre, threshold=1.0)
        self.assertEqual(report["matched_strokes"], 0)
        self.assertEqual(len(out), 2)

    def test_determinism(self):
        centre = (54.5, 54.5)
        a = [pc.Stroke(np.array([[15., 40.], [50., 40.]]),
                       np.array([2., 2.]))]
        b = ab.rotate_strokes(a, centre)
        out1, meta1 = ab.construct(a, b, centre)
        out2, meta2 = ab.construct(a, b, centre)
        self.assertEqual(meta1, meta2)
        for x, y in zip(out1, out2):
            self.assertTrue(np.array_equal(x.median, y.median))
            self.assertTrue(np.array_equal(x.half_width, y.half_width))


if __name__ == "__main__":
    unittest.main()
