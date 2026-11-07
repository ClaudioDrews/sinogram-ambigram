# Limitations of the Research and Tests

Evidence labels are defined in the [repository README](../README.md). Each limitation cites where it comes from (stated by a source, or observed during this documentation).

## L1. Evidence base

1. **No controlled native-reader validation** — no blind reading test, no ε calibration, no 100–200-pair judgement sample (proposed in `comparative discussion`, `earlier planning outline`). All "ambigram" labels are geometric proxies.
2. **Heterogeneous experiments at very different scales**: 42 chars (GPT), 29 (GLM), 113 (Mistral), 2,136 for self-rotation (Kimi) and for Claude's filter, and 2,770 glyphs over all pairs (MiniMax, exp-08). A complete pair search now exists, but no pair search has been run under a **human-validated** metric: the MiniMax ranking is a geometric proxy whose ranking biases are documented and unresolved (X1–X8, CR1–CR7).
3. **KanjiVG was used in exactly one run** (MiniMax, exp-08), although every source recommends it. Mistral used another median dataset with known quirks; the other runs used font rasters.
4. **Single font lineage** (Source Han/Noto/Sarasa) for almost everything; Mincho only in Kimi (self-rotation) and Claude's control. Noto SC vs JP form differences (Claude's objection to GLM).
5. **IDS layer barely exercised**: GPT's CHISE download failed; Kimi's IDS blocked; only Claude loaded CHISE, and its algebra recall was 5/100 (non-validating). Atomic components (甲, 未) are not decomposed by CHISE.
6. **Lost artefacts**: Claude's scratch files (`res_*.npz`, `w1.npz`, `cand.json`, `trees.json`, CHISE IDS files — confirmed absent; Claude's zip itself is complete in `claude-run/`), Kimi's code/output, GLM's script, the GPT prototype zip as an archive (unpacked files present) — the runs cannot all be reproduced from the folder; Claude's can be regenerated with CHISE data.
7. **Runs are not independent**: GPT's third turn and later runs read earlier outputs; ordering is inferred, not timestamped.
8. **Provenance of syntheses**: `earlier rule synthesis`, `earlier synthesis`, `earlier visual-analogy notes`, `earlier candidate catalogue` carry no author/tool label; the owner says they were probably produced by Google NotebookLM/Gemini, which makes many errors → claims resting only on them are unverified (source inventory).

## L2. Metric limits (measured by the runs themselves)

Font optics (inner bars ≈5% em above centre), taper in Mincho, ink-mass blindness (甲), slot-size convention (昌/吕), alignment policy, thin-stroke IoU hypersensitivity, skeleton artefacts — see [metrics-comparison](../methods/metrics-comparison.md). Claude's v2 is a *candidate generator*, not a decision rule; its thresholds are uncalibrated.

## L3. Model/theory limits

1. The ε criterion is a model; the "iff" needs conditions; ε unknown ([existence criterion](../theory/existence-criterion.md)).
2. IDS algebra is symbolic: tree equality ≠ visual equality; leaf rotation partners must be supplied or measured; ⿻ undecided.
3. Nomura's six laws are known by **names only** (names confirmed on the publisher page; texts only in the unread book; his interviews give only qualitative support for Laws 1–3 — nomura-sources-and-findings); their formalisations are the AIs' interpretations; the book itself was not read (nomura doc).
4. The Inoue–Takahashi pipeline is described here from the full PDF; its results are on hiragana and do **not** transfer to kanji without testing ([paper doc](../methods/inoue-takahashi-2020.md)).
5. Word-level lemma assumes a block layout; vertical writing, punctuation, kana/latin mixtures untreated.
6. Scope not yet fixed: Japanese Jōyō vs wider hanzi/hanja/hangul; regional glyph forms (SC/TC/JP/KR) change geometry.

## L4. Tool-level gaps

no human-validated general-purpose ambigram generator, no candidate browser, no UI; no stroke-level vector data pipeline; no recogniser. A full pair catalogue and a partial ambigram generator exist (exp-08), but nothing turns a pair into a distributable SVG. See tool status.

## L5. Documentation limits

* Sources are in Portuguese; this documentation translated and condensed them. Quotations are paraphrases.
* Google Docs/Sheets were converted by pandoc/openpyxl for the `test-files` copies; images embedded in the original docs (e.g. AmbiGen illustrations in GPT chats) may be missing from the Markdown copies.
* The `earlier planning outline` (13 slides, mostly images) was read as text; slide imagery was not described.
* The Nomura sources found in the second pass (interviews, blog, X account, publisher page) were read live on 2026-11-01 (findings); X searches are limited (25 posts per call, older timeline not enumerated).
* The external web sources cited by the reports (interviews, blogs, KanjiVG pages, Unicode charts) and Nomura's book were not retrieved or verified by this documentation, except the Reversible Faces Benchmark repository (checked on GitHub) and the paper PDF.

## L6. Limits of the MiniMax baseline and of its independent review

1. **One shape per glyph.** KanjiVG gives one canonical outline; real ε includes typeface, hand and stroke weight ([rotgraph method](../methods/rotgraph-method.md) §10).
2. **Glyph level, not word level**; 180° only.
3. **Rotation centre is fixed at the box centre** (109 − x), with no translation or scale alignment. This limit is absent from both limit lists of the method document and was raised in the review (CR3).
4. **Skeleton metric, not ink metric**: it does not penalise "wrong stroke type in the right place" and over-ranks frame glyphs (圃, 園, 圏, 菌).
5. **Density bias**: denser glyphs score better simply because they fill the box (Spearman ρ between H and skeleton length = −0.43 on self-pairs, CR1).
6. **Hub bias**: a few glyphs concentrate the top of the ranking (圃 appears in 7 of the first 25 distinct pairs; X7).
7. **Graph reliability**: edges are only trustworthy up to H ≈ 0.085–0.09; above that the count is an artefact of which candidates were refined (CR4).
8. **Two H scales in the same folder**: grid distances and exact distances differ (X8) and must not be mixed in one table.
9. **The independent review was not run in the owner's environment**, on the owner's data, nor against `rotgraph.zip`; its numbers are [REPORTED] until reproduced (exp-08 §Independent review).

## Related

- [Results summary](../findings/results-summary.md)
- Open questions
- Experiments index
- [Metrics comparison](../methods/metrics-comparison.md)
