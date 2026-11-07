"""Stage 14: PRC half-turn coarse-geometry candidate search.

Requires a verified Stage 12 median cache and Stage 13 preset manifest.
Evaluates *all* pairs at 37x37 coarse raster resolution; retains the top K
partners per glyph for refinement. NOT exact Hausdorff, a complete exact-grid
ranking, or evidence of human readability.

  python code/stage14_prc_search.py --cache data/prc/cache \
      --inventories data/prc/inventories --out data/prc/search
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COARSE = 37


def load_verified(cache: Path, inventories: Path, preset: str):
    meta = json.loads((cache / "meta.json").read_text(encoding="utf-8"))
    manifest = json.loads((inventories / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != "prc-presets-v1":
        raise ValueError("Unsupported or missing preset schema")
    if preset not in manifest["presets"]:
        raise ValueError("Unknown regional preset")
    source_sha = manifest["graphics_sha256"]
    if len({row.get("source_sha256") for row in meta}) != 1 or meta[0]["source_sha256"] != source_sha:
        raise ValueError("Source SHA mismatch between cache and preset")
    if not all(row.get("region") == "unassigned" for row in meta):
        raise ValueError("Expected unassigned raw MMah cache; regional mixing forbidden")
    if any(row.get("source_scope") != "mixed-simplified-traditional" for row in meta):
        raise ValueError("Source scope differs from expected MMah input")
    glyph_index = {row["char"]: i for i, row in enumerate(meta)}
    raw = (inventories / (preset + ".txt")).read_text(encoding="utf-8")
    chars = raw.splitlines()
    if len(set(chars)) != len(chars) or not chars or any(len(x) != 1 for x in chars):
        raise ValueError("Invalid or empty preset membership")
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != manifest["presets"][preset]["members_sha256"]:
        raise ValueError("Preset member checksum mismatch")
    if len(chars) != manifest["presets"][preset]["covered"]:
        raise ValueError("Preset size mismatch")
    if sorted(chars, key=ord) != chars:
        raise ValueError("Preset is not Unicode sorted")
    try:
        selected = np.array([glyph_index[ch] for ch in chars], dtype=np.int64)
    except KeyError as exc:
        raise ValueError("Preset includes glyph absent from cache") from exc
    dt = np.load(cache / "dt.npy", mmap_mode="r")
    if dt.shape != (len(meta), 109, 109):
        raise ValueError("Incompatible Stage 12 distance transforms")
    return meta, manifest, chars, selected, dt


def coarse_occupancy(dt: np.ndarray, selected: np.ndarray) -> np.ndarray:
    """109 -> symmetric 111 padding -> 37 cells of width 3 (C2 equivariant)."""
    occ = np.asarray(dt[selected] == 0, dtype=bool)
    padded = np.pad(occ, ((0, 0), (1, 1), (1, 1)), mode="constant")
    return padded.reshape(len(selected), COARSE, 3, COARSE, 3).max(axis=(2, 4))


def rank(cache: Path, inventories: Path, out: Path,
         preset: str = "cn-s-gb2312", top_k: int = 20,
         batch_size: int = 64) -> dict:
    if not 1 <= top_k <= 500:
        raise ValueError("top_k must be between 1 and 500")
    if not 1 <= batch_size <= 1024:
        raise ValueError("batch_size out of range")
    meta, manifest, chars, idx, dt = load_verified(cache, inventories, preset)
    occ = coarse_occupancy(dt, idx)
    n = len(chars)
    flat = occ.reshape(n, -1).astype(np.float32)
    rotated = occ[:, ::-1, ::-1].reshape(n, -1).astype(np.float32)
    counts = flat.sum(axis=1, dtype=np.float64)
    del dt, occ
    null_mu = np.empty(n, dtype=np.float64)
    null_sd = np.empty(n, dtype=np.float64)
    pairs: dict[tuple[int, int], float] = {}
    for first in range(0, n, batch_size):
        last = min(first + batch_size, n)
        intersections = flat[first:last] @ rotated.T
        # Raster counts <=1369 are exactly represented in float32.
        union = counts[first:last, None] + counts[None, :] - intersections.astype(np.float64)
        overlaps = intersections.astype(np.float64) / np.maximum(union, 1.0)
        for local, i in enumerate(range(first, last)):
            scores = overlaps[local]
            others = np.concatenate((scores[:i], scores[i + 1:])) if n > 1 else scores
            null_mu[i] = float(others.mean())
            null_sd[i] = max(float(others.std(ddof=0)), 1e-12)
            # Every partner is scored at coarse resolution; ties are
            # deterministically resolved by Unicode-sorted input order.
            ordered = np.argsort(-scores, kind="stable")[:min(n, top_k)]
            for j in ordered:
                a, b = (i, int(j)) if i <= j else (int(j), i)
                score = float(scores[j])
                if (a, b) in pairs and not np.isclose(pairs[(a, b)], score, atol=1e-8):
                    raise AssertionError("Expected C2-pair score symmetry")
                pairs[(a, b)] = score
    out.mkdir(parents=True, exist_ok=True)
    with (out / "null_model_grid37.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["character", "n_strokes", "null_mu_iou_grid37",
                         "null_sigma_iou_grid37", "partner_count"])
        for i, ch in enumerate(chars):
            writer.writerow([ch, meta[int(idx[i])]["n_strokes"], f"{null_mu[i]:.9f}",
                             f"{null_sd[i]:.9f}", n - 1 if n > 1 else 1])
    records = []
    for (i, j), overlap in pairs.items():
        za = (overlap - null_mu[i]) / null_sd[i]
        zb = (overlap - null_mu[j]) / null_sd[j]
        records.append((i, j, overlap, za, zb, min(za, zb)))
    records.sort(key=lambda x: (-x[5], -x[2], ord(chars[x[0]]), ord(chars[x[1]])))
    with (out / "candidates_grid37.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["a", "b", "n_strokes_a", "n_strokes_b", "iou_grid37",
                         "z_a_grid37", "z_b_grid37", "z_pair_grid37", "preset", "region"])
        for i, j, sim, za, zb, zp in records:
            writer.writerow([chars[i], chars[j], meta[int(idx[i])]["n_strokes"],
                             meta[int(idx[j])]["n_strokes"], f"{sim:.9f}",
                             f"{za:.9f}", f"{zb:.9f}", f"{zp:.9f}", preset, "cn-s"])
    report = {
        "schema": "prc-coarse-search-v1", "preset": preset, "region": "cn-s",
        "regional_form_certified": False, "graphics_sha256": manifest["graphics_sha256"],
        "metric": "37x37 median-occupancy IoU under 180-degree rotation; not exact",
        "null_model": "all other preset members, population mean and std",
        "pair_z_definition": "min(z_a_grid37,z_b_grid37)",
        "selection": "union of top-K per glyph, stable Unicode tie break",
        "n_glyphs": n, "n_candidates": len(records), "top_k": top_k,
        "ranking_is_full_exact_grid": False, "human_legibility_validated": False,
    }
    (out / "search-summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, default=ROOT / "data/prc/cache")
    p.add_argument("--inventories", type=Path, default=ROOT / "data/prc/inventories")
    p.add_argument("--out", type=Path, default=ROOT / "data/prc/search")
    p.add_argument("--preset", default="cn-s-gb2312")
    p.add_argument("--top-k", type=int, default=20)
    p.add_argument("--batch-size", type=int, default=64)
    args = p.parse_args()
    print(json.dumps(rank(args.cache, args.inventories, args.out,
                          args.preset, args.top_k, args.batch_size), sort_keys=True))


if __name__ == "__main__":
    main()
