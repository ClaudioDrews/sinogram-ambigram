"""Source-level fixed-cohort replay for PRC v1.16, with SHA-256 pin.

This reproduces the archived 120 rotation-centre examples, 53 sector-rule
examples and six sector representatives using the **published** source
geometry and construction module. Published cohorts are frozen as inputs:
this does NOT rerun the historical candidate-selection pipeline.
No legibility or reader-study result is implied.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import prc_construct as pc  # noqa: E402

SOURCE_SHA256 = "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
SOURCE_COMMIT = "bddc96d41bef78427ed0e034e9f7e31d71fd1b92"
CENTRE_COLUMNS = ["source", "target", "box_sym", "centre_sym", "rules_sym",
                  "final_sym", "retention", "meanings_not_tested"]
SECTOR_COLUMNS = ["source", "target", "base_sym", "edited_sym", "gain",
                  "retention", "growth", "constraints_pass"]
REPS = ("令", "告", "昔", "普", "匿", "阗")
EM_CENTRE = (512.0, 384.0)
EM_SIDE = 984.0
EPS = 2e-12


def cohort(path: Path, columns: list[str], size: int) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError(f"Noncanonical CSV header in {path}")
        rows = list(reader)
    if len(rows) != size or any(None in x or None in x.values() for x in rows):
        raise ValueError(f"Invalid cohort row count or malformed CSV: {path}")
    if len({(r["source"], r["target"]) for r in rows}) != size:
        raise ValueError("Duplicate source/target in fixed cohort")
    return rows


def copy_strokes(strokes):
    return [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]


def centred(strokes, ref, origin):
    best_c, best_o = origin, -1.0
    for dy in (-1.5, 0.0, 1.5):
        for dx in (-1.5, 0.0, 1.5):
            c = (origin[0] + dx, origin[1] + dy)
            score = pc.symmetric_ink(strokes, c, ref)
            if score > best_o:
                best_o, best_c = score, c
    return best_c, best_o


def centre_case(ch: str, partner: str, graphics: dict) -> dict:
    """Exact per-item procedure of archived analysis/step12_repo_module.py."""
    strokes = pc.load_glyph(ch, graphics, EM_CENTRE, EM_SIDE)
    if not strokes:
        raise ValueError(f"Absent source strokes: {ch}")
    ref = pc.raster(strokes)
    origin = (pc.EM / 2, pc.EM / 2)
    row = {"a": ch, "b": partner, "n_strokes": len(strokes),
           "ink": int(ref.sum()), "box": pc.symmetric_ink(strokes, origin, ref)}
    c0 = pc.ink_centroid(strokes)
    row["centroid"] = list(c0)
    row["centroid_overlap"] = pc.symmetric_ink(strokes, c0, ref)
    best_c, best_o = centred(strokes, ref, c0)
    row["centre_only"] = best_o
    row["centre_only_at"] = list(best_c)
    work = copy_strokes(strokes)
    row["reconciled"] = pc.reconcile(work, best_c)
    row["with_rules"] = pc.symmetric_ink(work, best_c, ref)
    row["retention"] = pc.retention(work, ref)
    best_c2, best_o2 = best_c, row["with_rules"]
    for dy in (-1.5, 0.0, 1.5):
        for dx in (-1.5, 0.0, 1.5):
            c = (best_c[0] + dx, best_c[1] + dy)
            w = copy_strokes(strokes)
            pc.reconcile(w, c)
            o = pc.symmetric_ink(w, c, ref)
            if o > best_o2:
                best_o2, best_c2 = o, c
    w = copy_strokes(strokes)
    pc.reconcile(w, best_c2)
    row["best_centre"] = list(best_c2)
    row["final"] = max(best_o2, row["with_rules"])
    leg = pc.legibility(w, best_c2, ref)
    for key in ("L", "mu", "ret", "pi"):
        row[key] = leg[key]
    return row


def best_sector_centre(strokes, ref, origin):
    best, score = origin, -1.0
    for dy in (-1.5, 0.0, 1.5):
        for dx in (-1.5, 0.0, 1.5):
            c = (origin[0] + dx, origin[1] + dy)
            val = pc.sector_score(strokes, c, ref)
            if val["ok"] and val["sym"] > score:
                best, score = c, val["sym"]
    return best


def historic_m1(strokes, masks, kernel):
    """Archived M1 counts on *eroded* masks, unlike the evolved pc module."""
    g = pc.raster(strokes)
    mult = np.ones(9)
    for i in range(3):
        for j in range(3):
            s = i * 3 + j
            r = (2 - i) * 3 + (2 - j)
            if r <= s:
                continue
            a = float((g & masks[s]).sum())
            b = float((g & masks[r]).sum())
            if a <= 0 or b <= 0:
                continue
            ratio = b / a
            if ratio > 1:
                mult[s] = min(1.40, ratio)
            else:
                mult[r] = min(1.40, 1 / ratio)
    field = pc.multiplier_field(mult, masks, kernel)
    return pc.apply_sector_field(strokes, field), mult


def historic_m2(strokes, centre, ref, masks, kernel):
    mults = np.ones(9)
    best = pc.sector_score(strokes, centre, ref)
    for _ in range(3):
        improved = False
        for s in range(9):
            for value in (0.55, 0.70, 0.85, 1.0, 1.15, 1.30, 1.45):
                trial = mults.copy()
                trial[s] = value
                candidate = pc.apply_sector_field(
                    strokes, pc.multiplier_field(trial, masks, kernel)
                )
                score = pc.sector_score(candidate, centre, ref)
                if score["ok"] and score["sym"] > best["sym"] + 1e-9:
                    best, mults, improved = score, trial, True
        if not improved:
            break
    return pc.apply_sector_field(
        strokes, pc.multiplier_field(mults, masks, kernel)
    ), mults


def sector_case(ch: str, partner: str | None, graphics: dict,
                masks, kernel, representative: bool = False) -> dict:
    strokes = pc.load_glyph(ch, graphics, EM_CENTRE, EM_SIDE)
    if not strokes:
        raise ValueError(f"Absent source strokes: {ch}")
    ref = pc.raster(strokes)
    centre = best_sector_centre(strokes, ref, pc.ink_centroid(strokes))
    s0 = pc.sector_score(strokes, centre, ref)
    w1, m1 = historic_m1(strokes, masks, kernel)
    c1 = best_sector_centre(w1, ref, centre)
    s1 = pc.sector_score(w1, c1, ref)
    if not representative:
        return {"char": ch, "partner": partner, "n_strokes": len(strokes),
                "base": s0, "m1": {"mult": m1.tolist(), "score": s1}}
    w2, m2 = historic_m2(strokes, centre, ref, masks, kernel)
    c2 = best_sector_centre(w2, ref, centre)
    s2 = pc.sector_score(w2, c2, ref)
    return {"char": ch, "n_strokes": len(strokes), "ink": int(ref.sum()),
            "centre": list(centre), "baseline": s0,
            "m1": {"multipliers": m1.tolist(), "score": s1, "centre": list(c1)},
            "m2": {"multipliers": m2.tolist(), "score": s2, "centre": list(c2)}}


def compare(expected: dict, actual: dict, names: dict[str, str], label: str) -> None:
    for input_key, result_key in names.items():
        x, y = float(expected[input_key]), float(actual[result_key])
        if not (math.isfinite(x) and math.isfinite(y) and abs(x-y) <= EPS):
            raise AssertionError(f"{label}.{input_key}: archived {x}, rerun {y}")


def replay(graphics_path: Path, archive: Path, out: Path, with_reps: bool = True):
    digest = hashlib.sha256(graphics_path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Pinned graphics SHA-256 mismatch: {digest}")
    centres = cohort(archive / "prc-centre-extremity-120.csv", CENTRE_COLUMNS, 120)
    sectors = cohort(archive / "prc-sector-generalisation-53.csv", SECTOR_COLUMNS, 53)
    if not all(r["meanings_not_tested"] == "True" for r in centres):
        raise ValueError("Unexpected human-readability metadata")
    graphics = pc.load_graphics(graphics_path)
    masks = pc.sector_masks(grid=pc.GRID, margin=6)
    kernel = pc.gaussian_kernel(3.0)
    main_out = []
    for i, r in enumerate(centres, 1):
        item = centre_case(r["source"], r["target"], graphics)
        compare(r, item, {"box_sym": "box", "centre_sym": "centre_only",
                          "rules_sym": "with_rules", "final_sym": "final",
                          "retention": "retention"}, f"centre-{i}")
        main_out.append(item)
        if i % 20 == 0:
            print(f"Reproduced centre {i}/120", flush=True)
    sector_out = []
    for i, r in enumerate(sectors, 1):
        item = sector_case(r["source"], r["target"], graphics, masks, kernel)
        values = {"base_sym": item["base"]["sym"], "edited_sym": item["m1"]["score"]["sym"],
                  "gain": item["m1"]["score"]["sym"] - item["base"]["sym"],
                  "retention": item["m1"]["score"]["retention"],
                  "growth": item["m1"]["score"]["growth"]}
        for key, measured in values.items():
            x = float(r[key])
            if not (math.isfinite(x) and abs(x-measured) <= EPS):
                raise AssertionError(f"sector-{i}.{key}: archived {x}, rerun {measured}")
        if (r["constraints_pass"] == "True") != item["m1"]["score"]["ok"]:
            raise AssertionError(f"sector-{i}: constraint status changed")
        sector_out.append(item)
        if i % 10 == 0:
            print(f"Reproduced sector {i}/53", flush=True)
    rep_out = []
    if with_reps:
        for ch in REPS:
            rep_out.append(sector_case(ch, None, graphics, masks, kernel, representative=True))
            print(f"Reproduced representative {ch}", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    results = {"repo_module_results.json": main_out,
               "sector_generalisation.json": sector_out}
    if with_reps:
        results["sector_experiment.json"] = rep_out
    for name, rows in results.items():
        (out / name).write_text(
            json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"scope": "fixed-cohort numeric replay, not original cohort discovery",
            "graphics_sha256": digest, "centre_count": len(main_out),
            "sector_count": len(sector_out), "representatives": len(rep_out),
            "human_legibility_tested": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graphics", type=Path, default=ROOT / "data/prc/graphics.txt")
    p.add_argument("--archive", type=Path, default=ROOT / "data/prc/archive-v1.16")
    p.add_argument("--out", type=Path, default=ROOT / "output/prc-v116-replay")
    p.add_argument("--skip-representatives", action="store_true")
    a = p.parse_args()
    print(json.dumps(replay(a.graphics, a.archive, a.out, not a.skip_representatives),
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
