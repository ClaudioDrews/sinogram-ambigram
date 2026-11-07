"""Regression tests for the published blind VLM pilot scoring contract."""
from __future__ import annotations

import csv
import hashlib
import collections
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

    def test_source_response_and_reference_content_digests(self):
        # Canonical hashes of sanitized tables checked independently against
        # the original trial-order and scoring data before publication.
        cols = ["trial_id", "pair_id", "task", "arm", "orientation",
                "expected_character", "character_a", "character_b", "sha256"]
        def digest(rows, keys):
            body = "\\n".join(",".join(x[k] for k in keys) for x in rows)
            return hashlib.sha256(body.encode("utf-8")).hexdigest()
        self.assertEqual(
            digest(self.key, cols),
            "2a355591eb35bcf83ecbf9474e82cb77b1ebbd968f584e566092a77123079930")
        self.assertEqual(
            digest(self.responses, ["trial_id", "MM", "DS", "HY", "GLM"]),
            "faf15e0d80b3dde437daf8d81dcd4188c0090d99b91f5d845e7e989427a574e7")

    def test_completion_metadata_preserved_and_coherent(self):
        finish = benchmark.read_csv(BASE / "data/finish_reasons.csv")
        self.assertEqual(
            [x["trial_id"] for x in finish],
            [x["trial_id"] for x in self.responses])
        counts = collections.Counter(value for x in finish
                                     for k in ("MM", "DS", "HY", "GLM")
                                     for value in (x[k],))
        self.assertEqual(counts, {"S": 184, "L": 23, "E": 1})
        by_trial = {x["trial_id"]: x for x in self.responses}
        for x in finish:
            y = by_trial[x["trial_id"]]
            for name in ("MM", "DS", "HY", "GLM"):
                self.assertEqual(x[name] == "E", y[name] == "ERROR")
                if x[name] == "L":
                    self.assertEqual(y[name], "INVALID")

    def test_fusion_does_not_modify_both_test_pairs(self):
        lookup = {(x["task"], x["arm"], x["character_a"],
                   x["character_b"], x["orientation"]): x["sha256"]
                  for x in self.key}
        for a, b in (("甲", "由"), ("韦", "芈")):
            for orientation in ("upright", "rotated"):
                self.assertEqual(
                    lookup[("pair", "ab-fusion", a, b, orientation)],
                    lookup[("pair", "thickness-fixed", a, b, orientation)])

    def test_pair_vs_self_not_pooled(self):
        result = benchmark.score(self.key, self.responses)
        self.assertEqual(set(result["counts"]), {
            f"{task}/{arm}" for task, arms in benchmark.TASK_ARMS.items()
            for arm in arms})
        self.assertEqual(result["comparisons"][
            "self:thickness-fixed>harmonic"]["paired_orientations"], 40)


if __name__ == "__main__":
    unittest.main()
