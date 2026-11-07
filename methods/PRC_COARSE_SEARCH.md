# PRC coarse rotational candidate search

**Status:** experimentally implemented, source and preset isolated. This
deterministic shortlist generator is **not** an exact-distance proof or
evidence of readable ambigrams. Outputs are derived from licensed source
geometry and require review before redistribution.

## Input and regional guards

Stage 14 reads Stage 12's median-skeleton distance-transform cache and
Stage 13's hash-verified repertoire. It rejects absent/duplicate members,
mismatched source digests, malformed cache shapes, and wrongly assigned raw
regions. Default preset: cn-s-gb2312. Regional glyph forms have not been
independently certified.

## Algorithm

1. Each glyph's 109×109 occupancy is the condition dt == 0. Symmetrically
   pad to 111×111 and max-pool non-overlapping 3×3 tiles to 37×37. Symmetric
   padding commutes with a 180° rotation: C(R(A)) = R(C(A)).
2. For every glyph a, compute its coarse intersection over union with every
   half-turned glyph b:

   \[
   \operatorname{IoU}_{37}(a,b)
   = \frac{|C(a) \cap R_{180} C(b)|}{|C(a) \cup R_{180} C(b)|}.
   \]

   Block matrix multiplication evaluates all 6,763×6,763 **ordered**
   coarse scores without holding the complete similarity matrix in RAM.
3. For each glyph a, calculate its null distribution from **all other**
   glyphs: mu_a = mean_{j != a}(IoU37(a,j)) and
   sigma_a = std_{j != a}(IoU37(a,j)). Use the population standard
   deviation, floored at 1e-12. For pair (a,b), compute
   z_a = (IoU37(a,b) - mu_a) / sigma_a, likewise z_b, and the pair score
   min(z_a,z_b), so both glyphs must be unusually similar relative to
   their own null populations.
4. Collect the union of the top 20 coarse matches **per glyph**, including
   self-pairs when selected. Deduplicate canonically; ties are broken by
   Unicode scalar order. This is a shortlist, **not** an exhaustive
   fine-grid Hausdorff or exact point-cloud ranking.

Coarse scores use the suffix _grid37; never equate them with 109-grid,
point-cloud exact, or filled-ink construction scores.

## Reproduce

~~~bash
bash scripts/download_prc_sources.sh
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt
python code/stage13_prc_presets.py --graphics data/prc/graphics.txt
python code/stage14_prc_search.py \
  --cache data/prc/cache \
  --inventories data/prc/inventories \
  --out data/prc/search \
  --preset cn-s-gb2312 --top-k 20 --batch-size 64
~~~

Results are deliberately local:

- null_model_grid37.csv: every glyph's null mean, population deviation and
  partner count.
- candidates_grid37.csv: canonical pairs, coarse IoU, both null scores, pair
  score, region and preset.
- search-summary.json: source SHA, method, cohort and explicit
  human_legibility_validated=false.

## Limitations and next step

Coarse pooling yields false positives/negatives relative to fine-grid
distances. Stroke medians differ from filled ink. Neither high overlap nor
a high z-score establishes character readability. The next **separate**
step is detailed pair refinement using the 109-grid DT/point cloud,
optimal rotation centres, matched before/after comparisons on held-out
characters, and perceptual evaluation where feasible.
