from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "research_scenarios.json"
ADAPTIVE_SKILL = SKILL.parents[1] / "adaptive-presentation" / "SKILL.md"
DEMO_SKILL = SKILL.parents[1] / "ai-platform-demo" / "SKILL.md"
REPOSITORY_ROOT = SKILL.parents[3]
CLI_MCP_CONFIG = REPOSITORY_ROOT / ".github" / "mcp.json"
VSCODE_MCP_CONFIG = REPOSITORY_ROOT / ".vscode" / "mcp.json"
FACT_LEDGER_SCHEMA = SKILL.parent / "schema" / "fact-ledger.schema.json"
FACT_LEDGER_EXAMPLE = SKILL.parent / "examples" / "fact-ledger.example.json"


class WebSearchSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        frontmatter = cls.skill.split("---", 2)[1]
        description_line = next(
            line for line in frontmatter.splitlines() if line.startswith("description:")
        )
        cls.description = description_line.split(":", 1)[1].strip().strip('"')

    def test_copilot_search_capabilities_are_prioritized(self):
        web_search = self.skill.index(
            "Copilot이 제공하는 general web search tool(예: `web_search`)"
        )
        research_agent = self.skill.index(
            "Copilot CLI의 `/research` 또는 web source를 지원하는 Research agent"
        )
        domain_search = self.skill.index("도메인 전용 검색")

        self.assertLess(web_search, research_agent)
        self.assertLess(research_agent, domain_search)
        self.assertIn("GitHub Copilot CLI와 VS Code Copilot Chat/Agent", self.skill)

    def test_public_serp_scraping_is_forbidden(self):
        self.assertIn("공개 검색 결과 페이지(SERP)", self.skill)
        self.assertIn("직접 조회하지 않는다", self.skill)
        self.assertNotIn("https://www.google.com/search", self.skill)
        self.assertNotIn("https://html.duckduckgo.com", self.skill)
        self.assertNotIn("DuckDuckGo HTML로 전환", self.skill)

    def test_search_results_require_canonical_source_verification(self):
        self.assertIn("검색 provider의 답변만으로 검증 완료 처리하지 않고", self.skill)
        self.assertIn("canonical 원문을 직접 확인한다", self.skill)

    def test_foundational_research_has_a_fact_ledger_contract(self):
        self.assertIn("Research Brief", self.skill)
        self.assertIn("Fact Ledger 계약", self.skill)

        for field in (
            "ID",
            "Type",
            "Claim",
            "Evidence",
            "Source",
            "Publisher",
            "Published/updated",
            "Accessed",
            "Scope/status",
            "Confidence",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)

        self.assertIn("`Fact`·`Inference`·`Assumption`", self.skill)
        self.assertIn("fact-ledger.md", self.skill)
        self.assertIn("fact-ledger.json", self.skill)
        self.assertIn("timezone이 포함된 ISO 8601 timestamp", self.skill)
        self.assertIn("page·section·", self.skill)
        self.assertIn("table 등 원문 위치(locator)", self.skill)
        self.assertIn("`YYYY-MM-DD`", self.skill)
        self.assertIn("`High`", self.skill)
        self.assertIn("`Medium`", self.skill)
        self.assertIn("`Low`", self.skill)

        schema = json.loads(FACT_LEDGER_SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(FACT_LEDGER_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(example["schemaVersion"], 1)
        self.assertGreaterEqual(len(example["facts"]), 2)
        self.assertEqual(
            set(schema["properties"]["facts"]["items"]["required"]),
            set(example["facts"][0]),
        )

    def test_research_has_explicit_completion_criteria(self):
        self.assertIn("**완료 판정**", self.skill)
        self.assertIn("필수 조사 축마다", self.skill)
        self.assertIn("각 사실 주장에 최소 한 개의 canonical 원문", self.skill)
        self.assertIn("독립 출처로 교차검증", self.skill)
        self.assertIn("미확보 범위와 탐색 한계", self.skill)
        self.assertNotIn("결과 없음→쿼리 재구성 1회", self.skill)

    def test_skill_triggers_include_foundational_research(self):
        self.assertIn("기초자료 조사", self.description)
        self.assertIn("자료 검색/수집", self.description)
        self.assertIn("고객/기업 조사", self.description)
        self.assertIn("시장 규모", self.description)

    def test_downstream_skills_preserve_common_ledger_fields(self):
        common_fields = (
            "ID",
            "Type",
            "Claim",
            "Evidence",
            "Source",
            "Publisher",
            "Published/updated",
            "Accessed",
            "Scope/status",
            "Confidence",
        )
        for downstream in (ADAPTIVE_SKILL, DEMO_SKILL):
            content = downstream.read_text(encoding="utf-8")
            for field in common_fields:
                with self.subTest(skill=downstream.parent.name, field=field):
                    self.assertIn(field, content)

    def test_research_scenario_policies(self):
        scenarios = json.loads(FIXTURES.read_text(encoding="utf-8"))
        normalized_skill = " ".join(self.skill.split())
        for scenario in scenarios:
            for expected_policy in scenario["expected_policy"]:
                with self.subTest(
                    scenario=scenario["name"], expected_policy=expected_policy
                ):
                    self.assertIn(" ".join(expected_policy.split()), normalized_skill)

    def test_only_first_party_documentation_mcp_is_bundled(self):
        cli_config = json.loads(CLI_MCP_CONFIG.read_text(encoding="utf-8"))
        vscode_config = json.loads(VSCODE_MCP_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(set(cli_config["mcpServers"]), {"microsoft-learn"})
        self.assertEqual(set(vscode_config["servers"]), {"microsoft-learn"})
        self.assertNotIn("search MCP/API", self.skill)


if __name__ == "__main__":
    unittest.main()
