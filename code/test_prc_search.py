"""Offline complete-pair coarse-search tests using tiny MMah-like fixtures."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import stage12_prc_ingest as stage12
import stage13_prc_presets as stage13
import stage14_prc_search as stage14


def specimen(ch, pts):
    return {"character": ch, "strokes": ["M 0 0 L 1 1"], "medians": [pts]}


class TestCoarseSearch(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.graphics = self.root / "g.txt"
        entries = [specimen("工", [[150, 700], [820, 700]]),
                   specimen("土", [[150, 700], [820, 700], [820, 100]]),
                   specimen("口", [[100, 800], [800, 800], [800, 100],
                                  [100, 100], [100, 800]])]
        self.graphics.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n"
                                         for x in entries), encoding="utf8")
        self.sha = stage12.sha256(self.graphics)
        self.cache = self.root / "cache"
        self.inventory = self.root / "inv"
        stage12.build(self.graphics, self.cache, self.sha)
        stage13.generate(self.graphics, self.inventory, expected_sha=self.sha)

    def test_rotation_compatible_pool(self):
        meta, manifest, chars, idx, dt = stage14.load_verified(
            self.cache, self.inventory, "cn-s-gb2312")
        self.assertEqual(len(chars), 3)
        coarse = stage14.coarse_occupancy(dt, idx)
        self.assertEqual(coarse.shape, (3, 37, 37))
        self.assertTrue(np.array_equal(coarse[:, ::-1, ::-1][:, ::-1, ::-1], coarse))

    def test_deterministic_outputs_and_scales(self):
        out1 = self.root / "first"
        out2 = self.root / "second"
        r1 = stage14.rank(self.cache, self.inventory, out1, top_k=2, batch_size=1)
        r2 = stage14.rank(self.cache, self.inventory, out2, top_k=2, batch_size=3)
        self.assertEqual(r1, r2)
        self.assertFalse(r1["ranking_is_full_exact_grid"])
        self.assertFalse(r1["human_legibility_validated"])
        self.assertEqual(r1["n_glyphs"], 3)
        self.assertGreaterEqual(r1["n_candidates"], 3)
        for a in out1.iterdir():
            self.assertEqual(a.read_bytes(), (out2 / a.name).read_bytes(), a.name)
        with (out1 / "candidates_grid37.csv").open(encoding="utf8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), len({(r["a"], r["b"]) for r in rows}))
        self.assertTrue(all(r["region"] == "cn-s" for r in rows))

    def test_pin_mismatch_is_rejected(self):
        manifest = self.inventory / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf8"))
        data["graphics_sha256"] = "0" * 64
        manifest.write_text(json.dumps(data), encoding="utf8")
        with self.assertRaisesRegex(ValueError, "Source SHA mismatch"):
            stage14.rank(self.cache, self.inventory, self.root / "invalid")

    def test_tampered_preset_is_rejected(self):
        (self.inventory / "cn-s-gb2312.txt").write_text("一\n", encoding="utf8")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            stage14.rank(self.cache, self.inventory, self.root / "invalid")

    def test_unknown_preset_or_bad_limits_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown regional"):
            stage14.rank(self.cache, self.inventory, self.root / "invalid", preset="jp")
        with self.assertRaisesRegex(ValueError, "top_k"):
            stage14.rank(self.cache, self.inventory, self.root / "invalid", top_k=0)


if __name__ == "__main__":
    unittest.main()
