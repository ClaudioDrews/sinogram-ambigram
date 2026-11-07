# Human evaluation protocol

> **Status: protocol only. No study has been run.** Nothing in this repository
> has been validated by human readers. This document specifies how such a
> study should be run so that its results are interpretable and its decision
> rules are fixed before the data are seen.

The design adapts the study by Inoue and Takahashi (2020), *"Automatic
Creation of Ambigrams"*, which is the only peer-reviewed human evaluation in
this area that the project has access to. That paper evaluated 46 hiragana
with 1,081 candidate pairs and 18 raters, and reported the proportion of pairs
that raters could read. This project differs in one crucial respect: the
object of evaluation is a **constructed drawing**, not a pair of characters.

## 1. Hypotheses

- **H1 (geometric validity).** A construction whose half-turn distance falls
  in the best stratum is more often read correctly than a random-pair control.
- **H2 (metric value).** The de-biased ranking (per-glyph z-score plus optimal
  rotation centre, `data/v2/`) selects constructions that are read at least as
  often as those selected by the v1 raw-distance ranking.
- **H3 (shared core).** Constructions whose two readings share most of their
  strokes are read more often than those whose readings barely overlap.
- **H4 (aesthetics).** Legibility and aesthetic rating are related but not
  identical; a construction can be readable and unappealing, or attractive and
  illegible.

H1 and H2 are the hypotheses the pilot (F0.5) tests. H3 and H4 are addressed
in the full study (F4).

## 2. Unit of analysis

**One construction.** A construction is a single generated drawing plus the
pair of characters it is intended to be read as. Raters judge the drawing; the
pair is metadata used for analysis and is never shown during judging.

The score of one construction is

```
L_item = min( median_ratings(reading A), median_ratings(reading B) )
```

where each median is taken across raters for one reading. The **minimum** is
deliberate: an ambigram needs *both* readings to work, so the weaker reading
limits the construction. Using the mean would let a strong reading mask a
failed one.

> **Note on the deflation this implies.** Taking the minimum of two medians
> biases `L_item` below the per-reading median by roughly 0.3 Likert points at
> 8 raters. Any absolute threshold applied to `L_item` must account for that;
> see §7.

## 3. Materials

Each item consists of:

1. the construction, rendered as an SVG, with a control that rotates it by
   180°;
2. the two reference characters, shown separately as plain text (not as
   images, to avoid cueing the glyph shapes);
3. two Likert scales, one per reading, plus an aesthetic scale.

### Scales

| Scale | Range | Question |
|---|---|---|
| Legibility A | 1–7 | "How clearly does this drawing read as the character shown?" |
| Legibility B | 1–7 | Same, for the rotated reading |
| Aesthetic | 1–7 | "How appealing is this drawing as an image?" |
| Confidence | 1–5 | "How sure are you of your reading?" |

Anchors are given at 1 ("not readable at all") and 7 ("immediately readable").
Raters may leave a legibility score blank if they cannot identify either
character; a blank is recorded as a failure to read, not as a missing datum.

### Controls

| Control type | Purpose |
|---|---|
| **Negative** | Pairs of unrelated characters drawn with the same construction method, matched by stroke count. Tests whether the method produces readable results by accident. |
| **Positive anchor** | Constructions the geometry already ranks highly. Tests whether the instrument is sensitive enough to detect known-good material. |

Negative controls are matched by stroke count so that they cannot be
distinguished from the real items by complexity alone.

## 4. Sampling

The pilot draws from the **v2 ranking**, because Gate A publishes the v2
ranking and a pilot that only examined v1 pairs would not evidence what will
be shown. Items are stratified:

| Stratum | Count | Content |
|---|---|---|
| v1-top | 12 | Best distinct pairs of the v1 raw-distance ranking |
| v2-top | 14 | Best distinct pairs of the v2 z-score ranking, **disjoint** from v1-top |
| Self-rotation | 8 | Strong C₂ glyphs (目, 回 and similar) |
| Negative control | 14 | Unrelated pairs, stroke-count matched, fixed seed |

**48 items, not 30.** The original pilot design of 30 items is under-powered
for the difference the decision rule asks about; see §7. The v2-top stratum is
disjoint from v1-top so that the two rankings are compared on different
material rather than on the same easy pairs.

The v2-top and control strata are the two the decision rule compares, so they
are the two that were grown. Splitting the remaining eight items evenly
between them gives 14 each; the simulated GO probability rises from 0.58 for a
40-item design to 0.66, while a design with more items in one stratum than the
other is no better (§7.4).

Raters see a **randomised order** of all items, different for every rater.
The stratum, the geometric score and the z-score are never shown. The
stratum label appears only in the exported data.

## 5. Procedure

1. Rater opens the evaluation page and reads the consent statement.
2. Rater answers three screening questions: native language, reading
   proficiency, age band. No other personal data is collected.
3. Rater works through the randomised items.
4. Rater may rotate any item, as often as needed.
5. At the end the rater may submit comments. Comments are stored verbatim and
   are reported in aggregate; they are not analysed as claims.
6. The page exports a JSON/CSV file that the rater sends to the maintainer.

The evaluation runs on a static page with no server. No network request
carries any response, and no identifier is generated.

## 6. Analysis

Reported descriptively. With the pilot's sample size no significance claim is
made.

- **Per item**: median `L_item`, the distribution of legibility scores for
  both readings, and the number of raters who failed to read it.
- **Per group**: median `L_group` (median of `L_item` within the stratum),
  with the interquartile range.
- **Between groups**:
  - **Cliff's delta** between the v2-top and control item sets, with the
    interpretation band.
  - **Mann–Whitney U**, one-sided, exact p-value by enumeration.
  - The same two statistics for v1-top against controls, as the comparison
    the hypothesis needs.
- **Descriptive cross-check**: Spearman correlation between a construction's
  percentile-z and its `L_item`, over all items.

## 7. Decision rules

These are fixed before the pilot's data exist. They may be revised by the
maintainer before the pilot runs, but not after seeing results.

### 7.1 Why the rule uses rank statistics, not a median gap

An earlier draft of this protocol decided the pilot on the difference between
two group medians:

```
GO if  L_group(v2-top) >= 4  and  L_group(v2-top) - L_group(controls) >= 1.0
```

The protocol's power claims are produced by `code/test_pilot_power.py`, which
simulates the whole design and prints the table below. The model is stated in
full in that script's docstring: each item has a latent readability, the
`v2-top` items are one Likert point above the controls, every rater scores
every item with a rating standard deviation of 1.3, `L_item` is the median of
one item's ratings and `L_group` the median of a stratum's `L_item` values.

On the original 30-item design (8 raters, 9 v2-top items, 6 controls, Likert
standard deviation 1.3) it gives:

| Gate | Probability under a true difference of 1.0 Likert point |
|---|---|
| `L_group(v2-top) >= 4` | 1.00 |
| `L_group(v2-top) - L_group(controls) >= 1.0` | 0.65 |
| Both (the rule as drafted) | **0.56** |
| One-sided exact Mann–Whitney, p < 0.05, same data | **0.57** |

The absolute gate is never the problem; the *gap between medians* is. The
median of six control items is a coarse statistic, and taking the minimum of
two medians per item compounds the coarseness. The rank-based test the
protocol already specifies uses the full item-level information and is far
more sensitive on the adopted design (§7.4).

Raising the number of raters does not fix this: on the 48-item design the
rule's power moves only from 0.66 (8 raters) to 0.66 (12 raters). Raising the
number of **items per stratum** does.

### 7.2 The rule as adopted

> **GO** if, for the v2-top stratum against the negative controls:
> - the one-sided exact Mann–Whitney U test gives `p < 0.05`, **and**
> - Cliff's delta is at least 0.33 (a "medium" effect), **and**
> - `L_group(v2-top)` exceeds `L_group(controls)` by at least 1.0 Likert
>   point.
>
> **NO-GO** if the v2-top stratum is not distinguishable from the controls by
> any of the three criteria. A geometric method that produces nothing
> distinguishable from random pairs does not support a perceptual claim.
>
> **ESCALATE** (adjust the construction method, not the metric) if:
> - the v2-top stratum is distinguishable from controls but
>   `L_group(v2-top) < L_group(v1-top) - 0.5`, meaning the de-biasing made
>   perception worse; or
> - `L_group(v2-top) < 4`, meaning that even the best-ranked constructions are
>   not comfortably readable and the problem lies in the construction method
>   rather than in the ranking.

The three criteria in the GO branch are deliberately redundant: the
statistical test, the effect size and the practically meaningful gap must all
be satisfied. A significant result with a negligible effect is not a GO.

### 7.3 What this rule cannot establish

A GO means the v2 ranking selects constructions that native readers can read
more often than random-pair controls. It does **not** establish that any
particular construction is a good ambigram, and it does not calibrate ε for
the whole inventory. Those are the full study's business (§8).

### 7.4 What the pilot can and cannot detect

On the adopted 48-item design with 8 raters, the probability that the rule
reaches GO is:

| True difference (Likert points) | 0.5 | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|
| Probability of GO | 0.21 | 0.66 | 0.94 | 1.00 |

A pilot that reaches NO-GO therefore does not establish that the method
produces nothing readable: with a true difference of half a Likert point the
rule would miss it four times out of five. What NO-GO does establish is that
the constructions are not distinguishable from random pairs by a margin the
project can rely on, which is what the rule is for. The pilot is a risk check
on the *construction method*, and its resolution is deliberately limited.

Reproduce the table with:

```bash
python code/test_pilot_power.py
```

## 8. The full study

The pilot is a risk check, not a publication. The full study (F4) differs in:

- **Size**: at least 15 complete respondents per group, for Japanese,
  Simplified Chinese and Traditional Chinese.
- **Items**: stratified by score, with negative controls and anchors, drawn
  from the calibrated v3 ranking.
- **Scope**: legibility, aesthetics and cultural appropriateness, with the
  cultural scale reported against the same negative-control baseline.
- **Output**: the mapping from geometric score to probability of correct
  reading, a logistic curve per complexity class, and the replacement of the
  heuristic thresholds in the engine with calibrated ones.

The study is pre-registered before it runs (OSF), and the analysis plan is
fixed in advance.

## 9. Ethics and consent

- Participation is voluntary and may be abandoned at any point.
- Only three screening answers are collected: native language, reading
  proficiency, age band. No names, no contact details, no device identifiers.
- The consent statement is given in English and Japanese for the pilot, and
  in all three study languages for the full study.
- Responses are anonymised before analysis: each respondent gets a random
  identifier, and the mapping is held only by the maintainer.
- Findings are reported in aggregate. Individual verbatim comments are quoted
  only with the participant's explicit permission.
- The page collects nothing automatically and sends nothing anywhere.

## 10. Limitations of this protocol

- The scales are subjective and the instrument is unvalidated.
- Raters are self-selected, so they are not a random sample of readers.
- The pilot's design can detect a large effect but not a small one; a NO-GO
  result is informative, a GO result is weaker evidence than the full study
  will provide.
- The construction method itself is experimental. A low legibility score
  cannot distinguish "the metric ranked the wrong pair" from "the drawing
  method is the problem". The decision rule separates these two cases, but
  only coarsely.

## 11. Related

- [`findings/limitations.md`](../findings/limitations.md) — what the research does not establish
- [`findings/anchors.txt`](../findings/anchors.txt) — the frozen anchor set and its decision rule
- [`methods/rotgraph-method.md`](rotgraph-method.md) — how the geometry is computed
- [`theory/existence-criterion.md`](../theory/existence-criterion.md) — the formal model the protocol tests
- [`methods/inoue-takahashi-2020.md`](inoue-takahashi-2020.md) — the study this design adapts