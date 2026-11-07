# Metrics Used Across Runs

Different runs measured different things on different glyph sets, so **scores are not comparable across rows**. Evidence labels are defined in the [repository README](../README.md).

| Run | Metric | Raw definition (from code/log) | Tolerance / alignment | What it is blind to |
|---|---|---|---|---|
| GPT (exp-01) | Raster IoU of R(A) vs B, 128 px, threshold 96 | ink mask intersection over union | none ("unshifted") or ±3 px ("aligned") | stroke identity; weights ink mass; font optics |
| GLM (exp-02) | max-IoU over translation | same, ±40 px | ±40 px | same; discovery-oriented; hypersensitive for thin strokes (per Claude) |
| Claude v1 (exp-03) | skeleton F-score @ τ=8 px, S=160, chance-corrected | tolerance-band precision/recall of skeletons | 8 px | failed controls (inner-bar offset ~5% em) |
| Claude v2 | W1 on projection profiles (filter) → quantile warp + branch-wise skeleton score (τ=5, K=80), symmetric min | stroke-length profiles; monotone warps | up to warp | rare structures never pre-filtered in; 申 not self-recovered |
| Kimi (exp-04) | FFT max-IoU (±52 px), 2 fonts | raster | ±52 px | ink-mass blindness (甲); taper in Mincho |
| Mistral (exp-05) | chamfer/point-cloud distance + greedy stroke matching on medians (lower = better; d_bb) | geometry of median polylines | bbox centring | stroke width/ends; data quirk (verticals leak) |
| Visual reading (exp-06) | model reading of A, R(A), B | qualitative | n/a | not human; label priming |
| MiniMax (exp-08) | chamfer, RMS, symmetric Hausdorff and dilated IoU (r = 2,3,4) between KanjiVG stroke centrelines; values divided by the 109-unit box | point clouds resampled at 0.45 u from SVG paths; no raster | none (box centre, fixed scale) | stroke type and ink mass; one shape per glyph; frame glyphs favoured |
| IDS algebra (GPT, Claude) | exact tree equality after `R` | symbolic | none | typography/slot conventions; atomic characters (甲, 未) |

## Two H scales inside the MiniMax output (X8)

`c2_class.csv` (2,770 self-pairs) and `rotation_pairs.csv` (5,180 refined pairs) carry **exact** distances (dense point clouds). `rotation_pairs_top5000.csv`, `rotation_pairs_top.csv.gz` and `rotation_pairs_full.csv.gz` carry **grid** distances (chamfer 3-4 distance transform, steps of 1/327 of the box). The same glyph has different H in each: 目 0.03229 (exact) vs 0.03670 (grid); 日 0.04358 vs 0.05199; 田 0.05085 vs 0.06116; the canonical pair 由↔甲 0.0751 (exact) vs 0.08257 (grid). Dilated IoU is identical in both (0.5346 for 目). Never mix the two in one table without a label; the grid/exact gap is quantified by the independent review per band (r = 0.73 below 0.10, 0.996 above 0.14, CR5).

## Metrics proposed but **not run**

Chance-corrected tolerant F1 (run only in Claude); W1 (Claude only); symmetric Chamfer / Hausdorff on KanjiVG medians; GED with M:N merges; TPS warp cost; SDF midpoint `g=(f_a+R f_b)/2` and its rendering error; OCR/CNN recogniser as ρ proxy; distinctiveness weighting; ρ symmetry alarm from the [RFB repo](https://github.com/ClaudioDrews/reversible-faces-benchmark/blob/main/scripts/perceptual.py); composite `D = αD_skeleton + βD_topology + γD_distinctiveness + δD_style` (`later methodological critique`). Details: [existence-criterion §6](../theory/existence-criterion.md).

## Known systematic biases

1. **Font optics:** inner bars of 十 日 目 sit ≈5% em above centre in Noto Sans (Claude) — depresses raster scores of true C2 glyphs.
2. **Taper:** Mincho wedge strokes: 一 gothic 1.000 vs Mincho .204 (Kimi).
3. **Ink-mass weighting:** a discriminating stroke of ~15% ink (甲 vs 由 protrusion) is invisible to IoU (GLM, Kimi, GPT).
4. **Slot convention:** upper component of ⿱SS drawn smaller → 昌/吕 .09–.54 although algebraically exact.
5. **Alignment policy:** translation search (±3/±40/±52 px) changes ranks (GPT 上↔丁 .563 → .680); compounds are slot-anchored in reality.
6. **Font lineage:** GLM/Kimi/GPT/Claude all use Source Han–family outlines; the 土↔士 discrepancy (.24–.86) is partly attributed to rendering differences — unresolved ([C-03](../findings/conflicts-and-corrections.md)).

## Related

- Methodology
- Experiments index
- [Results summary](../findings/results-summary.md)
- [Rotation-graph method (MiniMax)](../methods/rotgraph-method.md)
