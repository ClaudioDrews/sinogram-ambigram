"""Stage 7: per-glyph null model and z-score normalisation of the rotation graph.

The raw distance between two glyphs is not comparable across the inventory. A
dense glyph fills more of the character box, so it sits closer to many
partners simply because of how much ink it carries. The measured consequence
is a documented density bias (Spearman rho of about -0.43 between Hausdorff
distance and skeleton length on self-pairs; see
``findings/limitations.md``).

This stage removes that bias by comparing every pair against the *null
distribution of its own glyph*:

    mu(a), sigma(a)   mean and standard deviation of the distance from glyph
                      ``a`` to K randomly drawn partners of similar complexity
    z(a, b)           (d(a, R.b) - mu(a)) / sigma(a)

A pair is then ranked by how unusually good it is for the characters involved,
rather than by its raw distance.

**Scale.** Every number this stage produces is a **grid distance-transform
approximation**, matching the scale of ``pairs3.npy``. It is never mixed with
the exact point-cloud distances of ``data/rotation_pairs.csv``: the two
scales have different error characteristics and different rankings. Columns
are named accordingly (``z_grid``, ``percentile_z_grid``).

**Symmetry.** ``d(a, R.b)`` is symmetric, but the null model is per glyph, so
the raw z-score is not. The published per-pair value is

    z_pair(a, b) = max( z(a, b), z(b, a) )

so a pair must beat the expectation of *both* characters involved to rank
highly. Both per-side values are kept in the output for auditability.

**Determinism.** The partner sampling uses a fixed seed and a fixed
generator, and every selection step is a sort. Two runs produce byte-identical
output.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from pathlib import Path

import numpy as np

import paths
from paths import add_common_args, resolve

EM = 109.0
GRID = 109

#: Fixed seed for the null-partner sampling. Changing it changes every z-score.
SEED = 20261107

#: Number of random partners drawn per glyph for the null distribution.
NULL_PARTNERS = 30

#: Maximum stroke-count difference accepted when drawing a null partner.
#: The window widens by one stroke at a time when a glyph has too few peers.
STROKE_WINDOW = (1, 2, 3, 5, 100)

FIELDS_V2 = (
    "a", "b", "a_set", "b_set", "a_strokes", "b_strokes",
    "hausdorff_grid", "chamfer_grid", "rms_grid",
    "z_a_grid", "z_b_grid", "z_pair_grid", "percentile_z_grid",
    "stratum", "self",
)


def _load_meta(cache: Path) -> list[dict]:
    with open(cache / "meta.json", encoding="utf-8") as handle:
        return json.load(handle)


def _rotated_indices(points: np.ndarray, offsets: np.ndarray) -> list[np.ndarray]:
    """Flat indices of the half-turned sample points, one array per glyph.

    ``dist(p, R.b) = dist(R.p, b)``, so the same table serves both directions
    of a pair.
    """
    out = []
    for i in range(len(offsets) - 1):
        p = points[offsets[i]:offsets[i + 1]]
        cx = np.clip((GRID - 1) - p[:, 0].astype(np.int32), 0, GRID - 1)
        cy = np.clip((GRID - 1) - p[:, 1].astype(np.int32), 0, GRID - 1)
        out.append((cy * GRID + cx).astype(np.int64))
    return out


def _grid_hausdorff(dt_flat: np.ndarray, rot_a: np.ndarray, rot_b: np.ndarray,
                    a: int, b: int) -> float:
    """Symmetric grid Hausdorff between glyphs ``a`` and ``b``."""
    d1 = dt_flat[b][rot_a]
    d2 = dt_flat[a][rot_b]
    return float(max(d1.max(), d2.max()))


def _null_model(dt_flat: np.ndarray, rot: list[np.ndarray], strokes: np.ndarray,
                n_glyphs: int, seed: int = SEED,
                partners: int = NULL_PARTNERS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estimate the per-glyph null mean, standard deviation and partner count."""
    rng = np.random.default_rng(seed)
    mu = np.zeros(n_glyphs)
    sigma = np.zeros(n_glyphs)
    used = np.zeros(n_glyphs, dtype=np.int64)
    for a in range(n_glyphs):
        chosen: list[int] = []
        for window in STROKE_WINDOW:
            pool = np.flatnonzero(
                (np.abs(strokes - strokes[a]) <= window) & (np.arange(n_glyphs) != a))
            if len(pool) == 0:
                continue
            take = min(partners, len(pool))
            picked = rng.choice(pool, size=take, replace=False)
            chosen = [int(x) for x in picked]
            if len(chosen) >= partners:
                break
        if not chosen:
            chosen = [a]
        distances = [_grid_hausdorff(dt_flat, rot[a], rot[b], a, b) for b in chosen]
        values = np.asarray(distances, dtype=np.float64)
        mu[a] = values.mean()
        sigma[a] = values.std(ddof=0)
        if sigma[a] <= 0.0:
            sigma[a] = 1.0  # a glyph whose partners are all at distance 0
        used[a] = len(chosen)
    return mu, sigma, used


def _strata(strokes: np.ndarray, a_idx: np.ndarray, b_idx: np.ndarray) -> np.ndarray:
    """Complexity stratum of a pair: the rounded mean of its stroke counts."""
    return np.rint((strokes[a_idx] + strokes[b_idx]) / 2.0).astype(np.int32)


def _average_ranks(values: np.ndarray) -> np.ndarray:
    """Ranks of ``values`` starting at zero, ties sharing the average rank.

    This is the conventional rank definition: equal values get the same rank,
    which is the midpoint of the positions they occupy. It matters for the
    percentile because a tie at the stratum boundary would otherwise be broken
    arbitrarily by the sort order.
    """
    n = len(values)
    sorter = np.argsort(values, kind="stable")
    ranks = np.empty(n, dtype=np.float64)
    sorted_values = values[sorter]
    start = 0
    while start < n:
        stop = start + 1
        while stop < n and sorted_values[stop] == sorted_values[start]:
            stop += 1
        # positions start .. stop-1 average to (start + stop - 1) / 2
        ranks[sorter[start:stop]] = (start + stop - 1) / 2.0
        start = stop
    return ranks


def _percentile_within_stratum(z: np.ndarray, stratum: np.ndarray) -> np.ndarray:
    """Percentile rank of z inside each complexity stratum (0-100).

    The scale runs so that **a larger value means a better pair**: a pair whose
    z-score sits at the 95th percentile of its stratum is among the closest 5%
    percent of that stratum. The raw z-score keeps the opposite orientation
    (a smaller z is closer), so the percentile is its mirror.
    """
    out = np.zeros(len(z), dtype=np.float64)
    order = np.argsort(stratum, kind="stable")
    bounds = np.flatnonzero(np.diff(stratum[order])) + 1
    for block in np.split(order, bounds):
        if len(block) == 0:
            continue
        ranks = _average_ranks(z[block])
        out[block] = 100.0 - (ranks / max(len(block) - 1, 1)) * 100.0
    return out


def normalise(cache: Path, out_dir: Path, seed: int = SEED,
              partners: int = NULL_PARTNERS) -> dict:
    """Compute the null model, z-scores and percentiles; write the v2 datasets."""
    cache = Path(cache)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = _load_meta(cache)
    chars = [m["char"] for m in meta]
    sets = [m["set"] for m in meta]
    strokes = np.asarray([m["n_strokes"] for m in meta], dtype=np.int64)
    n = len(meta)

    points = np.load(cache / "points.npy")
    offsets = np.load(cache / "offsets.npy")
    dt = np.load(cache / "dt.npy", mmap_mode="r")
    dt_flat = [np.asarray(dt[i]).reshape(-1) for i in range(n)]

    print(f"rotating sample points for {n} glyphs", flush=True)
    rot = _rotated_indices(points, offsets)

    print(f"estimating null model ({partners} partners per glyph, seed {seed})", flush=True)
    mu, sigma, used = _null_model(dt_flat, rot, strokes, n, seed=seed, partners=partners)

    pairs = np.load(cache / "pairs3.npy")
    a_idx = pairs["a"].astype(np.int64)
    b_idx = pairs["b"].astype(np.int64)
    raw = pairs["haus"].astype(np.float64)

    z_a = (raw - mu[a_idx]) / sigma[a_idx]
    z_b = (raw - mu[b_idx]) / sigma[b_idx]
    z_pair = np.maximum(z_a, z_b)
    stratum = _strata(strokes, a_idx, b_idx)
    pct = _percentile_within_stratum(z_pair, stratum)

    # ---- per-glyph null model -------------------------------------------------
    null_path = out_dir / "null_model.csv"
    with open(null_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["char", "codepoint", "set", "n_strokes", "null_mu_grid",
                         "null_sigma_grid", "null_partners", "seed"])
        for i, m in enumerate(meta):
            writer.writerow([chars[i], m["codepoint"], sets[i], int(strokes[i]),
                             f"{mu[i]:.8f}", f"{sigma[i]:.8f}", int(used[i]), seed])

    # ---- full grid, z-scored ---------------------------------------------------
    order = np.lexsort((b_idx, a_idx))
    full_path = out_dir / "rotation_pairs_full_grid_v2.csv.gz"
    with open(full_path, "wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8", newline="") as text:
                writer = csv.writer(text, lineterminator="\n")
                writer.writerow(FIELDS_V2)
                for idx in order:
                    a, b = int(a_idx[idx]), int(b_idx[idx])
                    writer.writerow((
                        chars[a], chars[b], sets[a], sets[b],
                        int(strokes[a]), int(strokes[b]),
                        f"{pairs['haus'][idx] / EM:.8f}",
                        f"{pairs['mean'][idx] / EM:.8f}",
                        f"{pairs['rms'][idx] / EM:.8f}",
                        f"{z_a[idx]:.8f}", f"{z_b[idx]:.8f}", f"{z_pair[idx]:.8f}",
                        f"{pct[idx]:.4f}",
                        int(stratum[idx]),
                        a == b,
                    ))

    # ---- refined pairs, joined with their z-scores -----------------------------
    refined_path = out_dir / "rotation_pairs_refined_v2.csv"
    refined = np.load(cache / "refined.npy")
    key = {(int(a), int(b)): i for i, (a, b) in enumerate(zip(a_idx, b_idx))}
    with open(refined_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([
            "a", "b", "a_set", "b_set", "a_strokes", "b_strokes",
            "hausdorff_exact", "chamfer_exact", "rms_exact", "sim",
            "z_a_grid", "z_b_grid", "z_pair_grid", "percentile_z_grid",
            "stratum", "self",
        ])
        rows = []
        for i in range(len(refined)):
            a, b = int(refined["a"][i]), int(refined["b"][i])
            j = key.get((a, b))
            if j is None:
                continue
            rows.append((
                chars[a], chars[b], sets[a], sets[b], int(strokes[a]), int(strokes[b]),
                f"{float(refined['haus'][i]) / EM:.8f}",
                f"{float(refined['mean'][i]) / EM:.8f}",
                f"{float(refined['rms'][i]) / EM:.8f}",
                f"{float(refined['sim'][i]):.6f}",
                f"{z_a[j]:.8f}", f"{z_b[j]:.8f}", f"{z_pair[j]:.8f}", f"{pct[j]:.4f}",
                int(stratum[j]),
                a == b,
            ))
        rows.sort(key=lambda r: (float(r[12]), r[0], r[1]))
        writer.writerows(rows)

    stats = {
        "seed": seed,
        "null_partners": partners,
        "glyphs": n,
        "pairs": int(len(a_idx)),
        "refined_rows": len(rows),
        "z_definition": "z_pair(a,b) = max(z(a,b), z(b,a)); z(a,b) = (d - mu_a)/sigma_a",
        "scale": "grid distance-transform approximation, normalised by 109",
        "distinct_pairs": int(sum(1 for a, b in zip(a_idx, b_idx) if a != b)),
    }
    with open(out_dir / "normalisation_stats.json", "w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"null-partner sampling seed (default: {SEED})")
    parser.add_argument("--partners", type=int, default=NULL_PARTNERS,
                        help=f"null partners per glyph (default: {NULL_PARTNERS})")
    parser.add_argument("--v2", type=Path, default=None,
                        help="output directory for the v2 datasets (default: <repo>/data/v2)")
    args = parser.parse_args(argv)
    resolve(args)
    out_dir = args.v2 if args.v2 is not None else paths.REPOSITORY / "data" / "v2"
    stats = normalise(paths.CACHE, out_dir, seed=args.seed, partners=args.partners)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()