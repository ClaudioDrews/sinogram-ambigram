"""Regression guard for the independent PRC width-semantics versions.

Offline synthetic tests prove offset units, source-rectangle parity and
byte-identical preservation of the historic module. They do not establish
fidelity to real Make Me a Hanzi contours or human readability.
"""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

import numpy as np

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
for folder in (CODE, ROOT / "tools"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import prc_construct as corrected
import prc_construct_legacy_v116 as historic
import replay_prc_v116 as replay

HISTORICAL_GIT_BLOB = "87d02ef641f879dae41275551546a671381b9fb9"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii")
                        + b"\0" + data).hexdigest()


class WidthSemanticsTest(unittest.TestCase):
    def test_historic_module_matches_frozen_main_blob(self):
        data = (CODE / "prc_construct_legacy_v116.py").read_bytes()
        self.assertEqual(git_blob_sha(data), HISTORICAL_GIT_BLOB)

    def test_archived_replay_imports_frozen_module(self):
        self.assertIs(replay.pc, historic)
        self.assertIsNot(replay.pc, corrected)

    def test_measured_half_width_is_not_halved_again(self):
        line = np.array([[30.0, 50.0], [50.0, 50.0]])
        radii = np.array([3.0, 3.0])
        a = corrected.stroke_polygon(line, radii)
        b = historic.stroke_polygon(line, radii)
        self.assertEqual(float(a[:, 1].min()), 47.0)
        self.assertEqual(float(a[:, 1].max()), 53.0)
        self.assertEqual(float(b[:, 1].min()), 48.5)
        self.assertEqual(float(b[:, 1].max()), 51.5)

    def test_corrected_matches_independent_rectangle_source(self):
        # Source contour specified directly, not derived by either stroke_polygon.
        original = np.array([[30., 47.], [50., 47.],
                             [50., 53.], [30., 53.]])
        source_mask = np.zeros((109, 109), dtype=bool)
        corrected.fill_polygon(original, source_mask)
        median = np.array([[30., 50.], [50., 50.]])
        widths = np.array([3., 3.])
        stroke = corrected.Stroke(median, widths)
        reconstructed = corrected.raster([stroke])
        archived = historic.raster([historic.Stroke(median, widths)])
        self.assertEqual(int(source_mask.sum()), 120)
        self.assertTrue(np.array_equal(reconstructed, source_mask))
        self.assertEqual(int(archived.sum()), 60)
        self.assertLess(int(np.logical_and(archived, source_mask).sum()),
                        int(np.logical_and(reconstructed, source_mask).sum()))

    def test_curved_path_offsets_follow_given_radius(self):
        median = np.array([[20., 20.], [30., 20.], [40., 30.],
                           [50., 40.], [60., 40.]])
        radii = np.array([1., 2., 3., 2., 1.])
        poly = corrected.stroke_polygon(median, radii)
        self.assertTrue(np.allclose(np.linalg.norm(poly[:len(median)] - median,
                                                   axis=1), radii, atol=1e-12))

    def test_degenerate_single_point_is_empty_without_crash(self):
        median = np.array([[30., 50.]])
        widths = np.array([3.])
        for implementation in (corrected, historic):
            poly = implementation.stroke_polygon(median, widths)
            self.assertEqual(poly.shape, (0, 2))
            self.assertEqual(int(implementation.raster(
                [implementation.Stroke(median, widths)]).sum()), 0)


if __name__ == "__main__":
    unittest.main()
