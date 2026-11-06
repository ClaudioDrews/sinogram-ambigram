"""Path configuration for the rotation-graph pipeline.

Environment variables override every location without code modification:

    ROTG_ROOT       code root (default: /workspace/rotgraph)
    ROTG_DATA       input data directory (default: /workspace/data)
    ROTG_KANJI_DIR  KanjiVG SVG directory
    ROTG_LISTS      lists.json file
    ROTG_CACHE      intermediate cache directory
    ROTG_OUT        output directory (default: /workspace/output)
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("ROTG_ROOT", "/workspace/rotgraph"))
DATA = Path(os.environ.get("ROTG_DATA", "/workspace/data"))
KDIR = Path(os.environ.get("ROTG_KANJI_DIR", str(DATA / "kanjivg-master" / "kanji")))
LISTS = Path(os.environ.get("ROTG_LISTS", str(DATA / "lists.json")))
CACHE = Path(os.environ.get("ROTG_CACHE", str(ROOT / "cache")))
OUT = Path(os.environ.get("ROTG_OUT", "/workspace/output"))
CAT = OUT / "catalog"
PREVIEW = OUT / "preview"
