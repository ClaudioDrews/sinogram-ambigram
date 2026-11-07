# The Existence Criterion (ε-theorem), Legibility Sets, Parity Decomposition

**Evidence basis:** The formulas below are derived from explicit structural assumptions; empirical claims require geometric measurements or recognition tests.

> **Evidence boundary:** Earlier synthesis documents suggested some of these rules without testing them. Untested rules remain [CLAIM] or [PLAN], not measured conclusions.

## 1. Model as stated in the sources [DERIVED / model]

* Shape space 𝒢 (binary images or distance fields in [0,1]²). For each character `c`, `F(c) ⊂ 𝒢` = canonical forms (all fonts/hands read as c).
* Tolerant recogniser: `ρ(g) = c ⇔ d(g, F(c)) ≤ ε(c)`; ε(c) is the perceptual tolerance (brain reads by prediction; inverted text is confusing because ρ is orientation-sensitive).
* Rotation `R f(x) = f(2·centre − x)`, an involution.
* Definition: `g` is a rotational ambigram of ordered pair (a,b) if `ρ(g)=a` and `ρ(R g)=b`.
* **Criterion (as claimed)**: exists `g` ⇔ `d(F(a), R·F(b)) ≤ ε(a)+ε(b)` (set distance, e.g. Hausdorff). Equivalent picture: legibility balls `B(F(a),ε(a))` and `R⁻¹B(F(b),ε(b))` intersect; the optimum is the midpoint of the intersection (`RPT-RULES`).

Consequences claimed: (i) **ε is the resource that pays for the ambigram** (exact equality essentially never happens for distinct pairs); (ii) identical type (同一型, b=a): criterion reduces to `d(F(a), R·F(a)) ≤ 2ε(a)`, exactly met by C2 glyphs; (iii) every construction method either reduces `d` (pair choice), builds the intermediate `g`, or manipulates ε via stroke weight/salience (Nomura).

## 2. Corrections and caveats (important)

| Issue | Where | Content |
|---|---|---|
| "iff" is not a theorem | `LOG-GPT2` (GPT, 3rd turn) | With tolerance sets in an arbitrary metric space the inequality is **necessary** for neighbourhood intersection but **not universally sufficient**; Hausdorff distance ≠ minimum distance between sets. Rigorous general form: **`L_A ∩ R⁻¹(L_B) ≠ ∅`** where `L_c` = effective legibility set. The inequality is an operational approximation under explicit geometric assumptions. |
| "Anti-automorphism" is not uniform | same | Some IDS operators swap child positions, some change the surrounding operator, some keep distinct roles ⇒ implement a *typed* algebra with per-operator rules ([ids-rotation-algebra](../theory/ids-rotation-algebra.md)). |
| "Theorem" language | `LOG-MULTI` (Claude critique) | The first proposal's claims were partly "theorems by definition"; thresholds/ε uncalibrated. |
| ε unknown | all | ε per character/family/reader/style is **not known**; no experiment calibrated it. Sources propose human blind tests / OCR-CNN proxies ([methods](../methods/methods-and-pipelines-proposed.md)). |
| Distance unspecified | all | d could be Hausdorff, Chamfer, EMD, Procrustes, GED, IoU-based, or neural feature distance; experiments used different ones ([metrics-comparison](../methods/metrics-comparison.md)). |

## 3. Legibility-set formulation (alternative) [PLAN]

`LOG-GPT1` §7.3 (and `CAT-XLSX` "Legibility Set Intersection Theorem"): define manifolds `M_A = {X : P(A|X) ≥ τ_A}`, `M_B` likewise (classifier confidence thresholds). Ambigram exists iff `M_A ∩ R_π(M_B) ≠ ∅`. An "ambigramability" score E(A,B) can be estimated (compare AmbiFusion's notion, related work). If the intersection is empty there is no solution under those recognition criteria; if non-empty, its extent gives the cost of the best solution.

## 4. Midpoint and SDF rule (Nomura law 3 formalisation) [PLAN]

`g = (f_a + R·f_b)/2` in a signed-distance-field representation; minimises `max(d_a, d_b)` (`META-DECK` slide 4/9). Companion rule from the Reversible Faces Benchmark: compromise point `s* = (w_A·a + w_B·R(b)) / (w_A+w_B)`, which for equal weights also minimises the worst deviation (see [RFB geometry §4](https://github.com/ClaudioDrews/reversible-faces-benchmark/blob/main/docs/geometry.md)). In both, two closed balls of equal radius ε intersect iff `‖a − R(b)‖ ≤ 2ε` (RFB geometry §4), which mirrors the sinogram criterion with ε(a)=ε(b).

## 5. Parity / harmonic decomposition (approach 4) [DERIVED]

* Ink function `f(r,θ)`; `R` ⇒ `f(r,θ+π)`; in the angular Fourier series `f_n → (−1)^n f_n` (odd harmonics change sign).
* Even part `f₊ = (f + R f)/2` = C2-symmetric skeleton shared by both readings; odd part `f₋ = (f − R f)/2` carries the asymmetric strokes (`R f₊ = f₊`, `R f₋ = −f₋`). Pure C2 glyphs have all odd harmonics = 0.
* Idea: keep low-frequency (structure), sacrifice high-frequency (detail) — `LOG-MULTI`/`META-DECK` slide 11.
* Differentiable generation: SDF + Fourier rendering would allow gradient optimisation of `ρ(g)=a ∧ ρ(Rg)=b` ([methods](../methods/methods-and-pipelines-proposed.md)).
* Caveat: this is algebra; it does not isolate the *meaning* of A and B (RFB makes the same remark, [geometry §3](https://github.com/ClaudioDrews/reversible-faces-benchmark/blob/main/docs/geometry.md)). `f₋` can be negative, so it is not itself an ink image.

## 6. Diagnostics proposed alongside

* **Symmetry penalty ρ_sym(I) = ‖I − R·I‖/‖I‖** (from RFB, `RPT-FACES`): ≈0 ⇒ the glyph is just identical upside-down (self-ambigram collapse); proposed as a penalty/filter in SDF optimisation so a generator for A≠B does not collapse to a C2 glyph such as 田. In RFB it is only an advisory one-sided alarm (warning when ρ < 0.15) — see the repo's [scripts/perceptual.py](https://github.com/ClaudioDrews/reversible-faces-benchmark/blob/main/scripts/perceptual.py) and [geometry §6](https://github.com/ClaudioDrews/reversible-faces-benchmark/blob/main/docs/geometry.md). Not used in any sinogram run.
* **Radial/bounding envelope** `r₀(φ) = max{r_A(φ), r_B(φ+π)}` (RFB geometry §5) proposed to preserve the em-square frame; not implemented for sinograms.
* **Distinctiveness-weighted distance** `D = αD_skeleton + βD_topology + γD_distinctiveness + δD_style` (`LOG-GPT2`): shared ink mass must not dominate; distinctive strokes (the dot of 玉, the short stroke of 末) weigh more. Proposed only.
* **Three-way separation** (GPT): exact geometric symmetries / natural near pairs / pairs legible only after transformation — adopted as premise P4.

## 7. Status

The criterion is **unvalidated**. No source computed ε. The main measurable surrogate used so far is geometric overlap of rotated glyphs (see experiments).

## Related

- [Family rules](../theory/family-rules.md)
- Glossary and notation
- [Proposed methods](../methods/methods-and-pipelines-proposed.md)
- [Inoue & Takahashi (2020)](../methods/inoue-takahashi-2020.md)
