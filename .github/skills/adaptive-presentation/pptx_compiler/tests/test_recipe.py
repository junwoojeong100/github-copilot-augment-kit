from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from collections import Counter
from dataclasses import replace
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = SKILL_ROOT / "examples"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(EXAMPLES_DIR))

from compiler_quickstart import design_for  # noqa: E402
from pptx_compiler import (  # noqa: E402
    AdaptiveLayoutSelector,
    BlueprintLibrary,
    ComponentRegistry,
    ContentItem,
    DeckRecipe,
    FontMetrics,
    LayoutError,
    RecipeAssembler,
    SlideRecipe,
)


def sample_recipe() -> DeckRecipe:
    return DeckRecipe(
        title="Recipe Test",
        expected_slides=4,
        min_layout_families=4,
        slides=(
            SlideRecipe(
                id="cover",
                title="",
                semantic_type="cover",
                emphasis="hero",
                content={
                    "kicker": "RECIPE",
                    "headline": "Adaptive deck",
                    "subtitle": "Explicit Design DNA",
                    "visual_text": "SPEC → PPTX",
                },
            ),
            SlideRecipe(
                id="statement",
                title="Meaning and appearance remain separate",
                semantic_type="statement",
                content={
                    "hero": "CONTENT ≠ DESIGN",
                    "support": "Recipe plus Design DNA",
                    "evidence": "NO FIXED THEME",
                },
            ),
            SlideRecipe(
                id="process",
                title="Layout selection uses content and history",
                semantic_type="process",
                slots=3,
                content={
                    "items": [
                        {"title": "SPEC", "detail": "message", "color_role": "secondary"},
                        {"title": "DNA", "detail": "appearance", "color_role": "accent"},
                        {"title": "BUILD", "detail": "compiler", "color_role": "primary"},
                    ]
                },
            ),
            SlideRecipe(
                id="status",
                title="Quality gates remain mandatory",
                semantic_type="status",
                component="status_ledger",
                content={
                    "headers": ["GATE", "STATUS"],
                    "rows": [["Compiler", "PASS"], ["Render", "PASS"]],
                },
            ),
        ),
    )


class RecipeTests(unittest.TestCase):
    def test_recipe_rejects_visual_tokens(self):
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="bad",
                title="Bad recipe",
                semantic_type="statement",
                content={"palette": {"primary": "FF0000"}},
            )
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="bad-coordinates",
                title="Bad recipe",
                semantic_type="statement",
                content={"x": 1.0, "hero": "text"},
            )
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="bad-size",
                title="Bad recipe",
                semantic_type="statement",
                content={"evidenceSizePt": 30},
            )
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="bad-font",
                title="Bad recipe",
                semantic_type="statement",
                content={"hero_font_family": "Arial"},
            )
        unsafe = DeckRecipe(
            title="Unsafe content item",
            slides=(
                SlideRecipe(
                    id="unsafe",
                    title="Unsafe",
                    semantic_type="process",
                    content={
                        "items": [
                            ContentItem("RAW HEX", "forbidden", "FF0000"),
                            ContentItem("SAFE", "role", "primary"),
                        ]
                    },
                ),
            ),
        )
        with self.assertRaises(LayoutError):
            RecipeAssembler(design_for("technical")).compile(unsafe)
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="direct-size",
                title="Direct size",
                semantic_type="statement",
                content={"evidence_size_pt": 72},
            )

    def test_direct_recipe_construction_is_strict_and_immutable(self):
        with self.assertRaises(LayoutError):
            SlideRecipe(
                id="bad-bool",
                title="Bad bool",
                semantic_type="statement",
                allow_repeat="false",
            )
        mutable = {"hero": "Original", "nested": {"value": "locked"}}
        slide = SlideRecipe(
            id="immutable",
            title="Immutable",
            semantic_type="statement",
            content=mutable,
        )
        mutable["hero"] = "Changed"
        mutable["nested"]["value"] = "changed"
        self.assertEqual(slide.content["hero"], "Original")
        self.assertEqual(slide.content["nested"]["value"], "locked")
        with self.assertRaises(TypeError):
            slide.content["hero"] = "mutate"

    def test_component_booleans_require_exact_boolean_values(self):
        for content in (
            {"hero": "A", "support": "B", "support_bold": "false"},
            {
                "hero_spans": [
                    {
                        "text": "A",
                        "role": "metric",
                        "color_role": "primary",
                        "bold": "false",
                    }
                ]
            },
        ):
            recipe = DeckRecipe(
                title="Boolean validation",
                slides=(
                    SlideRecipe(
                        id="statement",
                        title="Statement",
                        semantic_type="statement",
                        content=content,
                    ),
                ),
            )
            with self.assertRaises(LayoutError):
                RecipeAssembler(design_for("technical")).compile(recipe)

    def test_statement_semantic_colors_adapt_without_changing_recipe(self):
        base = design_for("technical")
        low_contrast = replace(
            base,
            palette=replace(base.palette, primary=base.palette.canvas),
        )
        recipe = DeckRecipe(
            title="Adaptive statement",
            slides=(
                SlideRecipe(
                    id="statement",
                    title="Adaptive statement",
                    semantic_type="statement",
                    content={
                        "hero": "PRIMARY SIGNAL",
                        "support": "Readable support",
                    },
                ),
            ),
        )
        compiler = RecipeAssembler(low_contrast).compile(recipe)
        report = compiler.validate(min_layout_families=1)
        self.assertFalse(report.errors)

    def test_same_recipe_compiles_with_distinct_designs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            first = temp / "technical.pptx"
            second = temp / "editorial.pptx"
            recipe = sample_recipe()
            first_report = RecipeAssembler(design_for("technical")).compile_to(
                recipe,
                first,
            )
            second_report = RecipeAssembler(design_for("editorial")).compile_to(
                recipe,
                second,
            )
            self.assertFalse(first_report.errors)
            self.assertFalse(second_report.errors)
            self.assertNotEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                first_xml = archive.read("ppt/slides/slide1.xml")
            with zipfile.ZipFile(second) as archive:
                second_xml = archive.read("ppt/slides/slide1.xml")
            self.assertNotEqual(first_xml, second_xml)

    def test_selector_penalizes_recent_layout_repetition(self):
        selector = AdaptiveLayoutSelector()
        comparison = SlideRecipe(
            id="comparison",
            title="Compare",
            semantic_type="comparison",
        )
        components = ComponentRegistry()
        blueprints = BlueprintLibrary(design_for("technical").layout)
        first = selector.choose(
            comparison,
            [],
            Counter(),
            slots=4,
            component="comparison",
            components=components,
            blueprints=blueprints,
        )
        second = selector.choose(
            comparison,
            [first],
            Counter({first.family: 1}),
            slots=4,
            component="comparison",
            components=components,
            blueprints=blueprints,
        )
        self.assertEqual(first.family, "comparison")
        self.assertEqual(second.family, "comparison")
        self.assertNotEqual(first.variant, second.variant)

    def test_json_recipe_has_no_design_dependency(self):
        payload = {
            "title": "JSON Recipe",
            "expected_slides": 1,
            "slides": [
                {
                    "id": "statement",
                    "title": "JSON works",
                    "semantic_type": "statement",
                    "content": {
                        "hero": "Semantic",
                        "support": "No visual tokens",
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "recipe.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            recipe = DeckRecipe.from_json(path)
            self.assertEqual(recipe.slides[0].semantic_type, "statement")

    def test_json_recipe_rejects_coercion_and_unknown_keys(self):
        with self.assertRaises(LayoutError):
            SlideRecipe.from_dict(
                {
                    "id": "bad",
                    "title": "Bad",
                    "semantic_type": "statement",
                    "allow_repeat": "false",
                }
            )
        with self.assertRaises(LayoutError):
            SlideRecipe.from_dict(
                {
                    "id": "bad",
                    "title": "Bad",
                    "semantic_type": "statement",
                    "card_grid": "false",
                }
            )
        with self.assertRaises(LayoutError):
            DeckRecipe.from_dict(
                {
                    "title": "Bad",
                    "slides": [],
                    "max_card_grid_ratio": "nan",
                }
            )
        with self.assertRaises(LayoutError):
            DeckRecipe.from_dict(
                {
                    "title": "Bad",
                    "slides": [],
                    "misspelled_key": True,
                }
            )

    def test_selector_respects_component_layout_contracts(self):
        recipe = DeckRecipe(
            title="Component Contracts",
            slides=(
                SlideRecipe(
                    id="status-one",
                    title="Status one",
                    semantic_type="status",
                    content={
                        "headers": ["A", "B"],
                        "rows": [["1", "2"]],
                    },
                ),
                SlideRecipe(
                    id="status-two",
                    title="Status two",
                    semantic_type="status",
                    content={
                        "headers": ["A", "B"],
                        "rows": [["1", "2"]],
                    },
                ),
                SlideRecipe(
                    id="code",
                    title="Code with explanation",
                    semantic_type="code",
                    content={
                        "lines": ["x = 1"],
                        "explanations": [
                            {"title": "Why", "detail": "Because"}
                        ],
                    },
                ),
                SlideRecipe(
                    id="architecture",
                    title="Pipeline architecture",
                    semantic_type="architecture",
                    content={
                        "nodes": {
                            "input": {"title": "IN", "detail": ""},
                            "core": {"title": "CORE", "detail": ""},
                            "output": {"title": "OUT", "detail": ""},
                        }
                    },
                ),
                SlideRecipe(
                    id="process",
                    title="Five steps",
                    semantic_type="process",
                    content={
                        "items": [
                            {"title": f"S{index}", "detail": ""}
                            for index in range(1, 6)
                        ]
                    },
                ),
            ),
        )
        compiler = RecipeAssembler(design_for("technical")).compile(recipe)
        records = compiler.records
        self.assertEqual(
            [(records[0].family, records[0].variant), (records[1].family, records[1].variant)],
            [("matrix", "table"), ("matrix", "table")],
        )
        self.assertEqual((records[2].family, records[2].variant), ("code", "split"))
        self.assertEqual(
            (records[3].family, records[3].variant),
            ("architecture", "pipeline"),
        )
        self.assertEqual(records[4].family, "process")

    def test_custom_component_can_declare_required_regions(self):
        components = ComponentRegistry()
        components.register(
            "code-with-explain",
            lambda canvas, payload: None,
            allowed_families=["code"],
            required_regions=["code", "explain"],
        )
        recipe = DeckRecipe(
            title="Custom component",
            slides=(
                SlideRecipe(
                    id="custom-code",
                    title="Custom code",
                    semantic_type="code",
                    component="code-with-explain",
                    content={},
                ),
            ),
        )
        compiler = RecipeAssembler(
            design_for("technical"),
            components=components,
        ).compile(recipe)
        self.assertEqual(compiler.records[0].variant, "split")

    def test_matrix_weights_must_be_positive_finite_numbers(self):
        for weights in ([0, 0], [-1, 2], [float("nan"), 1], ["1", "2"]):
            with self.subTest(weights=weights):
                recipe = DeckRecipe(
                    title="Bad matrix",
                    slides=(
                        SlideRecipe(
                            id="matrix",
                            title="Bad weights",
                            semantic_type="matrix",
                            content={
                                "headers": ["A", "B"],
                                "rows": [["1", "2"]],
                                "column_weights": weights,
                            },
                        ),
                    ),
                )
                with self.assertRaises(LayoutError):
                    RecipeAssembler(design_for("technical")).compile(recipe)

    def test_font_metrics_measure_or_fallback_cleanly(self):
        metrics = FontMetrics()
        measured = metrics.measure_points("Hello", "DejaVuSans.ttf", 14)
        if measured is not None:
            self.assertGreater(measured, 0)
        self.assertIsNone(
            metrics.measure_points(
                "Hello",
                "definitely-not-a-real-font-family-12345",
                14,
            )
        )
        regular = metrics.measure_points("Wide text", "DejaVuSans.ttf", 20)
        bold = metrics.measure_points(
            "Wide text",
            "DejaVuSans.ttf",
            20,
            bold=True,
        )
        if regular is not None and bold is not None:
            self.assertGreaterEqual(bold, regular)
        self.assertFalse(metrics._family_matches("Inter", "Interstate"))

    def test_certified_components_compile_across_design_dna(self):
        recipe = DeckRecipe(
            title="Certified Components",
            expected_slides=4,
            min_layout_families=3,
            slides=(
                SlideRecipe(
                    id="resource",
                    title="Resource and projects keep different boundaries",
                    semantic_type="resource_hierarchy",
                    component="resource_hierarchy",
                    content={
                        "resource": {
                            "title": "RESOURCE",
                            "detail": "governance boundary",
                            "color_role": "primary",
                        },
                        "projects": [
                            {
                                "title": "PROJECT A",
                                "detail": "team assets",
                                "color_role": "secondary",
                            },
                            {
                                "title": "PROJECT B",
                                "detail": "team assets",
                                "color_role": "accent",
                            },
                        ],
                        "connected": [
                            {
                                "title": "STORAGE",
                                "detail": "separate boundary",
                                "color_role": "warning",
                            },
                            {
                                "title": "SEARCH",
                                "detail": "separate boundary",
                                "color_role": "success",
                            },
                        ],
                        "boundary_label": "CONTROL PLANE ≠ DATA PLANE",
                    },
                ),
                SlideRecipe(
                    id="agent",
                    title="Agent anatomy remains semantic",
                    semantic_type="agent_anatomy",
                    component="agent_anatomy",
                    emphasis="inverse",
                    content={
                        "agent": {
                            "title": "AGENT",
                            "detail": "reason and act",
                            "color_role": "primary",
                        },
                        "left": [
                            {
                                "title": "MODEL",
                                "detail": "reasoning",
                                "color_role": "accent",
                            },
                            {
                                "title": "INSTRUCTIONS",
                                "detail": "constraints",
                                "color_role": "secondary",
                            },
                        ],
                        "right": [
                            {
                                "title": "TOOLS",
                                "detail": "actions",
                                "color_role": "primary",
                            },
                            {
                                "title": "KNOWLEDGE",
                                "detail": "grounding",
                                "color_role": "accent",
                            },
                        ],
                        "foundation": "STATE · IDENTITY · OBSERVABILITY",
                    },
                ),
                SlideRecipe(
                    id="security",
                    title="Security is layered",
                    semantic_type="security_layers",
                    component="security_layers",
                    slots=5,
                    content={
                        "items": [
                            {"title": "IDENTITY", "detail": "RBAC", "color_role": "primary"},
                            {"title": "NETWORK", "detail": "VNet", "color_role": "accent"},
                            {"title": "DATA", "detail": "CMK", "color_role": "warning"},
                            {"title": "RUNTIME", "detail": "isolation", "color_role": "secondary"},
                            {"title": "GUARDRAIL", "detail": "controls", "color_role": "danger"},
                        ]
                    },
                ),
                SlideRecipe(
                    id="quality",
                    title="Quality is a closed loop",
                    semantic_type="quality_loop",
                    component="quality_loop",
                    slots=4,
                    content={
                        "items": [
                            {"title": "TRACE", "detail": "spans", "color_role": "secondary"},
                            {"title": "EVAL", "detail": "scores", "color_role": "accent"},
                            {"title": "MONITOR", "detail": "drift", "color_role": "warning"},
                            {"title": "IMPROVE", "detail": "promote", "color_role": "success"},
                        ]
                    },
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            for style in ("technical", "editorial"):
                report = RecipeAssembler(design_for(style)).compile_to(
                    recipe,
                    temp / f"{style}.pptx",
                )
                self.assertFalse(report.errors)


if __name__ == "__main__":
    unittest.main()
