"""Offline acceptance tests for PRC catalogue serialization and scope gates."""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prc.build_catalog import build  # noqa: E402


class TestPublicCatalogue(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.csv = self.root / "pairs.csv"
        self.manifest = self.root / "manifest.json"
        pairs = [("一", "乙", .4, 2.0), ("一", "中", .5, 1.5),
                 ("中", "乙", .7, 3.0), ("一", "一", .1, -.7)]
        self.write_pairs(pairs)
        self.manifest.write_text(json.dumps({
            "schema": "prc-presets-v1", "region": "cn-s",
            "regional_form_certified": False,
            "graphics_sha256": "a" * 64,
            "presets": {"cn-s-gb2312": {"covered": 3}}
        }), encoding="utf8")

    def write_pairs(self, pairs):
        with self.csv.open("w", encoding="utf8", newline="") as out:
            writer = csv.writer(out, lineterminator="\n")
            writer.writerow(["a", "b", "iou_grid37", "z_pair_grid37", "preset", "region"])
            for a, b, sim, score in pairs:
                writer.writerow([a, b, sim, score, "cn-s-gb2312", "cn-s"])

    def test_deterministic_and_symmetric_shortlist(self):
        a = self.root / "one.json"
        b = self.root / "two.json"
        self.assertEqual(build(self.csv, self.manifest, a, top_k=2),
                         build(self.csv, self.manifest, b, top_k=2))
        self.assertEqual(a.read_bytes(), b.read_bytes())
        j = json.loads(a.read_text(encoding="utf8"))
        self.assertEqual(j["glyphs"], 3)
        self.assertEqual(j["shortlisted_pairs"], 4)
        self.assertEqual(j["partners"]["一"][0][0], "乙")
        self.assertEqual(j["partners"]["乙"][0][0], "中")
        self.assertFalse(j["human_readability_validated"])
        self.assertFalse(j["source_forms_certified"])

    def test_mixed_region_rejected(self):
        self.write_pairs([("一", "乙", .4, 2.)])
        s = self.csv.read_text().replace("cn-s\n", "jp\n")
        self.csv.write_text(s)
        with self.assertRaisesRegex(ValueError, "Mixed variant"):
            build(self.csv, self.manifest, self.root / "bad.json")

    def test_coverage_failure_rejected(self):
        self.write_pairs([("一", "乙", .4, 2.)])
        with self.assertRaisesRegex(ValueError, "cover every"):
            build(self.csv, self.manifest, self.root / "bad.json")

    def test_duplicate_rejected(self):
        with self.csv.open("a", encoding="utf8") as out:
            out.write("一,乙,0.4,2,cn-s-gb2312,cn-s\n")
        with self.assertRaisesRegex(ValueError, "Duplicate pair"):
            build(self.csv, self.manifest, self.root / "bad.json")

    def test_nonfinite_and_limits(self):
        with self.assertRaisesRegex(ValueError, "top_k"):
            build(self.csv, self.manifest, self.root / "bad.json", top_k=0)
        s = self.csv.read_text().replace("0.4,2.0", "0.4,nan")
        self.csv.write_text(s)
        with self.assertRaisesRegex(ValueError, "Invalid scores"):
            build(self.csv, self.manifest, self.root / "bad.json")


if __name__ == "__main__":
    unittest.main()
