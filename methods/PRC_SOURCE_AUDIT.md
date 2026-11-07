# PRC Source Audit — integration checkpoint

## Context

The PRC construction experiment is distributed in the Drive archive
`sinogram-prc-construction-v1.16.tar.gz`. It contains a dedicated
`prc_construct.py` construction implementation, 28 synthetic unit tests,
and experimental JSON/SVG reports. This branch deliberately introduces the
source-ingestion and coverage contract **before** publishing those larger
modules. It must not be described as the complete PRC implementation.

## Reproducibility and provenance

- Source: Make Me a Hanzi `graphics.txt`, with SHA-256 pinned in
  [the downloader](../scripts/download_prc_sources.sh).
- Regional tag: `cn-s`, separate from `jp`.
- Coverage: `code/prc_inventory.py` reports source SHA-256, inventory
  denominator, matched count, and missing characters. A TCC transcription is
  optional and requires its own pin and licence check.
- Only source geometry is fetched; no third-party dictionary is bundled.
- Full source assets, experimental logs, and the 113 MB full-grid export are
  not committed to Git history.

## Independent verification still needed

The internal v2.0.6 roadmap reports an improvement in PRC symmetric ink
from centre optimisation, modest effects from terminal reconciliation, and
stronger gains from 3×3 sector thickness control. **These are source
reports, not independently reproduced claims in this branch.**

Before integrating the construction module, check the numerical results
against pinned geometry, test retention >= 0.90 and ink growth <= 1.30,
compare identical cohorts at every stage, and publish a script-derived
table with measurements and checksums. No claim of perceptual legibility
is justified without reader evidence.

The staged pipeline currently remains in draft PRs #1, #2 and #3.
This audit is stacked on #3; do not merge it directly into main while
those prerequisites remain unmerged.
