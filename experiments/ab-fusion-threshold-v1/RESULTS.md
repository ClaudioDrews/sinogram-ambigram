# A/B fusion registration thresholds — fixed-cohort results (v1)

**Status:** completed geometric diagnostic; **not merged**. This is an
observed result from the predeclared
[protocol](PROTOCOL.md), not a model-reading or human-reading result.

- **Experimental PR:** [#21](https://github.com/ClaudioDrews/sinogram-ambigram/pull/21),
  stacked on unmodified [#16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16).
- **Passing Actions run:** [42414606642](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42414606642)
  and separate source checks [42414606648](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42414606648).
- **Pre-result protocol commit:** `f0e01f9bea7d6731577ce2e1eaa27073f9b8a57c`.
- **Pinned source SHA-256:**
  `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
- **New cohort:** 32 previously uninspected A↔B pairs from a source-only
  hash-selected 128-glyph pool (16 geometrically enriched; 16 seed-selected
  controls). The two known PR #16 pairs 甲↔由 and 韦↔芈 are reported
  **separately**, not included in the new cohort denominators.
- **Numerical evidence:** the CI artifact `ab-fusion-threshold-v1-numerical`
  contains all **170** observations, unabridged cohort manifest and
  JSON aggregate. A compact **34-pair** CSV is checked in at
  [`data/prc/ab-fusion-threshold-v1/pair-diagnostics.csv`](../../data/prc/ab-fusion-threshold-v1/pair-diagnostics.csv).
  No source-derived PNGs have been committed.

## Registered stroke matches versus changed output

The table shows **number of pairs with at least one matched stroke**.
Each denominator is 16 *new pairs*, constant across thresholds.

| Max spine RMS threshold | Geometrically enriched | Hash-selected controls | New pairs with changed binary pixels |
|---:|---:|---:|---:|
| 2 | 0/16 | 0/16 | **0/32** |
| 4 | 2/16 | 1/16 | **0/32** |
| 8 | 11/16 | 6/16 | **0/32** |
| 12 | 14/16 | 9/16 | **0/32** |
| 16 | 16/16 | 15/16 | **0/32** |

Among the **160 new pair-threshold observations**, **74** contained at
least one registered stroke (188 matched spine links total), but **none
was accepted as a different final drawing**. Every proposed output
was pixel-identical to the corrected unmodified union baseline;
there were **zero** differences in binary-raster minimum F1, joint F1
or any 109-grid pixels. At threshold 16, **31/32 new pairs have a
match yet 0/32 have changed ink**.

Across the **10 excluded historical-anchor observations**, the same
pattern holds: zero changed pixels at all five thresholds. At the
original threshold of 4, both anchors have no registration (nearest
spine-pair RMS **5.0310368365** for 甲↔由 and **4.3487651204** for 韦↔芈),
replicating the earlier forensic no-op diagnosis. Matches do appear at
higher thresholds, but none results in an accepted different drawing.

## Interpretation

The pilot's no-op images were caused by **no stroke registration** at
threshold 4. The new diagnostic demonstrates a **second failure stage**:
once registration exists, PR #16's original `construct` function still
returns the unmodified union for every evaluated case. Thus merely
increasing the distance threshold cannot activate fusion on this fixed
cohort. This is an operator-selection outcome, **not a proof of
mathematical impossibility or an estimate of all GB2312 pairs**.

The implementation searches blends with alpha 0.25/0.5/0.75 and accepts
one only if the minimum of upright/reversed reference F1 does not fall
and either joint F1 improves or a tie is achieved with fewer strokes.
The observed aggregate data confirm **zero accepted blends**; they do
*not*, on their own, isolate which inequality rejected each proposed
alpha. The appropriate next instrumented, **post-hoc** experiment is to
record the candidate metrics **before** this acceptance check and
separate no-match, matched-rejected, quantization-tied and accepted
outcomes. That would explain the second failure stage without
retrospectively changing the frozen thresholds or scores.

The two arms are diagnostic convenience samples, not a statistically
representative GB2312 pair population. Selecting by source-only IoU
enriches overlaps deliberately. Different stroke counts and reused
baseline geometry constrain transfer; no native-reader validation
or regional glyph-form certification was attempted.

## Reproduce and provenance

```bash
python -m pip install -r code/requirements.txt
bash scripts/download_prc_sources.sh
python -m unittest discover -s code -p 'test_prc*.py' -v
python tools/ab_fusion_threshold_sweep.py \
  --graphics data/prc/graphics.txt --out /tmp/ab-fusion-threshold
```

CI independently reruns and compares `cohort.json`, `summary.json`
and `observations.csv` byte-for-byte, and verifies the historical anchor
control. The artifacts' exact SHA-256 values:

| Artifact | SHA-256 |
| --- | --- |
| `cohort.json` | `cce885df23d4303c7e482c130327f66e84a7490ed8bd57d5f528fb2c6f43ba7e` |
| `summary.json` | `1119dd6dbcf5961eeee079c9c079180c8fd3e4c092066196dc3b4163c281628e` |
| `observations.csv` | `dbc7950417b742a8a2776c4d4ebfd84522bae4cfb082de382eb95613dbc54439` |

All metrics reflect corrected measured half-width geometry, **not**
archived PRC v1.16 renderer scores. The old historical PRC results
are unchanged. Human readability is **not validated**;
`human_readability_validated=false`,
`regional_forms_certified=false`.
