#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from pptx_compiler import (  # noqa: E402
    ContentItem,
    DesignDNA,
    Palette,
    Region,
    ShapeLanguage,
    SlideCompiler,
    SlideFrame,
    Source,
    Typography,
)


def design_for(style: str) -> DesignDNA:
    if style == "technical":
        return DesignDNA(
            name="Technical Signal",
            concept_words=("precise", "modular", "fast"),
            visual_metaphor="signal network",
            palette=Palette(
                canvas="F4F1EA",
                canvas_alt="0B1017",
                surface="FFFFFF",
                surface_alt="141D28",
                ink="111820",
                ink_inverse="F7FAFC",
                muted_ink="5D6B78",
                muted_inverse="AAB6C2",
                primary="E65F2B",
                secondary="1677C8",
                accent="7856D8",
                border="D6D9DC",
                border_inverse="2A3948",
                success="238A57",
                warning="C48316",
                danger="C43D55",
                preview="8A4EC7",
            ),
            typography=Typography(
                body_font="Apple SD Gothic Neo",
                display_font="Apple SD Gothic Neo",
                mono_font="Menlo",
            ),
            shapes=ShapeLanguage(corner_style="subtle", depth="flat"),
        )
    if style == "editorial":
        return DesignDNA(
            name="Editorial Journal",
            concept_words=("measured", "human", "clear"),
            visual_metaphor="annotated field journal",
            palette=Palette(
                canvas="F7F2E8",
                canvas_alt="2A1F1A",
                surface="FFFFFA",
                surface_alt="392C25",
                ink="241C18",
                ink_inverse="FFF9F1",
                muted_ink="6E625B",
                muted_inverse="CDBFB2",
                primary="B34A32",
                secondary="4F6D5A",
                accent="92734B",
                border="D8CCC0",
                border_inverse="57463B",
                success="3F7654",
                warning="A66A22",
                danger="A33B45",
                preview="76528A",
            ),
            typography=Typography(
                body_font="Apple SD Gothic Neo",
                display_font="Georgia",
                mono_font="Menlo",
                cover_pt=42,
                title_pt=30,
                body_pt=19,
            ),
            shapes=ShapeLanguage(
                corner_style="rounded",
                spacing="spacious",
                depth="border",
            ),
        )
    raise ValueError(f"Unknown style: {style}")


def build(output: Path, style: str) -> None:
    design = design_for(style)
    compiler = SlideCompiler(
        design,
        title="Reusable Slide Compiler Quickstart",
        subject="Same semantic deck compiled with explicit Design DNA",
    )

    cover = compiler.begin_slide(
        SlideFrame(
            title="",
            background_role="canvas_alt",
            inverse=True,
            show_header=False,
            show_footer=False,
        ),
        family="cover",
        variant="split",
    )
    cover.text(
        "kicker",
        design.name.upper(),
        role="label",
        color="primary",
        bold=True,
    )
    cover.text(
        "headline",
        "Reusable mechanics.\nAdaptive design.",
        role="cover",
        color="ink_inverse",
        background="canvas_alt",
        bold=True,
        valign=MSO_ANCHOR.MIDDLE,
    )
    cover.text(
        "subtitle",
        "The compiler receives a new Design DNA for every deck.",
        role="body",
        color="muted_inverse",
        background="canvas_alt",
    )
    cover.box("visual", fill="surface_alt", line="primary")
    cover.text(
        cover.region("visual", inset=0.55),
        "SPEC\n+\nDNA\n→\nPPTX",
        role="metric",
        color="ink_inverse",
        bold=True,
        align=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE,
    )

    statement = compiler.begin_slide(
        SlideFrame(
            title="The compiler owns mechanics, not visual identity",
            section="CONTRACT",
            number=2,
            source=Source(
                "Adaptive Presentation",
                "Slide Compiler contract",
                "2026-07-15",
            ),
        ),
        family="statement",
        variant="hero-left",
    )
    statement.text(
        "hero",
        "Deck Spec\n+\nDesign DNA\n+\nSemantic Blueprint",
        role="metric",
        color="primary",
        bold=True,
        valign=MSO_ANCHOR.MIDDLE,
    )
    statement.box("support", fill="surface", line="secondary")
    statement.text(
        statement.region("support", inset=0.22),
        "Reusable\n• geometry safety\n• text fitting\n• sources\n• validation",
        role="secondary",
        color="ink",
        bold=True,
    )
    statement.text(
        "evidence",
        "No default palette. No fixed card template.",
        role="body",
        color="danger",
        bold=True,
        align=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE,
    )

    comparison = compiler.begin_slide(
        SlideFrame(
            title="Reuse implementation while regenerating the visual system",
            section="BOUNDARY",
            number=3,
        ),
        family="comparison",
        variant="axis",
    )
    comparison.comparison(
        "REUSE",
        ["PPTX primitives", "Layout regions", "Text-fit checks", "QA metadata"],
        "REGENERATE",
        ["Palette", "Typography", "Metaphor", "Section rhythm"],
    )

    process = compiler.begin_slide(
        SlideFrame(
            title="A semantic flow can be rendered through any Design DNA",
            section="COMPILE",
            number=4,
        ),
        family="process",
        variant="rail",
        slots=4,
    )
    process.process(
        [
            ContentItem("SPEC", "Lock conclusion and evidence", "secondary"),
            ContentItem("DNA", "Derive visual language", "accent"),
            ContentItem("BUILD", "Compile regions and vectors", "primary"),
            ContentItem("QA", "Audit, render, repair", "success"),
        ]
    )

    roadmap = compiler.begin_slide(
        SlideFrame(
            title="Future deck scripts become smaller and more consistent",
            section="RESULT",
            number=5,
        ),
        family="roadmap",
        variant="gates",
        slots=4,
    )
    roadmap.roadmap(
        [
            ContentItem("Research", "Fact Ledger remains deck-specific.", "secondary"),
            ContentItem("Design", "Design DNA remains deck-specific.", "accent"),
            ContentItem("Compile", "Mechanics are imported once.", "primary"),
            ContentItem("Verify", "Full render QA remains mandatory.", "success"),
        ]
    )

    compiler.save(
        output,
        expected_slides=5,
        min_layout_families=5,
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
