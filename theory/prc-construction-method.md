# The PRC Construction Method: Reconciling the Extremities

**Evidence basis:** the constants below are measured on the PRC inventory
(MMah `graphics.txt`, Arphic Public License) over the GB2312 set; the rules
are implemented in [`code/prc_construct.py`](../code/prc_construct.py) and
covered by [`code/test_prc_construct.py`](../code/test_prc_construct.py).

> **Evidence boundary:** nothing in this document certifies that a drawing is
> readable. Legibility is perceptual and this project has no reader evidence
> for the PRC inventory yet (see [SCOPE.md](../SCOPE.md) and
[findings/limitations.md](../findings/limitations.md)). Every drawing
> produced here is a **candidate** (候选图形). The measurements say how well
> the ink agrees with itself under a half-turn; they say nothing about
> whether a reader would accept it.

---

## 1. Why the PRC inventory needs its own method

The Japanese pipeline works on **skeletons**: KanjiVG provides stroke
outlines, the skeleton is extracted, and the pair search runs on the
centre-lines. The PRC source is different. MMah's `graphics.txt` carries
**stroke medians** — the medial axis of each stroke — together with the
outlines. Two consequences follow.

1. **The centre-line is the right object.** A PRC form is written as a
   sequence of strokes; the median is the spine of the stroke and the ink
   around it is the stroke's *weight*. The construction questions are
   therefore questions about weight, direction and extent at the ends of the
   spines.

2. **The ink is not half-turn invariant, even when the centre-line is.** A
   frame such as 田 has a left vertical that is a wedge and a right vertical
   that is thin; the half-turn maps the wedge onto the thin stroke. The
   skeleton says the frame is symmetric, the ink says it is not. Measuring
   symmetry on the ink rather than on the centre-line is what makes the
   frame family visible at all — the centre-line measure produced false
   negatives for 口, 田, 目, 日 and 回.

## 2. The measurement that decides everything: the rotation centre

A half-turn about a centre `c` is `R_c(p) = 2c − p`. On a 109 × 109 grid,
moving the centre by `d` translates the half-turned glyph by `2d`. The
centre is therefore a **translation** parameter, and the project already
searches it for the Japanese set ([stage 8](../code/stage8_optimal_center.py)).

On the PRC data this parameter turns out to dominate everything else.

**Measured.** The measure is the **symmetric ink**: the share of the
*original* ink that survives the half-turn, measured on a 109 × 109 raster.
Measuring against the original and not against the edited drawing is what
stops a rule from winning by erasing — see §7.

Over the 120 best PRC candidates:

| stage | median | mean gain |
|---|---|---|
| centre of the em square | 0.167 | — |
| centre of the ink (centroid of the medians) | 0.192 | +0.025 |
| searched centre | 0.240 | **+0.093** |
| searched centre + the extremity rules | 0.243 | +0.002 |
| final | 0.252 | **+0.106** total |

Per glyph, the centre alone:

| glyph | centre of the em square | searched centre | gain |
|---|---|---|---|
| 一 | 0.006 | 0.835 | +0.829 |
| 囗 | 0.287 | 0.551 | +0.264 |
| 垂 | 0.381 | 0.482 | +0.101 |
| 团 | 0.310 | 0.479 | +0.169 |
| 囝 | 0.319 | 0.475 | +0.156 |
| 回 | 0.169 | 0.463 | +0.294 |
| 圃 | 0.417 | 0.460 | +0.043 |
| 国 | 0.171 | 0.410 | +0.239 |
| 囿 | 0.328 | 0.435 | +0.107 |
| 口 | 0.147 | 0.392 | +0.245 |

The optimal offset is **systematically +2.5 units in y** (2.3% of the box
side) for almost every glyph. The source font places the ideographic square
above the geometric centre of the em square, so the centre of the em square
is the wrong centre for every PRC form. **Rule R0**: rotate about the ink
centre, not about the centre of the square.

**This is the largest single lever in the whole method, and it is larger
than every extremity rule put together.** The centre alone is worth +0.093
of symmetric ink; the extremity rules are worth +0.002.

$$
c^* = \arg\min_{c \in \mathcal{C}} \sum_{p \in P(A)} d\bigl(p, R_c(A)\bigr),
\qquad \mathcal{C} = c_{box} + \{-8,\ldots,+8\}
$$

with `c_box` the centre of the em square. A cheap and accurate surrogate is
the centroid of the medians, refined on a ±1.5-unit grid.

## 3. The geometry of an extremity

Every stroke has two extremities. An extremity carries:

* a **place** — a point; several extremities of different strokes can share
  it (the horizontal and the vertical both end at a frame corner);
* a **weight** — the half-width of the stroke there, measured as the distance
  from the median to the nearest outline point;
* a **direction** — the tangent of the spine at that end.

**Measured.** The half-width profile of the PRC strokes is not flat. The two
ends of the same stroke differ by a median of **0.30 to 0.83 box units**
while the median weight of a stroke is 1.36 to 2.09 units. The ratio of the
lighter end to the heavier end, averaged over the strokes of a glyph, lies
between **0.59 and 0.86**. In other words, a PRC stroke carries a systematic
weight gradient along its length, and the half-turn maps the heavy end of a
stroke onto the light end of its counterpart.

**Measured — where the residual error lives.** With the centre corrected,
the error of each sample of the drawing (its distance to the ink of the
other reading) splits into two zones, the last 6 units of a stroke (the
extremity zone) and the body of the stroke:

| zone | mean error | share of the samples |
|---|---|---|
| extremity (last 6 units) | 3.81 | 28% |
| body of the stroke | 2.67 | 72% |

The extremity zone carries **35.7%** of the residual error in 28% of the
samples: a concentration of 1.28× in the error and 1.43× in the mean error
per sample. The extremities are not where most of the error is, but they
are where the error is *most concentrated*, and they are the only place
where the two readings can be reconciled by a local edit.

**Measured — how far apart the two readings' extremities are.** For every
extremity of a drawing, the distance to the nearest extremity of the
other reading:

| percentile | 50 | 75 | 90 | 95 | 99 |
|---|---|---|---|---|---|
| distance (box units) | 7.99 | 12.35 | 20.20 | 26.94 | 38.74 |

This distribution fixes the two radii the rules need:

* **δ_f = 8.0** — the fusion radius. Two extremities closer than this are
  the same place seen from the two readings.
* **r_c = 12.4** — the contested radius. Beyond this the two readings are
  not fighting over the same ink any more.

## 4. The rules

Let `A` be a drawing, `c` its rotation centre, `P` the set of places it
occupies, and `R = R_c` the half-turn.

### R0 — the centre

Rotate about `c*` (§2). This is a translation of the half-turned glyph and
changes nothing else.

### R1 — equalise the weight of the rotation-matched places

For a place `P` whose half-turn image `R(P)` falls on another place `Q`
(`‖R(P) − Q‖ ≤ δ_f`), the two places carry the same weight:

$$
w^*(P) = w^*(Q) = \max\bigl(w(P),\, w(Q)\bigr),
\qquad
w_{new}(t) = w(t) + \bigl(w^* - w(t)\bigr)\,\psi\!\left(\frac{s(t)}{\kappa}\right)
$$

with `s(t)` the arc distance from the extremity and the taper profile

$$
\psi(u) = (1-u)^2 \;\text{ for } 0 \le u \le 1, \qquad \psi(u) = 0 \text{ otherwise}.
$$

The heavier place is left alone and the lighter one is thickened. `κ = 6`
units: the thickening is spread over the last 6 units of the stroke, which
is the terminal zone used in §3.

### R2 — the direction of an extremity

The half-turn reverses a tangent, so the two ends of a rotation-matched pair
must face opposite ways. The deviation is measured, not corrected:

$$
\Delta\theta = \Bigl| \arg\bigl(\tan Q\bigr) - \arg\bigl(-\tan P\bigr) \Bigr|
$$

This is where the PRC forms fail most visibly: a hook (亅, 乚, 乙) or a
wedge-ended vertical that is exclusive to one reading points the wrong way
once the drawing is turned. **R2 is the rule with the least support in this
document**: the measurement of the deviation exists, the correction does
not. [PLAN]

### R3 — R-STRUCT: split the stroke at the corner

When the half-turn image of a place `P` falls on the **body** of a stroke
rather than on one of its extremities, the two orientations do not agree on
the drawing's extremity structure, and no re-weighting can repair it. The
repair is to **split** the stroke at `P`, so that `P` becomes an extremity
in both orientations:

$$
\text{stroke} \;\longrightarrow\; \bigl(\text{median}[0 \ldots j],\; \text{median}[j \ldots]\bigr),
\qquad \text{median}[j] \leftarrow P
$$

The ink is unchanged; only the way the strokes are counted changes. This
matters for the PRC reading: the enclosure 囗 draws its top and right sides
as one stroke (横折), so splitting it turns 口 from three strokes into four
and 囗 from three into four, against the stroke-order convention. The
construction accepts that cost because the ambigram is judged on the ink.

The alternative — trimming the stroke back to `P` — destroys the part of
the stroke that lies between its end and `P`. It was implemented first and
measured: it loses more ink than it gains.

If the image falls further than the orphan tolerance (2 units) from any
stroke, the place is an **orphan**: the drawing has a corner in one
orientation that does not exist in the other, and no local edit can fix it.
Orphans are the honest boundary of the method. [MEASURED]

### R4 — frame closure

For a 囗-family form the frame is the dominant structure, and its centre
must coincide with `c*`. The frame's own centre is measurable from the
membership of the four frame strokes; when it differs from `c*` by `Δ`,
either `c*` moves to the frame centre or the frame group is displaced by
`Δ`. On the measured data this single correction is worth up to **+0.24**
of symmetric ink (国: 0.171 → 0.410 on the raster measure, 0.339 → 0.763 on
the centre-line measure). [MEASURED]

### R5 — stroke-count reconciliation

Two readings can need a different number of independent strokes. A stroke
that has no counterpart in the other reading must either be fused into a
neighbour — its weight ramped to zero over `κ` — or trimmed to a stub, or
the two readings will not agree on how many strokes they see. The PRC forms
make this acute: 563 of the 5,196 codepoints shared with the Japanese
inventory differ in stroke count (10.8%), 骨 among them (10 strokes in the
Japanese form, 9 in the PRC form). [MEASURED for the data; the rule itself
is [PLAN]]

## 5. The objective

The rules above are applied to minimise a single objective over the free
parameters — the centre `c`, the terminal weights `w(τ)` and the terminal
positions `p(τ)`:

$$
E(c, w, p) = \alpha\,\bigl(1 - \mu(A,B)\bigr) + \beta\,\bigl(1 - \pi(A,B)\bigr)
+ \gamma \sum_{\tau} c(\tau) + \rho \sum_{\tau} \mathbb{1}[\tau \text{ orphan}]
$$

subject to the constraint that **no reading loses more than 20% of its ink
weight**:

$$
\sum_{s \in \text{strokes}(X)} \int w_s(t)\,\lVert s'(t) \rVert \, dt
\;\ge\; 0.8 \sum_{s \in \text{strokes}(X_0)} \int w_s^{(0)}(t)\,\lVert s'(t) \rVert \, dt,
\qquad X \in \{A, B\}
$$

where `μ` is the ink overlap, `π` the share of places that are
rotation-matched, `c(τ)` the contested flag of an extremity and `X₀` the
original drawing. The weights `α, β, γ, ρ` are not calibrated: no reader
evidence exists for the PRC inventory, so the objective is used only as a
search direction, never as a legibility score. [PLAN]

## 6. The two groups

120 PRC candidates were measured with the published module. The value used is
the **final symmetric ink**: the share of the original ink that is symmetric
under the half-turn, after the centre has been searched and the rules
applied. The retention of the original ink is 1.005 in the median, so
nothing is being bought by erasing.

### Group A — readable in both orientations almost as they stand

Final value ≥ 0.45. Eleven candidates:

| glyph | partner | centre of the box | searched centre | final |
|---|---|---|---|---|
| 一 | 一 | 0.006 | 0.835 | **0.835** |
| 丨 | 丨 | 0.000 | 0.737 | **0.737** |
| 囗 | 囗 | 0.287 | 0.551 | **0.551** |
| 垂 | 罟 | 0.381 | 0.482 | **0.482** |
| 团 | 因 | 0.310 | 0.479 | **0.479** |
| 囝 | 囝 | 0.319 | 0.475 | **0.475** |
| 因 | 团 | 0.198 | 0.473 | **0.473** |
| 困 | 园 | 0.271 | 0.464 | **0.464** |
| 回 | 回 | 0.169 | 0.465 | **0.465** |
| 圃 | 圜 | 0.417 | 0.460 | **0.462** |
| 壬 | 壬 | 0.430 | 0.456 | **0.456** |

The group is dominated by the **enclosure family** — 一, 丨, 囗 and the
囗-derived forms — and by the strokes that are symmetric on their own.
These are the forms whose *whole* structure is half-turn symmetric: the
enclosure closes on itself, and the interior either is symmetric too (回,
囝) or is small enough not to dominate the ink.

### Group B — possible, but the drawing has to be worked on

Final value between 0.30 and 0.45. Thirty candidates; the strongest:

| glyph | partner | centre of the box | searched centre | final |
|---|---|---|---|---|
| 囹 | 囵 | 0.314 | 0.441 | **0.443** |
| 围 | 囡 | 0.311 | 0.436 | **0.437** |
| 囿 | 囵 | 0.328 | 0.435 | **0.435** |
| 固 | 囵 | 0.373 | 0.428 | **0.430** |
| 日 | 日 | 0.431 | 0.428 | **0.431** |
| 圆 | 圆 | 0.407 | 0.413 | **0.416** |
| 国 | 国 | 0.171 | 0.410 | **0.414** |
| 口 | 口 | 0.147 | 0.392 | **0.399** |
| 圈 | 圈 | 0.308 | 0.387 | **0.393** |
| 噩 | 罟 | 0.082 | 0.390 | **0.393** |
| 囫 | 囫 | 0.316 | 0.386 | **0.386** |
| 圉 | 圉 | 0.307 | 0.376 | **0.378** |

These are the forms whose **frame** is symmetric but whose **interior is
not**. 国 is the clearest case: the enclosure 囗 can be made half-turn
symmetric, but the 玉 inside it cannot — the middle horizontal of 玉 is at
the bottom of the character and the vertical is off-centre. Turning the
drawing turns the interior into a shape that is no longer 玉. No local edit
fixes that; the interior has to be redesigned. That is a construction
problem, not a tuning problem.

The three-level split (A ≥ 0.45, B 0.30–0.45, C < 0.30) puts 79 of the 120
candidates in C. The distribution of the final value is p10 0.184,
p25 0.225, p50 0.252, p75 0.361, p90 0.438, p95 0.474, max 0.835.

### What separates A from B, measured

| | Group A | Group B |
|---|---|---|
| places with a counterpart under the half-turn | 1–6 of 2–17 | 1–6 of 7–20 |
| orphan places | 0–7 | 2–9 |
| strokes split at a corner (R-STRUCT) | 0–2 | 0–5 |
| symmetric ink after the centre alone | 0.44–0.84 | 0.39–0.44 |

The discriminator is **not** the number of strokes and **not** the weight
gradient. It is whether the half-turn maps the *stroke decomposition* onto
itself. Group A does; Group B does not, and the gap has to be closed by
redrawing the interior, not by trimming the ends.

## 7. What the rules actually buy, measured

The rules were implemented and run over the 120 candidates. The result is
mostly negative, and it is worth stating plainly.

| quantity | value |
|---|---|
| places (corners where strokes end) measured | 2,065 |
| places with a counterpart under the half-turn | **421** (20%) |
| orphan places | **938** (45%) |
| candidates the rules improve | 53 of 120 |
| candidates the rules make worse | 26 of 120 |
| mean change in symmetric ink from the rules | **+0.002** |

**The rules are almost never enough, because the asymmetry is structural.**
Of the places a drawing occupies, fewer than a fifth have a counterpart under
the half-turn. The rest are places where the half-turn wants an extremity
that the drawing does not have, because in the other orientation that corner
is a *bend inside a stroke* rather than the end of one.

The enclosure family is the clear case. 口 draws its top and right sides as
one stroke (横折), so the top-right corner is not an extremity — it is a
bend. Turned 180°, the bottom-left corner of the frame is an extremity of
two strokes. The two orientations therefore do not even agree on how many
strokes they see, and no amount of re-weighting the ends repairs that.

**R-STRUCT** is the rule that addresses it: split the stroke at the corner
so that both orientations have the same extremity structure. The ink is
unchanged; only the stroke count of the drawing changes (口 goes from three
strokes to four). It fires on 0–5 corners per candidate and is what the
+0.002 comes from. It is necessary and it is not sufficient.

**What would be sufficient** is a redesign of the drawing rather than a
correction of it: the interior of 国, the 玉, has to be redrawn so that it is
itself half-turn symmetric, which means giving up the PRC stroke order of
the original character. That is a construction decision with a cost, and it
belongs to the merged, cross-pair construction, not to the extremity rules.

Two consequences for the method:

* the order of work is **centre first, structure second, extremities last**;
* a construction that reports "the extremities have been reconciled" is
  claiming very little, and the numbers above are what it is worth.

## 8. R-SECT: thickness by sector

The rules above act on the extremities. There is a coarser and, on the PRC
forms, a **more productive** lever: the thickness of the strokes, changed
sector by sector.

The box is divided into a 3 × 3 grid of sectors `S(i, j)`. The half-turn
maps `S(i, j)` onto `S(2 − i, 2 − j)`, so the nine sectors form four
opposite pairs plus the centre. Each sector carries a thickness multiplier
`m_s`, and the half-width of a stroke sample becomes

$$
w_{new}(t) = w(t)\; M(p(t))
$$

where `M` is the multiplier field and `p(t)` the position of the sample.
The field is a normalised convolution of the sector values,

$$
M(p) = \frac{\sum_s \mathrm{blur}\bigl(\chi_s(p)\,m_s\bigr)}
            {\sum_s \mathrm{blur}\bigl(\chi_s(p)\bigr)},
$$

with `χ_s` the indicator of sector `s` eroded by six cells. The erosion is
what makes the multiplier exact in the interior of a sector; the blur blends
the borders. A hard step at a sector border would put a visible notch in the
middle of a stroke, and a reader would read the notch as a break.

### The rule

For every pair of opposite sectors, compare the ink they carry and thicken
the lighter one until the pair balances:

$$
A(s) = \bigl|\,\mathrm{ink} \cap S(s)\,\bigr|,
\qquad
m_s = \min\bigl(1.40,\; A(r)/A(s)\bigr) \text{ if } A(r) > A(s),
\qquad r = (2-i,\; 2-j)
$$

The comparison uses the **full** sectors, which tile the box; the eroded
masks exist only to build the field. Counting on the eroded masks drops the
ink that lies near a border, which for a narrow stroke is all of it.

### The score, and what keeps it honest

$$
\mathrm{sym}(D) = \frac{|D \cap R(D)|}{|D|}
\quad\text{subject to}\quad
\frac{|D \cap D_0|}{|D_0|} \ge 0.90,
\qquad
\frac{|D|}{|D_0|} \le 1.30
$$

`D₀` is the original drawing. The first constraint says at most 10% of the
original ink may be erased; the second says at most 30% of ink may be
added. Without them the score can be gamed: a drawing can always be made
symmetric by deleting what is not, and always made "symmetric" by flooding
the box. **A manipulation that raises the score by erasing or by flooding is
rejected by the constraints, not by the score.**

### Measured

Six frameless ideograms from the median band of the measured distribution
(the interquartile band 0.225–0.361 of the symmetric-ink values). A form is
**frameless** when its ink does not enclose any region of its own bounding
box: the raster is closed by two cells and the background is flooded from
the border of the canvas, and whatever the flood cannot reach is
enclosed. The test is geometric, not a radical lookup, and it separates
囗 (0.58), 国 (0.44), 回 (0.39), 圓 (0.43) from 令 (0.00), 告 (0.05),
普 (0.08), 昔 (0.08). It also catches the forms that *contain* an
enclosure — 涸 (0.25), 吕 (0.26), 崮 (0.26) — because they have one
somewhere in the character.

| ideogram | strokes | base | rule R-SECT | greedy search | retention |
|---|---|---|---|---|---|
| 令 | 5 | 0.318 | 0.350 | 0.409 | 0.910 |
| 告 | 7 | 0.350 | 0.360 | 0.439 | 0.962 |
| 昔 | 8 | 0.329 | 0.330 | 0.410 | 0.924 |
| 普 | 12 | 0.250 | 0.311 | 0.340 | 0.998 |
| 匿 | 10 | 0.332 | 0.351 | 0.386 | 1.000 |
| 阗 | 13 | 0.351 | 0.377 | 0.451 | 0.977 |
| **median** | | **0.331** | **0.350** (+0.023) | **0.409** (+0.090) | |

**Yes, the manipulation works, and it works better than the extremity rules
of §4.** The rule alone lifts 普 from 0.250 to 0.311 (+0.061) and 阗 from
0.351 to 0.377 (+0.026); the greedy search, which may also *thin*, adds
another +0.029 on 普 and +0.074 on 阗.

What the multipliers look like is the interesting part. The rule finds the
imbalance between two opposite sectors and thickens the lighter one: for
令, 告, 昔 and 普 the pair that needs work is the top-middle against the
middle-left, and the multipliers land at 1.40 on one of them. For 匿 the
right-hand column — the 若 inside the 匚 — carries less ink than the left,
and the rule thickens that column. In other words, **the rule discovers the
asymmetric component of the character and compensates it with weight**,
which is exactly what a human calligrapher would do.

The search goes further by thinning as well as thickening: for 昔 it thins
the left column to 0.70 and thickens the middle column to 1.45, which the
rule does not find. But the greedy descent is not guaranteed to be the
global optimum, and widening the multiplier range does not always help —
for 匿 the wider range gives a *worse* result (0.404 → 0.386).

### Does it generalise?

The rule was then run over **every frameless candidate in the median band** —
53 ideograms, not six:

| | value |
|---|---|
| base, median | 0.240 |
| after R-SECT, median | 0.266 |
| median gain | **+0.023** |
| mean gain | **+0.030** |
| candidates that improve | **52 of 53** |
| candidates that get worse | 1 of 53 (by 0.001) |
| median retention of the original ink | 1.000 |

The biggest gains: 匈 0.180 → 0.296 (+0.115), 罱 0.198 → 0.279 (+0.081),
匆 0.202 → 0.279 (+0.077). The gain does not depend on the
number of strokes: the correlation between the gain and the stroke count is
**-0.17**, and the largest gain is on a six-stroke character while a
fourteen-stroke character gains almost as much.

### What this does not settle

* The score is geometric. Whether a thicker 氵 reads better to a reader is
  exactly the question the pilot instrument exists for, and that evidence
  does not exist.
* Six ideograms plus a generalisation run over the frameless median band
  is a sample of a sample. The numbers show the lever exists; they do not
  establish a rate for the PRC inventory.
* The 3 × 3 grid is a choice. A finer grid would localise the imbalance
  better but has more parameters to fit and more risk of fitting noise.

## 9. What this does not do

* It does not prove that any drawing is readable. It measures agreement of
  ink with itself under a half-turn.
* It implements the **self-rotation** case (`a ↔ a`). The merge of two
  *different* forms — deciding which stroke of `a` answers to which stroke
  of `b`, and then applying the same rules to the union — is not
  implemented. The measured PRC pair distances are in
  [findings/prc-extremity-analysis.md](../findings/prc-extremity-analysis.md).
* It uses the PRC medians as given. A median is not always the exact medial
  axis, so the weight profile carries the font's own approximation.
* The sector manipulation (§8) has been measured on six ideograms and on
  the frameless median band; it has not been run over the whole PRC
  inventory, and the cross-pair merge is still not implemented.
* The constants `δ_f`, `r_c`, `κ` are measured on one font (Arphic Public
  License, GB and UKai faces) on one inventory. They are properties of that
  font, not of the PRC script.

## 10. Reproducing the measurements

```bash
python code/prc_construct.py \
    --graphics data/prc/graphics.txt \
    --characters 口,田,国,日,一 \
    --out output/prc-construction.json
```

The module needs no network access and no external data beyond the MMah
file; see [SCOPE.md](../SCOPE.md) for the licensing position and
[the licence audit](../LICENSE-AUDIT.md) for the status of every input.