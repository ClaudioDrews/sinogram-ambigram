# PRC Source Audit — verified integration status

**Last updated: 2026-11-07.** This document records source and release
boundaries after the integration of PRs #1–#11 into `main`. Earlier text
referring to draft branches and experiments that had not been reproduced
was superseded by completed GitHub Actions runs.

## Provenance and licence

- Source: Make Me a Hanzi `graphics.txt`, fixed to upstream commit
  `bddc96d41bef78427ed0e034e9f7e31d71fd1b92` and SHA-256
  `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
  Fetching is done by [the pinned downloader](../scripts/download_prc_sources.sh).
- `graphics.txt` contains both simplified and traditional Chinese forms,
  under the [Arphic Public License](../licenses/ARPHICPL.TXT).
  Raw geometry and derived bitmap caches are not committed as MIT assets.
  See [NOTICE](../NOTICE.md) and the [licence audit](../LICENSE-AUDIT.md).
- `jp` KanjiVG and `cn-s` PRC-source pair rankings are computed separately.
  The source's per-codepoint presence is not a certification of its regional
  normative glyph form.

## Checks completed

| Check | Independent evidence |
| --- | --- |
| Source ingestion | Pinned 30,778,076-byte `graphics.txt`; 9,574 records; two byte-identical complete median caches. [Run](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42379382585) |
| Regional coverage | 6,763 of 6,763 GB2312 codepoints found in the pinned source. This is codepoint coverage, not normative glyph certification. |
| Coarse ranking | 106,347 candidate pairs from complete 37×37 screening; scores are approximate and not readability probabilities. [Run](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42381308937) |
| Published v1.16 archive | Canonical CSV with 120 centre/extremity and 53 sector rows; schema and aggregate-statistic regression tests. |
| **Independent source replay of the published cohorts** | Pinned MMah source, 120/120 centre cases, 53/53 sector cases and six representatives recomputed. The 120/53 individual scores and the historical summary agree to absolute 2e-12. [Run](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42386763335) |
| Public site | The [PRC explorer](../prc/) and its measured numeric `catalog.json` were published through GitHub Pages. It is a coarse candidate browser, not a complete construction generator. |

## Scientific boundary

The [v1.16 source replay](PRC_V116_REPRODUCTION.md) uses **frozen candidate
cohorts**. It verifies the measurements from source glyphs, but does not
replay the full original process that selected those 120/53 candidates.
The historical selection scripts remain in the research archive referenced
by the reproduction guide, rather than in this Git tree. This distinction
is a remaining provenance limitation, not a reason to deny the successful
source-level numerical check.

Source ink overlap and constraints (retention at least 0.90, growth at most
1.30 for the sector run) are mechanical measurements. They do **not**
establish that a human reader can recognize either orientation. Reader
evaluation is a post-publication research stage and is not a release gate.

The original 2013 TCC inventory transcript, its licensing and formal
per-glyph regional certification are also separate pending research
deliverables. No source-derived graphic is relabelled as MIT here.
