#!/usr/bin/env python3
"""Predeclared, source-pinned PRC contour-fidelity comparison.

Use before accepting corrected-width semantics. This benchmark selects 32
previously unseen GB2312 codepoints by *source metadata only*, eight from
each stroke-count stratum, with a frozen hash ordering. It reconstructs the
MMah original outline from the `strokes` SVG paths separately from both
median-based renderers. All numbers are geometric, never reading evidence.

The reference is a 109x109 scanline approximation to the original SVG paths:
Q/C curves are flattened by prc_construct.parse_path, and path subcontours
are filled even-odd. It is not a browser-grade vector rasterizer. Numerical
ties, miter/cap geometry and source median offsets remain limitations.
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
import prc_construct as v2
import prc_construct_legacy_v116 as v116

SOURCE_SHA256 = "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
SEED = "prc-width-independent-stratified-2026-11-07-v1"
EXCLUDED_EXPLORATORY = frozenset("中口日田目甲由韦芈")
PER_STRATUM = 8
EM_CENTRE = (512.0, 384.0)
EM_SIDE = 984.0
STRATA = ("1-4", "5-8", "9-12", "13+")


def stratum(n: int) -> str:
    if 1 <= n <= 4:
        return "1-4"
    if n <= 8:
        return "5-8"
    if n <= 12:
        return "9-12"
    return "13+"


def select_source_only(graphics: dict) -> list[tuple[str, str]]:
    pools = {label: [] for label in STRATA}
    for char, data in graphics.items():
        if len(char) != 1 or char in EXCLUDED_EXPLORATORY:
            continue
        try:
            char.encode("gb2312")
        except UnicodeEncodeError:
            continue
        strokes = data.get("strokes", [])
        medians = data.get("medians", [])
        if not strokes or len(strokes) != len(medians) or not all(strokes):
            continue
        label = stratum(len(strokes))
        rank = hashlib.sha256((SEED + "|" + char).encode("utf-8")).hexdigest()
        pools[label].append((rank, char))
    selected = []
    for label in STRATA:
        if len(pools[label]) < PER_STRATUM:
            raise ValueError(f"Insufficient valid source cases for stratum {label}")
        selected.extend((label, char) for _, char in
                        sorted(pools[label])[:PER_STRATUM])
    if len(set(char for _, char in selected)) != PER_STRATUM * len(STRATA):
        raise AssertionError("Cohort has duplicate glyphs")
    return selected


def source_outline_mask(entry: dict) -> np.ndarray:
    # The original SVG outline data, not a polygon from median half-width.
    scale = v2.EM / EM_SIDE
    offset = np.asarray(EM_CENTRE, dtype=np.float64)
    combined = np.zeros((v2.GRID, v2.GRID), dtype=bool)
    for svg_path in entry["strokes"]:
        subpath_mask = np.zeros_like(combined)
        for polygon in v2.parse_path(svg_path):
            transformed = (polygon - offset) * scale + v2.EM / 2
            single = np.zeros_like(combined)
            v2.fill_polygon(transformed, single)
            subpath_mask ^= single  # even-odd within the same source stroke
        combined |= subpath_mask    # union between strokes
    return combined


def metrics(reference: np.ndarray, proposed: np.ndarray) -> dict:
    source_area = int(reference.sum())
    candidate_area = int(proposed.sum())
    intersection = int(np.logical_and(reference, proposed).sum())
    union = int(np.logical_or(reference, proposed).sum())
    return {
        "iou": intersection / union if union else 0.0,
        "area": candidate_area,
        "area_relative_error": abs(candidate_area-source_area) / source_area,
        "source_retained": intersection / source_area,
        "candidate_precision": intersection / candidate_area if candidate_area else 0.0,
    }


def run(graphics_path: Path, out: Path, enforce: bool) -> dict:
    digest = hashlib.sha256(graphics_path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Pinned source mismatch: {digest}")
    graphics = v2.load_graphics(graphics_path)
    selected = select_source_only(graphics)
    records = []
    for label, char in selected:
        reference = source_outline_mask(graphics[char])
        if not reference.any():
            raise AssertionError(f"Empty source outline for U+{ord(char):04X}")
        strokes = v2.load_glyph(char, graphics, EM_CENTRE, EM_SIDE)
        if len(strokes) != len(graphics[char]["strokes"]):
            raise AssertionError(f"Unexpected median omission for U+{ord(char):04X}")
        old_ink = v116.raster(strokes)
        new_ink = v2.raster(strokes)
        old = metrics(reference, old_ink)
        new = metrics(reference, new_ink)
        records.append({
            "character": char, "codepoint": f"U+{ord(char):04X}",
            "stratum": label, "stroke_count": len(strokes),
            "source_area": int(reference.sum()),
            "legacy_v116": old, "corrected_width_v2": new,
            "iou_delta": new["iou"]-old["iou"],
            "different_pixels": int(np.count_nonzero(new_ink != old_ink)),
        })
    old_iou = [x["legacy_v116"]["iou"] for x in records]
    new_iou = [x["corrected_width_v2"]["iou"] for x in records]
    old_error = [x["legacy_v116"]["area_relative_error"] for x in records]
    new_error = [x["corrected_width_v2"]["area_relative_error"] for x in records]
    summary = {
        "schema": "prc-original-outline-fidelity-v1",
        "status": "exploratory geometric measurement, not human readability",
        "source_sha256": digest,
        "historical_geometry_git_blob": "87d02ef641f879dae41275551546a671381b9fb9",
        "geometry_semantics": {
            "legacy_v116": "measured_half_width_halved_again_historically",
            "corrected_width_v2": "measured_half_width_v2",
        },
        "region": "mm ah source, GB2312 repertoire; regional glyph forms not certified",
        "selection_seed": SEED,
        "selection_rule": "8 SHA-256-ranked, GB2312-encodable glyphs per source stroke-count stratum; excludes nine previous VLM pilot glyphs",
        "strata": list(STRATA),
        "n": len(records),
        "median_iou_legacy": float(np.median(old_iou)),
        "median_iou_corrected": float(np.median(new_iou)),
        "median_iou_delta_paired": float(np.median(np.asarray(new_iou) - old_iou)),
        "mean_iou_delta_paired": float(np.mean(np.asarray(new_iou) - old_iou)),
        "median_relative_area_error_legacy": float(np.median(old_error)),
        "median_relative_area_error_corrected": float(np.median(new_error)),
        "corrected_better": sum(a > b for a, b in zip(new_iou, old_iou)),
        "corrected_equal": sum(a == b for a, b in zip(new_iou, old_iou)),
        "corrected_worse": sum(a < b for a, b in zip(new_iou, old_iou)),
        "changed_pixel_cases": sum(x["different_pixels"] > 0 for x in records),
        "human_readability_validated": False,
        "source_forms_certified": False,
        "raster_reference_limit": "SVG curves flattened to polygons; scanline even-odd source reconstruction at 109x109; no browser-renderer parity assertion",
        "records": records,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "source-outline-fidelity.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
        encoding="utf-8")
    with (out / "source-outline-fidelity.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["codepoint", "character", "stratum", "strokes",
                         "source_area", "legacy_iou", "corrected_iou",
                         "paired_iou_delta", "legacy_area_error",
                         "corrected_area_error", "different_pixels"])
        for r in records:
            writer.writerow([
                r["codepoint"], r["character"], r["stratum"],
                r["stroke_count"], r["source_area"],
                format(r["legacy_v116"]["iou"], ".12g"),
                format(r["corrected_width_v2"]["iou"], ".12g"),
                format(r["iou_delta"], ".12g"),
                format(r["legacy_v116"]["area_relative_error"], ".12g"),
                format(r["corrected_width_v2"]["area_relative_error"], ".12g"),
                r["different_pixels"],
            ])
    print(json.dumps({k: v for k, v in summary.items() if k != "records"},
                     ensure_ascii=False, sort_keys=True))
    if enforce:
        if summary["changed_pixel_cases"] != len(records):
            raise AssertionError("Corrected-width code failed to change all sampled silhouettes")
        if summary["median_iou_corrected"] < summary["median_iou_legacy"]:
            raise AssertionError("Median source-outline IoU regressed; review the original contour fit")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--require-not-worse", action="store_true",
                        help="Enforce preregistered median-IoU non-regression and actual pixel changes")
    args = parser.parse_args()
    run(args.graphics, args.out, args.require_not_worse)


if __name__ == "__main__":
    main()
