# Adaptive Design DNA

Adaptive Design DNA는 Golden Runtime 위에 적용되는 고객별 시각 계약이다. 브랜드 색 하나만 바꾸는
theme이 아니라, 고객·산업·청중·목적의 물성을 UI token과 composition으로 번역한다.

Industry Pack은 Design DNA를 정의할 수 없다. Pack의 `designHints`는 참고 정보일 뿐이며, 최종
`design` section은 실시간 조사 결과를 반영한 Customer Overlay가 매 요청 새로 제공한다.

## 1. 반드시 결정할 항목

`demo-spec.json`의 `design`에 다음을 기록한다.

1. `conceptWords` — 고객 인상을 설명하는 3개 단어
2. `visualMetaphor` — control room, signal network, operating map 등 1개
3. `archetype` — 기본 archetype
4. `counterInfluence` — 획일화를 피하기 위한 보조 영향
5. `theme` — `dark` 또는 `light`
6. palette roles — canvas, surface, ink, muted, brand, secondary, accent, semantic colors
7. typography — scale, weight, mono usage
8. shape language — radius, border strength, shadow, line style
9. density — `compact`, `executive`, `spacious`
10. chart grammar — line weight, fill opacity, grid visibility, highlight behavior
11. motion — `restrained`, `balanced`, `energetic`
12. `avoid` — 이번 고객에게 사용하지 않을 패턴 3개

## 2. Archetype

Runtime은 다음 archetype을 제공한다. Archetype은 시작점이며 spec token이 항상 우선한다.

| Archetype | 적합한 상황 | 기본 인상 |
|---|---|---|
| `precision-control-room` | 제조·반도체·물류·에너지 | 정밀, 실시간, 기술적 |
| `trusted-executive` | 금융·공공·규제 산업 | 신뢰, 절제, 통제 |
| `operational-canvas` | 유통·서비스·현장 운영 | 명료, 활동적, 접근성 |
| `premium-minimal` | 전략·투자·브랜드 중심 | 여백, 집중, 고급감 |

`counterInfluence` 예:

- precision-control-room + editorial clarity
- trusted-executive + live operations
- operational-canvas + premium restraint
- premium-minimal + technical evidence

## 3. Token contract

```json
{
  "design": {
    "conceptWords": ["precision", "confidence", "learning"],
    "visualMetaphor": "closed-loop signal network",
    "archetype": "precision-control-room",
    "counterInfluence": "editorial clarity",
    "theme": "dark",
    "density": "executive",
    "motion": "balanced",
    "tokens": {
      "canvas": "#08100e",
      "canvasAlt": "#0b1512",
      "surface": "#101c18",
      "surfaceAlt": "#0d1815",
      "ink": "#f1f7f3",
      "inkMuted": "#a7bbb0",
      "inkFaint": "#6f877a",
      "brand": "#73bc5a",
      "brandAlt": "#a6d65f",
      "accent": "#35d4c7",
      "info": "#40a9ff",
      "success": "#54db8f",
      "warning": "#ffc85a",
      "danger": "#ff6b63",
      "violet": "#a78bfa",
      "radius": 16,
      "navWidth": 254,
      "fontScale": 1
    },
    "avoid": ["generic red-blue gradient", "oversized glass cards", "decorative 3D icons"]
  }
}
```

## 4. Design DNA 도출 절차

1. 공식 고객 사이트·IR·제품 UI에서 반복되는 색, 대비, 형태, 이미지 톤을 관찰한다.
2. 로고 색을 전체 배경으로 확장하지 말고 `brand`/highlight 역할로 제한한다.
3. 산업의 물성을 선택한다.
   - 정밀 제조: 얇은 grid, mono metric, restrained motion
   - 금융: 높은 대비, 넓은 여백, 명시적 control states
   - 유통: 밝은 hierarchy, 빠른 status scan, 지도/흐름
4. audience density를 결정한다.
   - CEO/board: executive
   - operator: compact
   - external showcase: spacious
5. storyline의 climax가 가장 강하게 보이도록 accent와 motion budget을 배분한다.
6. `avoid`를 적어 기존 demo와 시각적으로 같은 결과가 나오는 것을 방지한다.

## 5. 품질 가드

- brand 색 하나를 모든 card와 chart에 반복하지 않는다.
- semantic status color는 brand와 분리한다.
- text contrast는 dark/light theme 모두에서 읽을 수 있어야 한다.
- animation은 의미 있는 state 변화에만 사용한다.
- density가 달라도 최소 body text와 click target은 유지한다.
- 고객 로고를 임의 생성하거나 비공식 asset을 포함하지 않는다.

## 6. 속도 최적화 원칙

Design DNA는 CSS를 다시 작성하는 작업이 아니다. Agent는 12개 결정을 spec으로 확정하고 Runtime이
token과 archetype을 적용한다. 고객별 고유성은 유지하면서 build 단계의 반복 CSS 작성은 제거한다.
