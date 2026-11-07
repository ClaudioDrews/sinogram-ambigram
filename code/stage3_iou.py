"""Stage 2c: dilated IoU (approximately two-unit tolerance) and combined scores.

Single-pixel skeleton IoU is brittle: one-cell misalignment can eliminate
intersection. Dilating skeletons by radius r gives a tolerant overlap measure.
"""
from __future__ import annotations

import argparse

import json
import time

import numpy as np

import paths
from paths import add_common_args, resolve
GRID = 109
EM = 109.0


def dilated_iou(dt, r):
    n = dt.shape[0]
    A = (dt <= r).reshape(n, GRID * GRID).astype(np.float32)
    Arot = A.reshape(n, GRID, GRID)[:, ::-1, ::-1].reshape(n, GRID * GRID).copy()
    cnt = A.sum(axis=1)
    inter = A @ Arot.T
    union = cnt[:, None] + cnt[None, :] - inter
    return inter / np.maximum(union, 1.0)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Stage 3: dilated IoU and combined pair metrics.')
    add_common_args(parser)
    args = parser.parse_args(argv)
    resolve(args)
    with open(f"{paths.CACHE}/meta.json", encoding="utf-8") as handle:
        meta = json.load(handle)
    n = len(meta)
    try:
        res = np.load(f"{paths.CACHE}/pairs2.npz")
    except Exception:
        res = np.load(f"{paths.CACHE}/pairs2.npz.npy")   # np.save appended .npy
    res = np.asarray(res)
    print(f"{len(res)} pairs loaded", flush=True)


    dt = np.load(f"{paths.CACHE}/dt.npy", mmap_mode="r")
    ious = {}
    for r in (2, 3, 4):
        t0 = time.time()
        iou = dilated_iou(np.asarray(dt), r)
        ious[r] = iou
        print(f"  dilated IoU r={r} in {time.time()-t0:.1f}s", flush=True)
    new_dtype = res.dtype.descr + [("iou2", "f4"), ("iou3", "f4"), ("iou4", "f4")]
    out = np.empty(len(res), dtype=new_dtype)
    for name in res.dtype.names:
        out[name] = res[name]
    for r in (2, 3, 4):
        out[f"iou{r}"] = ious[r][res["a"], res["b"]].astype(np.float32)
    np.save(f"{paths.CACHE}/pairs3.npy", out)
    res = out
    del ious

    # ---------------- diagnostics ----------------
    chars = [m["char"] for m in meta]
    idx = {c: i for i, c in enumerate(chars)}
    print("\n-- self-pairs (C2 class): lowest Hausdorff D(a,a) --")
    sel = res[res["a"] == res["b"]]
    sel = sel[np.argsort(sel["haus"])][:15]
    for r in sel:
        print(f"   {chars[r['a']]}  haus={r['haus']/EM:.4f}  mean={r['mean']/EM:.4f}  "
              f"IoU3={r['iou3']:.3f}")
    print("\n-- self-pairs: worst (asymmetric) --")
    sel = res[res["a"] == res["b"]]
    sel = sel[np.argsort(-sel["haus"])][:8]
    for r in sel:
        print(f"   {chars[r['a']]}  haus={r['haus']/EM:.4f}  mean={r['mean']/EM:.4f}")
    print("\n-- distinct pairs: top by dilated IoU r=3 --")
    d = res[res["a"] != res["b"]]
    d = d[np.argsort(-d["iou3"])][:20]
    for r in d:
        print(f"   {chars[r['a']]} <-> {chars[r['b']]}  IoU3={r['iou3']:.3f} "
              f"haus={r['haus']/EM:.4f} mean={r['mean']/EM:.4f}")
    print("\n-- reference pair from the original proposal: 甲 <-> 由 --")
    for (x, y) in [("甲", "由"), ("由", "甲")]:
        m = (res["a"] == idx[x]) & (res["b"] == idx[y])
        if m.any():
            r = res[m][0]
            print(f"   {x}<->{y} haus={r['haus']/EM:.4f} mean={r['mean']/EM:.4f} "
                  f"IoU2={r['iou2']:.3f} IoU3={r['iou3']:.3f} IoU4={r['iou4']:.3f}")


if __name__ == "__main__":
    main()