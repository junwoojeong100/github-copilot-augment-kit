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
            "spec": {"design": {"theme": "light"}},
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_pack_cannot_replace_root_with_customer_sections(self):
        document = {
            "_pack": {"id": "bad", "name": "Bad Pack"},
            "spec": {
                "$replace": {
                    "meta": {"customer": "Injected"},
                    "design": {"theme": "light"},
                    "story": {"frame": "Injected"},
                }
            },
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_pack(document, Path("bad-pack.json"))

    def test_customer_overlay_must_not_define_design(self):
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
                "design": {"theme": "light"},
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
            "design": {"theme": "dark-dimmed"},
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
        self.assertEqual(result["design"], {"theme": "dark-dimmed"})

    def test_apply_customer_layer_rejects_design_defensively(self):
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.apply_customer_layer(
                {
                    "meta": {},
                    "design": {"theme": "dark-dimmed"},
                    "story": {},
                },
                {
                    "meta": {},
                    "story": {},
                    "design": {"theme": "light"},
                },
                [],
            )

    def test_stale_research_override_is_repository_scoped(self):
        self.assertTrue(
            compose_demo_spec.stale_research_allowed(
                SKILL_ROOT / "examples" / "overlay.json",
                SKILL_ROOT,
            )
        )
        self.assertFalse(
            compose_demo_spec.stale_research_allowed(
                SKILL_ROOT.parent / "customer-overlay.json",
                SKILL_ROOT,
            )
        )

    def test_stale_override_does_not_allow_future_research(self):
        document = {
            "_customer": {
                "research": {
                    "mode": "live",
                    "checkedAt": "2999-01-01T00:00:00Z",
                    "sourceUrls": ["https://example.com/a", "https://example.com/b"],
                }
            },
            "spec": {"meta": {}, "story": {}},
        }
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_customer(
                document,
                [],
                allow_stale=True,
                max_age_hours=24,
            )

    def test_ipv6_source_url_is_canonicalized_safely(self):
        self.assertEqual(
            compose_demo_spec.canonical_source_url("https://[2001:db8::1]:443/a#fragment"),
            "https://[2001:db8::1]/a",
        )

    def test_output_paths_require_safe_extensions_and_no_aliases(self):
        inputs = {SKILL_ROOT / "examples" / "base.json"}
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_output_paths(
                SKILL_ROOT / "work" / "spec.txt", None, inputs
            )
        with self.assertRaises(compose_demo_spec.ComposeError):
            compose_demo_spec.validate_output_paths(
                SKILL_ROOT / "work" / "spec.json",
                SKILL_ROOT / "work" / "SPEC.JSON",
                inputs,
            )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "base.json"
            output = Path(directory) / "output.json"
            source.write_text("{}", encoding="utf-8")
            output.hardlink_to(source)
            with self.assertRaises(compose_demo_spec.ComposeError):
                compose_demo_spec.validate_output_paths(
                    output, Path(directory) / "demo.html", {source}
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
