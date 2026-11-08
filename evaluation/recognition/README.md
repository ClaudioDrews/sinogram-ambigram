# Simple Native Reader Gallery

A minimal, voluntary native-reader gallery for **one completed experimental ambigram at a time**, published at [`evaluation/recognition/`](index.html).

This page is an **exploratory feedback tool**, not the original 48-item prompted-legibility protocol ([`methods/HUMAN_EVAL.md`](../../methods/HUMAN_EVAL.md)). It does not ask for native-language status, proficiency or any identifying information.

## Participant flow

1. On the opening screen, select **Chinese (汉字)** or **Japanese (漢字)**. There are exactly two material choices; text switches to the chosen reading language automatically.
2. View **one fully consolidated drawing** on a fixed light-colored canvas. **Tap the drawing itself** to visibly rotate it **180°**; each further tap performs another animated half-turn. There is no automatic animation and no animation of source components.
3. Choose exactly one **meaning recognition** response: *both orientations*, *one orientation*, or *neither orientation*. The participant must rotate the drawing at least once before advancing.
4. See the **generation method**, with no expected character labels. Enter an optional observation.
5. Advance to the next generated drawing.
6. At the end, optionally download a **CSV** or a **TXT** file for manual sharing. Nothing is automatically transmitted.

The prompt deliberately concerns **whether a reader finds meaning** in either orientation, not just whether the form vaguely resembles a character. The simplified three-choice response does **not** record separate character identities, which orientation was legible when only one was, or detailed semantic glosses. These are intentional tradeoffs for ease of use; do not infer facts the three-choice response does not establish.

## Stimuli and method labeling

**Japanese:** 12 committed constructed drawings from [`evaluation/items.json`](../items.json): the first six `v1-top` and first six `v2-top` KanjiVG-derived stroke-salience pilot examples. The associated method is labeled as stroke-salience construction v1 or v2. Negative controls, C2 canonical source anchors and unconstructed geometry-only demonstrations are not included in this simplified gallery.

**Chinese:** coarse candidate pairs selected from preselected GB2312 anchors in [`prc/catalog.json`](../../prc/catalog.json). The page fetches static finished outline paths from a pinned Make Me a Hanzi commit and consolidates upright A with 180°-rotated B into **one black-ink SVG vector composition**. The method label is **PRC source vector union (unoptimized)**. This algorithmic construction is **not a stroke-refined or independently human-validated ambigram**. Chinese source glyphs require network connectivity to the pinned image source; unavailable individual pairs are omitted.

Each track uses only its own sources. Tracks are not comparable samples of equal difficulty. For Japanese and Chinese alike, rotating the exact same **`<img>`** element rather than switching source files guarantees consistent geometry in the two orientations.

## Export and privacy

The lightweight schema is `sinogram-simple-reader-v1`:

- `track`, `seed` and `answers[]` in the JSON-like in-memory record (no JSON download button).
- For each answer: `position`, `id`, `track`, `method`, `source`, intended `a`/`b` for subsequent offline analysis, `meaning_orientations` (0, 1 or 2), `turn_count` and free-text `observation`.
- CSV includes these fields, with UTF-8 BOM and quoted cells. TXT is intentionally more human-readable and includes the rating, method and observations.

No answers are posted to a server. Browser/server access itself is not anonymous to hosting infrastructure; the external source host receives ordinary image requests. Export files may be shared voluntarily, outside the webpage.

Do not use these exploratory responses to claim a method statistically outperforms another without native-reader review, adequate sampling, and adjudication of whether the perceived meaning matches any intended character.
