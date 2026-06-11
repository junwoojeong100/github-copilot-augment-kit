---
name: slide-generator
description: "정리된 콘텐츠를 기반으로 가독성 높은 PowerPoint(.pptx) 발표자료를 설계하고 생성합니다. 서비스 비교, 아키텍처 리뷰, 전략 브리핑 산출물을 슬라이드 spec(JSON)으로 구조화한 뒤 python-pptx 기반 builder로 deck을 만듭니다. WHEN: PPT 만들기, 슬라이드 생성, 발표자료, 프레젠테이션, deck, pptx, create slides, presentation, customer briefing deck, 고객 발표자료, 제안 발표자료, strategy briefing deck, architecture review deck, service comparison deck."
argument-hint: "슬라이드로 만들 콘텐츠, 대상 청중, 목적, 톤, 원하는 슬라이드 수를 입력하세요"
---

# Slide Generator

정리된 콘텐츠를 **읽기 쉬운 PowerPoint(.pptx) deck**으로 변환하는 스킬입니다. `cloud-competitive-analysis`, `azure-architecture-review`, `it-ai-strategy-advisory` 등 다른 스킬의 산출물을 발표 흐름에 맞게 구조화하고, [slide_builder.py](./assets/slide_builder.py)로 일관된 디자인의 `.pptx` 파일을 생성합니다.

## When to Use

- **고객 발표자료**: customer briefing, 제안 발표, 임원 보고용 deck이 필요할 때
- **서비스 비교**: Azure vs AWS vs GCP, GitHub vs GitLab 등 비교표를 슬라이드로 만들 때
- **아키텍처 리뷰**: WAF 리뷰 결과, 개선 권고, roadmap을 전달용 deck으로 정리할 때
- **전략 브리핑**: IT/AI/AX 전략, ROI, governance, roadmap을 executive summary 형태로 발표할 때
- **기존 문서 변환**: 긴 Markdown/보고서를 짧고 명확한 presentation flow로 재구성할 때

## 사전 조건

| 항목 | 기준 |
|------|------|
| Python | Python 3.10+ |
| Package | `python-pptx>=1.0.2` ([requirements.txt](./assets/requirements.txt)) |
| Input | 구조화 가능한 콘텐츠 또는 slide spec JSON |
| Design guide | [slide-design-guide.md](./references/slide-design-guide.md) |

## Workflow

### Step 1: 콘텐츠 구조화

다른 스킬 또는 사용자 입력을 발표 흐름으로 재구성합니다.

| 입력 예시 | 변환 방식 |
|----------|----------|
| `cloud-competitive-analysis` 비교표 | `table`, `two_column`, `callout` 중심의 service comparison deck |
| `azure-architecture-review` 리뷰 | `section`, `cards`, `table`로 findings, risks, recommendations 정리 |
| `it-ai-strategy-advisory` 전략 | `title`, `cards`(use case), `kpi`(지표), `timeline`(로드맵), `two_column`, `closing`으로 executive briefing 구성 |

> **디자인 권장**: 텍스트 나열보다 시각 구조를 우선합니다. 4가지 항목은 `cards`, 핵심 수치는 `kpi`,
> 단계별 계획은 `timeline`으로 표현하고, content 슬라이드에는 `eyebrow`(영문 라벨)·`insight`("핵심")·`source`("출처")를 더해 밀도를 높입니다.

이 단계의 산출물은 `slide spec(JSON)`입니다. 샘플은 [sample_deck.json](./assets/sample_deck.json)을 참고합니다.

### Step 2: `slide_builder.py`로 .pptx 생성

```bash
cd .github/skills/slide-generator/assets
# 권장: 가상환경 사용 (외부 관리형 Python / PEP 668 환경 대비)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python slide_builder.py sample_deck.json -o sample_deck.pptx
```

`slide_builder.py`는 CLI와 import 방식을 모두 지원합니다.

```python
from slide_builder import build_pptx

build_pptx("sample_deck.json", "sample_deck.pptx")
```

### Step 3: 검토/전달

1. deck title, slide order, 핵심 메시지 흐름을 검토합니다.
2. 긴 문장, 과도한 bullet, 너무 큰 table은 분리합니다.
3. 고객명, 날짜, 발표자, contact 등 전달 정보를 확인합니다.
4. 최종 `.pptx`와 필요 시 slide spec JSON을 함께 전달합니다.

## Slide Spec Schema

최상위 JSON 구조:

```json
{
  "title": "Deck title",
  "subtitle": "Optional subtitle",
  "author": "Optional author",
  "eyebrow": "Optional eyebrow label (영문 카테고리)",
  "chips": ["Optional", "키워드", "칩"],
  "theme": {
    "font": "Segoe UI",
    "kr_font": "Malgun Gothic",
    "colors": { "primary": "0F2A4A", "accent": "0078D4" },
    "series": ["accent", "gold", "teal", "purple"]
  },
  "slides": [
    { "type": "title", "heading": "Opening title", "subtitle": "Optional", "author": "Optional" }
  ]
}
```

### Common Fields

| 필드 | 필수 | 설명 |
|------|------|------|
| `title` | Yes | deck title. footer에도 사용 |
| `subtitle` | No | title slide 보조 문구 |
| `author` | No | 작성자/조직/날짜 |
| `eyebrow` | No | deck/슬라이드 상단 영문 카테고리 라벨 (예: `WHY NOW`) |
| `chips` | No | title/callout/closing의 키워드 칩 배열 (최대 6개) |
| `theme` | No | `font`(라틴), `kr_font`(한글/동아시아), `colors`, `series` override. 기본값은 builder의 `THEME` dict |
| `slides` | Yes | slide 객체 배열 |

> **폰트**: 기본은 라틴 `Segoe UI` + 한글 `Malgun Gothic`을 run마다 분리 적용합니다. 한국어 발표에 권장됩니다.
> **컬러 시리즈(`series`)**: 슬라이드/카드 인덱스에 따라 `accent`(파랑)·`gold`·`teal`·`purple`을 순환 적용해 시각적 리듬을 만듭니다.

### Slide Types Supported

모든 content 타입(`bullets`·`two_column`·`table`·`callout`·`cards`·`kpi`·`timeline`·`architecture`·`process`)은 공통 옵션으로
`eyebrow`(영문 라벨), `subhead`(제목 아래 보조 한 줄), `insight`("핵심" 박스), `source`("출처" 박스)를 지원합니다.
content 슬라이드는 **제목 아래 언더라인 액센트(풀폭 hairline + 짧은 컬러 세그먼트)**와 우상단 페이지 뱃지가 자동으로 붙습니다.

| Type | 주요 필드 | 용도 |
|------|------|------|
| `title` | `heading?`, `subtitle?`, `author?`, `eyebrow?`, `chips?` | opening slide (네이비 배경·골드 밴드·코너 액센트) |
| `section` | `heading`, `subtitle?`, `eyebrow?`, `number?` | 장 전환 divider (큰 번호) |
| `bullets` | `heading`, `bullets` | 핵심 메시지를 컬러 마커 카드로. nested sub-bullets 지원 |
| `cards` | `heading`, `cards:[{title,text,badge?}]`, `columns?`, `numbered?` | 2~6개 항목 카드 그리드 (좌측 컬러바·구분선, `numbered:true`면 번호 뱃지) |
| `kpi` | `heading`, `items:[{value,label,caption?}]`, `style?` | 핵심 수치 강조 (최대 4개). `style:"solid"`면 네이비 박스+골드 숫자 |
| `timeline` | `heading`, `phases:[{label,title?,items?}]` | 단계별 로드맵 (연결선·번호 dot, 최대 4단계) |
| `two_column` | `heading`, `left:{title,bullets,color?}`, `right:{…}` | 옵션/장단점/Before-After 비교 (컬러 헤더) |
| `table` | `heading`, `columns`, `rows`, `emphasize_first_column?` | 서비스 매핑·경쟁 비교·우선순위 표 |
| `architecture` | `heading`, `layers:[{title,text?,highlight?}]`, `sidebar?`, `footer?`, `subhead?` | 레이어 스택 아키텍처 다이어그램 (좌측 사이드바·하단 거버넌스 바) |
| `process` | `heading`, `steps:[{label,text?}]` | 가로 단계 플로우 (네이비/블루 박스 + 골드 쉐브론 화살표, 최대 6단계) |
| `callout` | `heading`, `text`, `chips?`, `style?`, `note?` | big statement. `style:"dark"`면 네이비 풀스크린 KEY MESSAGE |
| `closing` | `heading`, `contact?`, `chips?` | Q&A, next step, contact (네이비 배경·골드 밴드) |

Nested bullet 예시:

```json
{
  "type": "bullets",
  "eyebrow": "Differentiators",
  "heading": "Microsoft 차별화 포인트",
  "insight": "단일 서비스가 아니라 플랫폼 전략으로 봅니다.",
  "bullets": [
    {
      "text": "Azure + Microsoft Foundry + GitHub Copilot 생태계",
      "children": ["모델 접근", "개발 생산성", "거버넌스"]
    }
  ]
}
```

신규 시각 타입 예시:

```json
{ "type": "cards", "heading": "4대 시나리오", "numbered": true, "cards": [
    {"title": "규제 대응 Copilot", "text": "규정·내부통제 문서 연결 (RAG)"},
    {"title": "고객 상담 자동화", "text": "지식 기반 응대"}
] }
```

```json
{ "type": "kpi", "heading": "도입 효과", "style": "solid", "items": [
    {"value": "55%", "label": "코딩 속도 향상", "caption": "파일럿 가정치"},
    {"value": "24/7", "label": "디지털 상담", "caption": "무중단 응대"}
] }
```

```json
{ "type": "architecture", "heading": "안전한 AI 아키텍처",
  "subhead": "플랫폼·데이터·신원·보안의 결합",
  "sidebar": {"eyebrow": "신원 통제", "name": "Microsoft Entra", "text": "조건부 접근 · 최소 권한"},
  "layers": [
    {"title": "사용자 채널", "text": "Teams · M365 Copilot"},
    {"title": "AI 플랫폼 · Microsoft Foundry", "text": "모델 · 에이전트 · 평가", "highlight": true},
    {"title": "근거 검색 · Azure AI Search", "text": "하이브리드 · 벡터 RAG"}
  ],
  "footer": {"title": "거버넌스 & 보안", "text": "Purview · Defender · GitHub Advanced Security"} }
```

```json
{ "type": "process", "heading": "보안 내재화 SDLC", "steps": [
    {"label": "코드 작성"}, {"label": "리뷰"}, {"label": "취약점 수정"}, {"label": "운영 반영"}
] }
```

```json
{ "type": "callout", "style": "dark", "eyebrow": "Key Message",
  "heading": "핵심 메시지", "text": "통제 구조 안에서 생산성과 고객 가치를 함께 높입니다.",
  "note": "Microsoft Foundry · Azure AI · Purview · Entra · Defender · GitHub",
  "chips": ["규제 대응", "데이터 통제", "개발 생산성"] }
```

```json
{ "type": "timeline", "heading": "로드맵", "phases": [
    {"label": "Now · 0~3M", "title": "Quick Win", "items": ["Copilot 파일럿"]},
    {"label": "Next · 3~12M", "title": "확산", "items": ["랜딩존", "AI CoE"]}
] }
```

## How Readability Is Enforced

- **16:9 layout**: widescreen 기본 비율 사용
- **카드 기반 시각 시스템**: bullets·cards·kpi·timeline·two_column·architecture·process를 둥근 카드/다이어그램으로 렌더링해 텍스트 벽(wall of text)을 방지
- **제목 언더라인 액센트**: content 슬라이드마다 제목 아래 풀폭 hairline + 짧은 컬러 세그먼트로 헤더/본문을 분리
- **멀티컬러 액센트 시리즈**: navy `#0F2A4A` 기반에 `accent`(파랑)·`gold`·`teal`·`purple`을 순환 적용 — `THEME` dict에서 중앙 관리
- **일관된 헤더**: content 슬라이드마다 `eyebrow`(영문 라벨) + 큰 heading + 우상단 페이지 뱃지로 시선 흐름 고정
- **핵심/출처 박스**: `insight`("핵심")·`source`("출처")를 하단 강조 박스로 분리해 메시지와 근거를 구분
- **라틴/한글 폰트 분리**: 라틴 `Segoe UI` + 한글 `Malgun Gothic`을 run마다 적용
- **Bullet 제한**: top-level bullet은 자동 제한(6개)하고 초과 시 분리 안내 문구 삽입
- **Table readability**: navy header, 첫 컬럼 강조, alternating row shading, 기본 banded 스타일 제거
- **Text safety**: 긴 텍스트는 wrap되며, optional field 누락 시 기본값 또는 생략 처리

자세한 원칙은 [slide-design-guide.md](./references/slide-design-guide.md)를 따릅니다.

## Output Format

기본 응답은 다음을 포함합니다.

```markdown
## Slide Deck 생성 결과

- Spec: <path-to-spec.json>
- PPTX: <path-to-output.pptx>
- Slide count: <n>
- Theme: Microsoft-inspired readable theme

## 검토 포인트
- 핵심 메시지 흐름
- 긴 문장/표 분리 필요 여부
- 고객명/발표자/contact 확인
```

## Error Handling

| 상황 | 대응 |
|------|------|
| `python-pptx` 미설치 | `cd .github/skills/slide-generator/assets && pip install -r requirements.txt` 실행 |
| `pip install` 시 PEP 668(외부 관리형 Python) 오류 | 가상환경 사용: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (또는 `pip install --user python-pptx`) |
| Python 버전 낮음 | Python 3.10+ 환경에서 실행 |
| JSON 문법 오류 | JSON parser 오류 위치를 확인하고 comma/quote를 수정 |
| 알 수 없는 slide `type` | 지원 type(`title`, `section`, `bullets`, `two_column`, `table`, `callout`, `closing`, `cards`, `kpi`, `timeline`, `architecture`, `process`) 중 하나로 변경 |
| 필수 필드 누락 | 오류 메시지의 slide index와 field를 확인해 `heading`, `bullets`, `columns`, `rows`, `cards`, `items`, `phases` 등을 추가 |
| 표가 너무 큼 | 핵심 5~7개 행만 본문 slide에 유지하고 상세 표는 appendix 또는 별도 문서로 분리 |
| 텍스트가 너무 김 | `bullets`, `two_column`, `callout`으로 나누고 한 slide에 하나의 메시지만 유지 |
| 출력 경로 권한 없음 | 쓰기 가능한 repo 내부 경로 또는 사용자 지정 output path 사용 |

## Assets & References

- Builder: [assets/slide_builder.py](./assets/slide_builder.py)
- Requirements: [assets/requirements.txt](./assets/requirements.txt)
- Sample spec: [assets/sample_deck.json](./assets/sample_deck.json)
- Design guide: [references/slide-design-guide.md](./references/slide-design-guide.md)
