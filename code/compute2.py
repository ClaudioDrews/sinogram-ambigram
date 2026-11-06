"""Stage 2b: complementary metrics for the rotation graph.

1) Skeleton IoU (S-overlap): |A ∩ R(B)| / |A ∪ R(B)|, computed for
   every pair through BLAS matrix multiplication.
2) Symmetric Hausdorff (maximum of directed distances) via distance transforms.
3) Chamfer RMS (sensitive to outliers).

Stores pair indices and metrics in the pipeline cache.
"""
from __future__ import annotations

import json
import time
from multiprocessing import Pool

import numpy as np

from paths import CACHE
GRID = 109
EM = 109.0

_PTS = _OFF = _DT = _ROT = _FLAT = None


def _init():
    global _PTS, _OFF, _DT, _ROT, _FLAT
    _PTS = np.load(f"{CACHE}/points.npy")
    _OFF = np.load(f"{CACHE}/offsets.npy")
    _DT = np.load(f"{CACHE}/dt.npy", mmap_mode="r")
    _FLAT = np.ascontiguousarray(_DT).reshape(len(_OFF) - 1, -1)
    rot = []
    for i in range(len(_OFF) - 1):
        p = _PTS[_OFF[i]:_OFF[i + 1]]
        cx = np.clip((GRID - 1) - p[:, 0].astype(np.int32), 0, GRID - 1)
        cy = np.clip((GRID - 1) - p[:, 1].astype(np.int32), 0, GRID - 1)
        rot.append((cy * GRID + cx).astype(np.int64))
    _ROT = rot


def _chunk(args):
    a0, a1 = args
    n = len(_OFF) - 1
    out = np.empty((sum(n - a for a in range(a0, a1)), ),
                   dtype=[("a", "i4"), ("b", "i4"), ("mean", "f4"), ("rms", "f4"),
                          ("haus", "f4"), ("iou", "f4")])
    k = 0
    for a in range(a0, a1):
        idx_a = _ROT[a]
        dta = _FLAT[a]
        for b in range(a, n):
            dtb = _FLAT[b]
            idx_b = _ROT[b]
            d1 = dtb[idx_a]
            d2 = dta[idx_b]
            out[k] = (a, b, 0.5 * (d1.mean() + d2.mean()),
                      float(np.sqrt(0.5 * (np.mean(d1 * d1) + np.mean(d2 * d2)))),
                      max(float(d1.max()), float(d2.max())), 0.0)
            k += 1
    return out


def main():
    meta = json.load(open(f"{CACHE}/meta.json"))
    n = len(meta)
    dt = np.load(f"{CACHE}/dt.npy", mmap_mode="r")
    print(f"{n} glyphs", flush=True)

    # ---------- skeleton IoU for all pairs (BLAS) ----------
    t0 = time.time()
    A = (np.asarray(dt) == 0).reshape(n, GRID * GRID).astype(np.float32)
    Arot = A.reshape(n, GRID, GRID)[:, ::-1, ::-1].reshape(n, GRID * GRID).copy()
    counts = A.sum(axis=1)
    inter = A @ Arot.T                      # inter[a,b] = |A_a ∩ R(B_b)|
    union = counts[:, None] + counts[None, :] - inter
    iou = inter / np.maximum(union, 1.0)
    print(f"IoU matrix in {time.time()-t0:.1f}s", flush=True)
    del A, Arot, inter, union

    # ---------- chamfer / rms / hausdorff ----------
    blocks = []
    step = max(1, n // 24)
    for a0 in range(0, n, step):
        blocks.append((a0, min(a0 + step, n)))
    t0 = time.time()
    with Pool(2, initializer=_init) as pool:
        parts = []
        for i, r in enumerate(pool.imap_unordered(_chunk, blocks)):
            parts.append(r)
            print(f"  block {i+1}/{len(blocks)} {time.time()-t0:.1f}s", flush=True)
    res = np.concatenate(parts)
    # imap_unordered returns blocks in completion order, not index order.
    # Look up each metric by its explicit pair indices instead.
    res["iou"] = iou[res["a"], res["b"]].astype(np.float32)
    np.save(f"{CACHE}/pairs2.npz", res)
    print(f"saved: {len(res)} pairs in {time.time()-t0:.1f}s", flush=True)

    # ---------- ranking ----------
    order = np.argsort(-res["iou"], kind="stable")
    top = res[order[:15]]
    print("\ntop by skeleton IoU:")
    for r in top:
        print(f"   {meta[r['a']]['char']} <-> {meta[r['b']]['char']}  "
              f"IoU={r['iou']:.3f}  chamfer={r['mean']/EM:.4f}  haus={r['haus']/EM:.4f}")


if __name__ == "__main__":
    main()
