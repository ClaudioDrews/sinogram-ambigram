# Contributing to Sinogram Ambigrams

This repository holds research algorithms, numerical datasets and interactive
demonstrations for **180° rotational ambigram candidates** in Chinese hanzi and
Japanese kanji.

Everything in this repository is written in **English**. Chinese and Japanese
mirrors live under `docs/zh/` and `docs/ja/`.

## Scope and honesty rules

These are not style preferences. They are the conditions under which the
project's conclusions remain usable.

1. **A geometric match is a candidate, not an ambigram.** Nothing in the
   repository has been validated by a controlled native-reader study. Use the
   word *candidate* in prose, issues, pull requests and release notes. See
   `findings/limitations.md`.
2. **Do not invent evidence.** No statistic, citation, semantic pair, character
   list or cultural claim enters the repository without a citable source. If a
   source cannot be verified, say so explicitly or leave it out.
3. **Keep the two distance scales apart.** `data/rotation_pairs.csv` and
   `data/c2_class.csv` hold *exact point-cloud* distances;
   `data/rotation_pairs_top5000.csv` holds *grid-screening* approximations.
   The numbers are not interchangeable and the thresholds are not the same.
   `data/README.md` is the reference.
4. **Never mix data from sources with different licences in one artifact**
   without a per-item provenance field. See `LICENSE-AUDIT.md`.
5. **Attribution is not endorsement.** The work of Issei Nomura inspired this
   project. The artist did not author, review or endorse it, and no artwork of
   theirs is redistributed here.

## Running the project

Requirements: Python 3.11+ (the pinned versions in `code/requirements.txt`
target 3.12+), NumPy, Pillow, and `curl`/`tar`/`sha256sum` for the data
helper.

```bash
python -m pip install -r code/requirements.txt
bash scripts/download_kanjivg.sh   # pinned KanjiVG snapshot + checksum check
python -m unittest discover -s code -p 'test_*.py' -v
```

The download helper verifies `kvg-index.json` against the pinned SHA-256 and
stores the snapshot under `data/kanjivg/kanji/`, which is git-ignored.

### Pipeline stages

| Stage | Script | Produces |
|---|---|---|
| 1 | `code/stage1_skeleton.py` | stroke skeletons, occupancy grids, chamfer distance transforms |
| 2 | `code/stage2_distances.py` | all-pairs grid distances and skeleton IoU |
| 3 | `code/stage3_iou.py` | dilated IoU and combined pair metrics |
| 4 | `code/stage4_refine.py` | exact Euclidean refinement of shortlisted pairs |
| 5 | `code/stage5_catalog.py` | published catalogue CSVs and graph statistics |
| 6 | `code/stage6_export_full_grid.py` | optional complete grid-screened CSV archive |

```bash
python code/stage1_skeleton.py
python code/stage2_distances.py
python code/stage3_iou.py
python code/stage4_refine.py --top-k 2500
python code/stage5_catalog.py
python code/export_full_grid.py  # deprecated alias, still works
```

### Configuration

Paths resolve **relative to the repository** by default, so a clean clone runs
with no setup. Every stage also accepts explicit flags:

```bash
python code/stage1_skeleton.py --data ./mydata --cache ./mycache --out ./myout
```

The `ROTG_*` environment variables (`ROTG_ROOT`, `ROTG_DATA`, `ROTG_KANJI_DIR`,
`ROTG_LISTS`, `ROTG_CACHE`, `ROTG_OUT`) remain available as **optional
overrides**, for example to keep several datasets side by side. Explicit flags
take precedence over environment variables, which take precedence over the
repository defaults.

The old stage filenames (`build.py`, `compute2.py`, `compute3.py`,
`refine.py`, `catalog.py`, `export_full_grid.py`) remain as deprecated aliases
for one release cycle and emit a `DeprecationWarning`. They will be removed in
release v0.3.0.

## Determinism

The pipeline contains no random number generator. Sampling is by constant arc
length, candidate selection is by sorting, and the export writes gzip with a
fixed timestamp, so repeated runs are byte-for-byte identical.

Two regression layers enforce this:

- `code/test_determinism.py::TestSyntheticDeterminism` runs stage 1 twice on a
  fixed synthetic corpus and compares the artifacts against each other *and*
  against frozen golden checksums. It needs no external data.
- `code/test_determinism.py::TestPublishedArtifactChecksums` runs stage 1
  against the pinned KanjiVG snapshot and verifies the published checksums
  recorded in `methods/rotgraph-method.md`. It is skipped when the snapshot is
  absent, so CI stays fast.

**If you change stage 1, the synthetic golden checksums will fail.** That is
the point. Decide deliberately whether the change is intended, and if it is,
update `SYNTHETIC_MD5` in a separate commit with an explicit justification.
Never adjust a checksum to make a failing test pass without saying so.

The published artifacts are also reproducible end to end:

```bash
bash scripts/download_kanjivg.sh
python code/stage1_skeleton.py
md5sum output/cache/points.npy output/cache/meta.json output/cache/dt.npy
```

## Code conventions

- Python 3.11+, standard library plus NumPy and Pillow only.
- No `scipy`: the distance transform and the spatial hash are implemented
  directly so the pipeline has the smallest possible dependency surface.
- Stage scripts read their paths from the `paths` module at call time
  (`paths.CACHE`, not a module-level copy), so configuration changes are
  honoured.
- Public functions carry a docstring stating what the numbers mean and how they
  are normalised.
- Prefer descriptive metric names over ambiguous ones. A column named
  `hausdorff` must state its scale; `hausdorff_grid` does, `hausdorff` does
  not.

## Task reports

Work is organised as one branch and one atomic commit per task:
`task/<ID>-<slug>`, commit message `<ID>: <short title>`. The pull request
updates the task table and attaches a report in this form:

```text
TASK: <ID> — <title>
EXECUTOR: <model/tool + version>
DATE: <yyyy-mm-dd>
CHANGES: <files created or modified, one line each>
VERIFICATION: <commands run + results, including determinism checks where relevant>
DECISIONS: <every discretionary decision and why>
PENDING: <what is left for another task>
DIVERGENCES: <where the repository and the roadmap disagree with reality>
```

A task is only marked complete when every acceptance check passes. When a
check fails twice with different approaches, stop and escalate rather than
looping.

## Before you open a pull request

```bash
python -m unittest discover -s code -p 'test_*.py' -v
python tools/check_links.py
```

Both must be green. The link checker resolves every repository-local Markdown
link in every `.md` file outside dotted directories.

## Reporting a candidate

Issues about specific characters are welcome. Include the character pair, a
screenshot or exported SVG, the construction method used, and what you
observed when rotating the drawing. Describe legibility as an observation, not
as a proof: the project has no calibrated perceptual tolerance yet.

## Licence

Original code and prose are MIT licensed. KanjiVG-derived stroke vectors in
the browser demonstrations are **CC BY-SA 3.0** and must keep their attribution
and share-alike terms. See `LICENSE` and `NOTICE.md`; `LICENSE-AUDIT.md`
records the obligations per source.