# Key facts

Twelve statements that are easy to get wrong and expensive to get wrong. Each one links to the document that carries the evidence.

1. **Rotation by 180° is `R(x,y) = (−x,−y)`** (determinant +1, an involution). It is **not** a mirror. Mirror pairs such as 上↔下 are **not** rotational ambigrams, although several raster metrics score them high enough to require an explicit mirror filter. [Derivation](../theory/existence-criterion.md)

2. **"Exists ⇔ d(F(a), R·F(b)) ≤ ε(a)+ε(b)" is a model, not a theorem about readers.** ε is uncalibrated. The rigorous form is set intersection: a rotational ambigram exists if `L_A ∩ R⁻¹L_B ≠ ∅`. [Existence criterion](../theory/existence-criterion.md)

3. **IDS rotation is an anti-automorphism** — children are reversed and enclosing operators dualised — but IDS equality does **not** imply visual equality: stroke types, slot sizes and fonts decide the rest. [IDS algebra](../theory/ids-rotation-algebra.md)

4. **⿲ and ⿳ take three operands**, not four. The duals are ⿷↔⿼, ⿸↔⿽, ⿹↔⿺, ⿵↔⿶ (Unicode 15.1 added ⿼ ⿽ ⿾ ⿿). [IDS algebra](../theory/ids-rotation-algebra.md)

5. **The Inoue–Takahashi paper is about 46 hiragana (1,081 pairs), not kanji.** Its "724 pairs" are the list in Nomura's book, not an output of the algorithm. [Paper](../methods/inoue-takahashi-2020.md)

6. **Numbers from different runs are not comparable.** Fonts, canvases, tolerances and metrics all differ; see the table of metrics before comparing anything. [Metrics](../methods/metrics-comparison.md)

7. **Six runs actually executed code and produced numbers**: GPT (42-character pilot + IDS operator tests), GLM 5.3 (29 glyphs), Claude (v1 and v2 over the full Jōyō, 2,136), Kimi (self-rotation over Jōyō, pair search unfinished), Mistral (median graph over 113 characters) and MiniMax (rotation graph over 2,770 glyphs). DeepSeek, Qwen, Meta and Gemini turns are conceptual or analytical only. Experiments index

8. **The canonical pairs 甲↔由, 土↔士, 未↔末 and 上↔下 are disputed** across runs, and were intended as controls, not as validated results. 由↔甲 is now well supported on vectors (2nd best distinct pair, H = 0.0751) but that is a geometric result, not a legibility one. [Pair matrix](../findings/pair-evidence-matrix.md)

9. **KanjiVG was used — once, by the last run.** MiniMax downloaded the repository, took 6,984 canonical glyphs from 11,941 SVGs and used the stroke centrelines as skeletons for the whole 2,770-glyph universe. Earlier runs could not reach it from their sandboxes. exp-08

10. **Claims such as "IDS top-level match gives 3× chance" and "pair choice is 70% of the work" have no source in the repository** and are [CLAIM]. A search of Nomura's interviews also failed to find them; he says only that the pair search is the hardest step. [Conflicts](../findings/conflicts-and-corrections.md)

11. **The six law names are verified; their texts are not.** They are in Nomura's book, which nobody has read. His interviews support Laws 1–3 qualitatively, and he states that kanji ambigrams are mostly impossible while same-name and kana ambigrams are routine. Nomura sources

12. **Claude's v1 CSVs (`EXPLORATORIO_*`) are gothic-only**, although the script's console label says "minimum of the two fonts" — the Mincho matrix was computed and never used. exp-03

## Related

- [Results summary](../findings/results-summary.md)
- [Conflicts and corrections](../findings/conflicts-and-corrections.md)
- [Limitations](../findings/limitations.md)
- [KanjiVG rotation-graph method](../methods/rotgraph-method.md)
