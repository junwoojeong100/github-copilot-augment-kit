from __future__ import annotations

import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


class WebSearchSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_web_search_is_primary_provider(self):
        web_search = self.skill.index("전용 general web search tool(예: `web_search`)")
        research_agent = self.skill.index("web source를 지원하는 client의 Research agent")
        domain_search = self.skill.index("도메인 전용 검색")

        self.assertLess(web_search, research_agent)
        self.assertLess(research_agent, domain_search)

    def test_public_serp_scraping_is_forbidden(self):
        self.assertIn("공개 검색 결과 페이지(SERP)", self.skill)
        self.assertIn("직접 조회하지 않는다", self.skill)
        self.assertNotIn("https://www.google.com/search", self.skill)
        self.assertNotIn("https://html.duckduckgo.com", self.skill)
        self.assertNotIn("DuckDuckGo HTML로 전환", self.skill)

    def test_search_results_require_canonical_source_verification(self):
        self.assertIn("검색 provider의 답변만으로 검증 완료 처리하지 않고", self.skill)
        self.assertIn("canonical 원문을 직접 확인한다", self.skill)


if __name__ == "__main__":
    unittest.main()
