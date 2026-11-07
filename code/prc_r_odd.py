"""Experimental local thickness compensation for PRC C2 drawings.

This is a *geometric* operator, not a legibility estimator and not a literal
odd-component subtraction. It changes widths, never centre lines. All
measurements use the thickness-corrected prc_construct rasterizer.
"""
from __future__ import annotations

import numpy as np
import prc_construct as pc


def distance_to_ink(ink: np.ndarray) -> np.ndarray:
    """Approximate Euclidean distance in pixels with a two-pass 8-neighbour DT."""
    d = np.where(ink, 0.0, 1e6).astype(float)
    h, w = d.shape
    diagonal = np.sqrt(2.0)
    for y in range(h):
        for x in range(w):
            if x:
                d[y, x] = min(d[y, x], d[y, x - 1] + 1)
            if y:
                d[y, x] = min(d[y, x], d[y - 1, x] + 1)
                if x:
                    d[y, x] = min(d[y, x], d[y - 1, x - 1] + diagonal)
                if x + 1 < w:
                    d[y, x] = min(d[y, x], d[y - 1, x + 1] + diagonal)
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if x + 1 < w:
                d[y, x] = min(d[y, x], d[y, x + 1] + 1)
            if y + 1 < h:
                d[y, x] = min(d[y, x], d[y + 1, x] + 1)
                if x:
                    d[y, x] = min(d[y, x], d[y + 1, x - 1] + diagonal)
                if x + 1 < w:
                    d[y, x] = min(d[y, x], d[y + 1, x + 1] + diagonal)
    return d


def compensate(strokes: list[pc.Stroke], centre: tuple[float, float],
               lam: float = 0.9, radius: float = 12.4,
               cap: float = 1.9, growth_max: float = 1.28):
    """Return (strokes, metrics); choose maximum feasible intensity by bisection.

    The baseline is always retained when the operator does not improve
    symmetry or violates retention/growth constraints.
    """
    if radius <= 0 or cap < 1 or lam < 0 or growth_max < 1:
        raise ValueError("Invalid compensation parameters")
    original = pc.raster(strokes)
    if not original.any():
        return [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes], {
            "sym": 0.0, "retention": 0.0, "growth": 0.0, "ok": False}
    rotated = pc.half_turn_grid(original, centre)
    dt = distance_to_ink(rotated)

    def apply(intensity):
        result = []
        for s in strokes:
            iy = np.clip(np.floor(s.median[:, 1]).astype(int), 0, dt.shape[0] - 1)
            ix = np.clip(np.floor(s.median[:, 0]).astype(int), 0, dt.shape[1] - 1)
            dist = dt[iy, ix]
            falloff = np.clip(1.0 - dist / radius, 0.0, 1.0) ** 2
            multiplier = np.minimum(cap, 1 + intensity * falloff)
            result.append(pc.Stroke(s.median.copy(), s.half_width * multiplier))
        return result

    baseline = [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]
    baseline_metrics = pc.sector_score(baseline, centre, original)
    best, best_metrics = baseline, baseline_metrics
    low, high = 0.0, lam
    # Width growth is monotone in intensity; use a bound then evaluate
    # quantized masks with the repository's official geometry metric.
    for _ in range(16):
        mid = (low + high) / 2
        trial = apply(mid)
        metrics = pc.sector_score(trial, centre, original)
        if metrics["ok"] and metrics["growth"] <= growth_max:
            low = mid
            if metrics["sym"] > best_metrics["sym"] + 1e-12:
                best, best_metrics = trial, metrics
        else:
            high = mid
    # A final candidate at the best feasible intensity catches cases where
    # the binary raster has changed between adjacent bisection steps.
    trial = apply(low)
    metrics = pc.sector_score(trial, centre, original)
    if metrics["ok"] and metrics["growth"] <= growth_max and metrics["sym"] > best_metrics["sym"] + 1e-12:
        best, best_metrics = trial, metrics
    return best, best_metrics
