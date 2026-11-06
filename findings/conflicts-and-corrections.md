# Conflicts Between Sources and Corrections Recorded

IDs are stable references used across the docs. Each entry states the claims, who made them, and the current status. **Nothing here is resolved by this publication**; where a check was possible it is noted. Evidence labels are defined in the [repository README](../README.md).

## A. Pair-level conflicts

| ID | Topic | Claims (source) | Status |
|---|---|---|---|
| C-01 | Why do canonical pairs score low? | GLM: "degraded by the font" (0.40/0.52/0.44) · Claude: may be metric artefacts (thin-stroke IoU hypersensitivity) and wanted soft IoU/chamfer first · Kimi: rendering artefact for 土士 | Open; v2/Mistral metrics reduce but do not settle it |
| C-02 | 未↔末 | GLM mid-log: first R(未)≠末, then "R(未)=H(未)=末" (V-symmetric) · Claude: that correction is wrong (legs go on top; 末 differs from 未 by bar length only); R(未)≈半 · numbers: GLM .44, GPT .436/.373, Claude v1 .63, v2 .56, Mistral .111 | Evidence favours **not** a rotation pair (Claude visual); unresolved by an independent human test |
| C-03 | 土↔士 | DeepSeek (derived): exact · GLM .40 · Claude: refuted (head/tail shift ≈25% em; absent from v2 candidates) · Kimi .864 gothic/.808 Mincho (attributes .40 to rendering; provenance of number unclear) · GPT .242/.221 · Mistral .155 (data quirk) | **Unresolved**; Kimi vs GPT/Claude/GLM disagree by >0.5 |
| C-04 | 上↔下 | Claude v1 H .83 vs R .44 and GLM H .66>R .61 → mirror; yet Claude v2 CSV lists 上,下 at .793; GPT .530 aligned; Mistral #51 | Mirror per reasoning; metric still scores high — mirror filter needed |
| C-05 | 甲↔由 | [second pass: 甲 occurs nowhere in `v2_pares_cruzados.csv`, lowest kept score .662] Claude v2 text: first neighbour of R(甲), .92 (but pair is **absent** from `v2_pares_cruzados.csv`; only 3 pairs ≥ .9 in it) · RPT-CONSOL: .818 → .92 · GPT .455/.385 · GLM .52 · Mistral rank 24/6,328 · Claude visual: R(甲)=由 · CHISE treats 甲 as atomic (IDS cannot separate) · Kimi: 甲 self .818 although not C2 | Visual evidence good; metric support varies |
| C-14 | 丁↔上 and other text-vs-CSV mismatches | Claude text .81 vs CSV .746 (丁,上 line 92); 目↔自 v1 .958 vs v2 .752; 玉 listed among "≥.85" self-ambigrams though CSV .848 | Discrepancy documented only |
| C-15 | 旦 | Meta lists 旦↔旦 self-pair; measured/visual R(旦)= bar over 日; Claude: 旦~目 false positive; 旦↔百 .981/.862/#48 | 旦 not self; 旦↔百 candidate |

## B. Method/claim conflicts

| ID | Topic | Claims | Status |
|---|---|---|---|
| C-06 | C2 lists | RPT-META lists 士 木 品 吕 as C2; contradicted: R(士)≈干 (士 is not C2); 木 is not point-symmetric; measured C2 lists differ per metric ([results R-C2](../findings/results-summary.md)); editorial: 木 is only left–right symmetric and 品 (one box above two) is not point-symmetric, although Mistral's table lists 品 at d .110 | Meta list unreliable |
| C-07 | 昌/吕/呂 | Algebra: exact iff S C2 · GLM .54/.52, GPT self .091–.194 (昌), .203–.382 (呂) · Mistral: 昌 C2 rank 6 (.053) · Claude: CHISE 昌 = ⿱日曰 (≠ 日日), 昌 吕 not Jōyō · Kimi: absent from top | Slot-convention hypothesis (GLM); Mistral's median metric disagrees |
| C-08 | Paper vs secondary sources | Paper: 46 hiragana; **724 = pairs in Nomura's book (ref 1)**, not an algorithm output; 325/724 readable (RPT-META says 324) · Qwen/RPT misread as graph scores (45%/26%); GLM flagged it | Documented ([paper doc](../methods/inoue-takahashi-2020.md)) |
| C-09 | Unsupported statistics | "3× chance when IDS top-level matches" (`META-DECK` slide 7, `LOG-META`, `RPT-CONSOL`); "pair choice is 70% of the work" (`META-DECK`, `RPT-CONSOL`, `LOG-META`, `CAT-XLSX`) — **not in the paper**, no measurement | Treat as [CLAIM] |
| C-10 | IDS data/operators | GLM earlier errors ("⿷ no dual", "⿸ dual ⿿") corrected · ⿾⿿ names confirmed only via secondary sites (symbl.cc, fileformat.info, Wikipedia; unicode.org PDF blocked) · IDS source: CHISE (Claude, GPT planned) vs UCD 15.1 (DeepSeek) · Claude: GLM's "Noto Sans SC" vs JP forms | Open: which dataset |
| C-11 | 全力↔不屈 | RPT-CONSOL/META/DECK: R(力)≈不, R(全)≈屈 (fusing three horizontals of 王 into 尸); source cited: a community post on stroke-density selection · Claude v2 list: 全 only with 手/芋 | Unmeasured; [CLAIM] |
| C-12 | ⿻ operator | DeepSeek reverses children; GPT `Rterm` and Claude keep order; no test | Open ([algebra doc](../theory/ids-rotation-algebra.md)) |
| C-13 | Mistral data provenance | Called "derived from KanjiVG/animCJK via Make Me a Hanzi" in one place and as KanjiVG-equivalent in another | Unverified |
| C-16 | GPT report table header | First table headed "IoU after rotation and alignment" but equals the unshifted ranking; aligned ±3 px is a second table (上↔丁 .680, 王↔玉 .671) | Documented (exp-01) |

## C. Corrections made inside the sources (kept for traceability)

* GPT: ⿲ ⿳ have **3** operands (not 4).
* GLM: 圭/朋 not self-ambigrams; 上↔下 reclassified as mirror; dual-map names corrected; "R(撇) goes up-left" wording corrected (it is the ink profile that flips, not the direction).
* Claude: v1 failed its own sanity controls and said so; 土士 "exact" claim refuted (then contested by Kimi); 未末 correction by GLM rejected.
* Kimi: 土士 .40 → .864/.808 (Source Han).
* GPT (third turn): ε "iff" needs conditions; IDS algebra must be typed.
* Gemini: re-framed the contact-sheet reading after the owner's "Nope. 180°" (exp-06).

## D. Referenced-but-missing items

* `sinogram_ambigram_prototype.zip` (mentioned in `EMAIL-GPT`): **not present as an archive**; the unpacked GPT files are in `gpt-run/`.
* Catalog source index rows #9 "Ambigramas de Sinogramas" and #12 "Ambigramas Jōyō": not files in the folder; the owner says they are **unknown**.
* Claude's `res_*.npz`, `w1.npz`, `cand.json`, `trees.json` (and CHISE IDS files): **confirmed absent** from `claude-run/` after a re-check of Drive and `sources/`; per the owner all files of Claude's zip are already in `claude-run/`, so these were never part of it. Regenerable.
* Kimi's code and result files; GLM's `rotation_family_check.py`: absent.
* Nomura's book: not read by any run; the six laws' text is not online (nomura-sources-and-findings).

## E. Script/label inconsistency found in a second-pass code read

| ID | Item | Detail |
|---|---|---|
| C-17 | `analyze.py` console label vs code | Prints "minimum of the two fonts" / "score=min(gothic,mincho)" but uses the gothic matrix only; the v1 `EXPLORATORIO_*` CSVs are therefore gothic-only (exp-03). |

## F. MiniMax internal divergences (X1–X8) — recorded, not corrected

The MiniMax run (`exp-08`) disagrees with itself in eight places. **No number was changed here.** Each item states both readings and, where a check exists, what the check gave. The independent review below confirms X1–X4 and X7 and adds the rest. X1 was the only item that a measurement could close; it is closed at §F.1 (2026-11-05), the other seven stay open as recorded.

| ID | What conflicts | Readings | Status |
|---|---|---|---|
| C-18 / **X1** | Number of evaluated pairs | Method doc and log: 3,835,785. Report §4.1 and §6: 3,837,835. For n = 2,770: C(n,2) = 3,835,065; with self-pairs, 3,837,835. The first value matches neither. The rotation-pairs note then says the full file has 3,835,785 data rows | **Resolved 2026-11-05** — row count of the stored `.csv.gz`, not a formula. See the measured table below: **3,837,835** is correct; **3,835,785 is an erroneous report**. Historical quotes are kept and marked `[DIVERGENCE]` |
| C-19 / **X2** | Graph size at H ≤ 0.10 | Report table: 655 edges / 537 nodes / largest component 402. Report text and log: 710 / 558 / 440. At H ≤ 0.085 both agree (28 / 44) | **Open and worse than a typo**: neither count is the real one — the table saturates at 2,410 refined pairs, so above ~0.09 the count is an artefact of the cut. Independent recount (exact, all candidates refined): 31 edges at 0.085, 135 at 0.09, 2,301 at 0.10 |
| C-20 / **X3** | Verification V2 (negatives at the bottom of the C2 class) | Method doc: 又 乃 刀 万 之 九 丁 have H > 0.45. `c2_class.csv`: they sit at H 0.166–0.344 (positions 1,886–2,766); the largest H in the file is 0.434 (入) | **Confirmed** by the review; the review replaces the criterion (R5, median of normalised negative ranks) and passes by a narrow margin |
| C-21 / **X4** | "Confirms 十 口 日 田" | Report §4.2. In `c2_class.csv`, 目 日 一 田 口 occupy positions 1–5, but 十 is **370th** (H 0.115); 工 1,016th; 二 1,836th | **Confirmed**; the review adds 工 三 王 二. Worse: 菫 (#7) and 鰯 (#8) rank above 圏 (#10) and 圃 (#9) — a metric bias, not a finding |
| C-22 / **X5** | Stroke count as a predictor | Report §4.5 states it without any analysis | **Partly answered in another variable**: the review measured *density* (Spearman −0.43 between H and skeleton length on self-pairs). Stroke count itself remains untested → treat the sentence as [CLAIM] |
| C-23 / **X6** | The `rank` column of `rotation_pairs.csv` | It mixes self-pairs and distinct pairs (吉↔阜 rank 6, 由↔甲 rank 10) | **Confirmed and quantified**: 5,180 = 2,770 self-pairs + 2,410 distinct pairs; the "top 2,500" already contained 90 self-pairs. "2nd place" is therefore *among distinct pairs* |
| C-24 / **X7** | Hub bias | 圃 appears in 7 of the first 25 pairs | **Confirmed and larger**: degree 41 for 圃 and 獅, 38 for 園, 33 for 固 in the top-1,000 by grid metric; 58 for 圃 in the review's exact re-run. After length normalisation the hubs become 羽 (143) and 三 (132). Recommendation: mutual-5NN graph (1,568 edges, 1,466 nodes, giant component 1,187) |
| C-25 / **X8** | Two different "H" in the same folder | `c2_class.csv` / `rotation_pairs.csv` use exact distances; `rotation_pairs_top*` use grid distances (目 0.03229 vs 0.03670; 日 0.04358 vs 0.05199). Dilated IoU is identical in both | **Structural, not an error**: label which scale a table uses; do not mix. The grid cut at 5,000 is arbitrary among ties (rows 4,997–5,000 all at H = 0.11009) |

### F.1 X1 — the measurement that closes it (2026-11-05)

The conflict was settled by counting the stored file, not by a formula. File: `rotation_pairs_full.csv.gz`, 82,212,176 bytes as stored on Drive.

| Check | Result | Label |
|---|---|---|
| SHA-256 of `.csv.gz` as stored | `f4b929693148146379bc71c0783c81279149e4834ed15e11c573fbf67aba66e0` | `[MEASURED]` — identical to the previously `[REPORTED]` value |
| Header | `rank,a,b,a_set,b_set,a_strokes,b_strokes,hausdorff,chamfer,rms,iou_dil2,iou_dil3,iou_dil4` | `[MEASURED]` |
| Data rows | **3,837,835** | `[MEASURED]` |
| Unique characters in `a`∪`b` | **2,770** | `[MEASURED]` |
| Rows with `a == b` (self-pairs) | **2,770** | `[MEASURED]` |
| Rows with `a < b` | 3,835,065 | `[MEASURED]` |
| Rows with `a > b` | 0 | `[MEASURED]` — pairs stored unordered, plus self |
| Consecutive duplicate `(a,b)` | 0 | `[MEASURED]` |
| C(2770,2) | 3,835,065 | formula |
| C(2770,2) + 2,770 self | 3,837,835 | formula — **matches the file** |

Outcome:

* **3,837,835 is correct** for this file (unordered pairs including self-rotation), so the report/curated figure stands.
* **3,835,785 is an erroneous report**: it matches neither `C(n,2) = 3,835,065` nor `C(n,2)+n = 3,837,835`. It is **not** rewritten in the faithful translations or in the Portuguese originals; those passages carry `[DIVERGENCE: X1 resolved 2026-11-05 — measured file has 3,837,835; the method figure 3,835,785 is erroneous]`.
* `rotgraph/data/README.md` and `rotgraph/README.md` now carry the count and the checksum as `[MEASURED]`; the status of the GitHub Release asset remains **`planned`** — the file exists privately, the public Release is not published.
* OQ-27 is closed.

Also noted: `catalog.py` has a duplicated `paths` import; the log refers to `output/catalog/…` and `the original Portuguese-named output folder/index.html`, paths that do not exist in the delivered folder; the three `hailuo_*.jpeg` files are the `top_pairs_sheet`, `top_ambigrams` and `c2_sheet` images of the log (mapping inferred from content, [NOT VERIFIED]).

## G. Independent review of the MiniMax run (CR1–CR7)

A three-turn conversation between the owner and a model labelled "Claude", delivered with a script (`rotgraph_v2.py`) and a validation report. It re-implemented the method from scratch (own parser, KanjiVG from GitHub, 2,770 glyphs from `c2_class.csv`), on the reviewer's sandbox, **not** in the owner's environment and **not** against `rotgraph.zip`; every number is [REPORTED].

| ID | Finding | Evidence / caveat |
|---|---|---|
| CR1 | **Density bias**: dense glyphs score better just by covering the box. ρ(H, skeleton length) = −0.43 on self-pairs | Per-node median normalisation was not enough (ρ = −0.20; 又 rises from 2,107th to ~405th); log-length regression normalisation (`--norm-mode lenfit`) gives ρ = +0.02 (R3 PASS) |
| CR2 | **Unlikely glyphs at the top**: 菫 (#7) and 鰯 (21 strokes, #8) above 圏 and 冒; 回 at #6 | Reproduced in `c2_class.csv`. 鰯 has H = 0.0751; the review's replica gives 0.073 |
| CR3 | **Rotation centre**: rotation is about the fixed box centre (109 − x) with no translation or scale alignment; this limit appears in neither list of limits in the method doc | Hypotheses only: centroid alignment improves 十 (0.115 → 0.070) and 中 (0.110 → 0.084); bounding-box alignment worsens several; 工 二 三 王 stay between 0.13 and 0.18. The reviewer withdrew his own "symmetric by construction" sentence |
| CR4 | **Graph reliability**: MiniMax edges are only trustworthy up to ~0.085–0.09 | Sampled recall on the complement of the grid proxy's top-2,410: 97% below 0.085, 86% below 0.09, 43% below 0.10. `rotgraph_v2.py` computes a "reliable threshold" of 0.11 for **its own** refined set (71,001 pairs) — two different candidate sets, not comparable |
| CR5 | **Grid vs exact by band**: the global r = 0.944 may hide a worse correlation at low H | r = 0.73 in 0.08–0.10; 0.81 in 0.10–0.12; 0.90 in 0.12–0.14; 0.996 above 0.14 |
| CR6 | **Tests that fail in the review itself**: R4 (positives in the normalised top-20) is **FAIL** — 中 is 30th (十 7th, 日 3rd, 田 5th, 口 4th, 目 2nd); R5 passes narrowly (1,390 vs a 1,385 cut) | `validacao_report.md`; no criterion was adjusted after the failure |
| CR7 | **Incomplete coverage of the normalised score**: estimated recall 0.92 with `--norm-top 30000` | Raising `--norm-top` closes the gap at an unmeasured cost |

The review also lists eleven improvements, each with an acceptance criterion; they are tracked as a roadmap in tool status and roadmap. It is internally inconsistent in three places (degree of 圃 41 vs 58; "reliable graph" up to 0.085–0.09 vs 0.11; per-node median recommended and then discarded) — recorded as they are.

## Related

- [Results summary](../findings/results-summary.md)
- [Pair evidence matrix](../findings/pair-evidence-matrix.md)
- [KanjiVG rotation-graph method](../methods/rotgraph-method.md)
- [Limitations](../findings/limitations.md)
