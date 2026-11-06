"""Stage 4: produce the final catalogue (CSV, graph JSON and statistics)."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict

import numpy as np

from paths import CACHE, CAT as OUT
EM = 109.0


def main():
    meta = json.load(open(f"{CACHE}/meta.json"))
    chars = [m["char"] for m in meta]
    sets = [m["set"] for m in meta]
    strokes = [m["n_strokes"] for m in meta]
    n = len(meta)

    res = np.load(f"{CACHE}/pairs3.npy")
    ref = np.load(f"{CACHE}/refined.npy")
    # merge grid IoU metrics with exact metrics
    key = {(int(a), int(b)): i for i, (a, b) in enumerate(zip(res["a"], res["b"]))}
    iou3 = np.zeros(len(ref), np.float32)
    iou2 = np.zeros(len(ref), np.float32)
    for i, (a, b) in enumerate(zip(ref["a"], ref["b"])):
        j = key.get((int(a), int(b)))
        if j is not None:
            iou3[i] = res["iou3"][j]
            iou2[i] = res["iou2"][j]

    rows = []
    for i in range(len(ref)):
        a, b = int(ref["a"][i]), int(ref["b"][i])
        rows.append({
            "a": chars[a], "b": chars[b],
            "a_set": sets[a], "b_set": sets[b],
            "a_strokes": strokes[a], "b_strokes": strokes[b],
            "hausdorff": float(ref["haus"][i]) / EM,
            "chamfer": float(ref["mean"][i]) / EM,
            "rms": float(ref["rms"][i]) / EM,
            "sim": float(ref["sim"][i]),
            "iou3": float(iou3[i]), "iou2": float(iou2[i]),
            "self": a == b,
        })
    rows.sort(key=lambda r: r["hausdorff"])

    # ---------------- complete CSV ----------------
    import os
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/rotation_pairs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank"] + list(rows[0].keys()))
        w.writeheader()
        for i, r in enumerate(rows):
            r = dict(r)
            r["rank"] = i + 1
            w.writerow(r)

    # ---------------- C2 class (rotation fixed points) ----------------
    c2 = [r for r in rows if r["self"]]
    with open(f"{OUT}/c2_class.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in c2:
            w.writerow(r)

    # ---------------- graph: connected components by threshold ----------------
    thresholds = [0.07, 0.075, 0.08, 0.085, 0.09, 0.10, 0.12, 0.15]
    graph_stats = []
    for t in thresholds:
        edges = [(r["a"], r["b"]) for r in rows if r["hausdorff"] <= t and not r["self"]]
        adj = defaultdict(set)
        nodes = set()
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
            nodes.add(a)
            nodes.add(b)
        # connected components
        seen, comps = set(), []
        for v in nodes:
            if v in seen:
                continue
            stack, comp = [v], []
            seen.add(v)
            while stack:
                x = stack.pop()
                comp.append(x)
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            comps.append(comp)
        comps.sort(key=len, reverse=True)
        degs = [len(adj[v]) for v in nodes]
        graph_stats.append({
            "threshold": t,
            "edges": len(edges),
            "nodes": len(nodes),
            "components": len(comps),
            "largest_component": len(comps[0]) if comps else 0,
            "max_degree": max(degs) if degs else 0,
            "mean_degree": float(np.mean(degs)) if degs else 0,
            "top_components": ["".join(sorted(c, key=lambda ch: ch)) for c in comps[:6]],
        })

    # ---------------- distribution (all 3.8M pairs, grid metric) ----
    allres = np.load(f"{CACHE}/pairs3.npy")
    h_all = allres["haus"] / EM
    hist_all, edges_all = np.histogram(h_all, bins=48, range=(0, 0.30))
    # ---------------- validation: grid vs exact ----------------
    key2 = {}
    for i, (a, b) in enumerate(zip(allres["a"], allres["b"])):
        key2[(int(a), int(b))] = i
    pairs_cmp = 0
    idxmap = {c: i for i, c in enumerate(chars)}
    g_h, e_h = [], []
    for r in rows:
        j = key2.get((idxmap[r["a"]], idxmap[r["b"]]))
        if j is None:
            continue
        g_h.append(allres["haus"][j] / EM)
        e_h.append(r["hausdorff"])
        pairs_cmp += 1
    g_h = np.array(g_h); e_h = np.array(e_h)
    valid = {
        "n": int(pairs_cmp),
        "corr": float(np.corrcoef(g_h, e_h)[0, 1]),
        "mae": float(np.abs(g_h - e_h).mean()),
        "bias": float((g_h - e_h).mean()),
        "median_abs": float(np.median(np.abs(g_h - e_h))),
        "p95_abs": float(np.percentile(np.abs(g_h - e_h), 95)),
    }
    h = np.array([r["hausdorff"] for r in rows])
    hist, edges_h = np.histogram(h, bins=40, range=(0, 0.12))
    stats = {
        "inventory_total": n,
        "inventory_jouyou": sum(1 for s in sets if s == "jouyou"),
        "inventory_jinmeiyo": sum(1 for s in sets if s == "jinmeiyo"),
        "pairs_total": len(rows),
        "c2_count": len(c2),
        "c2_strict": sum(1 for r in c2 if r["hausdorff"] <= 0.08),
        "distinct_strict": sum(1 for r in rows if r["hausdorff"] <= 0.08 and not r["self"]),
        "c2_strict_08": sum(1 for r in c2 if r["hausdorff"] <= 0.08),
        "hist": {"counts": hist.tolist(), "edges": edges_h.tolist()},
        "hist_all": {"counts": hist_all.tolist(), "edges": edges_all.tolist()},
        "validation": valid,
        "n_pairs_all": int(len(allres)),
        "graph_stats": graph_stats,
        "top_pairs": [r for r in rows if not r["self"]][:400],
        "c2_pairs": c2[:200],
        "pairs_by_set": dict(Counter(
            f'{r["a_set"]}|{r["b_set"]}' for r in rows if r["hausdorff"] <= 0.08)),
    }
    json.dump(stats, open(f"{OUT}/stats.json", "w"), ensure_ascii=False)

    print(f"catalogue: {len(rows)} refined pairs")
    print(f"C2 class (self-pairs): {len(c2)}  (strict H<=0.08: {stats['c2_strict']})")
    for g in graph_stats:
        print(f"  H<={g['threshold']:.3f}: edges={g['edges']:5d} nodes={g['nodes']:4d} "
              f"components={g['components']:4d} largest={g['largest_component']:4d} "
              f"max_degree={g['max_degree']}")
    print("\ntop 30 distinct pairs:")
    for r in [r for r in rows if not r["self"]][:30]:
        print(f"   {r['a']} <-> {r['b']}  H={r['hausdorff']:.4f} C={r['chamfer']:.4f} "
              f"sim={r['sim']:.3f} iou3={r['iou3']:.3f}")
    print("\nC2 class (top 30):")
    for r in c2[:30]:
        print(f"   {r['a']}  H={r['hausdorff']:.4f}  ({r['a_set']})")


if __name__ == "__main__":
    main()
