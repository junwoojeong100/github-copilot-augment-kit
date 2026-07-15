from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import compose_demo_spec  # noqa: E402


class ComposeDemoSpecTests(unittest.TestCase):
    def test_deep_merge_replaces_arrays_and_deletes_keys(self):
        base = {
            "a": {"keep": 1, "remove": 2},
            "formula": {"old": 1},
            "items": [1, 2],
        }
        overlay = {
            "a": {"remove": {"$delete": True}, "added": 3},
            "formula": {"$replace": {"new": 2}},
            "items": [9],
        }
        self.assertEqual(
            compose_demo_spec.deep_merge(base, overlay),
            {
                "a": {"keep": 1, "added": 3},
                "formula": {"new": 2},
                "items": [9],
            },
        )

    def test_pack_cannot_define_customer_design(self):
        document = {
            "_pack": {"id": "bad", "name": "Bad Pack"},
            "spec": {"design": {"theme": "dark"}},
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_pack_cannot_replace_root_with_customer_sections(self):
        document = {
            "_pack": {"id": "bad", "name": "Bad Pack"},
            "spec": {
                "$replace": {
                    "meta": {"customer": "Injected"},
                    "design": {"theme": "dark"},
                    "story": {"frame": "Injected"},
                }
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_customer_overlay_requires_complete_design_dna(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": ["https://example.com/a", "https://example.com/b"],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
                "design": {"theme": "dark"},
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_customer_overlay_requires_customer_visual_tokens(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": ["https://example.com/a", "https://example.com/b"],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
                "design": {
                    "conceptWords": ["a", "b", "c"],
                    "visualMetaphor": "network",
                    "archetype": "trusted-executive",
                    "counterInfluence": "operations",
                    "theme": "dark",
                    "density": "executive",
                    "motion": "balanced",
                    "tokens": {},
                    "avoid": ["x", "y", "z"],
                },
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_customer_required_paths_replace_instead_of_merge(self):
        base = {
            "meta": {"customer": "Base"},
            "design": {"theme": "light"},
            "story": {"frame": "Base"},
            "operations": {
                "hero": {
                    "title": "Base title",
                    "subtitle": "Base subtitle",
                    "icon": "◇",
                }
            },
        }
        customer = {
            "meta": {"customer": "Customer"},
            "design": {"theme": "dark"},
            "story": {"frame": "Customer"},
            "operations": {
                "hero": {
                    "$replace": {
                        "title": "Customer title",
                        "subtitle": "Customer subtitle",
                        "icon": "◇",
                    }
                }
            },
        }
        result = compose_demo_spec.apply_customer_layer(
            base,
            customer,
            ["operations.hero"],
        )
        self.assertEqual(
            result["operations"]["hero"],
            {
                "title": "Customer title",
                "subtitle": "Customer subtitle",
                "icon": "◇",
            },
        )

    def test_forbidden_acronym_uses_token_boundaries(self):
        compose_demo_spec.check_output_leaks(
            {"text": "Spinning reserve is stable."},
            ["SPI"],
        )

    def test_forbidden_term_detects_html_entity_encoding(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.check_output_leaks(
                {"text": "Con&#116;oso"},
                ["Contoso"],
            )

    def test_forbidden_term_detects_inline_tag_splitting(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.check_output_leaks(
                {"text": "Con<b>to</b>so"},
                ["Contoso"],
            )

    def test_research_sources_reject_non_string_values(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": ["https://example.com/a", {}],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
                "design": {
                    "conceptWords": ["a", "b", "c"],
                    "visualMetaphor": "network",
                    "archetype": "trusted-executive",
                    "counterInfluence": "operations",
                    "theme": "dark",
                    "density": "executive",
                    "motion": "balanced",
                    "tokens": {
                        "canvas": "#000000",
                        "canvasAlt": "#111111",
                        "surface": "#222222",
                        "surfaceAlt": "#333333",
                        "ink": "#ffffff",
                        "inkMuted": "#dddddd",
                        "inkFaint": "#aaaaaa",
                        "brand": "#ff0000",
                        "brandAlt": "#cc0000",
                        "accent": "#00ffff",
                        "radius": 12,
                        "navWidth": 250,
                        "fontScale": 1,
                    },
                    "avoid": ["x", "y", "z"],
                },
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_research_sources_reject_invalid_port_and_fragment_duplicates(self):
        base_document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2026-07-15T12:40:00+09:00",
                    "sourceUrls": [
                        "https://example.com:bad/a",
                        "https://example.org/b",
                    ],
                }
            },
            "spec": {
                "meta": {},
                "story": {},
                "design": {
                    "conceptWords": ["a", "b", "c"],
                    "visualMetaphor": "network",
                    "archetype": "trusted-executive",
                    "counterInfluence": "operations",
                    "theme": "dark",
                    "density": "executive",
                    "motion": "balanced",
                    "tokens": {
                        "canvas": "#000000",
                        "canvasAlt": "#111111",
                        "surface": "#222222",
                        "surfaceAlt": "#333333",
                        "ink": "#ffffff",
                        "inkMuted": "#dddddd",
                        "inkFaint": "#aaaaaa",
                        "brand": "#ff0000",
                        "brandAlt": "#cc0000",
                        "accent": "#00ffff",
                        "radius": 12,
                        "navWidth": 250,
                        "fontScale": 1,
                    },
                    "avoid": ["x", "y", "z"],
                },
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                base_document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

        base_document["_customer"]["research"]["sourceUrls"] = [
            "https://example.com/page#one",
            "https://example.com/page#two",
        ]
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                base_document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_repository_example_composes_and_renders(self):
        with tempfile.TemporaryDirectory(prefix="demo-compose-test-") as temp_dir:
            temp = Path(temp_dir)
            spec_output = temp / "demo-spec.json"
            html_output = temp / "demo.html"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPTS / "compose_demo_spec.py"),
                    "--base",
                    str(SKILL_ROOT / "examples" / "precision-manufacturing.example.json"),
                    "--pack",
                    str(SKILL_ROOT / "packs" / "renewable-energy-holdings.pack.json"),
                    "--customer",
                    str(SKILL_ROOT / "examples" / "renewable-energy.customer-overlay.example.json"),
                    "--output",
                    str(spec_output),
                    "--html-output",
                    str(html_output),
                    "--allow-stale-research",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            spec = json.loads(spec_output.read_text(encoding="utf-8"))
            self.assertEqual(spec["meta"]["customer"], "Northstar Energy Holdings")
            self.assertEqual(spec["design"]["archetype"], "trusted-executive")
            self.assertNotIn("Contoso", spec_output.read_text(encoding="utf-8"))
            self.assertIn("energy", spec["agents"]["placeholder"].lower())
            self.assertNotIn("품질·공정", spec["agents"]["placeholder"])
            html = html_output.read_text(encoding="utf-8")
            self.assertIn("Northstar Nexus", html)
            self.assertIn("renewable generation", html)


if __name__ == "__main__":
    unittest.main()
