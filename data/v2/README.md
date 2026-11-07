# v2 datasets

> **Status: experimental.** These files are the output of the de-biasing work
> described in [`findings/debias-report.md`](../../findings/debias-report.md). They
> have **not** been validated by human readers, and no result in them is a
> validated ambigram.

The v1 datasets live in [`../`](../README.md) and are left untouched.
This directory holds the re-ranked, re-centred data produced by
`code/stage7_normalise.py` and `code/stage8_optimal_center.py`.

## Files

| File | Contents | Scale |
|---|---|---|
| `null_model.csv` | Per-glyph null mean, standard deviation and partner count | Grid distance-transform approximation |
| `rotation_pairs_full_grid_v2.csv.gz` | All 3,837,835 unordered pairs with z-scores, percentiles and strata | Grid distance-transform approximation |
| `rotation_pairs_refined_v2.csv` | The 5,180 refined pairs with their exact metrics **and** their v2 ranking quantities | Mixed — see below |
| `optimal_centres.csv` | The optimal rotation centre and distance for each refined pair | Grid distance-transform approximation |
| `optimal_centres_stats.json` | Summary of the centre search | — |
| `normalisation_stats.json` | Seed, partner count, definitions | — |

## The scale warning, in detail

**Two scales appear in `rotation_pairs_refined_v2.csv`, deliberately, and the
column names say which is which:**

| Column | Scale |
|---|---|
| `hausdorff_exact`, `chamfer_exact`, `rms_exact`, `sim` | **Exact point-cloud** Euclidean distances, normalised by 109 |
| `z_a_grid`, `z_b_grid`, `z_pair_grid`, `percentile_z_grid` | **Grid** distance-transform approximation, normalised by 109 |

The z-scores are computed on the grid scale because the null model needs a
distance for every one of the 2,770 × 30 partner draws, and because the
percentile is defined over the full pair space, which only the grid stage
covers. The exact metrics are retained because they are the more precise
measurement for the shortlisted pairs.

**Do not compare a `hausdorff_exact` value with a `hausdorff_grid` value, and
do not apply a threshold from one to the other.** This is the same trap the
conflict register records as X8.

## Column meanings

### `null_model.csv`

One row per glyph in the 2,770-character inventory.

| Column | Meaning |
|---|---|
| `null_mu_grid` | Mean grid distance from this glyph to its 30 drawn null partners |
| `null_sigma_grid` | Standard deviation of the same distances |
| `null_partners` | How many partners were actually drawn (30 unless the glyph had too few peers) |
| `seed` | The seed used for the sampling |

A glyph with a small `null_mu_grid` is one that sits close to many partners
simply because of its own size or density. That is what the z-score removes.

### `rotation_pairs_full_grid_v2.csv.gz`

| Column | Meaning |
|---|---|
| `hausdorff_grid`, `chamfer_grid`, `rms_grid` | Raw grid distances, unchanged from v1's grid stage |
| `z_a_grid` | `(d − mu_a) / sigma_a` — the pair's score relative to character *a*'s null |
| `z_b_grid` | The same relative to character *b*'s null |
| `z_pair_grid` | `max(z_a_grid, z_b_grid)` — the published per-pair score |
| `percentile_z_grid` | Rank of `z_pair_grid` within the complexity stratum, 0–100, **larger is better** |
| `stratum` | Rounded mean of the two characters' stroke counts |
| `self` | Whether the pair is a self-rotation |

Pairs are written in canonical order (by character, then by code point), so
the file is stable between runs.

### `optimal_centres.csv`

| Column | Meaning |
|---|---|
| `hausdorff_grid_zero` | Grid Hausdorff at the box centre, the centre the v1 ranking assumed |
| `hausdorff_grid_optimal` | Grid Hausdorff at the best centre found |
| `improvement_grid` | `hausdorff_grid_zero − hausdorff_grid_optimal` |
| `centre_dx`, `centre_dy` | Offset of the best centre from the box centre, in units |
| `translation_dx`, `translation_dy` | The equivalent translation of the half-turned partner, in units |
| `self` | Whether the pair is a self-rotation |

The centre grid is 9 × 9 points at 54.5 + {−6, −4.5, …, +6} units. The
distance transform is computed on a padded 125 × 125 canvas so that a
translated point that leaves the character box receives a meaningful distance
instead of being clipped onto the border. At offset zero the padded transform
reproduces the original one exactly (maximum difference 0.00000 over seven
test pairs), so the two centre columns are comparable with each other and
neither is comparable with a `hausdorff_exact` value.

Of the 5,180 refined pairs, 3,646 (70.4%) have a best centre other than the
box centre, and 2,886 (55.7%) improve on it. The rest have an offset that is
equally good, which the grid order breaks as a tie.

## Reproducing

```bash
bash scripts/download_kanjivg.sh
python code/stage1_skeleton.py
python code/stage2_distances.py
python code/stage3_iou.py
python code/stage4_refine.py --top-k 2500
python code/stage7_normalise.py
python code/stage8_optimal_center.py
python code/stage9_select_pilot_items.py
python code/stage11_debias_report.py
```

The normalisation stage is deterministic: the partner sampling uses a fixed
seed (20261107) and a fixed selection rule, so repeated runs produce
byte-identical files. `code/test_determinism.py` guards stage 1 against
unintended change.

`rotation_pairs_full_grid_v2.csv.gz` is a build artefact and is **not tracked
in this repository**: it is 108 MiB, above the 100 MiB that GitHub accepts
for a single file, and the v1 archive follows the same convention. The stage
above regenerates it byte for byte from the pinned KanjiVG snapshot.

## Licence and provenance

These are derived research outputs of the project, MIT licensed as in
[`../../LICENSE`](../../LICENSE), except where a row inherits a third-party source:
the glyph geometry they measure is KanjiVG (CC BY-SA 3.0). See
[`../../LICENSE-AUDIT.md`](../../LICENSE-AUDIT.md) and
[`../../NOTICE.md`](../../NOTICE.md).

## What the de-biasing changed

Measured by `code/stage11_debias_report.py`, reproduced in
[`../../findings/debias-report.md`](../../findings/debias-report.md):

| | v1 | v2 |
|---|---|---|
| Spearman ρ between the ranking quantity and the stroke count | −0.419 | **−0.026** |
| Degree of the most connected character of the top 100 pairs | 20 | **5** |
| Share of edges held by the ten most connected characters | 27.0% | **17.5%** |
| Pairs common to the two top-100 lists | — | 11 of 100 |

All seven decision anchors frozen in `findings/anchors.txt` fall in the top
5% of their complexity stratum under v2, where the frozen rule needs four.
The rule's own output is GO; the maintainer still approves it.

## Related

- [`../README.md`](../README.md) — the v1 datasets and their metric provenance
- [`../../findings/known-biases.md`](../../findings/known-biases.md) — what the biases are
- [`../../findings/debias-report.md`](../../findings/debias-report.md) — before and after
- [`../../findings/anchors.txt`](../../findings/anchors.txt) — the frozen anchors