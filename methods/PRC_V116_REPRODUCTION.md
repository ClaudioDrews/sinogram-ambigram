# Reproducing the PRC v1.16 construction measurements

## What is now versioned

The original 2026-11-07 audit identified a real gap: the repository
published archived numerical tables and a *post hoc* JSON verifier, but it
did not contain a runnable way to recompute the reported quantities from
the source glyphs.

The source-based **fixed-cohort replay** now lives in
[tools/replay_prc_v116.py](../tools/replay_prc_v116.py). Its purpose is to
verify the geometry, not to retroactively reinvent the selection rules.

| Step | Input | Output / check |
| --- | --- | --- |
| Source integrity | Make Me a Hanzi graphics.txt | SHA-256 check against immutable pinned source |
| Frozen cases | 120 pairs from committed standard CSV | Recompute baseline, optimal centre, terminal reconciliation, final score and retention |
| Frozen sectors | 53 pairs from committed standard CSV | Recompute baseline, sector thickness M1, retained ink, growth and constraints |
| Representative experiment | Six named cases | Recompute M1 and optional M2 discrete greedy search |
| Numerical comparison | Replayed values and committed tables | Fail on deviation greater than 2e-12 |
| Summary | Replayed JSON | Run tools/verify_prc_archive.py on newly produced source-derived JSON |

**The replay is not the complete historical discovery pipeline.** It
uses frozen candidate lists rather than independently reproducing the
original all-GB2312 nearest-neighbour selection, interquartile sampling
and frame detection. Those historical stages remain preserved in the
2026-11-07 research archive, which is outside the public code tree.
Thus, this addresses the *metric reproduction* gap while leaving
*cohort-selection provenance* explicitly separate.

## Source identity

- Make Me a Hanzi: https://github.com/skishore/makemeahanzi
- Upstream pinned commit: bddc96d41bef78427ed0e034e9f7e31d71fd1b92
- graphics.txt SHA-256: a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee
- License of glyph source: Arphic Public License, unaltered
  English text in [licenses/ARPHICPL.TXT](../licenses/ARPHICPL.TXT)
- Original full research archive:
  sinogram-prc-construction-v1.16.tar.gz in the owner's project Drive.
  The archived package supplied on 2026-11-07 has SHA-256:
  c689e728f6700409330d0f41549271f009c22fe3f54656b18cb15be80e2bac90.

Original JSON-file SHA-256 digests are recorded separately in
[data/prc/archive-v1.16/prc-archive-summary.json](../data/prc/archive-v1.16/prc-archive-summary.json).
These identify *historical output serialization*. A source-level replay
may produce numerically identical measurements with different JSON row
order, so new JSON hashes are not asserted to equal historical hashes.

## Reproduction without source redistribution

Run from a clean clone of the public repository:

~~~bash
python -m pip install -r code/requirements.txt
bash scripts/download_prc_sources.sh

python tools/replay_prc_v116.py \
  --graphics data/prc/graphics.txt \
  --archive data/prc/archive-v1.16 \
  --out output/prc-v116-replay

python tools/verify_prc_archive.py output/prc-v116-replay \
  --out output/prc-v116-verified

python -m unittest discover -s code -p 'test_prc_archive*.py' -v
~~~

The replay reads the locally downloaded source, verifies the hash before
writing outputs and fails immediately on numeric differences from the
committed fixed-cohort results. It does not need a private Drive archive
to reproduce the 120 + 53 measurements.

### Why the historical sector rule is kept

The present [prc_construct.py](../code/prc_construct.py) has evolved:
its newer sector equalisation evaluates *full* 3×3 sectors. The original
v1.16 experiment evaluated ink on *eroded* sector masks. Those methods
are **not interchangeable**. The replay implements the archived mask
convention explicitly rather than silently measuring the old published
numbers with the new estimator.

The new replay uses the current module's geometry primitives and checks
the resulting numbers against historical tables; it is not a source snapshot
of all original analysis scripts. If a later edit to the geometry core
changes values, CI should fail rather than rewrite historical data.

## CSV repair: numeric agreement vs byte equality

The first publication accidentally stored the two CSVs through an
intermediate spreadsheet export, introducing a non-CSV two-line preamble,
a spurious index column, and decimal reformatting. Both files now begin
with conventional headers, and [test_prc_archive_csv.py](../code/test_prc_archive_csv.py)
verifies their schema and statistics on every CI run.

The commit repairs the format **without claiming** that the reformatted
floats are byte-identical to the original verifier's output. Numerical
agreement is measured to at least 1e-12. To recover exact verifier
serialization, rerun the original JSON input from the historical archive
with [verify_prc_archive.py](../tools/verify_prc_archive.py), or use
the source replay's derived JSON and keep its newly generated input hashes.

## What remains explicitly unverified

- Human reader recognition of the resulting glyphs (post-publication study).
- Reproduction of original 120/53 **candidate selection**, as opposed to
  independent score computation on the frozen cohorts.
- Identical behavior on a different font face or operating environment.
- Whether source-derived glyph assets may be redistributed as independent
  MIT data (no such redistribution is performed here).

The source replay job is defined in
[.github/workflows/prc-archive-reproduction.yml](../.github/workflows/prc-archive-reproduction.yml).
Its run status, not merely the presence of this document, determines whether
source-level numeric reproduction was actually verified by CI.
