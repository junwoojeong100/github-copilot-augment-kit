from __future__ import annotations

import sys
import unittest
from pathlib import Path

import fitz


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from rendered_overlap import (  # noqa: E402
    assign_spans_to_shapes,
    detect_span_overflow,
    detect_span_overlaps,
)


class RenderedOverlapTests(unittest.TestCase):
    def test_assignment_uses_text_and_nearest_frame(self):
        shapes = [
            {
                "shape": "left",
                "text": "01",
                "normalized": "01",
                "rect": fitz.Rect(0, 0, 50, 50),
            },
            {
                "shape": "right",
                "text": "01",
                "normalized": "01",
                "rect": fitz.Rect(100, 0, 150, 50),
            },
        ]
        spans = [
            {
                "text": "01",
                "normalized": "01",
                "size_pt": 20,
                "rect": fitz.Rect(110, 10, 140, 40),
            }
        ]
        assigned, unmapped = assign_spans_to_shapes(spans, shapes)
        self.assertEqual(unmapped, 0)
        self.assertEqual(assigned[0]["shape_index"], 1)

    def test_distinct_text_frames_with_rendered_collision_are_reported(self):
        shapes = [
            {
                "shape": "first",
                "text": "runtime plane",
                "normalized": "runtimeplane",
                "rect": fitz.Rect(0, 0, 100, 30),
            },
            {
                "shape": "second",
                "text": "decision",
                "normalized": "decision",
                "rect": fitz.Rect(70, 25, 150, 55),
            },
        ]
        spans = [
            {
                "shape_index": 0,
                "text": "plane",
                "normalized": "plane",
                "size_pt": 20,
                "rect": fitz.Rect(60, 20, 100, 42),
            },
            {
                "shape_index": 1,
                "text": "decision",
                "normalized": "decision",
                "size_pt": 14,
                "rect": fitz.Rect(80, 30, 140, 48),
            },
        ]
        overlaps = detect_span_overlaps(spans, shapes)
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0]["shape_a"], "first")

        spans[1]["shape_index"] = 0
        self.assertEqual(detect_span_overlaps(spans, shapes), [])

    def test_rendered_spill_is_reported_separately(self):
        shapes = [
            {
                "shape": "wrapped",
                "text": "runtime plane",
                "normalized": "runtimeplane",
                "rect": fitz.Rect(0, 0, 100, 30),
            }
        ]
        spans = [
            {
                "shape_index": 0,
                "text": "runtime",
                "normalized": "runtime",
                "size_pt": 20,
                "rect": fitz.Rect(0, 0, 90, 22),
            },
            {
                "shape_index": 0,
                "text": "plane",
                "normalized": "plane",
                "size_pt": 20,
                "rect": fitz.Rect(20, 24, 65, 48),
            },
        ]
        findings = detect_span_overflow(spans, shapes, tolerance_pt=4)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["overflow_edges_pt"]["bottom"], 18)


if __name__ == "__main__":
    unittest.main()
