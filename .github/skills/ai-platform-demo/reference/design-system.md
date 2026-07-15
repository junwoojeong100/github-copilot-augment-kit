# Design System Reference (Fixed Microsoft-tone)

이 데모의 시각 시스템은 **Microsoft(Fluent) 톤으로 고정**되어 있고, 실제 source of truth는
`runtime/runtime.css` 하나다. 고객·산업이 바뀌어도 색·타이포·간격·모션은 바꾸지 않는다(고객별로는
메뉴와 데이터만 바뀐다). 색을 바꿔야 하면 `runtime.css`의 `:root`만 수정한다.

## 1. 고정 토큰 (`runtime.css`의 `:root`)
```css
:root{
  --canvas:#f3f2f1; --canvas-alt:#faf9f8;
  --surface:#ffffff; --surface-alt:#f8f7f6; --surface-strong:#edebe9;
  --ink:#201f1e; --ink-muted:#484644; --ink-faint:#797775;
  --brand:#0078d4; --brand-alt:#2b88d8;      /* Microsoft blue */
  --accent:#038387;                           /* Fluent teal */
  --info:#0078d4; --success:#107c10; --warning:#c77700; --danger:#d13438; --violet:#8661c5;
  --line:rgba(0,0,0,.10); --line-soft:rgba(0,0,0,.06);
  --radius:12px; --nav-width:254px; --font-scale:1; --gap:15px; --panel-pad:18px;
  --shadow:0 8px 24px rgba(0,0,0,.09);
  --font:'Pretendard',-apple-system,'Segoe UI',sans-serif;
  --mono:'SFMono-Regular',Consolas,Menlo,monospace;
}
```
폰트 CDN(`<head>`): Pretendard(한글) + 시스템 폰트 폴백.

상태 색 매핑: ok=success(green), warn=warning(amber), bad=danger(red), info=info(blue), AI/거버넌스=violet.

## 2. 컴포넌트 클래스 (구조 — `runtime.css` 정의)

- 레이아웃: `#app`(grid), `#sidebar`, `#topbar`, `#view` · 진입 애니메이션 `.view-enter`
- 내비: `.brand`, `.nav a(.active)`, `.learning-card`, `.side-user`
- 카드/KPI: `.panel`, `.grid(-2/-3/-4)`, `.kpi`(`.kpi-value`/`.kpi-delta`), `.sparkline`, `.hero`
- 배지·버튼·표: `.badge(.ok/.warn/.bad/.info/.violet)`, `.button(.ghost/.info/.violet/.small)`, `.data-table`, `.click-row`
- 차트·피드·슬라이더: `.chart-box`, `.feed`(`.feed-item`), `input[type=range]`, `.agent-row(.on)`
- 채팅·토스트·기타: `.chat`/`.msg(.bot/.me)`, `.toasts`/`.toast`, `.steps`/`.step`, `.bars`/`.bar`, `.kanban`/`.kcol`, `.flow`/`.fnode`, `.code`

> 모든 컴포넌트는 위 토큰(`var(--...)`)과 `color-mix`로 색을 파생하므로, `:root`만 바꾸면 전체가
> 일관되게 바뀐다. 실명 금지 — 사용자 표기는 `SP · 삼표 임원`처럼 회사명/직무만 쓴다.
