#!/usr/bin/env python3
"""Render a PPTX to PDF and attachment-safe JPEG previews."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


SOFFICE_CANDIDATES = [
    "/opt/homebrew/bin/soffice",
    "/usr/local/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice(explicit: Path | None) -> str:
    if explicit:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return str(path)

    from_path = shutil.which("soffice")
    if from_path:
        return from_path

    for candidate in SOFFICE_CANDIDATES:
        if Path(candidate).is_file():
            return candidate

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

    invalid = sorted(number for number in selected if number < 1 or number > total)
    if invalid:
        raise ValueError(f"Slides out of range 1-{total}: {invalid}")
    return sorted(selected)


def convert_to_pdf(deck: Path, out_dir: Path, soffice: str) -> Path:
    expected = out_dir / f"{deck.stem}.pdf"
    if expected.exists():
        expected.unlink()

    with tempfile.TemporaryDirectory(prefix="copilot-soffice-") as profile_dir:
        profile_uri = Path(profile_dir).resolve().as_uri()
        result = subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={profile_uri}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(out_dir),
                str(deck),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        raise RuntimeError(
            "LibreOffice conversion failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    if not expected.is_file():
        raise RuntimeError(
            f"LibreOffice reported success but PDF was not created: {expected}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return expected


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
        image = Image.open(path).convert("RGB")
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
        candidate = candidate.resize(
            (
                max(720, int(candidate.width * 0.86)),
                max(405, int(candidate.height * 0.86)),
            ),
            Image.Resampling.LANCZOS,
        )
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

    out_dir = (
        args.out.expanduser().resolve()
        if args.out
        else Path(tempfile.mkdtemp(prefix=f"{deck.stem}-qa-"))
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_soffice(args.soffice)
    pdf = convert_to_pdf(deck, out_dir, soffice)

    if hasattr(fitz, "TOOLS") and hasattr(fitz.TOOLS, "mupdf_display_errors"):
        fitz.TOOLS.mupdf_display_errors(False)

    document = fitz.open(pdf)
    total_slides = len(document)
    selected = parse_slides(args.slides, total_slides)
    rendered: list[tuple[int, Path]] = []
    matrix = fitz.Matrix(args.scale, args.scale)
    image_format = getattr(args, "image_format", "jpg")
    quality = getattr(args, "quality", 82)
    max_image_kb = getattr(args, "max_image_kb", 900)
    suffix = ".png" if image_format == "png" else ".jpg"

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

    document.close()
    keep_pdf = getattr(args, "keep_pdf", False)
    pdf_path = str(pdf)
    if not keep_pdf:
        pdf.unlink()
        pdf_path = None

    manifest = {
        "deck": str(deck),
        "pdf": pdf_path,
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
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render PPTX slides to compact JPEG previews and contact sheets."
    )
    parser.add_argument("deck", type=Path, help="Path to the .pptx file")
    parser.add_argument(
        "--out",
        type=Path,
        help="Output directory (default: unique system temporary directory)",
    )
    parser.add_argument(
        "--soffice",
        type=Path,
        help="Explicit path to the LibreOffice soffice executable",
    )
    parser.add_argument(
        "--slides",
        help="Optional comma/range selection, e.g. 2,5-8,20",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.25,
        help="PyMuPDF render scale (default: 1.25)",
    )
    parser.add_argument(
        "--per-sheet",
        type=int,
        default=30,
        help="Maximum slides per contact sheet (default: 30)",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=5,
        help="Contact-sheet columns (default: 5)",
    )
    parser.add_argument(
        "--thumb-width",
        type=int,
        default=220,
        help="Contact-sheet thumbnail width (default: 220)",
    )
    parser.add_argument(
        "--thumb-height",
        type=int,
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
        type=int,
        default=82,
        help="Initial JPEG quality (default: 82)",
    )
    parser.add_argument(
        "--max-image-kb",
        type=int,
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
        print(f"PDF: {manifest['pdf']}")
    else:
        print("PDF: discarded after rendering")
    for sheet in manifest["contact_sheets"]:
        size_kb = manifest["contact_sheet_sizes_bytes"][sheet] / 1024
        print(f"Contact sheet: {sheet} ({size_kb:.1f} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
