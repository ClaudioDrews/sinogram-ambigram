# Pilot 01 — Blind VLM Reading of Rotational Sinograms

[简体中文](README.zh-CN.md) · [Results (English)](RESULTS.md) · [中文结果](RESULTS.zh-CN.md)

**Status:** exploratory, reproducible research pilot; **not evidence of human readability or an approved merge**.

## Scope

A blinded image-only pilot compared four vision-language-model families over **52 raster stimuli**, each shown in a separate request: 26 drawings × two orientations. Five self-rotating glyphs were evaluated in four geometric arms (historical main, thickness-corrected, R-ODD, harmonic), and two **distinct-character pairs** were evaluated in three arms (historical main, thickness-corrected union, A/B fusion). There were 208 scheduled model×image trials.

Methods differ in task: self-rotation and distinct-character fusion **must not be pooled into a single algorithm ranking**. The sample is a demonstration cohort, not randomly sampled or held out. It includes no human readers.

## Research artifacts

- [PROTOCOL.md](PROTOCOL.md): verbatim model prompt, trial isolation, parsing, known deviations, analysis rules.
- [RESULTS.md](RESULTS.md): scored descriptive findings and limitations.
- [data/responses_matrix.csv](data/responses_matrix.csv): the **exact short text returned** by the four models for each of 52 image IDs. The tokens `INVALID` and `ERROR` encode empty response/status, not literal model text. `UNKNOWN` was a literal response.
- [data/ground_truth.csv](data/ground_truth.csv): trial-to-arm/reference mapping and expected character; **do not disclose to test models**.
- [data/finish_reasons.csv](data/finish_reasons.csv): per-model completion metadata (`S` = stop, `L` = output cap, `E` = transport failure).
- [scripts/score.py](scripts/score.py): deterministic report/scoring, validation, paired comparisons; standard-library Python only.
- [scripts/rebuild_stimuli.py](scripts/rebuild_stimuli.py): rebuilds all 52 PNGs from pinned commits, verifies every SHA-256 and packages an unlabeled ZIP.
- [scripts/test_score.py](scripts/test_score.py): unit tests for pairing, parsing and non-independence safeguards.
- [LICENSE-NOTICE.md](LICENSE-NOTICE.md): source provenance and distribution boundary.

A trial-order file and 52 PNGs were distributed to the original evaluation runner. Their source is the pinned Make Me a Hanzi geometry snapshot, SHA-256
`a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.
The original no-label PNGs **are not committed**: source-derived renderings are kept in reproducible GitHub Actions artifacts while their redistribution terms are reviewed. The [benchmark reconstruction workflow](../../.github/workflows/vlm-stimuli-rebuild.yml) regenerates all 52 images, validates their checksums and uploads the answer-free `prc-vlm-blind-pilot-01` archive. Existing PRC workflows provide per-arm previews. See [PRC experiment instructions](../PRC_EXPERIMENTS_README.md).

## To evaluate your own vision models

1. Download the answer-free ZIP from the [benchmark reconstruction workflow](../../.github/workflows/vlm-stimuli-rebuild.yml), or rebuild locally with `python experiments/vlm-reading-pilot-01/scripts/rebuild_stimuli.py --graphics data/prc/graphics.txt --out /tmp/blind.zip` from the repository root; verify all image hashes.
2. Hide all manifests with labels, `ground_truth.csv`, this results document, model responses and method names from the inference agent.
3. Use the exact P1 prompt in [PROTOCOL.md](PROTOCOL.md) and one fresh image-only inference per trial; preserve raw output and error cases.
4. Save your model responses, then evaluate after the run is frozen with `python scripts/score.py --responses data/responses_matrix.csv --key data/ground_truth.csv`. See `--help` for CSV formats.
5. Report dual-orientation correctness by **model×drawing**, per-orientation correctness, individual changes relative to the corrected baseline, and missing/error rates. Keep held-out test cohorts independent of this published pilot.

**Important:** publicly available ground truth makes independent testing a procedural blind, not cryptographic blinding. Pre-register any future evaluation set and control model access to the solution file during inference. Avoid claiming model agreement proves correctness.

## Experimental controls and known issues

Models: `minimax/minimax-m3.1-flash`, `deepseek/deepseek-v4.1-flash`, `tencent/hy4`, `z-ai/glm-5.3-flash`. Each of 52 images was submitted once per model in the main study. The input was a 436×436 PNG without metadata in the prompt. Temperature 0, output cap 4096 tokens. Exact identifiers are provider aliases, not frozen snapshots.

There were **207 HTTP 200 responses**, **one transport error**, and **23 outputs with finish_reason=length**. Invalid, UNKNOWN and errors count as incorrect in the primary intention-to-test scoring. A preliminary low-token-cap test preceded the uniform main run; it is disclosed in the protocol rather than concealed.

**Do not promote** any experimental branch from this pilot. The paired A/B fusion produced byte-identical images to the thickness-fixed union for both tested pairs; zero correct readings in either orientation across all pair arms/models. The self-glyph improvements are descriptive and small-sample.

## Language policy

Research prose is maintained here in English and Simplified Chinese. The broader project supports English, Chinese and Japanese; a Japanese translation can be added as a separate localized document. No Portuguese text or private agent nicknames belong in the public benchmark.

Original code and documentation follow the repository's MIT licensing; this does **not** relicense the upstream Arphic glyph data.
