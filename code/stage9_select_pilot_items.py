"""Stage 9: select the pilot's evaluation items and render them.

The pilot tests whether the constructions the engine puts on top are read more
often than constructions made from unrelated pairs. For that, the selection
must be drawn from the ranking that Gate A will publish (the v2 ranking), and
it must contain a matched negative control set so that a positive result
cannot be explained by the construction method producing readable drawings by
accident.

Strata, following methods/HUMAN_EVAL.md:

  v1-top        12  best distinct pairs of the v1 raw-distance ranking
  v2-top        14  best distinct pairs of the v2 z-score ranking, disjoint
                   from v1-top
  self          8   strongest C2 self-rotations
  control       14  random unrelated pairs drawn from the *same complexity
                   stratum* as the v2-top items, so that the control set
                   cannot be told apart by complexity alone

The two strata the decision rule compares, v2-top and control, carry the
same number of items: that pairing is what the power simulation in
``code/test_pilot_power.py`` found to be the strongest of the designs it
tested, and it is the design methods/HUMAN_EVAL.md fixes.

The seed for the control draw is fixed and recorded.

Each item is rendered with the same salience construction the browser
generator uses, so the pilot judges the artefact a visitor actually sees.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import paths  # noqa: E402
from paths import add_common_args, resolve  # noqa: E402

SEED = 20261107
N_V1 = 12
N_V2 = 14
N_SELF = 8
N_CONTROL = 14


def _read_v1(repo: Path) -> list[dict]:
    with open(repo / "data" / "rotation_pairs.csv", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_v2_full(v2_dir: Path) -> list[tuple[str, str, float, int]]:
    """Distinct pairs with their percentile-z and stratum, best first."""
    path = v2_dir / "rotation_pairs_full_grid_v2.csv.gz"
    rows = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["self"] == "True":
                continue
            rows.append((row["a"], row["b"], float(row["percentile_z_grid"]),
                         int(row["stratum"])))
    rows.sort(key=lambda r: (-r[2], r[0], r[1]))
    return rows


def select(repo: Path, out_path: Path, seed: int = SEED) -> dict:
    v1 = _read_v1(repo)
    v2_dir = repo / "data" / "v2"

    strokes: dict[str, int] = {}
    sets: dict[str, str] = {}
    for row in v1:
        strokes[row["a"]] = int(row["a_strokes"])
        strokes[row["b"]] = int(row["b_strokes"])
        sets[row["a"]] = row["a_set"]
        sets[row["b"]] = row["b_set"]

    # ---- v1 top (distinct) ----------------------------------------------------
    distinct_v1 = sorted((r for r in v1 if r["a"] != r["b"]),
                          key=lambda r: float(r["hausdorff"]))
    v1_top = [(r["a"], r["b"]) for r in distinct_v1[:N_V1]]
    v1_keys = {frozenset(p) for p in v1_top}

    # ---- v2 top (distinct), disjoint from v1 top -------------------------------
    v2_rows = _read_v2_full(v2_dir)
    v2_top: list[tuple[str, str]] = []
    for a, b, _pct, _stratum in v2_rows:
        if frozenset((a, b)) in v1_keys:
            continue
        v2_top.append((a, b))
        if len(v2_top) == N_V2:
            break

    # ---- self-rotations -------------------------------------------------------
    self_rows = sorted((r for r in v1 if r["a"] == r["b"]),
                       key=lambda r: float(r["hausdorff"]))
    self_top = [(r["a"], r["a"]) for r in self_rows[:N_SELF]]

    # ---- matched negative controls -------------------------------------------
    rng = np.random.default_rng(seed)
    stratum_members: dict[int, list[tuple[str, str]]] = {}
    for a, b, _pct, stratum in v2_rows:
        stratum_members.setdefault(stratum, []).append((a, b))

    used = {frozenset(p) for p in v2_top} | v1_keys | {frozenset(p) for p in self_top}
    controls: list[tuple[str, str]] = []
    for a, b in v2_top:
        if len(controls) >= N_CONTROL:
            break
        target = int(round((strokes.get(a, 12) + strokes.get(b, 12)) / 2))
        pool = [p for p in stratum_members.get(target, [])
                if frozenset(p) not in used]
        if not pool:
            # The exact stratum is exhausted: take the nearest stratum that
            # still has members, so the control set keeps its full size and
            # stays as close as possible in complexity.
            for delta in (1, -1, 2, -2, 3, -3, 5, -5):
                alternative = stratum_members.get(target + delta)
                if not alternative:
                    continue
                pool = [p for p in alternative if frozenset(p) not in used]
                if pool:
                    break
        if not pool:
            continue
        pick = pool[int(rng.integers(len(pool)))]
        used.add(frozenset(pick))
        controls.append(pick)

    items = []
    index = 0
    for stratum, pairs in (("v1-top", v1_top), ("v2-top", v2_top),
                           ("self", self_top), ("control", controls)):
        for a, b in pairs:
            index += 1
            items.append({
                "id": f"pilot-{index:03d}",
                "stratum": stratum,
                "pair": [a, b],
                "label_a": a,
                "label_b": b,
                "a_set": sets.get(a, ""),
                "b_set": sets.get(b, ""),
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0",
        "seed": seed,
        "note": "Stratum is recorded for analysis only and is never shown to a "
                "participant. The order of items is randomised per respondent by "
                "the page.",
        "items": items,
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return payload


def render(repo: Path, items_path: Path, out_path: Path) -> int:
    """Attach the rendered construction SVG to every item."""
    from make_ambigram import ambigram_svg

    payload = json.loads(items_path.read_text(encoding="utf-8"))
    for item in payload["items"]:
        a, b = item["pair"]
        # ambigram_svg returns the strokes of the construction; the page needs
        # a complete SVG document, because a bare fragment cannot be drawn.
        item["construction_svg"] = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 109 109" '
            'class="construction">' + ambigram_svg(a, b) + '</svg>'
        )
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return len(payload["items"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--repo", type=Path, default=paths.REPOSITORY)
    parser.add_argument("--items", type=Path, default=None)
    parser.add_argument("--render", type=Path, default=None,
                        help="where to write the rendered items "
                             "(default: the same file as --items)")
    args = parser.parse_args(argv)
    resolve(args)

    repo = args.repo
    items_path = args.items if args.items is not None else repo / "evaluation" / "items.json"
    payload = select(repo, items_path, seed=args.seed)
    counts: dict[str, int] = {}
    for item in payload["items"]:
        counts[item["stratum"]] = counts.get(item["stratum"], 0) + 1
    print(f"selected {len(payload['items'])} items -> {items_path}")
    for stratum, count in counts.items():
        print(f"  {stratum}: {count}")

    render_path = args.render if args.render is not None else items_path
    count = render(repo, items_path, render_path)
    print(f"rendered {count} constructions -> {render_path}")


if __name__ == "__main__":
    main()