# C₂ Visual Research Lab — mathematical and scientific scope

**Status:** standalone static visual demonstration under independent PR review. This does not change the underlying research methods, historical measurements, or human-reading claims.

## Five demonstrations

1. **C₂ parity decomposition and moving rotation centre.** Uses the exact same Japanese KanjiVG stroke paths as the existing Rotation Lab, moved verbatim into a shared JavaScript data file. The glyph is sampled by Canvas2D on a 145×145 grid with 18-pixel padding around its former 109-unit domain. The visitor controls glyph, centre offsets, interpolated rotation, and an optional animation.
2. **PRC historical versus corrected width.** Synthetic median-to-outline bands illustrate that the original v1.16 path drew effective stroke width h for a measured half-width h, while the correction draws 2h. Separately shown historical research medians are source-outline IoU 0.4743 to 0.9083, improvement in 32/32 cases, as verified in PR #19. The bands are not original MMah outlines.
3. **A/B match registration versus accepted drawing.** Frozen independent 32-pair study from draft PR #21: at thresholds 2, 4, 8, 12, 16, the two separate 16-pair arms report 0+0, 2+1, 11+6, 14+9 and 16+15 pairs with at least one registered stroke. The number of final raster changes is zero in all 32 new pairs at each threshold. The two older pilot pairs are excluded from the denominators.
4. **Local and harmonic spatial field concepts.** Two synthetic heatmaps illustrate a local Gaussian patch and an exactly C₂-even cosine-product field. These are *not* outputs from R-ODD PR #14 or harmonic PR #15 and are not evidence of method superiority.
5. **Geometry versus reading.** Source geometry similarity, construction changes, VLM recognition and human recognition are separate evaluations. The visual laboratory only demonstrates geometry.

## Exact mathematical contract

Let R be the half-turn about centre c and g a scalar ink-coverage field:

    R_c g(p) = g(2c - p)
    g_even = (g + R_c g)/2
    g_odd  = (g - R_c g)/2
    g(t)   = g_even + t*g_odd,  -1 <= t <= 1

On the unbounded plane, R²=identity, R(g_even)=g_even, R(g_odd)=-g_odd.
The interpolation is the actual source at t=+1 and its exact half-turn at t=-1; the even component at t=0 need not be a readable character.

Pixel-centre positions are rotated on a grid of N=145 by the integer-index mapping x'=round(2*cx-x-1), similarly for y. The centre offset slider uses integer positions. A finite canvas can still clip some ink; a clipped-ink diagnostic is displayed. The original paths, rasterized strokes, and finite-pixel geometry are not equivalent to the ideal continuous contour.

**Geometric metrics:** binary overlap is IoU on coverage>=0.5; normalized asymmetry is sum(abs(g-Rg))/sum(g+Rg), zero if both empty. Neither is a human readability score.

The original Rotation Lab's historical "C₂ symmetry" mode only *overlays* source paths and their rotated copies. Its description is corrected to "C₂ overlay"; the new page is the one performing an actual even/odd decomposition.

## Reproduce and review

The page runs as static HTML/CSS/JS without external JavaScript, model API, analytics, or personal-data submission.

    node --check demo/kanjivg-geometry.js
    node --check demo/c2-core.js
    node --check demo/c2/app.js
    node --test tests/c2-visual.test.cjs

The tests verify R² on interior grids, even/odd invariants, endpoints of interpolation, centre movement, symmetry metrics, clipping, input validation, shared KanjiVG geometry, local asset links and English/Chinese/Japanese translation keys. Desktop and mobile rendering should be smoke-tested before deployment.

## Source and licence

- Japanese stroke paths: **KanjiVG, CC BY-SA 3.0**, retaining existing project attribution.
- PRC data provenance and widths: **Make Me a Hanzi, Arphic Public License**. No MMah-derived outlines or images are included in this page.
- Original UI/math/tests: repository MIT license; synthetic heatmaps and width diagrams are original schematic illustrations.
- Findings from PRs #19 and #21 are cited without modifying or reinterpreting old source-level datasets.

Not claimed: native-reader success, regional norm certification, complete PRC ambigram construction, or superiority of experimental operators.
