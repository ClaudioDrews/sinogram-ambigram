# Candidate discovery, construction and evaluation

This page describes a **descending research workflow**: test inexpensive hypotheses first, keep successful mechanisms, and apply more expensive transformations only when necessary. Methods below are proposals unless marked **implemented**; they should not be interpreted as demonstrated human-readable ambigrams.

## 1. Discover rotational candidates

| Method | What to compute | State |
| --- | --- | --- |
| **180° geometric rotation graph** | Rank glyph pairs by distance between the first glyph's stroke skeleton and the rotated second skeleton, using grid screening followed by exact refinement. | **Implemented:** 2,770-character KanjiVG inventory and 5,180 refined pairs |
| **Rotational self-symmetry C₂** | Rank `A` against its own 180°-rotated structure; look for stable strokes and distinctive exceptions. | **Implemented:** 2,770 self-pairs |
| **IDS decomposition** | Parse character component trees; reverse the order of components under rotation and apply enclosure-specific transformations. | Algebra explored; corpus-level verified rewrite not implemented |
| **Alternative geometric descriptors** | Combine local stroke relationships, boundary profiles, skeleton topology and coarse ink distribution. | Proposed; earlier pilots tested several incompatible metrics |
| **Semantic alternatives** | When no direct candidate succeeds, replace the intended meaning with a related character, with explicit sense and language. | Small manually curated browser fallback; dictionary-wide lookup not implemented |

A low distance is **evidence of geometric proximity**, not proof of legibility. Grid and refined distances are not interchangeable; see [dataset guide](../data/README.md).

## 2. Construct a shared drawing

Let `A` and `B` be stroke representations and `R(B)` the second rotated by 180°. Explore a shared drawing `g`:

1. **Stroke-salience fusion (implemented experimentally):** overlay `A` and `R(B)`; increase weight of nearby/shared strokes while reducing the prominence of unmatched ones. See [Python implementation](../code/make_ambigram.py) and [browser prototype](../generator/).
2. **Component assignment (proposed):** minimise a cost such as `Σ D(cᵢ, R(c_{σ(i)})) + λ L_layout` over component correspondences, especially for repeated subcomponents.
3. **Enclosure-preserving edits (proposed):** keep robust outer frames stable and modify internal components, with topology and legibility constraints.
4. **Bounded deformation (proposed):** use differentiable Bézier curves, thin-plate splines or a signed-distance field to minimise fidelity error to both views while penalising curvature, self-crossing and changes to stroke grammar.
5. **Program synthesis (proposed):** search short sequences of interpretable operations (move, bend, merge, split, resize, thicken, reconnect) and cluster successful sequences into character-family rules.

The work of [Inoue and Takahashi (2020)](inoue-takahashi-2020.md) offers a peer-reviewed hiragana-specific structural method; its results cannot simply be transferred to complex kanji without additional component-level matching.

## 3. Rank and validate

Evaluation must separate three properties:

- **Shape proximity:** geometric metrics (Hausdorff, Chamfer, dilated IoU), with density and enclosure-bias diagnostics.
- **Readable meaning:** independent human judgments in both orientations, with the intended reading hidden. A controlled native-reader study remains unperformed.
- **Visual quality:** stroke continuity, type style, deformation cost and subjective visual appeal.

The proposed next empirical study is to choose a balanced set of candidates and negative controls, obtain blinded readings from native Chinese/Japanese readers, then estimate reading accuracy and confidence by character pair and rendering method. A recogniser can help shortlist candidates but should not substitute for human testing.

## 4. Iterative research order

```text
Pinned glyph inventory and reproducible geometry
    ↓
Geometric and C₂ candidates (implemented)
    ↓
IDS/component filters and known character-family rules
    ↓
Stroke-salience composite (experimental implementation)
    ↓
Bounded deformation and program synthesis (proposed)
    ↓
Blind perception study and error analysis (not yet performed)
    ↓
Calibrated, generalisable generation model (long-term goal)
```

Preserve negative results and contradictory measurements; do not merge score scales across fonts or experimental setups. For the reproducible geometric core, see [rotation-graph method](rotgraph-method.md); for limitations, see [findings](../findings/limitations.md).
