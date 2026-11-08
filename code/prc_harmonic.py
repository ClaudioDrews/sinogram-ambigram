"""Experimental C2-invariant smooth thickness field for PRC stroke medians.

Unlike a per-stroke-class multiplier, the scalar spatial field here is
provably invariant under exact 180-degree rotation about its centre.
It optimizes only the repository's binary-ink symmetry proxy, with
retention and growth limits; this is not evidence of legibility.
"""
from __future__ import annotations

import numpy as np
import prc_construct as pc

BASIS = ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2))


def log_field(points: np.ndarray, centre: tuple[float, float],
              coefficients: np.ndarray) -> np.ndarray:
    """Even cosine products: f(2c-p) == f(p), including off-grid points."""
    p = np.asarray(points, dtype=np.float64)
    c = np.asarray(centre, dtype=np.float64)
    q = (p - c) / (pc.EM / 2.0)
    out = np.zeros(len(q), dtype=np.float64)
    for a, (kx, ky) in zip(coefficients, BASIS):
        out += a * np.cos(np.pi * kx * q[:, 0]) * np.cos(np.pi * ky * q[:, 1])
    return out


def apply_field(strokes: list[pc.Stroke], centre: tuple[float, float],
                coefficients: np.ndarray, cap: float = 1.9):
    """Multiply each median half-width by a smooth bounded even field."""
    if cap < 1:
        raise ValueError("cap must be >= 1")
    if len(coefficients) != len(BASIS):
        raise ValueError("one coefficient per basis element is required")
    result = []
    for s in strokes:
        log_m = log_field(s.median, centre, coefficients)
        multiplier = np.clip(np.exp(np.clip(log_m, -1.0, 1.0)), 1.0 / cap, cap)
        result.append(pc.Stroke(s.median.copy(), s.half_width * multiplier))
    return result


def optimize(strokes: list[pc.Stroke], centre: tuple[float, float],
             levels=(-0.20, 0.20), rounds: int = 2,
             growth_max: float = 1.28):
    """Deterministic coordinate search; return best *feasible* configuration.

    Comparisons always use the original drawing as reference and the
    shared rasterizer. A strict improvement is required to replace baseline.
    """
    if rounds < 0 or growth_max < 1:
        raise ValueError("Invalid optimization bounds")
    reference = pc.raster(strokes)
    coeff = np.zeros(len(BASIS), dtype=float)
    best = [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]
    score = pc.sector_score(best, centre, reference)
    for _ in range(rounds):
        improved = False
        for k in range(len(BASIS)):
            local_coeff = coeff.copy()
            local_score = score
            local_strokes = best
            for delta in levels:
                trial_coeff = coeff.copy()
                trial_coeff[k] += delta
                trial_strokes = apply_field(strokes, centre, trial_coeff)
                trial_score = pc.sector_score(trial_strokes, centre, reference)
                if (trial_score["ok"] and
                        trial_score["growth"] <= growth_max and
                        trial_score["sym"] > local_score["sym"] + 1e-12):
                    local_coeff = trial_coeff
                    local_score = trial_score
                    local_strokes = trial_strokes
            if local_score["sym"] > score["sym"] + 1e-12:
                coeff, score, best = local_coeff, local_score, local_strokes
                improved = True
        if not improved:
            break
    return best, {"score": score, "coefficients": coeff.tolist()}
