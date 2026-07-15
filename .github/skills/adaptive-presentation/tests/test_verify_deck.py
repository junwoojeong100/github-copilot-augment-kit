from __future__ import annotations

import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import render_pptx  # noqa: E402
from verify_deck import (  # noqa: E402
    audit_namespace,
    build_parser,
    prepare_output_dirs,
    select_risk_slides,
    verify,
)


class VerifyDeckTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)

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
            deck=self.work_dir / "deck.pptx",
            expected_slides=5,
            allow_bleed="",
            bounds_tolerance=0.02,
            min_body_pt=16.0,
            min_title_pt=26.0,
            footer_top=6.9,
            min_small_text_chars=10,
            fail_small_text=False,
            allow_small_text="",
            fail_unsized_runs=False,
            fail_title_risks=False,
            strict=True,
        )
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertTrue(namespace.fail_small_text)
        self.assertTrue(namespace.fail_title_risks)
        self.assertTrue(namespace.fail_unsized_runs)

        args.allow_small_text = "2"
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertEqual(namespace.allow_small_text, {2})
        self.assertTrue(namespace.fail_small_text)

    def test_runner_clears_stale_qa_artifacts(self):
        detail = self.work_dir / "qa-detail"
        render_pptx.claim_output_dir(detail)
        stale = detail / "slide-99.jpg"
        stale.write_text("stale", encoding="utf-8")
        qa_dir, detail_dir = prepare_output_dirs(self.work_dir)
        self.assertTrue(qa_dir.is_dir())
        self.assertTrue(detail_dir.is_dir())
        self.assertFalse(stale.exists())

    def test_runner_refuses_unowned_qa_directory(self):
        qa_dir = self.work_dir / "qa"
        qa_dir.mkdir()
        unrelated = qa_dir / "notes.txt"
        unrelated.write_text("keep", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            prepare_output_dirs(self.work_dir)
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

    def test_runner_does_not_delete_deck_inside_managed_qa_directory(self):
        out = self.work_dir / "verify"
        qa_dir = out / "qa"
        qa_dir.mkdir(parents=True)
        deck = qa_dir / "deck.pptx"
        deck.write_bytes(b"preserve")
        args = build_parser().parse_args([str(deck), "--out", str(out)])
        with self.assertRaises(ValueError):
            verify(args)
        self.assertEqual(deck.read_bytes(), b"preserve")

    def test_runner_report_cannot_alias_input_deck(self):
        out = self.work_dir / "verify"
        out.mkdir()
        deck = self.work_dir / "deck.pptx"
        deck.write_bytes(b"preserve")
        (out / "verification-report.json").hardlink_to(deck)
        args = build_parser().parse_args([str(deck), "--out", str(out)])
        with self.assertRaises(ValueError):
            verify(args)
        self.assertEqual(deck.read_bytes(), b"preserve")


if __name__ == "__main__":
    unittest.main()
