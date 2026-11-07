# Scope

> **Currently scoped to Japanese kanji (Jōyō + Jinmeiyō).** Chinese hanzi expansion is
> planned. See the expansion plan below.

This document states exactly what this repository contains today, what it does
not contain, and why. It exists because the project name refers to *sinograms*
(a broad term for Chinese characters) while the measured dataset is a Japanese
kanji inventory. That gap should be visible to anyone who opens the repository,
not discoverable by them.

## What "sinogram" means here

The project name is retained deliberately. It describes the research question —
characters of Chinese origin, wherever they are used — rather than the current
data coverage. Renaming would break existing links and issue references, and
the expansion below is intended to make the name accurate.

## Current coverage

| Aspect | State |
|---|---|
| Inventory | **2,770 glyphs**: 2,136 Jōyō kanji + 634 Jinmeiyō kanji |
| Inventory source | Japanese Wikipedia tables, extracted and frozen in [`data/lists.json`](data/lists.json) |
| Stroke geometry | **KanjiVG**, one canonical SVG per glyph, pinned to commit `70a0b7ae…` |
| Glyph forms | **Japanese** standard forms only. No simplified Chinese, no traditional Chinese, no per-region variants |
| Pair space | 2,770 × 2,771 / 2 = **3,837,835** unordered pairs, including self-pairs |
| Published refined sample | 5,180 rows: 2,410 distinct pairs + 2,770 self-pairs |
| Searched pairs | Full unordered space at grid resolution; exact refinement applied to the 2,500 best grid-ranked candidates plus every self-pair |
| Language | Japanese kanji readings. The semantic fallback in the browser generator is a small hand-curated list, not a dictionary |

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

## What is explicitly not here

- **No simplified or traditional Chinese forms.** Every measurement uses the
  Japanese glyph shape. A Chinese reader looking at a result is seeing a
  Japanese rendering of the character.
- **No per-region pairing.** Pairs are formed inside a single inventory. A
  Japanese form is never compared against a Chinese form, because that
  comparison would measure the difference between writing systems rather than
  anything about the characters.
- **No validated perceptual threshold.** There is no calibrated ε. The
  thresholds in the code are geometric screening cut-offs.
- **No human validation of any result.** No reading test, no ε calibration, no
  native-reader study has been published. Every ambigram in this repository is
  a *candidate*. See [`findings/limitations.md`](findings/limitations.md).
- **No word-level or phrase-level work.** The unit of analysis is a single
  glyph. Rotating a word reverses its order as well as each glyph.
- **No 90° rotation, no mirroring, no figure–ground inversion.** Only the
  half-turn is in scope.

## Why the Japanese inventory comes first

The Japanese Jōyō + Jinmeiyō inventory has a rare property: it is small,
stable, publicly documented, and its glyph shapes are canonical in a single
maintained vector source. That makes it a defensible testbed for the geometry
before the method is pointed at a larger, more heterogeneous inventory.

It is also, precisely, a limitation: the result measures Japanese kanji
geometry. Every claim in [`findings/`](findings/) must be read with that
boundary in place.

## Expansion plan

The planned expansion proceeds in stages. Each stage is gated on the previous
one producing sound results, not on a calendar.

1. **Audit the licence of every new source** before ingestion. Chinese stroke
   data comes from sources with different, sometimes incompatible terms; see
   [`LICENSE-AUDIT.md`](LICENSE-AUDIT.md).
2. **Ingest Chinese stroke geometry** in a normalised representation that
   matches the existing pipeline, with a `source` field on every item.
3. **Model regional variants explicitly.** A character's simplified,
   traditional, Japanese, Taiwanese and Korean forms are different shapes and
   must be separate objects, not a lookup of one canonical form.
4. **Build one rotation graph per regional convention.** Pairs are only formed
   within the same convention.
5. **Report coverage per inventory** rather than a single global figure, and
   state the absolute coverage honestly, including the gaps.

## How to read the results

- A pair at the top of the ranking is a **geometric candidate**: its strokes
  align well after a half-turn.
- Whether it is *readable* is a perceptual question. This repository has not
  answered it.
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