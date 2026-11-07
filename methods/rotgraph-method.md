# Reproducing the 180° rotation graph

This is the public, self-contained protocol for the KanjiVG-based geometric search. It describes the published implementation and data, rather than its development history. **Geometric similarity is a candidate-ranking proxy; it does not prove human readability.**

## Inputs and outputs

- Inventory: 2,136 Jōyō and 634 Jinmeiyō characters; 2,770 unique glyphs in [`data/lists.json`](../data/lists.json).
- Canonical stroke centre-lines: KanjiVG, pinned to commit `70a0b7ae0c18ceb5cb358274b029cce0234a43bc`. See [pin and SHA-256](../data/KANJIVG_PIN.txt).
- Full unordered search space, including self-pairs: `2770 × 2771 / 2 = 3,837,835`.
- Published refined sample: [`data/rotation_pairs.csv`](../data/rotation_pairs.csv), 5,180 rows = 2,410 distinct + 2,770 self-pairs.
- Published grid-ranked sample: [`data/rotation_pairs_top5000.csv`](../data/rotation_pairs_top5000.csv). **Grid and exact distance columns must not be treated as the same metric.**

The complete 3,837,835-row grid archive is *not distributed in this repository*. The optional export script produces `output/catalog/rotation_pairs_full_grid.csv.gz` from recomputed grid results. It uses an explicitly labelled new CSV schema and does not claim byte identity with any earlier archive.

## Geometry and metrics

KanjiVG provides one SVG path per stroke in a nominal `109 × 109` viewBox. The parser in [`code/kvg.py`](../code/kvg.py) samples Bézier curves into polylines; [`code/build.py`](../code/build.py) resamples them at approximately 0.45 KanjiVG units, constructs occupancy grids, and computes a two-pass 3–4 chamfer distance transform.

For a point `p=(x,y)`, a half-turn in this coordinate system is `R(p)=(109-x,109-y)`. For sampled glyph point clouds `A` and `B`, compare `A` with `R(B)`:

```text
Chamfer(A,B)   = 1/2 (mean_a min_b ||a - R(b)|| + mean_b min_a ||a - R(b)||) / 109
Hausdorff(A,B) = max(max_a min_b ||a - R(b)||, max_b min_a ||a - R(b)||) / 109
```

The grid stage approximates neighbour distances using distance transforms; [`code/refine.py`](../code/refine.py) refines selected pairs using Euclidean point-cloud distances and spatial hashing. Gaussian similarity and dilated IoU are additional, separately defined metrics. Dilated IoU uses radii 2, 3 and 4 grid units. The grid-based Hausdorff distance and refined Hausdorff distance have distinct numerical error characteristics and rankings; see [metrics comparison](metrics-comparison.md).

## Reproduce from a clean clone

Requires Python 3.12+, NumPy and Pillow, `curl`, `tar`, and `sha256sum` (the download helper targets Linux/macOS-like shells with `sha256sum`). Run the following commands from the repository root:

```bash
python -m pip install -r code/requirements.txt
bash scripts/download_kanjivg.sh
python code/build.py
python code/compute2.py
python code/compute3.py
python code/refine.py 2500
python code/catalog.py
python code/export_full_grid.py  # optional complete grid CSV (~3.84M pairs)
python -m unittest discover -s code -p 'test_*.py' -v
```

The download helper verifies `kvg-index.json` against the pinned SHA-256. By default, source glyphs are stored under `data/kanjivg/kanji/`, intermediate arrays under `output/cache/`, and catalogues under `output/catalog/`. These outputs are ignored by Git. All paths can be overridden using the `ROTG_*` environment variables defined in [`code/paths.py`](../code/paths.py). Full recomputation can be resource-intensive and requires substantial free disk space and memory.

**Candidate selection:** `refine.py 2500` takes the 2,500 best grid-ranked rows and includes all 2,770 self-pairs, deduplicating overlaps. Ninety self-pairs are already within the 2,500, giving 5,180 refined rows.

## Checks and limitations

- Confirm 2,770 input glyphs and 3,837,835 unordered pairs in the grid output.
- Confirm 5,180 refined rows and 2,770 self-pairs; `由 ↔ 甲` has refined Hausdorff H ≈ 0.0751.
- Raw skeleton IoU is extremely sensitive to one-cell offsets; compare dilated IoU rather than assuming unshifted overlap is perceptual similarity.
- A framed glyph may be over-ranked because its enclosure contributes many sampled points.
- Distance-transform approximation, fixed rotation centre, stroke classification and font variation are unresolved sources of bias.
- No controlled native-reader validation or calibrated perceptual tolerance ε has been established.

For published results and disagreements, see [findings](../findings/results-summary.md), [conflicts](../findings/conflicts-and-corrections.md) and [limitations](../findings/limitations.md). For the distinction between a mathematical feasibility criterion and recognizer calibration, see [existence criterion](../theory/existence-criterion.md).
