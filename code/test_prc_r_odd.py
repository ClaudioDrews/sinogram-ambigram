"""Network-free tests for experimental local PRC compensation."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import prc_construct as pc
from prc_r_odd import compensate, distance_to_ink


class OddCompensationTests(unittest.TestCase):
    def sample(self):
        return [
            pc.Stroke(np.array([[32., 29.], [32., 78.]]), np.array([2., 2.])),
            pc.Stroke(np.array([[77., 29.], [77., 78.]]), np.array([1., 1.])),
        ]

    def test_distance_zero_on_ink(self):
        ink = np.zeros((7, 7), dtype=bool)
        ink[3, 3] = True
        dt = distance_to_ink(ink)
        self.assertEqual(float(dt[3, 3]), 0.0)
        self.assertAlmostEqual(float(dt[4, 4]), np.sqrt(2))

    def test_no_width_shrinks_and_budget_is_respected(self):
        baseline = self.sample()
        out, metrics = compensate(baseline, (54.5, 54.5))
        self.assertTrue(metrics["ok"])
        self.assertLessEqual(metrics["growth"], 1.28 + 1e-9)
        for old, new in zip(baseline, out):
            self.assertTrue(np.array_equal(old.median, new.median))
            self.assertTrue(np.all(new.half_width >= old.half_width))

    def test_deterministic_and_not_worse_than_baseline(self):
        baseline = self.sample()
        a, score_a = compensate(baseline, (54.5, 54.5))
        b, score_b = compensate(baseline, (54.5, 54.5))
        for sa, sb in zip(a, b):
            self.assertTrue(np.array_equal(sa.half_width, sb.half_width))
        self.assertEqual(score_a, score_b)
        baseline_score = pc.sector_score(baseline, (54.5, 54.5), pc.raster(baseline))
        self.assertGreaterEqual(score_a["sym"], baseline_score["sym"])


if __name__ == "__main__":
    unittest.main()
