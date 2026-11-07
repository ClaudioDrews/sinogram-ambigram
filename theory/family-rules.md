# Universal and Family-Specific Rules

**Evidence basis:** The formulas below are derived from explicit structural assumptions; empirical claims require geometric measurements or recognition tests.

> **Evidence boundary:** Earlier synthesis documents suggested some of these rules without testing them. Untested rules remain [CLAIM] or [PLAN], not measured conclusions.

## A. Universal rules (apply to any sinogram)

| # | Rule | Status |
|---|---|---|
| U1 | R is a half-turn involution; mirror pairs are excluded ("mirror pair filter": compare reflection score H with rotation score R; reject if H>R) | [DERIVED]; filter exercised in Claude v1 (上↔下: H 0.83 vs R 0.44), GLM (H 0.66 > R 0.61) |
| U2 | Existence criterion / legibility intersection ([existence-criterion](../theory/existence-criterion.md)) | model, ε uncalibrated |
| U3 | IDS anti-automorphism ([ids-rotation-algebra](../theory/ids-rotation-algebra.md)) | [DERIVED]; operator rules unit-tested (GPT 23/23) |
| U4 | Stroke-type re-typing ([stroke table](../theory/stroke-type-rotation-table.md)) | [DERIVED], untested on outlines |
| U5 | Word lemma `R(c₁…c_n)=R(c_n)…R(c₁)` ([word-level](../theory/word-level-and-lexical.md)) | [DERIVED] |
| U6 | Slot/typography convention breaks exact algebra (components drawn smaller/larger in a slot; thick/thin Mincho) | [MEASURED] (昌/吕 0.52–0.54 vs predicted exact; 土/士) |
| U7 | Density: complexity differences (e.g. 8 vs 12 strokes) need M:N stroke fusion (GED with merge/split cost) and Law 4 | [PLAN] |
| U8 | Natural pairs are best among low-stroke glyphs with centred structure ("<6 strokes + centred structure ⇒ larger ε") | [CLAIM] (`earlier planning outline` slides 5–6; heuristic, no data) |

## B. Family rules

| Family | Rule | Examples cited | Status / evidence |
|---|---|---|---|
| **Pure C2** | `R(c)=c`, zero-cost anchors | 一 十 口 日 田 王 中 申 皿 回 工 互 亜 車 且 (lists differ) | Measured self-rotation: strong for 一 二 三 工 王 互 回 亜 (several runs); weak or inconsistent for 日 田 目 口 十 中 申 depending on metric ([results](../findings/results-summary.md) R-C2). On KanjiVG vectors the order is 目 .0323, 日 .0436, 一 .0504, 田 .0509, 口 .0614, 回 .0697, with 23 glyphs at H ≤ 0.085 (exp-08); 十 is **not** in that group (370th, H 0.115), and the 囗 family dominates just below it. 士 and 木, 品 listed as C2 by `earlier exploratory summary` are contradicted (R(士)≈干). |
| **Quasi-C2 / symmetric core** | `X=C⊕_p s` ⇒ `R(X)=C⊕_{R(p)}R(s)` | 甲↔由, 土↔士 (claims) | 甲↔由 supported by Claude v2 (0.92 as neighbour), Mistral (rank 24/6328), contradicted by GPT pilot (0.455) — see matrix |
| **V-symmetric conjugation** | left–right symmetric glyphs: `R=H` | 甲/由, 土/士, 未/末, 杏/呆, 杳/杲 | 土/士 and 未/末 are **disputed**: Claude's final analysis says R(未)≈半 not 末 and 土~士 is head/tail displaced, other runs measure 0.40–0.86 |
| **Duplicate duad ⿰SS / ⿱SS** | exact self-ambigram iff S is C2 | 昌 (日日), 吕 (口口) | algebra [DERIVED]; font measurement 0.09–0.54 (slot convention); CHISE 昌=⿱日曰 (Claude) |
| **Full enclosure ⿴** | if frame and content are both C2 ⇒ `R(a)=a` | 回 国 困 囲 | 回 measured C2-like; 国/困/囲 not measured; 国 in Mistral missing (download failure) |
| **⿱ symmetric** | `R(⿱UL)=⿱R(L)R(U)`; works when U vertically symmetric and L is C2 | 旦 昌 杲 (`earlier exploratory summary`: 旦↔旦) | 旦 contradicted: R(旦)=bar over 日 ≈ not 旦 (Claude, contact sheet); 旦↔百 .98/.86 and 旦↔目 .896 reported instead |
| **⿰ left–right** | `R(⿰XY)=⿰R(Y)R(X)`; need X↔R(Y′) | 林 相 挑 | not measured; 挑戦↔勝利 claimed from Nomura's works |
| **⿸ ⿹ ⿺ ⿵ ⿶ ⿷ ⿼ ⿽** | enclosure dual; roof becomes base; multiple horizontals map onto enclosure | 病 屈 医; 全↔屈 | claims only (`earlier exploratory summary`); 問 (⿵門口→⿶) algebra only |
| **⿻ overlay** | intersection points as invariant anchors | 巫 卍 | claims only; operator rule disputed |
| **Semordnilap compounds** | `R(XY)≈YX` if `R(X)≈Y`, `R(Y)≈X` | 外人↔人外, 外国↔国外 | [DERIVED]; relies on R(外)=外, R(国)=国 (unmeasured) |
| **Hiragana** | paper's pipeline; 724 designer pairs; 87.8% word readability | 46 kana | [PAPER] ([inoue-takahashi-2020](../methods/inoue-takahashi-2020.md)) |
| **Katakana / Latin / mirrored hiragana** | paper applied the same pipeline | — | [PAPER] §8.2 (Fig. 26) |
| **Hangul** | jamo position permutation as IDS-like composition | — | `alternative-method proposal`/`earlier candidate catalogue` speculation; untested; outside the sinogram scope |
| **Complex multi-component kanji** | needs multi-component graph matching (paper's stated limit) | 天↔魔 (≈4 vs ~21 strokes) | [PLAN] |

## C. Pairs by relation type (taxonomy proposed in `earlier candidate catalogue`/`earlier synthesis`)

* **同一型** identical (C2); **准同一型** near-identical (quasi-C2: proportion/weight tweak); **conjugate pairs** (stroke-end flips: 千↔士, 士↔干); **insertion/attenuation pairs** (王↔玉: hide dot); **re-typing pairs** (上↔丁: hook→short stroke); **mirror pairs** (rejected: 上↔下); **exact IDS pairs** (杏↔呆, 杳↔杲, [DERIVED]); **word compositions** (全力↔不屈, 外国↔国外).

## Related

- [Existence criterion](../theory/existence-criterion.md)
- [Results summary](../findings/results-summary.md)
- [KanjiVG rotation-graph method](../methods/rotgraph-method.md)
- [IDS rotation algebra](../theory/ids-rotation-algebra.md)
