# Design System Reference (Fixed GitHub Soft-Dark)

이 데모의 시각 시스템은 **GitHub Primer `dark-dimmed` 계열 soft-dark 톤으로 고정**되어 있고,
실제 source of truth는 `runtime/runtime.css` 하나다. 고객·산업이 바뀌어도 색·타이포·간격·모션은
바꾸지 않는다(고객별로는 메뉴와 데이터만 바뀐다). 색을 바꿔야 하면 `runtime.css`의 `:root`만 수정한다.
Renderer는 `--canvas`를 읽어 HTML의 `theme-color`도 같은 값으로 자동 생성한다.

## 1. 고정 토큰 (`runtime.css`의 `:root`)
```css
:root{
  --canvas:#212830; --canvas-alt:#151b23;
  --surface:#262c36; --surface-alt:#2a313c; --surface-strong:#2f3742;
  --ink:#d1d7e0; --ink-muted:#b7bdc8; --ink-faint:#aab2bd; --on-emphasis:#f0f6fc;
  --brand:#539bf5; --brand-alt:#478be6; --brand-emphasis:#316dca; --brand-strong:#255ab2;
  --accent:#e0823d;
  --info:#6cb6ff; --success:#6bc46d; --warning:#daaa3f; --danger:#ff938a;
  --violet:#dcbdfb; --violet-emphasis:#8256d0; --violet-strong:#6b44bc;
  --line:#3d444d; --line-soft:rgba(61,68,77,.7);
  --radius:12px; --nav-width:276px; --font-scale:1; --gap:16px; --panel-pad:20px;
  --shadow:0 16px 40px rgba(0,0,0,.28);
  --font:'Pretendard',-apple-system,'Segoe UI',sans-serif;
  --mono:'SFMono-Regular',Consolas,Menlo,monospace;
}
```
본문 기본 크기는 `body{font-size:calc(16.2px * var(--font-scale))}`이며, 핵심 제목·KPI·표·내비게이션 글자 크기는 임원 시연 가독성을 위해 상향돼 있다.
폰트 CDN(`<head>`): Pretendard(한글) + 시스템 폰트 폴백.

Spec의 `design`은 고정 marker(`trusted-executive` / `dark-dimmed` / `executive` / `balanced`,
`tokens={}`)일 뿐 CSS를 override하지 않는다.

상태 색 매핑: ok=success(green), warn=warning(amber), bad=danger(red), info=info(blue), AI/거버넌스=violet.

## 2. 컴포넌트 클래스 (구조 — `runtime.css` 정의)

- 레이아웃: `#app`(grid), `#sidebar`, `#topbar`, `#view` · 진입 애니메이션 `.view-enter`
- 내비: `.brand`, `.nav a(.active)`, `.learning-card`, `.side-user`
- 카드/KPI: `.panel`, `.grid(-2/-3/-4)`, `.kpi`(`.kpi-value`/`.kpi-delta`), `.sparkline`, `.hero`
- 배지·버튼·표: `.badge(.ok/.warn/.bad/.info/.violet)`, `.button(.ghost/.info/.violet/.small)`, `.data-table`, `.click-row`
- 차트·피드·슬라이더: `.chart-box`, `.feed`(`.feed-item`), `input[type=range]`, `.agent-row(.active)`
- 채팅·토스트·기타: `.chat-panel`/`.message(.assistant/.user)`, `.toasts`/`.toast`, `.steps`/`.step`, `.bars`/`.bar`, `.board`/`.board-column`, `.orchestration-flow`/`.flow-node`, `.code`

> 모든 컴포넌트는 위 토큰(`var(--...)`)과 `color-mix`로 색을 파생하므로, `:root`만 바꾸면 전체가
> 일관되게 바뀐다. 실명 금지 — 사용자 표기는 `SP · 삼표 임원`처럼 회사명/직무만 쓴다.
