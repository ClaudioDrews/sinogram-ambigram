# Numerical datasets and metric provenance

These CSV files represent geometric measurements of **180°-rotated KanjiVG stroke centre-lines**, not judgments by human readers.

| File | Contents | Distance metric |
| --- | --- | --- |
| [`rotation_pairs.csv`](rotation_pairs.csv) | 5,180 refined pairs: 2,410 distinct + 2,770 self-pairs | **Exact point-cloud** Euclidean distances, normalised by 109 |
| [`c2_class.csv`](c2_class.csv) | 2,770 self-pairs extracted from refined results | **Exact point-cloud** distances |
| [`rotation_pairs_top5000.csv`](rotation_pairs_top5000.csv) | 5,000 shortlisted pairs from coarse screening | **Grid distance-transform approximation**, normalised by 109 |
| [`lists.json`](lists.json) | 2,136 Jōyō + 634 Jinmeiyō glyphs | Character inventory |
| [`curated-pair-findings.csv`](curated-pair-findings.csv) | Manually selected candidate notes | Heterogeneous evidence; read row context |

**Important:** The column `hausdorff` in the refined CSV and `hausdorff` in the grid shortlist (when present) do **not** imply identical calculations or interchangeable thresholds. Grid-distance errors can affect rankings. Other scores such as `iou2` and `iou3` are grid overlap measurements at the indicated dilation radii. No numerical score is a calibrated probability of character legibility.

The total unordered space, including self-pairs, is **3,837,835**. The complete archive is not distributed with this release. After following the [reproduction protocol](../methods/rotgraph-method.md), run `python code/export_full_grid.py` from the repository root. It writes `output/catalog/rotation_pairs_full_grid.csv.gz` using a **new, explicit grid-metric schema** and stable pair ordering. The numeric results come from the pinned [KanjiVG snapshot](KANJIVG_PIN.txt); the archive is not asserted to be byte-identical to any earlier export.

**License and provenance:** KanjiVG vectors are subject to CC BY-SA 3.0; the numeric measurements here are research outputs. See [NOTICE](../NOTICE.md).
