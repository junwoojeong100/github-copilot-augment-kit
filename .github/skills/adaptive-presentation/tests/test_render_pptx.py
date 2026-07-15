from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import render_pptx  # noqa: E402


class RenderPptxTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)

    def test_parse_slides_validates_ranges(self):
        self.assertEqual(render_pptx.parse_slides("3,1-2", 3), [1, 2, 3])
        with self.assertRaises(ValueError):
            render_pptx.parse_slides("3-1", 3)
        with self.assertRaises(ValueError):
            render_pptx.parse_slides("4", 3)
        with self.assertRaises(ValueError):
            render_pptx.parse_slides(",", 3)

    def test_nonfinite_scale_is_rejected(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            render_pptx.positive_float("nan")

    def test_reusable_pdf_requires_matching_hash_and_path(self):
        deck = self.work_dir / "deck.pptx"
        pdf = self.work_dir / "deck.pdf"
        deck.write_bytes(b"deck")
        pdf.write_bytes(b"pdf")
        manifest = {
            "deck": str(deck.resolve()),
            "deck_sha256": render_pptx.sha256_file(deck),
            "pdf": str(pdf.resolve()),
            "pdf_sha256": render_pptx.sha256_file(pdf),
        }
        (self.work_dir / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        self.assertEqual(
            render_pptx.validate_reusable_pdf(
                deck.resolve(), pdf, manifest["deck_sha256"]
            ),
            pdf.resolve(),
        )
        deck.write_bytes(b"changed")
        with self.assertRaises(RuntimeError):
            render_pptx.validate_reusable_pdf(
                deck.resolve(), pdf, render_pptx.sha256_file(deck)
            )

    def test_reusable_pdf_rejects_changed_pdf_content(self):
        deck = self.work_dir / "deck.pptx"
        pdf = self.work_dir / "deck.pdf"
        deck.write_bytes(b"deck")
        pdf.write_bytes(b"pdf")
        (self.work_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "deck": str(deck.resolve()),
                    "deck_sha256": render_pptx.sha256_file(deck),
                    "pdf": str(pdf.resolve()),
                    "pdf_sha256": render_pptx.sha256_file(pdf),
                }
            ),
            encoding="utf-8",
        )
        pdf.write_bytes(b"partial")
        with self.assertRaises(RuntimeError):
            render_pptx.validate_reusable_pdf(
                deck.resolve(), pdf, render_pptx.sha256_file(deck)
            )

    def test_nonempty_unowned_output_directory_is_rejected(self):
        output = self.work_dir / "qa"
        output.mkdir()
        unrelated = output / "slide-01.jpg"
        unrelated.write_bytes(b"user data")
        with self.assertRaises(RuntimeError):
            render_pptx.claim_output_dir(output)
        self.assertEqual(unrelated.read_bytes(), b"user data")

    def test_parser_requires_session_output(self):
        parser = render_pptx.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["deck.pptx"])
        args = parser.parse_args(["deck.pptx", "--out", str(self.work_dir)])
        self.assertEqual(args.out, self.work_dir)


if __name__ == "__main__":
    unittest.main()
