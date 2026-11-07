"""Build a compact, deterministic public PRC coarse-candidate catalogue.

Input is the *measured* Stage 14 shortlist plus Stage 13 manifest. This builder
does not invent pairs, modify glyph geometry or claim readable ambigrams.
The output intentionally contains Unicode character IDs and numeric ranking
measurements, not MMah stroke outlines, medians or downloaded source files.

Run:
  python prc/build_catalog.py --candidates data/prc/search/candidates_grid37.csv \
    --manifest data/prc/inventories/manifest.json --out prc/catalog.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "prc-public-coarse-catalog-v1"
COLUMNS = {"a", "b", "iou_grid37", "z_pair_grid37", "preset", "region"}


def build(candidates: Path, manifest_path: Path, out: Path,
          top_k: int = 8, expected_preset: str = "cn-s-gb2312") -> dict:
    if not 1 <= top_k <= 50:
        raise ValueError("top_k must be between 1 and 50")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "prc-presets-v1":
        raise ValueError("Unsupported preset manifest schema")
    if manifest.get("region") != "cn-s":
        raise ValueError("Expected independent CN-S inventory")
    if manifest.get("regional_form_certified") is not False:
        raise ValueError("Unexpected source-form certification flag")
    if expected_preset not in manifest.get("presets", {}):
        raise ValueError("Unknown preset")
    digest = manifest.get("graphics_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("Source digest is missing")

    groups: dict[str, list[tuple[str, float, float]]] = {}
    pair_keys = set()
    with candidates.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not COLUMNS.issubset(set(reader.fieldnames or [])):
            raise ValueError("Stage 14 CSV columns are missing")
        for number, row in enumerate(reader, 2):
            a, b = row["a"], row["b"]
            if any(len(ch) != 1 for ch in (a, b)) or ord(a) > ord(b):
                raise ValueError(f"Invalid or noncanonical pair at row {number}")
            if row["preset"] != expected_preset or row["region"] != "cn-s":
                raise ValueError(f"Mixed variant in row {number}")
            if (a, b) in pair_keys:
                raise ValueError(f"Duplicate pair at row {number}")
            pair_keys.add((a, b))
            score = float(row["z_pair_grid37"])
            iou = float(row["iou_grid37"])
            if not math.isfinite(score) or not math.isfinite(iou) or not 0 <= iou <= 1:
                raise ValueError(f"Invalid scores at row {number}")
            groups.setdefault(a, []).append((b, score, iou))
            if a != b:
                groups.setdefault(b, []).append((a, score, iou))
    if not pair_keys:
        raise ValueError("Empty shortlist")

    data = {}
    for ch in sorted(groups, key=ord):
        ranked = sorted(groups[ch], key=lambda x: (-x[1], -x[2], ord(x[0])))[:top_k]
        data[ch] = [[p, round(s, 5), round(i, 5)] for p, s, i in ranked]
    if len(data) != manifest["presets"][expected_preset]["covered"]:
        raise ValueError("Public catalogue does not cover every preset member")
    output = {
        "schema": SCHEMA,
        "preset": expected_preset,
        "region": "cn-s",
        "source": "skishore/makemeahanzi graphics.txt",
        "source_sha256": digest,
        "source_commit": "bddc96d41bef78427ed0e034e9f7e31d71fd1b92",
        "source_license": "Arphic Public License",
        "source_forms_certified": False,
        "human_readability_validated": False,
        "method": "37x37 median-occupancy rotation IoU, min per-glyph full-cohort z-score",
        "score_is": "coarse statistical rank, not readability",
        "glyphs": len(data),
        "shortlisted_pairs": len(pair_keys),
        "visible_partners_per_glyph": top_k,
        "partners": data,
    }
    encoded = json.dumps(output, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(encoded, encoding="utf-8", newline="\n")
    return {"glyphs": len(data), "source_pairs": len(pair_keys), "bytes": len(encoded.encode("utf-8")),
            "output_sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "prc/catalog.json")
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(build(args.candidates, args.manifest, args.out, args.top_k), sort_keys=True))


if __name__ == "__main__":
    main()
