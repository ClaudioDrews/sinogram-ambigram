# Sinogram Ambigram Generator — Browser PoC

A self-contained HTML proof of concept for 180° rotational ambigrams drawn from **Japanese KanjiVG geometry**. Although its interface accepts Chinese characters, its ranking and source glyphs are Japanese forms; use the separate [Mainland Chinese Explorer](../prc/) for PRC-source rankings. It works locally by opening `index.html` and can be deployed without a build step on GitHub Pages.

## Try it

Open [`index.html`](index.html), type one Han character, select Japanese or Chinese, and choose **Generate candidates**. Try `甲`, `由`, `目`, `回`, `国`, and `美` (the last one exercises the small semantic-alternative fallback). Select a candidate, switch between construction methods, rotate the generated SVG, or save it. The interface supports English, Chinese (Simplified), and Japanese.

## What is implemented

1. **Direct geometric candidate search.** The embedded index is a curated export of all **5,180 refined pair rows** in [`../data/rotation_pairs.csv`](../data/rotation_pairs.csv), including **2,770 self-pairs**. The numeric cut `H <= 0.115` is an adjustable exploratory shortlist threshold, not a legibility decision boundary. The source dataset is *not* a complete exact refinement of all 3.84 million pairs.
2. **Real vector glyphs.** The page embeds the stroke paths for **432 characters** from the original KanjiVG-based experimental HTML catalogue. For other characters in the dataset it attempts to load KanjiVG paths on demand from jsDelivr at the pinned KanjiVG commit recorded in [`../data/KANJIVG_PIN.txt`](../data/KANJIVG_PIN.txt). The embedded subset works fully offline; on-demand glyph retrieval requires a network connection and is best effort.
3. **Four geometrical views.** Stroke-salience blending (thick overlapping strokes, thin exclusive strokes), direct overlay, common-stroke extraction, and C₂ symmetry. They are separate geometry operations used to inspect or synthesize *candidate drawings*; they do not reproduce every algorithm from the research literature.
4. **Small lexical fallback.** When the selected character has no shortlisted drawable geometric candidate, the app tries a tiny, explicitly enumerated list of **sense-dependent related alternatives** for Japanese or Chinese. These are examples rather than a validated synonym lexicon; no dictionary API or language model is connected. The result makes the substitution visible.
5. **Export and feedback.** SVG download, 180° rotation, explanation of the selected method, source/reference comparison, and a copyable feedback template. The author is **Claudio Drews** ([GitHub](https://github.com/ClaudioDrews)). Feedback can be emailed to [Claudio Drews](mailto:21au6i06R3w55891@proton.me), with the current character pair and method included in the draft.

## What it does not implement

- Full cross-lingual synonym matching, word-level composition, a general IDS rewrite engine, a trained recognizer, or optimized deformation beyond overlay/salience rules.
- Exhaustive candidate search across all Unicode ideographs. The 2,770-character ranking comes from Japanese Jōyō and Jinmeiyō lists, not the complete Chinese character inventory.
- An automated judgement that the generated result is legible. Visual assessment and feedback are part of the intended exploratory workflow.

## GitHub Pages

Keep this folder in the repository as `generator/`. After publishing, the URL is `https://OWNER.github.io/REPOSITORY/generator/` if GitHub Pages is enabled for the repository's publishing source. This is a **static site**: no Python runtime, server, API key, or installation is needed.

For a link in the repository README:

```markdown
[Try the Ambigram Generator](generator/)
```

For a GitHub preview of the HTML source, open `generator/index.html`; for the *interactive application*, open its GitHub Pages URL or the downloaded HTML in a browser.

## Scientific and technical provenance

- Rotation graph and refined distances: [`../data/rotation_pairs.csv`](../data/rotation_pairs.csv) (source data used to prepare the embedded index).
- Stroke geometry: KanjiVG project, <https://kanjivg.tagaini.net/> and <https://github.com/KanjiVG/kanjivg>.
- Salience and geometry: research notes and [`../code/make_ambigram.py`](../code/make_ambigram.py), adapted into client-side JavaScript (the implementation is not bit-for-bit equivalent to that Python script).
- Theory: [`../theory/existence-criterion.md`](../theory/existence-criterion.md), [`../theory/ids-rotation-algebra.md`](../theory/ids-rotation-algebra.md), and [`../methods/rotgraph-method.md`](../methods/rotgraph-method.md).

**Licensing:** Embedded stroke data is derived from **KanjiVG, CC BY-SA 3.0**. Preserve attribution and review share-alike obligations before distribution. The HTML code and the numeric research data may have distinct licenses; do not silently relicense the KanjiVG-derived paths as MIT.
