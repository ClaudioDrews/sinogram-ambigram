"""Portable paths and explicit configuration for the rotation-graph pipeline.

Resolution order (highest priority first):

1. Explicit values passed to :func:`configure` (CLI flags ``--data``/``--cache``/
   ``--out``/``--kanji``).
2. Environment variables ``ROTG_*`` (optional overrides for side-by-side
   datasets or scratch workspaces).
3. Repository-relative defaults, so a clean clone works with no configuration
   at all.

Environment variables are *overrides*, not the primary configuration mechanism.
A fresh clone resolves every path inside the repository.
"""
from __future__ import annotations

import argparse
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


def configure(data: Path | str | None = None,
              cache: Path | str | None = None,
              out: Path | str | None = None,
              kanji: Path | str | None = None,
              lists: Path | str | None = None) -> None:
    """Apply explicit configuration, overriding environment variables and defaults.

    Called by each pipeline stage after parsing its command line. Values are
    resolved relative to the current working directory when relative.
    """
    global DATA, KDIR, LISTS, OUT, CACHE, CAT, PREVIEW

    if out is not None:
        OUT = Path(out).expanduser()
    if data is not None:
        DATA = Path(data).expanduser()
    if cache is not None:
        CACHE = Path(cache).expanduser()
    if kanji is not None:
        KDIR = Path(kanji).expanduser()
    if lists is not None:
        LISTS = Path(lists).expanduser()

    # Derived locations follow their parents unless set explicitly.
    if data is not None and kanji is None:
        KDIR = DATA / "kanjivg" / "kanji"
    if data is not None and lists is None:
        LISTS = DATA / "lists.json"
    if out is not None and cache is None:
        CACHE = OUT / "cache"
    CAT = OUT / "catalog"
    PREVIEW = OUT / "preview"


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add the shared path flags to a stage's argument parser."""
    parser.add_argument("--data", type=Path, default=None,
                        help="dataset directory (default: <repo>/data)")
    parser.add_argument("--cache", type=Path, default=None,
                        help="intermediate array directory (default: <out>/cache)")
    parser.add_argument("--out", type=Path, default=None,
                        help="output directory (default: <repo>/output)")
    parser.add_argument("--kanji", type=Path, default=None,
                        help="KanjiVG canonical SVG directory (default: <data>/kanjivg/kanji)")
    parser.add_argument("--lists", type=Path, default=None,
                        help="character inventory JSON (default: <data>/lists.json)")
    return parser


def resolve(args: argparse.Namespace) -> None:
    """Apply a parsed argument namespace produced by :func:`add_common_args`."""
    configure(data=getattr(args, "data", None),
              cache=getattr(args, "cache", None),
              out=getattr(args, "out", None),
              kanji=getattr(args, "kanji", None),
              lists=getattr(args, "lists", None))