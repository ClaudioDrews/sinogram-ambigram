"""Determinism regression tests for the rotation-graph pipeline.

Two levels:

* **Synthetic** (always runs, no external data): stage 1 is executed twice on a
  fixed, synthetic KanjiVG-shaped corpus. The three stage-1 artifacts must be
  byte-for-byte identical between runs and must match a frozen golden checksum,
  so any change to the parsing, resampling, rasterisation or distance-transform
  code is caught.
* **Published artifact** (runs when the pinned KanjiVG snapshot is present under
  ``data/kanjivg/kanji``): stage 1 is executed against the real corpus and the
  three published checksums are verified. These are the checksums recorded in
  ``methods/rotgraph-method.md``; they hold independently of the NumPy version
  used to produce them.

No test in this module writes outside a temporary directory.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import paths  # noqa: E402
import stage1_skeleton  # noqa: E402

REPOSITORY = CODE.parent
KANJI_DIR = REPOSITORY / "data" / "kanjivg" / "kanji"

#: Checksums of the published stage-1 artifacts, recorded in
#: ``methods/rotgraph-method.md``. Verified when the pinned KanjiVG snapshot is
#: available locally.
PUBLISHED_MD5 = {
    "points.npy": "b9a95dd6d3fc27c67dcd5623783cc8ce",
    "meta.json": "cbf4a688848d0f886341f86e322a715a",
    "dt.npy": "687a275a7537fb7215a3c0c575639683",
}

#: Golden checksums for the synthetic corpus below. Frozen on 2026-11-07.
#: Any change to stage 1 must update these deliberately, in a separate commit.
SYNTHETIC_MD5 = {
    "points.npy": "4d1ee32384c025020b8cb7719112d67e",
    "meta.json": "d48ed348dab7917e2007a0d9d55d72a0",
    "dt.npy": "2650892dbec7a01125b60dea4a93656b",
}

SYNTHETIC_CHARS = ("甲", "由", "日", "口")
_SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:kvg="http://kanjivg.tagaini.net" viewBox="0 0 109 109">'
    '<g id="kvg:StrokePaths_1">'
    '<path id="kvg:s1" kvg:type="㇐" d="{d1}"/>'
    '<path id="kvg:s2" kvg:type="丨" d="{d2}"/>'
    '</g></svg>'
)


def _synthetic_svg(index: int) -> str:
    """Deterministic, structurally distinct stroke pair for character ``index``."""
    top = 18 + index * 4
    bottom = 86 - index * 3
    left = 14 + index * 5
    right = 92 - index * 4
    d1 = f"M {left},{top} C {left + 20},{top - 3} {right - 24},{top + 2} {right},{top} L {right},{bottom}"
    d2 = f"M {left},{bottom} L {right},{bottom}"
    return _SVG_TEMPLATE.format(d1=d1, d2=d2)


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


class _PathsGuard:
    """Snapshot and restore the mutable path configuration."""

    def __init__(self) -> None:
        self._saved: dict[str, Path] = {}

    def __enter__(self) -> "_PathsGuard":
        for name in ("ROOT", "DATA", "KDIR", "LISTS", "OUT", "CACHE", "CAT", "PREVIEW"):
            self._saved[name] = getattr(paths, name)
        return self

    def __exit__(self, *exc: object) -> None:
        for name, value in self._saved.items():
            setattr(paths, name, value)


def _build_synthetic_corpus(root: Path) -> Path:
    """Create a synthetic dataset directory shaped like the real one."""
    data = root / "data"
    kanji = data / "kanjivg" / "kanji"
    kanji.mkdir(parents=True)
    for index, ch in enumerate(SYNTHETIC_CHARS):
        (kanji / f"{ord(ch):05x}.svg").write_text(_synthetic_svg(index), encoding="utf-8")
    (data / "lists.json").write_text(json.dumps({
        "joyo": list(SYNTHETIC_CHARS),
        "jinmeiyo_types": [],
        "inventory": list(SYNTHETIC_CHARS),
    }, ensure_ascii=False), encoding="utf-8")
    return data


def _run_stage1(data: Path, cache: Path) -> None:
    with _PathsGuard():
        stage1_skeleton.main([
            "--data", str(data),
            "--cache", str(cache),
            "--out", str(cache.parent / "out"),
        ])


class TestSyntheticDeterminism(unittest.TestCase):
    """Stage 1 must be reproducible on a fixed synthetic corpus."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = _build_synthetic_corpus(self.root)

    def test_two_runs_are_byte_identical(self):
        first = self.root / "cache_a"
        second = self.root / "cache_b"
        _run_stage1(self.data, first)
        _run_stage1(self.data, second)
        for name in ("points.npy", "meta.json", "dt.npy"):
            with self.subTest(artifact=name):
                self.assertTrue((first / name).is_file(), f"{name} missing")
                self.assertEqual(_md5(first / name), _md5(second / name),
                                 f"{name} differs between two identical runs")

    def test_matches_frozen_golden_checksums(self):
        cache = self.root / "cache"
        _run_stage1(self.data, cache)
        for name, expected in SYNTHETIC_MD5.items():
            with self.subTest(artifact=name):
                actual = _md5(cache / name)
                self.assertEqual(actual, expected,
                                 f"{name} checksum changed: {actual} != {expected}. "
                                 "If the change is intended, update SYNTHETIC_MD5 "
                                 "in a separate, explicitly justified commit.")


@unittest.skipUnless(KANJI_DIR.is_dir() and any(KANJI_DIR.glob("*.svg")),
                     "pinned KanjiVG snapshot not present (run scripts/download_kanjivg.sh)")
class TestPublishedArtifactChecksums(unittest.TestCase):
    """Stage 1 must reproduce the published artifacts byte for byte."""

    def test_published_stage1_checksums(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        cache = Path(tmp.name) / "cache"
        _run_stage1(REPOSITORY / "data", cache)
        for name, expected in PUBLISHED_MD5.items():
            with self.subTest(artifact=name):
                actual = _md5(cache / name)
                self.assertEqual(actual, expected,
                                 f"{name} no longer reproduces the published checksum "
                                 f"({actual} != {expected})")


if __name__ == "__main__":
    unittest.main()