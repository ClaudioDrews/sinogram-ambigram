"""Regression tests for the published blind VLM pilot scoring contract."""
from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
import score as benchmark


class TestPilot01(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = benchmark.read_csv(BASE / "data/ground_truth.csv")
        cls.responses = benchmark.read_csv(BASE / "data/responses_matrix.csv")

    def test_complete_pairing_and_trial_identity(self):
        truth = benchmark.validate_ground_truth(self.key)
        self.assertEqual(len(truth), 52)
        self.assertEqual(len({x["pair_id"] for x in self.key}), 26)
        self.assertEqual(len({x["sha256"] for x in self.key}) <= 52, True)
        self.assertEqual(sum(x["task"] == "self" for x in self.key), 40)
        self.assertEqual(sum(x["task"] == "pair" for x in self.key), 12)

    def test_complete_results_and_expected_counts(self):
        result = benchmark.score(self.key, self.responses)
        self.assertEqual(result["n_observations"], 208)
        self.assertEqual(result["counts"]["self/main-original"]["double_correct"], 10)
        self.assertEqual(result["counts"]["self/thickness-fixed"]["double_correct"], 14)
        self.assertEqual(result["counts"]["self/r-odd"]["double_correct"], 13)
        self.assertEqual(result["counts"]["self/harmonic"]["double_correct"], 15)
        self.assertEqual(result["counts"]["pair/ab-fusion"]["double_correct"], 0)
        self.assertEqual(result["counts"]["self/harmonic"]["orient_correct"], 32)

    def test_malformed_character_cannot_be_counted_correct(self):
        self.assertEqual(benchmark.classify("日\n理由"), ("invalid", ""))
        self.assertEqual(benchmark.classify("UNKNOWN"), ("unknown", ""))
        self.assertEqual(benchmark.classify("", "error"), ("error", ""))
        self.assertEqual(benchmark.classify("日"), ("valid", "日"))

    def test_missing_orientation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "orientation"):
            benchmark.validate_ground_truth(self.key[1:])

    def test_duplicate_trial_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Duplicate trial"):
            benchmark.validate_ground_truth(self.key + [self.key[0]])

    def test_unmatched_model_trial_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing model-trials"):
            benchmark.score(self.key, self.responses[1:])

    def test_wrong_label_fails_closed(self):
        altered = [x.copy() for x in self.key]
        altered[0]["expected_character"] = "田"
        with self.assertRaisesRegex(ValueError, "target mismatch"):
            benchmark.validate_ground_truth(altered)

    def test_pair_vs_self_not_pooled(self):
        result = benchmark.score(self.key, self.responses)
        self.assertEqual(set(result["counts"]), {
            f"{task}/{arm}" for task, arms in benchmark.TASK_ARMS.items()
            for arm in arms})
        self.assertEqual(result["comparisons"][
            "self:thickness-fixed>harmonic"]["paired_orientations"], 40)


if __name__ == "__main__":
    unittest.main()
