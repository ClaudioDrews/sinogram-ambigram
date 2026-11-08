# Methods, examples and evidence inventory

**Both Japanese kanji and Chinese hanzi are equal-priority experimental research tracks.** This file inventories *all* the method families that the public examples cover. A method can be a geometric candidate search, a source-glyph rotation, or a construction operator; these are distinct kinds of experiments, not interchangeable "generators".

**Reproducibility update (2026-11-08):** The original Chinese R-ODD, harmonic and A/B fusion PRs remain open and separate for historical provenance, but their tested algorithm modules and tests were copied into the integrated research publication branch. The pinned-source [output manifest](../evaluation/recognition/generated/manifest.json) now contains **22 genuine PRC-source algorithm examples spanning 11 categories**. The original 48-item Japanese evaluation protocol is unchanged.

## Evidence distinction

- **Historic search metric example:** A visual explanation using current pinned KanjiVG paths, *not* a falsely attributed reconstruction of GPT, GLM, Claude, Kimi or Mistral's historic font datasets.
- **Natural candidate:** Source glyph rotated unchanged, possibly against another predicted source character; geometric proximity is not readability.
- **Construction output:** Image emitted by the named algorithm. Unchanged pixels/no-op are genuine negative findings and remain visible.
- **Recognized ambigram:** Requires independent human native-reader evaluation, which this project has not established.

## Full methods matrix

| Track | Category | Method and illustrated page | Example | Implementation / outcome |
| --- | --- | --- | --- | --- |
| **Japanese · KanjiVG** | search | [GPT · raster IoU](jp-gpt-raster-iou/) | 甲 ↔ 由 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [GLM · translated raster IoU](jp-glm-translated-iou/) | 甲 ↔ 由 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [Claude v1 · tolerant skeleton F-score](jp-claude-skeleton-f1/) | 目 ↔ 目 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [Claude v2 · W1 + warp + structure](jp-claude-w1-warp/) | 甲 ↔ 由 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [Kimi · FFT + raster IoU](jp-kimi-fft-iou/) | 目 ↔ 目 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [Mistral · median point clouds](jp-mistral-medians/) | 王 ↔ 玉 | Historical search/comparison |
| **Japanese · KanjiVG** | search | [MiniMax · KanjiVG rotation graph](jp-minimax-rotgraph/) | 甲 ↔ 由 | Implemented geometric search |
| **Japanese · KanjiVG** | visual | [Natural C₂ / unmodified self-rotation](jp-natural-self/) | 目 ↔ 目 | Source-form geometric candidate |
| **Japanese · KanjiVG** | visual | [Natural distinct A↔B candidate](jp-natural-pair/) | 甲 ↔ 由 | Source-form geometric candidate |
| **Japanese · KanjiVG** | visual | [Direct overlay](jp-overlay/) | 甲 ↔ 由 | Exploratory constructed drawing |
| **Japanese · KanjiVG** | visual | [Shared-stroke salience](jp-salience/) | 甲 ↔ 由 | Exploratory constructed drawing |
| **Japanese · KanjiVG** | visual | [Shared structure extraction](jp-shared/) | 王 ↔ 玉 | Diagnostic, not finished ambigram |
| **Japanese · KanjiVG** | visual | [C₂ geometric blend](jp-c2-blend/) | 田 ↔ 田 | Exploratory constructed drawing |
| **Chinese · MMah** | search | [Natural C₂ / self-rotation](cn-natural-self/) | 田 ↔ 田 | PRC-source geometric candidate |
| **Chinese · MMah** | search | [Natural distinct-character search](cn-natural-pair/) | 甲 ↔ 由 | PRC-source geometric candidate |
| **Chinese · MMah** | construction | [Simple source union](cn-source-union/) | 甲 ↔ 由 | Actual PRC operator output |
| **Chinese · MMah** | construction | [Rotation centre optimisation](cn-centre-optimisation/) | 田 ↔ 田 | Actual PRC centre-selection output |
| **Chinese · MMah** | construction | [Terminal / extremity reconciliation](cn-extremity-reconciliation/) | 田 ↔ 田 | Actual experimental operator output |
| **Chinese · MMah** | construction | [Deterministic sector thickness (R-SECT)](cn-sector-deterministic/) | 田 ↔ 田 | Actual experimental operator output |
| **Chinese · MMah** | construction | [Constrained sector thickness search](cn-sector-search/) | 目 ↔ 目 | Actual experimental operator output |
| **Chinese · MMah** | construction | [Corrected measured half-width](cn-width-fixed/) | 田 ↔ 田 | Actual corrected raster baseline |
| **Chinese · MMah** | construction | [R-ODD local compensation](cn-r-odd/) | 田 ↔ 田 | Actual experimental operator output |
| **Chinese · MMah** | construction | [C₂-even harmonic thickness field](cn-harmonic/) | 目 ↔ 目 | Actual experimental operator output |
| **Chinese · MMah** | construction | [Registered A/B stroke fusion](cn-ab-fusion/) | 甲 ↔ 由 | Actual experimental operator output; measured no-op |

Each of the **24 methods above has its own HTML page** with a rotatable visual, formula, evidence note, source links and an animated half-turn. [Open the trilingual illustrated Methods index](index.html). [Native Reader Gallery](../evaluation/recognition/) samples every listed method family.

## Chinese source-derived algorithm outputs

Unlike an unexecuted proposal, the following examples are computed using the actual Python operator, not a replacement illustration. Source geometry is pinned to [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) commit `bddc96d41bef78427ed0e034e9f7e31d71fd1b92`, SHA-256 `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.

| Method | Real SVG examples | Did the output differ from the source? | Reproduction |
| --- | ---: | --- | --- |
| [Natural C₂ / self-rotation](cn-natural-self/) | [田↔田](../evaluation/recognition/generated/cn-natural-self-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-natural-self-30446-30446.svg) | unchanged from source / unchanged from source | [Builder](../code/build_prc_method_gallery.py) |
| [Natural distinct-character search](cn-natural-pair/) | [甲↔由](../evaluation/recognition/generated/cn-natural-pair-30002-30001.svg) · [王↔玉](../evaluation/recognition/generated/cn-natural-pair-29579-29577.svg) | unchanged from source / unchanged from source | [Builder](../code/build_prc_method_gallery.py) |
| [Simple source union](cn-source-union/) | [甲↔由](../evaluation/recognition/generated/cn-source-union-30002-30001.svg) · [王↔玉](../evaluation/recognition/generated/cn-source-union-29579-29577.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [Rotation centre optimisation](cn-centre-optimisation/) | [田↔田](../evaluation/recognition/generated/cn-centre-optimisation-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-centre-optimisation-30446-30446.svg) | unchanged from source / unchanged from source | [Builder](../code/build_prc_method_gallery.py) |
| [Terminal / extremity reconciliation](cn-extremity-reconciliation/) | [田↔田](../evaluation/recognition/generated/cn-extremity-reconciliation-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-extremity-reconciliation-30446-30446.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [Deterministic sector thickness (R-SECT)](cn-sector-deterministic/) | [田↔田](../evaluation/recognition/generated/cn-sector-deterministic-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-sector-deterministic-30446-30446.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [Constrained sector thickness search](cn-sector-search/) | [田↔田](../evaluation/recognition/generated/cn-sector-search-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-sector-search-30446-30446.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [Corrected measured half-width](cn-width-fixed/) | [田↔田](../evaluation/recognition/generated/cn-width-fixed-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-width-fixed-30446-30446.svg) | unchanged from source / unchanged from source | [Builder](../code/build_prc_method_gallery.py) |
| [R-ODD local compensation](cn-r-odd/) | [田↔田](../evaluation/recognition/generated/cn-r-odd-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-r-odd-30446-30446.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [C₂-even harmonic thickness field](cn-harmonic/) | [田↔田](../evaluation/recognition/generated/cn-harmonic-30000-30000.svg) · [目↔目](../evaluation/recognition/generated/cn-harmonic-30446-30446.svg) | changed from source / changed from source | [Builder](../code/build_prc_method_gallery.py) |
| [Registered A/B stroke fusion](cn-ab-fusion/) | [甲↔由](../evaluation/recognition/generated/cn-ab-fusion-30002-30001.svg) · [韦↔芈](../evaluation/recognition/generated/cn-ab-fusion-38886-33416.svg) | identical to union baseline / identical to union baseline | [Builder](../code/build_prc_method_gallery.py) |

**Important:** For centre optimisation, the source ink can be unchanged while its selected rotation centre differs from the box centre. The page and gallery record that centre. For A/B fusion the two published test cases are **pixel-identical to the source-union baseline**; they are not presented as an improved fusion. The source-width correction has its separate 32-glyph original-outline fidelity benchmark, which does *not* measure human legibility.

**Not merged by simple PR merge:** the original experimental PR #14 (R-ODD), #15 (harmonic), #16 (A/B), and #21 (threshold sweep) remain independent experiment discussions. The method modules and real output assets were integrated selectively into this publication branch with tests, not by discarding their evidence or equating metrics.

## Japanese historical provenance and visual-mode distinction

Seven historical algorithm/metric variants were tested in **six code-producing runs** (GPT, GLM, Claude v1/v2, Kimi, Mistral, MiniMax). The earlier run data use different sources and fonts, with noncomparable numeric scales. Every method page shows its intended geometric input and technique, but only current KanjiVG generator modes claim to produce actual current KanjiVG drawings.

Japanese actual visual operations: source-only natural C₂; source-only A↔B comparison; overlay; stroke salience; shared structure; C₂ blend. The `v1-top` and `v2-top` labels in [historic 48-item pilot](../evaluation/items.json) are *selection/ranking strata*, never two independently developed drawing algorithms.

See [metrics comparison](metrics-comparison.md), [ranking method](rotgraph-method.md), [results summary](../findings/results-summary.md), [pair evidence](../findings/pair-evidence-matrix.md), [known biases](../findings/known-biases.md), [C₂ Lab](../demo/c2/).

## Validation gates

1. **Correct source:** Japanese KanjiVG and Chinese MMah geometry remain separate. The Generator’s input-language option does not change its original KanjiVG geometry source.
2. **Actual operation:** Every Chinese constructed example is reproduced by [`code/build_prc_method_gallery.py`](../code/build_prc_method_gallery.py); labels reflect actual algorithms and precise parameters.
3. **Controlled data:** The visual gallery uses its separate [`stimuli.json`](../evaluation/recognition/stimuli.json) and [generated manifest](../evaluation/recognition/generated/manifest.json). It does not silently rewrite the historic 48-item pilot.
4. **Measured nulls:** unchanged source contours, unchanged A/B union, and unsuccessful recognition are reported, not hidden.
5. **No human-legibility inference:** even 22 correctly generated SVGs and successful CI prove only the geometric procedures, not human interpretation.
6. **Source licences:** [KanjiVG CC BY-SA 3.0](../NOTICE.md) and MMah [Arphic Public License](../licenses/ARPHICPL.TXT) apply to adapted assets; the MIT licence does not supersede either.

## Remaining work

Further shape refinement, broader representative glyph sampling, regional-form certification, genuine held-out human native-reader adjudication, and repeatability testing across independent fonts remain open. The project's **scope and documented methods are complete in this index; the science itself remains experimental**.
