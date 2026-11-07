# PRC regional inventories and variant consistency

**Status:** the GB2312 codepoint inventory is generated reproducibly. A
verified, distributable copy of the official 2013 通用规范汉字表 is **not bundled**.
A per-glyph source-form comparison against a normative PRC standard is also
pending; these are not interchangeable acceptance criteria.

## Why separate regional inventories?

A Unicode codepoint alone does not fully determine stroke order or regional
glyph design. Japanese KanjiVG and Chinese Make Me a Hanzi source shapes must
never enter the same nearest-neighbour ranking without explicit regional
control. Make Me a Hanzi itself contains simplified **and** traditional forms.
A repertoire is a membership list; it does **not** certify that every glyph
outline in an external source matches the intended printed standard.

## Supported presets

| ID | Standard / rule | Count | State |
| --- | --- | ---: | --- |
| `cn-s-gb2312` | Decode two-byte GB2312 with Python's standard codec; retain unified ideographs | 6,763 | Generated, source coverage checked |
| `cn-s-tcc-l1` | 2013 table indices 0001–3500 | 3,500 | Requires verified external transcription |
| `cn-s-tcc-l2` | 2013 table indices 3501–6500 | 3,000 | Requires verified external transcription |
| `cn-s-tcc-l3` | 2013 table indices 6501–8105 | 1,605 | Requires verified external transcription |
| `cn-s-tcc-all` | Union of the three 2013 levels | 8,105 | Requires verified external transcription |

See [`code/stage13_prc_presets.py`](../code/stage13_prc_presets.py) and
[`code/prc_inventory.py`](../code/prc_inventory.py). An external
2013 table is accepted only as **8,105 uniquely indexed codepoints**. Passing
this syntax check does not establish official provenance or redistribution
rights. Record its original publication and hash before releasing derived
inventory lists.

## Reproduction

~~~bash
bash scripts/download_prc_sources.sh
python code/stage13_prc_presets.py \
  --graphics data/prc/graphics.txt \
  --out data/prc/inventories

# Only with an independently verified, permitted local transcription:
python code/stage13_prc_presets.py \
  --graphics data/prc/graphics.txt --tcc /verified/tcc-2013.txt \
  --out data/prc/inventories
~~~

Generated files are intentionally excluded from Git history until the
source-specific release/licence review is complete:

- `manifest.json`: source hash, corpus size, supported presets, inventory
  sizes, measured source coverage, missing count, canonical member digest,
  region and `regional_form_certified=false`.
- `<preset>.txt`: covered member characters, sorted by codepoint (one per line).
- `<preset>-missing.txt`: codepoints absent from the pinned source.

A variant-specific ranking must match the manifest's **exact**
`graphics_sha256`, use only its covered member characters, carry its
preset identifier and source field in every derived record, and never import
the Japanese (`jp`) index. Mixed-inventory inputs must be rejected
rather than silently pooled. `regional_form_certified=false` must remain
visible until a separate authoritative glyph-form audit is complete.

## Evidence boundaries

This is a **membership and availability** audit, not a finding of ambigram
legibility, and not a guarantee that a particular MMah glyph is a certified
Mainland simplified printed form. No source glyph contours or medians are
redistributed here, and no PRC full-pair ranking has been produced. The
separately archived filled-ink construction scores must not be conflated
with the median-skeleton representation.
