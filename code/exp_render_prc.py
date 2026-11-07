"""Render blinded PRC experimental images from a pinned MMah graphics source.

Example:
  python code/exp_render_prc.py --graphics /path/to/graphics.txt \
    --characters "田,中" --mode baseline --out /tmp/prc-baseline
  python code/exp_render_prc.py --graphics /path/to/graphics.txt \
    --pairs "甲:由,韦:芈" --mode ab-fusion --out /tmp/prc-fusion

`case-N-upright.png` and `case-N-rotated.png` are unlabeled test stimuli.
Do not show the manifest or source character labels to vision models.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image
import numpy as np
import prc_construct as pc


def render_ink(ink, dest: Path, scale: int = 4):
    # Ink black, background white. NEAREST preserves the binary geometry.
    img = Image.fromarray(np.where(ink, 0, 255).astype("uint8"), mode="L")
    img = img.resize((img.width * scale, img.height * scale),
                     resample=Image.Resampling.NEAREST)
    img.save(dest)
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def generate(graphics: Path, out: Path, mode: str,
             characters: list[str], pairs: list[tuple[str, str]],
             em: tuple[float, float, float], centre: tuple[float, float]):
    data = pc.load_graphics(graphics)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for i, target in enumerate([*( (ch, ch) for ch in characters), *pairs], 1):
        ch_a, ch_b = target
        if ch_a not in data or ch_b not in data:
            raise ValueError("Missing character in provided graphics source")
        a = pc.load_glyph(ch_a, data, em[:2], em[2])
        b = pc.load_glyph(ch_b, data, em[:2], em[2])
        if mode == "ab-fusion":
            from prc_ab_fusion import construct, score
            drawing, info = construct(a, b, centre)
            metrics = score(drawing, a, b, centre)
        elif ch_a != ch_b:
            rotated_b = [pc.Stroke(pc.half_turn(s.median, centre),
                                   s.half_width.copy()) for s in b]
            drawing = a + rotated_b
            info = {"operator": "unmodified_union"}
            ink_union = pc.raster(drawing)
            ink_a, ink_b = pc.raster(a), pc.raster(b)
            ink_rot = pc.half_turn_grid(ink_union, centre)
            def _f1(x, y):
                return 2 * float(np.logical_and(x, y).sum()) / max(
                    float(x.sum() + y.sum()), 1.0)
            fa, fb = _f1(ink_union, ink_a), _f1(ink_rot, ink_b)
            metrics = {"f1_a": fa, "f1_b": fb, "minimum_f1": min(fa, fb),
                       "joint_f1": fa * fb, "stroke_count": len(drawing)}
        elif mode == "r-odd":
            from prc_r_odd import compensate
            drawing, metrics = compensate(a, centre)
            info = {"operator": mode}
        elif mode == "harmonic":
            from prc_harmonic import optimize
            drawing, info = optimize(a, centre)
            metrics = info["score"]
        else:
            drawing = a
            metrics = pc.sector_score(a, centre, pc.raster(a))
            info = {"operator": "baseline"}
        ink = pc.raster(drawing)
        rotated = pc.half_turn_grid(ink, centre)
        stem = f"case-{i:05d}"
        names = [stem + "-upright.png", stem + "-rotated.png"]
        hashes = [render_ink(grid, out / name)
                  for grid, name in zip((ink, rotated), names)]
        records.append({"case": stem, "target_a": ch_a, "target_b": ch_b,
                        "images": names, "sha256": hashes, "mode": mode,
                        "metrics": metrics, "info": info})
    manifest = {
        "schema": 1,
        "mode": mode,
        "centre": centre,
        "em": em,
        "source_sha256": hashlib.sha256(graphics.read_bytes()).hexdigest(),
        "records": records,
        "important": "Keep this manifest hidden during blinded VLM reading."}
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return len(records)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--graphics", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--mode", required=True,
                   choices=("baseline", "r-odd", "harmonic", "ab-fusion"))
    p.add_argument("--characters", default="")
    p.add_argument("--pairs", default="")
    p.add_argument("--em", default="512,384,984")
    p.add_argument("--centre", default="54.5,54.5")
    args = p.parse_args(argv)
    chars = [x.strip() for x in args.characters.split(",") if x.strip()]
    pairs = []
    for value in args.pairs.split(","):
        if not value.strip():
            continue
        parts = value.strip().split(":")
        if len(parts) != 2 or not all(parts):
            p.error("--pairs must be A:B,A:B")
        pairs.append((parts[0], parts[1]))
    if not chars and not pairs:
        p.error("Provide --characters or --pairs")
    if pairs and args.mode in ("harmonic", "r-odd"):
        p.error("Harmonic and R-ODD evaluate self-rotation only; use A/B fusion for distinct pairs")
    em = tuple(float(x) for x in args.em.split(","))
    centre = tuple(float(x) for x in args.centre.split(","))
    if len(em) != 3 or len(centre) != 2:
        p.error("Invalid --em or --centre")
    n = generate(args.graphics, args.out, args.mode, chars, pairs, em, centre)
    print(f"Saved {n} blinded cases to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
