---
title: "Reproducible method: the 180° rotation graph of sinograms"
id: rotgraph-method
type: methodology
status: reviewed
evidence: [MEASURED, REPORTED, DERIVED]
run: minimax
tags: [sinogram, ambigram, rotation-180, rotation-graph, kanjivg, chamfer, hausdorff, deterministic, minimax]
created: 2026-11-01
updated: 2026-11-05
language: en
license: MIT
translations: {zh: machine-assisted, ja: machine-assisted}
translation_of: ../../experiments/exp-08-minimax-rotation-graph/original/METODO.pt.md
translation_method: machine-assisted, faithful; numbers and criteria unchanged
translation_status: machine-assisted
related: [exp-08, rotgraph-report, metrics-comparison, data-sources-and-tools]
missing_artifacts: [../../experiments/exp-08-minimax-rotation-graph/rotgraph/data/rotation_pairs.csv]
---

# Reproducible method: the 180° rotation graph of sinograms

> Complete protocol for reproducing the results of *"Execution of the proposal: the 180° rotation graph of sinograms"*. Written so that someone else (or another agent) can rebuild the pipeline from scratch and obtain **the same numbers**.
>
> Method version: 1.0 · data collected 2026-11-01 · code in `rotgraph/`

**Editor's note (added by this repository, not part of the original).** This is a faithful English translation of the Portuguese method document; numbers, criteria and wording are preserved, including where the document contradicts itself. Eight internal divergences are on record and are *not* corrected here: **X1** number of pairs (3,835,785 here vs 3,837,835 in the report — **resolved by measurement on 2026-11-05: the file has 3,837,835 data rows and this document's 3,835,785 is erroneous; the body is left unchanged as a faithful translation**), **X2** graph size at H ≤ 0.10 (655/537 here vs 710/558 in the report's text), **X3** V2's "H > 0.45" for the negatives (the CSV has 0.166–0.344), **X4** the claim that 十 is in the top of the C2 class (it is 370th), **X5** stroke count as predictor (no analysis), **X6** the mixed `rank` column, **X7** hub bias, **X8** the two H scales. An independent review confirms X1–X4 and X7 and adds seven findings (CR1–CR7). See EXP-08 (source reference in repo2: `../experiments/exp-08-minimax-rotation-graph.md`) and the [conflict log](../findings/conflicts-and-corrections.md). The review also notes that the list of limits in §10 omits the fixed rotation centre (CR3).

---

## 0. Principle of the method

The target is the **existence criterion** of §1 of the original proposal: for a pair of sinograms (a, b), a rotation ambigram "without modification" exists when the shape of *a* and the shape of *b* rotated 180° lie within a perceptual tolerance ε.

The method **does not try to construct** ambigrams (that requires deformation). It **measures** the geometric distance between pairs and publishes the complete ranking. Consequently, what it delivers is the *horizontal axis* of the programme (the nodes and edges of the graph); the *vertical axis* (ε, warp, warping) `[sic — the Portuguese original repeats the term; read as "ε, warping"]` is left to recommendations 2, 4 and 5.

Two invariants guide every decision:

- **I1 — No rasterisation.** The KanjiVG `<path>` is the *centreline* of the brush. Using the path as a skeleton eliminates raster skeletonisation (and the loss of junctions noted in §3 of the original proposal).
- **I2 — The rotation graph is undirected.** Because R is an isometry and an involution, `d(p, R(q)) = d(R(p), q)`, hence `D(a,b) = D(b,a)`. This is a *consequence*, not a requirement: the code computes `D(a,b)` and `D(b,a)` along the same path and the result confirms the equality. It means that (甲,由) and (由,甲) are **one** pair, and that fixed points exist (self-pairs, the "C2 class").

---

## 1. Environment

| Item | Value | Note |
|---|---|---|
| OS | Linux x86-64 | any POSIX will do |
| Python | 3.11.2 | tested on 3.11; the pipeline has no version dependency |
| CPU | 2 cores | parallelism is `Pool(2)`; more cores only make it faster |
| RAM | ~1.5 GB peak | the on-disk cache takes 410 MB |
| Dependencies | `numpy` (required), `pillow` (PNG/render only) | **no scipy** |
| Network | only while collecting data | stages 2–7 are offline |

> **Environment note**: in the execution sandbox PyPI was unreachable (`scipy` and `scikit-image` could not be installed). The distance transform was implemented by hand (chamfer 3-4, `build.py:chamfer_dt`) and the nearest-neighbour search uses a *spatial hash* in pure numpy (`refine.py:_min_dist_to`). **The pipeline does not depend on scipy**, which is an advantage for reproducibility: the minimum dependency count is two.

### 1.1 Path configuration

`rotgraph/paths.py` resolves every path through environment variables, so the code runs on another machine **without editing**:

| Variable | Default | Content |
|---|---|---|
| `ROTG_ROOT` | `/workspace/rotgraph` | code root |
| `ROTG_DATA` | `/workspace/data` | raw data |
| `ROTG_KANJI_DIR` | `$ROTG_DATA/kanjivg-master/kanji` | KanjiVG SVGs |
| `ROTG_LISTS` | `$ROTG_DATA/lists.json` | character lists |
| `ROTG_CACHE` | `$ROTG_ROOT/cache` | intermediate cache |
| `ROTG_OUT` | `/workspace/output` | final artefacts |

---

## 2. Input data

### 2.1 KanjiVG (vector glyphs)

```bash
mkdir -p /workspace/data && cd /workspace/data
curl -sSL -o kanjivg_dl \
  "https://github.com/KanjiVG/kanjivg/archive/refs/heads/master.tar.gz"
tar xzf kanjivg_dl
# canonical glyphs in: kanjivg-master/kanji/*.svg
```

Dataset verification (what a reproduction should find):

- 11,941 `.svg` files in total;
- **6,984 canonical glyphs** = files whose name is exactly five hexadecimal digits
  (`^[0-9a-f]{5}\.svg$`, i.e. the Unicode code point in hexadecimal);
- the remainder (~4,957) are font variants (`04e14-Kaisho.svg`, `04e3b-VtLst.svg`, …) and
  **are not used**;
- each SVG has `viewBox="0 0 109 109"` — the canonical 109-unit box;
- each `<path>` inside `<g id="kvg:StrokePaths_...">` is **one stroke**, with
  `stroke-linecap="round"` and `stroke-width` set by the group style.

For bit-exact reproducibility, prefer a pinned *release*
(`kanjivg-YYYYMMDD-main.zip` from <https://kanjivg.tagaini.net/>) over `master`.

### 2.2 Official character lists

Extracted from Japanese Wikipedia through the API (wikitext tables):

```bash
curl -sSL --get "https://ja.wikipedia.org/w/api.php" \
  --data-urlencode "action=parse" --data-urlencode "page=常用漢字一覧" \
  --data-urlencode "prop=wikitext" --data-urlencode "format=json" -o joyo_page.json

curl -sSL --get "https://ja.wikipedia.org/w/api.php" \
  --data-urlencode "action=parse" --data-urlencode "page=人名用漢字" \
  --data-urlencode "prop=wikitext" --data-urlencode "format=json" -o jinmeiyo_page.json
```

Extraction rules (they determine the inventory — see trap **A2**):

- **Jōyō**: for each table row, the **last** occurrence of `[[wikt:X|Y]]` inside the cell of
  the 通用字体 column (index 1 of the `||` split). Expected result: **2,136 字種**.
- **人名用漢字**: the block `; [[常用漢字]]以外の文字とその[[異体字]]` of the page, treated as a
  space-separated list; variants joined by `‐` (U+2010) are **one** 字種 in two 字体.
  Expected result: **634 字種** (652 字体).
- Reconciliation with the original proposal: the "863 Jinmeiyō" quoted there counts
  **字体** (forms), not 字種.

Final inventory = union = **2,770 glyphs**. Verification: **all** 2,770 have a KanjiVG SVG (none excluded).

### 2.3 Unihan (cross-check only)

```bash
curl -sSL -o Unihan.zip "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"
```

Used only to cross `kIRG_JSource` (JIS X 0208 level 1/2) with the sets; it does not enter the numerical pipeline.

---

## 3. Pipeline

Each stage reads the output of the previous one. Times measured on 2 cores.

| # | Script | Input | Output | Time |
|---|---|---|---|---|
| 0 | `lists.py` (inline) | wikitexts | `data/lists.json` | < 5 s |
| 1 | `kvg.py` + `build.py` | KanjiVG | `cache/points.npy`, `offsets.npy`, `dt.npy`, `meta.json` | ~2.5 min |
| 2 | `compute2.py` | `cache/dt.npy` | `cache/pairs2.npz.npy` (3,835,785 pairs) `[DIVERGENCE: X1 — the stored file and C(2770,2)+2770 give 3,837,835; 3,835,785 is an erroneous report]` | ~5 min |
| 3 | `compute3.py` | `cache/pairs2.npz.npy` | `cache/pairs3.npy` (+ dilated IoU) | ~1 min |
| 4 | `refine.py 2500` | `cache/pairs3.npy` | `cache/refined.npy` (5,180 exact pairs) | ~30 min |
| 5 | `catalog.py` | `cache/refined.npy` + `pairs3.npy` | `catalog/*.csv`, `catalog/stats.json` | ~2 min |
| 6 | `make_html.py`, `make_sheets.py`, `make_report.py` | `catalog/stats.json` | page, PNGs, report | ~1 min |

### Stage 1 — skeletons and distance transform (`build.py`)

For each glyph:

1. **Parser** (`kvg.py:parse_path`): implements the SVG subset used by KanjiVG —
   `M m L l H h V v C c S s Q q T t A a Z z` — with Bézier flattening into 16 segments
   per curve and arcs by endpoint→centre parameterisation. (Canonical KanjiVG uses only
   `M, C, c, m, s, S`, but the complete parser avoids surprises on variants.)
2. **Resampling** (`resample_polyline`): each polyline is resampled at a constant step
   `SPACING = 0.45` units, by interpolation over accumulated length → a dense, uniform
   point cloud (≈ 958 points per glyph on average).
3. **Occupancy grid** 109×109 (1 unit = 1/109 of the box): marks the cells crossed by each
   segment — **walking vertex by vertex** (trap **A1**).
4. **Distance transform** (`chamfer_dt`): chamfer 3-4 in two passes
   (forward: `d[y] = min(d[y], d[y-1]+3, d[y-1]±1+4)`; backward: mirrored), result divided
   by 3 → distance in pixel units. It is a Euclidean approximation (max error ≈ 8% along
   the diagonal). *Editor's note (not in the original): computed directly, the 45° direction of the 3-4 kernel is off by 5.7%, and Borgefors (1986) gives ≤ 8% as the worst-case bound for this kernel — the original sentence conflates the bound with the diagonal.*

Outputs: `points.npy` (float32, concatenated), `offsets.npy` (int64, per-glyph offsets),
`dt.npy` (float32 memmap 2770×109×109 = 131 MB), `meta.json` (char, code point, file,
stroke count, stroke types, set).

### Stage 2 — all against all (`compute2.py`)

For every undirected pair (a ≤ b), with R(x) = (109−x₁, 109−x₂):

```
d1 = DT_b[ cells of the ROTATED points of a ]      # = dist(p_a, R(b))
d2 = DT_a[ cells of the ROTATED points of b ]
chamfer = ½(mean d1 + mean d2)
rms     = √(½(mean d1² + mean d2²))
haus    = max(max d1, max d2)
```

Why query the *rotated* points in the other glyph's DT: `dist(p, R(b)) = dist(R(p), b)`,
and the DT is indexed by cell — so the same table serves both directions.

- Blocks of `n // 24` glyphs, `Pool(2)`, `imap_unordered`; each block recomputes the
  positions (a ≤ b) so that pairs are not duplicated.
- Raw `IoU` (no dilation) is computed here but **not used** (see trap **A3**).

### Stage 3 — dilated IoU (`compute3.py`)

Tolerant overlap: `IoU_r(a,b) = |A_r ∩ R(B_r)| / |A_r ∪ R(B_r)|` with `A_r = {cells with
DT ≤ r}`, for r ∈ {2, 3, 4}. Computed by BLAS matrix multiplication (`A @ A_rot.T`,
2770×2770 in ~3 s) and indexed by (a,b) in the matrix.

### Stage 4 — exact refinement (`refine.py`)

No grid: true Euclidean distances between the dense point clouds.

- **Guide**: the DT gives `d0` (an approximation of the nearest neighbour). The exact
  minimum is searched in a ring of the *spatial hash* (cells of `CELL = 2` units) with
  radius `int(d0·1.25)+3`; if the ring comes back empty (the DT underestimates), there is a
  scan *fallback*.
- **Exact metrics**: mean chamfer, RMS, **symmetric Hausdorff** and Gaussian similarity
  `S = ½(mean exp(−d²/2σ²) + …)`, with `σ = 2` units.
- **Candidates**: `K = 2500` best pairs by grid Hausdorff **+ the 2,770 self-pairs** (the
  entire C2 class). 5,180 refined pairs in total. *Editor's arithmetic note: 2,500 + 2,770 = 5,270, not 5,180. The delivered data README states 5,180 = 2,410 distinct + 2,770 self-pairs, so 90 self-pairs must already have been inside the top-2,500 (derived: 2,500 − 2,410; X6). The figure 5,180 is correct — only this sentence's decomposition is loose.*
- Blocks of 200 pairs, `Pool(2)`, LRU cache of 120 glyphs per process (low memory).

### Stage 5 — catalogue (`catalog.py`)

- `catalog/rotation_pairs.csv` — the 5,180 refined pairs, with exact metrics.
- `catalog/c2_class.csv` — the 2,770 self-pairs (C2 class), sorted.
- `catalog/stats.json` — inventory, histogram, connected components per threshold,
  validation statistics, and the 400 best distinct pairs (the page payload).
- `catalog/rotation_pairs_full.csv.gz` — **the 3,835,785 pairs** `[DIVERGENCE: X1 — the stored file has 3,837,835 data rows; 3,835,785 is erroneous]` with the grid metric
  (82 MB, gzip). Generated by an ad-hoc script (§8).

---

## 4. Formal definitions (what the numbers mean)

With `EM = 109` (side of the box) and `R(x) = (EM − x₁, EM − x₂)`:

```
chamfer(a,b) = ½ [ mean_{p∈a} min_{q∈R(b)} |p−q| + mean_{q∈R(b)} min_{p∈a} |p−q| ]   ÷ EM
haus(a,b)    = max ( max_{p∈a} min_{q∈R(b)} |p−q| , max_{q∈R(b)} min_{p∈a} |p−q| )   ÷ EM
sim(a,b)     = ½ [ mean_{p∈a} e^{−d²/2σ²} + mean_{q∈R(b)} e^{−d²/2σ²} ],  σ = 2 units
```

All published values are **normalised by the box** (divisor 109): 0.01 = 1.09 units = 1% of
the glyph width.

**Interpretation**:

- `haus` answers "**is** this glyph the other one, rotated?" (worst point). It is the right
  criterion for "without modification".
- `chamfer` answers "do the two read alike?" (mean, with the perceptual behaviour of
  tolerant reading). It weights the interior of the glyph better.
- `sim` is a Gaussian kernel (σ = 2 units ≈ stroke width): it tolerates local displacement
  while penalising shape error.

The three disagree in some cases (e.g. pairs with a frame), and the disagreement is
informative — it is reported in the report.

---

## 5. Design decisions and their consequences

| Decision | Discarded alternative | Consequence |
|---|---|---|
| Skeleton = the KanjiVG path | raster + skeletonize | no loss of junctions; **but** the interior of framed glyphs is over-weighted (the frame dominates the skeleton) |
| 109×109 grid for screening | exact DT for everything | 100× faster; error ±0.5 unit, measured (r = 0.944) |
| Dilated IoU (r = 2..4) | raw IoU | raw IoU collapses with one cell of misalignment (十 vs 十 would give 0.006) |
| Skeleton metric, not ink metric | distance between areas | does not measure "wrong stroke type in the right place" |
| 180° rotation only | 90°, mirroring | outside the scope of the proposal (open question 6) |
| Glyph level, not word level | word graph | the graph gives the nodes; words need order reversal plus per-glyph rotation |

---

## 6. Traps (what breaks the result)

**A1 — Chord rasterisation.** The first version of `rasterize_segments` drew the segment
between the *first* and the *last* point of the polyline, ignoring intermediate vertices.
On curved strokes (the ㄱ of 田, for example) that turns the skeleton into a diagonal.
Symptom: the C2 class came out wrong (十 with IoU 0.006) and the grid's ASCII art showed
"staircases". **Fix**: walk every pair of consecutive vertices.
*How to detect*: a glyph whose occupancy grid does not look like the drawing.

**A2 — Variant mistaken for the standard form.** The Jōyō table has `[[wikt:𠮟|𠮟]]-[[wikt:叱|叱]]`
in the 通用字体 cell (variant + standard form). Taking the *first* link includes 𠮟 and
excludes 叱 → wrong inventory (2,135 instead of 2,136). **Fix**: take the last link of the
cell. *How to detect*: the inventory has 2,135 instead of 2,136 Jōyō, and 叱 does not appear.

**A3 — Skeleton IoU without dilation.** A skeleton is 1 cell wide; a 1-cell misalignment
zeroes the intersection. *How to detect*: IoU(十,十) ≈ 0 when it should be 1.

**A4 — Distance transform underestimating the true neighbour.** The DT is computed on
*rasterised* cells, which may be up to ~0.5 unit from the nearest sampled point; the ring
search can then come back empty. **Fix**: scan fallback (implemented). *How to detect*:
`inf` in the Hausdorff distance of a plausible pair.

**A5 — `np.save` with an `.npz` suffix.** `np.save("x.npz", arr)` writes `x.npz.npy`. The
reader has to use the real name. *How to detect*: `FileNotFoundError` in the next step.

**A6 — Pool with large copies.** Copying the DT memmap (131 MB) into RAM in each worker,
plus a Python hash for 2,770 glyphs, exhausted RAM and hung the `Pool` (the parent waited
for dead workers). **Fix**: keep the memmap, build the hash on demand with an LRU cache.
*How to detect*: parent process at 0% CPU with no live worker.

---

## 7. Verification of the implementation

Checks a reproducer should run (all pass in the delivered version):

| # | Check | Expected result |
|---|---|---|
| V1 | `目`, `日`, `田`, `口` at the top of the C2 class | H = 0.032 / 0.044 / 0.051 / 0.061 |
| V2 | `又, 乃, 刀, 万, 之, 九, 丁` at the bottom of the C2 class (they do not survive) | H > 0.45 |
| V3 | canonical pair `由 ↔ 甲` at the top of the distinct pairs | H = 0.0751, chamfer = 0.0232 |
| V4 | `D(a,b) = D(b,a)` | exact equality (bit for bit) |
| V5 | grid vs exact over the 5,180 pairs | r = 0.944 · median absolute error 0.0065 · bias +0.0095 |
| V6 | rendering: `十` rotated 180° = `十`; `由` rotated = `甲` | visual inspection (`preview/c2_sheet.png`) |
| V7 | the delivered code reproduces the published numbers | recompute 10 pairs from `refined.npy` → delta 0.00e+00 |

V7 is the most important: it guarantees that the published code is the code that generated
the catalogue.

*Editor's note on §7 (not in the original): the sentence that introduces the table says every check passes; **V2 does not**. In `c2_class.csv` the seven glyphs sit at H 0.166–0.344 and the file maximum is 0.434 (入). The error is recorded as X3 in the [conflict register](../findings/conflicts-and-corrections.md).*

**Revalidation after the path refactor** (2026-11-01, `paths.py` introduced): the pipeline
was re-run from stage 1 to 6 and **every artefact came out byte-for-byte identical** —

```
md5  points.npy    b9a95dd6d3fc27c67dcd5623783cc8ce   (before = after)
md5  dt.npy        687a275a7537fb7215a3c0c575639683   (before = after)
md5  meta.json     cbf4a688848d0f886341f86e322a715a   (before = after)
md5  pairs3.npy    1e32dc59c78a774984db84ff623b9ca5   (before = after)
sha256 catalog/rotation_pairs.csv   436f264d3a7c821a776c60c71f25cadefd2483494c9e34e2549ed94b75f84a41
sha256 catalog/c2_class.csv         7a5612e302762f14261d48a50b3e6fd702f676678b261f8dc873a632b6619b61
sha256 [historical output folder]/index.html  017c80318293f1ae17c2437c7bd87960ab02b1bcff2ee3511fbdeae796cbffaf
V7 (10 pairs recomputed)          maximum delta = 0.00e+00
```

This closes the loop: the delivered code, the published data and the numbers in the report
are mutually consistent.

**Determinism**: there is no RNG in any stage (sampling is by constant step over
accumulated length; candidate selection is by sorting). Two runs on the same KanjiVG give
the same result byte for byte.

---

## 8. Commands (from scratch)

```bash
# 0) data
cd /workspace/data
curl -sSL -o kanjivg_dl "https://github.com/KanjiVG/kanjivg/archive/refs/heads/master.tar.gz"
tar xzf kanjivg_dl
# (lists: see §2.2 -> data/lists.json with joyo[2136] and jinmeiyo_types[634])

# 1..4) numerical pipeline
cd /workspace/rotgraph
python3 build.py            # ~2.5 min -> cache/{points,offsets,dt}.npy, meta.json
python3 compute2.py         # ~5 min   -> cache/pairs2.npz.npy
python3 compute3.py         # ~1 min   -> cache/pairs3.npy
python3 refine.py 2500      # ~30 min  -> cache/refined.npy

# 5..6) catalogue and presentation
python3 catalog.py          # catalog/*.csv, catalog/stats.json
python3 - <<'PY'            # full catalogue of the 3.8 M pairs
import numpy as np, json, gzip, csv
meta=json.load(open("cache/meta.json")); chars=[m["char"] for m in meta]
sets=[m["set"] for m in meta]; strokes=[m["n_strokes"] for m in meta]
res=np.load("cache/pairs3.npy")
order=np.argsort(res["haus"], kind="stable")
with gzip.open("catalog/rotation_pairs_full.csv.gz","wt",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["rank","a","b","a_set","b_set","a_strokes","b_strokes",
                "hausdorff","chamfer","rms","iou_dil2","iou_dil3","iou_dil4"])
    for k,i in enumerate(order):
        a,b=int(res["a"][i]),int(res["b"][i])
        w.writerow([k+1,chars[a],chars[b],sets[a],sets[b],strokes[a],strokes[b],
            f"{res['haus'][i]/109:.5f}",f"{res['mean'][i]/109:.5f}",f"{res['rms'][i]/109:.5f}",
            f"{res['iou2'][i]:.4f}",f"{res['iou3'][i]:.4f}",f"{res['iou4'][i]:.4f}"])
PY
python3 make_html.py && python3 make_sheets.py && python3 make_report.py
```

**Expected outputs** (SHA-256 of the delivered version):

```
436f264d3a7c821a776c60c71f25cadefd2483494c9e34e2549ed94b75f84a41  catalog/rotation_pairs.csv
7a5612e302762f14261d48a50b3e6fd702f676678b261f8dc873a632b6619b61  catalog/c2_class.csv
f4b929693148146379bc71c0783c81279149e4834ed15e11c573fbf67aba66e0  catalog/rotation_pairs_full.csv.gz
017c80318293f1ae17c2437c7bd87960ab02b1bcff2ee3511fbdeae796cbffaf  [historical output folder]/index.html
```

---

## 9. Map of the scripts

| File | Role | Dependencies |
|---|---|---|
| `rotgraph/paths.py` | path resolution from environment variables | — |
| `rotgraph/kvg.py` | SVG path parser, resampling, inline SVG for the HTML | `numpy` |
| `rotgraph/build.py` | skeletons, occupancy grid, chamfer DT | `numpy` |
| `rotgraph/compute2.py` | all-pairs: chamfer, RMS, Hausdorff | `numpy` |
| `rotgraph/compute3.py` | dilated IoU (BLAS) | `numpy` |
| `rotgraph/refine.py` | exact metrics with a spatial hash | `numpy` |
| `rotgraph/catalog.py` | catalogue CSV + JSON, connected components | `numpy` |
| `rotgraph/render.py` | PNG of glyphs and contact sheets | `pillow` |
| `rotgraph/make_ambigram.py` | ambigram generator (law 2: thick common / thin exclusive) | `numpy`, `pillow` |
| `rotgraph/make_html.py` | self-contained visual page | `json` |
| `rotgraph/make_sheets.py` | visual verification sheets | `pillow` |
| `rotgraph/make_report.py` | markdown report from `stats.json` | — |

`rotgraph/compute.py` is an earlier version (chamfer only, superseded by `compute2.py`) —
it is not needed to reproduce the results. Like the other twelve scripts it is **not in this
distribution**, so "kept for history" describes the delivered folder, not this checkout.

---

## 10. Limits of the method (what it does **not** measure)

1. **ε is not measured.** The thresholds are geometric. Whether "H ≤ 0.08" means "legible"
   to a Japanese reader is the perceptual experiment of recommendation 4 — and it now has a
   finite, ranked set to work on.
2. **One shape per glyph.** KanjiVG offers one canonical shape; real ε includes typeface,
   handwriting and stroke weight. A natural refinement: repeat with the `-Kaisho`/`-VtLst`
   variants and measure the dispersion.
3. **Glyph, not word.** Rotating a word reverses the order *and* rotates each glyph; the
   current graph gives the nodes, not the sentences.
4. **180° only.** 90°, mirroring and figure–ground are left out (open question 6 of the
   proposal), although the same distance machinery would serve them.
5. **Geometry ≠ percept.** A skeleton metric does not penalise "wrong stroke type in the
   right place" (Nomura's law 5 is exactly that case: stroke fusion/division). The
   correction suggested in the report — weight ink area, or penalise stroke-type divergence
   — changes the ranking of framed pairs.

## Related

- EXP-08 — MiniMax rotation graph (source reference in repo2: `../experiments/exp-08-minimax-rotation-graph.md`)
- Rotation-graph report (translation) (source reference in repo2: `../findings/rotgraph-report.md`)
- [Metrics comparison](../methods/metrics-comparison.md)
- Data sources and tools (source reference in repo2: `data-sources-and-tools.md`)
