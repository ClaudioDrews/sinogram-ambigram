"""Tests for the v2 stages: null normalisation, generator index, report.

All of them run on small synthetic fixtures and need no downloaded dataset.
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import stage7_normalise as s7  # noqa: E402
import stage10_build_generator_index as s10  # noqa: E402


def _fake_cache(root: Path, n: int = 6) -> Path:
    """A minimal cache directory that stage 7 can read."""
    cache = root / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    chars = list("甲由日目口回")[:n]
    meta = [{"char": c, "codepoint": f"{ord(c):04x}", "set": "joyou",
             "n_strokes": 3 + i, "n_points": 10, "stroke_types": [],
             "file": f"{ord(c):05x}.svg"} for i, c in enumerate(chars)]
    (cache / "meta.json").write_text(json.dumps(meta, ensure_ascii=False),
                                     encoding="utf-8")

    grid = 109
    offsets = [0]
    points = []
    for i in range(n):
        pts = np.array([[10.0 + i, 10.0], [90.0, 90.0 - i]], dtype=np.float32)
        points.append(pts)
        offsets.append(offsets[-1] + len(pts))
    np.save(cache / "points.npy", np.concatenate(points, axis=0))
    np.save(cache / "offsets.npy", np.array(offsets, dtype=np.int64))

    dt = np.zeros((n, grid, grid), dtype=np.float32)
    for i in range(n):
        dt[i][:, :] = np.arange(grid, dtype=np.float32)[None, :]
    np.save(cache / "dt.npy", dt)

    pairs = []
    for a in range(n):
        for b in range(a, n):
            pairs.append((a, b, 10.0 + a + b, 4.0, 2.0, 0.1, 0.2, 0.3))
    dtype = [("a", "i4"), ("b", "i4"), ("haus", "f4"), ("mean", "f4"),
             ("rms", "f4"), ("iou2", "f4"), ("iou3", "f4"), ("iou4", "f4")]
    np.save(cache / "pairs3.npy", np.array(pairs, dtype=dtype))

    refined_dtype = [("a", "i4"), ("b", "i4"), ("mean", "f4"), ("rms", "f4"),
                     ("haus", "f4"), ("sim", "f4")]
    refined = [(a, b, 4.0, 2.0, 10.0 + a + b, 0.5) for a, b, *_ in pairs]
    np.save(cache / "refined.npy", np.array(refined, dtype=refined_dtype))
    return cache


class TestNullNormalisation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cache = _fake_cache(self.root)

    def test_outputs_are_written_and_consistent(self):
        out = self.root / "v2"
        stats = s7.normalise(self.cache, out, seed=s7.SEED, partners=4)
        self.assertEqual(stats["null_partners"], 4)
        self.assertEqual(stats["glyphs"], 6)
        for name in ("null_model.csv", "rotation_pairs_refined_v2.csv",
                     "rotation_pairs_full_grid_v2.csv.gz",
                     "normalisation_stats.json"):
            self.assertTrue((out / name).is_file(), f"{name} missing")

    def test_z_pair_is_the_max_of_the_two_sides(self):
        out = self.root / "v2"
        s7.normalise(self.cache, out, seed=s7.SEED, partners=4)
        with open(out / "rotation_pairs_refined_v2.csv", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows)
        for row in rows:
            za, zb, zp = (float(row["z_a_grid"]), float(row["z_b_grid"]),
                          float(row["z_pair_grid"]))
            self.assertAlmostEqual(zp, max(za, zb), places=6)

    def test_run_is_deterministic(self):
        first = self.root / "v2a"
        second = self.root / "v2b"
        s7.normalise(self.cache, first, seed=s7.SEED, partners=4)
        s7.normalise(self.cache, second, seed=s7.SEED, partners=4)
        for name in ("null_model.csv", "rotation_pairs_refined_v2.csv",
                     "rotation_pairs_full_grid_v2.csv.gz"):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(),
                             f"{name} differs between two identical runs")

    def test_different_seed_changes_the_null_model(self):
        first = self.root / "v2a"
        second = self.root / "v2c"
        s7.normalise(self.cache, first, seed=s7.SEED, partners=4)
        s7.normalise(self.cache, second, seed=s7.SEED + 1, partners=4)
        self.assertNotEqual((first / "null_model.csv").read_bytes(),
                            (second / "null_model.csv").read_bytes())


class TestGeneratorIndexInjection(unittest.TestCase):
    PAGE = ('<html><body><script id="pair-dataset" type="application/json">'
            '[1,2]</script><p>rest</p></body></html>')

    def test_injection_replaces_only_the_block(self):
        rows = [["甲", "由", 0.0751, 0.0232, False]]
        updated = s10.inject(self.PAGE, rows)
        self.assertIn('"甲"', updated)
        self.assertIn("<p>rest</p>", updated)
        payload = json.loads(s10.BLOCK.search(updated).group(2))
        self.assertEqual(payload, rows)

    def test_injection_is_idempotent(self):
        rows = [["甲", "由", 0.0751, 0.0232, False]]
        once = s10.inject(self.PAGE, rows)
        twice = s10.inject(once, rows)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()


class TestPercentileOrientation(unittest.TestCase):
    """The percentile is the rank of goodness, so larger is better.

    The stages that read the column take the highest percentiles as the
    strongest candidates, so an inversion here would rank the worst pairs of
    a stratum first.
    """

    def test_best_pair_gets_the_highest_percentile(self):
        z = np.array([1.0, 2.0, 3.0])
        stratum = np.array([7, 7, 7])
        pct = s7._percentile_within_stratum(z, stratum)
        self.assertAlmostEqual(float(pct[0]), 100.0)
        self.assertAlmostEqual(float(pct[2]), 0.0)

    def test_percentile_is_computed_inside_each_stratum(self):
        z = np.array([1.0, 2.0, 100.0, 101.0])
        stratum = np.array([5, 5, 9, 9])
        pct = s7._percentile_within_stratum(z, stratum)
        self.assertAlmostEqual(float(pct[0]), 100.0)
        self.assertAlmostEqual(float(pct[1]), 0.0)
        self.assertAlmostEqual(float(pct[2]), 100.0)
        self.assertAlmostEqual(float(pct[3]), 0.0)

    def test_ties_share_the_average_rank(self):
        ranks = s7._average_ranks(np.array([1.0, 2.0, 2.0, 3.0]))
        self.assertEqual(list(ranks), [0.0, 1.5, 1.5, 3.0])

    def test_tied_values_get_the_same_percentile(self):
        z = np.array([2.0, 2.0, 2.0])
        stratum = np.array([4, 4, 4])
        pct = s7._percentile_within_stratum(z, stratum)
        self.assertEqual(len(set(pct.tolist())), 1)


class TestAnchorParsing(unittest.TestCase):
    """The anchor file writes the separator as its own token, with spaces."""

    TEXT = """ANCHOR SET
===========

A. DECISION ANCHORS (7)
-----------------------

  #  pair          v1 H (exact)
  1  吉 ↔ 阜       0.06823
  2  由 ↔ 甲       0.07510

B. DIAGNOSTIC SET (2)
--------------------

  8  十 ↔ 十       0.11498

C. DECISION RULE
----------------
"""

    def test_both_sets_are_found(self):
        import stage11_debias_report as s11
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "findings").mkdir()
            (root / "findings" / "anchors.txt").write_text(self.TEXT, encoding="utf-8")
            rows = s11._anchor_rows(root)
        self.assertEqual(rows["decision"], ["吉 ↔ 阜", "由 ↔ 甲"])
        self.assertEqual(rows["diagnostic"], ["十 ↔ 十"])

    def test_a_real_anchor_file_is_parsed_whole(self):
        import stage11_debias_report as s11
        repo = CODE.parent
        rows = s11._anchor_rows(repo)
        self.assertEqual(len(rows["decision"]), 7)
        self.assertEqual(len(rows["diagnostic"]), 2)
        for label in rows["decision"] + rows["diagnostic"]:
            self.assertIn("↔", label)


class TestPilotSelection(unittest.TestCase):
    """The item selection must produce the strata the protocol fixes."""

    def test_stratum_sizes_match_the_protocol(self):
        import stage9_select_pilot_items as s9
        self.assertEqual((s9.N_V1, s9.N_V2, s9.N_SELF, s9.N_CONTROL),
                         (12, 14, 8, 14))
        self.assertEqual(s9.N_V1 + s9.N_V2 + s9.N_SELF + s9.N_CONTROL, 48)