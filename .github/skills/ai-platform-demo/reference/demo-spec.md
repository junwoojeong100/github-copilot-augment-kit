# Demo Spec Contract

`demo-spec.json`은 고객별 콘텐츠·Design DNA·산업 동작을 한 곳에 잠그는 build contract다. Fact
Ledger와 storyline을 먼저 확정한 뒤 작성하며, Renderer가 읽을 수 있는 JSON이어야 한다.

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
  "governance": {}
}
```

모든 top-level section은 필수다.

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
    "infrastructureLabel": "Microsoft Foundry · Reference Architecture",
    "demoNote": "모든 수치는 시연용 가정치입니다."
  }
}
```

실명 대신 회사명·직무를 사용한다.

## 3. Navigation

정확히 8개 항목이며 ID는 고정한다.

```json
[
  {"id":"dashboard","icon":"◫","name":"Executive Cockpit","short":"Overview"},
  {"id":"operations","icon":"◇","name":"Operations","short":"Live"},
  {"id":"simulator","icon":"△","name":"Simulator","short":"Predict"},
  {"id":"improvement","icon":"◎","name":"Improvement","short":"Improve"},
  {"id":"finance","icon":"₩","name":"Economics","short":"Finance"},
  {"id":"devops","icon":"⌘","name":"Software Delivery","short":"Copilot"},
  {"id":"agents","icon":"✦","name":"Agent Studio","short":"Orchestrate"},
  {"id":"governance","icon":"⬡","name":"Trust","short":"Govern"}
]
```

## 4. 공통 data shapes

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
  "status": "ok",
  "detailTitle": "Line A",
  "detail": "선택한 항목의 데모 설명"
}
```

### Feed item

```json
{"icon":"✓","title":"Quality Agent","text":"후보 4건을 우선순위화했습니다."}
```

## 5. Route sections

### Dashboard

- `hero`: `title`, `subtitle`, `badge`
- `kpis`: KPI 4개
- `stream`: `label`, `unit`, `values`, `min`, `max`
- `feed`: 4개 이상
- `table`: `headers`, `rows`
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
  - `id`, `label`, `min`, `max`, `step`, `value`, `unit`, `optimum`, `weight`
- `output`: `label`, `unit`, `base`, `min`, `max`, `decimals`
- `secondary`: `label`, `base`, `unit`, `decimals`, `weights`
- `recommendations`: `inputId`, `operator`, `threshold`, `message`
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
- `levers`: `id`, `label`, range, `value`, `unit`, `impact`
- `margin`: `base`, `unit`, `decimals`, `label`
- `summaryMetrics`: `label`, `base`, `unit`, `impacts`
- `composition`: 4개 segment
- `watchlist`

### DevOps

- `hero`, `kpis`
- `steps`: repository research부터 PR까지 5개
- `issues`: 3개 이상
  - `id`, `title`, `product`, `type`, `risk`, `status`, `diffLines`
- `highRiskBehavior`: 고위험 issue는 plan-only/human-led로 표시

### Agents

- `hero`
- `profiles`: 5~7개
  - `icon`, `name`, `subtitle`, `intro`
  - `qa`: 정확히 3개 권장, 각 `question`, `answer`
- `orchestration`: `intro`, `stages`, `summary`
- 모든 profile 이름은 서로 달라야 한다.

### Governance

- `hero`
- `cards`: 3개
- `controls`: Entra, Purview, Content Safety, Defender, GitHub, observability 등을 고객 맥락에 매핑
- `memories`: 고객 소유 평가셋·패턴·playbook
- `learningLoop`: 4단계
- `evaluation`: `initialScore`, `finalScore`, `checks`

## 6. Spec 작성 순서

1. Fact Ledger의 검증된 사실과 DEMO 가정을 분리한다.
2. Storyline과 audience message를 `story`에 잠근다.
3. Adaptive Design DNA를 `design`에 잠근다.
4. View Contract를 route section으로 변환한다.
5. Renderer validation을 통과시킨다.
6. 생성 후에는 HTML이 아니라 spec을 우선 수정해 재생성한다.

## 7. 금지

- JSON 안에 실행 JavaScript 함수나 사용자 입력 `eval`을 넣지 않는다.
- Rich text가 필요한 필드는 `<b>`, `<strong>`, `<em>`, `<code>`, `<br>`, `<div>`, `<span>`만 허용한다.
  속성은 message stat용으로 승인된 `class`만 가능하며 `style`, event handler, URL, SVG, image는 금지한다.
- 검증되지 않은 실제 고객 수치와 DEMO 수치를 섞지 않는다.
- route ID를 바꾸지 않는다.
- agent profile을 하나만 만들고 이름만 바꾸는 식으로 복제하지 않는다.
- Runtime 공통 파일에 고객명을 hard-code하지 않는다.
