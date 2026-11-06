# Sinogram Ambigrams

**A 180° turn can change more than the shape of a character.**

**Read in:** English · [简体中文](docs/zh/README.md) · [日本語](docs/ja/README.md)

A research and art project by **Claudio Drews** exploring how Chinese *hanzi* and Japanese *kanji* can be transformed into **rotational ambigrams**: a single drawing designed to suggest one character upright and another after a half-turn. It brings together geometric search, stroke-level construction, structural decomposition and visual interpretation.

Inspired by the ambigram art of [Issei Nomura](https://x.com/IsseiNomura) and by a fascination with the intersection of **geometry, language, perception and meaning**. This is an independent project, not affiliated with or endorsed by the artist.

![Screenshot of the browser-based Ambigram Generator showing 甲 and 由](assets/generator-preview.png)

## Explore the project

The website has a [compact landing page](index.html) linking both tools when GitHub Pages is enabled.


| Interactive experience | What you can do |
| --- | --- |
| **[Ambigram Generator](generator/index.html)** | Enter a Chinese or Japanese character, inspect ranked rotational neighbors, build a vector candidate, rotate it and save the SVG. Includes a small, explicitly curated semantic-alternative fallback. |
| **[Rotation Lab](demo/index.html)** | Explore **16 examples**, including dense and complex characters; compare geometric overlays, shared strokes, salience, symmetry and component-layout demonstrations. |

**To run the interactive pages:** open the HTML files locally, or enable [GitHub Pages](#publish-the-demos-on-github-pages). The links above open source files on GitHub until Pages is configured. Both interfaces provide English, Chinese and Japanese.

### A first example: 甲 ↔ 由

The generator looks for characters whose stroke geometry becomes similar after **180° rotation**. It uses a KanjiVG-based ranking to select potential partners and combines the original stroke skeleton with the rotated partner. The combined drawing is meant to be judged by rotating it and comparing it with the reference characters. It is an experimental drawing, not a claim that every candidate will be legible.

## How it works

```text
Input character
    │
    ├─ Rotation-graph search: identify geometric neighbors
    ├─ Vector construction: combine original and 180°-rotated strokes
    ├─ Explore methods: salience / overlay / shared skeleton / C₂ symmetry
    └─ If no suitable direct candidate: try a small curated semantic alternative
                 ↓
        Interactive, rotatable SVG + method explanation + feedback
```

**Core formal idea.** For rotation \(R(x,y)=(-x,-y)\) in centered coordinates, a drawing \(g\) is an A/B ambigram when it is perceived as **A** upright and **B** after applying \(R\). The project's geometric scores rank *shapes*, while the visitor's visual assessment helps judge whether a particular drawing succeeds.

The current prototype is intentionally small: the generator indexes **5,180 refined measurements** over **2,770 characters** (including 2,770 self-pairs); it embeds vectors for **432 characters** and may load further KanjiVG paths on demand. Its fallback is a small set of curated semantic alternatives, **not** a comprehensive Chinese/Japanese synonym dictionary. The Rotation Lab offers 16 selected examples. Neither application requires an LLM or server-side runtime.

## Research and implementation

| Directory | Contents |
| --- | --- |
| [`theory/`](theory/) | Rotational algebra, IDS composition, stroke families, word-level rules and the legibility-set formulation. |
| [`methods/`](methods/) | Search algorithms, vector geometry, distance metrics and the Inoue–Takahashi hiragana method. |
| [`findings/`](findings/) | Experimental results, interesting pairs, disagreements and practical limitations. |
| [`data/`](data/) | Character lists and CSV datasets for C₂ glyphs, refined pairs and top candidates. |
| [`code/`](code/) | Python rotation-graph pipeline components and experimental ambigram synthesis. |
| [`generator/`](generator/) | Standalone browser proof of concept, its technical README and attribution. |
| [`demo/`](demo/) | Rotation Lab: 16 interactive examples. |

The geometric experiment searched the **2,770-character Japanese Jōyō + Jinmeiyō inventory** and generated rankings for **3,837,835 unordered pairs including self-pairs**. The repository retains the selected refined results; it does not include the complete 3.84-million-row archive. This Japanese-derived inventory does **not** cover all Chinese hanzi.

### Try the Python modules

Requires **Python 3.12 or newer** for the versions pinned in `code/requirements.txt`.


```bash
python -m pip install -r code/requirements.txt
python -m unittest discover -s code -p 'test_*.py' -v
```

The smoke tests use synthetic data. Full recomputation requires the pinned KanjiVG source and the experiment inputs; see [`methods/rotgraph-method.md`](methods/rotgraph-method.md) and [`data/KANJIVG_PIN.txt`](data/KANJIVG_PIN.txt). Some pipeline stages retain their original environment-based path configuration.

## Publish the demos on GitHub Pages

1. Upload this directory as the **repository root**.
2. In **Settings → Pages**, choose **Deploy from a branch**, select the publishing branch and **/(root)**, then save.
3. Once Pages publishes the site, open `https://<account>.github.io/<repository>/generator/` or `https://<account>.github.io/<repository>/demo/` (replace the placeholders with the actual repository owner and name).

The demo HTML files run without a build process. The generator's embedded glyphs work offline; fetching additional vectors requires internet access. A GitHub repository file preview does not execute the JavaScript application.

## Contribute and give feedback

Try a character, rotate the output and compare it with both references. If you see a better reading or a promising transformation, share the character pair, screenshot/SVG and method by emailing **[Claudio Drews](mailto:21au6i06R3w55891@proton.me)** or through [GitHub](https://github.com/ClaudioDrews). After publication, repository issues can be used to collect examples and improvements.

## Credit and licensing

Original project code and prose by Claudio Drews: [MIT](LICENSE). **KanjiVG-derived vector artwork and adapted stroke data** embedded in the browser demos: [CC BY-SA 3.0](NOTICE.md). KanjiVG is © Ulrich Apel and contributors; see [KanjiVG](https://kanjivg.tagaini.net/). Licenses for the code, measurements and adapted artwork are distinguished in [`NOTICE.md`](NOTICE.md). The work of Issei Nomura is an inspiration, not content redistributed by this project.

**Research provenance:** model names in the experiment notes identify tools or experimental runs, not co-authors.
