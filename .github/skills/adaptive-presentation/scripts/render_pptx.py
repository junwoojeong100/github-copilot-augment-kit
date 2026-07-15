#!/usr/bin/env python3
"""Render a PPTX to PDF and attachment-safe JPEG previews."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from tooling import resolve_soffice

OUTPUT_MARKER = ".adaptive-presentation-render"
OUTPUT_MARKER_CONTENT = "adaptive-presentation-render-v1\n"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def jpeg_quality(value: str) -> int:
    parsed = int(value)
    if not 1 <= parsed <= 95:
        raise argparse.ArgumentTypeError("JPEG quality must be between 1 and 95")
    return parsed


def output_dir_is_owned(path: Path) -> bool:
    marker = path / OUTPUT_MARKER
    try:
        return marker.read_text(encoding="utf-8") == OUTPUT_MARKER_CONTENT
    except OSError:
        return False


def claim_output_dir(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(path)
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()) and not output_dir_is_owned(path):
        raise RuntimeError(
            f"Refusing to use non-empty unowned output directory: {path}. "
            "Choose a dedicated session QA directory."
        )
    (path / OUTPUT_MARKER).write_text(
        OUTPUT_MARKER_CONTENT, encoding="utf-8"
    )


def find_soffice(explicit: Path | None) -> str:
    resolved = resolve_soffice(explicit)
    if resolved:
        return resolved
    raise FileNotFoundError(
        "LibreOffice soffice not found. Install LibreOffice or pass --soffice."
    )


def parse_slides(value: str | None, total: int) -> list[int]:
    if not value:
        return list(range(1, total + 1))

    selected: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            start_text, end_text = item.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start > end:
                raise ValueError(f"Invalid slide range: {item}")
            selected.update(range(start, end + 1))
        else:
            selected.add(int(item))

    if not selected:
        raise ValueError("No slides selected")
    invalid = sorted(number for number in selected if number < 1 or number > total)
    if invalid:
        raise ValueError(f"Slides out of range 1-{total}: {invalid}")
    return sorted(selected)


def convert_to_pdf(
    deck: Path, out_dir: Path, soffice: str, timeout_seconds: float
) -> Path:
    expected = out_dir / f"{deck.stem}.pdf"
    stage_dir = out_dir / f".render-stage-{uuid.uuid4().hex}"
    profile_dir = stage_dir / "soffice-profile"
    profile_dir.mkdir(parents=True)
    try:
        profile_uri = profile_dir.resolve().as_uri()
        try:
            result = subprocess.run(
                [
                    soffice,
                    f"-env:UserInstallation={profile_uri}",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(stage_dir),
                    str(deck),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                f"LibreOffice conversion timed out after {timeout_seconds:g} seconds"
            ) from error
        if result.returncode != 0:
            raise RuntimeError(
                "LibreOffice conversion failed:\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        staged_pdf = stage_dir / f"{deck.stem}.pdf"
        if not staged_pdf.is_file():
            raise RuntimeError(
                f"LibreOffice reported success but PDF was not created: {staged_pdf}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        staged_pdf.replace(expected)
        return expected
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_reusable_pdf(deck: Path, pdf: Path, deck_sha256: str) -> Path:
    reusable = pdf.expanduser().resolve()
    if not reusable.is_file():
        raise FileNotFoundError(reusable)

    manifest_path = reusable.parent / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(
            f"Reusable PDF requires its render manifest: {manifest_path}"
        )

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Invalid reusable PDF manifest: {manifest_path}") from error

    if manifest.get("deck_sha256") != deck_sha256:
        raise RuntimeError(
            "Reusable PDF does not match the current PPTX. "
            "Run a fresh render with --keep-pdf."
        )

    manifest_pdf = manifest.get("pdf")
    if not manifest_pdf or Path(manifest_pdf).expanduser().resolve() != reusable:
        raise RuntimeError(
            f"Reusable PDF is not the PDF recorded in {manifest_path}: {reusable}"
        )

    manifest_deck = manifest.get("deck")
    if manifest_deck and Path(manifest_deck).expanduser().resolve() != deck:
        raise RuntimeError(
            f"Reusable PDF manifest belongs to another deck: {manifest_deck}"
        )
    manifest_pdf_sha256 = manifest.get("pdf_sha256")
    if not manifest_pdf_sha256 or sha256_file(reusable) != manifest_pdf_sha256:
        raise RuntimeError(
            "Reusable PDF content does not match its manifest. "
            "Run a fresh render with --keep-pdf."
        )
    return reusable


def make_contact_sheet(
    slide_paths: list[tuple[int, Path]],
    output: Path,
    columns: int,
    thumb_width: int,
    thumb_height: int,
    image_format: str,
    quality: int,
    max_image_kb: int,
) -> None:
    label_height = 34
    cell_width = thumb_width + 20
    cell_height = thumb_height + label_height + 18
    rows = (len(slide_paths) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * cell_width, rows * cell_height),
        (225, 231, 236),
    )

    for index, (slide_number, path) in enumerate(slide_paths):
        with Image.open(path) as source:
            image = source.convert("RGB")
        image.thumbnail((thumb_width, thumb_height))
        cell = Image.new("RGB", (cell_width, cell_height), "white")
        cell.paste(
            image,
            ((cell_width - image.width) // 2, 10),
        )
        draw = ImageDraw.Draw(cell)
        draw.text(
            (12, thumb_height + 22),
            f"{slide_number:02d}",
            fill=(20, 40, 60),
        )
        sheet.paste(
            cell,
            ((index % columns) * cell_width, (index // columns) * cell_height),
        )

    save_image(
        sheet,
        output,
        image_format=image_format,
        quality=quality,
        max_image_kb=max_image_kb,
    )


def save_image(
    image: Image.Image,
    output: Path,
    image_format: str,
    quality: int,
    max_image_kb: int,
) -> None:
    if image_format == "png":
        image.save(output, format="PNG", optimize=True)
        return

    max_bytes = max_image_kb * 1024 if max_image_kb > 0 else 0
    candidate = image.convert("RGB")
    for candidate_quality in [quality, 76, 68, 60]:
        candidate.save(
            output,
            format="JPEG",
            quality=candidate_quality,
            optimize=True,
            progressive=True,
        )
        if not max_bytes or output.stat().st_size <= max_bytes:
            return

    while max_bytes and output.stat().st_size > max_bytes and candidate.width > 720:
        width = max(720, int(candidate.width * 0.86))
        height = max(1, round(candidate.height * width / candidate.width))
        candidate = candidate.resize((width, height), Image.Resampling.LANCZOS)
        candidate.save(
            output,
            format="JPEG",
            quality=64,
            optimize=True,
            progressive=True,
        )

    for candidate_quality in [52, 44, 36]:
        if not max_bytes or output.stat().st_size <= max_bytes:
            return
        candidate.save(
            output,
            format="JPEG",
            quality=candidate_quality,
            optimize=True,
            progressive=True,
        )

    if max_bytes and output.stat().st_size > max_bytes:
        raise RuntimeError(
            f"Could not compress preview below {max_image_kb} KiB: {output}"
        )


def render(args: argparse.Namespace) -> dict:
    deck = args.deck.expanduser().resolve()
    if not deck.is_file():
        raise FileNotFoundError(deck)
    deck_sha256 = sha256_file(deck)

    out_dir = args.out.expanduser().resolve()
    claim_output_dir(out_dir)
    for pattern in (
        "slide-*.jpg",
        "slide-*.png",
        "contact-*.jpg",
        "contact-*.png",
        ".manifest-*.tmp",
    ):
        for stale in out_dir.glob(pattern):
            stale.unlink()

    reusable_pdf = getattr(args, "reuse_pdf", None)
    reused_pdf = reusable_pdf is not None
    if reused_pdf:
        pdf = validate_reusable_pdf(deck, reusable_pdf, deck_sha256)
    else:
        soffice = find_soffice(args.soffice)
        pdf = convert_to_pdf(
            deck,
            out_dir,
            soffice,
            getattr(args, "conversion_timeout", 120.0),
        )

    manifest_path = out_dir / "manifest.json"
    manifest_path.unlink(missing_ok=True)
    if hasattr(fitz, "TOOLS") and hasattr(fitz.TOOLS, "mupdf_display_errors"):
        fitz.TOOLS.mupdf_display_errors(False)

    rendered: list[tuple[int, Path]] = []
    matrix = fitz.Matrix(args.scale, args.scale)
    image_format = getattr(args, "image_format", "jpg")
    quality = getattr(args, "quality", 82)
    max_image_kb = getattr(args, "max_image_kb", 900)
    suffix = ".png" if image_format == "png" else ".jpg"

    with fitz.open(pdf) as document:
        total_slides = len(document)
        selected = parse_slides(args.slides, total_slides)
        for slide_number in selected:
            page = document[slide_number - 1]
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            path = out_dir / f"slide-{slide_number:02d}{suffix}"
            image = Image.frombytes(
                "RGB",
                (pixmap.width, pixmap.height),
                pixmap.samples,
            )
            save_image(
                image,
                path,
                image_format=image_format,
                quality=quality,
                max_image_kb=max_image_kb,
            )
            rendered.append((slide_number, path))

    sheets: list[str] = []
    for group_number, start in enumerate(
        range(0, len(rendered), args.per_sheet), 1
    ):
        group = rendered[start : start + args.per_sheet]
        first, last = group[0][0], group[-1][0]
        numbers = [number for number, _ in group]
        is_contiguous = numbers == list(range(first, last + 1))
        if len(group) == 1:
            stem = f"contact-{first:02d}"
        elif is_contiguous:
            stem = f"contact-{first:02d}-{last:02d}"
        else:
            stem = f"contact-selected-{group_number:02d}"
        output = out_dir / f"{stem}{suffix}"
        make_contact_sheet(
            group,
            output,
            columns=args.columns,
            thumb_width=args.thumb_width,
            thumb_height=args.thumb_height,
            image_format=image_format,
            quality=quality,
            max_image_kb=max_image_kb,
        )
        sheets.append(str(output))

    keep_slide_images = getattr(args, "keep_slide_images", False)
    slide_images = [str(path) for _, path in rendered]
    if not keep_slide_images:
        for _, path in rendered:
            path.unlink()
        slide_images = []

    keep_pdf = getattr(args, "keep_pdf", False) or reused_pdf
    pdf_path = str(pdf) if keep_pdf else None
    if not keep_pdf:
        pdf.unlink()

    manifest = {
        "deck": str(deck),
        "deck_sha256": deck_sha256,
        "pdf": pdf_path,
        "pdf_sha256": sha256_file(pdf) if keep_pdf else None,
        "reused_pdf": reused_pdf,
        "total_slides": total_slides,
        "rendered_slides": selected,
        "slide_images": slide_images,
        "contact_sheets": sheets,
        "scale": args.scale,
        "image_format": image_format,
        "max_image_kb": max_image_kb,
        "kept_slide_images": keep_slide_images,
        "kept_pdf": keep_pdf,
        "contact_sheet_sizes_bytes": {
            path: Path(path).stat().st_size for path in sheets
        },
    }
    manifest_tmp = out_dir / f".manifest-{uuid.uuid4().hex}.tmp"
    manifest_tmp.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest_tmp.replace(manifest_path)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render PPTX slides to compact JPEG previews and contact sheets."
    )
    parser.add_argument("deck", type=Path, help="Path to the .pptx file")
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Session-isolated output directory",
    )
    parser.add_argument(
        "--soffice",
        type=Path,
        help="Explicit path to the LibreOffice soffice executable",
    )
    parser.add_argument(
        "--conversion-timeout",
        type=positive_float,
        default=120.0,
        metavar="SECONDS",
        help="LibreOffice conversion timeout (default: 120)",
    )
    parser.add_argument(
        "--reuse-pdf",
        type=Path,
        help=(
            "Reuse a PDF kept by a previous render. Its sibling manifest.json "
            "must match the current PPTX."
        ),
    )
    parser.add_argument(
        "--slides",
        help="Optional comma/range selection, e.g. 2,5-8,20",
    )
    parser.add_argument(
        "--scale",
        type=positive_float,
        default=1.25,
        help="PyMuPDF render scale (default: 1.25)",
    )
    parser.add_argument(
        "--per-sheet",
        type=positive_int,
        default=30,
        help="Maximum slides per contact sheet (default: 30)",
    )
    parser.add_argument(
        "--columns",
        type=positive_int,
        default=5,
        help="Contact-sheet columns (default: 5)",
    )
    parser.add_argument(
        "--thumb-width",
        type=positive_int,
        default=220,
        help="Contact-sheet thumbnail width (default: 220)",
    )
    parser.add_argument(
        "--thumb-height",
        type=positive_int,
        default=124,
        help="Contact-sheet thumbnail height (default: 124)",
    )
    parser.add_argument(
        "--image-format",
        choices=["jpg", "png"],
        default="jpg",
        help="Preview image format (default: jpg)",
    )
    parser.add_argument(
        "--quality",
        type=jpeg_quality,
        default=82,
        help="Initial JPEG quality (default: 82)",
    )
    parser.add_argument(
        "--max-image-kb",
        type=positive_int,
        default=900,
        help="Adaptive JPEG size budget per preview image in KiB (default: 900)",
    )
    parser.add_argument(
        "--keep-slide-images",
        action="store_true",
        help="Keep individual slide previews; default keeps contact sheets only",
    )
    parser.add_argument(
        "--keep-pdf",
        action="store_true",
        help="Keep the intermediate PDF; default deletes it after rendering",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = render(args)
    print(
        f"Rendered {len(manifest['rendered_slides'])}/"
        f"{manifest['total_slides']} slides"
    )
    if manifest["pdf"]:
        action = "reused" if manifest["reused_pdf"] else "kept"
        print(f"PDF ({action}): {manifest['pdf']}")
    else:
        print("PDF: discarded after rendering")
    for sheet in manifest["contact_sheets"]:
        size_kb = manifest["contact_sheet_sizes_bytes"][sheet] / 1024
        print(f"Contact sheet: {sheet} ({size_kb:.1f} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
