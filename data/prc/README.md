# PRC geometry source (CN-S)

This directory holds **no bundled third-party glyphs**. To prepare the source:

```bash
bash scripts/download_prc_sources.sh
python code/prc_inventory.py --graphics data/prc/graphics.txt --out data/prc/coverage.json
```

The downloader retrieves the geometrical `graphics.txt` dataset from
[Make Me a Hanzi](https://github.com/skishore/makemeahanzi) and checks the
SHA-256 digest pinned in the script. The data include stroke outlines and
medians. They are **PRC-source glyphs**, not Japanese KanjiVG variants.

The dataset's Arphic Public License must be preserved and reviewed when
redistributing source-derived outlines. Do not silently treat all source data
as MIT solely because this repository's original code is MIT. The
`dictionary.txt` file is not downloaded and is outside this track.

The optional TCC (2013 通用规范汉字表) transcription is not included and
should not be ingested without provenance and reuse-rights verification.
The audit script rejects missing or duplicate TCC indices rather than
silently reporting misleading coverage.

Do not combine `jp` and `cn-s` measurements in the same ranking; do not
interpret geometric overlap as human readability. See
[the source audit](../../methods/PRC_SOURCE_AUDIT.md).

Generated source files and results belong in `data/prc/` locally and are
not required for the normal repository CI.
