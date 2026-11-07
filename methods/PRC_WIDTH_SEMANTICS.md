# PRC stroke-width semantics: historical v1.16 and corrected v2

**Status:** draft integration study; not merged to `main`. The criterion here
is fidelity to **source contours**, not automated or human recognition.

## Why two modules are mandatory

The Make Me a Hanzi loader measures `half_width` as the distance from
each resampled stroke median point to the nearest sampled source outline.
The archived PRC v1.16 polygon renderer subsequently used
`normal * (half_width / 2)`, which halves that measured radius a second
time. PR #13 corrects the reconstruction to `normal * half_width`.
That is a genuine geometric change, not a safe refactor of old scores.

- **Historical `legacy-v1.16`:** `code/prc_construct_legacy_v116.py`
  reproduces the exact `code/prc_construct.py` bytes of main commit
  `a9ddfabbdfe32d781c816ffbd6c93fc194d12e30`;
  Git blob SHA `87d02ef641f879dae41275551546a671381b9fb9`.
  `tools/replay_prc_v116.py` imports only this module.
- **Corrected `measured_half_width_v2`:** `code/prc_construct.py`
  retains PR #13's geometry change and its targeted synthetic regressions.
- **Historical archive:** numerical tables, JSON digests and source-pinned
  cohorts in `data/prc/archive-v1.16/` are not rewritten or re-labelled.

The historical replay checks 120 centre/extremity cases, 53 sector cases,
and six representatives, as described in
[`PRC_V116_REPRODUCTION.md`](PRC_V116_REPRODUCTION.md).
It reproduces *fixed-cohort measurements*, not original cohort selection.

## Pinned independent source-outline benchmark

The source is Make Me a Hanzi `graphics.txt` at upstream commit
`bddc96d41bef78427ed0e034e9f7e31d71fd1b92`, SHA-256
`a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
The source geometry has its own Arphic Public License, independent of
the repository's MIT code license. No derivative glyph images are committed.

The benchmark at `tools/benchmark_prc_outlines.py` was specified before
running the present CI. Its cohort selection depends **only on source
metadata**, not on observed IoU outcomes:

1. Keep one-codepoint source entries encodable by GB2312, with a one-to-one
   correspondence between nonempty `strokes` and `medians`.
2. Exclude the nine previously inspected pilot glyphs:
   `中 口 日 田 目 甲 由 韦 芈`.
3. Partition by source stroke count: 1–4, 5–8, 9–12 and 13 or more.
4. Sort each stratum by SHA-256 of
   `prc-width-independent-stratified-2026-11-07-v1|<character>`.
   Choose the first **eight** per stratum: **32 glyphs** total.
5. Reconstruct the original source SVG stroke contours separately from
   the two median-width polygons, and rasterize all three to 109×109.
6. Record per-glyph source area, candidate area, original-outline IoU,
   paired IoU delta, source retention, candidate precision, relative area
   error and the number of pixels changed by the correction.
7. Report medians and means, improved/equal/worse counts and the selection
   seed. Determinism is checked by repeated full runs and file comparison.

**Predeclared automated acceptance:** exact historical-module blob hash;
offline synthetic rectangle/curve/degenerate tests; archived 120/53/6 numeric
replay within the original tolerance; valid nonempty source masks;
at least one changed output in the 32-case benchmark; and corrected
**median** original-outline IoU no worse than the historical median.
A failure must be reported rather than removing difficult glyphs or
changing this threshold retrospectively. Per-glyph regressions are retained
even if the aggregate passes.

## Limits on what this measures

The original source contour reference is a *polygonal approximation*:
SVG quadratic and cubic curves are sampled and filled with an even-odd
109×109 scanline rule. This checks fidelity against the **original MMah
outline paths**, rather than against a raster constructed from the same
median-width hypothesis, but it is not a full browser SVG parity test.
The median-to-boundary estimate samples outline vertices; curved stroke
caps, concavities, zero-length tangents and pixel-edge ties can cause
local mismatch. Preserve the per-glyph results for subsequent diagnosis.

GB2312 codepoint coverage does **not** certify normative Mainland glyph
forms. This benchmark does not mix Japanese KanjiVG with the MMah source.
Neither ink IoU nor VLM recognition demonstrates human readability.
`human_readability_validated=false` and `source_forms_certified=false`.

## Reproduce

```bash
python -m pip install -r code/requirements.txt
python -m unittest discover -s code -p 'test_*.py' -v
bash scripts/download_prc_sources.sh

python tools/replay_prc_v116.py --graphics data/prc/graphics.txt \
  --archive data/prc/archive-v1.16 --out /tmp/prc-v116-replay
python tools/verify_prc_archive.py /tmp/prc-v116-replay \
  --out /tmp/prc-v116-verified

python tools/benchmark_prc_outlines.py --graphics data/prc/graphics.txt \
  --out /tmp/prc-width-study --require-not-worse
```

The PR GitHub Actions workflow records the source-level replay and two
deterministic benchmark executions. Inspect the Actions run and its
`prc-source-outline-fidelity` artifact for measured outcomes; do not
infer a passing benchmark merely because these commands are documented.

**Merge decision:** requires explicit maintainer review. Geometry may be
published experimentally without human-reader evidence, but must remain
labelled as unvalidated perceptual candidates.
