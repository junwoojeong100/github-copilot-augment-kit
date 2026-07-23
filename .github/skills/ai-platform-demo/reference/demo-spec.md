# Demo Spec Contract

`demo-spec.json`은 고객별 AI·App Platform 콘텐츠와 산업 동작을 한 곳에 잠그는 build contract다
(디자인은 고정 GitHub Primer Dark Dimmed 계열 soft-dark). Fact
Ledger와 storyline을 먼저 확정한 뒤 작성하며, Renderer가 읽을 수 있는 JSON이어야 한다.

기본 생성 경로에서는 이 파일을 0부터 직접 작성하지 않고
`reference/composable-spec.md`의 Base + Industry Pack + Customer Overlay 방식으로 합성한다. 적합한
Pack이 없거나 bespoke 구조가 더 빠르고 정확할 때만 전체 Spec을 직접 작성한다.

`schema/demo-spec.schema.json`은 editor completion용이고, 실제 완료 판정은
`scripts/render_demo.py --validate-only`의 구조·semantic·security validation을 기준으로 한다.

## 1. Top-level

```json
{
  "meta": {},
  "design": {},
  "story": {},
  "navigation": [],
  "dashboard": {},
  "operations": {},
  "simulator": {},
  "improvement": {},
  "finance": {},
  "devops": {},
  "agents": {},
  "governance": {},
  "notification": {}
}
```

위 section과 `notification`은 필수다. `design`은 base spec이 고정 soft-dark marker로 제공하며 고객
Overlay는 정의하지 않는다. 고정값은 `archetype=trusted-executive`, `theme=dark-dimmed`,
`density=executive`, `motion=balanced`, `tokens={}`다. 나머지 marker field도 base를 그대로 유지한다.
시각 토큰의 유일한 원천은 `runtime.css`다.

## 2. Meta

```json
{
  "meta": {
    "customer": "Customer",
    "industry": "Industry",
    "audience": "CEO, COO, CFO, CIO",
    "appName": "Customer IQ",
    "initials": "CI",
    "language": "ko",
    "infrastructureLabel": "Microsoft Foundry · GitHub · AKS/ACA 참조 아키텍처",
    "demoNote": "모든 수치는 시연용 가정치입니다."
  }
}
```

실명 대신 회사명·직무를 사용한다. `language`가 `ko`이면 임원이 보는 문구는 한글 우선으로 작성한다.
공식 제품명, 업계 표준 약어·단위, 코드 식별자처럼 영어가 더 명확하거나 일반적인 경우만 영어를 유지한다.

## 3. Navigation

Golden Runtime 데이터 계약은 정확히 8개 항목이며 ID와 순서를 고정한다. 사용자에게 노출할 route는
`story.routeScope`로 별도 선택한다.

```json
[
  {"id":"dashboard","icon":"◫","name":"경영 현황","short":"전체"},
  {"id":"operations","icon":"◇","name":"통합 운영","short":"실시간"},
  {"id":"simulator","icon":"△","name":"예측 시뮬레이션","short":"예측"},
  {"id":"improvement","icon":"◎","name":"개선 과제","short":"개선"},
  {"id":"finance","icon":"₩","name":"재무 효과","short":"재무"},
  {"id":"devops","icon":"⌘","name":"개발·배포","short":"GitHub"},
  {"id":"agents","icon":"✦","name":"AI 에이전트","short":"협업"},
  {"id":"governance","icon":"⬡","name":"통합 거버넌스","short":"통제"}
]
```

ID와 순서는 고정이지만 메뉴명·crumb는 `DEMO_FOCUS`와 고객 업무에 맞게 바꾼다. 기본은 8개를 모두
노출한다. 좁은 목적이면 `story.routeScope`에 canonical 순서로 `dashboard`부터 4~7개를 지정한다.
메뉴·제목·버튼·상태는 `meta.language`를 따르며 공식명 또는 일반 약어는 원문을 유지한다.

## 4. Straightforward content contract

- `dashboard.hero.title`은 제품명이 아니라 고객 결과를 한 문장으로 말한다.
- 각 route는 임원 질문 하나와 primary action 하나를 중심으로 구성한다.
- 클릭 전/후의 KPI·상태·추천은 눈에 띄게 달라야 한다.
- 제품명은 고객 가치 흐름에서 맡는 역할과 함께 쓴다. 한 화면에 제품 catalog를 만들지 않는다.
- 8개 route 데이터는 유지하되, `story.routeScope`와 핵심 4~6개 장면은 목적에 맞춰 정한다.

## 5. 공통 data shapes

### KPI

```json
{
  "label": "First-Pass Yield",
  "value": 98.4,
  "decimals": 2,
  "unit": "%",
  "delta": "+0.3%p demo",
  "direction": "up",
  "icon": "✓",
  "color": "success",
  "series": [97.8, 98.0, 98.1, 98.4],
  "tick": {"min": -0.05, "max": 0.08}
}
```

### Clickable row

```json
{
  "cells": ["Line A", "98.4%", "Stable"],
  "status": {"label": "Stable", "tone": "ok"},
  "detailTitle": "Line A",
  "detail": "선택한 항목의 데모 설명"
}
```

### Feed item

```json
{"icon":"✓","title":"Quality Agent","text":"후보 4건을 우선순위화했습니다."}
```

## 6. Route sections

### Dashboard

- `hero`: `title`, `subtitle`, `badge`
- `kpis`: KPI 4개
- `stream`: `label`, `unit`, `values`, `min`, `max`
- `feed`: 4개 이상
- `table`: `title`, `hint`, `headers`, `rows`
- `learningLoop`: `label`, `value`, `unit`, `note`

### Operations

- `hero`, `kpis`
- `flow.nodes`: 4~7개, 각 `name`, `metric`, `status`, `detail`
- `flow.events`: moving object가 통과할 때 표시할 문장
- `action`: `button`, `running`, `complete`, `recommendationBefore`, `recommendationAfter`
- `table`

### Simulator

- `hero`
- `inputs`: 정확히 3개 권장
  - `id`(CSS selector-safe), `label`, `min`, `max`, `step`(양수), `value`, `unit`, `optimum`, `weight`
- `output`: `label`, `unit`, `base`, `min`, `max`, `decimals`,
  `goodThreshold`, `warningThreshold`, `goodLabel`, `warningLabel`, `dangerLabel`
- `secondary`: `label`, `base`, `unit`, `decimals`, `weights`
- `recommendations`: `inputId`, `operator`, `threshold`, `message`
- `recommendations`의 마지막 항목은 유일한 `operator: "default"` 규칙
- `defaultRecommendation`: 조건 규칙이 일치하지 않을 때 표시할 기본 설명
- `history`

Runtime formula:

```text
output = clamp(base - Σ(abs(value - optimum) * weight), min, max)
secondary = base + Σ((value - input.value) * weights[input.id])
```

복잡한 산업 공식이 필요하면 generated HTML의 simulator route만 bespoke extension한다.

### Improvement

- `hero`, `kpis`
- `steps`: 5~7개
- `factors`: `label`, `value`, `color`
- `impacts`: 4개 권장
- `board`: 3개 column, 각 clickable item

### Finance

- `hero`
- `levers`: selector-safe `id`, `label`, range, 양수 `step`, `value`, `unit`
- `margin`: `base`, `unit`, `decimals`, `label`
- `summaryMetrics`: `label`, `base`, `unit`, `impacts`
- `composition`: 4개 segment
- `watchlist`

### DevOps

- `hero`, `kpis`
- `steps`: repository research·계획·코드/PR·GitHub Actions·AKS/ACA delivery 중 focus에 맞는 5개 이상.
  Runtime action의 직접 결과는 autonomous PR 또는 high-risk 실행 계획이며, 후속 CI/CD·runtime 상태는
  steps와 운영 route의 primary action으로 이어서 표현한다.
- `issues`: 3개 이상
  - `id`, `title`, `product`, `type`, `risk`, `status`, `diffLines`, `highRisk`
  - `highRisk=false`와 `highRisk=true` issue를 각각 하나 이상 포함해 autonomous와 human-led 경로를 모두 검증

### Agents

- `hero`
- `profiles`: 5~7개. 업무 Agent뿐 아니라 Platform·SRE·Release·FinOps·Security Agent를 사용할 수 있다.
  - `icon`, `name`, `subtitle`, `intro`
  - `qa`: 정확히 3개 권장, 각 `question`, `answer`
- `orchestration`: `intro`, `stages`, `summary`
- 모든 profile 이름은 서로 달라야 한다.

### Governance

- `hero`
- `cards`: 3개
- `controls`: Microsoft Entra ID, Microsoft Purview, Azure AI Content Safety, Microsoft Defender,
  GitHub AI Controls, GitHub Advanced Security, AKS/ACA policy, observability 등을 고객 맥락에 매핑
- `memories`: 고객 소유 평가셋·패턴·playbook
- `learningLoop`: 4단계
- `evaluation`: `initialScore`, `finalScore`, `checks`

## 7. Spec 작성 순서

1. 고객 요청마다 `web-search` 공통 계약을 따르는 실시간 `fact-ledger.md`와 machine-readable
   `fact-ledger.json`을 새로 만들고 검증된 사실과 DEMO 가정을 분리한다.
   직접 Spec을 작성하는 경우에도 `meta.research`에 현재 Ledger의 `checkedAt`, canonical source 2개 이상,
   Ledger ID를 포함해야 하며 누락된 Spec은 Renderer가 거부한다.
2. `DEMO_FOCUS`와 핵심 4~6개 시연 동선을 view contract에 정하고 Storyline·audience message를
   `story`에 잠근다.
3. 디자인은 GitHub soft-dark로 고정되어 base가 제공한다(고객 Overlay에는 `design`을 넣지 않는다).
4. View Contract의 high-impact route를 고객 Overlay로 변환한다.
5. Composer로 Industry Pack과 Overlay를 합쳐 전체 Spec을 만든다.
6. Renderer validation을 통과시킨다.
7. 생성 후에는 HTML보다 customer Overlay를 우선 수정해 재합성한다.

## 8. 금지

- JSON 안에 실행 JavaScript 함수나 사용자 입력 `eval`을 넣지 않는다.
- 색 필드는 `brand`, `accent`, `info`, `success`, `warning`, `danger`, `violet` semantic token만 사용한다.
- Rich text가 필요한 필드는 `<b>`, `<strong>`, `<em>`, `<code>`, `<br>`, `<div>`, `<span>`만 허용한다.
  속성은 message stat용으로 승인된 `class`만 가능하며 `style`, event handler, URL, SVG, image는 금지한다.
- 검증되지 않은 실제 고객 수치와 DEMO 수치를 섞지 않는다.
- route ID를 바꾸지 않는다.
- agent profile을 하나만 만들고 이름만 바꾸는 식으로 복제하지 않는다.
- App Platform·CI/CD 중심 요청을 AI-only climax로 되돌리거나, 제품명만 나열해 focus를 대신하지 않는다.
- Runtime 공통 파일에 고객명을 hard-code하지 않는다.
