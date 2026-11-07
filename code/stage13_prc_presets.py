"""Stage 13: auditable PRC character presets, kept separate from glyph geometry.

GB2312 is generated using Python's standard codec. An optional numbered TCC
transcription is external, user-provided data: NEVER substitute an unverified
online list. We publish no licensed TCC transcription with this source code.

  python code/stage13_prc_presets.py --graphics data/prc/graphics.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prc_inventory import checksum, gb2312_characters, graphics_characters, tcc_levels
from stage12_prc_ingest import pinned_sha

ROOT = Path(__file__).resolve().parents[1]


def character_file(chars: set[str]) -> str:
    """Canonically ordered Unicode scalar values, one character per line."""
    if any(len(c) != 1 for c in chars):
        raise ValueError("A preset can only contain single-codepoint characters")
    return "".join(c + "\n" for c in sorted(chars, key=ord))


def generate(graphics: Path, out: Path, tcc: Path | None = None,
             expected_sha: str | None = None) -> dict:
    expected = expected_sha or pinned_sha()
    got = checksum(graphics)
    if got != expected:
        raise ValueError(f"Graphics source SHA-256 mismatch: got {got}, expected {expected}")
    available = graphics_characters(graphics)
    sets = {"cn-s-gb2312": gb2312_characters()}
    if tcc is not None:
        levels = tcc_levels(tcc)
        sets.update({"cn-s-tcc-l1": levels["level1"],
                     "cn-s-tcc-l2": levels["level2"],
                     "cn-s-tcc-l3": levels["level3"],
                     "cn-s-tcc-all": set().union(*levels.values())})
    meta = {"schema": "prc-presets-v1", "source": "skishore/makemeahanzi graphics.txt",
            "graphics_sha256": got, "source_glyphs": len(available),
            "source_geometry_scope": "simplified-and-traditional",
            "region": "cn-s", "regional_form_certified": False,
            "tcc_transcription_sha256": checksum(tcc) if tcc else None,
            "presets": {}}
    payloads: dict[str, str] = {}
    for name, cohort in sets.items():
        present = cohort & available
        missing = cohort - available
        text = character_file(present)
        payloads[name + ".txt"] = text
        payloads[name + "-missing.txt"] = character_file(missing)
        meta["presets"][name] = {
            "inventory_size": len(cohort), "covered": len(present),
            "coverage": len(present) / len(cohort),
            "missing": len(missing),
            "members_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "order": "ascending Unicode scalar value",
            "variant": "cn-s",
            "source_form_assessment": "unverified per character",
        }
    # All input validation and computations precede the first write.
    out.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        (out / name).write_text(data, encoding="utf-8", newline="\n")
    (out / "manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return meta


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--graphics", type=Path, default=ROOT / "data/prc/graphics.txt")
    p.add_argument("--out", type=Path, default=ROOT / "data/prc/inventories")
    p.add_argument("--tcc", type=Path, help="verified external numbered 2013 TCC transcription")
    a = p.parse_args()
    meta = generate(a.graphics, a.out, tcc=a.tcc)
    print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
