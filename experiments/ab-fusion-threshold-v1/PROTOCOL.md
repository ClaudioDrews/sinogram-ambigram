# A/B fusion threshold-sensitivity experiment — frozen protocol v1

**Status:** experiment predeclared before examining the new threshold-sweep outputs.
**Independent branch:** `exp/ab-fusion-threshold-sensitivity`, forked from immutable
[PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) head
`c222133c59d07103d162dda5a1a3357764cfd0c7`. This does not rebase,
merge or modify PR #16. The existing PR #20 reports the **previously observed**
two-case null result; those cases are excluded from the new study.

## Question and mechanism

Does expanding the maximal RMS stroke-registration distance cause the existing
A/B fusion constructor to (a) find a one-to-one match, (b) accept a proposed
blend rather than the union fallback, and (c) produce a **pixel-different**
binary raster compared with the unchanged union control? These are *three*
separate empirical events, not interchangeable notions of success. A change
of pixels or geometric F1 cannot establish legibility.

## Frozen source, geometry, cohort and controls

- **Source:** Make Me a Hanzi `graphics.txt`, upstream revision
  `bddc96d41bef78427ed0e034e9f7e31d71fd1b92`, SHA-256
  `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
- **Constructor:** exactly PR #16's `code/prc_ab_fusion.py`, using corrected
  `code/prc_construct.py` measured half-width semantics and 109×109 grid.
  No operator modifications or adapted acceptance criteria in this study.
- **Selection seed:** `prc-ab-threshold-2026-11-07-v1`. Eligible glyphs are
  one-codepoint, GB2312-encodable, with matching nonempty `strokes` and
  `medians` arrays. Remove the nine already-inspected pilot glyphs
  `中口日田目甲由韦芈`; no Japanese KanjiVG glyphs.
- **Frozen eligibility pool:** 128 characters with the smallest SHA-256 of
  `seed|pool|character`. All selection is reproducible and based on the
  pinned source, **before running the fusion operator**.
- **Geometry-enriched arm:** among all unequal pairs from the pool, compute
  109-grid binary ink IoU of upright A against rotated B using *unmodified
  corrected-source shapes*. Rank by descending IoU, then by SHA-256 of
  `seed|enriched|A|B`; greedily take **16 pairs with disjoint glyphs**.
  This intentionally enriches high source-only geometric overlap.
- **Control arm:** remove the 32 characters used in enriched pairs, sort the
  remaining eligible pool by SHA-256 of `seed|control|character`, pair the
  first 32 in order for **16 disjoint-character control pairs**. Controls
  are seed-selected, not representative of the whole GB2312 repertoire.
- **Reproduction-only anchors:** **甲↔由** and **韦↔芈** from PR #16,
  labelled `previous_pilot`, never counted in the new 32-pair endpoints.
- Do not alter case selection based on whether matches or pixel changes occur.
  If no change is detected, publish that negative outcome rather than
  retrospectively selecting favourable examples.

## Fixed interventions and outcomes

- Centre: (54.5,54.5). Widths: measured half-width. Sampling: 24 points
  per median. Greedy one-to-one RMS matcher, including reversal.
- **Thresholds (109-grid pixels): 2, 4, 8, 12, 16.** Each threshold is applied
  independently to the *same frozen pair list*.
- Blend coefficients: **0.25, 0.5, 0.75** (PR #16 defaults).
- Baseline: unmodified union of A and the half-turned B, at identical source
  and geometry. Compute baseline F1 and changes relative to the same control.
- Per case/threshold: number of candidate matches, nearest spine-pair RMS,
  accepted stroke count, union stroke count, changed binary pixels, F1 for A
  and B, minimum F1, joint F1, and paired joint/min F1 deltas.
- Classify `no_match`, `matched_rejected_or_union`,
  `accepted_pixel_identical`, or `changed_pixels` *in this order*.
  An accepted blend may yield identical raster after quantization; do not
  label it a geometric pixel change.
- **Primary descriptive endpoints:** fraction of the *32 new pairs* with at
  least one matched stroke; fraction with nonzero changed pixels, by threshold
  and cohort arm. Report all five values, positive and negative.
- **Secondary endpoints:** nearest spine RMS distributions, accepted
  stroke-count reductions, joint/min F1 deltas and any failures to match
  after raising the threshold. Do not use these descriptive outcomes to
  select a winning threshold without a later independent test.
- Record all 34×5 observations (including anchors) in machine-readable CSV;
  also record per-arm counts and means in JSON, plus the 32-pair cohort
  manifest and SHA-256 provenance. `human_readability_validated=false`,
  `regional_forms_certified=false`.

## Technical gates

1. Verify pinned-source digest before any work; reject a mismatch.
2. Regenerate and diff the cohort manifest and all results twice in CI;
   byte-identical output is mandatory.
3. Preflight synthetic tests: matched vs unmatched, ascending thresholds,
   single-pair reversible RMS, no-op classification.
4. On historical anchors, threshold=4 must yield **0 matched** and **0
   changed pixels** as in PR #16. A mismatch invalidates the comparison.
5. Run existing PRC regressions on the experiment branch.
6. Preserve all original data, PRs #13–#17, main, and old metrics.
7. Save source-only quantitative findings and limitations in English and
   Simplified Chinese. A Japanese brief can follow; no Portuguese text,
   private run logs or agent identifiers may enter the public repository.
8. Use GitHub Actions to execute the full pinned-source study and retain
   numerical artifacts. **No MMah-derived PNGs** in git; code MIT and
   original outlines licensed separately under Arphic Public License.
9. No merge to main, tag or release on this phase. Findings are exploratory
   geometry diagnostics and **not** a blind perceptual study.

## Next independent experiment

R-ODD and harmonic branches address **single-character self-rotation**,
not A/B distinct-character fusion. Their assessment must use its own
paired cohort, the same corrected-width baseline, and separate geometry
and recognition endpoints. Do not rank or pool them with this A/B study.
