# Pilot 01 — Scored results (English)

## Summary

**Four vision-language model families, 52 images, 208 scheduled model×image trials.** These are exploratory images from five self-rotating source characters and two distinct-character pairs. All counts below use strict exact Unicode matching, with invalid/UNKNOWN/errors counted as incorrect. Models do not establish human legibility.

### Self-rotation: both orientations recognized

| Method | Model×drawing successes | Single-orientation matches |
|---|---:|---:|
| Historical main | **10/20** (50%) | **25/40** (62.5%) |
| Thickness-corrected | **14/20** (70%) | **31/40** (77.5%) |
| R-ODD | **13/20** (65%) | **31/40** (77.5%) |
| Harmonic | **15/20** (75%) | **32/40** (80%) |

All denominators are model×character combinations within the five-character self-rotation cohort, **not** statistically independent human readers.

### Same-model, same-character, same-orientation paired changes

| Comparison | Incorrect → correct | Correct → incorrect | Net |
|---|---:|---:|---:|
| Thickness versus historical main | 9 | 3 | +6/40 |
| R-ODD versus historical main | 8 | 2 | +6/40 |
| Harmonic versus historical main | 8 | 1 | +7/40 |
| R-ODD versus thickness | 3 | 3 | 0/40 |
| Harmonic versus thickness | 3 | 2 | +1/40 |

### Self-rotation: single-orientation matches by model

| Method | DeepSeek | MiniMax | HY4 | GLM | Total |
|---|---:|---:|---:|---:|---:|
| Historical main | 5/10 | 8/10 | 3/10 | 9/10 | 25/40 |
| Thickness-corrected | 6/10 | 8/10 | 8/10 | 9/10 | 31/40 |
| R-ODD | 7/10 | 9/10 | 7/10 | 8/10 | 31/40 |
| Harmonic | 6/10 | 8/10 | 8/10 | 10/10 | 32/40 |

### Self-rotation: both-orientation successes per character, out of four models

| Target | Historical main | Thickness | R-ODD | Harmonic |
|---|---:|---:|---:|---:|
| 中 | 1 | 4 | 4 | 4 |
| 口 | 3 | 4 | 4 | 4 |
| 日 | 3 | 4 | 4 | 3 |
| 田 | 2 | 1 | 0 | 3 |
| 目 | 1 | 1 | 1 | 1 |

## Different-character pairs

Pairs **甲 ↔ 由** and **韦 ↔ 芈** yielded **0 correct single-orientation reads out of 16 per arm**, and thus **0/8 dual-orientation successes per arm**, for each of historical main, thickness-fixed union and A/B fusion.

**Critical null finding:** all four A/B fusion PNGs were byte-identical to their thickness-fixed union counterparts. For these two examples the fusion algorithm made **no observable edit**. Divergent model outputs to duplicate images must not be attributed to an algorithmic geometry change.

## Output quality

| Model | Valid single-character | UNKNOWN | Invalid (empty) | Transport error |
|---|---:|---:|---:|---:|
| MiniMax M3.1 Flash | 37 | 0 | 14 | 1 |
| DeepSeek V4.1 Flash | 50 | 1 | 1 | 0 |
| Tencent HY4 | 52 | 0 | 0 | 0 |
| GLM-5.3 Flash | 44 | 0 | 8 | 0 |

Overall **207/208 HTTP 200**; **23 length-limited completions**. In 34/52 trials all four responses were syntactically valid; in 19/52 all four valid readings agreed. Agreement is not correctness. Invalid answers remain in the primary denominator.

## Interpretation

The thickness correction shows a descriptive improvement in the self-rotation task, compatible with restoration of stroke width. The apparent harmonic advantage over thickness is only **+1/40** single-orientation cases (three improved, two worsened), and R-ODD is **0/40** net. The five self-characters and two different-character pairs are a small preselected demonstration, with shared models, possible provider variation, and no human subjects.

The distinct-pair failure motivates structural/topological two-character construction, not a claim that rotational ambigrams are impossible. The results neither establish a winner nor justify merging experimental algorithms.

**Next gates:** verify contour fidelity against source outlines; enlarge and preregister a stratified held-out cohort; preserve exact response/error outputs; check genuine-glyph and malformed-glyph controls; report paired model×glyph changes; add native reader evaluation as a separate endpoint.
