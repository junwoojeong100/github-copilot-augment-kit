# Fixed GitHub Soft-Dark Design System

이 데모의 디자인은 **GitHub Primer `dark-dimmed` 계열의 soft-dark 톤으로 고정**되어 있다.
고객·산업이 바뀌어도 색·레이아웃·타이포·모션은 바꾸지 않는다. 고객별로는
**메뉴(라우트/도메인명)와 데이터만** 바뀐다.

과거의 "고객별 Adaptive Design DNA(archetype·palette·theme 도출)"는 제거되었다. 매 요청 디자인을
새로 설계하지 않으므로 생성이 빠르다.

## 1. 단일 원천 (source of truth)

- 시각 토큰의 원천은 `runtime/runtime.css`의 `:root` 하나다.
- Renderer는 `runtime.css`를 그대로 inline하며, JavaScript는 색 토큰을 override하지 않는다.
- `demo-spec.json`의 `design` 블록은 **base spec이 고정 marker**로 제공한다. `tokens`는 빈 객체이며 고객 Overlay는 `design`을 정의하지 않는다.

## 2. 고정 팔레트 (GitHub Primer Dark Dimmed inspired)

| 역할 | 토큰 | 값 |
|---|---|---|
| 배경 | `--canvas` / `--canvas-alt` | `#212830` / `#151b23` |
| 표면(카드) | `--surface` / `--surface-alt` / `--surface-strong` | `#262c36` / `#2a313c` / `#2f3742` |
| 텍스트 | `--ink` / `--ink-muted` / `--ink-faint` / `--on-emphasis` | `#d1d7e0` / `#b7bdc8` / `#aab2bd` / `#f0f6fc` |
| 인터랙션 | `--brand` / `--brand-alt` / `--brand-emphasis` | `#539bf5` / `#478be6` / `#316dca` |
| 강조 | `--accent` | `#e0823d` |
| 상태 | `--info` / `--success` / `--warning` / `--danger` | `#6cb6ff` / `#6bc46d` / `#daaa3f` / `#ff938a` |
| AI/거버넌스 | `--violet` / `--violet-emphasis` | `#dcbdfb` / `#8256d0` |
| 선/그림자 | `--line` / `--line-soft` / `--shadow` | `#3d444d` / `rgba(61,68,77,.7)` / `0 16px 40px rgba(0,0,0,.28)` |
| 형태 | `--radius` / `--nav-width` / `--font-scale` | `12px` / `276px` / `1` |
| 폰트 | `--font` / `--mono` (본문 16.2px, 핵심 컴포넌트 상향) | Pretendard / SFMono |

기준 출처는 GitHub의 공식 [Primer `dark-dimmed` theme 구성](https://github.com/primer/primitives/blob/main/scripts/themes.config.ts)과
[Dark Dimmed color primitives](https://github.com/primer/primitives/blob/main/src/tokens/base/color/dark/dark.dimmed.json5)다.
상태 텍스트는 작은 배지에서도 읽히도록 동일 scale 안에서 대비가 높은 단계를 사용하고,
`--ink-faint`는 tinted surface에서도 4.5:1 이상을 유지하도록 neutral scale 사이에서 보간한 값이다.

상태 색 매핑: ok=success(green), warn=warning(amber), bad=danger(red), info=info(blue), AI/governance=violet.

## 3. 바꾸지 않는다

- 팔레트·radius·폰트·간격·모션은 고객·산업별로 바꾸지 않는다.
- 색을 바꿔야 하면 `runtime/runtime.css`의 `:root`만 수정한다(전 고객 공통으로 반영됨).
- 고객 Overlay(`customer-overlay.json`)에 `design`을 넣으면 Composer가 실패한다.
- 고객 브랜드 색을 전체 배경으로 확장하지 않는다. 브랜드 색은 강조 역할로만 쓴다.

## 4. 정직성·자산

- `● DEMO DATA` 배지는 모든 화면에 유지한다.
- text contrast는 soft-dark neutral 표면에서 밝은 ink로 읽히도록 설계되어 있다(토큰 기반 `color-mix`).
- 고객 로고를 임의 생성하거나 비공식 asset을 포함하지 않는다.
