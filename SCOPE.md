# Scope

> **Two coequal experimental research tracks:** Japanese kanji (2,770 KanjiVG glyphs) **and** Chinese hanzi (6,763 GB2312 codepoints; Make Me a Hanzi). Both investigate natural half-turns, distinct-character pairs, and geometric construction; both have open questions and unvalidated human readability. Their different source glyphs, geometric scales, and regional-form constraints demand separate measurements, **not unequal priority, maturity, or scientific status**.

This document distinguishes shipped research from draft experiments and documents geographic and linguistic boundaries. *Sinograms* here refers to the wider research question, not to a claim that all regional forms are interchangeable or that all Chinese characters are covered.

## What "sinogram" means here

The project name is retained deliberately. It describes the research question —
characters of Chinese origin, wherever they are used — rather than the current
data coverage. Renaming would break existing links and issue references, and
the expansion below is intended to make the name accurate.

## Current coverage on `main`

The two tracks use **different source geometry and ranking methods**. Their counts and scores must not be combined.

| Aspect | Japanese KanjiVG track | Chinese-source GB2312 track |
|---|---|---|
| Character repertoire | 2,770 kanji: 2,136 Jōyō + 634 Jinmeiyō | 6,763 GB2312 codepoints, all present in the pinned source |
| Geometry | Japanese KanjiVG stroke paths | Make Me a Hanzi stroke paths and medians; 9,574 source glyph records |
| Regional form status | KanjiVG Japanese reference paths; other fonts and writing practices not individually certified | MMah source includes simplified and traditional shapes; not individually certified to official Mainland Chinese glyph norms |
| Candidate search | 3,837,835 unordered pairs at coarse grid scale, 5,180 refined rows selected | 106,347 coarse-shortlisted candidate pairs; public explorer shows up to eight partners per glyph |
| Ranking metric | KanjiVG stroke-centreline distances and DT grid approximation | Coarse 37×37 half-turn ink IoU, ranked against the GB2312 repertoire |
| Public interface | [Generator](generator/), [C₂ Lab](demo/c2/), [13 method pages](methods/), [Reader Gallery](evaluation/recognition/) | [PRC Explorer](prc/), [11 method pages](methods/), [Reader Gallery](evaluation/recognition/) |
| Human reading validation | Not established | Not established |

The original browser generator retains 5,180 refined Japanese-track measurements (2,410 distinct pairs plus 2,770 self-pairs), vector paths embedded for 432 characters and optional on-demand loading. Inputting a Chinese character **does not switch its geometry source**; use the independent PRC Explorer for Chinese-source screening.

### What the published numbers mean

`Hausdorff`, `Chamfer` and `RMS` are **geometric distances between stroke
centre-lines**, normalised by the 109-unit KanjiVG box. They are candidate
*rankings*, not probabilities of legibility.

Two distinct scales appear in the datasets and must not be mixed:

- **Exact point-cloud** distances — `data/rotation_pairs.csv`,
  `data/c2_class.csv`.
- **Grid distance-transform approximations** — `data/rotation_pairs_top5000.csv`.

[`data/README.md`](data/README.md) is the reference for which file uses which
scale.

## Chinese research track — PRC-source geometry

The [PRC Explorer](prc/) reads a measured shortlist of 6,763 GB2312 characters using Make Me a Hanzi geometry, rather than Japanese KanjiVG vectors. The pinned input includes 9,574 source glyph records and fully covers the GB2312 repertoire. Its 106,347 coarse-screened candidate pairs are **not** fine-grid exact results, not a confirmed Mainland normative form certification, and not validated human-readable ambigrams. Source-derived rendering stays with the Arphic Public License; [the research method](methods/PRC_COARSE_SEARCH.md) and [source audit](LICENSE-AUDIT.md) describe the boundaries. Future regional inventories (including a verified official 2013 TCC transcription) and exact PRC refinement are separate tasks.

## Integrated geometry correction

[PR #19](https://github.com/ClaudioDrews/sinogram-ambigram/pull/19) incorporated measured half-width rendering on `main` while retaining byte-identical v1.16 geometry for historical replay. On a separate 32-glyph pinned contour benchmark, original-outline fidelity improved for **32/32** samples (median IoU **0.4743 → 0.9083**). This is not certified regional shape fidelity or human reading validation; see [method](methods/PRC_WIDTH_SEMANTICS.md) and [findings](findings/prc-width-contour-fidelity.md).

## Historic experiment PRs and integrated operator examples

- [#13 — original PRC thickness draft](https://github.com/ClaudioDrews/sinogram-ambigram/pull/13) was **not merged directly**. Its correction reached `main` through protected PR #19; #13 remains open for provenance. [#14 — R-ODD](https://github.com/ClaudioDrews/sinogram-ambigram/pull/14), [#15 — harmonic field](https://github.com/ClaudioDrews/sinogram-ambigram/pull/15), and [#16 — A/B stroke fusion](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16) remain separate original PR histories; their tested R-ODD, harmonic and A/B algorithms and tests are integrated via PR #28, with real pinned-source outputs.
- [#17 — blind VLM-reading pilot](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17) is **draft**. It documents a preselected 52-image, 208-observation automated-reading experiment, with reproducible scoring and a source-pinned generator. Its self-rotation dual-reading counts range from 10/20 (historical) to 15/20 (harmonic); both tested distinct-character pairs failed dual recognition. Model recognition is not human validation.
- The pilot's unlabelled images are distributed through a reproducible, separately licensed workflow artifact rather than being silently relicensed under MIT.

## What is explicitly not here

- **The original Japanese Generator** still uses Japanese forms, even for Chinese text input. **The separate PRC Explorer** uses Make Me a Hanzi source glyphs, which include simplified and traditional forms and are not individually certified against a normative character-form table.
- **No JP/CN-S mixing.** Pair searches occur separately within each labelled repertoire. The PRC-source GB2312 repertoire is not yet sufficient to certify every source glyph as a particular regional canonical form.
- **No validated perceptual threshold.** There is no calibrated ε. The
  thresholds in the code are geometric screening cut-offs.
- **No human reading validation.** A draft blind **VLM** pilot exists, but no calibrated ε, controlled native-reader study, or confirmed human-readable A↔B construction has been published. All alleged ambigrams remain *candidates*. See [`findings/limitations.md`](findings/limitations.md).
- **No word-level or phrase-level work.** The unit of analysis is a single
  glyph. Rotating a word reverses its order as well as each glyph.
- **No 90° rotation, no mirroring, no figure–ground inversion.** Only the
  half-turn is in scope.

## Historical inventory sequencing is not research priority

KanjiVG was adopted in early experiments because its 2,770 Jōyō/Jinmeiyō inventory is bounded, documented and available as vector paths. Later work independently acquired MMah geometry and covers all 6,763 GB2312 codepoints. **This chronological sequence does not give Japanese kanji priority over Chinese hanzi in the scope, methodological ambition or publication. Both are coequal and experimental.**

It is also a limitation: historical Japanese-track results measure Japanese kanji geometry; the later, separate PRC-source track must be interpreted using its own source, conventions and metric. Neither certifies every regional glyph form.

## Expansion status and remaining work

1. **Completed for the source-screening stage:** licence assessment, checksum-pinned Chinese stroke ingestion, GB2312 codepoint inventory and coarse candidate ranking. See [source reproduction](findings/prc-source-reproduction.md) and [PRC screening method](methods/PRC_COARSE_SEARCH.md).
2. **Open:** certify source glyphs per region and shape; GB2312 codepoint coverage alone is not a certified simplified Chinese font. Preserve explicit source and regional-form metadata and avoid mixing incompatible conventions.
3. **Open:** improve detailed PRC pair construction and test genuine structural A↔B transformations. Draft experimental operators have not demonstrated a legible different-character pair.
4. **Open:** validate perceptions on a representative preregistered sample, including blind human native readers and genuine-/malformed-glyph controls. The small VLM pilot is preliminary and not an independent held-out generalization test.
5. **Ongoing:** distinguish licences for original code, KanjiVG-adapted graphics and Arphic-derived geometry; do not relicense images by implication.

## How to read the results

- A pair at the top of the ranking is a **geometric candidate**: its strokes
  align well after a half-turn.
- Whether it is *readable to humans* remains a perceptual question. A draft VLM pilot supplies limited automated-reading observations, not a human validation.
- The generator produces an experimental drawing to be judged by eye. Rotate it,
  compare it with both reference characters, and report what you see. If it
  does not read, that is a useful observation and an issue-worthy one.

## Related

- [`README.md`](README.md) — project overview and live demonstrations
- [`findings/limitations.md`](findings/limitations.md) — what the research does not establish
- [`findings/results-summary.md`](findings/results-summary.md) — measured, derived and claimed results, separated
- [`data/README.md`](data/README.md) — dataset contents and metric provenance
- [`LICENSE-AUDIT.md`](LICENSE-AUDIT.md) — obligations per source
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to run, test and propose changes
## Public method coverage

Both experimental tracks now have dedicated illustrated pages for every documented method family and an example in the [Native Reader Gallery](evaluation/recognition/). The [method catalog](methods/catalog.json) and [full inventory](methods/RESEARCH_TRACKS.md) enumerate **13 Japanese** and **11 Chinese** methods, including seven Japanese historical screening variants whose worked illustrations use contemporary source paths (not original historical renderings), and **22 source-pinned PRC method examples** from checksum-pinned MMah source. Failure/no-op is reported as such, including the A/B fusion results. No controlled native-reader validation has been established.
