from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from pptx import Presentation  # noqa: E402
from pptx.util import Inches  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

import audit_pptx  # noqa: E402


class RepairRiskTests(unittest.TestCase):
    def _deck_with_effectlst(self, count: int):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
        spPr = sp._element.spPr
        for _ in range(count):
            spPr.append(spPr.makeelement(qn("a:effectLst"), {}))
        return prs

    def test_flags_duplicate_effectlst(self):
        risks = audit_pptx.detect_repair_risks(self._deck_with_effectlst(2))
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]["slide"], 1)
        self.assertIn("effectLst", risks[0]["duplicate_children"])

    def test_single_effectlst_is_clean(self):
        self.assertEqual(audit_pptx.detect_repair_risks(self._deck_with_effectlst(1)), [])

    def test_no_effects_is_clean(self):
        self.assertEqual(audit_pptx.detect_repair_risks(self._deck_with_effectlst(0)), [])


if __name__ == "__main__":
    unittest.main()
