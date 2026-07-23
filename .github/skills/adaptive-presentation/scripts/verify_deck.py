#!/usr/bin/env python3
"""Run structural audit, full render, risk-slide render, and ZIP checks."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import audit_pptx
import render_pptx
import rendered_overlap
from tooling import path_is_within, paths_collide


def select_risk_slides(report: dict, count: int) -> list[int]:
    values = report["text_chars_per_slide"]["values"]
    maximum = max(max(values, default=0), 1)
    scores = {
        slide: (characters / maximum) * 5
        for slide, characters in enumerate(values, 1)
    }

    def add(items: list[dict], weight: float) -> None:
        for item in items:
            if item.get("slide") is None:
                continue
            slide = int(item["slide"])
            scores[slide] = scores.get(slide, 0) + weight

    add(report.get("small_text_body_candidates", []), 5)
    add(report.get("small_text_label_candidates", []), 1)
    add(report.get("title_risks", []), 10)
    add(report.get("title_size_inconsistencies", []), 12)
    add(report.get("group_shapes", []), 3)
    add(report.get("unsized_runs", []), 5)
    add(report.get("empty_text_frames", []), 1)
    add(report.get("ooxml_repair_risks", []), 30)
    add(report.get("unexpected_out_of_bounds", []), 20)
    add(report.get("overlap_candidates", []), 20)
    add(report.get("rendered_text_overlaps", []), 30)
    add(report.get("rendered_text_overflow_candidates", []), 4)
    add(
        [
            {"slide": slide}
            for slide in report.get("missing_required_source_slides", [])
        ],
        15,
    )

    return [
        slide
        for slide, _ in sorted(
            scores.items(),
            key=lambda item: (-item[1], item[0]),
        )[: max(0, count)]
    ]


def parse_slide_list(value: str | None) -> list[int] | None:
    if not value:
        return None
    return render_pptx.parse_slides(value, 10_000)


def audit_namespace(args: argparse.Namespace, report_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        deck=args.deck,
        expected_slides=args.expected_slides,
        allow_bleed=audit_pptx.parse_slide_set(args.allow_bleed)
        if args.allow_bleed
        else set(),
        bounds_tolerance=args.bounds_tolerance,
        min_body_pt=args.min_body_pt,
        min_title_pt=args.min_title_pt,
        footer_top=args.footer_top,
        min_small_text_chars=args.min_small_text_chars,
        allow_small_text=audit_pptx.parse_slide_set(args.allow_small_text)
        if args.allow_small_text
        else set(),
        allow_overlap=audit_pptx.parse_slide_set(args.allow_overlap)
        if args.allow_overlap
        else set(),
        allow_title_size=audit_pptx.parse_slide_set(args.allow_title_size)
        if args.allow_title_size
        else set(),
        require_sources=audit_pptx.parse_slide_set(args.require_sources)
        if args.require_sources
        else set(),
        title_size_tolerance_pt=args.title_size_tolerance_pt,
        fail_small_text=args.fail_small_text
        or args.strict,
        fail_unsized_runs=args.fail_unsized_runs or args.strict,
        fail_title_risks=args.fail_title_risks or args.strict,
        fail_title_consistency=args.fail_title_consistency or args.strict,
        fail_overlaps=args.fail_overlaps or args.strict,
        json=report_path,
        strict=args.strict,
    )


def render_namespace(
    deck: Path,
    out: Path,
    *,
    reuse_pdf: Path | None = None,
    slides: str | None = None,
    keep_slide_images: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        deck=deck,
        out=out,
        soffice=None,
        conversion_timeout=120.0,
        reuse_pdf=reuse_pdf,
        slides=slides,
        scale=1.25,
        per_sheet=30,
        columns=5,
        thumb_width=220,
        thumb_height=124,
        image_format="jpg",
        quality=82,
        max_image_kb=900,
        keep_slide_images=keep_slide_images,
        keep_pdf=True,
    )


def verify(args: argparse.Namespace) -> dict:
    deck = args.deck.expanduser().resolve()
    out = args.out.expanduser().resolve()
    report_path = out / "verification-report.json"
    if paths_collide(deck, report_path):
        raise ValueError("Verification report must not overwrite or alias the input deck")
    for candidate in (out / "qa", out / "qa-detail"):
        resolved_candidate = candidate.resolve()
        if path_is_within(deck, resolved_candidate):
            raise ValueError(
                f"Input deck must be outside the managed QA directory: {candidate}"
            )
    qa_dir, detail_dir = prepare_output_dirs(out)
    audit_path = qa_dir / "audit.json"

    audit_args = audit_namespace(args, audit_path)
    render_args = render_namespace(deck, qa_dir)
    with ThreadPoolExecutor(max_workers=2) as executor:
        audit_future = executor.submit(audit_pptx.audit, audit_args)
        render_future = executor.submit(render_pptx.render, render_args)
        audit_report, audit_failures = audit_future.result()
        render_manifest = render_future.result()

    with zipfile.ZipFile(deck) as archive:
        corrupt_member = archive.testzip()
    zip_integrity = "ok" if corrupt_member is None else corrupt_member
    if render_manifest["total_slides"] != audit_report["slides"]:
        audit_failures.append(
            "Rendered PDF slide count differs from PPTX: "
            f"{render_manifest['total_slides']} vs {audit_report['slides']}"
        )
    rendered_pdf = render_manifest.get("pdf")
    if not rendered_pdf:
        raise RuntimeError("Verification render did not retain its PDF")
    rendered_findings = rendered_overlap.audit_rendered_text(
        deck,
        Path(rendered_pdf),
        allowed_slides=audit_pptx.parse_slide_set(args.allow_overlap)
        if args.allow_overlap
        else set(),
    )
    audit_report.update(rendered_findings)
    if (
        args.fail_overlaps or args.strict
    ) and rendered_findings["unexpected_rendered_text_overlaps"]:
        audit_failures.append(
            f"{len(rendered_findings['unexpected_rendered_text_overlaps'])} "
            "rendered text overlap(s) require repair or --allow-overlap review"
        )
    audit_path.write_text(
        json.dumps(audit_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    selected = parse_slide_list(args.risk_slides)
    if selected is None:
        selected = select_risk_slides(audit_report, args.risk_count)
    invalid = [
        slide
        for slide in selected
        if slide < 1 or slide > render_manifest["total_slides"]
    ]
    if invalid:
        raise ValueError(
            f"Risk slides out of range 1-{render_manifest['total_slides']}: {invalid}"
        )

    detail_manifest = None
    if selected:
        pdf = Path(render_manifest["pdf"])
        detail_manifest = render_pptx.render(
            render_namespace(
                deck,
                detail_dir,
                reuse_pdf=pdf,
                slides=",".join(str(slide) for slide in selected),
                keep_slide_images=True,
            )
        )

    passed = not audit_failures and corrupt_member is None
    result = {
        "deck": str(deck),
        "passed": passed,
        "audit_failures": audit_failures,
        "audit": audit_report,
        "full_render": render_manifest,
        "risk_slides": selected,
        "detail_render": detail_manifest,
        "zip_integrity": zip_integrity,
    }
    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    result["report"] = str(report_path)
    return result


def prepare_output_dirs(out: Path) -> tuple[Path, Path]:
    qa_dir = out / "qa"
    detail_dir = out / "qa-detail"
    for path in (qa_dir, detail_dir):
        if path.exists():
            if path.is_symlink():
                raise RuntimeError(f"Refusing symlinked QA directory: {path}")
            if not path.is_dir():
                raise RuntimeError(f"Refusing non-directory QA path: {path}")
            if any(path.iterdir()) and not render_pptx.output_dir_is_owned(path):
                raise RuntimeError(
                    f"Refusing to replace non-empty unowned QA directory: {path}"
                )
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    return qa_dir, detail_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify a PPTX with audit, full render, risk slides, and ZIP integrity."
    )
    parser.add_argument("deck", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-slides", type=audit_pptx.positive_int)
    parser.add_argument("--risk-count", type=render_pptx.positive_int, default=3)
    parser.add_argument("--risk-slides")
    parser.add_argument("--allow-bleed", default="")
    parser.add_argument(
        "--bounds-tolerance", type=audit_pptx.nonnegative_float, default=0.02
    )
    parser.add_argument("--min-body-pt", type=audit_pptx.positive_float, default=13.0)
    parser.add_argument("--min-title-pt", type=audit_pptx.positive_float, default=26.0)
    parser.add_argument("--footer-top", type=audit_pptx.nonnegative_float, default=6.9)
    parser.add_argument(
        "--min-small-text-chars", type=audit_pptx.positive_int, default=10
    )
    parser.add_argument("--fail-small-text", action="store_true")
    parser.add_argument(
        "--allow-small-text",
        default="",
        metavar="SLIDES",
        help="Reviewed slides allowed sub-minimum body text, e.g. 4,8-9.",
    )
    parser.add_argument(
        "--allow-overlap",
        default="",
        metavar="SLIDES",
        help="Reviewed slides allowed intentional geometry/render overlap, e.g. 4,8-9.",
    )
    parser.add_argument(
        "--allow-title-size",
        default="",
        metavar="SLIDES",
        help="Reviewed slides allowed a different content-title size, e.g. 6,12.",
    )
    parser.add_argument(
        "--require-sources",
        default="",
        metavar="SLIDES",
        help="Slides with factual claims that must contain a Source:/출처: footer.",
    )
    parser.add_argument(
        "--title-size-tolerance-pt",
        type=audit_pptx.nonnegative_float,
        default=0.5,
        help="Allowed content-title size variation in points (default: 0.5).",
    )
    parser.add_argument("--fail-unsized-runs", action="store_true")
    parser.add_argument("--fail-title-risks", action="store_true")
    parser.add_argument("--fail-title-consistency", action="store_true")
    parser.add_argument("--fail-overlaps", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable typography, title, overlap, and configured source failures",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = verify(args)
    print(
        f"Verification {'PASS' if result['passed'] else 'FAIL'} | "
        f"slides={result['audit']['slides']} | "
        f"risk={','.join(map(str, result['risk_slides'])) or 'none'}"
    )
    print(f"Report: {result['report']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
