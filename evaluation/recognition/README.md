# Reader Gallery — coverage of all explored methods

**Equal experimental tracks:** Japanese kanji (KanjiVG, 2,770-glyph research inventory) and Chinese hanzi (Make Me a Hanzi, 6,763 GB2312 codepoints). Neither has validated human-readable rotational ambigrams.

The [simple Reader Gallery](index.html) keeps the approved UI (English-default EN/中文/日本語 landing, two language choices, tap to rotate a single image, both/one/neither meaning options, notes, next, local CSV/TXT). **No native-speaker eligibility question** is asked, and responses are not transmitted.

## Full current stimulus coverage

| Track | Research methods represented | Configured examples | Important distinction |
| --- | ---: | ---: | --- |
| **Japanese · KanjiVG** | **13** | **20** | Seven historical search-metric inputs are *current source illustrations*, not historic run reproductions; six natural/rendering method categories are current KanjiVG examples |
| **Chinese · MMah** | **11** | **22** (pinned, pre-generated SVGs) | **22 SVGs produced by actual Python operators**. All 11 method families are present, and the gallery loads these examples without a live upstream fetch |

Every listed method links from its gallery card to its **dedicated illustrated page with rotation/animation and explanatory evidence**. The [complete methods map](../../methods/) and [full matrix](../../methods/RESEARCH_TRACKS.md) distinguish historic comparison algorithms, natural source-glyph screens, real constructions and negative/null results.

### Japanese method coverage

- [GPT · raster IoU](../../methods/jp-gpt-raster-iou/) — 甲 ↔ 由 (illustration of search inputs, **not a reproduced historical result**).
- [GLM · translated raster IoU](../../methods/jp-glm-translated-iou/) — 甲 ↔ 由 (illustration of search inputs, **not a reproduced historical result**).
- [Claude v1 · tolerant skeleton F-score](../../methods/jp-claude-skeleton-f1/) — 目 ↔ 目 (illustration of search inputs, **not a reproduced historical result**).
- [Claude v2 · W1 + warp + structure](../../methods/jp-claude-w1-warp/) — 甲 ↔ 由 (illustration of search inputs, **not a reproduced historical result**).
- [Kimi · FFT + raster IoU](../../methods/jp-kimi-fft-iou/) — 目 ↔ 目 (illustration of search inputs, **not a reproduced historical result**).
- [Mistral · median point clouds](../../methods/jp-mistral-medians/) — 王 ↔ 玉 (illustration of search inputs, **not a reproduced historical result**).
- [MiniMax · KanjiVG rotation graph](../../methods/jp-minimax-rotgraph/) — 甲 ↔ 由 (illustration of search inputs, **not a reproduced historical result**).
- [Natural C₂ / unmodified self-rotation](../../methods/jp-natural-self/) — 目 ↔ 目 (actual contemporary KanjiVG geometric operation/source candidate).
- [Natural distinct A↔B candidate](../../methods/jp-natural-pair/) — 甲 ↔ 由 (actual contemporary KanjiVG geometric operation/source candidate).
- [Direct overlay](../../methods/jp-overlay/) — 甲 ↔ 由 (actual contemporary KanjiVG geometric operation/source candidate).
- [Shared-stroke salience](../../methods/jp-salience/) — 甲 ↔ 由 (actual contemporary KanjiVG geometric operation/source candidate).
- [Shared structure extraction](../../methods/jp-shared/) — 王 ↔ 玉 (actual contemporary KanjiVG geometric operation/source candidate).
- [C₂ geometric blend](../../methods/jp-c2-blend/) — 田 ↔ 田 (actual contemporary KanjiVG geometric operation/source candidate).

### Chinese method coverage

- [Natural C₂ / self-rotation](../../methods/cn-natural-self/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Natural distinct-character search](../../methods/cn-natural-pair/) — 甲 ↔ 由 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Simple source union](../../methods/cn-source-union/) — 甲 ↔ 由 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Rotation centre optimisation](../../methods/cn-centre-optimisation/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Terminal / extremity reconciliation](../../methods/cn-extremity-reconciliation/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Deterministic sector thickness (R-SECT)](../../methods/cn-sector-deterministic/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Constrained sector thickness search](../../methods/cn-sector-search/) — 目 ↔ 目 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Corrected measured half-width](../../methods/cn-width-fixed/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [R-ODD local compensation](../../methods/cn-r-odd/) — 田 ↔ 田 (actual [source-pinned SVG examples](generated/manifest.json)).
- [C₂-even harmonic thickness field](../../methods/cn-harmonic/) — 目 ↔ 目 (actual [source-pinned SVG examples](generated/manifest.json)).
- [Registered A/B stroke fusion](../../methods/cn-ab-fusion/) — 甲 ↔ 由 (actual [source-pinned SVG examples](generated/manifest.json)).

The active Chinese Gallery uses the generated, source-pinned 22 SVGs only; the 9 prior browser-sourced examples are retained as historical data in `stimuli.json.cn_legacy_browser_examples` but **are not active stimuli**. The 22 outputs use the actual algorithm paths: source/corrected-half-width, centre optimisation, terminal reconciliation, sector-wise thickness rule/search, R-ODD, even harmonic field and A/B fusion. They are generated deterministically by [`code/build_prc_method_gallery.py`](../../code/build_prc_method_gallery.py) from the pinned licensed source. **A/B fusion is displayed as an honest no-op relative to union** where the rendered pixels are unchanged. For centre optimisation, rotation uses the source-derived selected pivot; it may move without changing ink.

## Experimental protocol and file boundaries

- The [historical 48-item Japanese pilot](../items.json) and [its full protocol](../../methods/HUMAN_EVAL.md) **remain unchanged**, and are never relabelled as multiple original rendering methods just because they came from `v1-top` / `v2-top` selection strata.
- [`stimuli.json`](stimuli.json) contains the simplified Japanese curated example sources and archival Chinese-source browser cases (inactive), with provenance and status for each.
- [`generated/manifest.json`](generated/manifest.json) enumerates all 22 Chinese actual method outputs with source commit/checksum, method, pair, image SHA-256, geometric scores, and whether the output is pixel-identical to a baseline.
- [`index.html`](index.html) displays only one static generated image at a time, turns that *same* image 180° when clicked, and reports method, type and evidence status. Every export includes those fields.
- [Method-specific pages](../../methods/index.html) provide richer interactions separately. They do not complicate the approved reader-rating flow.

**A judgement of "meaning in both orientations" is *not* proof that the reader identified the intended A/B pair**, and the design does not ask for specific character identities. The raw volunteer observations may be exploratory and non-representative; no calibrated perceptual threshold or language-track comparison is justified.

## Reproducibility and licensing

- Generated Chinese SVGS: [`code/build_prc_method_gallery.py`](../../code/build_prc_method_gallery.py) and [GitHub Actions workflow](../../.github/workflows/method-gallery-prc.yml). MMah input commit `bddc96d41bef78427ed0e034e9f7e31d71fd1b92`, SHA-256 `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`. All derived glyph images retain upstream [Arphic Public License](../../licenses/ARPHICPL.TXT).
- Japanese example paths: pinned KanjiVG subset from the actual [Generator](../../generator/index.html), subject to KanjiVG CC BY-SA 3.0.
- [Tests](../../code/test_recognition_lab.py) check method coverage, source isolation, static page behavior and JS syntax. Passing them is not a controlled native reader experiment.
