from __future__ import annotations

import sys
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from verify_deck import (  # noqa: E402
    audit_namespace,
    prepare_output_dirs,
    select_risk_slides,
)


class VerifyDeckTests(unittest.TestCase):
    def test_risk_selection_prioritizes_structural_findings(self):
        report = {
            "text_chars_per_slide": {"values": [100, 500, 200, 300]},
            "small_text_body_candidates": [{"slide": 3}],
            "small_text_label_candidates": [{"slide": 4}],
            "title_risks": [],
            "group_shapes": [],
            "unexpected_out_of_bounds": [{"slide": 1}],
        }
        self.assertEqual(select_risk_slides(report, 3), [1, 3, 2])

    def test_zero_text_decks_do_not_divide_by_zero(self):
        report = {
            "text_chars_per_slide": {"values": [0, 0]},
            "small_text_body_candidates": [],
            "small_text_label_candidates": [],
            "title_risks": [],
            "group_shapes": [],
            "unexpected_out_of_bounds": [],
        }
        self.assertEqual(select_risk_slides(report, 2), [1, 2])

    def test_strict_mode_enables_typography_failures(self):
        args = Namespace(
            deck=Path("/tmp/deck.pptx"),
            expected_slides=5,
            allow_bleed="",
            bounds_tolerance=0.02,
            min_body_pt=14.0,
            min_title_pt=26.0,
            footer_top=6.9,
            min_small_text_chars=10,
            fail_small_text=False,
            allow_small_text=False,
            fail_title_risks=False,
            strict=True,
        )
        namespace = audit_namespace(args, Path("/tmp/audit.json"))
        self.assertTrue(namespace.fail_small_text)
        self.assertTrue(namespace.fail_title_risks)

        args.allow_small_text = True
        namespace = audit_namespace(args, Path("/tmp/audit.json"))
        self.assertFalse(namespace.fail_small_text)

    def test_runner_clears_stale_qa_artifacts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir)
            stale = out / "qa-detail" / "slide-99.jpg"
            stale.parent.mkdir(parents=True)
            stale.write_text("stale", encoding="utf-8")
            qa_dir, detail_dir = prepare_output_dirs(out)
            self.assertTrue(qa_dir.is_dir())
            self.assertTrue(detail_dir.is_dir())
            self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
