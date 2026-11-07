#!/usr/bin/env python3
"""Frozen, source-only pair selection and A/B fusion threshold sensitivity.

This study audits unchanged PR #16 code. It never evaluates human reading.
The full protocol is in experiments/ab-fusion-threshold-v1/PROTOCOL.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import prc_construct as pc
import prc_ab_fusion as ab

SEED = "prc-ab-threshold-2026-11-07-v1"
SOURCE_SHA256 = "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
POOL_SIZE = 128
PAIRS_PER_ARM = 16
THRESHOLDS = (2.0, 4.0, 8.0, 12.0, 16.0)
CENTRE = (54.5, 54.5)
SOURCE_CENTRE = (512.0, 384.0)
SOURCE_SIDE = 984.0
PILOT = frozenset("中口日田目甲由韦芈")
ANCHORS = (("甲", "由"), ("韦", "芈"))
CSV_FIELDS = (
    "arm", "case", "a", "b", "n_a", "n_b", "source_ink_iou",
    "threshold", "minimum_spine_rms", "matched_strokes", "union_strokes",
    "candidate_strokes", "changed_pixels", "status",
    "baseline_f1_a", "baseline_f1_b", "baseline_min_f1",
    "baseline_joint_f1", "fusion_f1_a", "fusion_f1_b",
    "fusion_min_f1", "fusion_joint_f1", "delta_min_f1",
    "delta_joint_f1",
)


def stable_hash(*parts: str) -> str:
    return hashlib.sha256("|".join((SEED, *parts)).encode("utf-8")).hexdigest()


def eligible_characters(graphics: dict) -> list[str]:
    out = []
    for char, data in graphics.items():
        if len(char) != 1 or char in PILOT:
            continue
        try:
            char.encode("gb2312")
        except UnicodeEncodeError:
            continue
        strokes, medians = data.get("strokes", []), data.get("medians", [])
        if not strokes or len(strokes) != len(medians) or not all(strokes):
            continue
        out.append(char)
    return sorted(out, key=lambda char: (stable_hash("pool", char), ord(char)))


def ink_iou(a: np.ndarray, rotated_b: np.ndarray) -> float:
    union = int(np.logical_or(a, rotated_b).sum())
    return int(np.logical_and(a, rotated_b).sum()) / union if union else 0.0


def select_cases(graphics: dict) -> tuple[list[dict], dict[str, list[pc.Stroke]]]:
    pool = eligible_characters(graphics)[:POOL_SIZE]
    if len(pool) < POOL_SIZE:
        raise AssertionError("Insufficient pinned GB2312 source glyphs")
    glyphs = {ch: pc.load_glyph(ch, graphics, SOURCE_CENTRE, SOURCE_SIDE)
              for ch in pool}
    if any(not glyphs[ch] for ch in pool):
        raise AssertionError("Selected source glyph has no usable median")
    rasters = {ch: pc.raster(glyphs[ch]) for ch in pool}
    rotated = {ch: pc.half_turn_grid(rasters[ch], CENTRE) for ch in pool}
    # Geometric enrolment comes from unmodified source drawings, NOT a
    # fusion result, match distance or chosen intervention threshold.
    ranked = []
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            aa, bb = sorted((a, b), key=ord)
            overlap = ink_iou(rasters[aa], rotated[bb])
            ranked.append((-overlap, stable_hash("enriched", aa, bb),
                           aa, bb, overlap))
    ranked.sort()
    cases, used = [], set()
    for _, _, a, b, overlap in ranked:
        if a in used or b in used:
            continue
        cases.append(dict(arm="source_overlap_enriched", a=a, b=b,
                          source_ink_iou=overlap))
        used.update((a, b))
        if len(cases) == PAIRS_PER_ARM:
            break
    if len(cases) != PAIRS_PER_ARM:
        raise AssertionError("Cannot construct 16 disjoint enriched pairs")
    remaining = sorted((ch for ch in pool if ch not in used),
                       key=lambda char: (stable_hash("control", char), ord(char)))
    control = remaining[:2 * PAIRS_PER_ARM]
    if len(control) != 2 * PAIRS_PER_ARM:
        raise AssertionError("Cannot construct 16 disjoint control pairs")
    for i in range(0, len(control), 2):
        a, b = control[i:i+2]
        aa, bb = sorted((a, b), key=ord)
        cases.append(dict(arm="source_hash_control", a=aa, b=bb,
                          source_ink_iou=ink_iou(rasters[aa], rotated[bb])))
    cases = [dict(case=f"case-{i:04d}", **item)
             for i, item in enumerate(cases, 1)]
    if len(cases) != 32 or len({ch for case in cases for ch in (case["a"], case["b"])}) != 64:
        raise AssertionError("Expected 32 distinct-character pairs, 64 unique glyphs")
    return cases, glyphs


def minimum_spine_rms(a: list[pc.Stroke], rotated_b: list[pc.Stroke]) -> float:
    best = float("inf")
    for x in a:
        xx = ab._sample(x.median)
        for y in rotated_b:
            yy = ab._sample(y.median)
            direct = np.mean(np.sum((xx - yy) ** 2, axis=1))
            reverse = np.mean(np.sum((xx - yy[::-1]) ** 2, axis=1))
            best = min(best, float(np.sqrt(min(direct, reverse))))
    return best


def classify(matches: int, pixels: int, chosen_strokes: int,
             baseline_strokes: int) -> str:
    if not matches:
        return "no_match"
    if pixels:
        return "changed_pixels"
    if chosen_strokes < baseline_strokes:
        return "accepted_pixel_identical"
    return "matched_rejected_or_union"


def measure(case: dict, glyphs: dict, threshold: float) -> dict:
    a, b = glyphs[case["a"]], glyphs[case["b"]]
    rb = ab.rotate_strokes(b, CENTRE)
    base = a + rb
    baseline = ab.score(base, a, b, CENTRE)
    baseline_raster = pc.raster(base)
    matches = ab.match_strokes(a, rb, threshold)
    candidate, info = ab.construct(a, b, CENTRE, threshold=threshold)
    if info["matched_strokes"] != len(matches):
        raise AssertionError("Registration disagrees with frozen operator")
    candidate_raster = pc.raster(candidate)
    pixels = int(np.count_nonzero(np.logical_xor(candidate_raster, baseline_raster)))
    obtained = ab.score(candidate, a, b, CENTRE)
    eps = 1e-10
    if obtained["minimum_f1"] < baseline["minimum_f1"] - eps:
        raise AssertionError("Constructor lowered min F1 below unchanged union")
    if obtained["joint_f1"] < baseline["joint_f1"] - eps:
        raise AssertionError("Constructor lowered joint F1 below unchanged union")
    return {
        "arm": case["arm"], "case": case["case"], "a": case["a"], "b": case["b"],
        "n_a": len(a), "n_b": len(b),
        "source_ink_iou": round(float(case["source_ink_iou"]), 10),
        "threshold": int(threshold),
        "minimum_spine_rms": round(minimum_spine_rms(a, rb), 10),
        "matched_strokes": len(matches),
        "union_strokes": len(base),
        "candidate_strokes": len(candidate),
        "changed_pixels": pixels,
        "status": classify(len(matches), pixels, len(candidate), len(base)),
        "baseline_f1_a": round(baseline["f1_a"], 10),
        "baseline_f1_b": round(baseline["f1_b"], 10),
        "baseline_min_f1": round(baseline["minimum_f1"], 10),
        "baseline_joint_f1": round(baseline["joint_f1"], 10),
        "fusion_f1_a": round(obtained["f1_a"], 10),
        "fusion_f1_b": round(obtained["f1_b"], 10),
        "fusion_min_f1": round(obtained["minimum_f1"], 10),
        "fusion_joint_f1": round(obtained["joint_f1"], 10),
        "delta_min_f1": round(obtained["minimum_f1"] - baseline["minimum_f1"], 10),
        "delta_joint_f1": round(obtained["joint_f1"] - baseline["joint_f1"], 10),
    }


def summarize(rows: list[dict]) -> list[dict]:
    output = []
    for arm in ("source_overlap_enriched", "source_hash_control", "previous_pilot"):
        for threshold in (int(t) for t in THRESHOLDS):
            selected = [r for r in rows if r["arm"] == arm and r["threshold"] == threshold]
            if not selected:
                raise AssertionError("Missing arm or threshold observations")
            output.append({
                "arm": arm, "threshold": threshold, "n": len(selected),
                "any_matches": sum(r["matched_strokes"] > 0 for r in selected),
                "changed_pixels_pairs": sum(r["changed_pixels"] > 0 for r in selected),
                "statuses": {k: sum(r["status"] == k for r in selected)
                             for k in ("no_match", "matched_rejected_or_union",
                                       "accepted_pixel_identical", "changed_pixels")},
                "total_changed_pixels": sum(r["changed_pixels"] for r in selected),
                "mean_delta_joint_f1": round(
                    sum(r["delta_joint_f1"] for r in selected) / len(selected), 10),
                "mean_delta_min_f1": round(
                    sum(r["delta_min_f1"] for r in selected) / len(selected), 10),
            })
    return output


def run(graphics_path: Path, out: Path) -> dict:
    digest = hashlib.sha256(graphics_path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Source SHA-256 mismatch: {digest}")
    graphics = pc.load_graphics(graphics_path)
    cases, glyphs = select_cases(graphics)
    for i, (a, b) in enumerate(ANCHORS, 1):
        if a not in graphics or b not in graphics:
            raise AssertionError("Pinned historical anchor absent from source")
        glyphs[a] = pc.load_glyph(a, graphics, SOURCE_CENTRE, SOURCE_SIDE)
        glyphs[b] = pc.load_glyph(b, graphics, SOURCE_CENTRE, SOURCE_SIDE)
        aa = pc.raster(glyphs[a])
        bb = pc.half_turn_grid(pc.raster(glyphs[b]), CENTRE)
        cases.append({"case": f"pilot-{i:04d}", "arm": "previous_pilot",
                      "a": a, "b": b, "source_ink_iou": ink_iou(aa, bb)})
    rows = [measure(case, glyphs, threshold)
            for case in cases for threshold in THRESHOLDS]
    if len(rows) != 170:
        raise AssertionError("Expected 34 pairs × 5 thresholds")
    for row in rows:
        if row["arm"] == "previous_pilot" and row["threshold"] == 4:
            if row["matched_strokes"] != 0 or row["changed_pixels"] != 0:
                raise AssertionError("Historical pilot zero-match result not reproduced")
    summary = {
        "schema": "ab-fusion-threshold-v1",
        "selection_seed": SEED,
        "source_sha256": digest,
        "source_pool_size": POOL_SIZE,
        "new_pair_count": 2 * PAIRS_PER_ARM,
        "previous_pilot_pair_count": len(ANCHORS),
        "thresholds": list(THRESHOLDS),
        "centre": list(CENTRE),
        "alphas": [0.25, 0.5, 0.75],
        "fixed_operator": "PR16 greedy 24-point RMS and constrained blend",
        "human_readability_validated": False,
        "regional_forms_certified": False,
        "arm_summaries": summarize(rows),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "cohort.json").write_text(
        json.dumps({"schema": "ab-fusion-cohort-v1", "selection_seed": SEED,
                    "source_sha256": digest, "cases": cases},
                   sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (out / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    with (out / "observations.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.graphics, args.out)
    print(json.dumps(summary, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
