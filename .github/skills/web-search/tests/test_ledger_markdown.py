from __future__ import annotations

import contextlib
import copy
import html
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_fact_ledger as validator  # noqa: E402


class LedgerMarkdownTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.value = json.loads(
            (SKILL_ROOT / "examples" / "fact-ledger.example.json").read_text(encoding="utf-8")
        )
        self.source = self.root / "fact-ledger.json"
        self.source.write_text(json.dumps(self.value), encoding="utf-8")

    def run_cli(self, output: Path) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = validator.main([
                str(self.source), "--markdown-output", str(output),
            ])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_view_preserves_all_entry_types_status_and_provenance(self):
        normalized = validator.validate_ledger(self.value)
        original = copy.deepcopy(normalized)
        markdown = validator.render_markdown(normalized)
        self.assertEqual(normalized, original)
        for expected in (
            "| ID | Type | Claim | Evidence | Sources/Basis | Scope/status | Confidence | Status |",
            "Schema version: 1",
            "Checked at: 2026-08-01T16:00:00+09:00",
            "| F-001 | Fact |",
            "| I-001 | Inference |",
            "| A-001 | Assumption |",
            "Basis: F-001, F-002",
            "Owner: Artifact producer",
            "Validation needed: Confirm outbound HTTPS access",
            "Unresolved<br>Reason: Connectivity must be checked",
            "published/updated: 확인 불가",
            "accessed: 2026-08-01",
            "locator: Overview",
            "[Microsoft Learn MCP Server overview](<https://learn.microsoft.com/training/support/mcp>)",
            "## Excluded sources",
            "No canonical original document was available.",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, markdown)
        rows = [line for line in markdown.splitlines() if line.startswith(("| F-", "| I-", "| A-"))]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(line.count("|") == 9 for line in rows))

    def test_multisource_and_legacy_provenance_are_rendered(self):
        first = self.value["facts"][0]
        first["sources"].append(copy.deepcopy(self.value["facts"][1]["sources"][0]))
        second = self.value["facts"][1]
        source = second.pop("sources")[0]
        second["source"] = {key: source[key] for key in ("title", "url", "locator")}
        for key in ("publisher", "publishedOrUpdated", "accessed"):
            second[key] = source[key]
        markdown = validator.render_markdown(validator.validate_ledger(self.value))
        first_row = next(line for line in markdown.splitlines() if line.startswith("| F-001"))
        second_row = next(line for line in markdown.splitlines() if line.startswith("| F-002"))
        self.assertIn("Microsoft Learn MCP Server overview", first_row)
        self.assertIn("<br>[About agent skills]", first_row)
        self.assertIn("GitHub; published/updated:", second_row)

    def test_untrusted_text_and_urls_cannot_break_the_table_or_inject_markup(self):
        entry = self.value["facts"][0]
        entry["claim"] = "A | B\r\n<script>alert(1)</script> [click](javascript:alert(1))"
        entry["evidence"] = "`code` *bold* & <img src=x>"
        entry["sources"][0]["title"] = "Source ](https://evil.example) | <img src=x>"
        entry["sources"][0]["url"] = 'https://example.com/path?q="><img src=x>&v=1|2'
        markdown = validator.render_markdown(validator.validate_ledger(self.value))
        row = next(line for line in markdown.splitlines() if line.startswith("| F-001"))
        self.assertEqual(row.count("|"), 9)
        self.assertIn("A &#124; B<br>&lt;script&gt;", row)
        self.assertIn(r"\[click\](javascript:alert(1))", row)
        self.assertIn(r"\`code\` \*bold\* &amp;", row)
        self.assertIn("%22%3E%3Cimg%20src=x%3E&amp;v=1%7C2", row)
        self.assertNotIn("<script>", markdown)
        self.assertNotIn("<img", markdown)

    def test_link_destination_preserves_literal_entities_in_source_urls(self):
        url = "https://example.com/docs?value=1&amp;literal=2&other=3"
        link = validator._source_link({"title": "Document", "url": url})
        destination = link.split("](<", 1)[1].removesuffix(">)")
        self.assertEqual(html.unescape(destination), url)
        self.assertIn("&amp;amp;literal=2&amp;other=3", destination)

    def test_markdown_export_preserves_source_path_parameters(self):
        url = "https://example.com/report;version=2026?lang=en"
        self.value["facts"][0]["sources"][0]["url"] = url
        self.source.write_text(json.dumps(self.value), encoding="utf-8")
        output = self.root / "fact-ledger.md"

        status, _, stderr = self.run_cli(output)

        self.assertEqual(status, 0, stderr)
        self.assertIn(f"](<{url}>)", output.read_text(encoding="utf-8"))

    def test_export_is_atomic_and_never_changes_the_json_source(self):
        original = self.source.read_bytes()
        output = self.root / "nested" / "fact-ledger.md"
        status, stdout, stderr = self.run_cli(output)
        self.assertEqual(status, 0, stderr)
        self.assertIn("Fact Ledger PASS", stdout)
        self.assertIn("Markdown:", stdout)
        self.assertEqual(output.read_text(), validator.render_markdown(validator.load_ledger(self.source)))
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(list(output.parent.glob("*.tmp")), [])

    def test_source_relative_symlink_and_hardlink_aliases_are_rejected(self):
        symlink = self.root / "symlink.md"
        symlink.symlink_to(self.source)
        hardlink = self.root / "hardlink.md"
        hardlink.hardlink_to(self.source)
        original = self.source.read_bytes()
        for output in (self.source, self.root / "unused" / ".." / self.source.name, symlink, hardlink):
            with self.subTest(output=output):
                status, stdout, stderr = self.run_cli(output)
                self.assertEqual(status, 1)
                self.assertNotIn("PASS", stdout)
                self.assertIn("alias", stderr)
                self.assertEqual(self.source.read_bytes(), original)

    def test_invalid_json_does_not_create_or_replace_a_markdown_view(self):
        self.source.write_text('{"schemaVersion": 1}', encoding="utf-8")
        output = self.root / "fact-ledger.md"
        output.write_text("preserve", encoding="utf-8")
        status, stdout, stderr = self.run_cli(output)
        self.assertEqual(status, 1)
        self.assertEqual(output.read_text(), "preserve")
        self.assertNotIn("PASS", stdout)
        self.assertIn("INVALID", stderr)

    def test_failed_replacement_preserves_existing_view_and_cleans_temporary_file(self):
        output = self.root / "fact-ledger.md"
        output.write_text("preserve", encoding="utf-8")
        with patch.object(Path, "replace", side_effect=OSError("write denied")):
            status, stdout, stderr = self.run_cli(output)
        self.assertEqual(status, 1)
        self.assertEqual(output.read_text(), "preserve")
        self.assertNotIn("PASS", stdout)
        self.assertIn("write denied", stderr)
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_all_supported_decisions_remain_visible(self):
        for status in ("Accepted", "Contested", "Rejected", "Unresolved"):
            value = copy.deepcopy(self.value)
            value["facts"] = [value["facts"][0]]
            value["facts"][0]["status"] = status
            value["facts"][0]["decisionRationale"] = "Decision explanation"
            value["excludedSources"] = []
            markdown = validator.render_markdown(validator.validate_ledger(value))
            self.assertIn(f"{status}<br>Reason: Decision explanation", markdown)
            self.assertIn("## Excluded sources\n\nNone.", markdown)


if __name__ == "__main__":
    unittest.main()
