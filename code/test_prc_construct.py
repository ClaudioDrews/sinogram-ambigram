"""Tests for the PRC construction method (code/prc_construct.py).

Covers the geometry primitives, the involution of the half-turn, the
extremity pairing, the reconciliation rules and determinism. No network and
no MMah data are required: the tests build synthetic strokes.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROTGRAPH = Path(__file__).resolve().parent
if str(ROTGRAPH) not in sys.path:
    sys.path.insert(0, str(ROTGRAPH))

import prc_construct as pc  # noqa: E402

EM = pc.EM


def _stroke(points, widths):
    return pc.Stroke(np.asarray(points, dtype=np.float64),
                      np.asarray(widths, dtype=np.float64))


class TestPrimitives(unittest.TestCase):
    def test_resample_keeps_the_endpoints(self):
        line = np.array([[0.0, 0.0], [10.0, 0.0]])
        out = pc.resample(line, 1.0)
        self.assertAlmostEqual(out[0, 0], 0.0)
        self.assertAlmostEqual(out[-1, 0], 10.0)
        seg = np.linalg.norm(np.diff(out, axis=0), axis=1)
        self.assertTrue(np.allclose(seg, seg[0]))

    def test_ramp_is_one_at_the_tip_and_zero_beyond_kappa(self):
        r = pc.ramp(np.array([0.0, pc.KAPPA / 2, pc.KAPPA, pc.KAPPA * 2]))
        self.assertAlmostEqual(r[0], 1.0)
        self.assertAlmostEqual(r[2], 0.0)
        self.assertAlmostEqual(r[3], 0.0)
        self.assertTrue(np.all(np.diff(r) <= 1e-12))

    def test_retarget_preserves_the_profile_endpoints(self):
        med = np.array([[0.0, 0.0], [5.0, 0.0], [10.0, 0.0]])
        hw = np.array([1.0, 2.0, 1.0])
        out = pc.retarget(med, hw)
        self.assertAlmostEqual(float(out[0]), 1.0)
        self.assertAlmostEqual(float(out[-1]), 1.0)

    def test_ink_overlap_of_identical_grids_is_one(self):
        g = np.zeros((pc.GRID, pc.GRID), dtype=bool)
        g[40:60, 40:60] = True
        self.assertAlmostEqual(pc.ink_overlap(g, g), 1.0)

    def test_ink_overlap_of_disjoint_grids_is_zero(self):
        a = np.zeros((pc.GRID, pc.GRID), dtype=bool)
        b = np.zeros((pc.GRID, pc.GRID), dtype=bool)
        a[10:20, 10:20] = True
        b[80:90, 80:90] = True
        self.assertAlmostEqual(pc.ink_overlap(a, b), 0.0)


class TestHalfTurn(unittest.TestCase):
    def test_half_turn_is_an_involution(self):
        c = (EM / 2 + 1.0, EM / 2 - 2.0)
        p = np.array([[10.0, 20.0], [30.0, 40.0]])
        self.assertTrue(np.allclose(pc.half_turn(pc.half_turn(p, c), c), p))

    def test_half_turn_of_a_centred_box_is_itself(self):
        c = (EM / 2, EM / 2)
        g = np.zeros((pc.GRID, pc.GRID), dtype=bool)
        g[30:79, 30:79] = True
        self.assertAlmostEqual(pc.ink_overlap(pc.half_turn_grid(g, c), g), 1.0)

    def test_half_turn_about_a_wrong_centre_misses(self):
        g = np.zeros((pc.GRID, pc.GRID), dtype=bool)
        g[30:79, 30:79] = True
        off = pc.ink_overlap(pc.half_turn_grid(g, (EM / 2 + 12, EM / 2)), g)
        self.assertLess(off, 0.9)


class TestPairing(unittest.TestCase):
    def _square(self):
        """A frame drawn as four strokes, symmetric about the box centre."""
        c = EM / 2
        r = 20.0
        return [
            _stroke([[c - r, c - r], [c - r, c + r]], [1.0, 1.0]),
            _stroke([[c - r, c - r], [c + r, c - r]], [1.0, 1.0]),
            _stroke([[c + r, c - r], [c + r, c + r]], [1.0, 1.0]),
            _stroke([[c - r, c + r], [c + r, c + r]], [1.0, 1.0]),
        ]

    def test_a_frame_has_four_places_and_two_pairs(self):
        strokes = self._square()
        pairs, clusters, _ = pc.pair_places(strokes, (EM / 2, EM / 2))
        self.assertEqual(len(clusters), 4)
        self.assertEqual(len(pairs), 2)

    def test_a_paired_place_is_within_the_fusion_radius(self):
        strokes = self._square()
        pairs, _, _ = pc.pair_places(strokes, (EM / 2, EM / 2))
        for _a, _b, gap in pairs:
            self.assertLessEqual(gap, pc.DELTA_F)

    def test_reconcile_leaves_a_balanced_drawing_unchanged(self):
        strokes = self._square()
        before = [s.half_width.copy() for s in strokes]
        points = [s.median.copy() for s in strokes]
        info = pc.reconcile(strokes, (EM / 2, EM / 2))
        self.assertGreater(info["pairs"], 0)
        for s, w in zip(strokes, before):
            self.assertTrue(np.allclose(s.half_width, w))
        for s, p in zip(strokes, points):
            self.assertTrue(np.allclose(s.median, p, atol=0.5))

    def test_reconcile_equalises_the_weight_inside_a_paired_place(self):
        strokes = self._square()
        # make one extremity heavy, the way a wedge-ended PRC stroke is
        strokes[0].half_width[0] = 4.0
        pc.reconcile(strokes, (EM / 2, EM / 2))
        tp = pc.terminals(strokes)
        pairs, clusters, _ = pc.pair_places(strokes, (EM / 2, EM / 2))
        self.assertTrue(pairs)
        for ia, ib, _gap in pairs:
            group = clusters[ia] + clusters[ib]
            weights = [tp[i].weight for i in group]
            self.assertAlmostEqual(max(weights) - min(weights), 0.0, places=5)

    def test_reconcile_never_increases_the_total_weight_without_a_pair(self):
        strokes = self._square()
        total_before = sum(float(s.half_width.sum()) for s in strokes)
        pc.reconcile(strokes, (EM / 2 + 9.0, EM / 2 + 9.0))
        total_after = sum(float(s.half_width.sum()) for s in strokes)
        self.assertAlmostEqual(total_before, total_after, places=6)


class TestLegibility(unittest.TestCase):
    def test_symmetric_ink_is_measured_against_the_original(self):
        c = EM / 2
        strokes = [_stroke([[20.0, c], [88.0, c]], [1.0, 1.0])]
        ref = pc.raster(strokes)
        # a drawing that keeps only its symmetric half must not look better
        half = [_stroke([[20.0, c], [54.0, c]], [1.0, 1.0])]
        self.assertLess(pc.symmetric_ink(half, (c, c), ref),
                        pc.symmetric_ink(strokes, (c, c), ref))

    def test_retention_falls_when_ink_is_removed(self):
        c = EM / 2
        strokes = [_stroke([[20.0, c], [88.0, c]], [1.0, 1.0])]
        ref = pc.raster(strokes)
        half = [_stroke([[20.0, c], [54.0, c]], [1.0, 1.0])]
        self.assertLess(pc.retention(half, ref), 0.7)

    def test_legibility_is_the_product_of_mu_and_pi(self):
        strokes = [
            _stroke([[20.0, EM / 2], [88.0, EM / 2]], [1.0, 1.0]),
        ]
        out = pc.legibility(strokes, (EM / 2, EM / 2))
        self.assertAlmostEqual(out["L"], out["mu"] * out["pi"])
        self.assertGreaterEqual(out["L"], 0.0)
        self.assertLessEqual(out["L"], 1.0)

    def test_a_bar_is_symmetric_about_its_own_centre(self):
        c = EM / 2
        strokes = [_stroke([[20.0, c], [88.0, c]], [1.0, 1.0])]
        out = pc.legibility(strokes, (c, c))
        self.assertGreater(out["mu"], 0.8)


class TestDeterminism(unittest.TestCase):
    def test_reconcile_gives_the_same_result_twice(self):
        strokes = [
            _stroke([[20.0, EM / 2], [88.0, EM / 2]], [1.0, 3.0]),
            _stroke([[EM / 2, 20.0], [EM / 2, 88.0]], [1.0, 3.0]),
        ]
        a = [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]
        b = [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]
        pc.reconcile(a, (EM / 2, EM / 2))
        pc.reconcile(b, (EM / 2, EM / 2))
        for x, y in zip(a, b):
            self.assertTrue(np.allclose(x.median, y.median))
            self.assertTrue(np.allclose(x.half_width, y.half_width))

    def test_raster_is_reproducible(self):
        strokes = [_stroke([[20.0, EM / 2], [88.0, EM / 2]], [1.0, 3.0])]
        self.assertTrue(np.array_equal(pc.raster(strokes), pc.raster(strokes)))


class TestSectorRule(unittest.TestCase):
    """R-SECT: sector-wise thickness manipulation."""

    def _bars(self):
        """A left-heavy drawing: the left column carries more ink.

        Both opposite sectors of the middle row carry ink, so the rule has
        a pair to balance.
        """
        c = EM / 2
        return [
            _stroke([[c - 20, c - 20], [c - 20, c + 20]], [3.0, 3.0]),
            _stroke([[c + 20, c - 20], [c + 20, c + 20]], [1.0, 1.0]),
        ]

    def test_sector_masks_cover_the_box(self):
        masks = pc.sector_masks()
        self.assertEqual(masks.shape, (9, pc.GRID, pc.GRID))
        for m in masks:
            self.assertTrue(m.any())

    def test_a_uniform_multiplier_field_changes_nothing(self):
        masks = pc.sector_masks()
        field = pc.multiplier_field(np.ones(9), masks)
        self.assertAlmostEqual(float(field.min()), 1.0, places=6)
        self.assertAlmostEqual(float(field.max()), 1.0, places=6)

    def test_the_multiplier_is_exact_inside_a_sector(self):
        masks = pc.sector_masks()
        mult = np.arange(1.0, 10.0)
        field = pc.multiplier_field(mult, masks)
        centre = pc.GRID // 6          # a cell well inside the top-left sector
        self.assertAlmostEqual(float(field[centre, centre]), 1.0, places=5)

    def test_the_field_blends_instead_of_stepping(self):
        masks = pc.sector_masks()
        mult = np.ones(9)
        mult[0] = 1.4
        field = pc.multiplier_field(mult, masks)
        values = np.unique(np.round(field, 3))
        self.assertGreater(len(values), 2)

    def test_the_rule_thickens_the_lighter_opposite_sector(self):
        strokes = self._bars()
        masks = pc.sector_masks()
        g = pc.raster(strokes)
        centre = (EM / 2, EM / 2)
        out, mult = pc.equalise_opposite_sectors(strokes, centre, masks)
        self.assertEqual(len(out), len(strokes))
        self.assertTrue(np.all(mult >= 1.0))
        self.assertGreater(float(mult.max()), 1.0)

    def test_the_rule_never_erases_ink(self):
        strokes = self._bars()
        ref = pc.raster(strokes)
        centre = (EM / 2, EM / 2)
        out, _ = pc.equalise_opposite_sectors(strokes, centre)
        sc = pc.sector_score(out, centre, ref)
        self.assertGreaterEqual(sc["retention"], pc.RETENTION_MIN)
        self.assertLessEqual(sc["growth"], pc.GROWTH_MAX)

    def test_the_score_rejects_a_flooded_drawing(self):
        strokes = self._bars()
        ref = pc.raster(strokes)
        centre = (EM / 2, EM / 2)
        flooded = [pc.Stroke(s.median.copy(), s.half_width * 12) for s in strokes]
        sc = pc.sector_score(flooded, centre, ref)
        self.assertFalse(sc["ok"])
        self.assertGreater(sc["growth"], pc.GROWTH_MAX)

    def test_the_search_never_scores_below_the_baseline(self):
        strokes = self._bars()
        ref = pc.raster(strokes)
        centre = (EM / 2, EM / 2)
        base = pc.sector_score(strokes, centre, ref)
        out, mult, sc = pc.search_sector_multipliers(strokes, centre, ref)
        self.assertGreaterEqual(sc["sym"] + 1e-9, base["sym"])
        self.assertTrue(sc["ok"])

    def test_the_search_is_deterministic(self):
        strokes = self._bars()
        ref = pc.raster(strokes)
        centre = (EM / 2, EM / 2)
        _, m1, _ = pc.search_sector_multipliers(strokes, centre, ref)
        _, m2, _ = pc.search_sector_multipliers(strokes, centre, ref)
        self.assertTrue(np.array_equal(m1, m2))



if __name__ == "__main__":
    unittest.main()