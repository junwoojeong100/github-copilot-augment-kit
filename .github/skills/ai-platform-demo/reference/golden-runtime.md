# Golden Runtime Contract

Golden Runtime은 고객 데모의 **동작 엔진**이다. 특정 고객의 색상이나 콘텐츠를 고정하는 템플릿이
아니며, 검증된 SPA lifecycle·interaction·rendering·QA hook을 재사용해 고객별 HTML 조립 시간을
줄이는 기반이다.

## 1. 고정하는 것

다음 항목은 고객·산업과 무관한 runtime contract다.

- 단일 HTML shell, 8-route hash router, sidebar/topbar, `DEMO DATA` 표시
- route 전환 시 timer/listener cleanup
- KPI tick, streaming chart, activity feed, toast, moving-object engine
- slider simulator, root-cause animation, finance what-if, Issue-to-PR flow
- 모든 agent 행 전환, 추천 질문, 자유 질문 fallback, orchestration sequence
- governance evaluation trace와 clickable detail rows
- SVG chart primitives, HTML escaping, DOM null guard
- 안정적인 DOM ID와 Puppeteer QA contract

Runtime 파일:

```text
runtime/
  shell.tmpl
  runtime.css
  runtime.js
```

이 파일들은 고객별 작업 폴더로 복사하지 않고 skill 자산에서 읽어 최종 HTML에 inline한다.

## 2. 고정하지 않는 것

다음 항목은 반드시 `demo-spec.json`과 Design DNA에서 고객별로 결정한다.

- 브랜드명, 앱명, 언어, audience, storyline
- dark/light canvas, palette, typography scale, radius, shadow, spacing, density
- hero 표현, chart grammar, visual metaphor, motion intensity
- route 이름과 domain terminology
- KPI label·단위·범위·tick behavior
- 운영 flow node, simulator input·formula, root-cause factor
- finance lever·가정, GitHub issue·diff
- agent profile·질문·답변·orchestration
- governance control·memory asset

**원칙:** engine은 고정하지만 skin·composition·narrative는 고정하지 않는다.

## 3. Runtime / Spec 경계

| Layer | 소유자 | 변경 빈도 | 예시 |
|---|---|---:|---|
| Golden Runtime | skill | 낮음 | router, cleanup, chart primitive, interaction engine |
| Design archetype | skill + request | 중간 | precision-control-room, trusted-executive |
| Design DNA | 고객별 spec | 매 요청 | palette, density, radius, chart style |
| Domain content | 고객별 spec | 매 요청 | KPI, flow, formula, agent QA |
| Bespoke extension | 생성 agent | 예외 | 산업 특화 map, uncommon visual simulator |

## 4. 기본 생성 경로

```bash
python3 -B .github/skills/ai-platform-demo/scripts/render_demo.py \
  --spec <session>/files/<app>-work/demo-spec.json \
  --output <session>/files/<app>-work/<app>.html
```

Renderer는 다음을 수행한다.

1. spec 필수 구조와 8개 route data를 검증한다.
2. `runtime.css`, `runtime.js`, 고객 spec을 `shell.tmpl`에 inline한다.
3. Rich text를 strict tag/class allowlist로 sanitize하고 event handler·SVG·URL·style을 거부한다.
4. `</script>`, U+2028/U+2029를 안전하게 escape하고 non-finite number를 거부한다.
5. 외부 JavaScript·chart dependency가 없는 단일 HTML을 생성한다.
6. output byte size와 route/agent 개수를 출력한다.

## 5. Runtime QA contract

다음 ID는 변경하지 않는다.

| Route | Required IDs |
|---|---|
| dashboard | `dashChart`, `dashFeed`, `dashTable` |
| operations | `opsFlow`, `flowMover`, `reopt`, `opsTable` |
| simulator | `simInputs`, `simGauge`, `simValue`, `simHistogram` |
| improvement | `runAnalysis`, `analysisSteps`, `factorBars`, `improvementBoard` |
| finance | `financeLevers`, `marginValue`, `valueDonut`, `financeTable` |
| devops | `assignIssue`, `devSteps`, `codeDiff`, `issueTable`, `prStatus` |
| agents | `agentList`, `chatTitle`, `chatLog`, `chips`, `chatInput`, `sendBtn`, `orchRun` |
| governance | `evalRun`, `evalScore`, `evalTrace`, `controlTable`, `memoryTable` |

QA는 추가로 확인한다.

- `DEMO DATA` badge
- `NaN`, `undefined`, `null%` 없음
- horizontal overflow 없음
- 모든 `.click-row`와 `.agent-row`에 click handler 존재
- 모든 agent title이 서로 다름
- 빠른 route 전환 후 console/page error 0

## 6. Bespoke extension 규칙

Golden Runtime이 고객의 핵심 장면을 충분히 표현하지 못할 때만 extension을 사용한다.

1. 먼저 spec의 `visual.variant`, Design DNA, route data로 해결한다.
2. 그래도 부족하면 생성된 HTML의 해당 `VIEWS.<route>`만 session 작업 폴더에서 patch한다.
3. runtime 공통 파일에 고객 전용 분기를 추가하지 않는다.
4. extension 후 targeted QA와 final full QA를 모두 수행한다.

이 방식으로 재사용성 때문에 고객별 차별성이 희생되는 것을 막는다.
