# Native Reader Recognition Lab (exploratory v2)

This is an **exploratory, intended-label-blind recognition exercise**, separate from the registered 48-item prompted-legibility pilot in [`methods/HUMAN_EVAL.md`](../../methods/HUMAN_EVAL.md). Source characters, expected answers, construction methods and source scores are not disclosed during ratings. The preliminary construction animation itself may cue component geometry; **do not call this a fully blinded perceptual experiment**.

## Independent material tracks

The landing page requires a choice of **Chinese OR Japanese** before the profile questionnaire. The materials are never mixed:

- **Chinese (汉字):** candidate pairs from the pinned GB2312-derived [`prc/catalog.json`](../../prc/catalog.json), using source glyph outlines fetched from a pinned Make Me a Hanzi commit. A parser extracts the **finished, unanimated stroke silhouettes** from each source SVG; it removes the original stroke-order animations, grey drawing guides, animation masks and animated paths. The two silhouettes are combined into **one black-ink vector composition**, with the B outline rotated 180° before combination. This is a deterministic geometric union of source forms: **not a stroke-refined, optimized or human-validated ambigram**. Candidate pairs whose source geometry cannot be retrieved are skipped with a console warning; fewer than four available candidates abort the session. Mainland source does not certify each character's simplified/traditional form.
- **Japanese (漢字):** 12 KanjiVG-derived constructed SVGs from the existing 48-item [`evaluation/items.json`](../items.json), choosing three from each of four pilot strata. Up to five additional Rotation Lab examples (constructed demonstration, geometry diagnostics, C2 anchor, negative control) are added if their geometry can be produced. A failure of an optional example no longer prevents the 12 committed pilot drawings from appearing.

**Dark-mode visibility:** the drawing stage and side-by-side comparisons retain a fixed light paper background because the SVG ink is dark, even when the surrounding UI follows the browser's dark theme.

The **EN / 中文 / 日本語** controls translate interface text independently of the material track. The questionnaire also records the respondent's main reading language and self-reported proficiency. These tracks are not comparable samples: do not pool their rates or treat them as equivalent generator outputs.

## Visual and rating sequence

1. Record voluntary participation, source track and reading background.
2. Randomize within the selected material track, recording a client-side random seed. Intended character identities remain hidden until after the entire session.
3. Display a **construction animation**: Chinese source silhouettes move into a consolidated vector drawing; Japanese final strokes are progressively revealed. The animation ends before advancing to the first rating. When `prefers-reduced-motion: reduce` is active, display the static final SVG without this animation.
4. Present **one consolidated drawing at 0°**. Record whether it is recognizable, the independently typed character (when possible), **whether the reader recognizes its meaning** (yes / no / unsure), an optional gloss in the respondent's own words and confidence (1–5).
5. Save the 0° response **before** rotating the **exact same DOM image** 180° with a visible CSS transition. Save the same independent character-and-meaning responses for this second orientation.
6. Display both orientations side by side using **the same static consolidated SVG** (0° and 180°), record the perceived relation between readings and an optional comment.
7. After all stimuli, reveal intended identities and construction provenance. The participant may manually export UTF-8 JSON or BOM-prefixed CSV; the site does not submit results to a server.

The meaning question is hidden when a drawing is explicitly rated unrecognizable; such missing semantic responses remain null. Switching interface languages preserves unsent responses.

**Interpretation caution:** The animation may prime a participant to attend to the source components. Although expected identities are not written on screen until the end, this is **not a strictly construction-blind experiment**. A future controlled comparison could omit construction animation for a separate group and compare results.

## Data format

The export schema is `native-reader-exploratory-v2` (not interchangeable with v1). It preserves `track`, interface `language`, `respondent`, `seed`, protocol metadata and ordered item records with provenance and original intended readings.

For **each orientation**, exports contain the typed character, recognition status, confidence, a semantic recognition code (`meaning_a` / `meaning_b`: **0 yes**, **1 no**, **2 uncertain**, **null not asked/not answered**) and optional free-text gloss (`meaning_gloss_a` / `meaning_gloss_b`). `both_meaningful_reported` is true only when both orientations received affirmative meaning reports, false when responses exist but this is not true, and null for skipped/incomplete responses. The independently reported cross-orientation `relation` is also preserved.

The `classification` output is a convenience label for **what the participant reports**, not independently established character identity or verified semantic equivalence. Do not treat free-text glyph entries or perceived semantic relations as ground truth without native-language adjudication.

## Constraints and reproducibility

- **Type 1:** both orientations independently identify the same character and a recognizable meaning.
- **Type 2:** both orientations independently identify distinct characters with distinct meanings.
- **Failure or ambiguity:** preserve unreadable, semantically unknown, uncertain, skipped and incomplete results separately. A recognizable form does not necessarily imply a recognized meaning.
- The Chinese candidate is a single *rendered* vector composition, but its construction remains an unoptimized union. Geometric equivalence or a successful CSS rotation does not prove ambigram readability.
- The two cohorts differ in source data, methods and selection; comparisons must be stratified by track and stimulus type.
- Before formal inference: freeze a manifest, independently verify regional glyph forms, recruit multiple native readers, adjudicate character identity and meaning, evaluate presentation-order bias and develop a preregistered study design. Consent/publication may require an ethics/privacy review.
- The screenshot conversation with one Chinese native reader remains qualitative design feedback, **not** a completed blinded study.

The page resides in [`index.html`](index.html), with repository-relative links to its Japanese JSON and Chinese derived catalogue. Chinese source outlines are fetched at runtime from the pinned public GitHub source; this requires network access and the image host may receive connection metadata. No personal responses are sent to GitHub by the questionnaire.

This module does not change the earlier [prompted-legibility evaluation](../) or its registered protocol.
