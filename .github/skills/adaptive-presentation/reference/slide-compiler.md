# Reusable Slide Compiler

`pptx_compiler`는 고정 템플릿이 아니라 **PowerPoint 생성 메커니즘을 재사용하는 렌더링 엔진**이다.
매 덱의 서사와 시각 언어는 계속 새로 설계하며, 반복 구현하던 좌표·텍스트·도형·검증 코드만 가져다 쓴다.

표준 슬라이드 조립은 `reference/deck-recipe.md`의 Recipe layer가 담당한다. Recipe 역시 디자인을
보유하지 않으며 Compiler를 호출하기 전에 현재 요청의 Design DNA가 반드시 필요하다.

## 1. 책임 경계

```text
Fact Ledger + Deck Spec  -> 무엇을 말할지
Design DNA               -> 어떻게 보일지
Semantic Blueprint       -> 정보 관계를 어떻게 배치할지
Slide Compiler           -> 안전하게 PPTX 객체로 생성하는 방법
```

Compiler가 재사용하는 것:

- PowerPoint 문서와 화면비 생성
- 텍스트 크기 추정과 최소 크기 보호
- 실제 설치 font를 찾을 수 있을 때 Pillow 기반 glyph width 측정
- 도형·선·화살표·배지·상태 칩
- `cover`/`contain` 이미지 배치와 crop
- 출처와 페이지 헤더 처리
- 안전 영역과 경계 검사
- 레이아웃 다양성·연속 반복·카드 비율 검사
- semantic blueprint의 named region 계산

Compiler가 소유하면 안 되는 것:

- 기본 브랜드 색 또는 고정 팔레트
- 모든 덱에 반복되는 커버 구도
- 고정된 카드 반경·그림자·섹션 표지
- 주제와 무관한 3열 카드 기본값
- 덱의 결론형 제목과 실제 콘텐츠

## 2. 위치와 import

```text
.github/skills/adaptive-presentation/
  pptx_compiler/
    models.py
    layouts.py
    compiler.py
```

세션 작업 폴더의 `build_<deck>.py`에서 스킬 디렉터리를 import path에 추가한다.

```python
import sys
from pathlib import Path

SKILL_DIR = Path("/absolute/path/to/.github/skills/adaptive-presentation")
sys.path.insert(0, str(SKILL_DIR))

from pptx_compiler import (
    ContentItem,
    DesignDNA,
    Palette,
    ShapeLanguage,
    SlideCompiler,
    SlideFrame,
    Typography,
)
```

## 3. Design DNA는 필수 입력

Compiler에는 기본 팔레트가 없다. `DesignDNA`를 명시적으로 만들지 않으면 덱을 생성할 수 없다.

```python
design = DesignDNA(
    name="Precision + Editorial",
    concept_words=("precise", "calm", "forward"),
    visual_metaphor="signal network",
    palette=Palette(
        canvas="F4F1EA",
        canvas_alt="0B1017",
        surface="FFFFFF",
        surface_alt="141D28",
        ink="111820",
        ink_inverse="F7FAFC",
        muted_ink="5D6B78",
        muted_inverse="AAB6C2",
        primary="E65F2B",
        secondary="1677C8",
        accent="7856D8",
        border="D6D9DC",
        border_inverse="2A3948",
        success="238A57",
        warning="C48316",
        danger="C43D55",
        preview="8A4EC7",
    ),
    typography=Typography(
        body_font="Apple SD Gothic Neo",
        display_font="Apple SD Gothic Neo",
        mono_font="Menlo",
    ),
    shapes=ShapeLanguage(
        corner_style="subtle",
        spacing="balanced",
        depth="flat",
    ),
)
```

위 HEX는 API 설명용 예시일 뿐이다. 사용자 덱에서 복사하지 않고 `design-dna.md`에서 새로 도출한다.

## 4. Semantic blueprint

Blueprint는 완성된 슬라이드 디자인이 아니라 named region을 반환한다.

| Family | Variants | Named regions |
|---|---|---|
| `cover` | `split`, `centered` | kicker, headline, subtitle, visual, meta |
| `statement` | `hero-left`, `centered` | hero, support, evidence |
| `comparison` | `balanced`, `axis` | left, axis, right |
| `process` | `rail`, `stair` | rail, step_1... |
| `layered` | `stack`, `pyramid` | layer_1... |
| `matrix` | `table`, `quadrants` | table 또는 q1...q4 |
| `architecture` | `pipeline`, `hub` | input/core/output/operations 또는 hub/left/right/bottom |
| `code` | `split`, `full` | code, explain |
| `roadmap` | `rail`, `gates` | rail, stage_1... |
| `custom` | 자유 문자열 | content |

`begin_slide`이 layout plan을 만들고 `SlideCanvas`를 반환한다.

```python
compiler = SlideCompiler(design, title="Deck title")

canvas = compiler.begin_slide(
    SlideFrame(
        title="평가는 배포 승인을 위한 Gate입니다",
        section="OPERATE",
        number=12,
        accent_role="primary",
    ),
    family="process",
    variant="rail",
    slots=4,
)

canvas.process([
    ContentItem("DATA", "Task-specific dataset", "secondary"),
    ContentItem("RUN", "Model or agent execution", "accent"),
    ContentItem("SCORE", "Quality and safety", "primary"),
    ContentItem("PROMOTE", "Threshold-based release", "success"),
])
```

Compiler의 convenience component가 내용에 맞지 않으면 named region과 primitive를 직접 사용한다.

```python
hero = canvas.region("step_1", inset=0.1)
canvas.box(hero, fill="surface", line="secondary")
canvas.text(hero.inset(0.2), "Custom composition", role="body")
```

## 5. 고정 디자인 방지 규칙

1. 매 덱마다 새 `DesignDNA`를 생성한다.
2. sample 또는 이전 덱의 팔레트를 기본값처럼 복사하지 않는다.
3. 20장 이상은 8개 이상의 layout family를 사용한다.
4. 같은 family 3회 연속은 `allow_repeat=True`로 의도를 명시하지 않으면 실패한다.
5. `matrix/quadrants` 같은 카드 구조가 전체의 35%를 넘으면 실패한다.
6. `ShapeLanguage.spacing`과 layout variant를 바꿔 정보 밀도와 geometry도 매 덱에서 조정한다.
7. 커버·섹션 표지·핵심 아키텍처는 visual metaphor에 맞춰 primitive로 추가 구성한다.
8. Compiler validation은 외부 `audit_pptx.py`와 렌더 QA를 대체하지 않는다.

## 6. 저장과 preflight

```python
report = compiler.save(
    OUT,
    expected_slides=30,
    min_layout_families=8,
    max_card_grid_ratio=0.35,
    report_path=WORK / "compiler-report.json",
)
```

저장 전에 다음 오류를 차단한다.

- 예상 장수 불일치
- slide/region 경계 초과
- 최소 크기 아래로 내려가야만 들어가는 본문
- no-wrap 텍스트의 수평 overflow와 code region 초과
- layout family 부족
- 같은 family 3회 연속
- 카드 그리드 비율 초과
- 텍스트 대비가 일반 4.5:1, large/bold 3:1 기준 미달
- 한 슬라이드에 3개 이상의 source를 넣어 footer에서 누락될 위험

역상 배경의 source footer는 LibreOffice의 hyperlink theme 색상 덮어쓰기를 피하기 위해 plain text로
생성한다. 밝은 source footer의 단일 출처는 hyperlink를 유지한다.

## 7. 실행 예제와 테스트

동일한 semantic deck을 서로 다른 두 Design DNA로 생성한다.

```bash
python3 -B .github/skills/adaptive-presentation/examples/compiler_quickstart.py \
  --style technical --out /tmp/compiler-technical.pptx

python3 -B .github/skills/adaptive-presentation/examples/compiler_quickstart.py \
  --style editorial --out /tmp/compiler-editorial.pptx
```

테스트:

```bash
python3 -B -m unittest discover \
  -s .github/skills/adaptive-presentation/pptx_compiler/tests -v
```

## 8. 생성 스크립트에서 남아야 하는 것

Compiler 도입 후에도 `build_<deck>.py`에는 다음이 남는다.

- 이번 덱의 Design DNA 객체
- 슬라이드별 결론과 콘텐츠
- blueprint family와 variant 선택
- 주제에 맞는 custom visual composition
- 실제 근거와 source 연결

즉 생성 스크립트는 짧아지지만, 덱의 디자인과 서사는 자동으로 고정되지 않는다.
