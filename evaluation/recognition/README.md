# Native Reader Recognition Lab (exploratory v1)

This is a **separate, blind, exploratory recognition exercise**, not a replacement for the registered 48-item prompted-legibility pilot in [`methods/HUMAN_EVAL.md`](../../methods/HUMAN_EVAL.md).

## Study-track separation

The welcome screen requires an exclusive choice **before enrollment**:

- **Chinese characters (汉字):** Mainland Chinese-source Make Me a Hanzi SVGs, selected from the pinned 6,763-character GB2312 candidate catalogue in [`prc/catalog.json`](../../prc/catalog.json). The page uses a simple upright-A / 180°-rotated-B overlay of source glyphs at 48% opacity, as in the PRC exploratory viewer. **These are not refined, constructed or validated ambigrams.** GB2312 membership does not certify the simplified/traditional form of every source glyph.
- **Japanese characters (漢字):** KanjiVG-derived drawings from the existing 48-item evaluation set (the first three in each of its four strata, 12 total), plus five pinned Rotation Lab examples (17 total). Those five examples include different *kinds*: constructed visual blends, geometry diagnostics, source anchors, and a negative control. They are **not equivalent generator methods**.

The tracks never share stimuli during a session. They have different source glyphs, different selection logic, and different construction maturity, so **do not combine them into one success rate or compare raw success percentages as if the inputs were matched**.

The website's **EN / 中文 / 日本語** buttons translate *only interface copy* and never select or replace the stimulus track. The rater separately records their primary reading language (Simplified Chinese, Traditional Chinese, Japanese, other) and proficiency. English, Chinese and Japanese versions of the task convey the same intent.

## Blind recognition sequence

1. Consent, mutually exclusive material track choice, primary reading language and proficiency.
2. Randomize **within the chosen track only**, with a recorded client-generated random seed. No expected characters, methods, geometry scores, or provenance are shown during judgement.
3. Present orientation A at 0°; record: identifiable / uncertain / unrecognizable, free-text observed character, and confidence (1–5 if possible).
4. Show the exact same drawing rotated 180°; record the same independent reading for B.
5. Only after both readings, present A and B simultaneously and ask whether the rater perceived one character, two different meanings, related variants/meanings, unreadability, or uncertainty. Optional notes.
6. Export **locally** in UTF-8 JSON or BOM-prefixed RFC-style quoted CSV. The participant manually shares the file; no form submission is implemented. After finishing, the original expected source codepoints and provenance are revealed.

The questionnaire asks for no account, name, contact information, IP address, or age. GitHub Pages and the upstream image host can still receive ordinary HTTP connection logs; do not describe website access as network-anonymous. In the Chinese track, source glyphs are retrieved from the same **pinned** upstream commit used by the existing PRC explorer. The questionnaire does not transmit answers. The Japanese track embeds its source glyphs in repository files.

## Data schema

`native-reader-exploratory-v1`: `track`, `language` (interface language), `respondent.native`, `respondent.proficiency`, `seed`, `protocol`, and ordered `items[]` with source provenance, method, stratum, intended readings (for post-collection evaluation), independent free-text readings and recognition responses for both orientations, relation response, optional comment and skipped status.

The webpage's `classification` field is an **analyst-friendly label for what a rater reported**. It does not certify linguistic identity, character equivalence, semantic meaning or human-legibility thresholds. It is possible for a participant to type one character while declaring an uncertain reading; preserve both raw fields.

## Interpretation and quality controls

- **Type 1 candidate:** both readings independently recognizable, with the *same actual character*. Orthographic self-symmetry alone is insufficient.
- **Type 2 candidate (the more useful goal):** both independently recognizable as different characters with different meanings, assessed for the participant's language and variant conventions.
- **Failure:** one or both orientations not recognizable; record separately from incomplete/skipped/uncertain.
- A different character may have the same or closely related meaning; keep this as a distinct ambiguity category.
- **Evaluate per track first**, and then per `kind` and `method`. Do not claim a technique works because a geometry-diagnostic overlay was judged recognizable.
- The source forms and external preselected pilot examples do not constitute a probability sample. Japanese and Chinese samples are not matched for complexity, glyph inventory, construction method or known readability.
- **Do not present the screenshot conversation with a single Chinese reader as an item-level measured dataset.** It is qualitative feedback motivating this protocol, not a completed blinded study.
- Before any formal inference, freeze an item manifest, implement identity/variant adjudication (native-language experts), multiple independent raters, verified region-specific source forms, appropriate sample-size planning and pre-registered analysis. Consent and publication practices may require additional ethics/privacy review.

## Deployment and reproducibility

The static page is [`index.html`](index.html), hosted at `/evaluation/recognition/` after this branch is merged and GitHub Pages deploys. It consumes the committed `evaluation/items.json`, the committed PRC derived catalogue and the pinned source for Chinese SVG images. No database or write API is needed.

This module is deliberately isolated from the original [prompted-legibility evaluation](../). Its original items, builder, language strings and statistical protocol are untouched.
