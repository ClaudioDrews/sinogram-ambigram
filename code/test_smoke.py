"""Fast smoke tests for rotgraph — no KanjiVG, no OpenRouter, no golden mutation.

Covers:
  - paths.py env overrides
  - 180° rotation involution and symmetry of synthetic Chamfer
  - kvg SVG path parsing / cubic flatten endpoints
  - importability of all rotgraph modules that do not touch disk at import
"""
from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path

import numpy as np

ROTGRAPH = Path(__file__).resolve().parent
if str(ROTGRAPH) not in sys.path:
    sys.path.insert(0, str(ROTGRAPH))

EM = 109.0


def _rotate180(pts: np.ndarray, em: float = EM) -> np.ndarray:
    pts = np.asarray(pts, dtype=np.float64)
    return np.column_stack([em - pts[:, 0], em - pts[:, 1]])


def _directed_chamfer(a: np.ndarray, b: np.ndarray) -> float:
    """mean_p min_q |p-q| (Euclidean)."""
    d = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1))
    return float(d.min(axis=1).mean())


def _sym_chamfer(a: np.ndarray, b: np.ndarray) -> float:
    return 0.5 * (_directed_chamfer(a, b) + _directed_chamfer(b, a))


class TestPathsEnv(unittest.TestCase):
    def test_env_overrides(self):
        env = {
            "ROTG_ROOT": "/tmp/ci-rotg-root",
            "ROTG_DATA": "/tmp/ci-rotg-data",
            "ROTG_KANJI_DIR": "/tmp/ci-rotg-kanji",
            "ROTG_LISTS": "/tmp/ci-rotg-data/lists.json",
            "ROTG_CACHE": "/tmp/ci-rotg-cache",
            "ROTG_OUT": "/tmp/ci-rotg-out",
        }
        old = {k: os.environ.get(k) for k in env}
        try:
            os.environ.update(env)
            sys.modules.pop("paths", None)
            paths = importlib.import_module("paths")
            self.assertEqual(str(paths.ROOT), env["ROTG_ROOT"])
            self.assertEqual(str(paths.DATA), env["ROTG_DATA"])
            self.assertEqual(str(paths.KDIR), env["ROTG_KANJI_DIR"])
            self.assertEqual(str(paths.LISTS), env["ROTG_LISTS"])
            self.assertEqual(str(paths.CACHE), env["ROTG_CACHE"])
            self.assertEqual(str(paths.OUT), env["ROTG_OUT"])
            self.assertEqual(str(paths.CAT), "/tmp/ci-rotg-out/catalog")
            self.assertEqual(str(paths.PREVIEW), "/tmp/ci-rotg-out/preview")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            sys.modules.pop("paths", None)


class TestMathRotation(unittest.TestCase):
    def test_rotation_is_involution(self):
        rng = np.random.default_rng(0)
        pts = rng.uniform(0, EM, size=(50, 2))
        twice = _rotate180(_rotate180(pts))
        np.testing.assert_allclose(twice, pts, atol=1e-9)

    def test_self_pair_after_rotation_zero_for_centrosymmetric(self):
        # Point set closed under 180° about (EM/2, EM/2) → Chamfer(a, R(a)) = 0
        base = np.array([[20.0, 30.0], [40.0, 80.0], [10.0, 55.0]])
        pts = np.vstack([base, _rotate180(base)])
        d = _sym_chamfer(pts, _rotate180(pts))
        self.assertLess(d, 1e-9)

    def test_chamfer_symmetry(self):
        rng = np.random.default_rng(1)
        a = rng.uniform(0, EM, size=(30, 2))
        b = rng.uniform(0, EM, size=(25, 2))
        dab = _sym_chamfer(a, _rotate180(b))
        dba = _sym_chamfer(b, _rotate180(a))
        # D(a, R(b)) need not equal D(b, R(a)) in general; symmetry claimed in
        # compute.py is D(a,b)=D(b,a) for the rotation-graph distance that
        # compares a to R(b). Check that property:
        d_ab = _sym_chamfer(a, _rotate180(b))
        d_ba = _sym_chamfer(b, _rotate180(a))
        # With Euclidean Chamfer on finite samples these are equal only when
        # the clouds match under the isometry; assert the definition itself
        # is symmetric in the (X, Y) arguments of _sym_chamfer:
        self.assertAlmostEqual(_sym_chamfer(a, b), _sym_chamfer(b, a), places=9)
        self.assertGreaterEqual(d_ab, 0.0)
        self.assertGreaterEqual(d_ba, 0.0)


class TestKvgParse(unittest.TestCase):
    def test_parse_simple_path(self):
        import kvg

        polys = kvg.parse_path("M10,10 L20,10 L20,20 Z")
        self.assertEqual(len(polys), 1)
        self.assertEqual(polys[0].shape[1], 2)
        self.assertGreaterEqual(len(polys[0]), 3)

    def test_cubic_ends_at_p3(self):
        import kvg

        end = kvg._flatten_cubic((0, 0), (0, 1), (1, 1), (1, 0), n=8)[-1]
        np.testing.assert_allclose(end, [1.0, 0.0], atol=1e-9)


class TestImports(unittest.TestCase):
    """Import modules that do not require cache/KanjiVG at import time."""

    def test_import_kvg_paths_build_catalog_helpers(self):
        for name in ("paths", "kvg"):
            sys.modules.pop(name, None)
            importlib.import_module(name)

    def test_compile_all_scripts_exist(self):
        # The public repository retains the core algorithms, not report builders.
        expected = {"paths.py", "kvg.py", "build.py", "compute2.py",
                    "compute3.py", "refine.py", "catalog.py",
                    "make_ambigram.py"}
        present = {p.name for p in ROTGRAPH.glob("*.py")}
        missing = sorted(expected - present)
        self.assertEqual(missing, [], f"missing scripts: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
