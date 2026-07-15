from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import ImageFont


@dataclass(frozen=True)
class ResolvedFont:
    path: str
    index: int = 0
    synthetic_bold: bool = False


class FontMetrics:
    """Measures rendered text width with installed fonts when available."""

    def __init__(self, dpi: int = 96):
        self.dpi = dpi
        self._resolved: dict[tuple[str, bool], ResolvedFont | None] = {}
        self._fonts: dict[tuple[str, int, int], ImageFont.FreeTypeFont] = {}

    def resolve(
        self,
        family_or_path: str,
        *,
        bold: bool = False,
    ) -> ResolvedFont | None:
        key = (family_or_path, bold)
        if key in self._resolved:
            return self._resolved[key]

        direct = Path(family_or_path).expanduser()
        if direct.is_file():
            resolved = ResolvedFont(
                str(direct.resolve()),
                synthetic_bold=bold,
            )
            self._resolved[key] = resolved
            return resolved

        try:
            ImageFont.truetype(family_or_path, 12)
        except OSError:
            pass
        else:
            resolved = ResolvedFont(family_or_path, synthetic_bold=bold)
            self._resolved[key] = resolved
            return resolved

        resolved = self._resolve_with_fontconfig(family_or_path, bold=bold)
        if resolved is None:
            resolved = self._resolve_from_font_directories(
                family_or_path,
                bold=bold,
            )
        self._resolved[key] = resolved
        return resolved

    def measure_points(
        self,
        text: str,
        family_or_path: str,
        size_pt: float,
        *,
        bold: bool = False,
    ) -> float | None:
        resolved = self.resolve(family_or_path, bold=bold)
        if resolved is None:
            return None
        pixel_size = max(1, round(size_pt * self.dpi / 72))
        key = (resolved.path, resolved.index, pixel_size)
        try:
            font = self._fonts.get(key)
            if font is None:
                font = ImageFont.truetype(
                    resolved.path,
                    pixel_size,
                    index=resolved.index,
                )
                self._fonts[key] = font
            measured = float(font.getlength(text)) * 72 / self.dpi
            return measured * (1.12 if resolved.synthetic_bold else 1.0)
        except OSError:
            return None

    def _resolve_with_fontconfig(
        self,
        family: str,
        *,
        bold: bool,
    ) -> ResolvedFont | None:
        executable = shutil.which("fc-match")
        if executable is None:
            return None
        query = f"{family}:style=Bold" if bold else family
        result = subprocess.run(
            [
                executable,
                "-f",
                "%{family[0]}|%{style[0]}|%{file}|%{index}\n",
                query,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            parts = line.split("|", 3)
            if len(parts) != 4:
                continue
            matched_family, matched_style, raw_path, raw_index = parts
            if not self._family_matches(family, matched_family):
                continue
            path = Path(raw_path.strip())
            if path.is_file():
                style_is_bold = self._style_is_bold(matched_style)
                try:
                    index = int(raw_index or 0)
                except ValueError:
                    index = 0
                return ResolvedFont(
                    str(path.resolve()),
                    index=index,
                    synthetic_bold=bold and not style_is_bold,
                )
        return None

    def _family_matches(self, requested: str, matched: str) -> bool:
        normalize = lambda value: "".join(
            character.lower() for character in value if character.isalnum()
        )
        requested_name = normalize(requested)
        matched_name = normalize(matched)
        if requested_name in {"sans", "sansserif", "serif", "monospace"}:
            return True
        return bool(requested_name and requested_name == matched_name)

    def _resolve_from_font_directories(
        self,
        family: str,
        *,
        bold: bool,
    ) -> ResolvedFont | None:
        normalized = "".join(character.lower() for character in family if character.isalnum())
        roots = (
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library/Fonts",
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
        )
        matches: list[Path] = []
        for root in roots:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if path.suffix.lower() not in {".ttf", ".ttc", ".otf"}:
                    continue
                stem = "".join(
                    character.lower() for character in path.stem if character.isalnum()
                )
                if normalized and self._stem_matches_family(stem, normalized):
                    matches.append(path)
        if not matches:
            return None
        if bold:
            for path in matches:
                if self._style_is_bold(path.stem):
                    return ResolvedFont(str(path.resolve()))
        return ResolvedFont(
            str(matches[0].resolve()),
            synthetic_bold=bold,
        )

    def _style_is_bold(self, style: str) -> bool:
        normalized = style.lower()
        return any(
            marker in normalized
            for marker in ("bold", "semibold", "demi", "heavy", "black")
        )

    def _stem_matches_family(self, stem: str, family: str) -> bool:
        if stem == family:
            return True
        style_suffixes = (
            "regular",
            "roman",
            "book",
            "medium",
            "light",
            "thin",
            "bold",
            "semibold",
            "demibold",
            "heavy",
            "black",
            "italic",
            "bolditalic",
        )
        return any(stem == family + suffix for suffix in style_suffixes)
