"""Offline integrity tests for exact-codepoint PRC inventories."""
from __future__ import annotations
from pathlib import Path
import tempfile
import unittest

import stage13_prc_presets as presets
from prc_inventory import checksum


class TestPresets(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.graphics = self.root / "g.txt"
        self.graphics.write_text('{"character":"一"}\n{"character":"中"}\n', encoding="utf8")
        self.sha = checksum(self.graphics)

    def test_codec_exact_6763(self):
        self.assertEqual(len(presets.gb2312_characters()), 6763)

    def test_deterministic_and_missing_reported(self):
        a = self.root / "a"
        b = self.root / "b"
        ma = presets.generate(self.graphics, a, expected_sha=self.sha)
        mb = presets.generate(self.graphics, b, expected_sha=self.sha)
        self.assertEqual(ma, mb)
        self.assertEqual(ma["presets"]["cn-s-gb2312"]["covered"], 2)
        self.assertEqual(ma["presets"]["cn-s-gb2312"]["missing"], 6761)
        self.assertEqual(ma["source_geometry_scope"], "simplified-and-traditional")
        self.assertFalse(ma["regional_form_certified"])
        for x in sorted(a.iterdir()):
            self.assertEqual(x.read_bytes(), (b / x.name).read_bytes(), x.name)
        self.assertEqual((a / "cn-s-gb2312.txt").read_text(),
                         presets.character_file({"中", "一"}))

    def test_pin_failure_writes_nothing(self):
        out = self.root / "invalid"
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            presets.generate(self.graphics, out, expected_sha="0" * 64)
        self.assertFalse(out.exists())

    def test_invalid_tcc_rejected_before_write(self):
        tcc = self.root / "incomplete.txt"
        tcc.write_text("0001 一\n", encoding="utf8")
        out = self.root / "no"
        with self.assertRaisesRegex(ValueError, "Expected TCC indices"):
            presets.generate(self.graphics, out, tcc=tcc, expected_sha=self.sha)
        self.assertFalse(out.exists())

    def test_character_file_scalar_only(self):
        with self.assertRaisesRegex(ValueError, "single-codepoint"):
            presets.character_file({"AB"})


if __name__ == "__main__":
    unittest.main()
