# PRC Inventory: Measured Evidence for the Construction Method

**Scope.** Every number below was measured on the PRC inventory, not
estimated. The measurements were produced with the scripts described in
[the method](../theory/prc-construction-method.md); the reproducible parts
ship in [`code/prc_construct.py`](../code/prc_construct.py).

**Source.** MMah `graphics.txt` — 9,574 characters, 9,534 CJK ideographs,
stroke medians and stroke outlines in a 1024 × 1024 space.
Licence: **Arphic Public License** (KaitiM GB and UKai faces),
MIT-compatible. `dictionary.txt` from the same project is **LGPL-3.0** and is
excluded from the MIT core of this repository.

---

## 1. Coverage of the PRC repertoire

| repertoire | covered | total | share |
|---|---|---|---|
| GB 2312-80 | 6,763 | 6,763 | **100%** |
| 通用规范汉字表 一级 (3500 common) | 3,500 | 3,500 | **100%** |
| 通用规范汉字表 二级 (3000 secondary) | 2,871 | 3,000 | 95.7% |
| 通用规范汉字表 三级 (1605 tertiary) | 495 | 1,605 | 30.8% |
| 通用规范汉字表 total | 6,866 | 8,105 | 84.7% |

The em square that contains every GB 2312 glyph was measured directly: the
square of side **984** centred at **(512, 384)** in source coordinates
contains **6,763 / 6,763** GB 2312 glyphs entirely.

## 2. The forms are genuinely PRC, not Japanese

The PRC and Japanese inventories share 5,196 codepoints. On **563** of them
(10.8%) the two forms have a **different number of strokes** — 骨 has 10
strokes in the Japanese form and 9 in the PRC form. The ranking of pairs is
therefore a separate computation on the PRC data and cannot be inherited
from the Japanese results.

## 3. Half-turn symmetry of the PRC forms

Measured on the ink, on a 109 × 109 grid with a chamfer distance transform.
The measure is graded, not binary: a tolerance is fixed and the number of
glyphs whose half-turn distance falls below it is counted.

| tolerance | Japanese (KanjiVG) | PRC (MMah) |
|---|---|---|
| 0.05 | 1 | 0 |
| 0.12 | 40 | 33 |
| **0.18** | **1,086** | **1,420** |
| 0.25 | 2,373 | 4,800 |

At the tolerance of 0.18 the eight known probes 口 田 目 日 一 回 十 中 are all
recovered on both inventories. Above 0.25 the measure degrades.

**The measure has to be taken on the ink.** The same measurement taken on the
skeleton centre-lines produced false negatives for 口, 田, 目, 日 and 回: the
*segmentation* of a form into strokes is not half-turn invariant, even
though the ink is. A vertical wedge stroke and a thin vertical stroke can
carry the same ink and still disagree on the centre-line.

**The best PRC self-candidates are dominated by the 囗 family.** The 40
best by half-turn distance are, in order: 一 圆 口 国 囫 囝 圜 圈 囵 鲁 圉 固
圃 缤 日 匿 铴 令 强 涸 镂 掰 普 丽 囤 惕 耢 霏 囿 髅 圊 绱 舅 囹 濒 灏
蛔 错 潴 潮 — frames, enclosures and simple symmetric forms.

## 4. The rotation centre

### 4.1 On the centre-lines

Measured on the 40 best candidates, the share of the *centre-line* points of
one reading that coincide with the centre-lines of the other:

| | median | 一 | 口 | 国 | 囝 | 日 | 鲁 |
|---|---|---|---|---|---|---|---|
| centre of the em square | 0.245 | 0.000 | 0.382 | 0.339 | 0.474 | 0.529 | 0.245 |
| searched centre | 0.640 | 1.000 | 0.753 | 0.763 | 0.862 | 0.798 | 0.677 |
| gain | **+0.395** | +1.000 | +0.371 | +0.424 | +0.387 | +0.270 | +0.431 |

### 4.2 On the ink

Measured on the 120 best candidates, the share of the *original ink* that
survives the half-turn (a raster measure, the one the published module
uses):

| stage | median | mean gain |
|---|---|---|
| centre of the em square | 0.167 | — |
| centre of the ink | 0.192 | +0.025 |
| searched centre | 0.240 | **+0.093** |
| searched centre + the extremity rules | 0.243 | +0.002 |
| final | 0.252 | **+0.106** total |

Per glyph, the centre alone: 一 0.006 → 0.835, 囗 0.287 → 0.551,
回 0.169 → 0.465, 口 0.147 → 0.392, 国 0.171 → 0.410.

The optimal offset is **+2.5 units in y** for almost every glyph: the source
font places the ideographic square above the geometric centre of the em
square, so the centre of the square is the wrong centre for every PRC form.

**The centre is a larger lever than every extremity rule put together.**
See §9.

## 5. The weight profile of the PRC strokes

Half-width measured as the distance from the median to the nearest outline
point.

| glyph | median weight at the start | median weight at the end | mean end-to-end difference | mean ratio lighter/heavier |
|---|---|---|---|---|
| 一 | 2.09 | 2.55 | 0.46 | 0.82 |
| 口 | 1.85 | 1.82 | 0.30 | 0.86 |
| 国 | 1.56 | 1.79 | 0.33 | 0.85 |
| 囝 | 1.59 | 1.73 | 0.39 | 0.81 |
| 圈 | 1.76 | 1.35 | 0.64 | 0.68 |
| 令 | 1.73 | 1.43 | 0.83 | 0.63 |
| 铴 | 1.69 | 1.21 | 0.78 | 0.59 |

No PRC stroke of this set has a flat profile: the two ends of the same
stroke differ by **14% to 41%** of its weight. This is the wedge: the
vertical of a frame is thick at one end and thin at the other, and the
half-turn maps that gradient onto its counterpart.

## 6. Where the residual error is

With the centre corrected, each sample of the drawing was measured against
the ink of the other reading. The samples were split into the last 6 units
of a stroke (the extremity zone) and the body of the stroke.

| zone | mean error | p90 | share of the samples |
|---|---|---|---|
| extremity | 3.81 | 7.99 | 28% |
| body | 2.67 | 6.13 | 72% |

The extremity zone carries **35.7%** of the error in 28% of the samples.

## 7. How far apart the two readings' extremities are

Distance from every extremity of a drawing to the nearest extremity of the
other reading, over the 40 candidates:

| percentile | 50 | 75 | 90 | 95 | 99 |
|---|---|---|---|---|---|
| all candidates | 7.99 | 12.35 | 20.20 | 26.94 | 38.74 |
| the symmetric ones | 7.81 | 11.82 | 26.45 | 31.85 | 38.75 |

The median fixes the fusion radius **δ_f = 8.0**; the 75th percentile fixes
the contested radius **r_c = 12.4**.

## 8. What the extremity rules are worth

The rules were implemented and run over the 120 candidates:

| quantity | value |
|---|---|
| places (corners where strokes end) measured | 2,065 |
| places with a counterpart under the half-turn | **421** (20%) |
| orphan places | **938** (45%) |
| candidates the rules improve | 53 of 120 |
| candidates the rules make worse | 26 of 120 |
| mean change in symmetric ink | **+0.002** |
| median retention of the original ink | 1.005 |

The rules are almost never enough, because the asymmetry is structural. The
enclosure family draws its top and right sides as one stroke (横折), so the
top-right corner is a bend and not an extremity; turned 180°, the
bottom-left corner of the frame is an extremity of two strokes. The two
orientations do not agree on how many strokes they see, and re-weighting
the ends cannot repair that. Splitting the stroke at the corner (R-STRUCT)
gives both orientations the same extremity structure; it is necessary and
it is not sufficient.

The discriminator between the two groups of rotatable ideograms is
therefore **whether the half-turn maps the stroke decomposition onto
itself**, not the number of strokes and not the weight gradient.

## 9. Sector-wise thickness manipulation

The ideograms above are dominated by the enclosure family, where the frame
decides everything. This section measures the other half of the inventory:
the **frameless** forms, where nothing encloses anything and the asymmetry
has to be absorbed by the weight of the strokes.

**The selection.** "Median candidates" = the interquartile band of the
measured symmetric-ink distribution (0.225–0.361). "Frameless" = the ink
does not enclose any region of its own bounding box. The frame test is
geometric, not a radical lookup: the raster is closed by two cells (a
tilted frame leaves a gap at the corner where two strokes meet), the
background is flooded from the border of the canvas, and whatever the flood
cannot reach is enclosed. It separates 囗 (0.58), 国 (0.44), 回 (0.39),
口 (0.40), 日 (0.45) from 令 (0.00), 普 (0.08), 告 (0.05), 昔 (0.08). It
also catches the forms that *contain* an enclosure — 涸 (0.25), 吕 (0.26),
崮 (0.26) — because they have one somewhere in the character. A perimeter
test does not work: a tilted frame touches its own bounding box only at the
corners.

Of the 120 measured candidates, **29 have a frame** and 91 do not; 53 of the
frameless ones fall in the median band.

**The manipulation.** The box is divided in a 3 × 3 grid of sectors. The
half-turn maps sector (i, j) onto (2 − i, 2 − j). Each sector carries a
thickness multiplier, and the half-width of every stroke sample is scaled by
the local multiplier. The field is a normalised convolution, so the
multiplier is exact in the interior of a sector and blends at the borders.

**The score.** `sym = |D ∩ R(D)| / |D|`, subject to two constraints that
keep the result honest: at most 10% of the original ink may be erased and
at most 30% of ink may be added. Without them the score is gameable — a
drawing can always be made symmetric by deleting what is not, and always
made "symmetric" by flooding the box.

### Six representatives

| ideogram | strokes | base | rule | search | retention | growth |
|---|---|---|---|---|---|---|
| 令 | 5 | 0.318 | 0.350 | 0.409 | 0.910 | 1.14 |
| 告 | 7 | 0.350 | 0.360 | 0.439 | 0.962 | 1.17 |
| 昔 | 8 | 0.329 | 0.330 | 0.410 | 0.924 | 1.25 |
| 普 | 12 | 0.250 | 0.311 | 0.340 | 0.998 | 1.30 |
| 匿 | 10 | 0.332 | 0.351 | 0.386 | 1.000 | 1.30 |
| 阗 | 13 | 0.351 | 0.377 | 0.451 | 0.977 | 1.30 |
| **median** | | **0.331** | **0.350** | **0.409** | | |

The **rule** thickens the lighter of each pair of opposite sectors until the
pair carries the same ink. It only ever adds ink, and it is capped at 1.40.
The **search** is a greedy coordinate descent over the nine multipliers and
may also thin.

What the multipliers reveal is the interesting part. For 令, 告, 昔 and 普
the imbalanced pair is the top-middle against the middle-left. For 匿 the
right-hand column — the 若 inside the 匚 — carries less ink than the left,
and the rule thickens that column. The rule is **discovering the asymmetric
component of the character and compensating it with weight**, which is what
a human calligrapher does.

### Generalisation over the whole frameless median band

53 ideograms, the rule only:

| | value |
|---|---|
| base, median | 0.240 |
| after R-SECT, median | 0.266 |
| median gain | **+0.023** |
| mean gain | **+0.030** |
| improve / worsen | **52 / 1** of 53 |
| median retention | 1.000 |

Largest gains: 匈 0.180 → 0.296 (+0.115), 罱 0.198 → 0.279 (+0.081),
匆 0.202 → 0.279 (+0.077). The correlation between the gain and
the stroke count is **-0.17**: the lever does not depend on how many
strokes the character has.

### Compared with the extremity rules

| lever | median gain on the 120 candidates | note |
|---|---|---|
| rotation centre | **+0.093** | the largest lever of all |
| extremity rules (§8 of the method) | +0.002 | most places have no counterpart |
| sector thickness (this section) | **+0.023** median, **+0.030** mean, 52/53 improve | on the frameless forms |

## 10. What was not measured

* No reader evidence. The perceptual pilot for the PRC inventory does not
  exist; the instrument is specified but not administered.
* No licence closure for `cjkvi-variants`, for the CHISE-IDS subset, for
  the Unihan version pin, for the transcription of the 通用规范汉字表 or for
  the PRC stroke-order standard.
* The merge of two *different* PRC forms (which stroke of `a` answers to
  which stroke of `b`) is not implemented; only the self-rotation case is.
* The sector manipulation was measured on 60 ideograms, not on the whole
  PRC inventory, and on one 3 × 3 grid; a finer grid was not tried.
* Whether a thickened 氵 reads *better* to a reader is not measured: the
  score is geometric.
* The constants were measured on one font. A second PRC face (UKai) will
  give different numbers.