"""Build reproducible, operator-attributed PRC glyph examples for the public site.

This script calls the actual integrated Python operators, never a substitute
CSS/schematic implementation. Generated ink is derived from checksum-pinned
Make Me a Hanzi geometry (Arphic Public License), NOT MIT-licensed artwork.

Invocation (after scripts/download_prc_sources.sh):
  python code/build_prc_method_gallery.py --graphics data/prc/graphics.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Callable

import numpy as np

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import prc_construct as pc
import prc_r_odd
import prc_harmonic
import prc_ab_fusion

ROOT = CODE.parent
OUTPUT = ROOT / "evaluation" / "recognition" / "generated"
SOURCE_COMMIT = "bddc96d41bef78427ed0e034e9f7e31d71fd1b92"
SOURCE_SHA256 = "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
EM = (512.0, 384.0, 984.0)
CENTER = (pc.EM / 2, pc.EM / 2)


def clone(strokes):
    return [pc.Stroke(s.median.copy(), s.half_width.copy()) for s in strokes]


def to_svg(mask: np.ndarray, center=None) -> str:
    """Losslessly encode each occupied raster row as contiguous SVG runs."""
    if mask.ndim != 2 or mask.shape != (pc.GRID, pc.GRID):
        raise ValueError("Unexpected PRC grid")
    commands = []
    for y, row in enumerate(mask):
        x = 0
        while x < len(row):
            if not row[x]:
                x += 1
                continue
            start = x
            while x < len(row) and row[x]:
                x += 1
            commands.append(f"M{start} {y}h{x-start}v1h-{x-start}z")
    d = "".join(commands)
    label = "PRC-source geometric candidate; no verified human reading"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 109 109" '
            'role="img" aria-label="'+label+'"><path fill="#26231f" d="'+d+'"/>'
            '</svg>\n')


def base_glyph(graphics, ch):
    if ch not in graphics:
        raise ValueError("Missing glyph from pinned MMah: "+ch)
    return pc.load_glyph(ch, graphics, EM[:2], EM[2])


def make_case(graphics, method: str, a: str, b: str) -> tuple[np.ndarray, dict]:
    source = base_glyph(graphics, a)
    reference = pc.raster(source)
    centre = CENTER
    meta = {}
    if method in {"cn-natural-self", "cn-natural-pair", "cn-source-outline"}:
        constructed = source
    elif method == "cn-source-union":
        target = base_glyph(graphics, b)
        rb = prc_ab_fusion.rotate_strokes(target, centre)
        constructed = clone(source) + rb
        meta["operator"] = "corrected-median ink union"
    elif method == "cn-centre-optimisation":
        centre, quality = pc.find_centre(source)
        constructed = source
        # The actual centre parameter is recorded; the output ink remains
        # unchanged (this method chooses a centre, not a new shape).
        meta["selected_center"] = list(centre)
        meta["selected_symmetry"] = float(quality)
    elif method == "cn-extremity-reconciliation":
        constructed = clone(source)
        meta["reconciliation"] = pc.reconcile(constructed, centre)
    elif method == "cn-sector-deterministic":
        constructed, mult = pc.equalise_opposite_sectors(source, centre)
        meta["sector_multipliers"] = [float(x) for x in mult]
    elif method == "cn-sector-search":
        constructed, mult, objective = pc.search_sector_multipliers(
            source, centre, reference, rounds=1
        )
        meta["sector_multipliers"] = [float(x) for x in mult]
        meta["objective"] = objective
        meta["rounds"] = 1
    elif method == "cn-width-fixed":
        # Current measured half-width semantics: the v2 corrective baseline
        # is *already* active in pc.load_glyph + pc.raster.
        constructed = source
        meta["corrected_half_width"] = True
    elif method == "cn-r-odd":
        constructed, metrics = prc_r_odd.compensate(source, centre)
        meta["objective"] = metrics
        meta["parameters"] = {"lam": 0.9, "radius": 12.4, "cap": 1.9, "growth_max": 1.28}
    elif method == "cn-harmonic":
        constructed, info = prc_harmonic.optimize(source, centre, rounds=2)
        meta["objective"] = info
        meta["parameters"] = {"levels": [-0.2, 0.2], "rounds": 2, "growth_max": 1.28}
    elif method == "cn-ab-fusion":
        target = base_glyph(graphics, b)
        constructed, info = prc_ab_fusion.construct(source, target, centre)
        meta["objective"] = info
        meta["parameters"] = {"threshold": 4.0, "alphas": [0.25, 0.5, 0.75]}
        union = pc.raster(clone(source) + prc_ab_fusion.rotate_strokes(target, centre))
        meta["identical_to_union"] = bool(np.array_equal(pc.raster(constructed), union))
    else:
        raise ValueError("Unknown method "+method)
    output = pc.raster(constructed)
    meta.update({
        "symmetry_before": float(pc.sector_score(source, centre, reference)["sym"]),
        "symmetry_after": float(pc.sector_score(constructed, centre, reference)["sym"]),
        "pixel_equal_to_source": bool(np.array_equal(reference, output)),
        "centre": [float(x) for x in centre],
        "ink_pixels": int(output.sum()),
    })
    if not output.any():
        raise ValueError("Blank method stimulus: "+method+" "+a)
    return output, meta


# Genuine operator examples. For self-rotation each case uses the same
# PRC-derived source glyph. For distinct-pair fusion, actual A and B inputs.
CASES = (
    ("cn-natural-self", "田", "田"), ("cn-natural-self", "目", "目"),
    ("cn-natural-pair", "甲", "由"), ("cn-natural-pair", "王", "玉"),
    ("cn-source-union", "甲", "由"), ("cn-source-union", "王", "玉"),
    ("cn-centre-optimisation", "田", "田"), ("cn-centre-optimisation", "目", "目"),
    ("cn-extremity-reconciliation", "田", "田"), ("cn-extremity-reconciliation", "目", "目"),
    ("cn-sector-deterministic", "田", "田"), ("cn-sector-deterministic", "目", "目"),
    ("cn-sector-search", "田", "田"), ("cn-sector-search", "目", "目"),
    ("cn-width-fixed", "田", "田"), ("cn-width-fixed", "目", "目"),
    ("cn-r-odd", "田", "田"), ("cn-r-odd", "目", "目"),
    ("cn-harmonic", "田", "田"), ("cn-harmonic", "目", "目"),
    ("cn-ab-fusion", "甲", "由"), ("cn-ab-fusion", "韦", "芈"),
)


def build(graphics_path: Path, output: Path, methods=None):
    source_hash = hashlib.sha256(graphics_path.read_bytes()).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError("Source checksum mismatch: refusing unpinned geometry")
    graphics = pc.load_graphics(graphics_path)
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    for method, a, b in CASES:
        if methods and method not in methods:
            continue
        mask, metrics = make_case(graphics, method, a, b)
        svg = to_svg(mask)
        name = f"{method}-{ord(a)}-{ord(b)}.svg"
        target = output / name
        target.write_text(svg, encoding="utf-8")
        cases.append({
            "id": name[:-4],
            "method": method,
            "track": "cn",
            "type": "constructed" if method not in {"cn-natural-self","cn-natural-pair"} else
                    ("natural-self" if method=="cn-natural-self" else "natural-pair"),
            "status": "experimental-operator-output" if method not in {"cn-natural-self","cn-natural-pair"} else "unmodified-source-geometric-candidate",
            "a": a, "b": b, "file": name,
            "svg_sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
            "raster_sha256": hashlib.sha256(mask.tobytes()).hexdigest(),
            "metrics": metrics,
            "source": "Make Me a Hanzi · corrected median geometry · Arphic Public License",
        })
        print(method, a, b, "changed", not metrics["pixel_equal_to_source"])
    manifest = {
        "schema": "sinogram-prc-method-examples-v1",
        "source_commit": SOURCE_COMMIT,
        "source_sha256": source_hash,
        "licence": "Arphic Public License; see ../../../licenses/ARPHICPL.TXT",
        "code": "code/build_prc_method_gallery.py, code/prc_construct.py, code/prc_{r_odd,harmonic,ab_fusion}.py",
        "disclaimer": "Actual geometric code output, not a native-reader validated ambigram.",
        "items": cases,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False)+"\n",
        encoding="utf-8"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--methods", type=str, default="")
    args = parser.parse_args()
    methods = set(args.methods.split(",")) if args.methods else None
    built = build(args.graphics, args.out, methods)
    print(f"Generated {len(built['items'])} genuine operator-attributed examples")


if __name__ == "__main__":
    main()
