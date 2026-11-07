# License audit

This document records the licence of every data source the project uses or
intends to use, the obligations each one carries, and where the material may
appear. It exists so that a licence question is answered before data is
ingested, not after.

**Nothing here is legal advice.** It is a record of what upstream states about
its own licensing, with the source link for each claim. Where a licence is
unclear or a source's terms have not been read in full, the row says
**verify before use** and the material must not ship until it is resolved.

## Rule: no silent mixing

> Any artifact that combines data from two sources with different licences must
> carry a **per-item provenance field** identifying the source of every row.
> A combined artifact inherits the *most restrictive* obligation of its parts.

This is the rule that follows from the table below. It is not optional and it
does not have exceptions for "small" amounts of data.

## Sources in use today

| Source | Licence | Obligations | Where it appears |
|---|---|---|---|
| **KanjiVG** — canonical Japanese stroke centrelines | **CC BY-SA 3.0** | Attribution to Ulrich Apel and contributors; **share-alike** on derivative vector data | `data/` (derived measurements), `generator/index.html` and `demo/index.html` (embedded stroke paths), `assets/*.png` (screenshots of KanjiVG-derived output) |
| **Original project code and prose** | **MIT** | Copyright notice and licence text retained | `code/`, `theory/`, `methods/`, `findings/`, `docs/`, `data/*.csv` (measurements), `LICENSE` |

The split between MIT and CC BY-SA 3.0 is documented in [`NOTICE.md`](NOTICE.md).
The MIT licence does not override the share-alike obligation on KanjiVG-derived
graphical data.

## Sources under evaluation

The source assets themselves are **not bundled**. The PRC ingestion and construction tools, and some archived numerical outputs, are staged in draft branches. The following third-party sources are listed because the expansion
to Chinese characters depends on them, and because their terms differ in ways
that constrain what may be combined with what.

| Source | Licence | Status | Constraint |
|---|---|---|---|
| **Make Me a Hanzi** — `graphics.txt` (stroke paths and medians, derived from the Arphic PL KaitiM GB and Arphic PL UKai fonts) | **Arphic Public License (APL)** | Text verified; scope of each derived numeric dataset requires review | APL is **not merely an attribution-only permissive licence**. It requires retaining the unaltered licence when distributing the Font, and for modifications to the Font it requires prominent notices of changes and making modifications freely available under APL. See [`licenses/ARPHICPL.TXT`](licenses/ARPHICPL.TXT), §§1–2. Source or modified glyph assets must not be relabelled as MIT. |
| **Make Me a Hanzi** — `dictionary.txt` (decompositions, etymology, definitions; derived from Unihan and CJKlib) | **GNU LGPL v3 or later** | Verified | Copyleft. Permits use and redistribution with attribution; derivative works of the *data file* remain under LGPL. |
| **Make Me a Hanzi** — `svgs.tar.gz` | **Arphic Public License** | Verified | Same terms as `graphics.txt`. |
| **animCJK** — files prefixed `graphics*`, and the kanji/hanzi SVG sets | **Arphic Public License** | Verified | Same redistribution terms. |
| **animCJK** — all other files (dictionaries, code, CSS) | **GNU LGPL** | Verified | Copyleft. |
| **animCJK** — SVG files for kana, bopomofo and single strokes | **Arphic Public License or, at the user's option, LGPL** | Verified | Optional: the upstream licence text offers the LGPL alternative for these files. State which one is used. |
| **CHISE-IDS** — Ideographic Description Sequences | **GNU GPL v2** | Verified for the package | **Strong copyleft and the most restrictive item in this table.** Upstream also states that some `IDS-UCS*` data is derived and expanded from the CDP database by C.C. Hsieh and colleagues at Academia Sinica — **the provenance of that subset must be checked separately before use.** |
| **Unihan Database** | Unicode Copyright and Permission Notice | Verified | Permissive; the notice must accompany redistributed data. |
| **Klee One**, **Yuji Syuku** (Fontworks) | **SIL Open Font License 1.1** | Verify per-file before embedding | OFL requires the licence text and reserved font names to travel with the font. Display-only use does not make the font a metric source. |
| **Hina Mincho** (Satsuyako) | **verify before use** | Not verified | Do not embed until the exact licence text is read and recorded here. |

Sources for the licence statements above:

- Make Me a Hanzi licence split — <https://github.com/skishore/makemeahanzi/blob/master/COPYING>
- Make Me a Hanzi sources — <https://github.com/skishore/makemeahanzi#sources>
- animCJK licence summary — <https://github.com/parsimonhi/animCJK#licenses>
- CHISE-IDS licence — <https://github.com/chise/ids/blob/main/README.md#license>
- KanjiVG — <https://kanjivg.tagaini.net/>

## Derived rule for combined artifacts

When a dataset combines, for example, KanjiVG-derived measurements (CC BY-SA
3.0) with Make Me a Hanzi graphics (Arphic Public License), the combined
artifact must:

1. carry a `source` column identifying the provenance of each row;
2. state both licences in its own documentation and in [`NOTICE.md`](NOTICE.md);
3. ship the required licence texts;
4. and, if the combined artifact includes CC BY-SA 3.0-derived material in a
   share-alike-covered form, be released under terms compatible with
   CC BY-SA 3.0 for that portion.

A dataset that mixes an Arphic Public License graphic with a GPL-2.0 dataset
must **not** be distributed as a single file without per-item provenance: a
consumer could not tell which terms apply to which row. Split them, or record
the provenance per row.

## Deliberately not used

| Source | Reason |
|---|---|
| Issei Nomura's published artwork | Inspired the project; no artwork is redistributed. The artist did not author, review or endorse this repository. |
| Commercial font outlines as a metric source | Font outlines measure the font, not the character. Display-only fonts may be embedded under their own terms, as above. |
| The paper by Inoue and Takahashi (2020) | Cited, not redistributed. Its method is described from the full text; the implementation here is not claimed as theirs. |

## Review checklist before adding a source

- [ ] The upstream licence text has been read in full, not inferred from a
      third-party summary.
- [ ] Redistribution of the specific artefact is permitted.
- [ ] Any modification requirement (share-alike, attribution, naming) is
      recorded above and implemented in the ingesting code.
- [ ] The provenance field is added to the output schema.
- [ ] The licence text ships with the data.
- [ ] The row above is updated with the source link.
- [ ] If any of the above is uncertain, the source is not ingested.

## Related

- [`NOTICE.md`](NOTICE.md) — attribution for what is already shipped
- [`LICENSE`](LICENSE) — MIT licence for original code and prose
- [`SCOPE.md`](SCOPE.md) — what the project covers and what it does not
## PRC geometry obligations reviewed on 2026-11-07

The exact [Arphic Public License](licenses/ARPHICPL.TXT) from the pinned MMah upstream commit was inspected. Sections 1–2 require an unaltered licence file with distributed font material, and for modified fonts require prominent notices of what changed and when, as well as offering those modifications under the same licence. This goes beyond attribution alone. Whether a particular statistical CSV of geometric measurements constitutes a protected adaptation is a fact- and jurisdiction-dependent question; **do not assert it is automatically MIT**. Keep raw/modified MMah outlines, median coordinate lists and renderings outside the public MIT core until that classification and the corresponding notices are verified. Code that implements algorithms without copying source-derived glyph data remains independently MIT where authorship permits. No legal conclusion is asserted here.
