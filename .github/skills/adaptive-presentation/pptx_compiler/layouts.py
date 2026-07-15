from __future__ import annotations

from collections.abc import Callable

from .models import LayoutError, LayoutMetrics, LayoutPlan, Region


class BlueprintLibrary:
    """Returns semantic layout regions without prescribing visual styling."""

    def __init__(self, metrics: LayoutMetrics, spacing: str = "balanced"):
        self.metrics = metrics
        self.spacing = spacing
        self.gap_scale = {
            "compact": 0.8,
            "balanced": 1.0,
            "spacious": 1.25,
        }[spacing]
        self._builders: dict[str, Callable[[str, int], LayoutPlan]] = {
            "cover": self._cover,
            "statement": self._statement,
            "comparison": self._comparison,
            "process": self._process,
            "layered": self._layered,
            "matrix": self._matrix,
            "architecture": self._architecture,
            "code": self._code,
            "roadmap": self._roadmap,
            "custom": self._custom,
        }

    @property
    def families(self) -> tuple[str, ...]:
        return tuple(self._builders)

    def plan(self, family: str, variant: str = "default", slots: int = 4) -> LayoutPlan:
        try:
            plan = self._builders[family](variant, slots)
        except KeyError as error:
            raise LayoutError(
                f"Unknown layout family {family!r}. Available: {', '.join(self.families)}"
            ) from error
        self._validate(plan)
        return plan

    def _content(self) -> Region:
        return Region(
            self.metrics.left,
            self.metrics.content_top,
            self.metrics.safe_width,
            self.metrics.content_height,
        )

    def _cover(self, variant: str, slots: int) -> LayoutPlan:
        width = self.metrics.width
        height = self.metrics.height
        if variant in {"default", "split"}:
            left = self.metrics.left + 0.08
            right = width - self.metrics.right
            safe_width = right - left
            gap = min(0.48, safe_width * 0.045)
            left_width = safe_width * 0.52
            visual_x = left + left_width + gap
            visual_width = right - visual_x
            visual_top = max(0.65, self.metrics.title_top + 0.18)
            visual_bottom = height - 0.9
            regions = {
                "kicker": Region(left, visual_top, left_width, 0.36),
                "headline": Region(
                    left,
                    visual_top + 0.52,
                    left_width,
                    min(2.0, height * 0.28),
                ),
                "subtitle": Region(
                    left + 0.02,
                    visual_top + 2.72,
                    left_width - 0.04,
                    min(0.78, height * 0.11),
                ),
                "visual": Region(
                    visual_x,
                    visual_top,
                    visual_width,
                    visual_bottom - visual_top,
                ),
                "meta": Region(left + 0.02, height - 1.25, left_width - 0.04, 0.42),
            }
            return LayoutPlan("cover", "split", regions)
        if variant == "centered":
            regions = {
                "kicker": Region(2.1, 0.85, width - 4.2, 0.38),
                "headline": Region(1.4, 1.48, width - 2.8, 1.9),
                "subtitle": Region(2.2, 3.65, width - 4.4, 0.8),
                "visual": Region(2.3, 4.7, width - 4.6, 1.3),
                "meta": Region(2.2, height - 0.82, width - 4.4, 0.34),
            }
            return LayoutPlan("cover", "centered", regions)
        raise LayoutError(f"Unknown cover variant: {variant}")

    def _statement(self, variant: str, slots: int) -> LayoutPlan:
        content = self._content()
        if variant in {"default", "hero-left"}:
            regions = {
                "hero": Region(content.x, content.y + 0.2, content.w * 0.56, content.h - 0.4),
                "support": Region(
                    content.x + content.w * 0.62,
                    content.y + 0.35,
                    content.w * 0.38,
                    content.h * 0.52,
                ),
                "evidence": Region(
                    content.x + content.w * 0.62,
                    content.y + content.h * 0.63,
                    content.w * 0.38,
                    content.h * 0.27,
                ),
            }
            return LayoutPlan("statement", "hero-left", regions)
        if variant == "centered":
            regions = {
                "hero": Region(content.x + 0.8, content.y + 0.45, content.w - 1.6, 2.35),
                "support": Region(content.x + 1.35, content.y + 3.08, content.w - 2.7, 1.05),
                "evidence": Region(content.x + 2.2, content.y + 4.35, content.w - 4.4, 0.58),
            }
            return LayoutPlan("statement", "centered", regions)
        raise LayoutError(f"Unknown statement variant: {variant}")

    def _comparison(self, variant: str, slots: int) -> LayoutPlan:
        if variant not in {"default", "balanced", "axis"}:
            raise LayoutError(f"Unknown comparison variant: {variant}")
        content = self._content()
        gutter = 0.42 * self.gap_scale
        axis_width = 1.2 if variant == "axis" else 0.3
        column_width = (content.w - gutter * 2 - axis_width) / 2
        regions = {
            "left": Region(content.x, content.y + 0.18, column_width, content.h - 0.36),
            "axis": Region(
                content.x + column_width + gutter,
                content.y + 0.18,
                axis_width,
                content.h - 0.36,
            ),
            "right": Region(
                content.x + column_width + gutter * 2 + axis_width,
                content.y + 0.18,
                column_width,
                content.h - 0.36,
            ),
        }
        normalized = "axis" if variant == "axis" else "balanced"
        return LayoutPlan("comparison", normalized, regions, card_grid=False)

    def _process(self, variant: str, slots: int) -> LayoutPlan:
        if not 2 <= slots <= 8:
            raise LayoutError("Process layouts support between 2 and 8 slots.")
        content = self._content()
        regions: dict[str, Region] = {
            "rail": Region(content.x + 0.3, content.y + content.h * 0.47, content.w - 0.6, 0.18)
        }
        if variant in {"default", "rail"}:
            gap = 0.22 * self.gap_scale
            width = (content.w - gap * (slots - 1)) / slots
            for index in range(slots):
                regions[f"step_{index + 1}"] = Region(
                    content.x + index * (width + gap),
                    content.y + 0.6,
                    width,
                    content.h - 1.2,
                )
            return LayoutPlan("process", "rail", regions)
        if variant == "stair":
            horizontal_gap = 0.16 * self.gap_scale
            width = content.w / slots - horizontal_gap
            step_height = min(1.22, content.h / (slots + 1))
            for index in range(slots):
                regions[f"step_{index + 1}"] = Region(
                    content.x + index * (width + horizontal_gap),
                    content.y + content.h - (index + 1) * step_height,
                    width,
                    step_height * (index + 1),
                )
            return LayoutPlan("process", "stair", regions)
        raise LayoutError(f"Unknown process variant: {variant}")

    def _layered(self, variant: str, slots: int) -> LayoutPlan:
        if not 3 <= slots <= 7:
            raise LayoutError("Layered layouts support between 3 and 7 slots.")
        content = self._content()
        regions: dict[str, Region] = {}
        if variant in {"default", "stack"}:
            gap = 0.16 * self.gap_scale
            height = (content.h - gap * (slots - 1)) / slots
            for index in range(slots):
                inset = index * 0.22 * self.gap_scale
                regions[f"layer_{index + 1}"] = Region(
                    content.x + inset,
                    content.y + index * (height + gap),
                    content.w - inset * 2,
                    height,
                )
            return LayoutPlan("layered", "stack", regions)
        if variant == "pyramid":
            gap = 0.12 * self.gap_scale
            height = (content.h - gap * (slots - 1)) / slots
            for index in range(slots):
                inset = (slots - index - 1) * 0.5 * self.gap_scale
                regions[f"layer_{index + 1}"] = Region(
                    content.x + inset,
                    content.y + index * (height + gap),
                    content.w - inset * 2,
                    height,
                )
            return LayoutPlan("layered", "pyramid", regions)
        raise LayoutError(f"Unknown layered variant: {variant}")

    def _matrix(self, variant: str, slots: int) -> LayoutPlan:
        content = self._content()
        if variant in {"default", "table"}:
            return LayoutPlan(
                "matrix",
                "table",
                {"table": Region(content.x, content.y + 0.15, content.w, content.h - 0.3)},
                card_grid=False,
            )
        if variant == "quadrants":
            gap = 0.22 * self.gap_scale
            width = (content.w - gap) / 2
            height = (content.h - gap) / 2
            regions = {
                "q1": Region(content.x, content.y, width, height),
                "q2": Region(content.x + width + gap, content.y, width, height),
                "q3": Region(content.x, content.y + height + gap, width, height),
                "q4": Region(
                    content.x + width + gap,
                    content.y + height + gap,
                    width,
                    height,
                ),
            }
            return LayoutPlan("matrix", "quadrants", regions, card_grid=True)
        raise LayoutError(f"Unknown matrix variant: {variant}")

    def _architecture(self, variant: str, slots: int) -> LayoutPlan:
        content = self._content()
        if variant in {"default", "pipeline"}:
            regions = {
                "input": Region(content.x, content.y + 0.75, content.w * 0.2, content.h - 1.5),
                "core": Region(
                    content.x + content.w * 0.3,
                    content.y + 0.4,
                    content.w * 0.4,
                    content.h - 0.8,
                ),
                "output": Region(
                    content.x + content.w * 0.8,
                    content.y + 0.75,
                    content.w * 0.2,
                    content.h - 1.5,
                ),
                "operations": Region(
                    content.x + content.w * 0.25,
                    content.y + content.h - 0.72,
                    content.w * 0.5,
                    0.55,
                ),
            }
            return LayoutPlan("architecture", "pipeline", regions)
        if variant == "hub":
            regions = {
                "hub": Region(
                    content.x + content.w * 0.35,
                    content.y + content.h * 0.22,
                    content.w * 0.3,
                    content.h * 0.52,
                ),
                "left": Region(content.x, content.y + 0.4, content.w * 0.25, content.h - 0.8),
                "right": Region(
                    content.x + content.w * 0.75,
                    content.y + 0.4,
                    content.w * 0.25,
                    content.h - 0.8,
                ),
                "bottom": Region(
                    content.x + content.w * 0.28,
                    content.y + content.h * 0.8,
                    content.w * 0.44,
                    content.h * 0.16,
                ),
            }
            return LayoutPlan("architecture", "hub", regions)
        raise LayoutError(f"Unknown architecture variant: {variant}")

    def _code(self, variant: str, slots: int) -> LayoutPlan:
        content = self._content()
        if variant in {"default", "split"}:
            return LayoutPlan(
                "code",
                "split",
                {
                    "code": Region(content.x, content.y + 0.08, content.w * 0.63, content.h - 0.16),
                    "explain": Region(
                        content.x + content.w * 0.68,
                        content.y + 0.08,
                        content.w * 0.32,
                        content.h - 0.16,
                    ),
                },
            )
        if variant == "full":
            return LayoutPlan(
                "code",
                "full",
                {"code": Region(content.x + 0.25, content.y + 0.08, content.w - 0.5, content.h - 0.16)},
            )
        raise LayoutError(f"Unknown code variant: {variant}")

    def _roadmap(self, variant: str, slots: int) -> LayoutPlan:
        if variant not in {"default", "rail", "gates"}:
            raise LayoutError(f"Unknown roadmap variant: {variant}")
        if not 3 <= slots <= 6:
            raise LayoutError("Roadmap layouts support between 3 and 6 slots.")
        content = self._content()
        gap = 0.25 * self.gap_scale
        width = (content.w - gap * (slots - 1)) / slots
        regions = {
            "rail": Region(content.x + 0.2, content.y + content.h * 0.55, content.w - 0.4, 0.18)
        }
        for index in range(slots):
            y = content.y + 0.45
            height = content.h - 0.9
            if variant == "gates":
                y += (index % 2) * 0.42
                height -= 0.42
            regions[f"stage_{index + 1}"] = Region(
                content.x + index * (width + gap),
                y,
                width,
                height,
            )
        normalized = "gates" if variant == "gates" else "rail"
        return LayoutPlan("roadmap", normalized, regions)

    def _custom(self, variant: str, slots: int) -> LayoutPlan:
        return LayoutPlan("custom", variant, {"content": self._content()})

    def _validate(self, plan: LayoutPlan) -> None:
        for name, region in plan.regions.items():
            if region.w <= 0 or region.h <= 0:
                raise LayoutError(
                    f"Layout {plan.family}/{plan.variant} region {name} has no area."
                )
            if (
                region.x < 0
                or region.y < 0
                or region.right > self.metrics.width + 0.001
                or region.bottom > self.metrics.height + 0.001
            ):
                raise LayoutError(
                    f"Layout {plan.family}/{plan.variant} region {name} is out of bounds: {region}"
                )
