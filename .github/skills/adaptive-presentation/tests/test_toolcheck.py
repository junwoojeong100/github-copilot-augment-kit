from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import toolcheck  # noqa: E402
import tooling  # noqa: E402


class ToolcheckTests(unittest.TestCase):
    def test_invalid_cache_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = Path(temp_dir) / "cache.json"
            cache.write_text("{broken", encoding="utf-8")
            self.assertIsNone(toolcheck.read_cache(cache))

    def test_strict_requirements_include_pillow(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": False,
            "has_pptx": True,
        }
        self.assertEqual(toolcheck.missing_required(info), ["Pillow (PIL)"])

    def test_korean_font_can_be_required(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": True,
            "has_pptx": True,
            "korean_fonts": [],
        }
        self.assertEqual(
            toolcheck.missing_required(info, require_korean_font=True),
            ["Korean font"],
        )

    def test_cache_is_bound_to_current_runtime(self):
        info = toolcheck.runtime_signature()
        self.assertTrue(toolcheck.cache_matches_runtime(info))
        changed = dict(info, python_executable="/different/python")
        self.assertFalse(toolcheck.cache_matches_runtime(changed))

    def test_path_containment_is_case_normalized(self):
        self.assertTrue(
            tooling.path_is_within(
                Path("/users/example/QA/deck.pptx"),
                Path("/Users/Example/qa"),
            )
        )


if __name__ == "__main__":
    unittest.main()
