# Slide Design Guide

읽기 쉬운 PowerPoint deck은 많은 정보를 넣는 것이 아니라, 청중이 한 번에 이해할 수 있도록 메시지를 구조화하는 데 집중합니다.

## Readability Principles

| 원칙 | 의미 | `slide_builder.py` 적용 방식 |
|------|------|------------------------------|
| One idea per slide | 슬라이드마다 하나의 핵심 메시지만 전달 | `heading`을 강한 메시지로 사용하고 slide type별 목적을 분리 |
| 6x6 rule | 한 슬라이드에 6개 이하 bullet, bullet당 6단어 수준을 지향 | `bullets` slide는 top-level bullet을 자동 제한하고 초과 시 분리 안내 |
| Visual hierarchy | 제목 → 섹션 → 본문 → footer 순서로 시선 흐름 설계 | 큰 heading, accent color, card/table 영역으로 계층 구분 |
| Contrast | 배경과 텍스트 대비를 확보 | Navy/white, dark text/light background 팔레트 사용 |
| Consistent color | 색상 의미를 일관되게 유지 | `THEME` dict에서 primary, accent, gray 계열을 중앙 관리 |
| Minimal text | 문단보다 짧은 문장과 키워드 중심 | `callout`, `two_column`, `table` type으로 긴 설명을 구조화 |
| Chart/table over walls of text | 비교·수치·매핑은 표나 시각 구조로 표현 | `table` slide는 header fill, alternating row shading 적용 |

## Slide Type Mapping

- `title`: 덱 목적과 대상 청중을 명확히 알리는 opening slide (eyebrow·chips 활용)
- `section`: 긴 deck의 장 전환을 위한 divider (큰 number로 진행감 부여)
- `bullets`: 핵심 메시지와 근거를 컬러 마커 카드로 정리
- `cards`: 4가지 강점·시나리오·구성요소처럼 **병렬 항목**을 카드 그리드로 표현 (좌측 컬러바·구분선, `numbered:true`면 번호 뱃지)
- `kpi`: 도입 효과·시장 규모 등 **핵심 수치**를 큰 숫자로 각인 (최대 4개, `style:"solid"`면 네이비 임팩트)
- `timeline`: 단계별 로드맵·도입 계획을 가로 흐름으로 표현 (최대 4단계)
- `architecture`: 플랫폼·데이터·신원·보안의 **레이어 구조**를 다이어그램으로 (좌측 사이드바·하단 거버넌스 바, 한 레이어 `highlight`로 강조)
- `process`: 단계 흐름(코드→리뷰→수정→운영)을 **가로 플로우 + 화살표**로 표현 (최대 6단계)
- `two_column`: 옵션 비교, 현재/미래, 장점/리스크처럼 대비가 필요한 내용
- `table`: 서비스 매핑, 경쟁 비교, 우선순위 등 구조화된 비교
- `callout`: 고객이 기억해야 할 big statement (chips로 키워드 강조, `style:"dark"`면 네이비 풀스크린 KEY MESSAGE)
- `closing`: next step, contact, Q&A 안내

## Color System

| 역할 | 토큰 | 기본값 | 용도 |
|------|------|--------|------|
| Primary | `primary` | `#0F2A4A` | 제목·표지/마무리 배경·헤더 |
| Accent | `accent` | `#0078D4` | 1차 강조 (Microsoft 블루) |
| Series | `gold`·`teal`·`purple` | `#E6A532`·`#0E7C86`·`#6B4FA1` | 카드/마커/타임라인 컬러 순환 |
| Surface | `card`·`card_alt`·`border` | `#FFFFFF`·`#F3F7FC`·`#D8E0EA` | 카드 면·연한 배경·테두리 |

- 색상은 **의미 단위로 순환**합니다. `series` 배열 순서대로 카드·항목에 자동 배정되어 단조로움을 피합니다.
- 강조색(gold·teal·purple)은 카드 상단바·번호 뱃지·헤더에만 쓰고, 본문 텍스트는 `text`/`muted_text`로 유지합니다.

## Card Layout Principles

1. **One concept per card**: 카드 하나에 제목 1개 + 1~2줄 설명. 카드 안에 또 다른 리스트를 넣지 않습니다.
2. **항목 수 → 타입 선택**: 병렬 항목은 `cards`(2~6), 수치는 `kpi`(2~4), 단계는 `timeline`(2~4)로 매핑합니다.
3. **eyebrow + heading**: content 슬라이드는 영문 `eyebrow` 라벨과 문장형 `heading`을 짝지어 맥락을 줍니다.
4. **insight / source**: 슬라이드의 결론은 `insight`("핵심"), 근거는 `source`("출처") 박스로 분리합니다.

## Practical Guidance

1. 슬라이드 제목은 문장형 메시지로 작성합니다. 예: “Azure는 Microsoft 투자 고객에게 TCO 이점이 큽니다.”
2. 표는 4~6개 열, 5~7개 행 이내로 유지합니다. 상세 표는 appendix로 분리합니다.
3. `callout`은 deck 전체에서 1~2회만 사용해 강조 효과를 유지합니다.
4. 색상·폰트·시리즈 변경은 `assets/slide_builder.py`의 `THEME` dict 또는 spec의 `theme`에서만 수행합니다.
5. 한국어 deck은 `kr_font`(기본 `Malgun Gothic`)를 유지해 한글 가독성을 확보합니다.
