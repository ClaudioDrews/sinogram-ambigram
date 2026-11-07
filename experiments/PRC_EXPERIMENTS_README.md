# PRC branch experiments — reproducible preview and reader protocol

**Status:** exploratory, unvalidated for human readability. Every candidate and its
metrics remain experimental until the gates in
[PRC_ABLATION_PROTOCOL.md](PRC_ABLATION_PROTOCOL.md) are satisfied.

## Branches and comparison baselines

| Branch | Experimental change | Comparison |
| --- | --- | --- |
| `main` | Historical unmodified code (pinned `a9ddfabbdfe32d781c816ffbd6c93fc194d12e30`) | Original reference |
| `exp/thickness-fix` | Reconstruct strokes from measured median-to-outline half-width | Pinned main |
| `exp/r-odd` | Locally add ink near corresponding rotated ink | Thickness-fixed reference |
| `exp/harmonic` | Optimize a continuous C2-even thickness field | Thickness-fixed reference |
| `exp/ab-fusion` | Align/merge matched strokes from A and half-turned B | Thickness-fixed *unmodified union* |

The three experimental methods use different problems: `r-odd` and
`harmonic` optimize *self-rotation* of a single glyph; `ab-fusion` builds
*distinct-character* candidates. Do not pool these as a single direct ranking.

## Workflow preview output

The `PRC experimental regression` GitHub Actions workflow downloads the
SHA-256 pinned MMah `graphics.txt`, runs all PRC regressions, and publishes
an artifact called `prc-experiment-stimuli`. Its folders are:

- `original-main-self`: a fixed historical main implementation, five glyphs;
- `original-main-pairs`: simple original main A/B union, two pairs;
- `fixed-self` and `fixed-pairs`: corresponding thickness-corrected controls;
- `method-self` (R-ODD/Harmonic) or `method-pairs` (A/B Fusion): method outputs.

Preview characters are `田,中,口,日,目`; preview pairs are `甲:由,韦:芈`.
These are **demonstrations, not a held-out test**. Never use the observed
preview performance to estimate generalization. Freeze a separate pair pool
before full automated-reading evaluation.

Every folder contains `case-00001-upright.png`,
`case-00001-rotated.png` and `manifest.json`.
The manifest deliberately contains expected characters and must be withheld
from the models. The PNGs have no target labels. SHA-256 values are recorded
for source, geometry code and PNG bytes. Retain the workflow run ID and commit
SHA as additional reproducibility metadata. The artifact includes the upstream
Arphic Public License; it does **not** relicense MMah-derived glyphs as MIT.

## Local reproduction

```bash
bash scripts/download_prc_sources.sh
python -m pip install -r code/requirements.txt
python -m unittest discover -s code -p 'test_prc*.py' -v

# All experimental branches support the same baseline export.
python code/exp_render_prc.py --graphics data/prc/graphics.txt \
  --characters '田,中,口,日,目' --mode baseline --out outputs/fixed-self

# Run only on exp/r-odd:
python code/exp_render_prc.py --graphics data/prc/graphics.txt \
  --characters '田,中,口,日,目' --mode r-odd --out outputs/method-self

# Run only on exp/harmonic:
python code/exp_render_prc.py --graphics data/prc/graphics.txt \
  --characters '田,中,口,日,目' --mode harmonic --out outputs/method-self

# Run only on exp/ab-fusion:
python code/exp_render_prc.py --graphics data/prc/graphics.txt \
  --pairs '甲:由,韦:芈' --mode ab-fusion --out outputs/method-pairs
```

## Blind VLM evaluation

For each frozen pair, present upright and rotated PNGs **independently**.
Use an identical prompt across methods, for example:

> Identify the single Chinese character depicted. Answer with exactly one
> Unicode character or UNKNOWN if you cannot identify it. Do not guess a
> character from any file name or associated metadata.

Record model/version, raw response, sampling settings, prompt, run timestamp,
image hash, orientation, exact-match result, model disagreement and controls.
The **primary outcome** is a correct answer in *both* orientations for the
same ambigram. Report model-specific results and pair-level confidence
intervals; do not count two orientations of one pair as independent trials.
A test with VLMs alone cannot establish human readability.

## Technical limitations

- Source codepoint coverage does not certify official regional glyph forms.
- `r-odd` is a geometric rotated-ink thickness heuristic, not a formal
  odd-component cancellation operator.
- The harmonic ablation enforces C2 symmetry of its scalar field, but not
  human recognition of the result.
- A/B fusion uses stroke matching and two-reference binary F1 proxies;
  it may still make the result illegible.
- Binary rasterization can be sensitive to exact pixel-border ties.
- `prc_construct.retention` outside `sector_score` retains an existing
  area-ratio definition; distinguish this from actual intersection retention.

No PR should merge until the project regression suite and the preregistered
dual-reading gates have been satisfied.
