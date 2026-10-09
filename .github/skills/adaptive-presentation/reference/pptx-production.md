# PPTX Production

슬라이드는 고정 생성 엔진이나 컴포넌트 라이브러리 없이 **`python-pptx`로 직접** 만든다. 매 덱마다
주제에 맞는 시각 형태를 자유롭게 구성하되, 결론이 가장 짧은 경로로 읽히는 Straightforward 구조와
아래 품질·위생 기준을 지킨다.

글꼴·타이포그래피·대비·발표 노트의 **상세 편집 기준의 정본**은 이 문서다. 다른 가이드는 아래 절을
참조하며 수치를 따로 유지하지 않는다. machine contract의 필드·정규화·검사는 기존 schema와 validator를
따른다. 명시적인 브랜드·템플릿 override도 deck spec에 기록하고 같은 검사를 적용한다.

## 1. 도구

1. Python 환경에서 `python-pptx`를 기본으로 사용한다.
2. 대량 데이터 처리·차트 계산에는 pandas/matplotlib를 쓸 수 있으나, 발표에 들어가는 핵심 도표는
   가능하면 PowerPoint 도형/네이티브 차트로 만들어 편집 가능하게 한다.
3. 외부 이미지가 필요하면 사용권과 원본 URL을 기록한다.
4. 도구 탐색·의존성 준비는 `scripts/toolcheck.py`와 아래 사전 준비 규칙을 따른다.
5. [글꼴](#fonts)과 [타이포그래피](#typography)를 먼저 확정하고 deck spec의 `fontPolicy`와 일치시킨다.

<a id="tool-cache"></a>

### 도구 캐시와 사전 준비

strict 사전 점검은 Python·`soffice`·PyMuPDF·Pillow·python-pptx·폰트를 탐지한다.
캐시는 `${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/`의 `toolchain.json`·
`fonts.txt`에 저장하며, hit에서도 interpreter·PATH·필수 import·실행 파일을 재확인한다.
비용이 큰 폰트 목록 탐색만 재사용한다. 검증된 `.venv/`는 필요한 경우에만 준비한다.

설치는 import 실패나 도구 부재가 확인된 의존성만 대상으로 한다. 도구 준비는 콘텐츠를 만들지 않으므로
조사와 병렬 실행할 수 있다. 고객 자료·시크릿·생성 산출물은 공용 캐시에 넣지 않는다.

## 2. 파일 구조

```text
<output>/<deck>.pptx                 # 사용자에게 보이는 기본 산출물

<session>/<deck>-work/               # SKILL.md의 portable 세션 artifact 디렉터리 아래
  fact-ledger.json                    # 검증된 근거 정본
  fact-ledger.md                      # web-search 검증기로 생성하는 읽기용 뷰
  deck-spec.json
  storyline.md
  template-profile.json                  # 템플릿이 있을 때만
  build_<deck>.py                    # python-pptx 직접 생성 스크립트
  qa/
    contact-01-30.jpg
    slide-08.jpg                     # 선택 검수 시에만
```

생성 스크립트·QA 산출물을 저장소 루트나 최종 출력 폴더에 두지 않는다. 사용자가 요청한 경우에만 세션
작업 폴더에서 최종 출력 위치로 복사한다. 중간 PDF는 QA가 끝날 때까지만 두고 정리한다. Python은
`python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 저장소에 `__pycache__`·`.pyc`가 생기지 않게 한다.

## 3. 생성 스크립트 골격

`python-pptx`를 직접 사용하는 최소 골격이다. 슬라이드마다 필요한 도형·텍스트·차트를 자유롭게 배치한다.

```python
import os
from pathlib import Path

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN

OUT = Path(os.environ["PPTX_OUT"])
TEMPLATE = os.environ.get("PPTX_TEMPLATE")

import sys
sys.path.insert(0, os.environ["ADAPTIVE_PRESENTATION_DIR"])
import pptx_helpers as H

# 주제·브랜드에 맞게 자유롭게 정하는 값 (고정 팔레트 아님)
INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x0F, 0x62, 0xFE)
CANVAS = RGBColor(0xFF, 0xFF, 0xFF)
BODY_FONT = "Apple SD Gothic Neo"
LEADING_MESSAGE_SIZE = 27

def textbox(slide, text, x, y, w, h, size, *, color=INK, bold=False,
            align=PP_ALIGN.LEFT, font=BODY_FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    H.set_run_font(run, font)
    run.font.color.rgb = color
    return box

def build():
    prs, blank = H.init_deck(
        TEMPLATE,
        clear_existing_slides=bool(TEMPLATE),
        width_in=13.333,
        height_in=7.5,
    )

    # 슬라이드마다 정보 관계에 맞는 형태를 직접 구성한다.
    slide = prs.slides.add_slide(blank)
    textbox(
        slide,
        "결론형 제목",
        0.72,
        0.5,
        11.9,
        1.0,
        LEADING_MESSAGE_SIZE,
        bold=True,
    )
    # ... 도형·차트·출처 footer 등 자유 배치 ...

    prs.save(OUT)

if __name__ == "__main__":
    build()
```

거대한 JSON 하나로 모든 장을 같은 레이아웃으로 렌더하지 않는다. 슬라이드마다 함수/구성을 나눠
정보 유형에 맞는 형태를 만든다.

### 선택: 디자인 중립 헬퍼로 보일러플레이트 줄이기

`pptx_helpers`는 색·좌표를 **인자로 받는** 기계적 프리미티브(box·text·bullets·chip·chevron·grid_table·
soft_shadow)만 제공한다. 팔레트·테마·슬라이드 유형이 없으므로 "정해진 틀 없이 자유 구성" 원칙을 그대로
지키면서 반복 코드를 줄인다. 템플릿이 있으면 template-aware initializer로 master·layout·theme·canvas를
보존하고 예시 슬라이드만 제거한다.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("<absolute-skill-dir>")))
import pptx_helpers as H

prs, blank = H.new_deck()                              # 16:9 치수(디자인 아님)
INK, ACCENT = H.hexc("14203A"), H.hexc("1F63D8")       # 색은 매 덱 자유
s = H.add_slide(prs, blank, bg=H.hexc("FFFFFF"))
H.text(
    s,
    "결론형 제목",
    0.72,
    0.6,
    11.9,
    1.0,
    27,
    INK,
    bold=True,
    font="Apple SD Gothic Neo",
)
H.bullets(s, ["근거 1", "근거 2"], 0.72, 1.9, 6.0, 2.0, 17, INK, marker_color=ACCENT)
prs.save(OUT)
```

### 편집형 비즈니스 덱 기본값

`Claude Cowork처럼`, `컨설팅 덱처럼`, `임원용으로 더 전문적으로`라는 요청은
[`editorial-business-style.md`](./editorial-business-style.md)를 따른다.

- 샘플 deck/template이 있으면 자체 팔레트보다 그 master·grid·font·layout을 우선한다.
- 샘플이 없으면 강한 제목, 정밀한 column/grid, 넓은 여백, hairline rule, native chart/table/diagram을
  기본 시각 언어로 사용한다.
- 내용 전달이 목적인 본문 슬라이드에는 편집 가능한 visual structure가 하나 이상 있어야 한다.
  표지·section divider·단순 마무리 장은 예외다.
- 한 화면의 primary reading path는 좌→우 또는 상→하 하나로 고정하고, 결론과 무관한 장식·중첩
  container·중복 label은 제거한다.
- 한 가지 visual motif를 반복하되 같은 layout을 반복하지 않는다.
- 제목 밑 짧은 accent line, 과도한 rounded card·pill chip·soft shadow는 기본값으로 금지한다.

## 4. 화면과 안전 영역

- 기본: 13.333 × 7.5 inch
- 좌우 여백: 0.6~0.8 inch
- 제목 영역: 상단 0.4~1.45 inch
- 본문 영역: 약 1.6~6.75 inch
- 출처/페이지: 7.0 inch 부근
- 장식 도형은 의도적으로 bleed할 수 있지만 텍스트는 안전 영역 안에 둔다
- 사용자가 `완전 흰 배경`을 요청하면 모든 슬라이드의 `slide.background.fill`을 `#FFFFFF`로 직접
  지정한다. slide 전체를 덮는 배경 도형도 흰색이어야 하며, 섹션별 `#F7F7F7` canvas 교대는 사용하지
  않는다. 카드와 강조 영역의 light neutral surface는 별도 역할이므로 유지할 수 있다.
- 제목·본문·주석·출처의 전용 행을 먼저 예약하고, 한 영역의 도형이나 텍스트가 다른 영역을 침범하지 않게
  좌표를 잡는다.
- 포함 관계가 아닌 콘텐츠 도형끼리는 bounding box가 겹치지 않게 한다. 배지·라벨처럼 의도적으로 도형
  위에 놓는 텍스트도 컨테이너 안에 완전히 들어가야 한다.
- 연결선과 화살표는 텍스트 상자 아래를 통과시키지 않는다. 공간이 부족하면 선을 우회시키거나 내용을 줄인다.

<a id="typography"></a>

## 5. 텍스트

- `word_wrap=True`, `auto_size=NONE`
- 텍스트 프레임 margin을 명시
- 모든 run에 font name/size/color를 직접 적용
- 모든 visible run의 Latin·East Asian·complex-script typeface는 [글꼴 계약](#fonts)을 따른다.
- 한글과 영문 혼용 렌더를 실제 PDF에서 확인
- 줄 간격과 paragraph spacing을 명시
- 텍스트가 들어가는 도형은 PowerPoint/LibreOffice의 폰트 메트릭 차이를 고려해 가로·세로 8~12%의
  여유를 둔다. 한 환경에서 간신히 맞는 상태는 합격이 아니다.
- 제목은 제목 전용 행 안에서 끝나야 하며 구분선·섹션 chip을 침범하지 않아야 한다. 카드 문구는 카드
  border 안에 완전히 들어가야 한다.

크기:

- 표지·section divider 제목 30~42pt
- 한국어 본문 리딩 메시지 27pt Bold
- 주요 본문 18~23pt 권장, 조밀한 비교도 15pt 하한
- 보조 주석 13~15pt; 주요 조건을 주석으로 숨기지 않음
- 표·도식 내용 15~17pt, 짧은 보조 label만 11~13pt
- 출처 8~9.5pt

표지·section divider를 제외한 본문 슬라이드 title role은 `fontPolicy.leadingMessage`를 사용한다. 한국어
repository 기본은 `Apple SD Gothic Neo · 27pt · Bold`다. 같은 title
row가 슬라이드마다 31/32/34pt로 달라지면 위계가 흔들린다. 긴 제목은 문구 단축, title frame 폭·높이,
명시적 줄바꿈으로 해결하고 해당 슬라이드만 축소하지 않는다. 정말 다른 위계인 슬라이드만 예외로 기록한다.

긴 제목은 2줄 전용 높이를 확보하거나 문구를 줄인다. 리딩 메시지 계약 대상이 아닌 표지·구분 제목에
한해, 의미를 훼손하지 않고 줄일 수 없을 때 28~29pt를 허용한다. 컨테이너 오버플로는
문구 단축·도형 높이/폭·명시적 줄바꿈을 먼저 조정한다. 사용자가 글자 축소를 요청했거나 소폭 축소로
해결되는 경우에는 역할별 기준을 먼저 0.5~2pt 일관되게 낮춘다. 그래도 남는 문제 frame만 0.5pt 단위로
줄이되, 주요 본문 15pt·보조 13pt 아래로 내리지 않는다.

밀도: 일반 슬라이드는 주요 본문 40~65단어를 기본 범위로 삼고, 기술 슬라이드도 문장 수를 제한한다.
글자 축소로 생긴 여백에는 검증 근거, KPI, owner, 예외 조건처럼 발표자의 설명력을 높이는 정보만
1~2개 보강한다. 이미 밀도가 높은 슬라이드는 내용을 늘리지 않으며, 표/부록은 필요하면 명확히
Appendix로 구분한다.

<a id="language"></a>

### 한국어 덱의 영문 유지 기준

- 설명 문장·결론·KPI 해설·행동 문구는 한국어 우선이다.
- 제품·서비스·공식 기능·기술 계약 이름은 원문 영문을 유지한다. 예:
  `GitHub Copilot`, `Microsoft Foundry`, `Code Review`, `Browser Tools`, `Hosted Agents`,
  `Memory`, `Routines`, `Trace`, `Eval`, `Control Plane`, `AKS`, `ACA`, `MCP`.
- 공식 기능명을 한글로 바꾸지 않는다. `코드 검토`가 일반 행위라면 한글이지만 GitHub의 기능을
  지칭하면 `Code Review`로 쓴다.
- 권장 패턴은 `공식 영문명 + 한국어 역할 설명`이다.
  예: `Hosted Agents로 격리 실행환경을 제공합니다`.
- 전체 영문 문자 비율은 약 40%를 목표로 하되 비율을 맞추려고 불필요한 영어를 추가하지 않는다.

### 비기술 청중용 기술 설명

- 기술 깊이를 낮춘다는 것은 기술명을 삭제한다는 의미가 아니다. service·feature·component name은
  English로 유지하고, 바로 아래 또는 옆에 쉬운 한국어로 역할을 설명한다.
- 제목은 고객이 이해할 변화나 질문을 말한다. visual node·card heading에는 정확한 English term을 쓰고,
  body에는 “무엇을 하는가 / 왜 필요한가 / 어떤 결과가 생기는가”를 한국어로 적는다.
- 새 핵심 technical term은 한 장에 3~5개를 기본으로 하고 첫 등장에 한 줄 역할 설명을 붙인다.
- architecture 흐름은 `English component → 쉬운 역할 → business outcome`으로 읽히게 한다.
- capitalization을 공식 문서와 일치시킨다. 예: `Microsoft Foundry`, `Hosted Agents`,
  `Foundry IQ`, `Toolboxes`, `Code Review`, `Browser Tools`, `Control Plane`.
- `Policy + Evidence`, `Sandbox + Review`, `Settings + Streaming`처럼 공식 기능명을 축약한 임의 묶음은
  피하고 `Managed Settings + Session Streaming`, `Sandboxes + Code Review`처럼 실제 명칭을 쓴다.
- 설명은 “권한 있는 근거를 찾는다”, “실행 범위를 제한한다”, “상태·비용·위험을 한곳에서 관리한다”처럼
  비기술 청중도 행동과 결과를 이해할 수 있는 문장으로 작성한다.

### Speaker notes

모든 본문·표지·마무리 장에 notes를 작성한다.
기존 notes가 있으면 내용을 먼저 파악하고, 생성할 새 덱에서만 비운 뒤 현재 storyline·visual·근거로
다시 작성한다. 내용 원본을 덮어쓰거나 notes 문구를 그대로 이어 붙이지 않는다.

```text
핵심 메시지: 슬라이드의 결론을 한 문장으로 말합니다.
핵심 근거와 visual 요소의 관계를 설명합니다.
작동 방식이나 운영 조건을 설명합니다.
고객에게 중요한 영향과 판단 기준을 연결합니다.
실행하거나 기억할 내용을 한 문장으로 닫습니다.
```

간결한 발표 cue는 다음처럼 작성한다.

```text
핵심 메시지: Foundry IQ는 사용자 권한을 반영해 Agent가 판단할 근거를 제공합니다.
Toolboxes는 승인된 API와 자격 증명을 재사용 가능한 실행 경계로 관리합니다.
Knowledge와 action을 분리하면 근거의 정확성과 실행 통제를 각각 검증할 수 있습니다.
권한과 access 변경을 중앙에서 관리해야 운영 중에도 같은 기준을 유지할 수 있습니다.
이 구조는 Agent의 업무 가치를 높이면서 허용되지 않은 실행 위험을 줄입니다.
```

- notes는 슬라이드 본문을 낭독하거나 상세 reference를 반복하지 않는다.
- notes는 보고서 문체가 아니라 발표자가 그대로 읽어도 자연스러운 쉬운 구어체로 쓴다. 한 문장에는
  한 가지 생각만 담고, 긴 명사 나열은 짧은 동사형 문장으로 풀어 쓴다.
- 공식 제품명·기능명은 유지하되, 처음 나오는 technical term은 `trace, 즉 실행 기록`처럼 바로
  이해할 수 있는 쉬운 표현을 붙인다. `승격 여부를 결정합니다`보다 `다음 버전으로 올릴지 정합니다`처럼
  실제 발표에서 입에 붙는 표현을 우선한다.
- 소리 내어 읽었을 때 숨이 차거나 의미가 한 번에 잡히지 않는 문장은 둘로 나눈다. 불필요한
  `~할 수 있습니다`, `~에 해당합니다`, `~을 의미합니다` 반복은 제거한다.
- 기본 `core-only` notes는 `핵심 메시지:`로 시작하고 `질문:`과 `전환:` 섹션을 넣지 않는다.
- 핵심 메시지는 메타 표현 없이 발표자가 그대로 말할 수 있는 4~6문장으로 쓴다. 제목을 반복하지 말고
  visual의 핵심 요소 2~4개 사이의 관계, 작동 원리, 고객 의미와 판단 또는 행동을 포함한다.
- 사용자가 workshop 진행 질문과 장표 간 bridge를 명시적으로 요청한 경우에만 `guided-flow` 모드로
  `질문/핵심 메시지/전환` 3블록을 작성한다.
- 실제 예시·구성 요소·KPI·상태 조건은 slide visual과 footer에서 전달하고, 결론을 바꾸는 조건만
  `핵심 메시지`에 압축한다.
- notes에는 출처 블록, Fact ID, URL을 넣지 않는다. machine traceability는 Fact Ledger와
  deck spec의 `claimIds`로 유지한다.
- 화면 footer는 `출처: Publisher · Document title`과 원문 hyperlink로 표시한다.
  원본 확인 날짜는 Fact Ledger의 `accessed`에 남기고 화면에서는 기본 생략한다.
  `[F-001]` 같은 내부 Fact ID와 긴 URL은 넣지 않으며, 수치 기준일·발행 연도·버전은 필요한 곳에 유지한다.
- 한국어 기준 장당 약 60초, 전체 120~600자·4~6문장을 기본으로 한다.

<a id="fonts"></a>

## 6. 한글 폰트

한국어 기본 글꼴은 `Apple SD Gothic Neo`다. 표지·본문·표·도식·footer의 모든 visible run에 같은
Latin·East Asian·complex-script typeface를 명시하고 `fontPolicy.requireAllTextFont=true`로 기록한다.
본문 리딩 메시지는 [타이포그래피](#typography)의 family·size·weight를 `fontPolicy.leadingMessage`에
기록한다. 명시적 브랜드·템플릿 override는 같은 계약의 `selected`와 `leadingMessage`를 함께 바꾼다.
실행 환경에서 설치 여부를 확인하되 임의의 slide별 글꼴 변경은 허용하지 않는다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/toolcheck.py \
  --strict --require-korean-font

(fc-list 2>/dev/null || true) | grep -Ei 'Noto Sans|Apple SD Gothic|Malgun|Aptos|Segoe'
```

설치·렌더 환경별 확인 후보(전달 PPTX의 기본 글꼴을 임의로 바꾸는 허가가 아님):

- macOS: Apple SD Gothic Neo
- Windows: Malgun Gothic
- 공통 배포 환경: Noto Sans CJK KR 설치 여부 확인

탐지 결과를 `deck-spec.json`의 `fontPolicy.selected`에 기록하고 생성 스크립트의 모든 run에 사용한다.
폰트를 PPTX에 임베드할 수 있다고 가정하지 않으며 verifier에서 PDF 렌더 폰트와 다시 대조한다.
렌더 전용 fallback이 필요하면 격리된 렌더 profile에만 적용하고 사용한 글꼴을 기록한다.
전달 PPTX의 typeface나 사용자 전역 앱 설정을 바꾸는 방법으로 렌더 문제를 숨기지 않는다.

<a id="contrast"></a>

## 7. 색과 대비

- 색은 주제와 (있다면) 사용자 브랜드에서 자유롭게 정한다. 고정 팔레트를 강제하지 않되, 먼저
  `canvas / surface / ink / primary / optional secondary` 역할을 정하고 덱 전체에서 재사용한다.
- 브랜드·템플릿이 없는 CIO/임원 자료의 기본값은 Microsoft Fluent 계열의 white/light neutral canvas,
  dark neutral ink, Microsoft Blue primary, 선택적 blue-teal secondary다.
- 임원 자료는 neutral을 포함해 **3~4개 색상 계열**로 제한한다. 같은 hue의 tint/shade는 한 계열로 보며,
  채도가 높은 accent는 최대 2계열만 쓴다.
- dominant color 하나가 약 60~70%의 시각 무게를 담당하고 support 1~2개와 sharp accent 1개만 보조한다.
- 카드·단계·팀마다 서로 다른 accent를 배정하지 않는다. 구분은 우선 위치·여백·크기·선 굵기·타이포
  계층으로 만들고, 색은 선택·강조·흐름에만 사용한다.
- 같은 의미와 상태는 덱 전체에서 같은 색을 사용한다.
- 본문·도식·중요 조건의 전경/배경 대비는 7:1을 목표로 하고 4.5:1 미만은 수정한다.
  사용자 지정 임계치는 그대로 적용하며, 큰 글자라는 이유로 낮은 대비를 허용하지 않는다.
- 실제 전경·배경의 상대 휘도로 `(Lmax + 0.05) / (Lmin + 0.05)`를 계산하고 색 조합별 결과를
  세션 검토 기록에 남긴다. 투명도·이미지·gradient 배경은 별도로 확인하며 미측정 값을 PASS로 간주하지 않는다.
- 제목은 크더라도 낮은 대비 회색으로 두지 않는다
- 색만으로 상태를 전달하지 않고 GA/PREVIEW/위험 텍스트를 병기
- 상태색이 꼭 필요하면 해당 슬라이드의 국소 예외로 제한하고, 구조 색상 체계를 rainbow palette로
  확장하지 않는다.
- PDF 변환에서 색이 달라질 수 있으므로 렌더를 확인
- 흰 canvas 요청은 렌더뿐 아니라 PPTX 구조에서도 각 slide background가 `FFFFFF`인지 확인한다.

## 8. 도형과 연결선

- 도형은 정보 계층을 표현해야 한다
- 선은 시작과 끝의 의미가 명확해야 한다
- 교차선 최소화
- 화살표 방향은 발표 흐름과 일치
- 포함 관계와 연결 관계를 다른 스타일로 표현
- 의도하지 않은 도형 겹침은 금지한다. 그림자와 얇은 border 접촉은 허용하지만, 콘텐츠 면적이나 텍스트가
  다른 객체를 가리면 결함이다.
- chevron·arrow·connector는 인접 카드 사이의 명시적 gap 안에 들어가야 한다. connector 폭이 gap보다
  크거나 대상 카드 아래로 숨어 들어가면 폭·간격을 다시 잡는다.
- 단계 번호·짧은 라벨도 예상보다 자주 강제 줄바꿈된다. `01`·`02` 같은 두 자리 숫자는 실제 글꼴에서
  한 줄로 들어가는 폭과 높이를 확보하고, 다음 본문 행과 독립된 frame을 사용한다.
- 최종 좌표 검사는 text/text, shape/shape, text/container를 모두 포함한다. frame 좌표가 겹치지 않아도
  줄바꿈된 글리프가 frame 밖으로 렌더될 수 있으므로 PDF text-span 검사까지 통과해야 한다.
- 편집형 비즈니스 덱은 square surface와 hairline separator를 우선한다. rounded rectangle·pill·shadow는
  의미가 있을 때만 국소적으로 사용하고 반복 motif로 삼지 않는다.

## 9. 표

- 6행×5열을 기본 상한으로 권장
- 공통 비교 축을 왼쪽에 고정
- 숫자 정렬과 단위 통일
- 긴 문장을 셀에 넣지 않는다
- 행 높이는 실제 줄 수와 cell padding을 수용해야 한다. 두 줄이 간신히 맞는 표는 렌더에서 늘어날 수
  있으므로 높이·여백을 확보하고, 공식명은 명칭 경계에서 줄바꿈한다.
- 표가 핵심 메시지를 숨기면 비교 카드·dot plot·decision tree로 전환

## 10. 차트

- 실제 데이터와 기준일을 사용
- 차트 제목은 데이터 이름이 아니라 결론
- 단위, 축 범위, 표본/출처 표시
- 선택 계열 1개만 강한 색
- 단순 막대·선·dot plot을 우선
- 파이/도넛은 5개 이하의 구성비에서만
- 3D 차트 금지

편집 가능성이 중요하면 PowerPoint 기본 chart API 또는 도형 기반 차트를 사용한다.

## 11. 이미지

- 낮은 해상도 이미지를 늘리지 않는다
- 크롭 비율을 통일
- 텍스트 위에 복잡한 이미지를 직접 깔지 않는다
- 공식 제품 UI 스크린샷은 날짜와 버전을 확인
- 고객 로고는 공식 자산만 사용

## 12. 출처

주장 슬라이드의 footer에 직접 표시한다.

```text
Source: Organization · Document title
```

- 출처별 footer 항목에 Fact Ledger의 발행자·문서명을 표시하고, 문서명 또는 표시한 URL에 해당 원문의
  실제 PPTX hyperlink를 건다. 긴 URL은 표시만 줄이고 hyperlink 대상은 원문 URL을 유지한다.
- 원본 확인 날짜는 화면에서 기본 생략하고 Fact Ledger의 `accessed`에 보존한다.
  사용자가 요구한 확인일과 해석에 필요한 발행 연도·측정 기간·가격 기준일·버전·시행일은 유지한다.
- 수치의 분모·기간·업무 범위·초기 내부 결과 같은 조건은 해당 수치 가까이에 표시한다.
  확인된 사례와 협력 발표·미확인 후보·제안용 구성은 구분하며 상세 근거는 `web-search` 계약을 따른다.
- 여러 출처는 2개를 넘기지 않도록 핵심 근거를 선택
- 생성형 AI로 만든 그림이나 DEMO DATA는 명시

## 13. 상태·불확실성

- GA: neutral/primary style + `GA`
- Partial GA: secondary 또는 outline style + `PARTIAL GA`
- Preview: secondary accent + `PREVIEW`
- 가정: `ASSUMPTION`
- 시연 수치: `DEMO DATA`

상태마다 새 hue를 추가하지 않는다. 경고색이 꼭 필요한 위험 정보만 국소 예외로 쓰고, 텍스트 라벨은
반드시 유지한다.

## 14. 완성 직전

```bash
# 문법 검사 (.pyc를 만들지 않도록 py_compile 대신 ast.parse 사용)
python3 -B -c 'import ast,pathlib; ast.parse(pathlib.Path("<work-dir>/build_<deck>.py").read_text(encoding="utf-8"))'

# 생성
PPTX_OUT="<absolute-output>/<deck>.pptx" python3 -B <work-dir>/build_<deck>.py

# canonical QA: 구조 감사, 전체 렌더, rendered overlap, 위험 슬라이드, ZIP 검사를 통합 실행
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  <absolute-output>/<deck>.pptx --out <work-dir>/verify \
  --deck-spec <work-dir>/deck-spec.json --reuse-render

```

첫 실행 후 contact sheet와 위험 슬라이드를 확인하고 finding 단위 exception과
현재 revision의 증거를 작성한다. 기존 증거는 보존하고
[검증 가이드의 revision별 절차](./verification.md#visual-review-revisions)로 완료한다.
렌더·PDF 재사용 조건과 실패 복구는 [렌더 재사용](./verification.md#render-reuse)을 따른다.
