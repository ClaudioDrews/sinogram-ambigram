"""Portable paths for the rotation-graph pipeline.

All paths resolve relative to this repository by default; environment
variables can override them for independent datasets or work directories.

ROTG_ROOT       directory containing the Python scripts (default: repo/code)
ROTG_DATA       dataset directory (default: repo/data)
ROTG_KANJI_DIR  KanjiVG canonical SVGs (default: repo/data/kanjivg/kanji)
ROTG_LISTS      character inventory (default: repo/data/lists.json)
ROTG_CACHE      intermediate arrays (default: repo/output/cache)
ROTG_OUT        generated results (default: repo/output)
"""
from __future__ import annotations

import os
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("ROTG_ROOT", str(REPOSITORY / "code"))).expanduser()
DATA = Path(os.environ.get("ROTG_DATA", str(REPOSITORY / "data"))).expanduser()
KDIR = Path(os.environ.get("ROTG_KANJI_DIR", str(DATA / "kanjivg" / "kanji"))).expanduser()
LISTS = Path(os.environ.get("ROTG_LISTS", str(DATA / "lists.json"))).expanduser()
OUT = Path(os.environ.get("ROTG_OUT", str(REPOSITORY / "output"))).expanduser()
CACHE = Path(os.environ.get("ROTG_CACHE", str(OUT / "cache"))).expanduser()
CAT = OUT / "catalog"
PREVIEW = OUT / "preview"
