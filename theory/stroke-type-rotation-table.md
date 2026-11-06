---
title: "Stroke-Type Behaviour Under 180° Rotation"
id: stroke-type-rotation-table
type: research
status: reviewed
evidence: [DERIVED, CLAIM, PLAN]
tags: [sinogram, stroke, rotation-180, algebra]
created: 2026-11-01
updated: 2026-11-05
language: en
license: MIT
translations: {zh: machine-assisted, ja: machine-assisted}
related: [ids-rotation-algebra, family-rules, glossary-and-notation]
---

# Stroke-Type Behaviour Under 180° Rotation

Sources: `LOG-MULTI` (Claude critique → GLM table; DeepSeek round), `LOG-DEEPSEEK` (cost table), `CAT-XLSX` rows ("Stroke Re-typing Mapping", "Stroke Class Inversion"). Labels: see README (source reference in repo2: `../README.md`).

> **Reliability caveat (owner, 2026-11-01):** `RPT-RULES`, `RPT-CONSOL`, `RPT-FACES` and the catalog `CAT-XLSX` were probably produced by Google NotebookLM/Gemini; the owner warns that these tools make many errors. Treat every claim in this file that rests **only** on those four sources as **unverified** ([CLAIM]), even where it is phrased as fact. Claims also backed by the paper `PAPER`, a script run in `sources/`, or Nomura's own interviews (nomura-sources-and-findings (source reference in repo2: `../research/nomura-sources-and-findings.md`)) are stronger.

## 1. Principle [DERIVED]

Rotation by 180° preserves the *direction line* of a stroke (a line keeps its slope) but reverses its *ink profile* (head ↔ tail, thick end ↔ thin end), swaps left/right and top/bottom. Hence stroke classes behave as:

| Class | Strokes | Under R |
|---|---|---|
| **Preserved** | 横 (horizontal), 竖 (vertical) | map to themselves (head/tail swapped) |
| **Swapped** | 撇 (left-falling) ↔ 提 (rising); 横折 ↔ 竖折 (right-angle turns) | `R(撇)=提`, `R(横折)=竖折` (`LOG-MULTI`: Claude/GLM verified by sources and reasoning) |
| **Broken** (need re-typing) | 捺 (right-falling), 点 (dot), hooks (钩, e.g. 亅, 乚), many curves | rotated form is not a standard stroke; must be replaced/hidden |

The 撇↔提 equivalence holds cleanly for **monoline gothic/sans** fonts; in Mincho/brush styles stroke modulation (triangular ends, 捺 tail) makes it inexact — hence the "font regime" split recommended in `LOG-MULTI` (gothic for discovery; Mincho adds a further defect).

## 2. Cost table proposed by DeepSeek (`LOG-DEEPSEEK`; STROKE_TRANSFORM_COST) [PLAN]

| Transformation | Cost |
|---|---|
| straight lines (一, 丨) | 0.0 |
| 撇 ↔ 提 (gothic) | 0.0 |
| right-angle turn 横折 ↔ 竖折 | 0.2 |
| hook removal 亅 ↔ 丨 (replace hook by short stroke) | 1.2 |

Stroke classes listed: 一, 丨, 丿, 丶, ㇀, 乙, 亅, 乚, ㇉. A pairwise `stroke_cost` function and a `STROKE_CLASS` mapping were drafted; **never executed**. The 1.2 and 0.2 values are arbitrary design choices, not fitted.

## 3. Observed consequences in experiments

* 上↔丁 needs "hook → short stroke" re-typing (Claude v2: 0.81, "approximate, requires swapping the hook for a short stroke"; GPT aligned IoU 0.680).
* 王↔玉 needs the dot (丶) hidden/attenuated in ink mass (GPT 0.644/0.671).
* The visual-reading experiment found R(丁) keeps the hook at the top (ends up as 丄-like), confirming the re-typing need (exp-06 (source reference in repo2: `../experiments/exp-06-visual-reading-of-contact-sheet.md`)).
* Errors fixed on the way: GLM's first claims about which stroke "goes up/left" under R were corrected (Claude/DeepSeek rounds); the claim about 未/末 flipped within the log: GLM first said R(未)≠末, then "corrected" itself to R(未)=H(未)=末, and Claude rejected that correction (stroke legs of 未 end up on top; 末 differs from 未 only in bar lengths) — see [conflicts C-02](../findings/conflicts-and-corrections.md).

## 4. Open

* No stroke-level table was validated on real font outlines or KanjiVG stroke types (KanjiVG never ingested).
* Costs and the 撇/提 equivalence are untested in brush styles.

## Related

- [IDS rotation algebra](../theory/ids-rotation-algebra.md)
- [Family rules](../theory/family-rules.md)
- Glossary and notation (source reference in repo2: `../project/glossary-and-notation.md`)
