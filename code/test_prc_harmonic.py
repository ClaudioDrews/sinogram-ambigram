"""Tests for the stand-alone harmonic thickness ablation."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import prc_construct as pc
import prc_harmonic as h


class HarmonicTests(unittest.TestCase):
    def sample(self):
        return [
            pc.Stroke(np.array([[25., 30.], [25., 80.]]), np.array([2., 2.])),
            pc.Stroke(np.array([[80., 30.], [80., 80.]]), np.array([1., 1.])),
        ]

    def test_field_is_c2_invariant(self):
        points = np.array([[10.7, 14.2], [40., 70.], [54.5, 54.5]])
        centre = (54.5, 54.5)
        a = np.array([0.1, -0.2, 0.08, 0.04, 0.07])
        mirrored = 2 * np.asarray(centre) - points
        self.assertTrue(np.allclose(h.log_field(points, centre, a),
                                    h.log_field(mirrored, centre, a), atol=1e-12))

    def test_zero_field_identity(self):
        strokes = self.sample()
        out = h.apply_field(strokes, (54.5, 54.5), np.zeros(len(h.BASIS)))
        for original, edited in zip(strokes, out):
            self.assertTrue(np.array_equal(original.half_width, edited.half_width))
            self.assertTrue(np.array_equal(original.median, edited.median))

    def test_optimization_is_deterministic_and_constrained(self):
        strokes = self.sample()
        a, ra = h.optimize(strokes, (54.5, 54.5), rounds=1)
        b, rb = h.optimize(strokes, (54.5, 54.5), rounds=1)
        self.assertEqual(ra, rb)
        self.assertTrue(ra["score"]["ok"])
        self.assertLessEqual(ra["score"]["growth"], 1.28 + 1e-9)
        baseline = pc.sector_score(strokes, (54.5, 54.5), pc.raster(strokes))
        self.assertGreaterEqual(ra["score"]["sym"], baseline["sym"])
        for x, y in zip(a, b):
            self.assertTrue(np.array_equal(x.half_width, y.half_width))


if __name__ == "__main__":
    unittest.main()
