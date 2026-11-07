# PRC v1.16 archived measurements (derived summaries)

These small, auditable tables were computed from the **v1.16 research archive** supplied in the project's Drive `new/` folder. They are **not** a new rerun of the original PRC experiment, and they are not human reading judgments. The raw Make Me a Hanzi geometry is not redistributed here.

Run against an independently obtained, unmodified extraction of `sinogram-prc-construction-v1.16.tar.gz`:

```bash
python tools/verify_prc_archive.py /path/to/sinogram-prc-construction-v1.16/results \
  --out data/prc/archive-v1.16
```

The verifier asserts input sample sizes and sector-edit constraints, writes two UTF-8 CSVs and a JSON digest/summary. Compare the generated files against this directory. The JSON summary stores SHA-256 hashes of the **three exact archived JSON input files**.

- `prc-centre-extremity-120.csv`: measured baseline, optimized centre, extremity-only and final geometric overlap for 120 candidates.
- `prc-sector-generalisation-53.csv`: 53 tested candidates, before/after overlap, retention, growth, constraints.
- `prc-archive-summary.json`: input hashes and aggregates, including **mean** and **median** centre improvement as separate statistics.

### Metric clarification

For the 120-source-item dataset, the **mean** `centre_only - box` is approximately **+0.0925**, while the **median paired gain** is approximately **+0.0692**. Do **not** label +0.093 as a median improvement. The 53-item sector experiment has median paired gain about **+0.0229**, mean paired gain about **+0.0300** and 52/53 improved. The baseline and edited *sample medians* are respectively about 0.2404 and 0.2661; the difference of medians is not identical to the median paired gain.

### Research boundary

These are archived geometric measurements only. They do not establish character legibility, translational generalization to another font, or statistical independence of selected candidates. The `cn-s` geometry and the Japanese `jp` rotation ranking must remain separate. The full original research archive, including results and experimental code, is required for deeper provenance review and source-level replication.
