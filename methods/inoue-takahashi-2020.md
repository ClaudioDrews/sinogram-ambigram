# Inoue & Takahashi (2020) — Hiragana Ambigram Generation (primary paper)

Source `PAPER` = [papers/49_301.pdf](https://www.jstage.jst.go.jp/article/iieej/49/4/49_301/_article/-char/ja), DOI [10.11371/iieej.49.301](https://doi.org/10.11371/iieej.49.301). Citation: Kazuki Inoue (井上和輝), Hiroki Takahashi, 「文字構造特徴を用いたひらがなアンビグラムの生成」 (*Generation of Hiragana Ambigram Based on Character Structure Characteristics*), Journal of the Institute of Image Electronics Engineers of Japan **49(4)**, 301–314 (2020), Univ. of Electro-Communications. All statements in this file are [PAPER] (read from the PDF text) unless flagged. The paper is in Japanese. **Re-checked 2026-11-05**: the PDF was downloaded again (2,841,138 bytes) and the figures below were re-read in it — 1,081 pairs, 724/325, 357/93, 246/216, 18 raters, the 3/5 and 2/3 majorities, the 20 px simplification threshold, the 300×300 input, Yu Gothic, ETL8, and reference [1] = Nomura's book. The second author's given-name reading is *not* confirmed here (the J-STAGE page shows the family name only in the metadata used); treat "Hiroki" as unverified.

## 1. What it does

Generate 180° rotational (inverted-image) ambigrams for **pairs of the 46 hiragana** (1,081 pairs = 46 chars one-to-one, as stated: "1,081 組"). Not kanji.

## 2. Pipeline (sections 3–5)

1. Input 300×300 px, font **Yu Gothic (游ゴシック)** — chosen because it has no serifs (うろこ) and uniform stroke width.
2. **Zhang–Suen thinning**; trace thinned pixels to extract strokes. Junction candidates are located; because in hiragana **no ≥3 strokes cross at a point**, junction degree is only 3 or 4. Degree 4: strokes cross; degree 3: split into two strokes by curvature (angle comparison at a point 3 px from the endpoint).
3. **Ramer–Douglas–Peucker simplification**, point-to-line threshold **20 px** (chosen so hook/sweep (はね/はらい) structure survives). Feature points = stroke endpoints, intersections, corner points.
4. **Graph**: feature points = nodes, connections = edges. Connected subgraphs; graph isomorphism (Eq. 1: bijection preserving adjacency). Isomorphism alone does not ensure geometric similarity, so isomorphic subgraph pairs are **ranked** by an Eq. (2) rank score built from normalised terms (one is the sum of Euclidean distances between corresponding points, Eq. 3; a slope-similarity threshold on corresponding adjacent edges is also used; normalisation to mean 0 / variance 1; coordinates scaled by 1/100); parameters were set from preliminary experiments. (Exact weights of Eq. 2 were not transcribed here — see the PDF.)
5. **Global** subgraph search: connected graphs with edge density ≥3, largest common structure of similar geometry → affine transform to overlap them; then **local** search for remaining nodes by node distance; final re-affine with new correspondences.
6. Triangle mesh from **Delaunay triangulation** + feature points; **per-triangle affine maps** produce the intermediate structure of the two characters.
7. **Brush-style rendering** (石亀 et al. brush model: triangle + circle): spline interpolation of feature points; brush pressure (thick on common/corresponding points, thin on non-corresponding) and brush-tip angle (initial 135°) — implements "common thick, exclusive thin".
8. Compute: Intel Core i7-8650U.

## 3. Evaluation (section 6) and results

| Experiment | Setup | Result |
|---|---|---|
| Single-character human readability | **18 participants** (Google Forms, free-text answers; "−" if unreadable); each *feasible* pair rated by **5**, each *unknown* pair by **3** raters; readable only if **both** readings correct; pair readable if majority (3/5 or 2/3). Participants only told "an ambigram is a character readable when inverted"; no creation experience. | **Feasible set F = 724 pairs documented in the designer's book (ref. [1], Nomura 2018)**: **325 readable, 399 not** (Table 1). **Unknown set = remaining 357 pairs**, which the authors judged hard to make by hand: **93 readable, 264 not** (Table 2; 26.1%). 1,081 = 724 + 357. |
| Hiragana CNN recogniser | CNN trained on ETL8 (160 writers); train acc 0.96 (loss 0.12), test acc 0.99 (loss 0.01); readable if both orientations recognised | Only **78 of 1,081** readable; of these only **42** also readable by humans ⇒ the authors conclude **no relation** between human and recogniser readability. Applying the recogniser to the designer's 724 pairs: **1** readable. |
| Word readability | 4-hiragana words from a Japanese-learner vocabulary list (dakuten, handakuten, small kana excluded; homophones merged): \|I\|=2,536; word-pair candidates built from pairs with readability ≥0.6: 15,474; one pair chosen per element ⇒ **246 word pairs**; 15 participants, 5 per word | **216 of 246 readable (87.8%)** even though words contained a low-readability character. The abstract's English text says "216 out of 246 words"; the Japanese abstract says "246 文字中 216 文字". |
| Correlations (section 7) | proportion of common strokes `r_c` (overlapping edge length / total edges) vs readable fraction; mean edge angle change vs readability | Readability **rises with common-stroke proportion** (bar chart Fig. 18; examples in Figs. 19–20: r_c 0.09 and 0.14 → readability 0.2; r_c 0.63 and 0.60 → readability 1.0). **No clear correlation with mean angular change.** Authors argue a few critical edge changes (e.g. き↔さ junction merging) matter more than average deformation. |
| Comparison with Riesen graph matching | Riesen et al. GED-style assignment, costs from node coordinates, insertion/deletion costs tuned so い↔い works | Riesen's matching broke positional relations (e.g. す↔ま nodes 2/9 vs 4/7; slope differences ~90°), supporting the use of structural features. |
| Scope (section 8.2) | Applied unchanged to lower/upper-case Latin, **katakana 180°**, and **mirror-inverted hiragana** (Fig. 26) | Works; only hiragana-specific assumption is junction degree ≤4. |

## 4. Limits stated by the authors (section 9–10)

* Global subgraph matching works only between **connected graphs**; cannot make 1-to-many (e.g. 2 chars → 3 chars) ambigrams.
* **Most kanji consist of several connected graphs**, so "global" matching ceases to be global — generalisation to kanji needs matching across multiple connected components.
* Characters with few feature points (く, へ) or few corresponding points get too little deformation; need better non-common-stroke suppression and thickening.
* More than half of feasible pairs were **not** readable (325/724).

## 5. Things the secondary documents say that the paper does NOT support

| Claim | Where | Status |
|---|---|---|
| "When IDS top-level operators match (both ⿰ or both ⿱) chance is 3× higher / matching is more stable" | `META-DECK` slide 7, `LOG-META`, `RPT-CONSOL` | Not in the paper (searched PDF text); no experiment in the folder. **[CLAIM]** |
| "724 pairs suggested feasible" read as the algorithm's output | abstract translations in `LOG-MULTI` | Full text: 724 are the designer's book pairs; the abstract wording "suggested feasible" is ambiguous. [PAPER] resolves it as above. |
| 324/724 readable | `RPT-META` | Paper says **325**. |
| Paper provides a closed formula "a→b" | `LOG-MULTI` (Claude) | Correct: it provides a procedure, not a formula. |
| Early AI analyses (`RPT-RULES`, `LOG-MULTI`) | | Based only on the abstract (full text could not be opened); statements about internals there were "inference marked as such". This file supersedes them. |

## 6. Generalisation proposals (not executed) — see [methods](../methods/methods-and-pipelines-proposed.md)

KanjiVG vectors instead of thinning; GED with merge/split instead of isomorphism; TPS/CPD warps; hierarchical stroke/component/radical graphs; OCR/CNN as ρ proxy; ε calibration. The paper's own limits (§4) are exactly the pain points those proposals target.

## Related

- [Existence criterion](../theory/existence-criterion.md)
- Related work
- [Word-level and lexical](../theory/word-level-and-lexical.md)
