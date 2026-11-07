"""Stage 8: optimal rotation centre for the shortlisted pairs.

Rotating a glyph about the centre of the character box is one choice among
many. Rotating about a different centre ``c`` gives

    R_c(p) = 2c - p = (109 - p) + 2(c - 54.5)

so varying the centre is exactly a translation of the half-turned glyph. The
search below therefore finds, for each shortlisted pair, the translation that
brings the half-turned partner closest to the original.

This removes the "rotation centre is fixed at the box centre" limitation
recorded in the independent review (CR3) and in
``findings/limitations.md``. It does not add degrees of freedom beyond
translation: no scaling, no shear, no stroke-level deformation.

Search grid: centres at 54.5 + {-6, -4.5, ..., +6} units, i.e. 9 x 9 = 81
offsets, with the corresponding translations of 2(c - 54.5) in {-12, ..., +12}
in steps of 3. The grid is fixed and recorded, so the result is reproducible.

**Padded distance transform.** A translation can move a point outside the
109 x 109 character box. Clipping such a point onto the border would silently
distort the distance, so this stage computes its own chamfer distance
transform on a padded canvas (the glyph centred in a 125 x 125 grid, with an
8-unit margin). Points that leave the box then land on free space and receive
a meaningful distance. The transform is the same 3-4 chamfer used in stage 1,
so the offset-zero result is directly comparable with the published
distances.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

import paths
from paths import add_common_args, resolve
from kvg import load_kanji, svg_file_for  # noqa: E402
from stage1_skeleton import resample_polyline, SPACING  # noqa: E402

EM = 109.0
PAD = 8
CANVAS = int(round(EM)) + 2 * PAD   # 125, an integer side length
GRID = 109
CH_A, CH_B = 3.0, 4.0

#: Centre offsets searched, in units. 9 values per axis, step 1.5.
CENTRE_STEP = 1.5
CENTRE_MAX = 6.0


def _chamfer_dt(occ: np.ndarray) -> np.ndarray:
    """Two-pass 3-4 chamfer distance transform on an arbitrary grid."""
    height, width = occ.shape
    INF = 1e6
    d = np.where(occ, 0.0, INF).astype(np.float32)
    for y in range(1, height):
        prev = d[y - 1]
        cand = prev + CH_A
        left = np.empty_like(cand)
        right = np.empty_like(cand)
        left[1:] = prev[:-1] + CH_B
        left[0] = INF
        right[:-1] = prev[1:] + CH_B
        right[-1] = INF
        d[y] = np.minimum(d[y], np.minimum(cand, np.minimum(left, right)))
    for y in range(height - 2, -1, -1):
        nxt = d[y + 1]
        cand = nxt + CH_A
        left = np.empty_like(cand)
        right = np.empty_like(cand)
        left[1:] = nxt[:-1] + CH_B
        left[0] = INF
        right[:-1] = nxt[1:] + CH_B
        right[-1] = INF
        d[y] = np.minimum(d[y], np.minimum(cand, np.minimum(left, right)))
    return d / CH_A


def _occupancy(strokes) -> np.ndarray:
    """Occupancy grid of a glyph, centred in the padded canvas."""
    occ = np.zeros((CANVAS, CANVAS), bool)
    for stroke in strokes:
        for poly in stroke["polys"]:
            rp = resample_polyline(poly, SPACING) + PAD
            for i in range(len(rp) - 1):
                x0, y0 = rp[i]
                x1, y1 = rp[i + 1]
                steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
                t = np.linspace(0, 1, steps + 1)
                xs = np.clip((x0 + (x1 - x0) * t).astype(int), 0, CANVAS - 1)
                ys = np.clip((y0 + (y1 - y0) * t).astype(int), 0, CANVAS - 1)
                occ[ys, xs] = True
    return occ


def _padded_indices(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Canvas indices of the half-turned points, in the padded frame."""
    p = points + PAD
    rx = CANVAS - 1 - p[:, 0].astype(np.int32)
    ry = CANVAS - 1 - p[:, 1].astype(np.int32)
    return rx.astype(np.int64), ry.astype(np.int64)


def _search_pair(dt_a: np.ndarray, dt_b: np.ndarray,
                 idx_a: np.ndarray, idx_b: np.ndarray,
                 offsets: np.ndarray) -> tuple[float, float, float]:
    """Return (best distance, best dx, best dy) over the translation grid."""
    flat_a = dt_a.reshape(-1)
    flat_b = dt_b.reshape(-1)
    best = (np.inf, 0.0, 0.0)
    for dx, dy in offsets:
        # Translating the half-turned partner by (dx, dy).
        rx = idx_a[0] + int(dx)
        ry = idx_a[1] + int(dy)
        np.clip(rx, 0, CANVAS - 1, out=rx)
        np.clip(ry, 0, CANVAS - 1, out=ry)
        d1 = flat_b[ry * CANVAS + rx]
        rx2 = idx_b[0] + int(dx)
        ry2 = idx_b[1] + int(dy)
        np.clip(rx2, 0, CANVAS - 1, out=rx2)
        np.clip(ry2, 0, CANVAS - 1, out=ry2)
        d2 = flat_a[ry2 * CANVAS + rx2]
        value = float(max(d1.max(), d2.max()))
        if value < best[0]:
            best = (value, float(dx), float(dy))
    return best


def optimal_centres(cache: Path, out_dir: Path, limit: int | None = None) -> dict:
    """Search the optimal rotation centre for the refined pairs."""
    cache = Path(cache)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cache / "meta.json", encoding="utf-8") as handle:
        meta = json.load(handle)
    chars = [m["char"] for m in meta]
    n = len(meta)

    points = np.load(cache / "points.npy")
    offsets = np.load(cache / "offsets.npy")

    # Pad the sample points into the canvas frame once.
    padded = []
    for i in range(n):
        # _padded_indices applies the PAD shift itself.
        seg = points[offsets[i]:offsets[i + 1]].astype(np.float64)
        padded.append(seg)

    refined = np.load(cache / "refined.npy")
    pairs = [(int(r["a"]), int(r["b"])) for r in refined]
    if limit is not None:
        pairs = pairs[:limit]
    needed = sorted({i for pair in pairs for i in pair})

    print(f"building padded distance transforms for {len(needed)} glyphs", flush=True)
    dt: dict[int, np.ndarray] = {}
    for count, i in enumerate(needed, 1):
        svg = svg_file_for(chars[i], paths.KDIR)
        strokes = load_kanji(svg)
        dt[i] = _chamfer_dt(_occupancy(strokes))
        if count % 400 == 0:
            print(f"  dt {count}/{len(needed)}", flush=True)

    idx: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for i in needed:
        idx[i] = _padded_indices(padded[i])

    steps = np.arange(-CENTRE_MAX, CENTRE_MAX + 1e-9, CENTRE_STEP)
    grid = np.array([(2 * dx, 2 * dy) for dx in steps for dy in steps], dtype=np.int64)

    print(f"searching {len(grid)} offsets for {len(pairs)} pairs", flush=True)
    zero = np.array([(0, 0)], dtype=np.int64)
    rows = []
    for count, (a, b) in enumerate(pairs, 1):
        best, dx, dy = _search_pair(dt[a], dt[b], idx[a], idx[b], grid)
        base, _zx, _zy = _search_pair(dt[a], dt[b], idx[a], idx[b], zero)
        rows.append({
            "a": chars[a], "b": chars[b],
            "hausdorff_grid_zero": base / EM,
            "hausdorff_grid_optimal": best / EM,
            "improvement_grid": (base - best) / EM,
            "centre_dx": dx / 2.0, "centre_dy": dy / 2.0,
            "translation_dx": dx, "translation_dy": dy,
            "self": a == b,
        })
        if count % 500 == 0:
            print(f"  {count}/{len(pairs)}", flush=True)

    rows.sort(key=lambda r: (r["hausdorff_grid_optimal"], r["a"], r["b"]))
    out_path = out_dir / "optimal_centres.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    stats = {
        "pairs": len(rows),
        "offset_grid": f"{len(steps)}x{len(steps)} centres, step {CENTRE_STEP}, "
                       f"max {CENTRE_MAX}",
        "padded_canvas": CANVAS,
        "scale": "grid distance-transform approximation, normalised by 109",
        "nonzero_offsets": sum(1 for r in rows
                               if r["translation_dx"] or r["translation_dy"]),
        "mean_improvement_grid": sum(r["improvement_grid"] for r in rows) / len(rows),
        "pairs_improved": sum(1 for r in rows if r["improvement_grid"] > 0),
    }
    with open(out_dir / "optimal_centres_stats.json", "w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--limit", type=int, default=None,
                        help="only search the first N refined pairs")
    parser.add_argument("--v2", type=Path, default=None,
                        help="output directory (default: <repo>/data/v2)")
    args = parser.parse_args(argv)
    resolve(args)
    out_dir = args.v2 if args.v2 is not None else paths.REPOSITORY / "data" / "v2"
    stats = optimal_centres(paths.CACHE, out_dir, limit=args.limit)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()