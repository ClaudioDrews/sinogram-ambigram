"""Offline tests for the PRC inventory audit; no copyrighted font needed."""
import json
from pathlib import Path
import tempfile
import unittest

import prc_inventory as audit


class TestPrcInventory(unittest.TestCase):
    def test_gb2312_inventory_size(self):
        self.assertEqual(len(audit.gb2312_characters()), 6763)

    def test_graphics_counts_and_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "graphics.txt"
            path.write_text('{"character":"一"}\n{"character":"中"}\n', encoding="utf-8")
            result = audit.report(path)
            self.assertEqual(result["source_character_count"], 2)
            self.assertEqual(result["variant"], "cn-s")
            self.assertEqual(result["cohorts"]["gb2312"]["covered"], 2)
            self.assertEqual(result["cohorts"]["gb2312"]["inventory"], 6763)
            self.assertEqual(len(result["graphics_sha256"]), 64)

    def test_duplicate_graphics_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "graphics.txt"
            path.write_text('{"character":"中"}\n{"character":"中"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.graphics_characters(path)

    def test_incomplete_tcc_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tcc.txt"
            path.write_text("0001 一\n0002 二\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit.tcc_levels(path)

    def test_checksum_changes_with_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "graphics.txt"
            path.write_bytes(b"a")
            first = audit.checksum(path)
            path.write_bytes(b"b")
            self.assertNotEqual(first, audit.checksum(path))


if __name__ == "__main__":
    unittest.main()
