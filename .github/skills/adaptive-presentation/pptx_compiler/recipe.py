from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from .compiler import SlideCanvas, SlideCompiler
from .components import ComponentRegistry
from .layouts import BlueprintLibrary
from .models import (
    DeckValidationError,
    ContentItem,
    DesignDNA,
    LayoutError,
    SlideFrame,
    Source,
    ValidationReport,
)


CustomBuilder = Callable[[SlideCanvas, Mapping[str, object]], None]

FORBIDDEN_RECIPE_KEYS = {
    "palette",
    "typography",
    "font",
    "font_size",
    "size_pt",
    "hex",
    "rgb",
    "coordinates",
    "x",
    "y",
    "w",
    "h",
    "width",
    "height",
    "corner_radius",
    "shadow",
    "fill_color",
    "line_color",
}

SEMANTIC_CANDIDATES: dict[str, tuple[tuple[str, str], ...]] = {
    "cover": (("cover", "split"), ("cover", "centered")),
    "statement": (("statement", "hero-left"), ("statement", "centered")),
    "comparison": (("comparison", "balanced"), ("comparison", "axis")),
    "process": (("process", "rail"), ("process", "stair")),
    "layers": (("layered", "stack"), ("layered", "pyramid")),
    "matrix": (("matrix", "table"), ("matrix", "quadrants")),
    "status": (("matrix", "table"), ("statement", "hero-left")),
    "architecture": (("architecture", "pipeline"), ("architecture", "hub")),
    "resource_hierarchy": (("architecture", "hub"),),
    "agent_anatomy": (("architecture", "hub"),),
    "code": (("code", "split"), ("code", "full")),
    "roadmap": (("roadmap", "rail"), ("roadmap", "gates")),
    "quality_loop": (("roadmap", "gates"), ("roadmap", "rail")),
    "security_layers": (("layered", "stack"), ("layered", "pyramid")),
    "custom": (("custom", "free"),),
}

ACCENT_ROLES = {
    "primary",
    "secondary",
    "accent",
    "success",
    "warning",
    "danger",
    "preview",
}


@dataclass(frozen=True)
class SlideRecipe:
    id: str
    title: str
    semantic_type: str
    component: str | None = None
    section: str = ""
    subtitle: str | None = None
    source_refs: tuple[str, ...] = ()
    emphasis: str = "standard"
    accent_role: str = "primary"
    family: str | None = None
    variant: str | None = None
    slots: int | None = None
    density: str = "balanced"
    content: Mapping[str, object] = field(default_factory=dict)
    custom_builder: str | None = None
    allow_repeat: bool = False
    card_grid: bool | None = None

    def __post_init__(self) -> None:
        string_fields = {
            "id": self.id,
            "title": self.title,
            "semantic_type": self.semantic_type,
            "section": self.section,
            "emphasis": self.emphasis,
            "accent_role": self.accent_role,
            "density": self.density,
        }
        for name, value in string_fields.items():
            if not isinstance(value, str):
                raise LayoutError(f"{name} must be a string.")
        for name, value in {
            "component": self.component,
            "subtitle": self.subtitle,
            "family": self.family,
            "variant": self.variant,
            "custom_builder": self.custom_builder,
        }.items():
            if value is not None and not isinstance(value, str):
                raise LayoutError(f"{name} must be a string or null.")
        if not isinstance(self.allow_repeat, bool):
            raise LayoutError("allow_repeat must be a boolean.")
        if self.card_grid is not None and not isinstance(self.card_grid, bool):
            raise LayoutError("card_grid must be a boolean or null.")
        if not isinstance(self.source_refs, Sequence) or isinstance(
            self.source_refs, (str, bytes)
        ):
            raise LayoutError("source_refs must be a sequence of source keys.")
        source_refs = tuple(self.source_refs)
        if any(not isinstance(reference, str) for reference in source_refs):
            raise LayoutError("Every source reference must be a string.")
        object.__setattr__(self, "source_refs", source_refs)
        if not isinstance(self.content, Mapping):
            raise LayoutError("Slide recipe content must be an object.")
        frozen_content = _freeze_recipe_value(self.content)
        object.__setattr__(self, "content", frozen_content)

        if not self.id.strip() or not self.title.strip() and self.semantic_type != "cover":
            raise LayoutError("Slide recipes require an id and conclusion title.")
        if self.semantic_type not in SEMANTIC_CANDIDATES:
            raise LayoutError(f"Unknown semantic type: {self.semantic_type!r}")
        if self.emphasis not in {"standard", "inverse", "hero"}:
            raise LayoutError("emphasis must be standard, inverse, or hero.")
        if self.density not in {"low", "balanced", "high"}:
            raise LayoutError("density must be low, balanced, or high.")
        if self.accent_role not in ACCENT_ROLES:
            raise LayoutError(
                f"accent_role must be a semantic palette role: {self.accent_role!r}"
            )
        if len(self.source_refs) > 2:
            raise LayoutError("A slide recipe supports at most two source references.")
        if self.slots is not None and (
            isinstance(self.slots, bool)
            or not isinstance(self.slots, int)
            or self.slots <= 0
        ):
            raise LayoutError("slots must be a positive integer when provided.")
        _reject_visual_tokens(frozen_content)

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "SlideRecipe":
        known = {
            "id",
            "title",
            "semantic_type",
            "component",
            "section",
            "subtitle",
            "source_refs",
            "emphasis",
            "accent_role",
            "family",
            "variant",
            "slots",
            "density",
            "content",
            "custom_builder",
            "allow_repeat",
            "card_grid",
        }
        unknown = set(value) - known
        if unknown:
            raise LayoutError(f"Unknown slide recipe keys: {sorted(unknown)}")
        raw_sources = value.get("source_refs", ())
        if not isinstance(raw_sources, Sequence) or isinstance(
            raw_sources, (str, bytes)
        ):
            raise LayoutError("source_refs must be a sequence of source keys.")
        raw_content = value.get("content", {})
        if not isinstance(raw_content, Mapping):
            raise LayoutError("Slide recipe content must be an object.")
        slots = value.get("slots")
        if slots is not None and (
            isinstance(slots, bool) or not isinstance(slots, int)
        ):
            raise LayoutError("slots must be an integer.")
        allow_repeat = value.get("allow_repeat", False)
        if not isinstance(allow_repeat, bool):
            raise LayoutError("allow_repeat must be a boolean.")
        card_grid = value.get("card_grid")
        if card_grid is not None and not isinstance(card_grid, bool):
            raise LayoutError("card_grid must be a boolean or null.")
        return cls(
            id=_required_string(value, "id"),
            title=_optional_string(value, "title", ""),
            semantic_type=_required_string(value, "semantic_type"),
            component=_optional_nullable_string(value, "component"),
            section=_optional_string(value, "section", ""),
            subtitle=_optional_nullable_string(value, "subtitle"),
            source_refs=tuple(str(item) for item in raw_sources),
            emphasis=_optional_string(value, "emphasis", "standard"),
            accent_role=_optional_string(value, "accent_role", "primary"),
            family=_optional_nullable_string(value, "family"),
            variant=_optional_nullable_string(value, "variant"),
            slots=slots,
            density=_optional_string(value, "density", "balanced"),
            content=raw_content,
            custom_builder=_optional_nullable_string(value, "custom_builder"),
            allow_repeat=allow_repeat,
            card_grid=card_grid,
        )


@dataclass(frozen=True)
class DeckRecipe:
    title: str
    slides: tuple[SlideRecipe, ...]
    subject: str = ""
    expected_slides: int | None = None
    min_layout_families: int | None = None
    max_card_grid_ratio: float = 0.35

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not isinstance(self.subject, str):
            raise LayoutError("DeckRecipe title and subject must be strings.")
        if not isinstance(self.slides, Sequence) or isinstance(
            self.slides, (str, bytes)
        ):
            raise LayoutError("DeckRecipe slides must be a sequence.")
        slides = tuple(self.slides)
        if any(not isinstance(slide, SlideRecipe) for slide in slides):
            raise LayoutError("DeckRecipe slides must contain SlideRecipe objects.")
        object.__setattr__(self, "slides", slides)
        if not self.title.strip() or not self.slides:
            raise LayoutError("DeckRecipe requires a title and at least one slide.")
        identifiers = [slide.id for slide in self.slides]
        duplicates = [
            identifier
            for identifier, count in Counter(identifiers).items()
            if count > 1
        ]
        if duplicates:
            raise LayoutError(f"Duplicate slide recipe ids: {duplicates}")
        if self.expected_slides is not None and (
            isinstance(self.expected_slides, bool)
            or not isinstance(self.expected_slides, int)
            or self.expected_slides <= 0
        ):
            raise LayoutError("expected_slides must be a positive integer.")
        if self.min_layout_families is not None and (
            isinstance(self.min_layout_families, bool)
            or not isinstance(self.min_layout_families, int)
            or self.min_layout_families <= 0
        ):
            raise LayoutError("min_layout_families must be a positive integer.")
        if isinstance(self.max_card_grid_ratio, bool) or not isinstance(
            self.max_card_grid_ratio, (int, float)
        ):
            raise LayoutError("max_card_grid_ratio must be a number.")
        if self.expected_slides is not None and self.expected_slides != len(self.slides):
            raise LayoutError(
                f"Recipe expected_slides={self.expected_slides}, "
                f"but contains {len(self.slides)} slides."
            )
        if (
            not math.isfinite(self.max_card_grid_ratio)
            or not 0 <= self.max_card_grid_ratio <= 1
        ):
            raise LayoutError("max_card_grid_ratio must be a finite number from 0 to 1.")

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "DeckRecipe":
        known = {
            "title",
            "subject",
            "slides",
            "expected_slides",
            "min_layout_families",
            "max_card_grid_ratio",
        }
        unknown = set(value) - known
        if unknown:
            raise LayoutError(f"Unknown deck recipe keys: {sorted(unknown)}")
        raw_slides = value.get("slides")
        if not isinstance(raw_slides, Sequence) or isinstance(
            raw_slides, (str, bytes)
        ):
            raise LayoutError("Deck recipe slides must be a sequence.")
        if any(not isinstance(slide, Mapping) for slide in raw_slides):
            raise LayoutError("Every deck recipe slide must be an object.")
        expected = _optional_positive_int(value, "expected_slides")
        minimum = _optional_positive_int(value, "min_layout_families")
        ratio = value.get("max_card_grid_ratio", 0.35)
        if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
            raise LayoutError("max_card_grid_ratio must be a number.")
        ratio = float(ratio)
        return cls(
            title=_required_string(value, "title"),
            subject=_optional_string(value, "subject", ""),
            slides=tuple(SlideRecipe.from_dict(slide) for slide in raw_slides),
            expected_slides=expected,
            min_layout_families=minimum,
            max_card_grid_ratio=ratio,
        )

    @classmethod
    def from_json(cls, path: Path) -> "DeckRecipe":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, Mapping):
            raise LayoutError("Deck recipe JSON must contain an object.")
        return cls.from_dict(data)


@dataclass(frozen=True)
class LayoutChoice:
    family: str
    variant: str


class AdaptiveLayoutSelector:
    """Chooses semantic layouts while penalizing repetition and overuse."""

    def choose(
        self,
        slide: SlideRecipe,
        history: Sequence[LayoutChoice],
        usage: Counter[str],
        *,
        slots: int,
        component: str | None,
        components: ComponentRegistry,
        blueprints: BlueprintLibrary,
    ) -> LayoutChoice:
        candidates = list(SEMANTIC_CANDIDATES[slide.semantic_type])
        if slide.family:
            candidates = [
                candidate
                for candidate in candidates
                if candidate[0] == slide.family
            ]
            if not candidates:
                candidates = [(slide.family, slide.variant or "default")]
        if slide.variant:
            candidates = [
                (family, variant)
                for family, variant in candidates
                if variant == slide.variant
            ] or [(slide.family or candidates[0][0], slide.variant)]

        supported: list[tuple[str, str]] = []
        failures: list[str] = []
        for candidate in candidates:
            if not self._supports_slots(candidate, slots):
                failures.append(f"{candidate[0]}/{candidate[1]} does not support slots={slots}")
                continue
            try:
                plan = blueprints.plan(candidate[0], candidate[1], slots)
            except LayoutError as error:
                failures.append(str(error))
                continue
            if component:
                error = components.layout_error(
                    component,
                    plan,
                    slide.content,
                    slots=slots,
                )
                if error:
                    failures.append(error)
                    continue
            supported.append(candidate)
        candidates = supported
        if not candidates:
            raise LayoutError(
                f"No layout candidate supports slide {slide.id!r}: "
                + "; ".join(dict.fromkeys(failures))
            )

        def score(candidate: tuple[str, str]) -> tuple[float, str, str]:
            family, variant = candidate
            value = usage[family] * 3.0
            if history and history[-1].family == family:
                value += 10
            if history and history[-1] == LayoutChoice(family, variant):
                value += 4
            if len(history) >= 2 and all(
                previous.family == family for previous in history[-2:]
            ):
                value += 100
            if slide.density == "high" and variant in {
                "centered",
                "quadrants",
                "stair",
            }:
                value += 3
            if slide.density == "low" and variant in {"table", "full", "stack"}:
                value += 2
            if slide.emphasis == "hero" and variant in {"centered", "hub", "split"}:
                value -= 2
            if (
                slide.semantic_type == "cover"
                and variant == "centered"
                and str(slide.content.get("visual_text", "")).count("\n") >= 2
            ):
                value += 12
            return value, family, variant

        family, variant = min(candidates, key=score)
        return LayoutChoice(family, variant)

    def _supports_slots(self, candidate: tuple[str, str], slots: int) -> bool:
        family = candidate[0]
        if family == "process":
            return 2 <= slots <= 8
        if family == "layered":
            return 3 <= slots <= 7
        if family == "roadmap":
            return 3 <= slots <= 6
        return True


class RecipeAssembler:
    """Compiles semantic recipes with an explicit per-deck Design DNA."""

    def __init__(
        self,
        design: DesignDNA,
        *,
        sources: Mapping[str, Source] | None = None,
        custom_builders: Mapping[str, CustomBuilder] | None = None,
        components: ComponentRegistry | None = None,
        selector: AdaptiveLayoutSelector | None = None,
    ):
        self.design = design
        self.sources = dict(sources or {})
        self.custom_builders = dict(custom_builders or {})
        self.components = components or ComponentRegistry()
        self.selector = selector or AdaptiveLayoutSelector()

    def compile(self, recipe: DeckRecipe) -> SlideCompiler:
        compiler = SlideCompiler(
            self.design,
            title=recipe.title,
            subject=recipe.subject,
        )
        history: list[LayoutChoice] = []
        usage: Counter[str] = Counter()

        for number, slide_recipe in enumerate(recipe.slides, 1):
            component = self._component_name(slide_recipe)
            slots = self._effective_slots(slide_recipe, component)
            choice = self.selector.choose(
                slide_recipe,
                history,
                usage,
                slots=slots,
                component=None if slide_recipe.custom_builder else component,
                components=self.components,
                blueprints=compiler.blueprints,
            )
            history.append(choice)
            usage[choice.family] += 1
            inverse = slide_recipe.emphasis in {"inverse", "hero"}
            frame = SlideFrame(
                title=slide_recipe.title,
                section=slide_recipe.section,
                number=number,
                subtitle=slide_recipe.subtitle,
                source=self._resolve_sources(slide_recipe.source_refs),
                background_role="canvas_alt" if inverse else "canvas",
                inverse=inverse,
                accent_role=slide_recipe.accent_role,
                show_header=slide_recipe.semantic_type != "cover",
                show_footer=bool(slide_recipe.source_refs),
            )
            canvas = compiler.begin_slide(
                frame,
                family=choice.family,
                variant=choice.variant,
                slots=slots,
                card_grid=slide_recipe.card_grid,
                allow_repeat=slide_recipe.allow_repeat,
            )
            if slide_recipe.custom_builder:
                try:
                    builder = self.custom_builders[slide_recipe.custom_builder]
                except KeyError as error:
                    raise LayoutError(
                        f"Missing custom builder {slide_recipe.custom_builder!r}."
                    ) from error
                builder(canvas, slide_recipe.content)
            else:
                self.components.render(component, canvas, slide_recipe.content)
        return compiler

    def compile_to(
        self,
        recipe: DeckRecipe,
        output: Path,
        *,
        report_path: Path | None = None,
    ) -> ValidationReport:
        compiler = self.compile(recipe)
        return compiler.save(
            output,
            expected_slides=recipe.expected_slides or len(recipe.slides),
            min_layout_families=recipe.min_layout_families,
            max_card_grid_ratio=recipe.max_card_grid_ratio,
            report_path=report_path,
        )

    def _resolve_sources(self, references: Sequence[str]) -> tuple[Source, ...]:
        missing = [reference for reference in references if reference not in self.sources]
        if missing:
            raise LayoutError(f"Unknown source references: {missing}")
        return tuple(self.sources[reference] for reference in references)

    def _component_name(self, slide: SlideRecipe) -> str:
        return slide.component or {
            "status": "status_ledger",
        }.get(slide.semantic_type, slide.semantic_type)

    def _effective_slots(self, slide: SlideRecipe, component: str) -> int:
        if slide.slots is not None:
            return slide.slots
        if component in {
            "process",
            "layers",
            "security_layers",
            "roadmap",
            "quality_loop",
        }:
            items = slide.content.get("items", [])
            if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
                raise LayoutError(f"{component} requires an items sequence.")
            if not items:
                raise LayoutError(f"{component} requires at least one item.")
            return len(items)
        return 4


def _reject_visual_tokens(value: object, path: str = "content") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            raw_key = str(key)
            normalized = "".join(character.lower() for character in raw_key if character.isalnum())
            exact = raw_key.lower().replace("-", "_")
            visual_key = (
                exact in FORBIDDEN_RECIPE_KEYS
                or exact in {"x", "y", "w", "h", "width", "height"}
                or any(
                    token in normalized
                    for token in (
                        "fontsize",
                        "sizept",
                        "fontfamily",
                        "fontname",
                        "hexcolor",
                        "rgbcolor",
                        "coordinate",
                        "cornerradius",
                        "fillcolor",
                        "linecolor",
                        "shadow",
                    )
                )
            )
            if visual_key:
                raise LayoutError(
                    f"DeckRecipe cannot store visual token {path}.{key}; "
                    "put it in DesignDNA or a custom builder."
                )
            _reject_visual_tokens(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _reject_visual_tokens(child, f"{path}[{index}]")


def _freeze_recipe_value(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _freeze_recipe_value(child)
                for key, child in value.items()
            }
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return tuple(_freeze_recipe_value(child) for child in value)
    if isinstance(value, ContentItem):
        return value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise LayoutError(
        f"Recipe content must be JSON-compatible or ContentItem, not {type(value).__name__}."
    )


def _required_string(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str):
        raise LayoutError(f"{key} must be a string.")
    return item


def _optional_string(
    value: Mapping[str, object],
    key: str,
    default: str,
) -> str:
    item = value.get(key, default)
    if not isinstance(item, str):
        raise LayoutError(f"{key} must be a string.")
    return item


def _optional_nullable_string(
    value: Mapping[str, object],
    key: str,
) -> str | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, str):
        raise LayoutError(f"{key} must be a string or null.")
    return item


def _optional_positive_int(
    value: Mapping[str, object],
    key: str,
) -> int | None:
    item = value.get(key)
    if item is None:
        return None
    if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
        raise LayoutError(f"{key} must be a positive integer.")
    return item
