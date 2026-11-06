---
title: "Proposed Methods, Algorithms and Roadmaps (not yet implemented unless stated)"
id: methods-and-pipelines-proposed
type: research
status: reviewed
evidence: [PLAN, DERIVED, CLAIM]
tags: [sinogram, ambigram, rotation-180, algebra]
created: 2026-11-01
updated: 2026-11-05
language: en
license: MIT
translations: {zh: machine-assisted, ja: machine-assisted}
related: [existence-criterion, tool-status-and-roadmap, exp-08, exp-05]
---

# Proposed Methods, Algorithms and Roadmaps (not yet implemented unless stated)

Sources: `LOG-MULTI`, `LOG-GPT1`/`LOG-GPT2`, `LOG-QWEN`, `LOG-DEEPSEEK`, `RPT-RULES` §3 & §6, `RPT-META` §3,§5,§7, `RPT-CONSOL` §5, `META-DECK` slide 12, `CAT-XLSX`. Labels: see README (source reference in repo2: `../README.md`). **Everything here is [PLAN] unless a row says "run".**

> **Reliability caveat (owner, 2026-11-01):** `RPT-RULES`, `RPT-CONSOL`, `RPT-FACES` and the catalog `CAT-XLSX` were probably produced by Google NotebookLM/Gemini; the owner warns that these tools make many errors. Treat every claim in this file that rests **only** on those four sources as **unverified** ([CLAIM]), even where it is phrased as fact. Claims also backed by the paper `PAPER`, a script run in `sources/`, or Nomura's own interviews (nomura-sources-and-findings (source reference in repo2: `../research/nomura-sources-and-findings.md`)) are stronger.

## 1. Candidate-generation methods

| Method | Description | Source | Status |
|---|---|---|---|
| Rotation graph (Approach 1) | compute `d(F(a), R·F(b))` for all Jōyō pairs (C(2,136,2) = 2,280,180 unordered pairs, i.e. ≈2.3 M; brute force viable; indexes only needed for full Unicode CJK); rank pairs below ε₀ | `RPT-RULES`, `META-DECK`, `LOG-MULTI` | **run** with raster/skeleton/profile/median metrics (experiments (source reference in repo2: `../experiments/README.md`)); KanjiVG-based version done at 2,770-glyph scale in exp-08 (source reference in repo2: `../experiments/exp-08-minimax-rotation-graph.md`) |
| Coarse-to-fine screening | packed-bitmap IoU at zero translation for all pairs → bounded top-k heap → ±3 px refinement of top 2,000 | `PKG-GPT` (`score_glyphs_large`) | coded, **never run** (needs full Jōyō list + font) |
| Cloud-based nearest neighbour | signature indices (Fourier descriptors, skeleton graph, ink distribution, Betti numbers) + ANN search; two-stage shape then semantic filter | `LOG-QWEN`, `CAT-XLSX` | proposal |
| Optimal-transport "distance maps between kanji" mining | hierarchical OT distance over nested components (Schuhmacher 2023, arXiv:2304.02493) + IDS filter → top 1,000 candidates. *Source note: `RPT-META` cites the distance maps and "Yencken & Baldwin" together; Yencken & Baldwin's work is rendered-image / radical-vector kanji similarity (ECAI 2008, COLING 2008), a different method, so the attribution is recorded as unverified* | `RPT-META` | proposal; paper not read |
| Procrustes / Hausdorff on stroke point clouds | per-stroke normalised clouds | `META-DECK`, `LOG-DEEPSEEK` | Mistral ran a chamfer + greedy stroke matching variant on 113 chars |
| IDS exact pairs | enumerate IDS trees, rewrite with R, look for exact matches (τ=0) | `LOG-DEEPSEEK`, `PKG-GPT` | operator rules unit-tested; no corpus run |

## 2. Construction methods (making `g`)

| Method | Description | Source |
|---|---|---|
| Generalised Inoue–Takahashi | KanjiVG strokes (no thinning) → graph (nodes = feature points) → **GED with merge/split** instead of isomorphism → **TPS/CPD smooth warp** instead of affine → OCR/CNN as ρ proxy; hierarchical graphs `H=(V,E,C,R,A)` over stroke/component/character; Jacobian bound `‖J−I‖<δ` to avoid folding | `RPT-RULES` §3, `RPT-META` §3.2, `LOG-GPT1` §4 |
| Component permutation search | choose σ∈S_n minimising `Σ D(c_i, R c_σ(i)) + L_layout` for repeated components (品, 晶, 森) | `LOG-GPT1` |
| Enclosure preservation | decompose `Enclose(O,I)`; keep outer boundary fixed and optimise interior (回 困 問) | `LOG-GPT1`, `CAT-XLSX` |
| Continuous ink-density model | Bézier/B-spline strokes `γ_i(t)`; `F_S = 1−exp(−Σ∫a_i K(·−γ_i)dt)`; gradient descent | `LOG-GPT1` §7, `CAT-XLSX` |
| Variational scalar field | minimise fidelity to A and R·B + smoothness + topological persistence + grammar/semantic terms (level sets, PDE) | `LOG-QWEN`, `CAT-XLSX` |
| Differentiable SDF + dual classifier | `L = −log P(A|X) − log P(B|R X)` + topology/deformation/complexity regularisers; related to VecFontSDF and AmbiGen | `LOG-GPT1` §8, `RPT-META` §5 |
| Genetic algorithm / evolutionary | amateur precedent (note.com/eku GA kanji ambigram, per `RPT-RULES` sources) | `RPT-RULES` |
| Rotation-equivariant latent space | encode glyphs in manifold such that rotating G lands near H; decode midpoint | `LOG-QWEN` |
| Program synthesis | DSL of stroke operations (move, scale, curve, reconnect, permute, thickness); search minimum-complexity program T=O_k∘…∘O₁; cluster programs into family rules F_k | `LOG-GPT1` §9, `LOG-QWEN`, `CAT-XLSX` |
| Brush/calligraphic rendering | variable-pressure brush (paper's model; Expresii "Quarter Mode" suggested for 4-quadrant stroke rendering) | `PAPER`, `RPT-META` |

## 3. Evaluation methods proposed

* Independent OCR/CNN in both orientations (the paper's ETL8 recogniser proved unrelated to human readability — [paper summary](../methods/inoue-takahashi-2020.md); so use as a weak proxy only).
* **Blind human tests** (`LOG-MULTI` Gemini/Claude): tachistoscopic exposure; contextual sentences (high/low predictability); fixation latency; 100–200-pair calibration sample judged by the owner; with and without context.
* ε calibration experiments: "how much deformation before it stops being read?" (`META-DECK` slide 12).
* Composite distance with distinctiveness and style terms ([existence-criterion §6](../theory/existence-criterion.md)).

## 4. Roadmaps proposed (all unexecuted as plans)

| Roadmap | Steps (abridged) | Source |
|---|---|---|
| Consensus order (Claude, after GLM/DeepSeek rounds) | (0) freeze font (gothic) + IDS-15.1 data; (1) stroke-R table by font regime; (2) IDS rewrite with total duals and native ⿾⿿; (3) exact pairs on Jōyō; (4) bounded-deformation score + edit script; (5) lexical filter; (6) human calibration | `LOG-MULTI` |
| GPT 9-stage protocol (stages 0–8) | operationalise phenomenon → representation (KanjiVG-first) → natural transformations → families → mechanisms → induce laws (program synthesis) → validate generalisation/perception → explanatory model → generative algorithms; feedback loops; later "audit & reproduce experiments before new laws" | `LOG-GPT1`/`LOG-GPT2` |
| Qwen 10 phases | formalisation; corpus & indices; natural pairs; reproduce I–T; Nomura constraints; functional/variational; family specialisation; human+computational+semantic validation; rule discovery; final product (assisted generator, validated-ambigram bank, extension to words/ideas) | `LOG-QWEN` |
| Meta 4-phase pipeline | OT mining + IDS filter → SDF morph with saliency weights → OCR/human validation → calligraphic refinement | `RPT-META` §7 |
| `META-DECK` next steps | rotation graph catalogue (2–4 weeks, "high return") → replicate I–T on kanji → Nomura corpus coding (#アンビグラム as (pair, correspondence, widths)) → calibrate ε → dual-reading generator | `META-DECK` slide 12 |
| GPT's final recommendation (`LOG-GPT2`) | consolidate GPT/Kimi results under one protocol; run the full Jōyō inventory with corrected structural metrics keeping four evaluations separate (raster, vector skeleton, IDS algebra, distinctiveness); keep controls 甲/由, 土/士, 未/末 **without presuming** they are valid; then induce family rules and test on unseen characters | `LOG-GPT2` |

## 5. Data/tool needs identified

KanjiVG (all sources), CHISE or UCD IDS, Jōyō+Jinmeiyō lists, JMdict/CC-CEDICT, a calibrated recogniser or human panel, a vector rendering path to SVG. Details and what was actually used: data-sources-and-tools (source reference in repo2: `../methodology/data-sources-and-tools.md`). What the final tool needs: tool-requirements-and-status (source reference in repo2: `../project/tool-status-and-roadmap.md`).

## Related

- [Existence criterion](../theory/existence-criterion.md)
- Tool status and roadmap (source reference in repo2: `../project/tool-status-and-roadmap.md`)
- EXP-08 — MiniMax rotation graph (source reference in repo2: `../experiments/exp-08-minimax-rotation-graph.md`)
- exp-05 (source reference in repo2: `../experiments/exp-05-mistral-medians-graph.md`)
