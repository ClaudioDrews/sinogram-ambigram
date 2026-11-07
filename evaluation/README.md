# Human evaluation

This folder holds the material for the pilot perceptual study: the page a
participant sees, the item selection it draws from, and the instructions for
running it.

> **No human-reader study has been run yet. Evaluation with multimodal LLMs is documented separately in [`methods/LLM_EVAL.md`](../methods/LLM_EVAL.md).** Nothing in this repository has been validated
> by human readers. See [`methods/HUMAN_EVAL.md`](../methods/HUMAN_EVAL.md)
> for the full protocol.

## Files

| File | Role |
|---|---|
| `template.html` | Page template. Contains two empty payload blocks and no items. |
| `text.json` | Interface text, English and Japanese. |
| `items.json` | The selected items. Generated, not hand-edited. |
| `build_page.py` | Injects the items and the text into the template. |
| `index.html` | The built, self-contained page displayed on GitHub Pages. |

## Building the page

```bash
python code/stage9_select_pilot_items.py            # writes evaluation/items.json
python code/stage9_select_pilot_items.py \
    --render evaluation/items.json                  # adds the rendered SVGs
python evaluation/build_page.py                     # writes evaluation/page.html
```

`index.html` is a single file with no external requests. It works from a USB
stick, from a local file, or from any static host.

## How the page behaves

- **Consent first.** A short statement of what happens and what is recorded,
  with an accept and a decline button. Declining clears the page.
- **Three screening questions**: native language, reading proficiency, age
  band. No name, no contact details, no identifier of any kind.
- **Randomised order.** The order of the drawings is fixed by a random seed
  generated in the participant's browser and stored in `localStorage`, so a
  reload keeps the same order for that participant while different
  participants see different orders. The seed travels with the exported data.
- **No stratification shown.** The geometric score, the z-score and the
  stratum are never displayed. The stratum appears only in the exported data,
  for the analyst.
- **Rotatable.** Each drawing has a 180° toggle. Participants are asked to
  score *both* readings, because an ambigram needs both to work.
- **Export.** JSON or CSV, generated in the browser. Nothing is transmitted.

## Running a session

1. Build `page.html` and send it to the participant, or host it.
2. The participant opens it, accepts, answers the screening questions and
   works through the drawings.
3. They download the results file and send it back.
4. Join the responses against `items.json` on `id` to recover the stratum.

Keep the seed with each response file. Two files with the same seed are the
same participant's session; a response file without a matching seed cannot be
ordered against the others.

## Analysis

Follow [`methods/HUMAN_EVAL.md`](../methods/HUMAN_EVAL.md) §6. The decision
rule in §7 was fixed before any data exist and uses rank statistics
(Mann–Whitney exact, Cliff's delta) rather than a difference between group
medians, because the median-gap version has power 0.68 where the rank test
has power 0.97 under a true difference of one Likert point.

## Editing the interface text

`text.json` holds every string. Both languages must define the same keys; the
page falls back to English for anything missing. When adding a key, add it to
both.

## Privacy

The page sets no cookies, registers no service worker, makes no network
request after the initial load, and stores one value in `localStorage`: the
random seed. If a participant clears it, the order changes and the exported
file carries the new seed.