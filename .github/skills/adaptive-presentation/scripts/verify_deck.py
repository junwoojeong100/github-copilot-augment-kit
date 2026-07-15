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


def select_risk_slides(report: dict, count: int) -> list[int]:
    values = report["text_chars_per_slide"]["values"]
    maximum = max(max(values, default=0), 1)
    scores = {
        slide: (characters / maximum) * 5
        for slide, characters in enumerate(values, 1)
    }

    def add(items: list[dict], weight: float) -> None:
        for item in items:
            slide = int(item["slide"])
            scores[slide] = scores.get(slide, 0) + weight

    add(report.get("small_text_body_candidates", []), 5)
    add(report.get("small_text_label_candidates", []), 1)
    add(report.get("title_risks", []), 10)
    add(report.get("group_shapes", []), 3)
    add(report.get("unexpected_out_of_bounds", []), 20)

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
        fail_small_text=args.fail_small_text
        or (args.strict and not args.allow_small_text),
        fail_title_risks=args.fail_title_risks or args.strict,
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
    qa_dir, detail_dir = prepare_output_dirs(out)
    audit_path = qa_dir / "audit.json"

    audit_args = audit_namespace(args, audit_path)
    render_args = render_namespace(deck, qa_dir)
    with ThreadPoolExecutor(max_workers=2) as executor:
        audit_future = executor.submit(audit_pptx.audit, audit_args)
        render_future = executor.submit(render_pptx.render, render_args)
        audit_report, audit_failures = audit_future.result()
        render_manifest = render_future.result()

    audit_path.write_text(
        json.dumps(audit_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with zipfile.ZipFile(deck) as archive:
        corrupt_member = archive.testzip()
    zip_integrity = "ok" if corrupt_member is None else corrupt_member

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
    report_path = out / "verification-report.json"
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
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    return qa_dir, detail_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify a PPTX with audit, full render, risk slides, and ZIP integrity."
    )
    parser.add_argument("deck", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-slides", type=int)
    parser.add_argument("--risk-count", type=int, default=3)
    parser.add_argument("--risk-slides")
    parser.add_argument("--allow-bleed", default="")
    parser.add_argument("--bounds-tolerance", type=float, default=0.02)
    parser.add_argument("--min-body-pt", type=float, default=14.0)
    parser.add_argument("--min-title-pt", type=float, default=26.0)
    parser.add_argument("--footer-top", type=float, default=6.9)
    parser.add_argument("--min-small-text-chars", type=int, default=10)
    parser.add_argument("--fail-small-text", action="store_true")
    parser.add_argument(
        "--allow-small-text",
        action="store_true",
        help="Under --strict, allow likely body text below --min-body-pt.",
    )
    parser.add_argument("--fail-title-risks", action="store_true")
    parser.add_argument("--strict", action="store_true")
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
    return 0 if result["passed"] or not args.strict else 1


if __name__ == "__main__":
    sys.exit(main())
