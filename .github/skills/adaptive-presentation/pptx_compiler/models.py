from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


HEX_PATTERN = re.compile(r"^[0-9A-Fa-f]{6}$")


class CompilerError(RuntimeError):
    """Base error raised by the slide compiler."""


class DesignValidationError(CompilerError):
    """Raised when Design DNA is incomplete or unsafe."""


class LayoutError(CompilerError):
    """Raised when a layout or shape exceeds its allowed geometry."""


class TextOverflowError(LayoutError):
    """Raised when text cannot fit without crossing its minimum size."""


class DeckValidationError(CompilerError):
    """Raised when the compiled deck fails preflight validation."""


def normalize_hex(value: str) -> str:
    normalized = value.strip().lstrip("#")
    if not HEX_PATTERN.fullmatch(normalized):
        raise DesignValidationError(f"Invalid HEX color: {value!r}")
    return normalized.upper()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    normalized = normalize_hex(value)
    return tuple(int(normalized[index : index + 2], 16) for index in (0, 2, 4))


def _linear_channel(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(value: str) -> float:
    red, green, blue = hex_to_rgb(value)
    return (
        0.2126 * _linear_channel(red)
        + 0.7152 * _linear_channel(green)
        + 0.0722 * _linear_channel(blue)
    )


def contrast_ratio(first: str, second: str) -> float:
    light, dark = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


@dataclass(frozen=True)
class Palette:
    canvas: str
    canvas_alt: str
    surface: str
    surface_alt: str
    ink: str
    ink_inverse: str
    muted_ink: str
    muted_inverse: str
    primary: str
    secondary: str
    accent: str
    border: str
    border_inverse: str
    success: str
    warning: str
    danger: str
    preview: str

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            object.__setattr__(self, name, normalize_hex(value))

        required_pairs = (
            ("canvas", self.canvas, self.ink),
            ("canvas_alt", self.canvas_alt, self.ink_inverse),
            ("surface", self.surface, self.ink),
            ("surface_alt", self.surface_alt, self.ink_inverse),
        )
        failures = [
            f"{name} contrast={contrast_ratio(background, foreground):.2f}"
            for name, background, foreground in required_pairs
            if contrast_ratio(background, foreground) < 4.5
        ]
        if failures:
            raise DesignValidationError(
                "Palette text contrast must be at least 4.5:1: " + ", ".join(failures)
            )

    def resolve(self, role_or_hex: str) -> str:
        if role_or_hex in self.__dataclass_fields__:
            return getattr(self, role_or_hex)
        return normalize_hex(role_or_hex)


@dataclass(frozen=True)
class Typography:
    body_font: str
    display_font: str
    mono_font: str
    cover_pt: float = 44
    title_pt: float = 32
    metric_pt: float = 48
    body_pt: float = 20
    secondary_pt: float = 15
    label_pt: float = 12
    code_pt: float = 15
    source_pt: float = 9

    def __post_init__(self) -> None:
        if not all((self.body_font, self.display_font, self.mono_font)):
            raise DesignValidationError("Typography requires body, display, and mono fonts.")
        if self.cover_pt < 34 or self.title_pt < 26:
            raise DesignValidationError("Cover and title sizes are below presentation minimums.")
        if self.body_pt < 16 or self.source_pt < 8.5:
            raise DesignValidationError("Body must be >=16pt and source must be >=8.5pt.")

    def size_for(self, role: str) -> float:
        sizes = {
            "cover": self.cover_pt,
            "title": self.title_pt,
            "metric": self.metric_pt,
            "body": self.body_pt,
            "secondary": self.secondary_pt,
            "label": self.label_pt,
            "code": self.code_pt,
            "source": self.source_pt,
        }
        if role not in sizes:
            raise DesignValidationError(f"Unknown typography role: {role}")
        return sizes[role]

    def font_for(self, role: str) -> str:
        if role in {"cover", "title", "metric"}:
            return self.display_font
        if role == "code":
            return self.mono_font
        return self.body_font

    def minimum_for(self, role: str) -> float:
        return {
            "cover": 34,
            "title": 26,
            "metric": 30,
            "body": 16,
            "secondary": 12,
            "label": 9.5,
            "code": 12,
            "source": 8.5,
        }[role]


@dataclass(frozen=True)
class ShapeLanguage:
    corner_style: str = "subtle"
    line_width_pt: float = 1.25
    border_width_pt: float = 0.8
    spacing: str = "balanced"
    depth: str = "flat"

    def __post_init__(self) -> None:
        if self.corner_style not in {"square", "subtle", "rounded"}:
            raise DesignValidationError(
                "corner_style must be square, subtle, or rounded."
            )
        if self.spacing not in {"compact", "balanced", "spacious"}:
            raise DesignValidationError(
                "spacing must be compact, balanced, or spacious."
            )
        if self.depth not in {"flat", "border", "shadow"}:
            raise DesignValidationError("depth must be flat, border, or shadow.")
        if self.line_width_pt <= 0 or self.border_width_pt <= 0:
            raise DesignValidationError("Line widths must be positive.")


@dataclass(frozen=True)
class LayoutMetrics:
    width: float = 13.333
    height: float = 7.5
    left: float = 0.72
    right: float = 0.72
    title_top: float = 0.46
    title_height: float = 0.92
    content_top: float = 1.62
    content_bottom: float = 6.78
    footer_top: float = 6.94

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise DesignValidationError("Slide dimensions must be positive.")
        if not (0 <= self.left < self.width and 0 <= self.right < self.width):
            raise DesignValidationError("Slide margins are invalid.")
        if not (
            self.title_top
            < self.title_top + self.title_height
            <= self.content_top
            < self.content_bottom
            <= self.footer_top
            < self.height
        ):
            raise DesignValidationError("Title, content, and footer regions overlap.")

    @property
    def safe_width(self) -> float:
        return self.width - self.left - self.right

    @property
    def content_height(self) -> float:
        return self.content_bottom - self.content_top


@dataclass(frozen=True)
class DesignDNA:
    name: str
    concept_words: tuple[str, str, str]
    visual_metaphor: str
    palette: Palette
    typography: Typography
    shapes: ShapeLanguage
    layout: LayoutMetrics = field(default_factory=LayoutMetrics)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DesignValidationError("Design DNA requires a name.")
        if len(self.concept_words) != 3 or any(
            not word.strip() for word in self.concept_words
        ):
            raise DesignValidationError("Design DNA requires exactly three concept words.")
        if not self.visual_metaphor.strip():
            raise DesignValidationError("Design DNA requires a visual metaphor.")


@dataclass(frozen=True)
class Source:
    organization: str
    title: str
    accessed: str
    url: str | None = None

    def label(self) -> str:
        return f"{self.organization} · {self.title} · accessed {self.accessed}"


@dataclass(frozen=True)
class SlideFrame:
    title: str
    section: str = ""
    number: int | None = None
    subtitle: str | None = None
    source: Source | Sequence[Source] | None = None
    background_role: str = "canvas"
    inverse: bool = False
    accent_role: str = "primary"
    show_header: bool = True
    show_footer: bool = True

    def sources(self) -> tuple[Source, ...]:
        if self.source is None:
            return ()
        if isinstance(self.source, Source):
            return (self.source,)
        return tuple(self.source)


@dataclass(frozen=True)
class Region:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def inset(self, horizontal: float, vertical: float | None = None) -> "Region":
        vertical = horizontal if vertical is None else vertical
        width = self.w - horizontal * 2
        height = self.h - vertical * 2
        if width <= 0 or height <= 0:
            raise LayoutError(f"Inset removes the entire region: {self}")
        return Region(
            self.x + horizontal,
            self.y + vertical,
            width,
            height,
        )


@dataclass(frozen=True)
class LayoutPlan:
    family: str
    variant: str
    regions: Mapping[str, Region]
    card_grid: bool = False

    def region(self, name: str) -> Region:
        try:
            return self.regions[name]
        except KeyError as error:
            raise LayoutError(
                f"Layout {self.family}/{self.variant} has no region {name!r}."
            ) from error


@dataclass(frozen=True)
class TextSpan:
    text: str
    role: str = "body"
    color_role: str = "ink"
    bold: bool = False
    size_pt: float | None = None
    font: str | None = None


@dataclass(frozen=True)
class ContentItem:
    title: str
    detail: str = ""
    color_role: str = "primary"
    status: str | None = None


@dataclass
class TextRecord:
    slide_number: int
    role: str
    text: str
    size_pt: float
    region: Region


@dataclass
class SlideRecord:
    number: int
    title: str
    family: str
    variant: str
    card_grid: bool
    allow_repeat: bool
    text: list[TextRecord] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    message: str
    slide: int | None = None


@dataclass
class ValidationReport:
    slide_count: int
    layout_families: tuple[str, ...]
    card_grid_ratio: float
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.level == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.level == "warning")

    def as_dict(self) -> dict:
        return {
            "slide_count": self.slide_count,
            "layout_families": list(self.layout_families),
            "card_grid_ratio": round(self.card_grid_ratio, 3),
            "issues": [
                {
                    "level": issue.level,
                    "message": issue.message,
                    "slide": issue.slide,
                }
                for issue in self.issues
            ],
        }

    def write_json(self, path: Path) -> None:
        import json

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.as_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def required_layout_families(slide_count: int) -> int:
    if slide_count >= 20:
        return 8
    if slide_count >= 10:
        return 5
    return max(1, math.ceil(slide_count / 3))
