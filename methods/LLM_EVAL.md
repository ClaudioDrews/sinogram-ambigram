# Multimodal model evaluation (experimental)

**Status:** Protocol proposal and tooling description, not a completed validity study. The repository currently has **no controlled human-reader observations**. A multimodal language model may evaluate a visual candidate, but the observation is a **model response**, not human reading evidence.

## What a model can and cannot establish

A model can provide reproducible image-to-character transcriptions under specified visual prompts, reveal large errors, and compare candidate renderings within a fixed experimental design. Because training data and visual biases are unknown, successful model transcription **does not establish** native-language legibility, cultural suitability, or human perceptual thresholds. Multiple samples from one model are correlated repeated measures, not independent readers.

## Three distinct protocols

1. **Unprompted identification:** show a clean 0° image *without target glyphs*; ask for the character(s) visible. Repeat separately at 180°, with randomised order, without target glyphs anywhere in the prompt, filenames, embedded labels or metadata. Collect verbatim answers and a structured transcription; do not supply the correct characters before both observations are complete.
2. **Target-conditioned evaluation:** reveal the intended A and B after the unprompted phase and score each rendering in both orientations. This measures *agreement with a suggested reading*, not spontaneous identification.
3. **Paired visual comparison:** present before/after drawings in randomised order with the target hidden or disclosed according to the stated question; ask for comparative readability and for specific visual errors. Distinguish aesthetic preference from character identification.

## Experimental contract

- Freeze a labelled inventory, glyph-source revision, rendering size, background, scoring thresholds and held-out candidate set before the run.
- Include positive controls (identity glyphs in both orientations), negative controls (unrelated or mirrored glyphs), enclosure-heavy counterexamples, and separate JP/CN-S subsets. Never pool font/region populations without labelling the strata.
- Record source SVG SHA-256, prompt template, model provider/name/version, date, parameters where adjustable (temperature, seed), item order, image orientation and raw response. Preserve refusals, uncertain results, multi-character readings and errors.
- Use an explicit independent run log: one row per image/model/prompt/repetition. Aggregate by **stimulus and model**, not by treating samples as distinct humans.
- Report model-assisted identification accuracy separately from geometry (Hausdorff, IoU, centre optimisation) and from human evaluations, if any are later collected.
- Test prospective transformation methods on **held-out glyphs**; a gain in the optimisation objective alone does not validate character legibility.

## Minimal result format

```json
{
  "image_sha256": "<sha256>",
  "inventory": "jp-kanjivg",
  "source_revision": "<pinned-commit>",
  "orientation_degrees": 180,
  "visibility": "unprompted",
  "model": "<provider/model/version>",
  "prompt_id": "free-transcription-v1",
  "raw_response": "<unaltered-output>",
  "transcription": ["<glyph>"],
  "repetition": 1,
  "evaluated_at_utc": "<ISO-8601>"
}
```

The browser-based [evaluation instrument](../evaluation/) is intended for voluntary reader ratings and exports locally; it is **not** proof of completed testing and does not silently call model APIs. For a human study, see [HUMAN_EVAL.md](HUMAN_EVAL.md). No personal identifiers or private model API keys should be included in published evaluation data.