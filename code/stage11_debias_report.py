"""Stage 11: build findings/debias-report.md from the v1 and v2 datasets.

The report is generated rather than written by hand, so that every number in
it can be regenerated from the data. The narrative is fixed in this file; the
measurements are computed.

Sections:

1. what changed
2. density bias, before and after
3. hub concentration, before and after
4. how much the ranking moved
5. the anchor set and the decision rule
6. the optimal rotation centre
7. the reliability threshold, in z terms
8. what this does not establish
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from pathlib import Path
import re
import sys

import numpy as np

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import paths  # noqa: E402
from paths import add_common_args, resolve  # noqa: E402

EM = 109.0
TOP_N = 100
TOP_HUB = 10


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = average
        i = j + 1
    return out


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = _ranks(list(x)), _ranks(list(y))
    n = len(rx)
    if n < 2:
        return 0.0
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def _load_v1(repo: Path) -> list[dict]:
    with open(repo / "data" / "rotation_pairs.csv", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_v2(repo: Path) -> list[dict]:
    with open(repo / "data" / "v2" / "rotation_pairs_refined_v2.csv",
              encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_centres(repo: Path) -> dict[tuple[str, str], dict]:
    path = repo / "data" / "v2" / "optimal_centres.csv"
    out: dict[tuple[str, str], dict] = {}
    if not path.is_file():
        return out
    with open(path, encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out[(row["a"], row["b"])] = row
    return out


def _hubs(pairs: list[tuple[str, str]]) -> dict[str, int]:
    degree: dict[str, set[str]] = {}
    for a, b in pairs:
        degree.setdefault(a, set()).add(b)
        degree.setdefault(b, set()).add(a)
    return {c: len(s) for c, s in degree.items()}


def _anchor_rows(repo: Path) -> dict[str, list[str]]:
    """Parse findings/anchors.txt into the two anchor sets."""
    text = (repo / "findings" / "anchors.txt").read_text(encoding="utf-8")
    decision: list[str] = []
    diagnostic: list[str] = []
    section = None
    # A numbered row of the anchor tables looks like "  1  吉 ↔ 阜   0.06823 ...".
    pattern = re.compile(r"^\s*\d+\s+(\S+)\s*↔\s*(\S+)")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("A. DECISION ANCHORS"):
            section = "A"
            continue
        if stripped.startswith("B. DIAGNOSTIC SET"):
            section = "B"
            continue
        if stripped.startswith("C. DECISION RULE"):
            section = None
            continue
        if not section:
            continue
        match = pattern.match(stripped)
        if match:
            target = decision if section == "A" else diagnostic
            target.append(f"{match.group(1)} ↔ {match.group(2)}")
    return {"decision": decision, "diagnostic": diagnostic}


def build_report(repo: Path, out_path: Path) -> dict:
    v1 = _load_v1(repo)
    v2 = _load_v2(repo)
    centres = _load_centres(repo)
    anchors = _anchor_rows(repo)["decision"]
    diagnostics = _anchor_rows(repo)["diagnostic"]

    strokes: dict[str, int] = {}
    for row in v1:
        strokes[row["a"]] = int(row["a_strokes"])
        strokes[row["b"]] = int(row["b_strokes"])

    # ---- 2. density bias ------------------------------------------------------
    v1_self = [r for r in v1 if r["a"] == r["b"]]
    v2_self = [r for r in v2 if r["a"] == r["b"]]
    rho_v1 = spearman([float(r["hausdorff"]) for r in v1_self],
                      [float(r["a_strokes"]) for r in v1_self])
    rho_v2 = spearman([float(r["z_pair_grid"]) for r in v2_self],
                      [float(r["a_strokes"]) for r in v2_self])
    rho_v2_raw = spearman([float(r["hausdorff_exact"]) for r in v2_self],
                          [float(r["a_strokes"]) for r in v2_self])

    # ---- 3. hub concentration -------------------------------------------------
    v1_dist = sorted(((r["a"], r["b"]) for r in v1 if r["a"] != r["b"]),
                      key=lambda p: float(next(
                          r["hausdorff"] for r in v1
                          if {r["a"], r["b"]} == set(p))))
    v1_top = v1_dist[:TOP_N]
    v2_top = [(r["a"], r["b"]) for r in v2 if r["a"] != r["b"]][:TOP_N]

    hub_v1 = _hubs(v1_top)
    hub_v2 = _hubs(v2_top)
    top_v1 = sorted(hub_v1.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_HUB]
    top_v2 = sorted(hub_v2.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_HUB]
    share_v1 = sum(c for _, c in top_v1) / max(sum(hub_v1.values()), 1)
    share_v2 = sum(c for _, c in top_v2) / max(sum(hub_v2.values()), 1)

    # ---- 4. rank movement -----------------------------------------------------
    v1_keys = [frozenset(p) for p in v1_top]
    v2_keys = [frozenset(p) for p in v2_top]
    overlap = len(set(v1_keys) & set(v2_keys))
    entered = [tuple(sorted(p)) for p in v2_keys if p not in set(v1_keys)]
    left = [tuple(sorted(p)) for p in v1_keys if p not in set(v2_keys)]

    # ---- 5. anchors -----------------------------------------------------------
    v2_index = {(r["a"], r["b"]): r for r in v2}
    v1_index = {(r["a"], r["b"]): r for r in v1}

    def anchor_row(label: str) -> dict | None:
        # The anchor file writes the pair as "A ↔ B", with spaces around the
        # separator; the character names carry no spaces of their own.
        a, b = (part.strip() for part in label.split("↔"))
        row = v2_index.get((a, b)) or v2_index.get((b, a))
        if row is None:
            return None
        pct = float(row["percentile_z_grid"])
        return {
            "label": label, "pct": pct,
            "in_top5": pct >= 95.0,
            "z": float(row["z_pair_grid"]),
            "v1_h": float(v1_index[(a, b)]["hausdorff"]),
        }

    anchor_data = [r for r in (anchor_row(a) for a in anchors) if r]
    diag_data = [r for r in (anchor_row(a) for a in diagnostics) if r]
    passed = sum(1 for r in anchor_data if r["in_top5"])
    outside = [r for r in anchor_data if not r["in_top5"]]

    # ---- 6. optimal centre ----------------------------------------------------
    moved = [r for r in centres.values()
             if float(r["translation_dx"]) or float(r["translation_dy"])]
    centre_examples = []
    for label in anchors + diagnostics:
        a, b = (part.strip() for part in label.split("↔"))
        row = centres.get((a, b))
        if row:
            centre_examples.append({
                "label": label,
                "before": float(v1_index[(a, b)]["hausdorff"]),
                "zero": float(row["hausdorff_grid_zero"]),
                "after": float(row["hausdorff_grid_optimal"]),
                "improvement": float(row["improvement_grid"]),
                "dx": float(row["centre_dx"]), "dy": float(row["centre_dy"]),
            })

    # ---- 7. reliability threshold --------------------------------------------
    thresholds = []
    for t in (95.0, 97.5, 99.0):
        count = sum(1 for r in v2 if float(r["percentile_z_grid"]) >= t)
        thresholds.append((t, count))

    # ---- render ---------------------------------------------------------------
    lines: list[str] = []
    a = lines.append
    a("# De-biasing report: before and after")
    a("")
    a("> Generated by `code/stage11_debias_report.py` from `data/rotation_pairs.csv`")
    a("> (v1) and `data/v2/` (v2). Every number below is reproducible.")
    a("")
    a("The v1 ranking compares raw distances between glyphs. The v2 ranking")
    a("compares each pair against the null distribution of its own characters,")
    a("and searches for the rotation centre that fits the pair best. This")
    a("report measures what that changed, and applies the decision rule frozen")
    a("in `findings/anchors.txt`.")
    a("")
    a("## 1. What changed")
    a("")
    a("| | v1 | v2 |")
    a("|---|---|---|")
    a("| Ranking quantity | raw exact Hausdorff | per-glyph z-score, within complexity stratum |")
    a("| Rotation centre | fixed at the box centre | searched on a 9 × 9 grid |")
    a("| Null model | none | 30 random partners per glyph, seed 20261107 |")
    a("| Stratum | none | rounded mean stroke count |")
    a("")
    a("## 2. Density bias")
    a("")
    a("Spearman correlation between the ranking quantity and stroke count, on")
    a(f"the {len(v1_self)} self-rotation pairs:")
    a("")
    a("| Quantity correlated with stroke count | ρ |")
    a("|---|---|")
    a(f"| v1 raw Hausdorff | **{rho_v1:+.3f}** |")
    a(f"| v2 raw Hausdorff (same pairs, for reference) | {rho_v2_raw:+.3f} |")
    a(f"| v2 z-score | **{rho_v2:+.3f}** |")
    a("")
    if abs(rho_v2) < abs(rho_v1):
        a(f"The z-score reduces the correlation with stroke count from "
          f"{rho_v1:+.3f} to {rho_v2:+.3f}. The residual correlation is the part "
          "of the density effect that the per-glyph null does not remove.")
    else:
        a(f"The z-score does **not** reduce the correlation with stroke count "
          f"({rho_v1:+.3f} to {rho_v2:+.3f}). This is a negative result and is "
          "reported as such.")
    a("")
    a("## 3. Hub concentration")
    a("")
    a(f"Degree in the graph of the top {TOP_N} distinct pairs, under each ranking:")
    a("")
    a("| Rank | v1 | degree | v2 | degree |")
    a("|---|---|---|---|---|")
    for i in range(TOP_HUB):
        c1, d1 = top_v1[i] if i < len(top_v1) else ("—", 0)
        c2, d2 = top_v2[i] if i < len(top_v2) else ("—", 0)
        a(f"| {i + 1} | {c1} | {d1} | {c2} | {d2} |")
    a("")
    a(f"Share of all edges held by the {TOP_HUB} most connected characters: "
      f"v1 {share_v1 * 100:.1f}%, v2 {share_v2 * 100:.1f}%.")
    a("")
    a("## 4. How much the ranking moved")
    a("")
    a(f"Between the two top-{TOP_N} lists of distinct pairs, **{overlap} of "
      f"{TOP_N}** are common ({overlap / TOP_N * 100:.0f}%).")
    a("")
    if entered:
        a("Pairs that entered the v2 top list:")
        a("")
        for pair in entered[:20]:
            a(f"- {pair[0]} ↔ {pair[1]}")
        a("")
    if left:
        a("Pairs that left the v1 top list:")
        a("")
        for pair in left[:20]:
            a(f"- {pair[0]} ↔ {pair[1]}")
        a("")
    a("## 5. The anchor set and the decision rule")
    a("")
    a("The anchor set and the rule were frozen in `findings/anchors.txt` before")
    a("any v2 result existed. The rule: at most 3 of the 7 decision anchors may")
    a("fall outside the top 5% of their complexity stratum.")
    a("")
    a("| Anchor | v1 H (exact) | v2 z | v2 percentile in stratum | Top 5%? |")
    a("|---|---|---|---|---|")
    for row in anchor_data:
        a(f"| {row['label']} | {row['v1_h']:.5f} | {row['z']:+.3f} | "
          f"{row['pct']:.1f} | {'yes' if row['in_top5'] else 'NO'} |")
    a("")
    a(f"**{passed} of {len(anchor_data)} anchors are in the top 5% of their "
      f"stratum.** The threshold is 4 of 7.")
    a("")
    if outside:
        a("Anchors outside the top 5%, which under the frozen rule require a")
        a("written explanation approved by the maintainer (G11, no")
        a("self-certification):")
        a("")
        for row in outside:
            a(f"- {row['label']} — percentile {row['pct']:.1f}")
        a("")
    else:
        a("No anchor falls outside the top 5%, so no explanation is required by")
        a("the frozen rule.")
        a("")
    a("### Diagnostic anchors")
    a("")
    a("These two are reported but excluded from the binary rule, because the")
    a("rule was pre-registered over 7 anchors and adding them would change its")
    a("denominator. They are the cases the independent review showed the fixed")
    a("rotation centre penalises.")
    a("")
    a("| Anchor | v1 H (exact) | v2 percentile in stratum | Top 5%? |")
    a("|---|---|---|---|")
    for row in diag_data:
        a(f"| {row['label']} | {row['v1_h']:.5f} | {row['pct']:.1f} | "
          f"{'yes' if row['in_top5'] else 'NO'} |")
    a("")
    a("## 6. The optimal rotation centre")
    a("")
    if centres:
        a(f"{len(moved)} of {len(centres)} refined pairs ({len(moved) / len(centres) * 100:.1f}%) "
          "have a best centre other than the box centre.")
        improved = sum(1 for r in centres.values()
                       if float(r["improvement_grid"]) > 0)
        a("")
        a(f"{improved} of them ({improved / len(centres) * 100:.1f}%) improve on the "
          "box centre; for the rest the search found an offset that is equally "
          "good, which the grid order breaks as a tie.")
        a("")
        a("| Anchor | v1 H (exact) | H at centre (grid) | H at optimal centre (grid) | gain | centre offset |")
        a("|---|---|---|---|---|---|")
        for row in centre_examples:
            a(f"| {row['label']} | {row['before']:.5f} | {row['zero']:.5f} | "
              f"{row['after']:.5f} | {row['improvement']:+.5f} | "
              f"({row['dx']:+.1f}, {row['dy']:+.1f}) |")
        a("")
        a("The exact metric and the grid metric are different scales and are not")
        a("interchangeable: the first column is the published exact value, the")
        a("other two are grid measurements. The gain column compares two grid")
        a("measurements with each other, so it shows what the centre search")
        a("contributes on its own.")
    else:
        a("The optimal-centre search has not been run.")
    a("")
    a("## 7. The reliability threshold, in z terms")
    a("")
    a("The v1 graph was described as trustworthy up to a Hausdorff distance of")
    a("roughly 0.085–0.09. In z terms, over the refined set:")
    a("")
    a("| Percentile-z threshold | Pairs at or above |")
    a("|---|---|")
    for t, count in thresholds:
        a(f"| ≥ {t:.1f} | {count} |")
    a("")
    a("## 8. What this does not establish")
    a("")
    a("Nothing in this report is evidence that any pair is readable. The")
    a("de-biasing changes which pairs the geometry prefers; whether a")
    a("construction is legible to a reader is the question the pilot and the")
    a("full study address, and no such study has been run. The anchor rule")
    a("decides whether the metric change preserved what the geometry already")
    a("found, nothing more.")
    a("")
    a("The enclosure bias described in `findings/known-biases.md` §4 is **not**")
    a("addressed by the z-score: a skeleton metric cannot see whether two")
    a("frames contain the same interior. An ink-area metric would.")
    a("")
    a("## Related")
    a("")
    a("- [`findings/anchors.txt`](anchors.txt) — the frozen anchors and the rule")
    a("- [`findings/known-biases.md`](known-biases.md) — what the biases are")
    a("- [`findings/limitations.md`](limitations.md) — the full limitations list")
    a("- [`methods/HUMAN_EVAL.md`](../methods/HUMAN_EVAL.md) — the study that would test legibility")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"anchors_passed": passed, "overlap": overlap, "rho_v1": rho_v1,
            "rho_v2": rho_v2, "moved_centres": len(moved)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--repo", type=Path, default=paths.REPOSITORY)
    parser.add_argument("--report", type=Path, default=None,
                        help="report path (default: <repo>/findings/debias-report.md)")
    args = parser.parse_args(argv)
    resolve(args)
    repo = args.repo
    out_path = args.report if args.report is not None else repo / "findings" / "debias-report.md"
    stats = build_report(repo, out_path)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()