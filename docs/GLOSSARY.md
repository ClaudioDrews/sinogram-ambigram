# Glossary

Terms that appear in this repository's documentation, in English, with a
citable source for each. The entries describe how a term is used *here* and
give its documented meaning; they are not essays on the concept and they make
no claim that a term belongs to a whole culture, a whole practice or a whole
people.

Where a term has no settled English equivalent, the source's own wording is
kept rather than forced into a single-word translation.

---

## Hanzi and kanji

**Hanzi** (漢字) is the usual English-language term for Chinese characters, the
writing system used for Chinese as well as for Japanese and Korean. **Kanji**
(漢字, literally "Han characters") is the Japanese term for the subset of
Chinese characters used in Japanese writing. The two words are not competing
names for different things: they are the same characters, named from the two
languages that use them.

For this repository the distinction is practical rather than cultural. The
measured inventory is the **Japanese** one, and every glyph shape comes from
KanjiVG, which records Japanese canonical forms. A Chinese reader looking at a
result in this repository is looking at a *Japanese rendering* of the
character. Simplified and traditional Chinese forms are different shapes and
are not measured here. See [`SCOPE.md`](../SCOPE.md).

*Sources:* Unicode Standard Annex #38 (Han Database), which distinguishes
"Chinese/Japanese ideographs"; and the Japanese Agency for Cultural Affairs
listing of the Jōyō kanji.

---

## Jōyō kanji and Jinmeiyō kanji

The **Jōyō kanji** (常用漢字, "characters for common use") is the official list
of 2,136 kanji designated by the Japanese Ministry of Education for everyday
use in Japan. The **Jinmeiyō kanji** (人名用漢字, "characters usable in personal
names") is the additional list of 634 character *types* (字種, allowing 652
written *forms*) permitted in Japanese personal names.

This repository's inventory of **2,770 glyphs** is the union of both lists,
extracted from the Japanese Wikipedia tables and frozen in
[`data/lists.json`](../data/lists.json). The distinction between 字種 and
字体 matters for counting: the often-quoted "863 Jinmeiyō" counts *forms*,
not *types*.

*Sources:* Japanese Wikipedia, 常用漢字一覧 and 人名用漢字, which are the
extraction source recorded in the reproduction protocol.

---

## Rotational ambigram

An **ambigram** is a design that reads as more than one word or text depending
on how it is viewed — most commonly by rotation, but also by reflection or by
rearranging parts. A **rotational ambigram** is one whose alternate reading
appears after a turn, typically a half-turn.

This repository uses the term for the *research question*: a single drawing
that is read as character **A** upright and character **B** after a 180°
rotation. A rotation by 180° is the map `R(x, y) = (−x, −y)` in centred
coordinates — an involution, not a mirror. A pair that resembles itself under
reflection is a **mirror pair** and is explicitly *not* a rotational ambigram.

Throughout the repository, "ambigram" is used in this aspirational sense. What
the code actually produces is a **candidate**: a drawing whose strokes align
well after a half-turn. Whether a candidate is *readable* has not been tested
with human readers, and no result in this repository should be described as a
validated ambigram.

*Sources:* the formal treatment in [`theory/existence-criterion.md`](../theory/existence-criterion.md)
and [`theory/ids-rotation-algebra.md`](../theory/ids-rotation-algebra.md).

---

## C₂ symmetry

A drawing is **C₂-symmetric** if a half-turn about its centre maps it onto
itself. The subscript refers to the cyclic group of order two, whose only
non-identity element is the half-turn.

This is the relevant notion for a *self*-ambigram: a character that looks the
same upside down does not need two different readings, so the task reduces to
finding characters whose canonical shape is already half-turn invariant.
Measured on KanjiVG vectors, the most C₂-like glyphs in this repository's
inventory are 目, 日, 一, 田, 口 and 回 — the ones whose structure is a frame
with a symmetric interior. The measured list is in
[`findings/results-summary.md`](../findings/results-summary.md); the geometric
definition of the self-rotation class is in
[`theory/family-rules.md`](../theory/family-rules.md).

*Source:* the mathematics of the half-turn is developed in
[`theory/existence-criterion.md`](../theory/existence-criterion.md).

---

## IDS (Ideographic Description Sequence)

An **IDS** is a compact notation for describing the structure of a Han
character, using the operators of the Unicode Ideographic Description
Characters block (U+2FF0–U+2FFF). A sequence such as ⿱亼3叩5 describes a
character as a top component over a bottom component, with the digits
counting the strokes of the remaining components.

The notation is data, not a rendering. IDS equality does **not** imply visual
equality: stroke types, slot sizes and font conventions decide the rest. Two
characters with the same IDS can look visibly different, and two characters
that look nearly identical can have different IDS.

*Sources:* the CHISE-IDS package documentation, and Unicode Standard Annex #38
for the operator repertoire. The rotation algebra over IDS operators is
developed in [`theory/ids-rotation-algebra.md`](../theory/ids-rotation-algebra.md).

---

## Ma (間)

**Ma** is a Japanese term written 間, read *ma* in its aesthetic sense. It
denotes an interval, gap or pause that is meaningful in itself rather than
merely the absence of something — the space that gives shape to what surrounds
it, and the pause that carries the rhythm of what comes before and after.

The character is used across spatial and temporal senses at once: *ma* denotes
the distance between two points, the extent of a time interval, and, in
aesthetic discussion, the deliberate emptiness that structures a composition.
Japanese aesthetics routinely evaluates the *ma* of a work — whether the
interval is well judged (`ma ga umai`) or badly (`ma ga warui`) — and in
calligraphy the unpainted paper around the strokes is part of the character
rather than its background.

This term is relevant here because a stroke-weight blend that makes shared
strokes bold and distinguishing strokes thin is, in effect, a decision about
which ink is *content* and which is *interval*. The term is offered as a
lens, not as a claim that the project's output embodies it.

*Sources:* the chapter "Emptiness, Nothingness and the Interval in Between"
in *Aesthetics and Heritage* (Springer); and the essay "MA: Place, Space,
Void" in *Kyoto Journal*, which traces the character's spatial and temporal
usages through compound words.

---

## Shodō (書道)

**Shodō** is Japanese calligraphy: the practice of writing characters with a
brush, valued as an expressive art as well as a writing system. It was
inscribed on UNESCO's Representative List of the Intangible Cultural Heritage
of Humanity in 2025.

Shodō is the reference point for the aesthetic criticism of this project's
output. A geometric stroke-blend derived from vector centrelines is a
*drawing*, not calligraphy: it has uniform width, no brush pressure, no
modulation of stroke ends, and no ink behaviour. That difference is the
substance of the objection that the output is "mechanical", and it is the
reason a calligraphic rendering is a separate, later stage of work rather
than a parameter that could simply be switched on.

*Sources:* UNESCO Intangible Cultural Heritage list entry for "Shodo,
Japanese calligraphy"; the Japanese Agency for Cultural Affairs nomination.

---

## Wabi-sabi (侘寂)

**Wabi** and **sabi** are aesthetic terms that are frequently paired. Britannica
describes them as "the twin ideals of cultivated simplicity and poverty
(*wabi*) and of the celebration of that which is old and faded (*sabi*)",
underpinned by an awareness of the transience of things. The pairing
*wabi-sabi* as a single term is a comparatively recent usage; the words have
separate histories, and *wabi* itself shifted meaning over time — Sen Rikyū's
tea aesthetics fixed it as deliberate simplicity in daily living, while *sabi*
retains its sense of age and patina.

The relevance here is narrow but real: a project that produced a polished,
uniform, mechanically symmetric drawing would be at odds with an aesthetic
that treats irregularity and age as sources of value. It is recorded to make
the project's own aesthetic position explicit — this repository does not
claim to produce wabi-sabi, and does not set out to.

*Sources:* Britannica, "Japan — Cultural life, Aesthetics" and "wabi";
Leonard Koren's *Wabi-Sabi for Artists, Designers, Poets & Philosophers*
(1994), as characterised in the Portland Japanese Garden's essay on the
term's history.

---

## Kotodama (言霊)

**Kotodama** (also written kototama) refers to the belief that spiritual
power is contained in words and names, and that the intonation of a word can
manifest that power. The *Encyclopedia of Shinto* describes it as an aspect of
animism, and notes its importance in waka poetry — where it is traditional to
say that words "move heaven and earth" — as well as among National Learning
(*kokugaku*) and Shinto scholars. The same entry records a scholarly view
that the belief attached originally to spells and incantations and took its
wider form during the compilation of the *Man'yōshū*.

Kotodama is listed here because the project's subject — a drawing that means
two different characters depending on how it is turned — sits close to a
tradition of reading significance out of the turning of a written form. The
entry is a record of that tradition, not a claim that a geometric candidate
carries any of this significance, and not a claim that the project speaks to
it.

*Source:* the *Encyclopedia of Shinto* (Kokugakuin University), entry
"Kotodama", by Teruyoshi Yonei.

---

## Terms used technically in this repository

| Term | Meaning here | Reference |
|---|---|---|
| **Sinogram** | The project's name; refers broadly to characters of Chinese origin. Does **not** imply Chinese-language coverage. | [`SCOPE.md`](../SCOPE.md) |
| **Half-turn** | The 180° rotation `R(x, y) = (−x, −y)`; an involution, not a mirror | [`theory/existence-criterion.md`](../theory/existence-criterion.md) |
| **Candidate** | A pair or drawing that satisfies a geometric criterion. Never a validated ambigram. | [`findings/limitations.md`](../findings/limitations.md) |
| **Legibility set** | The formal object standing for "the shapes a reader accepts as character *c*"; its intersection under rotation is the rigorous existence condition | [`theory/existence-criterion.md`](../theory/existence-criterion.md) |
| **ε (epsilon)** | The perceptual tolerance of a reader for a character. **Never measured** in this project. | [`theory/existence-criterion.md`](../theory/existence-criterion.md) |
| **Exact vs grid distance** | Two different scales of the same quantity; not interchangeable | [`data/README.md`](../data/README.md) |

---

## Contributing a term

A new entry needs a citable source that states the term's meaning, one
paragraph, and no essentialising language. If a term is used in the
repository's documentation but cannot be sourced, it does not enter this file
and its use should be reconsidered.