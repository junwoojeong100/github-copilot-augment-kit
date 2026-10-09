from __future__ import annotations

import json
import re
import shlex
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCE = SKILL_ROOT / "reference"
SKILL = SKILL_ROOT / "SKILL.md"
README = SKILL_ROOT.parents[2] / "README.md"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import verify_deck  # noqa: E402
import visual_review  # noqa: E402


def python_commands(content: str):
    for block in re.findall(r"```bash\n(.*?)\n```", content, re.DOTALL):
        for line in block.replace("\\\n", " ").splitlines():
            tokens = shlex.split(line, comments=True)
            for index, token in enumerate(tokens):
                if Path(token).name in {"verify_deck.py", "visual_review.py"}:
                    yield Path(token).name, tokens[index + 1:]
                    break


def local_links(path: Path):
    content = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", content):
        if target.startswith(("https://", "http://")):
            continue
        filename, _, fragment = target.partition("#")
        destination = (path.parent / filename if filename else path).resolve()
        yield destination, fragment


class PresentationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.verification = (REFERENCE / "verification.md").read_text(encoding="utf-8")
        cls.production = (REFERENCE / "pptx-production.md").read_text(encoding="utf-8")
        cls.coordination = (REFERENCE / "full-optimized.md").read_text(encoding="utf-8")

    def test_entrypoint_is_bounded_and_preflight_precedes_building(self):
        self.assertLessEqual(len(self.skill.splitlines()), 120)
        self.assertIn("NOT WHEN:", self.skill.split("---", 2)[1])
        self.assertEqual(
            len(re.findall(r"^## .*워크플로.*$", self.skill, re.MULTILINE)), 1
        )
        preflight = self.skill.index("scripts/toolcheck.py --strict")
        spec = self.skill.index("scripts/deck_spec.py")
        production = self.skill.index("reference/pptx-production.md")
        self.assertLess(preflight, spec)
        self.assertLess(spec, production)
        for guard in (
            "--require-korean-font", "scripts/inspect_template.py",
            "누락이 확인된 의존성만", "초안과 미검증 범위", "완료로 처리하지 않는다",
            "client가 제공한 artifact 디렉터리",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, self.skill[:production])
        self.assertIn("내부 Fact ID는 노출하지 않는다", self.skill)

    def test_documented_qa_commands_bind_distinct_revision_evidence(self):
        commands = list(python_commands(self.verification))
        creates = [
            visual_review.build_parser().parse_args(arguments)
            for script, arguments in commands
            if script == "visual_review.py"
        ]
        self.assertGreaterEqual(len(creates), 2)
        self.assertTrue(all(command.action == "create" for command in creates))
        by_path = {command.out: command for command in creates}
        self.assertEqual(len(by_path), len(creates))
        approvals = []
        for script, arguments in commands:
            if script != "verify_deck.py":
                continue
            command = verify_deck.build_parser().parse_args(arguments)
            if command.visual_review is None:
                continue
            with self.subTest(evidence=command.visual_review):
                self.assertIn(command.visual_review, by_path)
                review = by_path[command.visual_review]
                self.assertEqual(review.deck, command.deck)
                self.assertEqual(review.out.parent, command.out)
                self.assertEqual(
                    review.render_cache, command.out / "qa" / "render-cache.json"
                )
                self.assertTrue(command.reuse_render)
                self.assertTrue(review.reviewer.strip())
                self.assertGreaterEqual(len(review.notes.strip()), 12)
                approvals.append(command.visual_review)
        self.assertCountEqual(approvals, list(by_path))

    def test_auxiliary_guides_link_to_canonical_qa_and_tool_preparation(self):
        verification = (REFERENCE / "verification.md").resolve()
        for path in (
            SKILL, REFERENCE / "deck-spec.md",
            REFERENCE / "pptx-production.md", REFERENCE / "full-optimized.md",
        ):
            with self.subTest(path=path.name):
                self.assertIn(verification, {target for target, _ in local_links(path)})
        tooling = self.production.split("## 2.", 1)[0]
        self.assertIn("scripts/toolcheck.py", tooling)
        self.assertNotIn("full-optimized.md", tooling)
        self.assertIn(
            ((REFERENCE / "pptx-production.md").resolve(), "tool-cache"),
            set(local_links(REFERENCE / "full-optimized.md")),
        )

    def test_partial_and_automated_checks_do_not_replace_editorial_review(self):
        verification = " ".join(self.verification.split())
        for guard in (
            "부분 렌더는 최종 전체 QA나 시각 검토 증거를 대체하지 않는다",
            "최종 revision의 전체 contact sheet",
            "canonical runner의 자동 검사 범위가 아니다",
            "키워드 일치만으로 의미 보존을 판정하지 않음",
            "실제 발표 시간 보장 아님",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, verification)
        self.assertNotIn("전체 contact sheet는 다시 만들지 않는다", verification)

    def test_existing_deck_refinement_preserves_meaning_and_originals(self):
        content = (REFERENCE / "refinement.md").read_text(encoding="utf-8")
        self.assertIn("reference/refinement.md", self.skill)
        for guard in (
            "내용 원본", "디자인 참고", "source-inventory.json", "content-coverage.json",
            "원본 항목", "의미 단위의 보존", "기존 파일을 덮어쓰지 않고", "SHA-256",
            "발표 시간", "명시적 덮어쓰기 대상 외",
            "모든 덱의 완료 상태를 구분한다", "작업 소유 임시 PDF·QA 이미지 경로만 정리한다",
            "미측정 조합",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, content)

    def test_editorial_details_have_one_owner(self):
        production = (REFERENCE / "pptx-production.md").resolve()
        for path in (
            SKILL, REFERENCE / "refinement.md", REFERENCE / "editorial-business-style.md",
            REFERENCE / "slide-blueprints.md", REFERENCE / "deck-spec.md",
            REFERENCE / "verification.md", README,
        ):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn((production, "typography"), set(local_links(path)))
                for duplicated_detail in ("18~23pt", "4.5:1", "120~600자"):
                    self.assertNotIn(duplicated_detail, content)

    def test_requested_coordination_retains_ownership_and_optional_metrics(self):
        content = " ".join(self.coordination.split())
        for guard in (
            "사용자가 파일별 subagent를 요청한 경우에만",
            "공통 근거와 helper는 읽기 전용으로 공유",
            "담당자는 자기 덱의 계획·spec·생성 스크립트·QA만 수정",
            "최종 출력 폴더 복사와 전체 완료 선언은 메인 에이전트만",
            "한 파일의 PASS를 다른 파일에 재사용하지 않는다",
            "담당자의 계획을 덮어쓰지 않는다",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, content)
        self.assertIn("metrics.json", content)
        self.assertIn("일반 덱 생성의 완료 조건은 아니다", content)
        self.assertIn("측정하지 않은 개선", content)

    def test_source_dates_stay_in_evidence_and_necessary_context_stays_visible(self):
        for path in (
            SKILL, REFERENCE / "pptx-production.md",
            REFERENCE / "deck-spec.md", REFERENCE / "refinement.md",
        ):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("원본 확인 날짜", content)
                self.assertIn("발행 연도", content)
                self.assertNotIn("(accessed YYYY-MM-DD)", content)
                self.assertNotIn("(YYYY-MM-DD 확인)", content)
        self.assertIn("`accessed`", self.production)

    def test_reference_links_and_fragments_resolve(self):
        for path in (SKILL, README, *REFERENCE.glob("*.md")):
            for destination, fragment in local_links(path):
                with self.subTest(path=path.name, destination=destination, fragment=fragment):
                    self.assertTrue(destination.is_file())
                    if not fragment or destination.suffix != ".md":
                        continue
                    text = destination.read_text(encoding="utf-8")
                    anchors = set(re.findall(r'<a id="([^"]+)">', text))
                    for heading in re.findall(r"^#{1,6} (.+)$", text, re.MULTILINE):
                        anchors.add(
                            re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")
                        )
                    self.assertIn(fragment, anchors)


if __name__ == "__main__":
    unittest.main()
