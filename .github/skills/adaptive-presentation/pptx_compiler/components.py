from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from .compiler import SlideCanvas
from .models import ContentItem, LayoutError, LayoutPlan, Region, TextSpan


Renderer = Callable[[SlideCanvas, Mapping[str, object]], None]

COLOR_ROLES = {
    "ink",
    "ink_inverse",
    "muted_ink",
    "muted_inverse",
    "primary",
    "secondary",
    "accent",
    "success",
    "warning",
    "danger",
    "preview",
    "border",
    "border_inverse",
}


def _color_role(value: object, default: str = "primary") -> str:
    role = default if value is None else str(value)
    if role not in COLOR_ROLES:
        raise LayoutError(f"Recipe color must be a semantic palette role: {role!r}")
    return role


def _item(value: object) -> ContentItem:
    if isinstance(value, ContentItem):
        return ContentItem(
            title=value.title,
            detail=value.detail,
            color_role=_color_role(value.color_role),
            status=value.status,
        )
    if not isinstance(value, Mapping):
        raise LayoutError(f"Component item must be a mapping: {value!r}")
    return ContentItem(
        title=str(value.get("title", "")),
        detail=str(value.get("detail", "")),
        color_role=_color_role(value.get("color_role")),
        status=str(value["status"]) if value.get("status") is not None else None,
    )


def _items(value: object) -> list[ContentItem]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise LayoutError("Component items must be a sequence.")
    return [_item(item) for item in value]


def _strings(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise LayoutError("Expected a sequence of strings.")
    return [str(item) for item in value]


@dataclass(frozen=True)
class ComponentDefinition:
    name: str
    renderer: Renderer
    allowed_families: frozenset[str]
    required_regions: frozenset[str]
    compatibility: Callable[
        [LayoutPlan, Mapping[str, object], int],
        str | None,
    ] | None = None


class ComponentRegistry:
    """Design-DNA-driven semantic components for common slide relationships."""

    def __init__(self):
        self._definitions: dict[str, ComponentDefinition] = {}
        self._register_defaults()

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))

    def register(
        self,
        name: str,
        renderer: Renderer,
        *,
        allowed_families: Sequence[str],
        required_regions: Sequence[str] = (),
        compatibility: Callable[
            [LayoutPlan, Mapping[str, object], int],
            str | None,
        ] | None = None,
    ) -> None:
        if not name.strip():
            raise LayoutError("Component name cannot be empty.")
        self._definitions[name] = ComponentDefinition(
            name=name,
            renderer=renderer,
            allowed_families=frozenset(allowed_families),
            required_regions=frozenset(required_regions),
            compatibility=compatibility,
        )

    def render(
        self,
        name: str,
        canvas: SlideCanvas,
        payload: Mapping[str, object],
    ) -> None:
        try:
            definition = self._definitions[name]
        except KeyError as error:
            raise LayoutError(
                f"Unknown component {name!r}. Available: {', '.join(self.names)}"
            ) from error
        if canvas.plan.family not in definition.allowed_families:
            raise LayoutError(
                f"Component {name!r} requires one of "
                f"{sorted(definition.allowed_families)}, not {canvas.plan.family!r}."
            )
        definition.renderer(canvas, payload)

    def definition(self, name: str) -> ComponentDefinition:
        try:
            return self._definitions[name]
        except KeyError as error:
            raise LayoutError(
                f"Unknown component {name!r}. Available: {', '.join(self.names)}"
            ) from error

    def layout_error(
        self,
        name: str,
        plan: LayoutPlan,
        payload: Mapping[str, object],
        *,
        slots: int,
    ) -> str | None:
        definition = self.definition(name)
        if plan.family not in definition.allowed_families:
            return (
                f"component {name!r} requires {sorted(definition.allowed_families)}, "
                f"not {plan.family!r}"
            )

        missing_declared = sorted(
            definition.required_regions - set(plan.regions)
        )
        if missing_declared:
            return (
                f"component {name!r} requires missing regions "
                f"{missing_declared} for {plan.family}/{plan.variant}"
            )
        if definition.compatibility:
            error = definition.compatibility(plan, payload, slots)
            if error:
                return error

        required: set[str] = set()
        if name == "cover":
            required = {"kicker", "headline", "subtitle", "visual", "meta"}
        elif name == "statement":
            required = {"hero", "support", "evidence"}
        elif name == "comparison":
            required = {"left", "axis", "right"}
        elif name in {"matrix", "status_ledger"}:
            required = {"table"}
        elif name == "code":
            required = {"code"}
            if payload.get("explanations"):
                required.add("explain")
        elif name == "architecture":
            raw_nodes = payload.get("nodes", {})
            if isinstance(raw_nodes, Mapping):
                required.update(str(key) for key in raw_nodes)
            if payload.get("operations"):
                if "operations" in plan.regions:
                    required.add("operations")
                elif "bottom" in plan.regions:
                    required.add("bottom")
                else:
                    return "architecture operations require an operations or bottom region"
        elif name in {"resource_hierarchy", "agent_anatomy"}:
            required = {"hub", "left", "right", "bottom"}
        elif name in {"process"}:
            item_count = _item_count(payload)
            if item_count != slots:
                return f"process item count {item_count} does not match slots={slots}"
            required = {f"step_{index}" for index in range(1, slots + 1)}
        elif name in {"layers", "security_layers"}:
            item_count = _item_count(payload)
            if item_count != slots:
                return f"layer item count {item_count} does not match slots={slots}"
            required = {f"layer_{index}" for index in range(1, slots + 1)}
        elif name in {"roadmap", "quality_loop"}:
            item_count = _item_count(payload)
            if item_count != slots:
                return f"roadmap item count {item_count} does not match slots={slots}"
            required = {f"stage_{index}" for index in range(1, slots + 1)}

        missing = sorted(required - set(plan.regions))
        if missing:
            return (
                f"component {name!r} requires missing regions {missing} "
                f"for {plan.family}/{plan.variant}"
            )
        return None

    def _register_defaults(self) -> None:
        self.register(
            "cover",
            render_cover,
            allowed_families=["cover"],
            required_regions=["kicker", "headline", "subtitle", "visual", "meta"],
        )
        self.register(
            "statement",
            render_statement,
            allowed_families=["statement"],
            required_regions=["hero", "support", "evidence"],
        )
        self.register(
            "comparison",
            render_comparison,
            allowed_families=["comparison"],
            required_regions=["left", "axis", "right"],
        )
        self.register("process", render_process, allowed_families=["process"])
        self.register("layers", render_layers, allowed_families=["layered"])
        self.register(
            "matrix",
            render_matrix,
            allowed_families=["matrix"],
            required_regions=["table"],
        )
        self.register("architecture", render_architecture, allowed_families=["architecture"])
        self.register(
            "code",
            render_code,
            allowed_families=["code"],
            required_regions=["code"],
        )
        self.register("roadmap", render_roadmap, allowed_families=["roadmap"])
        self.register(
            "resource_hierarchy",
            render_resource_hierarchy,
            allowed_families=["architecture"],
            required_regions=["hub", "left", "right", "bottom"],
        )
        self.register(
            "agent_anatomy",
            render_agent_anatomy,
            allowed_families=["architecture"],
            required_regions=["hub", "left", "right", "bottom"],
        )
        self.register(
            "security_layers",
            render_security_layers,
            allowed_families=["layered"],
        )
        self.register(
            "quality_loop",
            render_quality_loop,
            allowed_families=["roadmap"],
        )
        self.register(
            "status_ledger",
            render_status_ledger,
            allowed_families=["matrix"],
            required_regions=["table"],
        )


def render_cover(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    background = canvas.frame.background_role
    inverse = canvas.frame.inverse
    canvas.text(
        "kicker",
        str(payload.get("kicker", "")),
        role="label",
        color=_color_role(payload.get("kicker_role"), "primary"),
        background=background,
        bold=True,
        size_pt=14,
        adapt_color=True,
    )
    canvas.text(
        "headline",
        str(payload.get("headline", "")),
        role="cover",
        color="ink_inverse" if inverse else "ink",
        background=background,
        bold=True,
        valign=MSO_ANCHOR.MIDDLE,
    )
    canvas.text(
        "subtitle",
        str(payload.get("subtitle", "")),
        role="body",
        color="muted_inverse" if inverse else "muted_ink",
        background=background,
    )
    canvas.box(
        "visual",
        fill="surface_alt" if inverse else "surface",
        line=_color_role(payload.get("visual_role"), "primary"),
    )
    canvas.text(
        canvas.region("visual", inset=0.25),
        str(payload.get("visual_text", "")),
        role=str(payload.get("visual_text_role", "title")),
        color="ink_inverse" if inverse else "ink",
        background="surface_alt" if inverse else "surface",
        bold=True,
        align=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE,
    )
    if payload.get("meta"):
        canvas.text(
            "meta",
            str(payload["meta"]),
            role="secondary",
            color="muted_inverse" if inverse else "muted_ink",
            background=background,
        )


def render_statement(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    background = canvas.frame.background_role
    hero_spans = payload.get("hero_spans")
    if hero_spans:
        if not isinstance(hero_spans, Sequence):
            raise LayoutError("hero_spans must be a sequence.")
        spans = [
            TextSpan(
                text=str(span.get("text", "")),
                role=str(span.get("role", "metric")),
                color_role=_color_role(span.get("color_role"), "primary"),
                bold=_boolean(span.get("bold", True), "hero_spans[].bold"),
                size_pt=float(span["size_pt"]) if span.get("size_pt") else None,
            )
            for span in hero_spans
            if isinstance(span, Mapping)
        ]
        canvas.rich_text(
            "hero",
            spans,
            background=background,
            adapt_color=True,
            align=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE,
        )
    else:
        canvas.text(
            "hero",
            str(payload.get("hero", "")),
            role=str(payload.get("hero_role", "metric")),
            color=_color_role(payload.get("hero_color"), "primary"),
            background=background,
            bold=True,
            adapt_color=True,
            valign=MSO_ANCHOR.MIDDLE,
        )
    if payload.get("support") is not None:
        canvas.text(
            "support",
            str(payload["support"]),
            role="body",
            color="ink_inverse" if canvas.frame.inverse else "ink",
            background=background,
            bold=_boolean(payload.get("support_bold", True), "support_bold"),
            align=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE,
        )
    if payload.get("evidence") is not None:
        canvas.chip(
            "evidence",
            str(payload["evidence"]),
            fill=_color_role(payload.get("evidence_role"), "primary"),
        )


def render_comparison(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.comparison(
        str(payload.get("left_title", "LEFT")),
        _strings(payload.get("left_items", [])),
        str(payload.get("right_title", "RIGHT")),
        _strings(payload.get("right_items", [])),
        left_color=_color_role(payload.get("left_color"), "secondary"),
        right_color=_color_role(payload.get("right_color"), "primary"),
    )
    if payload.get("axis"):
        canvas.text(
            "axis",
            str(payload["axis"]),
            role="secondary",
            color=_color_role(payload.get("axis_color"), "accent"),
            background=canvas.frame.background_role,
            bold=True,
            adapt_color=True,
            align=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE,
        )


def render_process(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.process(_items(payload.get("items", [])))


def render_layers(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.layers(_items(payload.get("items", [])))


def render_matrix(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    headers = _strings(payload.get("headers", []))
    raw_rows = payload.get("rows", [])
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes)):
        raise LayoutError("Matrix rows must be a sequence.")
    rows = [_strings(row) for row in raw_rows]
    raw_weights = payload.get("column_weights")
    weights = None
    if raw_weights is not None:
        if not isinstance(raw_weights, Sequence) or isinstance(
            raw_weights, (str, bytes)
        ):
            raise LayoutError("column_weights must be a numeric sequence.")
        weights = []
        for value in raw_weights:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise LayoutError(
                    "column_weights must contain finite positive numbers."
                )
            weights.append(float(value))
        if len(weights) != len(headers):
            raise LayoutError("column_weights must match the header count.")
    canvas.matrix(
        headers,
        rows,
        column_widths=weights,
        header_fill=_color_role(payload.get("header_role"), "ink"),
    )


def render_architecture(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    raw_nodes = payload.get("nodes", {})
    if not isinstance(raw_nodes, Mapping):
        raise LayoutError("Architecture nodes must be a mapping of region to item.")
    for region_name, value in raw_nodes.items():
        canvas.node(str(region_name), _item(value))

    raw_connections = payload.get("connections", [])
    if not isinstance(raw_connections, Sequence) or isinstance(
        raw_connections, (str, bytes)
    ):
        raise LayoutError("Architecture connections must be a sequence.")
    for connection in raw_connections:
        if not isinstance(connection, Mapping):
            raise LayoutError("Architecture connection must be a mapping.")
        start = canvas.region(str(connection["from"]))
        end = canvas.region(str(connection["to"]))
        canvas.arrow(
            (start.right + 0.05, start.y + start.h / 2),
            (end.x - 0.05, end.y + end.h / 2),
            color=_color_role(connection.get("color_role"), "primary"),
        )
    if payload.get("operations"):
        canvas.chip(
            "operations" if "operations" in canvas.plan.regions else "bottom",
            str(payload["operations"]),
            fill=_color_role(payload.get("operations_role"), "ink"),
        )


def render_code(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    lines = _strings(payload.get("lines", []))
    explanations = _items(payload.get("explanations", []))
    canvas.code(lines, explanations)


def render_roadmap(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.roadmap(_items(payload.get("items", [])))


def render_resource_hierarchy(
    canvas: SlideCanvas,
    payload: Mapping[str, object],
) -> None:
    canvas.node("hub", _item(payload.get("resource", {})))
    projects = _items(payload.get("projects", []))
    connections = _items(payload.get("connected", []))
    _stack_nodes(canvas, "left", projects)
    _stack_nodes(canvas, "right", connections)
    if payload.get("boundary_label"):
        canvas.chip(
            "bottom",
            str(payload["boundary_label"]),
            fill=_color_role(payload.get("boundary_role"), "ink"),
        )


def render_agent_anatomy(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.node("hub", _item(payload.get("agent", {})))
    _stack_nodes(canvas, "left", _items(payload.get("left", [])))
    _stack_nodes(canvas, "right", _items(payload.get("right", [])))
    if payload.get("foundation"):
        canvas.chip(
            "bottom",
            str(payload["foundation"]),
            fill=_color_role(payload.get("foundation_role"), "primary"),
        )


def render_security_layers(
    canvas: SlideCanvas,
    payload: Mapping[str, object],
) -> None:
    canvas.layers(_items(payload.get("items", [])))


def render_quality_loop(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    canvas.roadmap(_items(payload.get("items", [])))


def render_status_ledger(canvas: SlideCanvas, payload: Mapping[str, object]) -> None:
    render_matrix(canvas, payload)


def _stack_nodes(
    canvas: SlideCanvas,
    region_name: str,
    items: Sequence[ContentItem],
) -> None:
    if not items:
        return
    region = canvas.region(region_name)
    gap = 0.1
    height = (region.h - gap * (len(items) - 1)) / len(items)
    for index, item in enumerate(items):
        canvas.node(
            Region(
                region.x,
                region.y + index * (height + gap),
                region.w,
                height,
            ),
            item,
        )


def _item_count(payload: Mapping[str, object]) -> int:
    value = payload.get("items", [])
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return -1
    return len(value)


def _boolean(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise LayoutError(f"{name} must be a boolean.")
    return value
