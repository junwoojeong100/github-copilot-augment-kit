from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "research_scenarios.json"
ADAPTIVE_SKILL = SKILL.parents[1] / "adaptive-presentation" / "SKILL.md"
ADAPTIVE_FULL_OPTIMIZED = (
    ADAPTIVE_SKILL.parent / "reference" / "full-optimized.md"
)
ADAPTIVE_VERIFICATION = ADAPTIVE_SKILL.parent / "reference" / "verification.md"
ADAPTIVE_DECK_SPEC = ADAPTIVE_SKILL.parent / "reference" / "deck-spec.md"
ADAPTIVE_PRODUCTION = ADAPTIVE_SKILL.parent / "reference" / "pptx-production.md"
ADAPTIVE_REFINEMENT = ADAPTIVE_SKILL.parent / "reference" / "refinement.md"
ADAPTIVE_EDITORIAL = ADAPTIVE_SKILL.parent / "reference" / "editorial-business-style.md"
ADAPTIVE_BLUEPRINTS = ADAPTIVE_SKILL.parent / "reference" / "slide-blueprints.md"
CUSTOMER_EVIDENCE = SKILL.parent / "reference" / "customer-evidence.md"
ADAPTIVE_DECK_SCHEMA = ADAPTIVE_SKILL.parent / "schema" / "deck-spec.schema.json"
ADAPTIVE_EXCEPTION_SCHEMA = (
    ADAPTIVE_SKILL.parent / "schema" / "qa-exceptions.schema.json"
)
ADAPTIVE_VISUAL_SCHEMA = (
    ADAPTIVE_SKILL.parent / "schema" / "visual-review.schema.json"
)
REPOSITORY_ROOT = SKILL.parents[3]
COPILOT_INSTRUCTIONS = REPOSITORY_ROOT / ".github" / "copilot-instructions.md"
README = REPOSITORY_ROOT / "README.md"
CLI_MCP_CONFIG = REPOSITORY_ROOT / ".github" / "mcp.json"
VSCODE_MCP_CONFIG = REPOSITORY_ROOT / ".vscode" / "mcp.json"
FACT_LEDGER_SCHEMA = SKILL.parent / "schema" / "fact-ledger.schema.json"
FACT_LEDGER_EXAMPLE = SKILL.parent / "examples" / "fact-ledger.example.json"
FACT_LEDGER_VALIDATOR = SKILL.parent / "scripts" / "validate_fact_ledger.py"
sys.path.insert(0, str(FACT_LEDGER_VALIDATOR.parent))
import validate_fact_ledger  # noqa: E402


class WebSearchSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        frontmatter = cls.skill.split("---", 2)[1]
        description_line = next(
            line for line in frontmatter.splitlines() if line.startswith("description:")
        )
        cls.description = description_line.split(":", 1)[1].strip().strip('"')

    def test_search_routing_prefers_shortest_official_path(self):
        canonical = self.skill.index("알려진 canonical URL·공식 index")
        domain_search = self.skill.index("도메인 공식 검색")
        web_search = self.skill.index("general web search tool")
        research_agent = self.skill.index(
            "여러 독립 조사 축을 병렬 수집할 때만 `/research`"
        )

        self.assertLess(canonical, domain_search)
        self.assertLess(domain_search, web_search)
        self.assertLess(web_search, research_agent)
        self.assertIn("GitHub Copilot CLI와 VS Code Copilot Chat/Agent", self.skill)

    def test_public_serp_scraping_is_forbidden(self):
        self.assertIn("공개 검색 결과 페이지(SERP)", self.skill)
        self.assertIn("직접 조회하지 않는다", self.skill)
        self.assertNotIn("https://www.google.com/search", self.skill)
        self.assertNotIn("https://html.duckduckgo.com", self.skill)
        self.assertNotIn("DuckDuckGo HTML로 전환", self.skill)

    def test_search_results_require_canonical_source_verification(self):
        self.assertIn("검색 결과·snippet·AI 요약은 URL 발견용이며 근거가 아니다", self.skill)
        self.assertIn("canonical", self.skill)

    def test_empty_page_shell_is_not_verified_evidence(self):
        content = CUSTOMER_EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("HTTP 성공이나 URL 존재만으로 원문 확인을 판정하지 않는다", self.skill)
        self.assertIn("접근 제한 우회에는 사용하지 않는다", self.skill)
        self.assertIn("KPI 패널·표", content)
        self.assertIn("locator", content)
        self.assertIn("JS challenge·CAPTCHA·403·429는 우회·반복하지 않는다", content)
        self.assertIn("축별 두 가지 retrieval 전략", content)

    def test_customer_evidence_keeps_adoption_and_metric_scope(self):
        content = CUSTOMER_EVIDENCE.read_text(encoding="utf-8")
        for term in (
            "공개 고객 사례", "초기 내부 결과", "협력·계획·출시 발표",
            "공급자·모델 catalog", "제안용 구성·매트릭스",
            "분모·단위·기간·지역·표본·비교 기준·측정 주체·업무 범위",
            "특정 제품 하나가 성과를 만들었다고 단정하지 않는다",
            "검증된 출처 건수는 검증된 제품 운영 도입 건수가 아니다",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_customer_evidence_uses_existing_ledger_fields(self):
        content = CUSTOMER_EVIDENCE.read_text(encoding="utf-8")
        schema = json.loads(FACT_LEDGER_SCHEMA.read_text(encoding="utf-8"))
        fields = schema["$defs"]["ledgerEntry"]["properties"]
        for field in (
            "scopeOrStatus", "evidence", "decisionRationale",
            "assumptionOwner", "validationNeeded", "publishedOrUpdated", "accessed",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", content)
                self.assertIn(field, fields)
        self.assertNotIn("`caveats`", content)
        self.assertNotIn("`scope`", content)
        self.assertIn("`Unresolved`", content)
        self.assertIn("확인 불가", content)
        self.assertIn("확정 성과 제목·차트·ROI 계산의 근거가 아니며", content)

    def test_untrusted_web_content_cannot_direct_agent_actions(self):
        self.assertIn("untrusted data", self.skill)
        self.assertIn("prompt injection", self.skill)
        self.assertIn("도구 실행·파일 변경·로그인·업로드·secret 요청", self.skill)

    def test_foundational_research_has_a_fact_ledger_contract(self):
        self.assertIn("Research Brief", self.skill)
        self.assertIn("Fact Ledger 계약", self.skill)

        for field in ("ID", "Type", "Claim", "Evidence", "Sources/Basis", "Scope/status", "Confidence", "Status"):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)

        self.assertIn("`Fact`·`Inference`·`Assumption`", self.skill)
        self.assertIn("fact-ledger.md", self.skill)
        self.assertIn("validate_fact_ledger.py", self.skill)
        self.assertIn("locator", self.skill)
        self.assertIn("basisIds", self.skill)
        self.assertIn("assumptionOwner", self.skill)
        self.assertIn("validationNeeded", self.skill)
        self.assertIn("`High`", self.skill)
        self.assertIn("`Medium`", self.skill)
        self.assertIn("`Low`", self.skill)

        schema = json.loads(FACT_LEDGER_SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(FACT_LEDGER_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(example["schemaVersion"], 1)
        self.assertGreaterEqual(len(example["facts"]), 4)
        mutual_exclusions = {
            tuple(rule["required"])
            for rule in schema["$defs"]["ledgerEntry"]["allOf"][1]["not"]["anyOf"]
        }
        self.assertEqual(
            mutual_exclusions,
            {
                ("sources", "source"),
                ("sources", "publisher"),
                ("sources", "publishedOrUpdated"),
                ("sources", "accessed"),
            },
        )
        self.assertTrue(FACT_LEDGER_VALIDATOR.is_file())
        normalized = validate_fact_ledger.validate_ledger(example)
        self.assertEqual(len(normalized["facts"]), len(example["facts"]))

    def test_research_has_explicit_completion_criteria(self):
        self.assertIn("## 완료 판정", self.skill)
        self.assertIn("필수 조사 축마다", self.skill)
        self.assertIn("결론 영향 사실은 canonical 원문", self.skill)
        self.assertIn("source budget", self.skill)
        self.assertIn("축별 두 가지 retrieval 전략", self.skill)

    def test_freshness_dimensions_are_explicit(self):
        self.assertIn("가격은 지역·통화·기준일", self.skill)
        self.assertIn("제품·버전·지역·GA/Preview·확인 시각", self.skill)
        self.assertIn("관할·시행일", self.skill)
        self.assertIn("기간·단위·표본·방법론", self.skill)

    def test_skill_triggers_include_foundational_research(self):
        self.assertIn("기초자료 조사", self.description)
        self.assertIn("자료 검색/수집", self.description)
        self.assertIn("고객/기업 조사", self.description)
        self.assertIn("시장 규모", self.description)

    def test_skill_contracts_are_concise_and_bounded(self):
        limits = {
            SKILL: 100,
            ADAPTIVE_SKILL: 120,
        }
        for skill, limit in limits.items():
            content = skill.read_text(encoding="utf-8")
            with self.subTest(skill=skill.parent.name):
                self.assertLessEqual(len(content.splitlines()), limit)
                self.assertIn("NOT WHEN:", content.split("---", 2)[1])
                workflow_headings = re.findall(
                    r"^## .*워크플로.*$", content, flags=re.MULTILINE
                )
                self.assertEqual(len(workflow_headings), 1)

    def test_skill_catalog_matches_available_skills(self):
        available = {
            path.parent.name for path in SKILL.parents[1].glob("*/SKILL.md")
        }
        self.assertEqual(available, {SKILL.parent.name, ADAPTIVE_SKILL.parent.name})
        readme = README.read_text(encoding="utf-8")
        skill_table = readme.split("### [Skills]", 1)[1].split("\n---", 1)[0]
        documented = set(re.findall(r"^\| \*\*([^*]+)\*\* \|", skill_table, re.MULTILINE))
        self.assertEqual(documented, available)
        instructions = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        skill_section = instructions.split("## 스킬", 1)[1]
        instructed = set(re.findall(r"^- ([\w-]+):", skill_section, re.MULTILINE))
        self.assertEqual(instructed, available)

    def test_downstream_skill_delegates_search_backend_selection(self):
        skill_content = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        guide_content = ADAPTIVE_FULL_OPTIMIZED.read_text(encoding="utf-8")
        combined = f"{skill_content}\n{guide_content}"
        self.assertIn("검색 backend", skill_content)
        self.assertIn("`web-search`", skill_content)
        self.assertNotIn("Research agent", combined)
        self.assertNotIn("/research", combined)
        self.assertNotIn("/fleet", combined)

    def test_performance_metrics_are_optional(self):
        content = ADAPTIVE_FULL_OPTIMIZED.read_text(encoding="utf-8")
        self.assertIn("선택적 시간 측정", content)
        self.assertIn("완료 조건", content)

    def test_downstream_skill_keeps_mapping_outside_common_ledger(self):
        content = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        self.assertIn("공통 Fact Ledger 계약", content)
        self.assertIn("storyline과 deck spec", content)
        self.assertIn("Ledger를 확장하지 않고", content)
        self.assertNotIn("| ID | Type | Claim |", content)

    def test_factcheck_policy_is_risk_scoped(self):
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("최신성·수치·논쟁성·의사결정 영향", content)
        self.assertIn("단순·저위험 답변에는 표를 붙이지 않는다", content)
        self.assertNotIn("팩트체크 (항상)", content)

    def test_xhigh_execution_contract_is_bounded_and_read_only_safe(self):
        content = COPILOT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("위험과 복잡도에 비례한 사고", content)
        self.assertIn("질문·설명·검토 요청은 read-only", content)
        self.assertIn("acceptance criteria", content)
        self.assertIn("validator·schema", content)
        self.assertIn("사용자가 요청한 경우에만 수행", content)

    def test_adaptive_skill_exposes_canonical_session_and_qa_contract(self):
        content = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        verification = ADAPTIVE_VERIFICATION.read_text(encoding="utf-8")
        self.assertIn("client가 제공한 artifact 디렉터리", content)
        self.assertIn("scripts/verify_deck.py", content)
        self.assertIn("--deck-spec", content)
        self.assertIn("내부 Fact ID는 노출하지 않는다", content)
        self.assertIn("finding ID", verification)
        self.assertIn("visual-review.json", verification)

        deck_schema = json.loads(ADAPTIVE_DECK_SCHEMA.read_text(encoding="utf-8"))
        exception_schema = json.loads(
            ADAPTIVE_EXCEPTION_SCHEMA.read_text(encoding="utf-8")
        )
        visual_schema = json.loads(
            ADAPTIVE_VISUAL_SCHEMA.read_text(encoding="utf-8")
        )
        deck_contract = ADAPTIVE_DECK_SPEC.read_text(encoding="utf-8")
        self.assertEqual(deck_schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(
            exception_schema["properties"]["schemaVersion"]["const"], 1
        )
        self.assertEqual(visual_schema["properties"]["schemaVersion"]["const"], 1)
        self.assertIn("claimIds", deck_contract)
        self.assertIn("template-profile.json", deck_contract)
        self.assertIn("findingId", deck_contract)

    def test_existing_deck_refinement_preserves_meaning_and_originals(self):
        content = ADAPTIVE_REFINEMENT.read_text(encoding="utf-8")
        skill = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        self.assertIn("reference/refinement.md", skill)
        for term in (
            "내용 원본", "디자인 참고", "source-inventory.json",
            "content-coverage.json", "원본 항목", "의미 단위의 보존",
            "기존 파일을 덮어쓰지 않고", "SHA-256",
            "발표 시간", "명시적 덮어쓰기 대상 외",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)
        self.assertIn("모든 덱의 완료 상태를 구분한다", content)
        self.assertIn("작업 소유 임시 PDF·QA 이미지 경로만 정리한다", content)

    def test_readability_targets_do_not_imply_automated_coverage(self):
        skill = ADAPTIVE_SKILL.read_text(encoding="utf-8")
        guide = ADAPTIVE_REFINEMENT.read_text(encoding="utf-8")
        verification = " ".join(
            ADAPTIVE_VERIFICATION.read_text(encoding="utf-8").split()
        )
        for term in ("7:1", "4.5:1", "18~23pt", "15pt"):
            with self.subTest(term=term):
                self.assertIn(term, ADAPTIVE_PRODUCTION.read_text(encoding="utf-8"))
        for content in (skill, guide):
            self.assertIn("pptx-production.md#typography", content)
            self.assertIn("pptx-production.md#contrast", content)
        self.assertIn("미측정 조합", guide)
        self.assertIn("canonical runner의 자동 검사 범위가 아니다", verification)
        self.assertIn("키워드 일치만으로 의미 보존을 판정하지 않음", verification)
        self.assertIn("실제 발표 시간 보장 아님", verification)

    def test_detailed_style_rules_are_centralized_without_changing_contracts(self):
        production = ADAPTIVE_PRODUCTION.read_text(encoding="utf-8")
        self.assertIn("상세 편집 기준의 정본", production)
        self.assertIn("Apple SD Gothic Neo · 27pt · Bold", production)
        self.assertIn("120~600자·4~6문장", production)
        schema = json.loads(ADAPTIVE_DECK_SCHEMA.read_text(encoding="utf-8"))
        default = schema["properties"]["fontPolicy"]["properties"]["leadingMessage"]["default"]
        self.assertEqual(default, {
            "fontFamily": "Apple SD Gothic Neo", "sizePt": 27, "bold": True,
        })
        for path in (
            ADAPTIVE_SKILL, ADAPTIVE_REFINEMENT, ADAPTIVE_EDITORIAL,
            ADAPTIVE_BLUEPRINTS, ADAPTIVE_DECK_SPEC, ADAPTIVE_VERIFICATION, README,
        ):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("pptx-production.md#typography", content)
                for repeated_rule in ("18~23pt", "4.5:1", "120~600자"):
                    self.assertNotIn(repeated_rule, content)

    def test_ledger_json_is_the_source_of_the_generated_markdown_view(self):
        for path in (SKILL, ADAPTIVE_SKILL, ADAPTIVE_FULL_OPTIMIZED, README):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("정본", content)
                self.assertIn("--markdown-output", content)
        self.assertIn("두 파일을 독립적으로 수정하지 않는다", self.skill)

    def test_render_reuse_preserves_fresh_qa_and_exposes_cache_failures(self):
        verification = ADAPTIVE_VERIFICATION.read_text(encoding="utf-8")
        self.assertIn("과거 PASS를 현재 판단으로 재사용하지 않는다", verification)
        self.assertIn("renderCacheSha256", verification)
        schema = json.loads(ADAPTIVE_VISUAL_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["properties"]["renderCacheSha256"]["pattern"], "^[0-9a-f]{64}$",
        )
        self.assertNotIn("renderCacheSha256", schema["required"])
        self.assertIn("해시 불일치는", verification)
        self.assertIn("옵션 없는 기존 CLI는 항상 새로 렌더한다", verification)
        for path in (ADAPTIVE_SKILL, ADAPTIVE_PRODUCTION, ADAPTIVE_FULL_OPTIMIZED, README):
            with self.subTest(path=path.name):
                self.assertIn("--reuse-render", path.read_text(encoding="utf-8"))

    def test_source_dates_remain_in_evidence_not_default_footers(self):
        for path in (
            ADAPTIVE_SKILL, ADAPTIVE_PRODUCTION, ADAPTIVE_DECK_SPEC,
            ADAPTIVE_REFINEMENT, CUSTOMER_EVIDENCE,
        ):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("원본 확인 날짜", content)
                self.assertIn("발행 연도", content)
                self.assertNotIn("(accessed YYYY-MM-DD)", content)
                self.assertNotIn("(YYYY-MM-DD 확인)", content)
        self.assertIn("`accessed`", ADAPTIVE_PRODUCTION.read_text(encoding="utf-8"))

    def test_parallel_decks_have_requested_exclusive_ownership(self):
        content = " ".join(
            ADAPTIVE_FULL_OPTIMIZED.read_text(encoding="utf-8").split()
        )
        for term in (
            "사용자가 파일별 subagent를 요청한 경우에만",
            "공통 근거와 helper는 읽기 전용으로 공유",
            "담당자는 자기 덱의 계획·spec·생성 스크립트·QA만 수정",
            "최종 출력 폴더 복사와 전체 완료 선언은 메인 에이전트만",
            "한 파일의 PASS를 다른 파일에 재사용하지 않는다",
            "담당자의 계획을 덮어쓰지 않는다",
        ):
            with self.subTest(term=term):
                self.assertIn(term, content)

    def test_refinement_and_customer_guides_are_reachable(self):
        for path in (
            SKILL, ADAPTIVE_SKILL, ADAPTIVE_REFINEMENT, CUSTOMER_EVIDENCE,
            ADAPTIVE_PRODUCTION, ADAPTIVE_EDITORIAL, ADAPTIVE_BLUEPRINTS,
            ADAPTIVE_DECK_SPEC, ADAPTIVE_VERIFICATION, ADAPTIVE_FULL_OPTIMIZED, README,
        ):
            content = path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", content):
                if target.startswith(("https://", "http://")):
                    continue
                with self.subTest(path=path.name, target=target):
                    filename, _, fragment = target.partition("#")
                    destination = path.parent / filename if filename else path
                    self.assertTrue(destination.is_file())
                    if fragment and destination.suffix == ".md":
                        text = destination.read_text(encoding="utf-8")
                        anchors = set(re.findall(r'<a id="([^"]+)">', text))
                        for heading in re.findall(r"^#{1,6} (.+)$", text, re.MULTILINE):
                            slug = re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")
                            anchors.add(slug)
                        self.assertIn(fragment, anchors)
        self.assertIn("reference/customer-evidence.md", self.skill)

    def test_readme_matches_current_search_and_research_contracts(self):
        content = README.read_text(encoding="utf-8")
        self.assertIn("원문 검증은 `web-search` 계약을 따릅니다", content)
        self.assertIn("사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱", content)
        self.assertIn("--deck-spec", content)
        self.assertNotIn("research agent·`/fleet`에 위임하지 않습니다", content)
        self.assertNotIn("매번 실시간 공식 자료 조사", content)

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
