# Controlled PRC ambigram experiments

Status: **experimental — do not merge into main without regression and reading evidence**.

## Frozen comparison design

- Historical baseline: record the exact `main` commit and source glyph data checksum before running the benchmark.
- Common geometry baseline: `exp/thickness-fix`, after confirming the median-to-outline width convention and passing the regression suite.
- Single-factor branches, all forked from the same fixed baseline:
  - `exp/r-odd` — local compensation toward rotated ink.
  - `exp/harmonic` — smooth continuous thickness field.
  - `exp/ab-fusion` — two-character construction.
- A later `exp/harmonic-r-odd` may test interactions; never treat it as a single-factor ablation.

## Measurement contract

Use identical source glyphs, encoding, candidate lists, centres, seeds, input rendering, output raster resolution, and allowed ink-retention/growth constraints across arms. Keep reference images, raw output images, metrics, code commit, parameters, original source hash, and selection decisions.

Preserve old measurements rather than comparing numerical results across incompatible half-width interpretations. Record both original ink retention (intersection over original area) and growth (candidate area over original area). Symmetry is a geometric proxy, **not** readability.

## Blind VLM protocol

1. Freeze target pairs and evaluation images before querying readers.
2. Randomize image filenames and model presentation order. Do not disclose the intended labels, branch, or the desired rotation.
3. Present upright and exact 180-degree rotated rasters independently. Run reference genuine glyphs and malformed controls in the same batches.
4. Store model name/version, prompt, decoding parameters, timestamp, response verbatim, parsed reading, and missing/invalid result.
5. Primary endpoint: both orientation readings correct for one pair. Report per-orientation scores, model disagreement, exact pair counts, paired comparisons, and uncertainty separately.
6. Keep tuning/development examples separate from held-out test examples; do not tune against the held-out responses.
7. Human native-reader assessment remains a separate later gate. VLM success is automated recognition evidence, not proven human legibility.

## Merge gates

- Source provenance/licensing and no regional inventory mixing.
- Full existing suite plus method-specific tests (geometry, determinism, invariants, failure modes).
- Reproducible benchmark with frozen artifacts and no regression on baseline controls.
- Positive held-out dual-reading evidence with uncertainty; no cherry-picked examples.
- Human-reader gate when human legibility is claimed.

This protocol is a research contract. No visual-recognition results have yet been obtained by these branches.
