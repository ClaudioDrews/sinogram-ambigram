#!/usr/bin/env python3
"""Score blinded rotational-sinogram VLM recognition after answers are frozen.

Standard-library only. Images, model prompts and provider communication are
outside this script. Never provide ground_truth.csv to inference agents.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path
import unicodedata

MODELS = {
    "MM": "minimax/minimax-m3.1-flash",
    "DS": "deepseek/deepseek-v4.1-flash",
    "HY": "tencent/hy4",
    "GLM": "z-ai/glm-5.3-flash",
}
ARMS = ("main-original", "thickness-fixed", "r-odd", "harmonic", "ab-fusion")
TASK_ARMS = {
    "self": ("main-original", "thickness-fixed", "r-odd", "harmonic"),
    "pair": ("main-original", "thickness-fixed", "ab-fusion"),
}


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_ideograph(text: str) -> bool:
    return (len(text) == 1 and
            unicodedata.name(text, "").startswith(
                ("CJK UNIFIED IDEOGRAPH-", "CJK COMPATIBILITY IDEOGRAPH-")))


def classify(raw: str, explicit_status: str | None = None) -> tuple[str, str]:
    """Return (status, parsed character); never normalize variant characters."""
    if explicit_status in ("error", "unavailable"):
        return explicit_status, ""
    parsed = raw.strip()
    if parsed == "UNKNOWN":
        return "unknown", ""
    if is_ideograph(parsed):
        return "valid", parsed
    return "invalid", ""


def parse_observations(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict]:
    """Accept the published matrix or future long-form model response CSV."""
    if not rows:
        raise ValueError("No responses")
    observations = {}
    if "trial_id" not in rows[0]:
        raise ValueError("Missing trial_id")
    if set(MODELS).issubset(rows[0]):
        for row in rows:
            tid = row["trial_id"]
            for short, model in MODELS.items():
                token = row[short]
                status = ("error" if token == "ERROR" else
                          "invalid" if token == "INVALID" else None)
                raw = "" if status else token
                parsed_status, character = classify(raw, status)
                key = (model, tid)
                if key in observations:
                    raise ValueError("Duplicate model/trial: " + str(key))
                observations[key] = {
                    "raw": raw, "status": parsed_status, "parsed": character}
    else:
        needed = {"trial_id", "model_id", "raw_response"}
        if not needed.issubset(rows[0]):
            raise ValueError("Long-form input requires " + repr(needed))
        for row in rows:
            key = (row["model_id"], row["trial_id"])
            if key in observations:
                raise ValueError("Duplicate model/trial: " + str(key))
            original_status = row.get("status", "") or None
            status, character = classify(row["raw_response"], original_status)
            if original_status and original_status != status:
                raise ValueError("Status inconsistent with response for " + str(key))
            observations[key] = {
                "raw": row["raw_response"], "status": status,
                "parsed": character,
                "model_version": row.get("model_version", "")}
    return observations


def validate_ground_truth(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    needed = {"trial_id", "pair_id", "task", "arm", "orientation",
              "expected_character", "character_a", "character_b", "sha256"}
    if len(rows) == 0 or not needed.issubset(rows[0]):
        raise ValueError("Invalid ground truth columns")
    by_trial, by_pair = {}, collections.defaultdict(list)
    for row in rows:
        tid, pair = row["trial_id"], row["pair_id"]
        if tid in by_trial:
            raise ValueError("Duplicate trial ID: " + tid)
        if row["task"] not in TASK_ARMS:
            raise ValueError("Unknown task")
        if row["arm"] not in TASK_ARMS[row["task"]]:
            raise ValueError("Arm incompatible with task")
        if row["orientation"] not in ("upright", "rotated"):
            raise ValueError("Invalid orientation")
        if not is_ideograph(row["expected_character"]):
            raise ValueError("Invalid expected character")
        if len(row["sha256"]) != 64 or any(
                c not in "0123456789abcdef" for c in row["sha256"]):
            raise ValueError("Invalid PNG hash")
        if row["task"] == "self" and row["character_a"] != row["character_b"]:
            raise ValueError("Self task must use same character")
        expected = (row["character_a"] if row["orientation"] == "upright"
                    else row["character_b"])
        if row["expected_character"] != expected:
            raise ValueError("Orientation target mismatch")
        by_trial[tid] = row
        by_pair[pair].append(row)
    for pair, items in by_pair.items():
        if len(items) != 2 or {x["orientation"] for x in items} != {
                "upright", "rotated"}:
            raise ValueError("Missing or duplicated orientation: " + pair)
        if len({(x["arm"], x["task"], x["character_a"],
                 x["character_b"]) for x in items}) != 1:
            raise ValueError("Inconsistent pair metadata: " + pair)
    return by_trial


def score(key_rows: list[dict[str, str]],
          response_rows: list[dict[str, str]]) -> dict:
    truth = validate_ground_truth(key_rows)
    observations = parse_observations(response_rows)
    models = sorted({model for model, _ in observations})
    if not models:
        raise ValueError("No models")
    expected_pairs = {(model, tid) for model in models for tid in truth}
    actual_pairs = set(observations)
    if actual_pairs != expected_pairs:
        missing = sorted(expected_pairs - actual_pairs)
        unknown = sorted(actual_pairs - expected_pairs)
        raise ValueError(f"Missing model-trials: {missing[:4]}; unexpected: {unknown[:4]}")
    by_pair = collections.defaultdict(list)
    evaluated, counts = {}, collections.defaultdict(
        lambda: {"orient_correct": 0, "orient_total": 0,
                 "double_correct": 0, "drawings": 0})
    status_count = collections.defaultdict(collections.Counter)
    for tid, ref in truth.items():
        by_pair[ref["pair_id"]].append(ref)
        for model in models:
            obs = observations[(model, tid)]
            right = (obs["status"] == "valid" and
                     obs["parsed"] == ref["expected_character"])
            evaluated[(model, tid)] = right
            entry = counts[(ref["task"], ref["arm"])]
            entry["orient_total"] += 1
            entry["orient_correct"] += int(right)
            status_count[model][obs["status"]] += 1
    # Independent primary unit within each model: one drawing, two orientations.
    by_target = collections.defaultdict(dict)
    for pair_id, items in by_pair.items():
        meta = items[0]
        for model in models:
            good = all(evaluated[(model, x["trial_id"])] for x in items)
            entry = counts[(meta["task"], meta["arm"])]
            entry["drawings"] += 1
            entry["double_correct"] += int(good)
        for x in items:
            key = (meta["task"], meta["arm"], meta["character_a"],
                   meta["character_b"], x["orientation"])
            by_target[key] = {
                model: evaluated[(model, x["trial_id"])] for model in models}
    comparisons = {}
    for task, arms in TASK_ARMS.items():
        for prior in arms:
            for later in arms:
                if prior == later:
                    continue
                flipped_to_right = flipped_to_wrong = 0
                valid_pairs = 0
                chars = sorted({(x["character_a"], x["character_b"])
                                for x in key_rows if x["task"] == task})
                for ca, cb in chars:
                    for orientation in ("upright", "rotated"):
                        earlier = by_target.get((task, prior, ca, cb, orientation))
                        after = by_target.get((task, later, ca, cb, orientation))
                        if earlier is None or after is None:
                            continue
                        for model in models:
                            valid_pairs += 1
                            flipped_to_right += int(not earlier[model] and after[model])
                            flipped_to_wrong += int(earlier[model] and not after[model])
                comparisons[(task, prior, later)] = {
                    "improved": flipped_to_right, "worsened": flipped_to_wrong,
                    "paired_orientations": valid_pairs}
    return {
        "models": models, "n_trials": len(truth),
        "n_observations": len(observations), "n_drawings": len(by_pair),
        "counts": {f"{t}/{a}": v for (t, a), v in sorted(counts.items())},
        "status": {m: dict(counter) for m, counter in status_count.items()},
        "comparisons": {f"{t}:{a}>{b}": v
                        for (t, a, b), v in comparisons.items()}}


def report_markdown(result: dict) -> str:
    lines = [
        "# Blind VLM reading pilot — independently scored results", "",
        "All counts use exact CJK Unicode matching; invalid/UNKNOWN/errors "
        "remain incorrect. Small selected pilot; no human-reader evidence.", "",
        f"Trials: {result['n_trials']}; models: {len(result['models'])}; "
        f"responses: {result['n_observations']}; drawings: {result['n_drawings']}.",
        "", "## Recognition", "",
        "| Task | Arm | Both directions | Single direction |",
        "|---|---|---:|---:|",
    ]
    for key, c in result["counts"].items():
        task, arm = key.split("/")
        lines.append(f"| {task} | {arm} | "
                     f"{c['double_correct']}/{c['drawings']} | "
                     f"{c['orient_correct']}/{c['orient_total']} |")
    lines.extend(["", "## Paired single-orientation comparisons", "",
                  "| Task | Earlier | Later | Improved | Worsened | N |",
                  "|---|---|---|---:|---:|---:|"])
    for key, c in result["comparisons"].items():
        task, rest = key.split(":")
        earlier, later = rest.split(">")
        if earlier not in ("main-original", "thickness-fixed"):
            continue
        lines.append(f"| {task} | {earlier} | {later} | "
                     f"{c['improved']} | {c['worsened']} | "
                     f"{c['paired_orientations']} |")
    lines += ["", "## Per-model output status", "",
              "| Model | Valid | UNKNOWN | Invalid | Error | Unavailable |",
              "|---|---:|---:|---:|---:|---:|"]
    for model, c in sorted(result["status"].items()):
        lines.append(f"| {model} | {c.get('valid', 0)} | "
                     f"{c.get('unknown', 0)} | {c.get('invalid', 0)} | "
                     f"{c.get('error', 0)} | {c.get('unavailable', 0)} |")
    lines.extend(["", "## Interpretation",
                  "Counts are descriptive; model×drawing observations are "
                  "not statistically independent across characters, arms or "
                  "model training backgrounds. VLM recognition does not prove "
                  "human readability.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parents[1]
    parser.add_argument("--responses", default=str(here / "data/responses_matrix.csv"))
    parser.add_argument("--key", default=str(here / "data/ground_truth.csv"))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verify-pilot", action="store_true",
                        help="Fail if the published pilot counts change")
    args = parser.parse_args()
    result = score(read_csv(args.key), read_csv(args.responses))
    if args.verify_pilot:
        expected = {
            "self/main-original": (10, 20, 25, 40),
            "self/thickness-fixed": (14, 20, 31, 40),
            "self/r-odd": (13, 20, 31, 40),
            "self/harmonic": (15, 20, 32, 40),
            "pair/main-original": (0, 8, 0, 16),
            "pair/thickness-fixed": (0, 8, 0, 16),
            "pair/ab-fusion": (0, 8, 0, 16),
        }
        assert (result["n_trials"], result["n_observations"],
                result["n_drawings"]) == (52, 208, 26)
        for key, (dual, nd, correct, no) in expected.items():
            c = result["counts"][key]
            assert (c["double_correct"], c["drawings"],
                    c["orient_correct"], c["orient_total"]) == (
                dual, nd, correct, no), (key, c)
    text = json.dumps(result, ensure_ascii=False, indent=2) if args.json else report_markdown(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
