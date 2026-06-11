---
name: slide-generator
description: "정리된 콘텐츠를 기반으로 가독성 높은 PowerPoint(.pptx) 발표자료를 설계하고 생성합니다. 서비스 비교, 아키텍처 리뷰, 전략 브리핑 산출물을 슬라이드 spec(JSON)으로 구조화한 뒤 python-pptx 기반 builder로 deck을 만듭니다. WHEN: PPT 만들기, 슬라이드 생성, 발표자료, 프레젠테이션, deck, pptx, create slides, presentation, customer briefing deck, 고객 발표자료, 제안 발표자료, strategy briefing deck, architecture review deck, service comparison deck."
argument-hint: "슬라이드로 만들 콘텐츠, 대상 청중, 목적, 톤, 원하는 슬라이드 수를 입력하세요"
---

# Slide Generator

콘텐츠 → slide spec(JSON) → [slide_builder.py](./assets/slide_builder.py)(python-pptx) → `.pptx`.

## Executive Blueprint (기본)
15장 · Microsoft/컨설팅 스타일 · 최소 텍스트 · 강한 헤드라인.
- 구조→필드: 카테고리→`eyebrow` · 헤드라인(주장)→`heading` · 2~4 짧은 bullet→`bullets`/`cards`/`two_column` · 결론1문장→`insight` · 시각화→slide `type`.
- 규칙: 슬라이드당 1메시지 · 문단 금지 · 텍스트 최소 · 거버넌스 관점 · 기능 나열 금지("통제·가치"로).
- 흐름: WHY→WHAT→ARCHITECTURE→PLATFORM→PERFORMANCE→SECURITY→USE CASE→ROADMAP→KEY MESSAGE (+ title·cards·closing = 15장).
- type 매핑: WHY/WHAT=two_column·bullets·cards · ARCHITECTURE=architecture · PLATFORM=cards · PERFORMANCE=kpi·table · SECURITY=process·cards · USE CASE=table·cards · ROADMAP=timeline · KEY MESSAGE=callout(dark).

## 빌드
```bash
cd .github/skills/slide-generator/assets
python3 -m venv .venv && source .venv/bin/activate   # PEP668 대비
pip install -r requirements.txt
python slide_builder.py spec.json -o out.pptx
```

## Spec (JSON)
최상위: `title`(필수) · `subtitle?` · `author?` · `eyebrow?` · `chips?` · `theme?`(font·kr_font·colors·series) · `slides`(필수).
공통 옵션(content): `eyebrow` · `subhead` · `insight` · `source`. 언더라인 액센트·페이지 뱃지·soft shadow·둥근모서리 자동.

| type | 주요 필드 |
|------|----------|
| title | heading?·subtitle?·author?·eyebrow?·chips? |
| section | heading·number?·eyebrow? |
| bullets | heading·bullets(중첩 children) |
| cards | heading·cards:[{title,text,badge?}]·columns?·numbered? |
| kpi | heading·items:[{value,label,caption?}]·style?(solid) |
| timeline | heading·phases:[{label,title?,items?}] |
| two_column | heading·left/right:{title,bullets,color?} |
| table | heading·columns·rows·emphasize_first_column? |
| architecture | heading·layers:[{title,text?,highlight?}]·sidebar?·footer? |
| process | heading·steps:[{label,text?}] |
| callout | heading·text·style?(dark)·note?·chips? |
| closing | heading·contact?·chips? |

샘플: [sample_deck.json](./assets/sample_deck.json).

## 한계·처리
bullet ≤6 · 표 ≤7행. python-pptx 미설치→`pip install -r requirements.txt` · PEP668→venv · 알 수 없는 type/필수 필드 누락→오류의 index·field 확인 후 추가.
