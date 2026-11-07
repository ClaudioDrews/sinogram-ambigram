# PRC A/B fusion: forensic diagnosis of the two-pair no-op

**Status:** observed mechanism, 2026-11-07; separate diagnostic draft. The A/B operator in [PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) remains **unmerged and unchanged**. This is not a representative, held-out test of pair construction or reading.

## Immutable evidence

- Experimental commit: `c222133c59d07103d162dda5a1a3357764cfd0c7` (`exp/ab-fusion`).
- Successful [GitHub Actions run 42399361826](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42399361826), artifact `prc-experiment-stimuli` (ID `13584656789`).
- Downloaded artifact ZIP SHA-256: `17e453aed0186b59d560850386b6d86b1b09064fdd9a2bd8667369ed43135b24`; no derived glyph images are committed here.
- Pinned Make Me a Hanzi `graphics.txt` source SHA-256: `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
- Both `fixed-pairs/manifest.json` and `method-pairs/manifest.json` record the same source and geometric code hashes, the same centre `[54.5, 54.5]` and EM setup `[512, 384, 984]`.

## What the original run actually produced

| Pair | A strokes | Rotated B strokes | Matched by fusion | Baseline and fusion minimum F1 | Changed images |
| --- | ---: | ---: | ---: | ---: | ---: |
| 甲 ↔ 由 | 5 | 5 | **0** | 0.7347596043248217 | **0/2** |
| 韦 ↔ 芈 | 4 | 7 | **0** | 0.8075962018990505 | **0/2** |

The upright and rotated `method-pairs` PNGs are each **byte-identical** to their `fixed-pairs` simple-union counterpart. These checks use original artifact bytes, not visually judged images or merely equal F1 scores.

| Pair and orientation | Identical PNG SHA-256 |
| --- | --- |
| 甲/由, upright | `86167fdb78c9adfb0a97b9e46921323f0518986d679675db6396626d872b8cf1` |
| 甲/由, rotated | `7a362202012646012bcf3846bac55993f5f32569d8ffe6ba3a86dd9da96ecd29` |
| 韦/芈, upright | `20ecffbb31ac9f19c064d1292bdd4e11eaf34d73a1022abadf5bb84a1a44ccb3` |
| 韦/芈, rotated | `50902ec12cb1230a0fc6b893bd453be979352cd0939e246b68f2fc4df0d197bd` |

## Mechanism and scope of the conclusion

[`code/prc_ab_fusion.py` on PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/blob/exp/ab-fusion/code/prc_ab_fusion.py) performs greedy one-to-one median-spine registration with a default maximum 24-point resampled RMS distance of **4.0 raster units**. `construct()` first builds an A-plus-rotated-B simple union and only constructs blended replacements for registered pairs. When `matched_strokes = 0`, every original stroke remains unmatched. All candidate alphas reconstruct the same union, so neither geometry nor F1 can improve. This is the **observed proximate cause** of the no-op for the two published examples.

This observation **does not prove** that blending fails when a match exists, that an alternative registration distance is appropriate, or that human readers could recognize any constructed ambigram. The selected examples are prior pilot cases, not an independent held-out cohort. The separate VLM experiment's failure to recognize both orientations cannot distinguish a failed blend from a blend that was never activated.

## Independent reproduction from the original artifact

```bash
gh run download 42399361826 -R ClaudioDrews/sinogram-ambigram \
  -n prc-experiment-stimuli -D /tmp/prc-ab-pilot
python - <<'PY'
import json
from pathlib import Path
from hashlib import sha256
root = Path("/tmp/prc-ab-pilot")
simple = json.loads((root / "fixed-pairs/manifest.json").read_text())
fusion = json.loads((root / "method-pairs/manifest.json").read_text())
assert simple["source_sha256"] == fusion["source_sha256"]
for before, after in zip(simple["records"], fusion["records"]):
    assert before["target_a"] == after["target_a"]
    assert before["target_b"] == after["target_b"]
    assert after["info"]["matched_strokes"] == 0
    assert before["metrics"] == after["metrics"]
    for filename in before["images"]:
        b = (root / "fixed-pairs" / filename).read_bytes()
        f = (root / "method-pairs" / filename).read_bytes()
        assert b == f
        print(before["target_a"], before["target_b"], filename, sha256(b).hexdigest())
PY
```

Verify artifact identity, pinned source and commit before drawing conclusions from a regenerated run. Generated PNGs derive from Make Me a Hanzi and carry a separate Arphic Public License; they are not MIT-licensed by the repository.

## Next preregistered diagnostic gate (not yet completed)

1. Freeze a **new** source-defined A/B pair cohort excluding pilot pairs, without inspecting its fusion results.
2. Record nearest-spine RMS distance distributions, match counts per candidate threshold, rejected/accepted blend counts, actual changed pixels, and full paired upright/rotated F1 values.
3. Compare default 4.0 to **predeclared** thresholds on the frozen cohort; ensure a higher threshold does not create semantically arbitrary stroke matches or sacrifice either target.
4. Preserve negative results and only then conduct separately blinded model recognition. Human readability and regional source-form certification remain open questions.

**Conclusion:** the two-pair trial exercised an unmodified union, not an active fusion. This explains **this observed geometric null**, not whether A/B fusion can work in general. No tag, release, or merge of PRs #14–#17 follows from this result.
