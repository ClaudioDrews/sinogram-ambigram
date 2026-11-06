# Results Summary (what the evidence supports)

Strict summary of what was **measured, derived or only claimed**. For details follow the links. Evidence labels are defined in the [repository README](../README.md).

## R1. Documented / verified from the paper [PAPER]

* The only peer-reviewed method in the folder (Inoue & Takahashi 2020) works on **46 hiragana** (1,081 pairs): Yu Gothic 300 px → Zhang–Suen thinning → RDP (20 px) → graph isomorphism with ranking → Delaunay + affine → brush model; 18 raters; 325/724 pairs (book list) readable, 93/357 (new) readable; 216/246 4-kana words readable. Limits stated by the authors: kanji and complex characters need multi-component graph matching. [Details](../methods/inoue-takahashi-2020.md)

## R2. Algebraic/derived results (no data needed) [DERIVED]

* Half-turn is an involution; mirrors ≠ rotations ([existence criterion](../theory/existence-criterion.md)).
* IDS anti-automorphism: reverse children for binary/ternary compositions, dual enclosure operators, ⿴ self-dual; typed per-operator rules needed ([ids-rotation-algebra](../theory/ids-rotation-algebra.md)). Unit-tested in GPT's prototype (23/23) — tests only check rule consistency.
* `⿱SS` is an exact self-ambigram iff S is C2 → 昌 日日 / 吕 口口 *in the abstract*; 圭 (土土) and 朋 (月月) are not self-ambigrams once leaves are mapped.
* Stroke table: 横 竖 preserved; 撇↔提 and 横折↔竖折 swapped; 捺 点 hooks broken ([table](../theory/stroke-type-rotation-table.md)).
* Word lemma `R(c₁…c_n)=R(c_n)…R(c₁)` ([word-level](../theory/word-level-and-lexical.md)).
* Pair-count arithmetic: 46 hiragana ⇒ 1,081 pairs incl. self.

## R3. Measured (geometric proxies; No controlled native-reader validation) [MEASURED]

| ID | Result | Run | Caveat |
|---|---|---|---|
| R-C2 | Self-rotation is high for 一 二 三 工 王 互 亜 回 皿 且 重 (≥0.9 in Claude v1/v2; Kimi lists 目 .930 gothic, 皿 stable across fonts .868/.856) | Claude, Kimi, GPT (互 .799, 一 .786, 工 .742 unshifted) | Different metrics; 十 日 田 口 中 目 申 score low in some metrics (font optics) and high in others |
| R-FONT | Typography dominates: 一 1.000 gothic vs .204 Mincho; gap 0.15–0.60 | Kimi | single-lineage Source Han family |
| R-INK | 甲 self-IoU .818 although not C2: raster IoU is blind to small distinguishing strokes | Kimi, GLM, GPT | — |
| R-SLOT | 昌/吕 predicted exact by algebra, measured .09–.54 due to slot sizing | GLM, GPT | Mistral gives .053 d (inconsistent, [C-07](../findings/conflicts-and-corrections.md)) |
| R-CAND | Candidate near-pairs: 士↔干 (.984), 千↔士, 土↔干, 王↔玉, 王↔正, 玉↔正, 上↔丁 (aliasing: needs hook→bar), 旦↔百 | Claude v2, Mistral, GPT | scores are metric-specific (GPT's best pair stays < 0.70); no human check |
| R-MIRROR | 上↔下 is a mirror pair (H>R) | GLM, Claude v1 | Claude v2 CSV lists it at .793 |
| R-NEG | 未↔末 and 凹↔凸 behave as negative controls; R(未)≈半 | Claude v1/v2, GLM (凹凸) | GLM's own 未末 reasoning flip-flopped |
| R-VIS | Visual readings: R(士)=干, R(甲)=由, R(由)=甲, R(田)=田, R(中)=中, R(目)=目 | Claude (+ models) | VLM readers, not humans (exp-06) |
| R-PIPE | Pre-filtering with W1 profile + warp-based scoring works as a candidate generator, not as a decision rule | Claude v2 | uncalibrated threshold |
| R-C2COUNT | Exact Jōyō self-ambigrams ≈ 15–20 (gothic cut ≥0.80) | Kimi (13 ≥.9, 20 ≥.8 in Claude v2) | metric-dependent |
| R-C2VG | Vector self-rotation orders the C2 core as 目 .0323, 日 .0436, 一 .0504, 田 .0509, 口 .0614, 回 .0697; 23 glyphs at H ≤ 0.085 | MiniMax (exact refinement) | one canonical shape per glyph; frame glyphs over-ranked (CR2) |
| R-GRAPH | At H ≤ 0.085 the rotation graph has 28 edges over 44 nodes; at H ≤ 0.10, 655 edges / 537 nodes (table) — the text of the same report says 710/558 | MiniMax [REPORTED] | **contested**: independent recount gives 31 edges at 0.085 and 2,301 at 0.10 (X2) |
| R-CANON | 由↔甲 is the 2nd best **distinct** pair of the whole catalogue, H = 0.0751, chamfer 0.0232 | MiniMax (exact); reproduced by the independent review (H 0.0751) | "2nd" excludes self-pairs; 吉↔阜 is 1st at 0.0682 |

## R4. Claims without measurement [CLAIM/PLAN]

Nomura law formalisations; "3× chance / 70% of work" heuristics; 全力↔不屈 mechanism; 挑戦↔勝利 analysis; ε values; C2 lists with 士/木/品/吕; stroke cost values; all roadmaps; RFB transfer ideas (related work).

## R5. What is NOT yet known

See [limitations](../findings/limitations.md) and open questions. Most important: no calibrated ε, no human tests, no human-validated general-purpose ambigram generator. A full pair search over 2,770 glyphs under a KanjiVG-based geometric metric now exists (exp-08), but its ranking is not validated: it has a density bias and a hub bias, its graph is only reliable below H ≈ 0.09, and an independent review found that several "confirmed" findings of that run do not hold (X3, X4) and that some of its own tests fail (CR6).

## Related

- [Pair evidence matrix](../findings/pair-evidence-matrix.md)
- [Conflicts and corrections](../findings/conflicts-and-corrections.md)
- [Limitations](../findings/limitations.md)
- [KanjiVG rotation-graph method](../methods/rotgraph-method.md)
