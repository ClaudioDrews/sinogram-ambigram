# Research-track audit and method inventory

**Audit date:** 2026-11-08 · **Source:** `main` at `77ec5e7`, PRs #13–#17, #19, #21, #26–#27 and live GitHub Pages.  
**Purpose:** Make tested methods discoverable without conflating ranking, construction and recognition. [Interactive map](index.html) · [Project overview](../README.md).

## Definitions

- **Natural self-rotation / C₂ candidate:** rotate an unmodified source glyph by 180°; the claimed second reading has not been demonstrated.
- **Natural A↔B candidate:** a source glyph A, with R(A) geometrically close to B; screening is not synthesis.
- **Constructed geometry:** an algorithm emits a single modified or combined drawing from one or more source glyphs.
- **Experimental failure / no-op:** a measured implementation with no demonstrated image improvement or changed output. These outputs still belong in the research record.
- **Recognition:** the published Reader Gallery collects voluntary, unverified three-choice impressions. The draft blind VLM study is not a human-reader study.

A **method has a demonstrated visual output** only when the example is attributed to the code path that actually generated that output. A conceptual field diagram and an unmodified glyph are not interchangeable with an operator-generated output.

## Japanese KanjiVG — computational screening

| Tested run / method | Code/evidence | In main? | Public demo / example | Boundary |
| --- | --- | --- | --- | --- |
| GPT raster IoU | [Metric definitions](metrics-comparison.md) | Historic report | [Research methods](index.html); [results](../findings/results-summary.md) | Comparison, **not** an output SVG constructor |
| GLM translated raster IoU | [Metric definitions](metrics-comparison.md) | Historic report | [Research methods](index.html) | Translation policy changes rankings |
| Claude v1 skeleton F-score | [Metric definitions](metrics-comparison.md) | Historic report | [Research methods](index.html) | Tolerance score, not a reading |
| Claude v2 W1 + warp + structure | [Metric definitions](metrics-comparison.md) | Historic report | [Research methods](index.html) | Pre-filter can exclude viable glyphs |
| Kimi FFT + IoU | [Measured summaries](../findings/results-summary.md) | Historic report | [C₂ visual lab](../demo/c2/) (related geometry, **not** a replay of Kimi's algorithm) | Font-sensitive |
| Mistral median point-cloud | [Metric definitions](metrics-comparison.md) | Historic report | [Research methods](index.html) | Different source/normalisation |
| MiniMax KanjiVG graph (Hausdorff, Chamfer, RMS, dilated IoU) | [Implemented pipeline](rotgraph-method.md) | **Yes** | [Generator](../generator/), [C₂](../demo/c2/), [candidate CSV](../data/rotation_pairs.csv) | Fixed scale/centre; biased ranking |

**Important count:** Seven computational **variants**, drawn from **six code-producing runs**, not seven different ambigram renderers. Historic GPT/GLM/Claude/Kimi/Mistral outputs cannot be relabelled as outputs of the current KanjiVG generator.

## Japanese KanjiVG — source views and constructions

| Type / operation | Code/evidence | In main? | Visual availability | Critical label |
| --- | --- | --- | --- | --- |
| Natural self-rotation (A↔A / C₂) | [C₂ data](../data/c2_class.csv), [C₂ Lab](../demo/c2/) | **Yes** | [C₂ Lab](../demo/c2/); source-glyph examples in [Reader Gallery](../evaluation/recognition/) | Unmodified Japanese KanjiVG glyph; unverified reading |
| Natural distinct-character A↔B candidate | [Pair CSV](../data/rotation_pairs.csv), [pair matrix](../findings/pair-evidence-matrix.md) | **Yes** | [Generator](../generator/); source-only item in [Reader Gallery](../evaluation/recognition/) | Source A only; B is a geometric prediction |
| Overlay | [Generator method](../generator/README.md) | **Yes** | [Generator](../generator/) · [Reader Gallery](../evaluation/recognition/) | Diagnostic overlay, not a fused validated glyph |
| Stroke salience | [Generator method](../generator/README.md), [Python prototype](../code/make_ambigram.py) | **Yes** | [Generator](../generator/) · [48-item pilot](../evaluation/items.json) | Salience operation; `v1-top`/`v2-top` are selection strata |
| Shared structure | [Generator method](../generator/README.md) | **Yes** | [Generator](../generator/) · [Reader Gallery](../evaluation/recognition/) | May discard distinctive strokes; diagnostic, not an ambigram success |
| C₂ source + symmetric rendering | [Generator](../generator/README.md), [C₂ Lab](../demo/c2/) | **Yes** | [Generator](../generator/) · [C₂ Lab](../demo/c2/) | The algebraic even field is not necessarily a legible glyph |

## Chinese GB2312 / Make Me a Hanzi

| Tested method / category | Code / findings | In main? | Public visual example | Evidence status |
| --- | --- | --- | --- | --- |
| Natural self-rotation screening | [Coarse search](PRC_COARSE_SEARCH.md), [extremity findings](../findings/prc-extremity-analysis.md) | **Yes** | [PRC Explorer](../prc/) and [Reader Gallery](../evaluation/recognition/) | Coarse geometric candidate |
| Natural distinct A↔B screening | [Coarse search](PRC_COARSE_SEARCH.md), [catalogue](../prc/catalog.json) | **Yes** | [PRC Explorer](../prc/) and [Reader Gallery](../evaluation/recognition/) | 106,347 shortlisted pairs; not human-validated |
| Source-vector union | [PRC Explorer](../prc/README.md) | **Yes** (browser) | [PRC Explorer](../prc/), [Reader Gallery](../evaluation/recognition/) | Unmodified A + rotated B, not a refined constructor |
| Rotation-centre optimization | [Construction theory](../theory/prc-construction-method.md), [code](../code/prc_construct.py) | **Yes** (research code) | [C₂ Lab](../demo/c2/) demonstrates centre parameter; **not an emitted PRC optimization result** | Candidate geometric optimization |
| Extremity / terminal reconciliation | [Theory](../theory/prc-construction-method.md), [code](../code/prc_construct.py) | **Yes** (research code) | See [reproduction instructions](../theory/prc-construction-method.md); **no audited gallery SVG** | Experimental operator |
| Sector thickness — deterministic | [Theory](../theory/prc-construction-method.md), [code](../code/prc_construct.py) | **Yes** (research code) | No audited public method-specific SVG in the Reader Gallery | Experimental operator |
| Sector thickness — constrained search | [Theory](../theory/prc-construction-method.md), [code](../code/prc_construct.py) | **Yes** (research code) | No audited public method-specific SVG in the Reader Gallery | Experimental operator |
| Width semantics v2 | [PR #19](https://github.com/ClaudioDrews/sinogram-ambigram/pull/19), [fidelity study](../findings/prc-width-contour-fidelity.md) | **Yes** | [C₂ Lab](../demo/c2/) illustrative bands + measured stats | **32/32 contour-fidelity improvement, not reading** |
| R-ODD local compensation | [PR #14](https://github.com/ClaudioDrews/sinogram-ambigram/pull/14) | **No — draft** | [PR #14 reproducible preview workflow](https://github.com/ClaudioDrews/sinogram-ambigram/pull/14); [C₂ Lab](../demo/c2/) is concept-only | No controlled reader evidence |
| Harmonic C₂-even thickness | [PR #15](https://github.com/ClaudioDrews/sinogram-ambigram/pull/15) | **No — draft** | [PR #15 reproducible preview workflow](https://github.com/ClaudioDrews/sinogram-ambigram/pull/15); [C₂ Lab](../demo/c2/) is concept-only | No controlled reader evidence |
| Registered A/B fusion | [PR #16](https://github.com/ClaudioDrews/sinogram-ambigram/pull/16), [null diagnosis](../findings/prc-ab-fusion-null-diagnosis.md) | **No — draft** | [C₂ Lab no-op visualization](../demo/c2/), [threshold study PR #21](https://github.com/ClaudioDrews/sinogram-ambigram/pull/21) | 0/32 changed final rasters in later threshold study |

**Important:** the original draft thickness correction [PR #13](https://github.com/ClaudioDrews/sinogram-ambigram/pull/13) was not merged directly. [PR #19](https://github.com/ClaudioDrews/sinogram-ambigram/pull/19) safely introduced the corrected geometry while preserving historical v1.16 replay. Do not combine these numerical scales.

## Public-site and gallery audit

| Page | Track | What it actually shows | Gap / fix |
| --- | --- | --- | --- |
| [Home](../index.html) | Both | Links to major tools | Add independent research-track and Methods navigation |
| [Japanese Generator](../generator/) | JP/KanjiVG | Candidate ranking + four rendering modes | Explain input-language selector does not change glyph source |
| [Rotation Lab](../demo/) | JP/KanjiVG | Sixteen experiments | Better discoverability via Methods |
| [C₂ Lab](../demo/c2/) | JP and PRC research | Exact C₂ decomposition, measured PRC width and A/B no-op, field *concepts* | Do not pretend diagrams are algorithm output |
| [PRC Explorer](../prc/) | CN/MMah | Coarse ranked candidates and original-source overlay | No integrated multi-operator renderer yet |
| [Reader Gallery](../evaluation/recognition/) | Separate JP and CN | Simple per-language meaning-choice review | Retain UI; use identifiable actual method provenance |
| [48-item pilot](../evaluation/index.html) | JP/KanjiVG | Different larger-sample protocol | **Do not edit** its 48 original items to change the simple gallery |

**Remaining research gap, not something to disguise in a user interface:** some draft PRC operators have no audited, redistributable method-specific images on `main`. Producing those requires running the exact branch algorithm on pinned licensed source geometry, provenance/hashes and licensing review; a source glyph or conceptual field cannot be passed off as the algorithm's output. Such experiments remain discoverable through direct PR/reproduction links. The Reader Gallery must not silently invent missing successful constructions.

## Evidence and licensing rules

1. Geometric score ≠ human legibility. A self-rotation or pair candidate is not automatically a successful ambigram.
2. No controlled, independent native-reader validation exists. [Draft VLM pilot #17](https://github.com/ClaudioDrews/sinogram-ambigram/pull/17) includes 52 images/208 model readings but is not a human study.
3. The original Japanese Generator is Japanese KanjiVG even if its UI input language reads “Chinese”; PRC GB2312 uses MMah. Source licences differ: KanjiVG CC BY-SA 3.0; MMah-derived outlines Arphic Public License.
4. The Reader Gallery is exploratory, includes diagnostic negatives, and its method labels identify the *actual drawing process*. Never pool methods/tracks or interpret its unadjudicated selections as measured recognition rates.
5. [Full limitations](../findings/limitations.md), [source boundary](../SCOPE.md), [licence audit](../LICENSE-AUDIT.md).

## Future stimulus quality gate

Before admitting a draft-only operator to the Reader Gallery: (a) pin the source and branch commit; (b) run its actual implementation; (c) preserve image hash, pair, centre/parameters and operator; (d) verify it is not a duplicate/no-op of another arm; (e) review visual quality and redistribution terms; (f) label failures as failures; (g) ensure that the exported data records exact method/provenance. This gate is **not** a requirement that all images look good, only that every label is true.
