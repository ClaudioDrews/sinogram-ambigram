"""Parse KanjiVG SVG paths into stroke-centreline polylines.

KanjiVG represents each brush stroke with a single SVG path, preserving
its vector centreline without raster skeletonisation.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

SVG_NS = "{http://www.w3.org/2000/svg}"
KVG_NS = "{http://kanjivg.tagaini.net}"

VIEWBOX = 109.0  # canonical frame (KanjiVG units)


# ---------------------------------------------------------------- path parser
_TOKEN = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def _tokenize(d: str):
    for m in _TOKEN.finditer(d):
        if m.group(1):
            yield ("cmd", m.group(1))
        else:
            yield ("num", float(m.group(2)))


def _flatten_cubic(p0, p1, p2, p3, n=16):
    """Sample a cubic Bézier into n+1 points."""
    t = np.linspace(0.0, 1.0, n + 1)[1:]
    mt = 1.0 - t
    b0 = (mt ** 3)[:, None]
    b1 = (3 * mt ** 2 * t)[:, None]
    b2 = (3 * mt * t ** 2)[:, None]
    b3 = (t ** 3)[:, None]
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    p3 = np.asarray(p3, float)
    return b0 * p0 + b1 * p1 + b2 * p2 + b3 * p3


def _flatten_quad(p0, p1, p2, n=12):
    t = np.linspace(0.0, 1.0, n + 1)[1:]
    mt = 1.0 - t
    p0, p1, p2 = (np.asarray(p, float) for p in (p0, p1, p2))
    return (mt ** 2)[:, None] * p0 + (2 * mt * t)[:, None] * p1 + (t ** 2)[:, None] * p2


def _arc_points(p0, p1, rx, ry, phi, large, sweep, n=16):
    """Endpoint -> center parameterization (SVG 1.1 F.6.5)."""
    x1, y1 = p0
    x2, y2 = p1
    if rx == 0 or ry == 0:
        return np.array([p1], float)
    rx, ry = abs(rx), abs(ry)
    phi = np.deg2rad(phi)
    cosp, sinp = np.cos(phi), np.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cosp * dx2 + sinp * dy2
    y1p = -sinp * dx2 + cosp * dy2
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        s = np.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = np.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cosp * cxp - sinp * cyp + (x1 + x2) / 2.0
    cy = sinp * cxp + cosp * cyp + (y1 + y2) / 2.0

    def ang(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        ln = np.hypot(ux, uy) * np.hypot(vx, vy)
        a = np.arccos(np.clip(dot / ln, -1, 1)) if ln else 0.0
        if ux * vy - uy * vx < 0:
            a = -a
        return a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * np.pi
    elif sweep and dth < 0:
        dth += 2 * np.pi
    ts = np.linspace(0.0, dth, n + 1)[1:]
    px = cx + rx * np.cos(th1) * np.cos(phi) - ry * np.sin(th1) * np.sin(phi)
    py = cy + rx * np.cos(th1) * np.sin(phi) + ry * np.sin(th1) * np.cos(phi)
    xs = cx + rx * np.cos(th1 + ts) * np.cos(phi) - ry * np.sin(th1 + ts) * np.sin(phi)
    ys = cy + rx * np.cos(th1 + ts) * np.sin(phi) + ry * np.sin(th1 + ts) * np.cos(phi)
    return np.column_stack([xs, ys])


def parse_path(d: str, n_curve: int = 16):
    """Return a list of Nx2 polyline arrays for an SVG path d attribute."""
    toks = list(_tokenize(d))
    polys, cur = [], []
    i = 0
    cx = cy = 0.0          # current position
    sx = sy = 0.0          # subpath start
    cmd = None
    prev_c2 = None         # previous control point (reflection for S)
    prev_q = None
    while i < len(toks):
        kind, val = toks[i]
        if kind == "cmd":
            cmd = val
            i += 1
            if cmd in "Zz":
                if len(cur) > 1:
                    polys.append(np.array(cur, float))
                cur = []
                cx, cy = sx, sy
                continue
        # read numeric arguments for current command
        args = []
        while i < len(toks) and toks[i][0] == "num":
            args.append(toks[i][1])
            i += 1
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        k = 0
        while k < len(args):
            if c == "M":
                x, y = args[k], args[k + 1]
                if rel:
                    x, y = cx + x, cy + y
                if len(cur) > 1:
                    polys.append(np.array(cur, float))
                cur = [(x, y)]
                cx, cy = x, y
                sx, sy = x, y
                c = "L"  # subsequent coordinate pairs imply line-to
                k += 2
            elif c == "L":
                x, y = args[k], args[k + 1]
                if rel:
                    x, y = cx + x, cy + y
                cur.append((x, y))
                cx, cy = x, y
                k += 2
            elif c == "H":
                x = args[k]
                if rel:
                    x = cx + x
                cur.append((x, cy))
                cx = x
                k += 1
            elif c == "V":
                y = args[k]
                if rel:
                    y = cy + y
                cur.append((cx, y))
                cy = y
                k += 1
            elif c == "C":
                p = args[k:k + 6]
                if rel:
                    p = [cx + p[0], cy + p[1], cx + p[2], cy + p[3], cx + p[4], cy + p[5]]
                p1 = (p[0], p[1]); p2 = (p[2], p[3]); p3 = (p[4], p[5])
                cur.extend(map(tuple, _flatten_cubic((cx, cy), p1, p2, p3, n_curve)))
                prev_c2 = p2
                cx, cy = p3
                k += 6
            elif c == "S":
                p = args[k:k + 4]
                if rel:
                    p = [cx + p[0], cy + p[1], cx + p[2], cy + p[3]]
                p1 = (2 * cx - prev_c2[0], 2 * cy - prev_c2[1]) if prev_c2 else (cx, cy)
                p2 = (p[0], p[1]); p3 = (p[2], p[3])
                cur.extend(map(tuple, _flatten_cubic((cx, cy), p1, p2, p3, n_curve)))
                prev_c2 = p2
                cx, cy = p3
                k += 4
            elif c == "Q":
                p = args[k:k + 4]
                if rel:
                    p = [cx + p[0], cy + p[1], cx + p[2], cy + p[3]]
                p1 = (p[0], p[1]); p2 = (p[2], p[3])
                cur.extend(map(tuple, _flatten_quad((cx, cy), p1, p2)))
                prev_q = p1
                cx, cy = p2
                k += 4
            elif c == "T":
                p = args[k:k + 2]
                if rel:
                    p = [cx + p[0], cy + p[1]]
                p1 = (2 * cx - prev_q[0], 2 * cy - prev_q[1]) if prev_q else (cx, cy)
                p2 = (p[0], p[1])
                cur.extend(map(tuple, _flatten_quad((cx, cy), p1, p2)))
                prev_q = p1
                cx, cy = p2
                k += 2
            elif c == "A":
                p = args[k:k + 7]
                rx, ry, phi, large, sweep, x, y = p
                if rel:
                    x, y = cx + x, cy + y
                cur.extend(map(tuple, _arc_points((cx, cy), (x, y), rx, ry, phi,
                                                int(large), int(sweep))))
                cx, cy = x, y
                k += 7
            else:
                k = len(args)
    if len(cur) > 1:
        polys.append(np.array(cur, float))
    return polys


def load_kanji(svg_path: str):
    """Extract stroke polylines and their kvg:type labels."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    strokes = []
    for g in root.iter():
        tag = g.tag.replace(SVG_NS, "")
        if tag != "path":
            continue
        d = g.get("d")
        if not d:
            continue
        polys = parse_path(d)
        if not polys:
            continue
        strokes.append({
            "polys": polys,
            "type": g.get(KVG_NS + "type") or g.get("type") or "",
            "id": g.get("id") or "",
        })
    return strokes


def svg_file_for(char: str, kanji_dir: str) -> str | None:
    cp = ord(char)
    if cp > 0xFFFF:
        cp -= 0x10000
        hi = 0xD800 + (cp >> 10)
        lo = 0xDC00 + (cp & 0x3FF)
        names = [f"{hi:04x}.svg", f"{lo:04x}.svg"]
    else:
        names = [f"{cp:05x}.svg"]
    for n in names:
        p = Path(kanji_dir) / n
        if p.exists():
            return str(p)
    return None


def load_raw_paths(svg_path: str):
    """Return original SVG d attributes for embedding in HTML."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    out = []
    for g in root.iter():
        if g.tag.replace(SVG_NS, "") == "path" and g.get("d"):
            out.append(g.get("d"))
    return out


def glyph_svg(char: str, kanji_dir: str, rotate: bool = False, stroke: float = 7.0,
              color: str = "#14171e") -> str:
    """Inline glyph SVG (optional 180-degree rotation)."""
    f = svg_file_for(char, kanji_dir)
    if f is None:
        return ""
    ds = load_raw_paths(f)
    body = "".join(
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>' for d in ds)
    # Keep the transform inside the root: callers may embed only the inner SVG.
    if rotate:
        body = f'<g transform="rotate(180 54.5 54.5)">{body}</g>'
    return f'<svg viewBox="0 0 109 109" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


if __name__ == "__main__":
    import sys
    kd = "/workspace/data/kanjivg-master/kanji"
    for ch in sys.argv[1:]:
        f = svg_file_for(ch, kd)
        st = load_kanji(f)
        npts = sum(len(p) for s in st for p in s["polys"])
        print(f"{ch} {f}: {len(st)} strokes, {npts} points, tipos={[s['type'] for s in st]}")
