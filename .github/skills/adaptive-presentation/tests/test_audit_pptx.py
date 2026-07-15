from __future__ import annotations

import argparse
import sys
import subprocess
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from pptx import Presentation  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

import audit_pptx  # noqa: E402


def audit_args(deck: Path, **overrides) -> Namespace:
    values = {
        "deck": deck,
        "expected_slides": 1,
        "allow_bleed": set(),
        "allow_small_text": set(),
        "bounds_tolerance": 0.02,
        "min_body_pt": 16.0,
        "min_title_pt": 26.0,
        "footer_top": 6.9,
        "min_small_text_chars": 10,
        "fail_small_text": True,
        "fail_unsized_runs": True,
        "fail_title_risks": True,
        "json": None,
        "strict": True,
    }
    values.update(overrides)
    return Namespace(**values)


class AuditPptxTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)

    def make_deck(self, body_size: float = 16.0, explicit_body_size: bool = True) -> Path:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        title = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(10), Inches(0.7))
        title.text = "Conclusion title"
        title.text_frame.paragraphs[0].runs[0].font.size = Pt(30)
        body = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(1))
        body.text = "This body sentence is long enough to be classified."
        if explicit_body_size:
            body.text_frame.paragraphs[0].runs[0].font.size = Pt(body_size)
        slide.shapes.add_shape(1, Inches(1), Inches(4), Inches(2), Inches(1))
        out = self.work_dir / "deck.pptx"
        prs.save(out)
        return out

    def test_strict_typography_passes_at_sixteen_points(self):
        report, failures = audit_pptx.audit(audit_args(self.make_deck()))
        self.assertEqual(failures, [])
        self.assertEqual(report["empty_text_frames"], [])

    def test_nonfinite_thresholds_are_rejected(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            audit_pptx.positive_float("nan")
        with self.assertRaises(argparse.ArgumentTypeError):
            audit_pptx.nonnegative_float("inf")

    def test_small_text_exception_is_slide_scoped(self):
        deck = self.make_deck(body_size=15)
        _, failures = audit_pptx.audit(audit_args(deck))
        self.assertTrue(any("below 16.0 pt" in item for item in failures))
        report, failures = audit_pptx.audit(
            audit_args(deck, allow_small_text={1})
        )
        self.assertEqual(failures, [])
        self.assertTrue(report["small_text_body_candidates"][0]["allowed"])

    def test_fractional_size_below_threshold_fails_before_rounding(self):
        _, failures = audit_pptx.audit(
            audit_args(self.make_deck(body_size=15.99))
        )
        self.assertTrue(any("below 16.0 pt" in item for item in failures))

    def test_split_runs_cannot_bypass_body_length_threshold(self):
        deck = self.make_deck()
        prs = Presentation(deck)
        paragraph = prs.slides[0].shapes[1].text_frame.paragraphs[0]
        paragraph.clear()
        for value in ("Split ", "body ", "across ", "short ", "runs."):
            run = paragraph.add_run()
            run.text = value
            run.font.size = Pt(15)
        prs.save(deck)

        report, failures = audit_pptx.audit(audit_args(deck))
        self.assertGreaterEqual(len(report["small_text_body_candidates"]), 1)
        self.assertTrue(any("below 16.0 pt" in item for item in failures))

    def test_unsized_nonempty_run_fails(self):
        _, failures = audit_pptx.audit(
            audit_args(self.make_deck(explicit_body_size=False))
        )
        self.assertTrue(any("no explicit font size" in item for item in failures))

    def test_cover_requires_title_sized_text(self):
        deck = self.make_deck()
        prs = Presentation(deck)
        prs.slides[0].shapes[0].text_frame.paragraphs[0].runs[0].font.size = Pt(20)
        prs.save(deck)
        report, failures = audit_pptx.audit(audit_args(deck))
        self.assertEqual(report["title_risks"][0]["slide"], 1)
        self.assertTrue(any("no text at or above" in item for item in failures))

    def test_table_cell_text_is_audited(self):
        deck = self.make_deck()
        prs = Presentation(deck)
        slide = prs.slides[0]
        table = slide.shapes.add_table(
            1, 1, Inches(1), Inches(4), Inches(8), Inches(1)
        ).table
        run = table.cell(0, 0).text_frame.paragraphs[0].add_run()
        run.text = "Table body content that must meet the same size threshold."
        run.font.size = Pt(15)
        prs.save(deck)

        report, failures = audit_pptx.audit(audit_args(deck))
        candidates = report["small_text_body_candidates"]
        self.assertTrue(any("cell 1,1" in item["shape"] for item in candidates))
        self.assertTrue(any("below 16.0 pt" in item for item in failures))

    def test_text_table_cannot_use_decorative_bleed_exception(self):
        deck = self.make_deck()
        prs = Presentation(deck)
        table = prs.slides[0].shapes.add_table(
            1, 1, Inches(12.5), Inches(4), Inches(2), Inches(1)
        ).table
        table.cell(0, 0).text = "Visible text"
        prs.save(deck)

        report, failures = audit_pptx.audit(
            audit_args(deck, allow_bleed={1})
        )
        self.assertEqual(len(report["unexpected_out_of_bounds"]), 1)
        self.assertTrue(any("without allow-bleed" in item for item in failures))

    def test_json_report_cannot_alias_input_deck(self):
        deck = self.make_deck()
        alias = self.work_dir / "report.json"
        alias.hardlink_to(deck)
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPTS_DIR / "audit_pptx.py"),
                str(deck),
                "--json",
                str(alias),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(zipfile.is_zipfile(deck))


if __name__ == "__main__":
    unittest.main()
