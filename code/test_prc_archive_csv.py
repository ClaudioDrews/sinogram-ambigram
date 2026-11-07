"""Regression tests for machine-readable PRC v1.16 result tables.

The initial publication accidentally included spreadsheet wrapper lines and
an artificial 'index' column. This test protects the *raw on-disk CSV format*
and verifies its numerical agreement with the archived summary.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "prc" / "archive-v1.16"

CENTRE_HEADER = [
    "source", "target", "box_sym", "centre_sym", "rules_sym",
    "final_sym", "retention", "meanings_not_tested",
]
SECTOR_HEADER = [
    "source", "target", "base_sym", "edited_sym", "gain",
    "retention", "growth", "constraints_pass",
]


def read_csv(path: Path, expected_header: list[str], rows: int) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        raw_header = f.readline().strip("\r\n").split(",")
        if raw_header != expected_header:
            raise ValueError(f"Noncanonical PRC CSV header: {path.name}: {raw_header}")
        f.seek(0)
        reader = csv.DictReader(f)
        parsed = list(reader)
        if reader.fieldnames != expected_header:
            raise ValueError("Unexpected column order")
    if len(parsed) != rows:
        raise ValueError(f"Unexpected row count {len(parsed)} != {rows}")
    if any(None in row or None in row.values() for row in parsed):
        raise ValueError("Missing or extra CSV columns")
    if len({(x["source"], x["target"]) for x in parsed}) != rows:
        raise ValueError("Duplicate source/target pair in published CSV")
    return parsed


class TestPrcArchiveCsv(unittest.TestCase):
    def test_schema_and_sample_sizes(self):
        centre = read_csv(ARCHIVE / "prc-centre-extremity-120.csv", CENTRE_HEADER, 120)
        sector = read_csv(ARCHIVE / "prc-sector-generalisation-53.csv", SECTOR_HEADER, 53)
        self.assertTrue(all(x["meanings_not_tested"] == "True" for x in centre))
        self.assertTrue(all(x["constraints_pass"] == "True" for x in sector))

    def test_recover_archived_centre_statistics(self):
        summary = json.loads((ARCHIVE / "prc-archive-summary.json").read_text(encoding="utf-8"))
        data = read_csv(ARCHIVE / "prc-centre-extremity-120.csv", CENTRE_HEADER, 120)
        gains = [float(x["centre_sym"]) - float(x["box_sym"]) for x in data]
        rule_gains = [float(x["rules_sym"]) - float(x["centre_sym"]) for x in data]
        self.assertTrue(all(math.isfinite(x) for x in gains + rule_gains))
        self.assertAlmostEqual(statistics.mean(gains), summary["centre_gain_mean"], places=12)
        self.assertAlmostEqual(statistics.median(gains), summary["centre_gain_median"], places=12)
        self.assertAlmostEqual(statistics.mean(rule_gains), summary["extremity_gain_mean"], places=12)

    def test_recover_archived_sector_statistics(self):
        summary = json.loads((ARCHIVE / "prc-archive-summary.json").read_text(encoding="utf-8"))
        data = read_csv(ARCHIVE / "prc-sector-generalisation-53.csv", SECTOR_HEADER, 53)
        gains = [float(x["edited_sym"]) - float(x["base_sym"]) for x in data]
        baselines = [float(x["base_sym"]) for x in data]
        edited = [float(x["edited_sym"]) for x in data]
        for row, gain in zip(data, gains):
            self.assertTrue(math.isfinite(gain))
            self.assertAlmostEqual(float(row["gain"]), gain, places=12)
            self.assertGreaterEqual(float(row["retention"]), .90)
            self.assertLessEqual(float(row["growth"]), 1.30)
        self.assertEqual(sum(g > 0 for g in gains), summary["sector_improved_n"])
        self.assertAlmostEqual(statistics.mean(gains), summary["sector_delta_mean"], places=12)
        self.assertAlmostEqual(statistics.median(gains), summary["sector_delta_median"], places=12)
        self.assertAlmostEqual(statistics.median(baselines), summary["sector_baseline_median"], places=12)
        self.assertAlmostEqual(statistics.median(edited), summary["sector_edited_median"], places=12)

    def test_header_rejects_spreadsheet_wrappers(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.csv"
            p.write_text(
                "<PARSED TEXT FOR SHEET: 1 / 1 TABS\n"
                "TAB NAME: exported-sheet\n"
                "index,source,target\n"
                "0,一,一\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "Noncanonical"):
                read_csv(p, CENTRE_HEADER, 1)


if __name__ == "__main__":
    unittest.main()
