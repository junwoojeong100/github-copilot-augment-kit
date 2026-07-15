#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


EXAMPLES_DIR = Path(__file__).resolve().parent
SKILL_ROOT = EXAMPLES_DIR.parent
sys.path.insert(0, str(EXAMPLES_DIR))
sys.path.insert(0, str(SKILL_ROOT))

from compiler_quickstart import design_for  # noqa: E402
from pptx_compiler import (  # noqa: E402
    DeckRecipe,
    RecipeAssembler,
    SlideRecipe,
    Source,
)


def recipe() -> DeckRecipe:
    return DeckRecipe(
        title="Adaptive Deck Recipe Quickstart",
        subject="Semantic content compiled through explicit Design DNA",
        expected_slides=5,
        min_layout_families=5,
        slides=(
            SlideRecipe(
                id="cover",
                title="",
                semantic_type="cover",
                component="cover",
                emphasis="hero",
                content={
                    "kicker": "DECK RECIPE",
                    "headline": "Semantic content.\nAdaptive design.",
                    "subtitle": "No palette, font, or fixed coordinates live in this recipe.",
                    "visual_text": "RECIPE\n+\nDNA\n→\nPPTX",
                    "meta": "Same recipe · two visual systems",
                },
            ),
            SlideRecipe(
                id="contract",
                title="Recipe stores meaning while Design DNA controls appearance",
                semantic_type="statement",
                component="statement",
                section="CONTRACT",
                source_refs=("compiler",),
                content={
                    "hero": "CONTENT\n≠\nDESIGN",
                    "support": "Conclusion · evidence · relationship · blueprint intent",
                    "evidence": "NO HEX · NO FONT · NO COORDINATES",
                },
            ),
            SlideRecipe(
                id="boundary",
                title="Reusable production mechanics do not require a reusable look",
                semantic_type="comparison",
                component="comparison",
                section="BOUNDARY",
                content={
                    "left_title": "RECIPE",
                    "left_items": [
                        "Conclusion and takeaway",
                        "Semantic component",
                        "Source references",
                        "Optional layout override",
                    ],
                    "right_title": "DESIGN DNA",
                    "right_items": [
                        "Palette and typography",
                        "Shape and spacing",
                        "Visual metaphor",
                        "Section rhythm",
                    ],
                    "axis": "COMPILED\nTOGETHER",
                },
            ),
            SlideRecipe(
                id="flow",
                title="Adaptive selection avoids repeating the same layout family",
                semantic_type="process",
                component="process",
                section="ASSEMBLE",
                slots=4,
                content={
                    "items": [
                        {"title": "SPEC", "detail": "Lock the message", "color_role": "secondary"},
                        {"title": "SELECT", "detail": "Score layout candidates", "color_role": "accent"},
                        {"title": "COMPILE", "detail": "Apply Design DNA", "color_role": "primary"},
                        {"title": "VERIFY", "detail": "Audit and render", "color_role": "success"},
                    ]
                },
            ),
            SlideRecipe(
                id="status",
                title="Preflight and QA remain explicit release gates",
                semantic_type="status",
                component="status_ledger",
                section="VERIFY",
                density="high",
                content={
                    "headers": ["GATE", "MEASURE", "FAIL WHEN"],
                    "rows": [
                        ["Recipe", "No visual tokens", "Design leaks into content"],
                        ["Compiler", "Bounds · fit · contrast", "PPTX is structurally unsafe"],
                        ["Audit", "Fonts · density · integrity", "External structure fails"],
                        ["Render", "All slides + risks", "Visual defects remain"],
                    ],
                    "column_weights": [1.2, 2.0, 2.8],
                },
            ),
        ),
    )


def build(output: Path, style: str) -> None:
    sources = {
        "compiler": Source(
            "Adaptive Presentation",
            "Deck Recipe contract",
            "2026-07-15",
        )
    }
    assembler = RecipeAssembler(design_for(style), sources=sources)
    assembler.compile_to(
        recipe(),
        output,
        report_path=output.with_suffix(".compiler.json"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=["technical", "editorial"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.out.resolve(), args.style)
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
