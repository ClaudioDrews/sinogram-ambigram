"""Stage 3 (v2): refine candidates using dense stroke point clouds.

The one-unit grid distance transform estimates a nearest-skeleton distance d0.
Exact nearest-neighbour search uses a two-unit spatial hash and a search radius
of approximately 1.2*d0+2, allowing for chamfer-grid underestimation.

Metrics:
  C(a,b) = 1/2 [ mean_{p in a} min_{q in Rb} |p-q| + mean_{q in Rb} min_{p in a} |p-q| ]
  H(a,b) = symmetric maximum of directed distances
  S(a,b) = Gaussian similarity (sigma = 2 units)
"""
from __future__ import annotations

import argparse

import json
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

import paths
from paths import add_common_args, resolve
GRID = 109
EM = 109.0
CELL = 2.0          # spatial hash cell size (units)
SIGMA = 2.0         # Gaussian kernel width

_PTS = _OFF = _DT = _HASH = _ROTC = None


def _init():
    global _PTS, _OFF, _DT, _HASH, _ROTC
    _PTS = np.load(f"{paths.CACHE}/points.npy")
    _OFF = np.load(f"{paths.CACHE}/offsets.npy")
    _DT = np.load(f"{paths.CACHE}/dt.npy", mmap_mode="r")
    n = len(_OFF) - 1
    _HASH = []
    _ROTC = []
    for i in range(n):
        p = _PTS[_OFF[i]:_OFF[i + 1]].astype(np.float64)
        h = defaultdict(list)
        for j, (x, y) in enumerate(p):
            h[(int(y // CELL), int(x // CELL))].append(j)
        _HASH.append(h)
        _ROTC.append(np.column_stack([EM - p[:, 0], EM - p[:, 1]]))


def _min_dist_to(q, pts, h, dtrow):
    """Exact Euclidean distance from q to pts, guided by the distance transform."""
    cx, cy = int(q[0]), int(q[1])
    d0 = dtrow[min(max(cy, 0), GRID - 1), min(max(cx, 0), GRID - 1)]
    r = int(d0 * 1.25) + 3
    best = np.inf
    y0, y1 = cy - r, cy + r
    x0, x1 = cx - r, cx + r
    gy0, gx0 = int(y0 // CELL), int(x0 // CELL)
    gy1, gx1 = int(y1 // CELL), int(x1 // CELL)
    for gy in range(gy0, gy1 + 1):
        for gx in range(gx0, gx1 + 1):
            idx = h.get((gy, gx))
            if not idx:
                continue
            block = pts[idx]
            d = np.sqrt(((block - q) ** 2).sum(1)).min()
            if d < best:
                best = d
    if not np.isfinite(best):
        # fallback: exhaustive scan (the approximate DT may underestimate)
        for idx in h.values():
            d = np.sqrt(((pts[idx] - q) ** 2).sum(1)).min()
            if d < best:
                best = d
    return best


def _directed(X, Y, hY, dtY):
    """Minimum distance from each X point to Y (unrotated)."""
    out = np.empty(len(X))
    for i in range(len(X)):
        out[i] = _min_dist_to(X[i], Y, hY, dtY)
    return out


def _pair_metrics(a, b):
    Pa = _PTS[_OFF[a]:_OFF[a + 1]].astype(np.float64)
    Pb = _PTS[_OFF[b]:_OFF[b + 1]].astype(np.float64)
    Ra = np.column_stack([EM - Pa[:, 0], EM - Pa[:, 1]])
    Rb = np.column_stack([EM - Pb[:, 0], EM - Pb[:, 1]])
    dtA = np.asarray(_DT[a])
    dtB = np.asarray(_DT[b])
    # d(p in a, R(b)) = d(R(p), b)  -> query the distance transform for b
    d1 = _directed(Ra, Pb, _HASH[b], dtB)
    d2 = _directed(Rb, Pa, _HASH[a], dtA)
    mean = 0.5 * (d1.mean() + d2.mean())
    rms = float(np.sqrt(0.5 * ((d1 ** 2).mean() + (d2 ** 2).mean())))
    haus = float(max(d1.max(), d2.max()))
    sim = 0.5 * (np.exp(-(d1 ** 2) / (2 * SIGMA ** 2)).mean() +
                 np.exp(-(d2 ** 2) / (2 * SIGMA ** 2)).mean())
    return mean, rms, haus, sim


def _work(chunk):
    res = []
    for a, b in chunk:
        m, r, h, s = _pair_metrics(int(a), int(b))
        res.append((a, b, m, r, h, s))
    return np.array(res, dtype=[("a", "i4"), ("b", "i4"), ("mean", "f4"), ("rms", "f4"),
                                ("haus", "f4"), ("sim", "f4")])


def main(argv=None):
    parser = argparse.ArgumentParser(description='Stage 4: exact Euclidean refinement of shortlisted pairs.')
    add_common_args(parser)
    parser.add_argument("--top-k", type=int, default=60000,
                        help="number of grid-ranked candidates to refine (default: 60000)")
    args = parser.parse_args(argv)
    resolve(args)
    with open(f"{paths.CACHE}/meta.json", encoding="utf-8") as handle:
        meta = json.load(handle)
    res = np.load(f"{paths.CACHE}/pairs3.npy")
    n = len(meta)
    chars = [m["char"] for m in meta]

    # candidates: top-K by grid Hausdorff plus all self-pairs
    K = int(args.top_k)
    order = np.argsort(res["haus"], kind="stable")
    cand = order[:K]
    self_idx = np.nonzero(res["a"] == res["b"])[0]
    sel = np.union1d(cand, self_idx)
    pairs = np.stack([res["a"][sel], res["b"][sel]], axis=1)
    print(f"refined candidates: {len(pairs)} (top-{K} by grid H + {len(self_idx)} self-pairs)",
          flush=True)

    chunks = [pairs[i:i + 200] for i in range(0, len(pairs), 200)]
    t0 = time.time()
    out = []
    with Pool(2, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(_work, chunks)):
            out.append(r)
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{len(chunks)} blocks  {time.time()-t0:.1f}s", flush=True)
    ref = np.concatenate(out)
    np.save(f"{paths.CACHE}/refined.npy", ref)
    print(f"refined: {len(ref)} pairs in {time.time()-t0:.1f}s", flush=True)

    ref = ref[np.argsort(ref["haus"])]
    print("\n== top 30 pairs by exact Hausdorff ==")
    for r in ref[:30]:
        print(f"   {chars[r['a']]} <-> {chars[r['b']]}  H={r['haus']/EM:.4f} "
              f"C={r['mean']/EM:.4f} sim={r['sim']:.3f}")
    print("\n== self-pairs (C2 class), top 25 ==")
    selfr = ref[ref["a"] == ref["b"]][:25]
    for r in selfr:
        print(f"   {chars[r['a']]}  H={r['haus']/EM:.4f}  C={r['mean']/EM:.4f}")


if __name__ == "__main__":
    import sys
    main()