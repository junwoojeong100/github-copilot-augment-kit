# Fixed Microsoft-tone Design System

이 데모의 디자인은 **Microsoft(Fluent) 톤으로 고정**되어 있다. 고객·산업이 바뀌어도 색·레이아웃·
타이포·모션은 바꾸지 않는다. 고객별로는 **메뉴(라우트/도메인명)와 데이터만** 바뀐다.

과거의 "고객별 Adaptive Design DNA(archetype·palette·theme 도출)"는 제거되었다. 매 요청 디자인을
새로 설계하지 않으므로 생성이 빠르다.

## 1. 단일 원천 (source of truth)

- 시각 토큰의 원천은 `runtime/runtime.css`의 `:root` 하나다.
- Renderer는 `runtime.css`를 그대로 inline하며, JavaScript는 색 토큰을 override하지 않는다.
- `demo-spec.json`의 `design` 블록은 **base spec이 고정 제공**하며, 고객 Overlay는 이를 정의하지 않는다.

## 2. 고정 팔레트 (Microsoft / Fluent light)

| 역할 | 토큰 | 값 |
|---|---|---|
| 배경 | `--canvas` / `--canvas-alt` | `#f3f6fb` / `#fbfcfe` |
| 표면(카드) | `--surface` / `--surface-alt` / `--surface-strong` | `#ffffff` / `#f4f7fc` / `#eaeef6` |
| 텍스트 | `--ink` / `--ink-muted` / `--ink-faint` | `#1a1f2b` / `#4a5464` / `#79828f` |
| 브랜드 | `--brand` / `--brand-alt` | `#0f6cbd` / `#2b88d8` (Fluent 2 brand blue) |
| 강조 | `--accent` | `#0e7490` (refined teal) |
| 상태 | `--info` / `--success` / `--warning` / `--danger` | `#0f6cbd` / `#0e7a3d` / `#b26a00` / `#c43d4b` |
| AI/거버넌스 | `--violet` | `#8764b8` |
| 선/그림자 | `--line` / `--line-soft` / `--shadow` | `rgba(22,32,52,.10)` / `rgba(22,32,52,.055)` / `0 6px 20px rgba(16,24,40,.10)` |
| 형태 | `--radius` / `--nav-width` / `--font-scale` | `12px` / `264px` / `1` |
| 폰트 | `--font` / `--mono` (본문 15.5px, 컴포넌트 상향·최소 10.5px) | Pretendard / SFMono |

상태 색 매핑: ok=success(green), warn=warning(amber), bad=danger(red), info=info(blue), AI/governance=violet.

## 3. 바꾸지 않는다

- 팔레트·radius·폰트·간격·모션은 고객·산업별로 바꾸지 않는다.
- 색을 바꿔야 하면 `runtime/runtime.css`의 `:root`만 수정한다(전 고객 공통으로 반영됨).
- 고객 Overlay(`customer-overlay.json`)에 `design`을 넣으면 Composer가 실패한다.
- 로고 색을 전체 배경으로 확장하지 않는다. 브랜드 색은 강조 역할로만 쓴다.

## 4. 정직성·자산

- `● DEMO DATA` 배지는 모든 화면에 유지한다.
- text contrast는 고정 라이트 배경에서 읽히도록 이미 설계되어 있다(토큰 기반 `color-mix`).
- 고객 로고를 임의 생성하거나 비공식 asset을 포함하지 않는다.
