"""Stage 1: build point-cloud skeletons and distance transforms for the Joyo and
Jinmeiyo inventories using KanjiVG.

Cache outputs:
  points.npy   float32 (P,2) concatenated point clouds
  offsets.npy  int64 (N+1,) point-cloud offsets
  dt.npy       float32 (N,G,G) chamfer distance transforms (memmap)
  meta.json    glyph metadata (character, file, stroke types/count, point count)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kvg import load_kanji, svg_file_for  # noqa: E402

from paths import KDIR
from paths import CACHE, LISTS
GRID = 109          # grid resolution (one KanjiVG unit per cell)
SPACING = 0.45     # sampling interval along each stroke (units)
CH_A, CH_B = 3.0, 4.0   # chamfer weights (orthogonal / diagonal)


def resample_polyline(poly: np.ndarray, spacing: float) -> np.ndarray:
    """Resample a polyline at constant arc-length spacing."""
    if len(poly) < 2:
        return poly
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    if total <= 0:
        return poly[:1]
    n = max(2, int(np.ceil(total / spacing)) + 1)
    targets = np.linspace(0.0, total, n)
    xs = np.interp(targets, cum, poly[:, 0])
    ys = np.interp(targets, cum, poly[:, 1])
    return np.column_stack([xs, ys])


def rasterize_segments(poly: np.ndarray, grid: np.ndarray) -> None:
    """Mark grid cells traversed by segments (vertex by vertex)."""
    for i in range(len(poly) - 1):
        x0, y0 = poly[i]
        x1, y1 = poly[i + 1]
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        t = np.linspace(0, 1, steps + 1)
        xs = np.clip((x0 + (x1 - x0) * t).astype(int), 0, GRID - 1)
        ys = np.clip((y0 + (y1 - y0) * t).astype(int), 0, GRID - 1)
        grid[ys, xs] = True


def chamfer_dt(occ: np.ndarray) -> np.ndarray:
    """Two-pass 3–4 chamfer distance transform (Euclidean approximation)."""
    INF = 1e6
    d = np.where(occ, 0.0, INF).astype(np.float32)
    # forward pass: top to bottom
    for y in range(1, GRID):
        prev = d[y - 1]
        cand = prev + CH_A
        shifted_l = np.empty_like(cand)
        shifted_r = np.empty_like(cand)
        shifted_l[1:] = prev[:-1] + CH_B
        shifted_l[0] = INF
        shifted_r[:-1] = prev[1:] + CH_B
        shifted_r[-1] = INF
        d[y] = np.minimum(d[y], np.minimum(cand, np.minimum(shifted_l, shifted_r)))
    # backward pass: bottom to top
    for y in range(GRID - 2, -1, -1):
        nxt = d[y + 1]
        cand = nxt + CH_A
        shifted_l = np.empty_like(cand)
        shifted_r = np.empty_like(cand)
        shifted_l[1:] = nxt[:-1] + CH_B
        shifted_l[0] = INF
        shifted_r[:-1] = nxt[1:] + CH_B
        shifted_r[-1] = INF
        d[y] = np.minimum(d[y], np.minimum(cand, np.minimum(shifted_l, shifted_r)))
    return d / CH_A  # convert to pixel units


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    lists = json.load(open(str(LISTS)))
    inventory = lists["inventory"]
    joyo = set(lists["joyo"])
    jm = set(lists["jinmeiyo_types"])

    all_pts, offsets, meta = [], [0], []
    t0 = time.time()
    for i, ch in enumerate(inventory):
        f = svg_file_for(ch, KDIR)
        if f is None:
            print(f"[warn] no SVG for {ch} U+{ord(ch):04X}", flush=True)
            continue
        strokes = load_kanji(f)
        occ = np.zeros((GRID, GRID), bool)
        pts = []
        for s in strokes:
            for poly in s["polys"]:
                rp = resample_polyline(poly, SPACING)
                rasterize_segments(rp, occ)
                pts.append(rp)
        p = np.concatenate(pts, axis=0).astype(np.float32) if pts else np.zeros((0, 2), np.float32)
        all_pts.append(p)
        offsets.append(offsets[-1] + len(p))
        meta.append({
            "char": ch,
            "codepoint": f"{ord(ch):04X}",
            "file": Path(f).name,
            "n_strokes": len(strokes),
            "n_points": int(len(p)),
            "stroke_types": [s["type"] for s in strokes],
            "set": "jouyou" if ch in joyo else ("jinmeiyo" if ch in jm else "other"),
        })
        if (i + 1) % 400 == 0:
            print(f"  {i+1}/{len(inventory)}  {time.time()-t0:.1f}s", flush=True)

    pts = np.concatenate(all_pts, axis=0)
    np.save(CACHE / "points.npy", pts)
    np.save(CACHE / "offsets.npy", np.array(offsets, dtype=np.int64))
    json.dump(meta, open(CACHE / "meta.json", "w"), ensure_ascii=False)

    print(f"glyph clouds: {len(meta)}  total points: {len(pts)}", flush=True)
    print("computing distance transforms...", flush=True)
    dt_path = CACHE / "dt.npy"
    dt = np.lib.format.open_memmap(dt_path, mode="w+", dtype=np.float32,
                                   shape=(len(meta), GRID, GRID))
    t0 = time.time()
    for i, ch in enumerate([m["char"] for m in meta]):
        f = svg_file_for(ch, KDIR)
        strokes = load_kanji(f)
        occ = np.zeros((GRID, GRID), bool)
        for s in strokes:
            for poly in s["polys"]:
                rasterize_segments(resample_polyline(poly, SPACING), occ)
        dt[i] = chamfer_dt(occ)
        if (i + 1) % 500 == 0:
            print(f"  dt {i+1}/{len(meta)}  {time.time()-t0:.1f}s", flush=True)
    dt.flush()
    print("ok", flush=True)


if __name__ == "__main__":
    main()
