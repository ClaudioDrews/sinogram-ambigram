# Attribution and licensing by component

This repository contains original code and research text as well as third-party-derived graphical data. These components **do not all share the same license**.

## Original code and text

Original project code and documentation: [MIT License](LICENSE), copyright © 2026 Claudio Drews, excluding material listed below and any third-party material otherwise indicated. Algorithms cited from research papers are attributed to their authors; implementation is not a claim of authorship of those methods.

## KanjiVG vector stroke data

The browser demonstrations in [`generator/index.html`](generator/index.html) and [`demo/index.html`](demo/index.html) contain or may render **adaptations of KanjiVG stroke vectors**. KanjiVG is copyright © Ulrich Apel and contributors and is made available under **Creative Commons Attribution–ShareAlike 3.0 (CC BY-SA 3.0)**: https://creativecommons.org/licenses/by-sa/3.0/ . Source: https://kanjivg.tagaini.net/ and https://github.com/KanjiVG/kanjivg .

Stroke data are transformed for this project through geometric rotation, flattening/resampling, overlay and stroke-width alteration. **These derived graphical/vector portions must retain KanjiVG attribution and the applicable CC BY-SA 3.0 license.** The MIT license above is not intended to override those terms. The screenshot [`assets/generator-preview.png`](assets/generator-preview.png) depicts KanjiVG-derived vector output and is credited under the same terms.

`code/` reads KanjiVG but does not bundle its full glyph dataset; `data/` contains experiment-specific numeric measurements and character inventories, not the full source-vector library. Those measurements are distributed here as project research outputs, subject to any applicable upstream rights; this is not a legal opinion.

## Research and artistic inspiration

The ambigram art of [Issei Nomura](https://x.com/IsseiNomura) inspired the project. The artist did not author, review or endorse this repository, and no artwork from his profile is redistributed here.

The project discusses the research of Inoue and Takahashi (2020); the original paper is cited, not redistributed. Other source material should be consulted at the cited upstream links.
