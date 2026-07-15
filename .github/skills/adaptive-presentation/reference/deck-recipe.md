# Adaptive Deck Recipe

`DeckRecipe`는 조사와 디자인 사이의 **semantic assembly layer**다. 슬라이드별 결론, 정보 관계,
source reference, component 이름, blueprint intent를 구조화하지만 색상·폰트·좌표는 저장하지 않는다.

## 1. 전체 계약

```text
실시간 공식 조사
  → Fact Ledger
  → Deck Spec
  → Deck Recipe                    # 의미와 정보 관계

매 요청의 Design DNA              # 색·타입·형태·밀도·은유
  + Deck Recipe
  → Adaptive Layout Selector
  → Certified Components / Custom Builders
  → Slide Compiler
  → verify_deck.py
```

실시간 조사는 최적화 대상에서 제외한다.

- 외부 사실·기능 상태·가격·규제·고객 성과는 매 요청마다 현재 공식 출처로 다시 확인한다.
- 이전 Fact Ledger는 검색 후보와 안정적 용어를 제공할 뿐 최신 사실의 근거로 단독 사용하지 않는다.
- 시간 단축은 조사 이후의 구조화·조립·preflight·QA orchestration에서만 수행한다.

## 2. Recipe가 저장하는 것과 금지하는 것

저장:

- conclusion title, section, subtitle
- semantic type와 component
- source key 최대 2개
- content item, matrix row, code line
- 강조 의도(`standard`, `inverse`, `hero`)
- 필요 시 family/variant override
- custom builder key

금지:

- HEX/RGB와 palette
- font, font size
- x/y/w/h와 고정 좌표
- corner radius, shadow, line color
- 고정 커버·브랜드·카드 스타일

금지 키는 Recipe 생성 시 `LayoutError`로 차단한다. 핵심 슬라이드는 `custom_builder`로 별도 구성하지만,
그 builder도 현재 덱의 `DesignDNA` role과 Compiler primitive를 사용한다.

## 3. 기본 사용법

```python
from pptx_compiler import (
    DeckRecipe,
    RecipeAssembler,
    SlideRecipe,
)

recipe = DeckRecipe(
    title="Developer Platform",
    expected_slides=3,
    slides=(
        SlideRecipe(
            id="cover",
            title="",
            semantic_type="cover",
            emphasis="hero",
            content={
                "kicker": "DEVELOPER EDITION",
                "headline": "Build to operate",
                "subtitle": "One governed lifecycle",
                "visual_text": "BUILD → RUN → IMPROVE",
            },
        ),
        SlideRecipe(
            id="comparison",
            title="두 선택지는 제어 수준에서 갈립니다",
            semantic_type="comparison",
            content={
                "left_title": "FAST",
                "left_items": ["managed", "configuration-first"],
                "right_title": "CONTROL",
                "right_items": ["custom code", "runtime ownership"],
            },
        ),
        SlideRecipe(
            id="quality",
            title="평가는 배포 승인을 위한 Gate입니다",
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

assembler = RecipeAssembler(design, sources=source_registry)
assembler.compile_to(recipe, OUT, report_path=WORK / "compiler-report.json")
```

`design`은 매 요청에서 새로 만든 `DesignDNA`다. Recipe만으로는 PPTX를 생성할 수 없다.

## 4. Adaptive Layout Selector

family/variant를 생략하면 semantic type, item count, density, emphasis, 앞선 슬라이드의 사용 기록으로
후보를 점수화한다.

- 같은 family의 직전 사용에 penalty
- 같은 family 3회 연속에 매우 큰 penalty
- hero intent에는 split/centered/hub 선호
- 고밀도 콘텐츠에는 table/rail/stack 선호
- slot 수를 지원하지 않는 process/layered/roadmap 후보 제거

선택 결과는 deterministic하지만 고정 템플릿은 아니다. Design DNA, 콘텐츠, 이전 layout rhythm이
달라지면 geometry·variant·타이포·색이 달라진다. 중요한 슬라이드는 `family`와 `variant`를 명시한다.

## 5. Certified Components

`ComponentRegistry`는 정보 관계를 재사용한다.

| Component | 관계 | 권장 family |
|---|---|---|
| `cover` | thesis + visual field | cover |
| `statement` | hero + support + evidence | statement |
| `comparison` | common-axis comparison | comparison |
| `process` | ordered steps | process |
| `layers` | hierarchy / stack | layered |
| `matrix`, `status_ledger` | exact comparison / status | matrix |
| `architecture` | input-core-output | architecture |
| `code` | code + explanation | code |
| `roadmap`, `quality_loop` | gates / feedback stages | roadmap |
| `resource_hierarchy` | resource-project-connected boundaries | architecture/hub |
| `agent_anatomy` | core + surrounding capabilities | architecture/hub |
| `security_layers` | identity-network-data-runtime-controls | layered |

Component는 semantic color role만 받는다. 현재 Design DNA에서 role 대비가 부족하면 Compiler가
읽기 가능한 ink role을 선택하고 의미 색은 border·badge로 유지한다.

## 6. Custom slide 비율

권장:

- 70~80%: Recipe + Certified Component
- 20~30%: custom builder

직접 구성할 대상:

- cover와 section opener
- 핵심 thesis
- 복잡한 시스템 아키텍처
- 최신 업데이트 overview
- close / decision slide

```python
def build_custom_architecture(canvas, payload):
    core = canvas.region("hub")
    canvas.box(core, fill="surface", line="primary")
    # Design DNA role과 Compiler primitive만 사용

assembler = RecipeAssembler(
    design,
    custom_builders={"critical-architecture": build_custom_architecture},
)
```

## 7. 실제 Font Metrics

`FontMetrics`는 다음 순서로 폰트를 찾는다.

1. 명시된 font file
2. Pillow가 직접 로드할 수 있는 font
3. `fc-match`
4. macOS/Linux font directory
5. 찾지 못하면 기존 보수적 heuristic

실제 `ImageFont.getlength()` 값을 point로 환산해 no-wrap code와 긴 제목의 수평 overflow를 생성 전에
차단한다. 폰트 탐색 결과와 측정 객체는 같은 Compiler 실행에서 캐시한다.

## 8. 통합 QA Runner

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx \
  --out <work-dir> \
  --expected-slides 30 \
  --strict
```

`--strict`는 장수·경계·ZIP뿐 아니라 작은 본문 후보와 title risk도 실패 처리한다. audit 오탐을 사람이
확인해 의도적인 보조 텍스트임이 분명할 때만 `--allow-small-text`를 추가한다.

한 명령에서 다음을 수행한다.

1. 구조 audit와 전체 render를 병렬 실행
2. 중간 PDF 유지
3. 텍스트 밀도·작은 글자·title risk·group·bounds로 위험 슬라이드 자동 선정
4. 같은 PDF를 재사용해 위험 슬라이드 원본 크기 JPEG 생성
5. PPTX ZIP integrity 검사
6. `verification-report.json` 생성

전체 contact sheet와 위험 슬라이드는 사람이 확인한다. Runner는 시각 QA를 생략하는 도구가 아니라
반복 명령과 수동 risk selection을 줄이는 orchestration 도구다.

## 9. 실행 예제

```bash
python3 -B .github/skills/adaptive-presentation/examples/recipe_quickstart.py \
  --style technical --out /tmp/recipe-technical.pptx

python3 -B .github/skills/adaptive-presentation/examples/recipe_quickstart.py \
  --style editorial --out /tmp/recipe-editorial.pptx
```

두 결과는 같은 Recipe를 사용하지만 Design DNA에 따라 palette, typography, spacing, corner, background
rhythm이 달라진다.
