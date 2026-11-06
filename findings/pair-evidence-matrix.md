---
title: "Pair Evidence Matrix"
id: pair-evidence-matrix
type: finding
status: reviewed
evidence: [MEASURED, REPORTED, DERIVED]
tags: [sinogram, ambigram, rotation-180, control-pair, candidate-pair]
created: 2026-11-01
updated: 2026-11-05
language: en
license: MIT
translations: {zh: machine-assisted, ja: machine-assisted}
related: [results-summary, conflicts-and-corrections, metrics-comparison, exp-08]
---

# Pair Evidence Matrix

One row per pair; every cell cites the run that produced it. **Not comparable across columns** (different metrics, fonts, universes — see [metrics-comparison](../methods/metrics-comparison.md)). Higher = more similar except Mistral (distance, lower = more similar). "—" = not measured / not in the output. Labels: see README (source reference in repo2: `../README.md`).

| Pair | GPT pilot (IoU aligned/unshifted) | GLM (IoU) | Claude v1 (F1) | Claude v2 (score) | Kimi (IoU gothic/Mincho) | Mistral (d_bb, rank/6,328) | MiniMax (exact H) | Reading / verdict |
|---|---|---|---|---|---|---|---|---|
| 土↔士 | .242 / .221 | .40 | refuted: head↔tail shift ≈25% em | absent from candidates | .864 / .808 (blames GLM's rendering) | .155 (depressed by median quirk) | — | **DISPUTED** — [C-03](../findings/conflicts-and-corrections.md) |
| 甲↔由 | .455 / .385 | .52 | .58 (text) | .92 first neighbour of R(甲) in text; **absent from `v2_pares_cruzados.csv`** | self-IoU of 甲 .818 (not C2) | rank 24, .072 | H = .0751, **2nd among distinct pairs** | Visual reading confirms R(甲)=由; metric support varies — [C-05](../findings/conflicts-and-corrections.md) |
| 未↔末 | .436 / .373 | .44 (GLM first said ≠, then "corrected" to =) | .63 | .56; "R(未)≈半" | — | .111 | — | Likely **not** a rotation pair (Claude reading); disputed — [C-02](../findings/conflicts-and-corrections.md) |
| 上↔下 | .530 / .393 | H .66 > R .61 | H .83 vs R .44 | .793 (file line 38 of CSV) | — | #51, .078 | — | Mirror pair (H>R) by GLM and Claude; Claude v2 CSV still lists it — [C-04](../findings/conflicts-and-corrections.md) |
| 士↔干 | .471 / .413 | — | — | **.984** (top row); text: "R(士) practically 干" | self-IoU 干 .760/.568 | #11, .066 | — | **Supported** by Claude (CSV + visual) and Mistral; GPT only .47 (low in raster IoU); visual confirmed |
| 千↔士 | .369 / .307 | — | — | .900 (row 3) | — | **#1, .044** | — | Two independent supports (Claude v2, Mistral); GPT raster IoU is low (.369) |
| 土↔干 | .480 / .383 | — | — | .932 (row 2); text "approximate" | — | — | — | Claude only; visual "R(土)≈干" |
| 王↔玉 | .671 / .644 (top unshifted) | — | .953 | .861 | — | #16, .068 | — | Consistent across runs; one dot to hide — approximate |
| 王↔正 | .671 / .606 | — | — | — | — | #20, .070 | — | GPT, Mistral only |
| 玉↔正 | .627 / .493 | — | — | — | — | #2, .050 | — | GPT, Mistral |
| 上↔丁 | **.680** / .563 | — | — | text .81; CSV `丁,上` .746 (line 92) | — | — | — | Needs hook→bar re-typing; text/CSV differ ([C-14](../findings/conflicts-and-corrections.md)) |
| 旦↔目 | .481 / .382 (目↔旦) | — | .972 (且目 in v1; 旦目 not in v1 list) | .896 (row 4); text: 旦 .91 > 目 .88 as R(目) partner | — | — | — | **False positive** per visual: R(旦) = bar over 日 |
| 旦↔百 | — | — | .981 | .862 | — | #48, .078 | — | Candidate (v1, v2, Mistral) |
| 目↔自 | — | — | .958 (text .96) | .752 (line 78) | — | #31, .075 (自→目) | — | Visual: only resembles; not equivalence; v1/v2 differ much |
| 日↔田 | .263 / .134 | — | — | — | — | — | — | low (GPT) |
| 昌 self | .244 (昌↔呂) / self .091–.194 | .54 | — | not top | absent from top | #6 as "C2", .053 | — | **DISPUTED** — [C-07](../findings/conflicts-and-corrections.md); CHISE gives 昌 = ⿱日曰 |
| 呂/吕 self | self .203–.382 | .52 | — | — | — | .101 (rank 39) | — | slot-convention defect (GLM, Kimi) |
| 圭 self | .139–.145 | .60 (V=.98 mirror) | — | — | absent | — | — | Not self-ambigram (GLM, GPT fixtures) |
| 朋 self | .222–.348 | .52 | — | — | absent | — | — | Not self-ambigram |
| 凹↔凸 | — | R .33 | — | — | — | — | — | negative control OK (GLM only) |

Notes:
* "Row n" for Claude v2 = ranking row in `v2_pares_cruzados.csv` (delivered with the project, not in this distribution), counted from the top excluding the header; "line n" = file line number including the header.
* GPT's self-rotation values for the same character differ between "aligned" and "unshifted" columns (exp-01 (source reference in repo2: `../experiments/exp-01-gpt-pilot-42.md`)).
* MiniMax column: exact distances from `rotation_pairs.csv` (5,180 refined pairs). Only the canonical pair is reproduced here; the full ranking is in `rotation_pairs.csv` (not in this distribution) and the grid-metric version in `rotation_pairs_top.csv.gz` (different scale, see [metrics](../methods/metrics-comparison.md)).
* Pairs not measured anywhere: 杏↔呆, 杳↔杲, 全力↔不屈 (and its characters), 外国↔国外.

## Related

- [Results summary](../findings/results-summary.md)
- [Conflicts and corrections](../findings/conflicts-and-corrections.md)
- [Metrics comparison](../methods/metrics-comparison.md)
- EXP-08 — MiniMax rotation graph (source reference in repo2: `../experiments/exp-08-minimax-rotation-graph.md`)
