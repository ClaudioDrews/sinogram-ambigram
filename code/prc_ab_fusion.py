"""Experimental pair construction by stroke registration, not naive ink union.

Given upright A and upright B, transform B by a half-turn, align nearby
stroke spines and blend only well-matched strokes. Unmatched strokes remain
explicit. This is an *experimental geometry baseline*, not validated reading.
"""
from __future__ import annotations

import numpy as np
import prc_construct as pc


def rotate_strokes(strokes: list[pc.Stroke], centre: tuple[float, float]):
    return [pc.Stroke(pc.half_turn(s.median, centre),
                      s.half_width.copy()) for s in strokes]


def _sample(points: np.ndarray, n: int = 24):
    if len(points) < 2:
        return np.repeat(points[:1], n, axis=0)
    ds = np.linalg.norm(np.diff(points, axis=0), axis=1)
    cs = np.r_[0.0, np.cumsum(ds)]
    if cs[-1] <= 1e-12:
        return np.repeat(points[:1], n, axis=0)
    target = np.linspace(0, cs[-1], n)
    return np.column_stack([np.interp(target, cs, points[:, 0]),
                            np.interp(target, cs, points[:, 1])])


def match_strokes(a: list[pc.Stroke], rb: list[pc.Stroke],
                  threshold: float = 4.0):
    """Greedy one-to-one matches by resampled spine RMS distance."""
    candidates = []
    for i, x in enumerate(a):
        xx = _sample(x.median)
        for j, y in enumerate(rb):
            yy = _sample(y.median)
            direct = float(np.sqrt(np.mean(np.sum((xx - yy) ** 2, axis=1))))
            reverse = float(np.sqrt(np.mean(np.sum((xx - yy[::-1]) ** 2, axis=1))))
            distance = min(direct, reverse)
            if distance <= threshold:
                candidates.append((distance, i, j, reverse < direct))
    used_a, used_b, matches = set(), set(), []
    for distance, i, j, reverse in sorted(candidates):
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        matches.append((i, j, reverse, distance))
    return matches


def _blend(x: pc.Stroke, y: pc.Stroke, reverse: bool, alpha: float):
    xa, ya = _sample(x.median), _sample(y.median)
    if reverse:
        ya = ya[::-1]
    # Interpolate the sampled width profiles onto a common arc parameter.
    wx = np.interp(np.linspace(0, 1, len(xa)),
                   np.linspace(0, 1, len(x.half_width)), x.half_width)
    wy = np.interp(np.linspace(0, 1, len(ya)),
                   np.linspace(0, 1, len(y.half_width)), y.half_width)
    if reverse:
        wy = wy[::-1]
    return pc.Stroke((1 - alpha) * xa + alpha * ya,
                     (1 - alpha) * wx + alpha * wy)


def _f1(candidate: np.ndarray, reference: np.ndarray):
    common = float(np.logical_and(candidate, reference).sum())
    return 2 * common / max(float(candidate.sum() + reference.sum()), 1.0)


def score(candidate: list[pc.Stroke], a: list[pc.Stroke],
          b: list[pc.Stroke], centre: tuple[float, float]):
    """Both-orientation raster F1; never label it as a readability score."""
    ca = pc.raster(candidate)
    cr = pc.half_turn_grid(ca, centre)
    ra, rb = pc.raster(a), pc.raster(b)
    fa, fb = _f1(ca, ra), _f1(cr, rb)
    return {"f1_a": fa, "f1_b": fb, "minimum_f1": min(fa, fb),
            "joint_f1": fa * fb, "stroke_count": len(candidate)}


def construct(a: list[pc.Stroke], b: list[pc.Stroke],
              centre: tuple[float, float] = (pc.EM / 2, pc.EM / 2),
              threshold: float = 4.0,
              alphas=(0.25, 0.5, 0.75)):
    """Search shared-spine blend; retain union baseline unless F1 improves."""
    rb = rotate_strokes(b, centre)
    matches = match_strokes(a, rb, threshold)
    base = [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in a + rb]
    best, metrics = base, score(base, a, b, centre)
    used_a = {m[0] for m in matches}
    used_b = {m[1] for m in matches}
    for alpha in alphas:
        joined = [_blend(a[i], rb[j], rev, alpha) for i, j, rev, _ in matches]
        joined += [pc.Stroke(s.median.copy(), s.half_width.copy())
                   for i, s in enumerate(a) if i not in used_a]
        joined += [pc.Stroke(s.median.copy(), s.half_width.copy())
                   for j, s in enumerate(rb) if j not in used_b]
        ms = score(joined, a, b, centre)
        # Both readings must be at least as good as the baseline
        # geometrically; no wins by sacrificing one reading for the other.
        if (ms["minimum_f1"] >= metrics["minimum_f1"] - 1e-12 and
                (ms["joint_f1"] > metrics["joint_f1"] + 1e-12 or\n                 (ms["joint_f1"] >= metrics["joint_f1"] - 1e-12 and\n                  ms["stroke_count"] < metrics["stroke_count"]))):
            best, metrics = joined, ms
    return best, {"metrics": metrics, "matched_strokes": len(matches),
                  "total_a": len(a), "total_b": len(b),
                  "centre": list(centre)}
