# Mainland Chinese rotation explorer (experimental)

This folder is the public static site at [`/prc/`](index.html). It is an **executable research demonstration** of PRC-source character screening, not a finished generator of validated ambigrams.

## What visitors can do

- Enter one character from the **6,763-codepoint GB2312 repertoire**.
- Browse its best candidates according to the **37×37 coarse half-turn IoU**, normalized against all other characters in the same repertoire.
- Display an experimental half-turn overlay of two source glyphs, rotate the overlay 180°, and compare it with both unrotated glyph references.
- Switch among English, 简体中文 and 日本語.

**The overlay is intentionally simple.** It displays A upright and B rotated 180°, with adjustable transparency. It does not modify strokes or optimize a single ambigram design. A geometric candidate is **not necessarily legible** as either character. There has been no human-reader validation; no perceptual success threshold is claimed. This limitation does **not** block publishing research previews.

## Source and licensing

- Dataset: [Make Me a Hanzi](https://github.com/skishore/makemeahanzi), `graphics.txt`; source commit `bddc96d41bef78427ed0e034e9f7e31d71fd1b92`, content SHA-256 `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
- Source uses the **Arphic Public License**, included unaltered at [`licenses/ARPHICPL.TXT`](../licenses/ARPHICPL.TXT). Source SVGs are loaded directly from the upstream repository at its pinned revision; this project does not copy the vector glyph outlines or source medians into the public site.
- `catalog.json` contains only character IDs and **derived numerical screening measurements**. It carries the source revision, licence and method. Source-derived material may be subject to upstream obligations; the MIT licence for original application code does not relicense source glyphs. See [the audit](../LICENSE-AUDIT.md).
- Make Me a Hanzi includes **both simplified and traditional** forms and uses PRC stroke order. GB2312 is a codepoint **repertoire**, not an independent per-glyph certification of simplified character forms. The catalogue flags `source_forms_certified=false`. No JP KanjiVG results are included in its ranking.
- This page requests SVG images from `raw.githubusercontent.com` when a visitor selects a character. It does not collect or send user answers. An internet connection is needed for remote reference glyphs.

## Reproducible build

The catalogue is generated **from actual Stage 14 results**, never by assigning synthetic scores. In a local clone, install the dependencies and run:

```bash
python -m pip install -r code/requirements.txt
bash scripts/download_prc_sources.sh
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt
python code/stage13_prc_presets.py --graphics data/prc/graphics.txt
python code/stage14_prc_search.py --cache data/prc/cache \
  --inventories data/prc/inventories --out data/prc/search
python prc/build_catalog.py --candidates data/prc/search/candidates_grid37.csv \
  --manifest data/prc/inventories/manifest.json --out prc/catalog.json
python -m unittest discover -s code -p 'test_*.py' -v
```

The build is executed and checked by [GitHub Actions](../.github/workflows/prc-site-build.yml). The action only publishes a catalogue from a pinned source after all source, inventory, and ranking guards pass. The source data and intermediate caches remain untracked.

## Dataset sizes (pinned build)

| Statistic | Value |
|---|---:|
| Source records in MMah `graphics.txt` | 9,574 |
| Source coverage of GB2312 | 6,763 / 6,763 |
| Candidate pairs in Stage 14 shortlist | 106,347 |
| Public explorer view | Up to 8 top partners per glyph |
| Pair ranking | `min(z_A, z_B)` of coarse 37×37 IoU |
| Human legibility tested | No |

The 106,347 pairs result was independently produced in [GitHub Actions](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42381308937). A small subset is exposed for convenient browsing, but the full stage is reproducible from the source.

## Related Chinese-method research outputs

This PRC Explorer remains a **coarse ranking/overlay tool**, but it is only one part of the **equally important Chinese research track**. All **11 Chinese method pages** and **22 real source-pinned method examples** are available in the [Research Methods index](../methods/) and [Reader Gallery](../evaluation/recognition/). The published experiments include centre and extremity optimisation, deterministic and searched sector width, R-ODD, harmonic thickness, and A/B fusion null outputs. They do not establish readability.

## Next research steps

Detailed 109-grid pair refinement and optimal rotation-centre experiments, source-form/official-TCC checks, and automated output of aesthetically improved constructions are **separate stages**. Human-reader studies are planned **after** publication and are not a release gate. Numerical ranks must never be described as confirmed recognizability.
