# Known biases in the rotation graph

> **Status:** measured on the published v1 dataset and on the v2 normalised
> dataset. Every number below was computed from the data in this repository;
> the commands that produce them are in `methods/rotgraph-method.md`.

The ranking in `data/rotation_pairs.csv` is a **geometric** ranking, and it is
not free of systematic distortions. This document states the biases that were
measured, how large they are, and what the v2 normalisation does about them.

The biases are not defects of the implementation. They are properties of
comparing raw distances between glyphs of very different sizes and shapes.

---

## 1. Density bias

**What it is.** A glyph with many strokes fills more of the character box, so
it sits closer to more of its potential partners. Raw distance therefore
rewards dense glyphs, regardless of how well the pairing actually works.

**Measured (v1, exact distances, 2,770 self-pairs).**

| Quantity | Value |
|---|---|
| Spearman ρ between Hausdorff distance and stroke count | **−0.419** |
| Mean H for glyphs with 1–6 strokes | 0.1891 |
| Mean H for glyphs with 20+ strokes | 0.1328 |

The independent review recorded ρ = −0.43; the small difference is a
rounding artefact of the rank computation, not a disagreement.

**Consequence.** A 21-stroke glyph such as 鰯 sits at H = 0.0751 as a
self-rotation, ahead of 回 at 0.06971, and both are ahead of much simpler
glyphs that a reader would probably find more stable. The review recorded
this as finding CR2: in the C₂ class the order is 目, 日, 一, 田, 口, 回, 菫,
鰯, 圃, 圏 — the last four are structurally implausible as self-rotations
precisely because they are dense.

**What v2 does.** Each glyph gets its own null distribution, estimated from 30
randomly drawn partners of similar stroke count. A pair is then scored by how
unusually good it is *for the characters involved*, not by raw distance. See
`data/v2/null_model.csv`.

---

## 2. Hub bias

**What it is.** A small number of glyphs appear in a disproportionate number
of good pairs. They act as attractors, and a ranking built on raw distance
repeats them rather than discovering new structure.

**Measured (v1, exact distances, all 2,410 distinct refined pairs).**

| Character | Degree in the distinct-pair graph |
|---|---|
| 圃 | 159 |
| 国 | 85 |
| 商 | 71 |
| 圏 | 69 |
| 困 | 60 |
| 亜 | 58 |
| 園 | 53 |

圃 appears in **7 of the first 25** distinct pairs, as recorded in the conflict
register (X7). The review measured a lower degree on the grid metric over the
top 1,000 and a different denominator again in its own re-run; the three
figures are not comparable because they use different pair sets, but they
agree on the identity of the hubs.

**What v2 does.** Because the null model is per glyph, a hub no longer gains
from being close to everything. Its own null distribution accounts for that.
The concentration of degree before and after normalisation is reported in
`findings/debias-report.md`.

---

## 3. Fixed rotation centre

**What it is.** Every distance in v1 is computed with the partner rotated
about the centre of the 109 × 109 character box, `R(p) = 109 − p`. Two glyphs
that would match slightly better under a different centre are penalised.

**Measured.** The review reported this as finding CR3 and noted that it was
absent from the method document's own list of limits. The review's
hypothetical alignment gave 十 0.115 → 0.070 and 中 0.110 → 0.084; the
current values are 0.11498 and 0.10988.

**What v2 does.** The optimal rotation centre is searched on a fixed grid of
9 × 9 centres around the box centre (step 1.5 units), which is equivalent to
searching a translation of the half-turned partner. No other degree of
freedom is added. See `data/v2/optimal_centres.csv`.

---

## 4. Enclosure bias

**What it is.** A glyph drawn inside a frame (囗 and its relatives) contributes
a large number of sampled points along the frame. The skeleton metric then
measures how well two frames align, which is easy, and says little about the
interior.

**Observed.** 圃, 園, 圏, 菌 and 国 are among the hubs in section 2, and 圃
and 園 hold two of the three best distinct-pair slots in the v1 ranking.

**Status.** Not corrected by the v2 normalisation, which addresses density
and hub concentration but not the fact that a skeleton metric cannot see
whether the *interiors* match. The proposed remedy — an ink-area metric
rather than a skeleton metric — is out of scope for v2 and remains an open
item.

---

## 5. Scale ambiguity

**What it is.** The repository publishes two scales of the same quantity.
`data/rotation_pairs.csv` and `data/c2_class.csv` hold **exact point-cloud**
distances; `data/rotation_pairs_top5000.csv` holds **grid distance-transform**
approximations. The two are not interchangeable and their thresholds are not
the same.

**Status.** Structural, not an error, and recorded as X8 in the conflict
register. It is handled by naming: `data/README.md` states which file uses
which scale, and the v2 export uses explicit `*_grid` column names so that no
file can be mistaken for an exact measurement.

---

## 6. What is *not* a bias

For completeness, these are properties of the metric that are often mistaken
for distortions:

- **One shape per glyph.** KanjiVG provides one canonical form. Real
  perceptual tolerance includes typeface, handwriting and stroke weight. The
  dispersion across the KanjiVG font variants has not been measured.
- **Glyph level, not word level.** Rotating a word reverses its order as well
  as each glyph.
- **180° only.** 90° rotation, mirroring and figure–ground inversion are out
  of scope. A mirror pair is not a rotational ambigram, and the v1 ranking
  contains no explicit mirror filter beyond the geometry itself.
- **Geometry is not legibility.** None of the above changes the fact that a
  high score means "these strokes align after a half-turn", not "a reader can
  read it". No native-reader validation has been published.

---

## Related

- [`findings/debias-report.md`](debias-report.md) — before/after measurements and the anchor decision
- [`findings/limitations.md`](limitations.md) — the full limitations list
- [`findings/conflicts-and-corrections.md`](conflicts-and-corrections.md) — the conflict register, including CR1–CR7 and X1–X8
- [`findings/anchors.txt`](anchors.txt) — the frozen anchor set and its decision rule
- [`data/README.md`](../data/README.md) — dataset contents and metric provenance