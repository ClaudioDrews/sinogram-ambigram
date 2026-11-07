# Word-Level Ambigrams and Lexical Filtering

**Evidence basis:** The formulas below are derived from explicit structural assumptions; empirical claims require geometric measurements or recognition tests.

> **Evidence boundary:** Earlier synthesis documents suggested some of these rules without testing them. Untested rules remain [CLAIM] or [PLAN], not measured conclusions.

## 1. Reversal lemma [DERIVED]

For a block of n characters in left-to-right layout, a half-turn reverses the **spatial order** of the sequence:
`R_block(c₁c₂…c_n) = R(c_n)…R(c₁)`.
So a word-ambigram needs a *lexical* partner: `w′ = reverse(map_R(w))` must be a real word. Implementation sketch (`structural proposal`, `reverse_word_ambigram`): for each position take the list of near-R-partners of `c_i` (from the character rotation graph), take the Cartesian product, reverse, and look up in hash sets built from **JMdict** (Japanese) and **CC-CEDICT** (Chinese). Not run anywhere ([PLAN]).

Caveats the sources mention or imply:
* Layout: horizontal (yokogaki) vs vertical (tategaki) writing changes which axis reverses; not analysed.
* Words of different length/density need M:N stroke fusion (全力 8 strokes ↔ 不屈 12), Law 4 (head/tail tolerance).
* Kana, punctuation, Latin and numerals in mixed text are not handled.
* Segmentation: the paper's 4-kana experiment shows that a word context raises readability of weak characters (87.8% word readability although single-character readability was low) — Table-5 pattern: a word with one unreadable (0.2/0.4) character is still often readable if others are readable ([paper summary](../methods/inoue-takahashi-2020.md)). This is hiragana only.

## 2. Named examples (none measured in this project)

| Pair | Claimed mechanism | Status |
|---|---|---|
| 全力 ↔ 不屈 | R(力)≈不 (central cross), R(全)≈屈 (three horizontals of 王 fuse into 尸 enclosure); 8 vs 12 strokes | **[CLAIM]** (`earlier hypothesis note`, `earlier synthesis`, `earlier exploratory summary`); the stroke-level correspondences are stated, not measured, in the folder ([conflicts C-11](../findings/conflicts-and-corrections.md)) |
| 外国 ↔ 国外, 外人 ↔ 人外 | semordnilap with R(外)=外, R(国)=国 | [DERIVED], R(外) not measured; 国 missing from Mistral dataset |
| 挑戦 ↔ 勝利 (Nomura poster) | left–right anti-automorphism; GED | cited as Nomura's work; no analysis |
| 天使 ↔ 悪魔 (KSK ONE), 陰 ↔ 陽 (Nomura) | the problem the criterion is meant to solve | cited in `earlier planning outline`/`earlier rule synthesis` |
| 平成 ↔ 令和, 努力 ↔ 才能, 短所 ↔ 長所 | semantic-contrast pair selection (N4) | proposals |

## 3. Semantic scoring [PLAN]

`Q(A,B)=η₁G+η₂M+η₃P` (geometric compatibility, semantic/narrative interest, predicted legibility) with an LLM for M — `initial geometric analysis` N4. Two-stage filtering (shape filter then semantic classification) in `alternative-method proposal`.

## Related

- [Inoue & Takahashi (2020)](../methods/inoue-takahashi-2020.md)
- [Family rules](../theory/family-rules.md)
- [Proposed methods](../methods/methods-and-pipelines-proposed.md)
