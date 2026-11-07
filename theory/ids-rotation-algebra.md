# IDS Rotation Algebra (anti-automorphism)

**Evidence basis:** The formulas below are derived from explicit structural assumptions; empirical claims require geometric measurements or recognition tests.

> **Evidence boundary:** Earlier synthesis documents suggested some of these rules without testing them. Untested rules remain [CLAIM] or [PLAN], not measured conclusions.

## 1. Core rule [DERIVED]

IDS trees describe how components compose a glyph. 180° rotation reverses the order of children (both axes flip) and replaces enclosing operators by their duals:

`R(op(t₁,…,t_k)) = op′(R(t_k),…,R(t₁))`

| Operator | Arity | Rule under R |
|---|---|---|
| ⿰ ⿱ | 2 | self-dual; children **reversed**: `R(⿰AB)=⿰R(B)R(A)`, `R(⿱AB)=⿱R(B)R(A)` |
| ⿲ ⿳ | **3** | self-dual; reversed: `R(⿲ABC)=⿲R(C)R(B)R(A)` (an early draft wrongly said four operands; corrected by GPT/Claude) |
| ⿵ ↔ ⿶ | 2 | dual pair (surround from above ↔ below); frame/content roles keep order |
| ⿷ ↔ ⿼ | 2 | dual pair (U+2FFC ⿼, Unicode 15.1) |
| ⿸ ↔ ⿽ | 2 | dual pair (U+2FFD ⿽, Unicode 15.1) |
| ⿹ ↔ ⿺ | 2 | dual pair |
| ⿴ | 2 | self-dual; frame and content keep roles (frame must itself be R-invariant for C2) |
| ⿻ | 2 | overlay — **implementations disagree** (see §4) |
| ⿾ ⿿ | 1 | Unicode 15.1 reflection / rotation primitives; `R(⿿A)=A`; `R(⿾A)=⿿⿾A` (GPT encodes V as R∘H) |

`R` also acts on leaves: a leaf is replaced by its R-partner σ(leaf) (e.g. 口→口, 日→日; 土→士? disputed). Identity as fallback is **not** proof of invariance (GPT code comment).

## 2. Theorems / laws derived (all [DERIVED]; CAT-XLSX rows)

* **Duplicate duad**: ⿰SS or ⿱SS is an exact self-ambigram iff S is C2 (昌=⿱日日, 吕/呂=⿱口口 predicted). In fonts the top component is drawn smaller (slot convention): measured IoU of 昌/吕 only 0.52–0.54 (GLM), 0.091/0.203 unshifted (GPT) — the algebra predicts, the font breaks (exp-02, exp-01).
* **Symmetric core shift**: `X = C ⊕_p s` ⇒ `R(X) = C ⊕_{R(p)} R(s)` (甲↔由: vertical stroke at top vs bottom of 田).
* **V-symmetric conjugation**: for left–right symmetric glyphs `R(S)=H(S)` (vertical flip) since `R = V∘H`; explains mirror-like pairs (士/干, 土/士, 未/末 *claims*).
* **Conjugation**: for an edit T, `R∘T = T′∘R` where T′ is the conjugated edit (`LOG-DEEPSEEK`, three-layer framework below).
* **Exact IDS pairs** (DeepSeek, `CAT-XLSX`): 杏 (⿱木口) ↔ 呆 (⿱口木), 杳 (⿱木日) ↔ 杲 (⿱日木) under `R(⿱AB)=⿱R(B)R(A)` — zero tree cost (τ=0) **provided the leaves 木/口/日 are treated as R-invariant**. *Editorial note (not in sources):* 木 is left–right symmetric but not point-symmetric, so `R(木)=木` is an assumption; no run tested these four characters visually. Status [DERIVED], untested.
* **Fixed IDS examples that fail**: 圭 (⿱土土) is *not* a self-ambigram if R(土)=士; 朋 undetermined until R(月) known (GPT fixture notes).
* **Three-layer edit cost** σ=(τ,ρ,α) = (tree edit distance, stroke re-typing cost, affine residual) — `LOG-DEEPSEEK`; `anti(node)` recursive function; costs in [stroke table](../theory/stroke-type-rotation-table.md). Not executed.

## 3. Implementations present in the folder

| Implementation | Where | Notes |
|---|---|---|
| `rotate_ids`, `DUAL`, `POSITIONAL_REVERSE`, `SURROUND_OPERATORS`, CHISE parser (`parse_chise_ids` incl. `@apparent=`) | `PKG-GPT` `sinogram_rotation_prototype.py`; **23/23 offline tests passed** [MEASURED per `pilot_run_summary.json`/report] | Unknown/new operators raise instead of being guessed. |
| `Rterm`, `DUAL`, `REVERSE={⿰⿱⿲⿳}`, `ARITY` (⿲⿳=3, ⿾⿿=1), `load_ids` over `IDS-UCS-Basic/Ext-A/Compat` | `PKG-CLAUDE` `rot.py` | CHISE files (not saved in folder); 941 leaf components; leaf map from visual F1≥0.80. |
| `anti_ids`, `edit_anti` | `LOG-DEEPSEEK` | Code text only; never executed. |

## 4. Known disagreements and open points

* **⿻ (overlay)**: DeepSeek reverses children; GPT code **preserves layer order** ("overlay/layer order"); Claude `Rterm` leaves it unchanged (`DUAL.get(op, op)`, not in REVERSE). No test decides. [CONFLICT C-12]
* **⿾ / ⿿ meaning**: names confirmed only via secondary sites (symbl.cc, fileformat.info, Wikipedia; UCD PDF blocked) — ⿾ horizontal reflection, ⿿ rotation (`LOG-MULTI`). Earlier GLM answer "⿷ has no dual" was wrong (⿼ is its dual); earlier "⿸ dual ⿿" wrong (it is ⿽).
* **Source of IDS data**: CHISE (GPT/Claude/Kimi planned) vs UCD `IDS.txt` Unicode 15.1 (DeepSeek: CHISE may lag U+2FFC–2FFF). CHISE decomposes some chars with alternates and some as atomic (甲, 未 atomic ⇒ IDS cannot separate 甲/由); CHISE lists 昌 as ⿱日曰 not ⿱日日 (Claude) — so "duplicate duad" fixtures are idealised, not CHISE-verified (GPT states this).
* **Unicode IDC usage**: IDS is *positional*; stroke-type/curvature info absent ⇒ algebra gives structure only; geometry/legibility layers still needed (GPT's three-component architecture: structural algebra + transformational geometry + legibility model).
* Operator subtleties by family: ⿴/⿻ may keep distinct roles for frame vs content; ternary operators need 3-way reversal; enclosure opening direction flips.

## Related

- Glossary and notation
- [Stroke-type rotation table](../theory/stroke-type-rotation-table.md)
- [Family rules](../theory/family-rules.md)
