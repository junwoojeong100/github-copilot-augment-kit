---
name: slide-generator
description: "정리된 콘텐츠를 기반으로 가독성 높은 PowerPoint(.pptx) 발표자료를 설계하고 생성합니다. 서비스 비교, 아키텍처 리뷰, 전략 브리핑 산출물을 슬라이드 spec(JSON)으로 구조화한 뒤 python-pptx 기반 builder로 deck을 만듭니다. WHEN: PPT 만들기, 슬라이드 생성, 발표자료, 프레젠테이션, deck, pptx, create slides, presentation, customer briefing deck, 고객 발표자료, 제안 발표자료, strategy briefing deck, architecture review deck, service comparison deck."
argument-hint: "슬라이드로 만들 콘텐츠, 대상 청중, 목적, 톤, 원하는 슬라이드 수를 입력하세요"
---

# Slide Generator

콘텐츠를 **읽기 쉬운 PowerPoint(.pptx)** deck으로 변환합니다. slide spec(JSON)을 구성한 뒤 [slide_builder.py](./assets/slide_builder.py)(python-pptx)로 생성합니다.

## Executive Deck Blueprint (기본 템플릿)

별도 요구가 없으면 **15장 executive PPT**를 기본으로: Microsoft/컨설팅 스타일 · 최소 텍스트 · 강한 헤드라인.

**슬라이드별 구조 → builder 필드**: Title(짧은 카테고리)→`eyebrow` · Headline(인사이트 주장)→`heading` · 2–4 짧은 bullet→`bullets`/`cards`/`two_column` · Key takeaway(1문장)→`insight` · 시각화→slide `type`(+`source`).

**규칙**: 슬라이드당 1메시지 · 문단 금지(짧은 구) · 텍스트 최소 · 플랫폼/거버넌스 관점 · 기능 나열 금지("통제·가치"로 표현).

**표준 흐름**: WHY → WHAT → ARCHITECTURE → PLATFORM → PERFORMANCE → SECURITY → USE CASE → ROADMAP → KEY MESSAGE

| 흐름 | 권장 type | 흐름 | 권장 type |
|------|----------|------|----------|
| WHY | two_column/bullets | SECURITY | process/cards |
| WHAT | bullets/cards | USE CASE | table/cards |
| ARCHITECTURE | architecture | ROADMAP | timeline |
| PLATFORM | cards/bullets | KEY MESSAGE | callout(dark) |
| PERFORMANCE | kpi/table | | |

표지(`title`) · 요약(`cards`) · 마무리(`closing`)를 더해 15장. 흐름은 deck 목적에 맞게 가감.

## 빌드

```bash
cd .github/skills/slide-generator/assets
python3 -m venv .venv && source .venv/bin/activate   # PEP 668 대비
pip install -r requirements.txt
python slide_builder.py spec.json -o out.pptx
```

import도 지원: `from slide_builder import build_pptx; build_pptx("spec.json", "out.pptx")`

## Slide Spec (JSON)

최상위: `title`(필수) · `subtitle?` · `author?` · `eyebrow?` · `chips?` · `theme?` · `slides`(필수). `theme`로 `font`(기본 Segoe UI) · `kr_font`(기본 Malgun Gothic) · `colors` · `series`(accent·gold·teal·purple 순환) override.

모든 content 타입은 공통 옵션 `eyebrow` · `subhead` · `insight`("핵심") · `source`("출처")를 지원하고, 제목 언더라인 액센트 + 우상단 페이지 뱃지가 자동 적용됩니다.

| Type | 주요 필드 | 용도 |
|------|----------|------|
| `title` | heading?·subtitle?·author?·eyebrow?·chips? | 표지(네이비·골드 밴드) |
| `section` | heading·subtitle?·eyebrow?·number? | 장 전환 |
| `bullets` | heading·bullets(중첩 children 지원) | 핵심 메시지 카드 |
| `cards` | heading·cards:[{title,text,badge?}]·columns?·numbered? | 2~6 항목 그리드 |
| `kpi` | heading·items:[{value,label,caption?}]·style? | 수치 강조(≤4, solid=네이비+골드) |
| `timeline` | heading·phases:[{label,title?,items?}] | 로드맵(≤4) |
| `two_column` | heading·left/right:{title,bullets,color?} | 비교 |
| `table` | heading·columns·rows·emphasize_first_column? | 매핑/비교표(≤7행) |
| `architecture` | heading·layers:[{title,text?,highlight?}]·sidebar?·footer? | 레이어 다이어그램 |
| `process` | heading·steps:[{label,text?}] | 가로 플로우(≤6) |
| `callout` | heading·text·chips?·style?·note? | big statement(style:"dark"=KEY MESSAGE) |
| `closing` | heading·contact?·chips? | 마무리 |

예시:
```json
{ "type": "kpi", "heading": "도입 효과", "style": "solid",
  "items": [{"value": "55%", "label": "코딩 속도", "caption": "파일럿 가정치"}] }
```
중첩 bullet: `{"text": "상위", "children": ["하위1", "하위2"]}`. 전체 샘플은 [sample_deck.json](./assets/sample_deck.json).

## 디자인 마감 (자동 적용 — 별도 설정 불필요)
- 카드/패널/KPI/아키텍처/타임라인에 **soft shadow + 일관 모서리 반경**으로 입체감(`_panel`·`_soft_shadow`·`_rounded`). 좌측 액센트 바·언더라인 등 장식은 평면(`_bar`).
- 16:9, navy(`#0F2A4A`) 기반 + accent/gold/teal/purple 순환, 라틴/한글 폰트 분리.
- 아키텍처 레이어가 많으면 제목/설명을 좌우로 배치해 오버플로를 방지합니다.

## 가독성 원칙
슬라이드당 1메시지, bullet ≤6(초과 시 분리), 표 ≤7행. 텍스트 벽 대신 cards/kpi/timeline/architecture로 시각화하고, 긴 문장은 callout/two_column으로 분리합니다.

## Error Handling
| 상황 | 대응 |
|------|------|
| python-pptx 미설치 | `pip install -r requirements.txt` |
| PEP 668(외부 관리형 Python) 오류 | venv 사용(위 빌드 명령) |
| 알 수 없는 slide `type` | 지원 type 중 하나로 변경 |
| 필수 필드 누락 | 오류의 slide index·field 확인 → heading/bullets/columns/rows/cards/items/phases 추가 |
| 표/텍스트 과다 | 행 분리, callout/two_column으로 메시지 분할 |
