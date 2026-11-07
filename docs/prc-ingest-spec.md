# PRC source ingestion — median-skeleton cache (Stage 12)

**Status:** Source-format implementation with offline synthetic tests; a real
pinned-source run, coverage report and independent numerical comparison remain
pending. This is not a PRC-wide ranking or a claim of human legibility.

## Input and pin

The input is `graphics.txt` from [Make Me a Hanzi](https://github.com/skishore/makemeahanzi),
a JSONL file with `character`, `strokes` (SVG paths), and `medians` (one list
of xy coordinates per stroke). The source states that its coordinate system
is 1024 × 1024 with upper-left `(0, 900)` and lower-right `(1024, -124)`:
positive source y points upward. The source mixes simplified and traditional
Chinese characters. Do not interpret every record as a certified Mainland
simplified form. See [the source pin](../data/MMAH_PIN.txt) for SHA-256
and [the licence audit](../LICENSE-AUDIT.md) for reuse boundaries.

The loader verifies the entire file's SHA-256 before emitting output. It
rejects malformed characters, duplicates, unpaired stroke/median counts,
non-finite coordinates and empty median lists. The downloader uses a moving
upstream branch with **content-hash enforcement**, but a source commit is not
yet independently confirmed; this is an explicit open provenance check.

## Coordinate conversion and point cloud

Let (x_m, y_m) be one MMah median point. Convert to the shared 109-unit,
y-down, top-left-origin grid by

    x_109 = 109*x_m/1024
    y_109 = 109*(900-y_m)/1024

For each stroke, resample the polyline at a nominal interval of 0.45 units
using Stage 1's resampler. Rasterize each resampled segment with Stage 1's
rasterizer and generate the shared 3–4 chamfer distance transform. This
preserves the **existing Stage 1 grid scale** instead of introducing an
unrelated distance measure. The 180° rotation on integer raster coordinates
uses (x',y') = (108-x,108-y); shifted-centre searches require the padded
transform specified in Stage 8.

## Outputs

Run from the repository root:

~~~bash
bash scripts/download_prc_sources.sh
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt --out data/prc/cache
~~~

The cache is local and ignored by Git:

| File | Shape / semantics |
| --- | --- |
| `meta.json` | Unicode-sorted records; source checksum; stroke/point counts; region unassigned; optional JP stroke-count comparison |
| `points.npy` | float32 concatenated median skeleton points (P,2) |
| `offsets.npy` | int64 offsets (N+1) indexing each glyph's cloud |
| `dt.npy` | float32 chamfer distance transform (N,109,109) |

Optional `--jp-meta output/cache/meta.json` populates
`jp_n_strokes` and `jp_stroke_count_diff`; matching stroke counts **do not**
establish matching glyph forms. No downloaded glyph data or dictionary
materials enter the repository.

## Geometry and regional gates

The older T1.15–T1.16 PRC construction experiments use **filled outline ink**
rasterized with a fitted em square. This stage uses **median skeletons** and
the MMah canvas mapping. They are different representations: do not equate
their distances or improvements without a controlled comparison.

The source includes simplified and traditional characters. This step does
**not** stamp every record `cn-s`. A verified inventory/preset (T1.3)
must assign the regional variant before ranking. Until then the cache records
`region: unassigned` and is deliberately **not eligible for a regional ranking**.

## Verification and uncompleted gates

~~~bash
python -m unittest discover -s code -p 'test_*.py' -v
python code/prc_inventory.py --graphics data/prc/graphics.txt
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt --out data/prc/cache
~~~

Synthetic tests cover coordinate conversion, shapes and dtypes, byte-identical
outputs on independent rebuilds, source pin rejection, optional Japanese
stroke-count comparisons and malformed-input rejection.

**Still pending:** independently run on the pinned full source, check inventory
and coverage counts, independently repeat the full run, verify the source
revision and reuse licence, and compare regional variant forms before using
the cache for scientific claims. Model judgments are not human validation.
