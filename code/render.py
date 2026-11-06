"""Renderiza glifos KanjiVG como PNG (traços desenhados a partir das
polilinhas do path) e monta folhas de contato para os pares do grafo."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kvg import load_kanji, svg_file_for  # noqa: E402

from paths import KDIR


def render_glyph(char: str, px: int = 240, width_units: float = 7.0,
                 pad: float = 4.0, invert: bool = False) -> Image.Image:
    """Desenha o kanji. invert=True -> rotacao de 180 graus."""
    f = svg_file_for(char, KDIR)
    strokes = load_kanji(f)
    scale = (px - 2 * pad) / 109.0
    img = Image.new("L", (px, px), 255)
    dr = ImageDraw.Draw(img)
    w = max(1, int(round(width_units * scale)))
    for s in strokes:
        for poly in s["polys"]:
            pts = [(pad + x * scale, pad + y * scale) for x, y in poly]
            if len(pts) >= 2:
                dr.line(pts, fill=0, width=w, joint="curve")
            for x, y in pts:            # tampas/joins redondos
                r = w / 2.0
                dr.ellipse([x - r, y - r, x + r, y + r], fill=0)
    if invert:
        img = img.rotate(180)
    return img


def render_pair(a: str, b: str, px: int = 240) -> Image.Image:
    """[a | R(b)] lado a lado, com um separador."""
    ia = render_glyph(a, px)
    ib = render_glyph(b, px, invert=True)
    out = Image.new("L", (px * 2 + 12, px), 255)
    out.paste(ia, (0, 0))
    out.paste(ib, (px + 12, 0))
    return out


def contact_sheet(items, path, cell=120, cols=8, labels=None):
    """items: lista de (a,b) -> sheet com pares a | R(b)."""
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("L", (cols * (cell * 2 + 8), rows * (cell + 18)), 255)
    dr = ImageDraw.Draw(sheet)
    for k, (a, b) in enumerate(items):
        r, c = divmod(k, cols)
        ia = render_glyph(a, cell).resize((cell, cell))
        ib = render_glyph(b, cell, invert=True).resize((cell, cell))
        x = c * (cell * 2 + 8)
        y = r * (cell + 18)
        sheet.paste(ia, (x, y))
        sheet.paste(ib, (x + cell + 8, y))
        if labels:
            dr.text((x + 2, y + cell + 3), labels[k], fill=0)
    sheet.save(path)
    return path


if __name__ == "__main__":
    out = PREVIEW
    out.mkdir(exist_ok=True)
    chars = sys.argv[1:] or list("一十日田口王申車亜由甲天魔三品呂")
    sheet = Image.new("L", (len(chars) * 150, 160), 255)
    dr = ImageDraw.Draw(sheet)
    for i, ch in enumerate(chars):
        g = render_glyph(ch, 140)
        sheet.paste(g, (i * 150 + 5, 5))
        dr.text((i * 150 + 5, 150), ch, fill=0)
        gr = render_glyph(ch, 140, invert=True)
        # segunda linha: rotacionado
    sheet2 = Image.new("L", (len(chars) * 150, 160), 255)
    dr2 = ImageDraw.Draw(sheet2)
    for i, ch in enumerate(chars):
        g = render_glyph(ch, 140, invert=True)
        sheet2.paste(g, (i * 150 + 5, 5))
        dr2.text((i * 150 + 5, 150), ch + " (180)", fill=0)
    both = Image.new("L", (max(sheet.width, sheet2.width), sheet.height + sheet2.height), 255)
    both.paste(sheet, (0, 0))
    both.paste(sheet2, (0, sheet.height))
    both.save(out / "check.png")
    print(out / "check.png")
