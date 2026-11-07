"""Power simulation for the perceptual pilot's decision rule.

The protocol (``methods/HUMAN_EVAL.md`` §7) fixes the decision rule before the
pilot runs and states the probability that the rule reaches GO under a true
effect. This script reproduces those numbers so that the claim can be checked
and re-checked after any change to the design.

The model is deliberately simple and stated in full:

* every item has a latent readability on a 1-7 Likert scale;
* the ``v2-top`` items are drawn with a latent mean one point above the
  controls, which is the smallest difference the decision rule accepts;
* every rater scores every item, adding a rater effect and an item effect, so
  the total rating standard deviation is ``sd`` (1.3 in the protocol);
* ratings are clipped to 1-7 and rounded to integers;
* ``L_item`` is the median of the ratings of one item, ``L_group`` the median
  of the ``L_item`` values of one stratum.

Run:

    python code/test_pilot_power.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

SEED = 20261107
LIKERT_MIN, LIKERT_MAX = 1, 7
GAP = 1.0
DELTA_MIN = 0.33
P_MAX = 0.05


def _mann_whitney_exact_greater(x: np.ndarray, y: np.ndarray) -> float:
    """One-sided exact Mann-Whitney p-value, conditional on the observed data.

    The p-value is the probability that a group of the same size drawn at
    random from the pooled observations has a rank sum at least as large as
    the observed one. That distribution is computed exactly by dynamic
    programming over the distinct values, so tied observations are handled
    without enumerating the label assignments. Ties at the observed value
    contribute half of their mass.
    """
    from math import comb

    n1, n2 = len(x), len(y)
    total = n1 + n2
    combined = np.concatenate([x, y])

    # Mid-ranks of every distinct value.
    values, counts = np.unique(combined, return_counts=True)
    mid = np.empty(len(values), dtype=np.float64)
    start = 0
    for i, c in enumerate(counts):
        mid[i] = start + (c + 1) / 2.0
        start += c

    # dp[(chosen, rank sum)] = number of ways to pick `chosen` observations
    # with that rank sum.
    dp: dict[tuple[int, float], int] = {(0, 0.0): 1}
    for c, r in zip(counts, mid):
        nxt: dict[tuple[int, float], int] = {}
        for (k, s), ways in dp.items():
            for take in range(min(int(c), n1 - k) + 1):
                key = (k + take, s + take * r)
                nxt[key] = nxt.get(key, 0) + ways * comb(int(c), take)
        dp = nxt

    ranks = np.empty(total, dtype=np.float64)
    ranks[:n1] = _mid_ranks(x, combined)
    observed_sum = float(ranks[:n1].sum())

    total_ways = sum(ways for (k, _s), ways in dp.items() if k == n1)
    extreme = 0
    for (k, s), ways in dp.items():
        if k != n1:
            continue
        if s >= observed_sum:
            extreme += ways
    p = extreme / total_ways
    return float(min(1.0, max(0.0, p)))


def _mid_ranks(sample: np.ndarray, pooled: np.ndarray) -> np.ndarray:
    """Average rank of each element of ``sample`` within ``pooled``."""
    order = np.argsort(pooled, kind="stable")
    sorted_values = pooled[order]
    ranks = np.empty(len(pooled), dtype=np.float64)
    i = 0
    while i < len(pooled):
        j = i + 1
        while j < len(pooled) and sorted_values[j] == sorted_values[i]:
            j += 1
        ranks[order[i:j]] = (i + 1 + j) / 2.0
        i = j
    return ranks[:len(sample)]


def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Cliff's delta: P(x > y) - P(x < y), ties counting zero."""
    diff = np.sign(x[:, None] - y[None, :])
    return float(diff.sum() / (len(x) * len(y)))


def simulate(n_raters: int, n_v2: int, n_control: int, sd: float,
             effect: float, n_sims: int, seed: int) -> dict:
    """Run the simulation and report how often each gate fires."""
    rng = np.random.default_rng(seed)
    base_v2, base_ctl = 4.0, 4.0 - effect
    gates = {"median_gap": 0, "mann_whitney": 0, "cliffs_delta": 0,
             "absolute_median": 0, "go": 0, "go_median_rule": 0}
    for _ in range(n_sims):
        n_items = n_v2 + n_control
        latent = np.concatenate([np.full(n_v2, base_v2), np.full(n_control, base_ctl)])
        item_effect = rng.normal(0.0, sd / np.sqrt(2), size=n_items)
        ratings = np.empty((n_raters, n_items))
        for r in range(n_raters):
            rater_effect = rng.normal(0.0, sd / np.sqrt(2))
            raw = latent + item_effect + rater_effect
            ratings[r] = np.clip(np.round(raw), LIKERT_MIN, LIKERT_MAX)
        l_item = np.median(ratings, axis=0)
        x = l_item[:n_v2]
        y = l_item[n_v2:]
        median_v2 = float(np.median(x))
        median_ctl = float(np.median(y))
        gap = median_v2 - median_ctl
        p = _mann_whitney_exact_greater(x, y)
        delta = _cliffs_delta(x, y)

        if gap >= GAP:
            gates["median_gap"] += 1
        if p < P_MAX:
            gates["mann_whitney"] += 1
        if delta >= DELTA_MIN:
            gates["cliffs_delta"] += 1
        if median_v2 >= 4.0:
            gates["absolute_median"] += 1
        if p < P_MAX and delta >= DELTA_MIN and gap >= GAP:
            gates["go"] += 1
        if median_v2 >= 4.0 and gap >= GAP:
            gates["go_median_rule"] += 1
    return {k: v / n_sims for k, v in gates.items()}


DESIGNS = (
    # label, raters, v2 items, control items
    ("original 30-item design (9 / 6)", 8, 9, 6),
    ("40-item design (12 / 8)", 8, 12, 8),
    ("48-item design (14 / 14)", 8, 14, 14),
    ("48-item design, 12 raters", 12, 14, 14),
    ("48-item design (16 / 12)", 8, 16, 12),
)

EFFECTS = (0.5, 1.0, 1.5, 2.0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sims", type=int, default=2000)
    parser.add_argument("--sd", type=float, default=1.3)
    parser.add_argument("--effect", type=float, default=1.0,
                        help="true difference between the strata, in Likert points")
    args = parser.parse_args(argv)

    print(f"simulation: {args.sims} runs, sd {args.sd}, true effect "
          f"{args.effect} Likert point\n")
    header = f"{'design':<34} {'gap>=1':>7} {'MW p<.05':>9} {'d>=.33':>7} {'GO(3)':>7} {'GO(median)':>11}"
    print(header)
    print("-" * len(header))
    for label, raters, n_v2, n_ctl in DESIGNS:
        r = simulate(raters, n_v2, n_ctl, args.sd, args.effect, args.sims, SEED)
        print(f"{label:<34} {r['median_gap']:>7.2f} {r['mann_whitney']:>9.2f} "
              f"{r['cliffs_delta']:>7.2f} {r['go']:>7.2f} {r['go_median_rule']:>11.2f}")

    print("\nGO probability of the adopted rule against the true effect "
          "(48-item design, 8 raters):")
    print(f"{'true effect':>12} {'GO(3)':>8}")
    for effect in EFFECTS:
        r = simulate(8, 14, 14, args.sd, effect, args.sims, SEED)
        print(f"{effect:>12.1f} {r['go']:>8.2f}")


if __name__ == "__main__":
    main()