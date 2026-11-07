# Blind VLM recognition protocol — Pilot 01

## Identification and fixed design
Date of main run: **2026-11-07**. A fixed randomized order of 52 trial IDs was used. All four model families saw one image per isolated inference request, with no previous stimuli, prior replies or answer key in the model prompt. A transport-level audit verified the request body and input-image checksums for all 208 scheduled trials.

## Exact prompt P1

> Identify the single Chinese character shown in this image. Return exactly one Unicode CJK character if you can recognize it, or UNKNOWN if you cannot. Do not explain, do not guess from filenames or metadata, and do not alter or rotate the image.

## Models and request constraints

| Provider model ID | Image input | Temperature | Output cap |
|---|---|---:|---:|
| `minimax/minimax-m3.1-flash` | Yes | 0 | 4096 |
| `deepseek/deepseek-v4.1-flash` | Yes | 0 | 4096 |
| `tencent/hy4` | Yes | 0 | 4096 |
| `z-ai/glm-5.3-flash` | Yes | 0 | 4096 |

Endpoint: OpenRouter-compatible chat completions. One independent image request per model/trial. Original 436×436 PNG transmitted unchanged as an image attachment; no filenames, trial codes, tool outputs, browsing, OCR tools or correct labels transmitted to the model. No answer repair or hindsight re-queries after freezing.

For DeepSeek and HY4 a reasoning-disabled field was transmitted; for MiniMax and GLM the adapter omitted this requested field, so reasoning is not proven disabled. Aliases may change without dated model snapshots. No seed/top-p was forced, and temperature 0 does not guarantee provider determinism.

## Raw parsing and missingness

The literal text content was concatenated in provider event order, then **only surrounding whitespace was stripped** for parsed output. Exactly one CJK unified or compatibility ideograph is `valid`; the literal `UNKNOWN` is `unknown`; otherwise `invalid`. Network failure is `error`. No Chinese variant normalization or guess-filling is allowed.

The public compact responses matrix preserves all 183 single-character raw outputs and one literal UNKNOWN. `data/finish_reasons.csv` separately records the per-trial stop, length-cap or transport-error outcome. There were 23 empty invalid responses and one empty transport error, represented by reserved status tokens `INVALID` and `ERROR`. For new model submissions use the full-schema CSV format supported by `scripts/score.py` to retain actual raw text and status separately.

Of 208 scheduled requests, 207 received HTTP 200 and one failed in transport. **23 responses ended at length cap**. These observations remain in the denominator for the primary accuracy endpoint.

## Deviations and operational audit

A preliminary small-output-cap trial was conducted and yielded no valid short answer. The cap was subsequently fixed uniformly at 4096 before the main collection. The first stimulus therefore had documented prior exposure to one model; the main session did not receive the preliminary output.

All model×trial main sessions were isolated. Internal attempts to retry after truncated outputs or transport faults were blocked before transmission; no completed main trial was repeated. Some initialization probes were stopped before transmission. These facts are methodological, not additional independent observations. Local provider runtime details, workstation paths and account identifiers are intentionally omitted as not needed to replicate the image-only protocol.

No claim is made about hidden OCR or preprocessing inside model providers. Provider-level request headers and complete HTTP traces are not published because they may carry private network/account metadata. The sanitized response matrix retains every observable text answer and error status.

## Primary outcome and units

For each **model×drawing**, both upright and rotated answers must exactly equal their corresponding expected Unicode characters. Two orientations of one drawing are paired, not two independent trials. Other arms with the same target are additionally dependent; model families may share training/recognition behavior. Report both counts and denominators and perform paired arm comparisons on identical targets/model combinations. Do not treat all 208 requests as independent estimates of an algorithm's success rate.

Secondary outcomes: per-orientation exact match; valid, unknown, invalid and error rates; model disagreement and image hash duplicates. Treat all invalid, unknown and error trials as incorrect in the intention-to-test primary analysis.

No human readership was sampled. This pilot cannot validate human legibility or population-level generalization.

## Reproducibility and source boundary

The historical original geometry is pinned at `a9ddfabbdfe32d781c816ffbd6c93fc194d12e30`; experimental PRs are #13 (thickness), #14 (R-ODD), #15 (harmonic), #16 (A/B fusion). The MMah source is SHA-256 pinned and under the Arphic Public License. Rebuild rendered images using experiment workflows, not by copying PNG bytes into the MIT project tree.

The public labeled mapping is intended **only after new models' outputs have been frozen**. A claimed independent blind trial must prove that target labels and results were not provided to the inference model. The released pilot is not a held-out dataset for subsequent optimization.
