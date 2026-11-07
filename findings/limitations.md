# Limitations of the Research and Tests

This document distinguishes **historical Japanese-track limitations** from the **current PRC-source implementation on `main`** and **separate draft PR research**. Older observations are retained as historical provenance; they must not be misread as claims about the capabilities of the entire present repository. See the [project overview](../README.md) and [scope](../SCOPE.md).

## L1. Evidence base

1. **No controlled human native-reader validation.** The [draft VLM pilot](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17) contains 52 images and 208 automated-recognition observations; it is **not** a human reading study, a calibrated ε threshold or a 100–200-pair judgement sample. All proposed ambigrams remain unverified human-reading candidates.
2. **Heterogeneous historical Japanese experiments at very different scales**: 42 chars (GPT), 29 (GLM), 113 (Mistral), 2,136 for self-rotation (Kimi) and for Claude's filter, and 2,770 glyphs over all pairs (MiniMax, exp-08). A complete pair search now exists, but no pair search has been run under a **human-validated** metric: the MiniMax ranking is a geometric proxy whose ranking biases are documented and unresolved (X1–X8, CR1–CR7).
3. **Historical source heterogeneity.** Among the older model-generated experiment reports, KanjiVG was used in only one run (MiniMax exp-08); another used a separate median dataset and others used font rasters. **This is not a statement about the new PRC-source pipeline**, which pins and checksums Make Me a Hanzi geometry.
4. **Historical font-lineage dependence.** Most early font-raster experiments used Source Han/Noto/Sarasa; one self-rotation study included Mincho. Japanese/Chinese regional form differences remain consequential. The separate MMah-based PRC track reduces reliance on Japanese KanjiVG input for Chinese candidates, but its regional source forms still require individual normative certification.
5. **Historical IDS layer barely exercised.** In the early experimental runs, most decomposition attempts were blocked or unvalidated; one documented CHISE algebra recall was only 5/100 (non-validating). Symbolic decomposition is not yet an established validated construction method. Atomic components such as 甲 and 未 present decomposition limitations.
6. **Lost artefacts**: Claude's scratch files (`res_*.npz`, `w1.npz`, `cand.json`, `trees.json`, CHISE IDS files — confirmed absent; Claude's zip itself is complete in `claude-run/`), Kimi's code/output, GLM's script, the GPT prototype zip as an archive (unpacked files present) — the runs cannot all be reproduced from the folder; Claude's can be regenerated with CHISE data.
7. **Runs are not independent**: GPT's third turn and later runs read earlier outputs; ordering is inferred, not timestamped.
8. **Provenance of syntheses**: `earlier rule synthesis`, `earlier synthesis`, `earlier visual-analogy notes`, `earlier candidate catalogue` carry no author/tool label; the owner says they were probably produced by Google NotebookLM/Gemini, which makes many errors → claims resting only on them are unverified (source inventory).

## L1a. Current PRC-source track and the blind VLM pilot

- **Published on `main`:** independent PRC-source geometry from a pinned Make Me a Hanzi revision (9,574 source glyph records), 6,763/6,763 GB2312 codepoint coverage, 106,347 coarse geometric shortlisted candidate pairs, and a public PRC Explorer. These numbers are **not** fine-grid recognition scores or certification of simplified/traditional glyph forms. See [PRC screening](../methods/PRC_COARSE_SEARCH.md) and [source reproducibility](prc-source-reproduction.md).
- **Still unresolved:** regional font-form certification, general-purpose distinct-character stroke construction, calibrated perceptual success, native human reading studies, and representative held-out screening.
- **Experimental draft PRs:** [thickness](https://github.com/ClaudioDrews/sinogram-ambigram/pull/13), [R-ODD](https://github.com/ClaudioDrews/sinogram-ambigram/pull/14), [harmonic](https://github.com/ClaudioDrews/sinogram-ambigram/pull/15), [A/B fusion](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) and the [blind VLM pilot](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17) are **not merged to `main`**.
- **VLM pilot:** the self-rotation task produced 10/20 both-orientation recognitions on historical geometry, 14/20 on thickness-fixed geometry, 13/20 for R-ODD and 15/20 for harmonic. The distinct-character pairs 甲↔由 and 韦↔芈 produced **zero** dual-reading successes; A/B fusion did not alter the two examples relative to the thickness-fixed union. Only five self-glyphs and two different-character pairs were tested. The four models are not independent human subjects. Results do **not** establish generalization, a winning method or human readability.
- **Geometric proxies remain distinct:** KanjiVG centreline distances, PRC coarse IoU, filled-ink symmetry and VLM exact character outputs are **not interchangeable metrics**.
- **Licensing:** Japanese KanjiVG-derived artwork and PRC MMah-derived geometry have different upstream licences. Experimental source-derived PNGs must not silently inherit the MIT licence of original code.

## L2. Metric limits (measured by the runs themselves)

Font optics (inner bars ≈5% em above centre), taper in Mincho, ink-mass blindness (甲), slot-size convention (昌/吕), alignment policy, thin-stroke IoU hypersensitivity, skeleton artefacts — see [metrics-comparison](../methods/metrics-comparison.md). Claude's v2 is a *candidate generator*, not a decision rule; its thresholds are uncalibrated.

## L3. Model/theory limits

1. The ε criterion is a model; the "iff" needs conditions; ε unknown ([existence criterion](../theory/existence-criterion.md)).
2. IDS algebra is symbolic: tree equality ≠ visual equality; leaf rotation partners must be supplied or measured; ⿻ undecided.
3. Nomura's six laws are known by **names only** (names confirmed on the publisher page; texts only in the unread book; his interviews give only qualitative support for Laws 1–3 — nomura-sources-and-findings); their formalisations are the AIs' interpretations; the book itself was not read (nomura doc).
4. The Inoue–Takahashi pipeline is described here from the full PDF; its results are on hiragana and do **not** transfer to kanji without testing ([paper doc](../methods/inoue-takahashi-2020.md)).
5. Word-level lemma assumes a block layout; vertical writing, punctuation, kana/latin mixtures untreated.
6. Scope is now **explicitly split** between Japanese KanjiVG and a PRC-source GB2312 track, but **regional shape certification remains unresolved**. SC/TC/JP/KR variations can change geometry; the two current tracks must not be mixed as if they were normatively equivalent.

## L4. Tool-level gaps

**No human-validated general-purpose generator or recognizer.** However, the repository **does have** a published Japanese KanjiVG-based browser Generator with rotatable/downloadable SVG, a 16-example Rotation Lab and a separate Chinese-source GB2312 candidate browser. The Chinese track also includes reproducible stroke-median ingestion, repertoire construction and 106,347 coarse geometric candidate pairs. These are **research tools, not a completed or human-validated PRC A↔B generator**. The unmerged draft branches add PRC stroke-width construction variants and automated VLM recognition experiments. See [PRC Explorer](../prc/), [scope](../SCOPE.md) and [PR #17](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17).

## L5. Documentation limits

* Some historical **private source notes** were originally in Portuguese and were summarized or translated during early consolidation; they are not the repository's publication language. Public research documentation is maintained in English, Chinese and Japanese as appropriate. Reconstructed accounts of private notes are not substitutes for independent source verification.
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

- [Scope](../SCOPE.md)
- [Blind VLM research pilot, draft PR #17](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17)
- [Results summary](../findings/results-summary.md)
- Open questions
- Experiments index
- [Metrics comparison](../methods/metrics-comparison.md)
