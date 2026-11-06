"""Experimental rotational-ambigram generator based on Nomura-inspired
stroke-salience and intermediate-shape heuristics (laws 2 and 3).

For pair (a,b), superimpose the skeleton of a and the rotated skeleton R(b).
Classify strokes as COMMON when near the other skeleton within tau, and
EXCLUSIVE otherwise; draw common strokes thick and exclusive strokes thin.
The same drawing is intended to be read as A upright and B after 180 degrees.
The result is intended for iterative visual inspection.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kvg import load_kanji, svg_file_for  # noqa: E402

from paths import KDIR, PREVIEW
EM = 109.0
TAU = 1.6          # tolerance (units) for a "common" stroke
W_THICK = 11.0     # common-stroke width (units)
W_THIN = 4.5       # exclusive-stroke width


def strokes_of(char: str):
    f = svg_file_for(char, KDIR)
    out = []
    for s in load_kanji(f):
        for poly in s["polys"]:
            out.append(poly)
    return out


def _dist_to_set(pts: np.ndarray, others: list) -> np.ndarray:
    """Minimum distance from each point in pts to the array list others."""
    if not others:
        return np.full(len(pts), np.inf)
    best = np.full(len(pts), np.inf)
    for o in others:
        d = np.sqrt(((pts[:, None, :] - o[None, :, :]) ** 2).sum(-1)).min(axis=1)
        best = np.minimum(best, d)
    return best


def _classify(polys, others):
    """For each polyline return (common fraction, points)."""
    res = []
    for poly in polys:
        d = _dist_to_set(poly, others)
        frac = float((d <= TAU).mean())
        res.append((poly, frac))
    return res


def build_ambigram(a: str, b: str, px: int = 420, pad: float = 4.0) -> Image.Image:
    """Candidate g intended as a upright and b when rotated 180 degrees."""
    pa = strokes_of(a)
    pb = strokes_of(b)
    # R(b): rotate 180 degrees in the frame
    rb = [np.column_stack([EM - p[:, 0], EM - p[:, 1]]) for p in pb]

    cls_a = _classify(pa, rb)
    cls_b = _classify(rb, pa)

    scale = (px - 2 * pad) / EM
    img = Image.new("L", (px, px), 255)
    dr = ImageDraw.Draw(img)

    def draw(items):
        for poly, frac in items:
            w = max(1, int(round((W_THICK if frac >= 0.5 else W_THIN) * scale)))
            pts = [(pad + x * scale, pad + y * scale) for x, y in poly]
            if len(pts) >= 2:
                dr.line(pts, fill=0, width=w, joint="curve")
            for x, y in pts:
                r = w / 2.0
                dr.ellipse([x - r, y - r, x + r, y + r], fill=0)

    draw(cls_a)
    draw(cls_b)
    return img


def build_pair_views(a: str, b: str, px: int = 210) -> Image.Image:
    """Side-by-side [a | R(b) | g] for visual inspection."""
    from render import render_glyph
    ia = render_glyph(a, px)
    ib = render_glyph(b, px, invert=True)
    ig = build_ambigram(a, b, px)
    out = Image.new("L", (px * 3 + 16, px), 255)
    out.paste(ia, (0, 0))
    out.paste(ib, (px + 8, 0))
    out.paste(ig, (px * 2 + 16, 0))
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3 or any(len(ch) != 1 for ch in sys.argv[1:]):
        raise SystemExit("Usage: python code/make_ambigram.py <character-A> <character-B>")
    out = PREVIEW
    out.mkdir(parents=True, exist_ok=True)
    pairs = [(sys.argv[1], sys.argv[2])]
    for p in pairs:
        im = build_pair_views(p[0], p[1])
        im.save(out / f"ambigram_{p[0]}_{p[1]}.png")
        print(out / f"ambigram_{p[0]}_{p[1]}.png")


def ambigram_svg(a: str, b: str, color: str = "#14171e") -> str:
    """Ambigram candidate SVG: thicker common strokes and thinner exclusive strokes."""
    pa = strokes_of(a)
    pb = strokes_of(b)
    rb = [np.column_stack([EM - p[:, 0], EM - p[:, 1]]) for p in pb]
    cls_a = _classify(pa, rb)
    cls_b = _classify(rb, pa)
    parts = []
    for items in (cls_a, cls_b):
        for poly, frac in items:
            w = W_THICK if frac >= 0.5 else W_THIN
            pts = []
            for x, y in poly:
                if not pts or ((x - pts[-1][0]) ** 2 + (y - pts[-1][1]) ** 2) ** 0.5 > 0.7:
                    pts.append((x, y))
            d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
                         f'stroke-linecap="round" stroke-linejoin="round" opacity="0.92"/>')
    return "".join(parts)
