# PRC stroke-width correction: original-outline fidelity results

**Status (2026-11-07):** fixed-cohort geometric study integrated via [PR #19](https://github.com/ClaudioDrews/sinogram-ambigram/pull/19) at `ec6e406686f785c9be804d4cd193dd2c62fde7ad`. The corrected constructor is on `main`; the historical v1.16 module remains unchanged for archive replay. No human-reader validation or regional glyph-form certification is claimed.

## Experimental contract

The [predeclared benchmark](../methods/PRC_WIDTH_SEMANTICS.md) selected 32
distinct GB2312-encodable source glyphs from the SHA-256 pinned Make Me a
Hanzi `graphics.txt`: eight in each of four source stroke-count strata,
excluding the nine previously inspected VLM pilot glyphs. It compared
the historical median-to-outline offset (`half_width/2`) against the
corrected offset (`half_width`), using 109×109 masks computed from original
source SVG paths as the reference.

The **entire numerical per-glyph cohort** is retained in
[`data/prc/width-semantics-v2/source-outline-fidelity-32.csv`](../data/prc/width-semantics-v2/source-outline-fidelity-32.csv).
The script reproduces the CSV; the pull-request CI is required to compare
the regenerated file with the frozen checked-in table.

Source SHA-256: `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
Original historical module Git blob SHA:
`87d02ef641f879dae41275551546a671381b9fb9`.

## Measured geometric outcome

| Endpoint (32 glyphs) | Historical v1.16 | Corrected v2 |
| --- | ---: | ---: |
| Median original-outline IoU | 0.47434552 | **0.90834749** |
| Median relative area error | 0.52565448 | **0.06224262** |
| Glyphs with better source-outline IoU | — | **32/32** |
| Glyphs with worse source-outline IoU | — | **0/32** |
| Glyphs with a changed raster silhouette | — | **32/32** |

Median of **paired** IoU gains: **+0.43517647**; mean of paired gains:
**+0.43231246**. The difference of marginal medians is a different
statistic from the median of paired gains; do not conflate them.

All four strata showed improvements in all eight sampled glyphs.
No failure or tie is excluded from the denominator. The smallest observed
paired gain was approximately +0.39753 (`U+659C`), and the large gains
are unsurprising because the legacy code halved already measured radii.

The corrected reconstruction is substantially closer to the underlying
**polygonal source contour approximation** in this fixed cohort.
This does **not** show that any character is readable at both rotations,
nor that every source contour will improve.

## Historical PRC v1.16 results preserved

[Source-level replay CI](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42410884999)
passed on the immutable geometry module: **120/120** centre/extremity
cases, **53/53** sector cases and **six** sector representatives. Historical
summary values were reproduced at absolute tolerance `2e-12`:

- Centre-search mean paired gain: **+0.09251757373426**.
- Centre-search median paired gain: **+0.06921681025491**.
- Mean extremity-rule gain: **+0.00184898858731**.
- Sector gain median: **+0.02287228821046**, mean:
  **+0.03004042551581**; **52/53** sector cases improved.

These are old scores calculated under the old raster semantics; the
corrected-width study has an independent cohort and cannot overwrite
them. This replay does **not** reproduce original cohort-selection logic.

## Reproduction and limitations

```bash
bash scripts/download_prc_sources.sh
python tools/benchmark_prc_outlines.py --graphics data/prc/graphics.txt \
  --out /tmp/prc-outline --require-not-worse
cmp /tmp/prc-outline/source-outline-fidelity.csv \
  data/prc/width-semantics-v2/source-outline-fidelity-32.csv
```

The original SVG outlines are flattened (Q/C sampled) into polygons
and scanline-filled at 109×109. The reference is **independent of the
median-derived outline polygons**, but both paths use the repository's
SVG parser and scanline rasterizer. Browser-accurate SVG rendering,
cap topology and actual region-specific normative source forms remain
separate checks. The sampled cohort is source-stratified, not a
population-level proof.

This repository publishes numerical geometric measurements and source
code. It does not redistribute Make Me a Hanzi original stroke outlines
or PNG-derived glyph assets; their Arphic Public License remains separate
from the MIT license for the code. `human_readability_validated=false`
and `source_forms_certified=false`.

**Decision record:** corrected half-width semantics were approved and merged through replay-safe PR #19 after passing independent source-outline fidelity checks and fixed-cohort historical replay. This is a geometry decision, **not** a determination of ambigram readability.
