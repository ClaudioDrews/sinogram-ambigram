"""Auditable, region-specific coverage of a pinned PRC glyph source.

Inputs: Make Me a Hanzi graphics.txt (JSONL) and, optionally, a numbered
transcription of the 2013 Tongyong Guifan Hanzibiao (TCC). The transcription
is not bundled; its licensing/provenance must be checked independently.

Usage:
    python code/prc_inventory.py --graphics data/prc/graphics.txt
    python code/prc_inventory.py --graphics data/prc/graphics.txt --tcc path/to/list.txt --out data/prc/coverage.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def gb2312_characters() -> set[str]:
    result: set[str] = set()
    for first in range(0xA1, 0xF8):
        for second in range(0xA1, 0xFF):
            try:
                character = bytes((first, second)).decode("gb2312")
            except UnicodeDecodeError:
                continue
            if len(character) == 1 and "\u4e00" <= character <= "\u9fff":
                result.add(character)
    return result


def graphics_characters(path: Path) -> set[str]:
    found: set[str] = set()
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            character = data.get("character")
            if not isinstance(character, str) or len(character) != 1:
                raise ValueError(f"Bad character at {path}:{number}")
            if character in found:
                raise ValueError(f"Duplicate glyph at {path}:{number}: {character}")
            found.add(character)
    return found


def tcc_levels(path: Path) -> dict[str, set[str]]:
    rows: dict[int, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"^\s*(\d{4})\s+(\S)", line)
        if not match:
            continue
        index, char = int(match.group(1)), match.group(2)
        if index in rows:
            raise ValueError(f"Duplicate TCC index at line {number}")
        rows[index] = char
    if len(rows) != 8105 or set(rows) != set(range(1, 8106)):
        raise ValueError(f"Expected TCC indices 1..8105, found {len(rows)}")
    if len(set(rows.values())) != len(rows):
        raise ValueError("Duplicate character in TCC transcription")
    return {
        "level1": {c for n, c in rows.items() if n <= 3500},
        "level2": {c for n, c in rows.items() if 3500 < n <= 6500},
        "level3": {c for n, c in rows.items() if n > 6500},
    }


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def report(graphics: Path, tcc: Path | None = None) -> dict:
    available = graphics_characters(graphics)
    cohorts = {"gb2312": gb2312_characters()}
    if tcc is not None:
        cohorts.update(tcc_levels(tcc))
        cohorts["tcc_all"] = set.union(*(cohorts[k] for k in ("level1", "level2", "level3")))
    measured = {}
    for name, characters in cohorts.items():
        count = len(characters & available)
        measured[name] = {
            "inventory": len(characters),
            "covered": count,
            "coverage": count / len(characters),
            "missing": "".join(sorted(characters - available)),
        }
    return {
        "variant": "cn-s",
        "source": "skishore/makemeahanzi graphics.txt",
        "graphics_sha256": checksum(graphics),
        "source_character_count": len(available),
        "tcc_sha256": checksum(tcc) if tcc is not None else None,
        "cohorts": measured,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", required=True, type=Path)
    parser.add_argument("--tcc", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = report(args.graphics, args.tcc)
    encoded = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
