# Design System Reference

이 문서는 Golden Runtime 컴포넌트의 시각 참고 자료다. 실제 source of truth는
`runtime/runtime.css`이며, 고객별 결과는 `reference/adaptive-design-dna.md`와
`demo-spec.json`의 palette·theme·density·shape token으로 결정한다. 브랜드 색 하나만 바꾸는 고정
template 방식으로 사용하지 않는다.

## 1. 토큰 (`:root`)
```css
:root{
  --bg:#0a0e17; --bg2:#0d1320; --panel:#111827; --panel2:#0f1726;
  --ink:#eef2f9; --ink2:#9fb0c8; --ink3:#64748b;
  --brand:#e2231a; --brand2:#ff4b3e;        /* 예시 기본값; 고객 Design DNA가 role별 token을 override */
  --blue:#2b9bff; --blue2:#0a84ff; --cyan:#27e0d8;
  --green:#34e29b; --amber:#ffc24b; --violet:#9b7bff;
  --line:rgba(255,255,255,.08); --line2:rgba(255,255,255,.05);
  --ok:#34e29b; --warn:#ffc24b; --bad:#ff5f57;
  --font:'Pretendard',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Segoe UI',sans-serif;
  --mono:'SF Mono',ui-monospace,'JetBrains Mono',Menlo,monospace;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--font);overflow:hidden;font-size:14px}
::-webkit-scrollbar{width:9px;height:9px}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:6px}
.mono{font-family:var(--mono)} .muted{color:var(--ink3)} .sub{color:var(--ink2)}
```
폰트 CDN(`<head>`): `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css`

## 2. 레이아웃
```css
#app{display:grid;grid-template-columns:252px 1fr;height:100vh}
#sidebar{background:linear-gradient(180deg,#0c1220,#0a0e17);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:18px 14px}
#main{display:flex;flex-direction:column;overflow:hidden;min-width:0}
#topbar{height:62px;flex:none;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:16px;padding:0 24px;background:rgba(13,19,32,.7);backdrop-filter:blur(10px)}
#view{flex:1;overflow:auto;padding:22px 24px}
.view-anim{animation:fade .4s ease}@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
```

## 3. 사이드바 내비 + 브랜드
```css
.brand{display:flex;align-items:center;gap:11px;padding:8px 10px 18px}
.brand .sq{width:34px;height:34px;border-radius:9px;background:linear-gradient(150deg,var(--brand),var(--brand2));display:grid;place-items:center;font-weight:900;color:#fff;font-size:17px;box-shadow:0 4px 18px rgba(226,35,26,.45)}
.nav{display:flex;flex-direction:column;gap:2px}
.nav a{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:10px;color:var(--ink2);font-weight:600;font-size:13.5px;cursor:pointer;transition:.15s;position:relative}
.nav a .ic{width:20px;text-align:center;font-size:15px} .nav a .nm{flex:1} .nav a .sb{font-size:10px;color:var(--ink3)}
.nav a:hover{background:rgba(255,255,255,.04);color:var(--ink)}
.nav a.on{background:linear-gradient(100deg,rgba(43,155,255,.16),rgba(43,155,255,.04));color:#fff}
.nav a.on::before{content:"";position:absolute;left:-14px;top:8px;bottom:8px;width:3px;border-radius:0 3px 3px 0;background:var(--blue)}
.side-foot{margin-top:auto;padding:12px;border-top:1px solid var(--line);display:flex;align-items:center;gap:10px}
.side-foot .av{width:34px;height:34px;border-radius:50%;background:linear-gradient(150deg,#2b9bff,#9b7bff);display:grid;place-items:center;font-weight:800;font-size:13px}
```
> 사이드바 사용자는 **실명 금지** — 회사명/직무만(예: `SP · 삼표 임원`).

## 4. 토프바 요소
```css
.tb-spacer{flex:1}
.tb-item{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink2);font-weight:600;padding:7px 11px;border-radius:9px;border:1px solid var(--line);background:rgba(255,255,255,.02)}
.dot-live{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(52,226,155,.5)}70%{box-shadow:0 0 0 7px rgba(52,226,155,0)}100%{box-shadow:0 0 0 0 rgba(52,226,155,0)}}
.bell{position:relative;width:38px;height:38px;border-radius:9px;border:1px solid var(--line);display:grid;place-items:center;cursor:pointer;font-size:16px}
.bell .bdg{position:absolute;top:-5px;right:-5px;min-width:17px;height:17px;border-radius:9px;background:var(--brand);color:#fff;font-size:10px;font-weight:800;display:grid;place-items:center;padding:0 4px;border:2px solid var(--bg2)}
.demo-badge{font-size:10px;font-weight:800;letter-spacing:.08em;color:var(--amber);border:1px solid rgba(255,194,75,.4);background:rgba(255,194,75,.1);padding:5px 9px;border-radius:7px}
```
토프바에 항상: `● DEMO DATA` 배지 + 실시간 시계 + 인프라 배지(예: `Azure Korea Central · Foundry`).

## 5. 카드 · KPI · 그리드
```css
.grid{display:grid;gap:16px} .g4{grid-template-columns:repeat(4,1fr)} .g3{grid-template-columns:repeat(3,1fr)} .g2{grid-template-columns:1fr 1fr}
.panel{background:linear-gradient(160deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:16px;padding:18px 20px}
.panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.panel-head h3{font-size:15px;font-weight:700} .panel-head .hint{font-size:11.5px;color:var(--ink3)}
.kpi .kl{font-size:12.5px;color:var(--ink2);font-weight:600;display:flex;align-items:center;gap:7px}
.kpi .kv{font-size:32px;font-weight:800;letter-spacing:-.02em;margin-top:8px;line-height:1}
.kpi .kv small{font-size:15px;color:var(--ink2);font-weight:700}
.kpi .kd{font-size:12px;font-weight:700;margin-top:8px}
.kico{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;font-size:16px;background:rgba(43,155,255,.12);border:1px solid var(--line)}
.up{color:var(--green)} .down{color:var(--bad)}
.hero{padding:20px 22px;border-radius:16px;background:linear-gradient(120deg,rgba(226,35,26,.12),rgba(43,155,255,.08));border:1px solid var(--line);margin-bottom:16px;display:flex;align-items:center;gap:18px}
.hero .ht{font-size:18px;font-weight:800} .hero .hs{font-size:13px;color:var(--ink2);margin-top:4px;line-height:1.5}
```

## 6. 배지 · 칩 · 버튼 · 테이블
```css
.bdg{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:7px;font-size:11.5px;font-weight:700;border:1px solid transparent}
.bdg.ok{color:#bff5dd;background:rgba(52,226,155,.13);border-color:rgba(52,226,155,.3)}
.bdg.warn{color:#ffe6b0;background:rgba(255,194,75,.13);border-color:rgba(255,194,75,.3)}
.bdg.bad{color:#ffc4bf;background:rgba(255,95,87,.13);border-color:rgba(255,95,87,.35)}
.bdg.info{color:#bfe0ff;background:rgba(43,155,255,.13);border-color:rgba(43,155,255,.3)}
.bdg.vio{color:#ddd3ff;background:rgba(155,123,255,.13);border-color:rgba(155,123,255,.3)}
.btn{cursor:pointer;border:none;border-radius:10px;padding:10px 16px;font-family:var(--font);font-weight:700;font-size:13px;background:linear-gradient(120deg,var(--blue2),var(--blue));color:#fff;transition:.18s;display:inline-flex;align-items:center;gap:7px}
.btn:hover{filter:brightness(1.1);transform:translateY(-1px)}
.btn.red{background:linear-gradient(120deg,var(--brand),var(--brand2))} .btn.ghost{background:rgba(255,255,255,.04);border:1px solid var(--line);color:var(--ink2)} .btn.sm{padding:7px 12px;font-size:12px;border-radius:8px}
table.tbl{width:100%;border-collapse:collapse;font-size:13px}
table.tbl th{text-align:left;color:var(--ink3);font-weight:700;font-size:11.5px;padding:8px 10px;border-bottom:1px solid var(--line);text-transform:uppercase}
table.tbl td{padding:11px 10px;border-bottom:1px solid var(--line2)}
table.tbl tr:hover td{background:rgba(255,255,255,.02)}
.chip{padding:8px 13px;border-radius:9px;border:1px solid var(--line);background:rgba(255,255,255,.03);font-size:12.5px;font-weight:600;color:var(--ink2);cursor:pointer;transition:.15s}
.chip:hover{border-color:var(--cyan);color:#fff;background:rgba(39,224,216,.08)}
```

## 7. 피드 · 슬라이더 · 행(클릭형)
```css
.feed{display:flex;flex-direction:column;gap:2px;max-height:330px;overflow:auto}
.feed-item{display:flex;gap:11px;padding:10px 8px;border-radius:9px;animation:fadeIn .5s ease}
@keyframes fadeIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
.feed-item .fi{width:30px;height:30px;border-radius:8px;display:grid;place-items:center;font-size:14px;flex:none;background:rgba(255,255,255,.04);border:1px solid var(--line)}
.feed-item .ft{font-size:13px;font-weight:600;line-height:1.4} .feed-item .fm{font-size:11px;color:var(--ink3);margin-top:2px}
input[type=range]{-webkit-appearance:none;width:100%;height:6px;border-radius:6px;background:rgba(255,255,255,.1);outline:none}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:var(--cyan);cursor:pointer;box-shadow:0 0 10px rgba(39,224,216,.6);border:3px solid #08111f}
.slabel{display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:7px}
.agent-row{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:11px;border:1px solid var(--line);background:rgba(255,255,255,.02);cursor:pointer;transition:.15s;margin-bottom:8px}
.agent-row:hover{border-color:rgba(43,155,255,.4);background:rgba(43,155,255,.05)}
.agent-row.on{border-color:var(--cyan);background:rgba(39,224,216,.06)}
.agent-row .ai{width:38px;height:38px;border-radius:10px;display:grid;place-items:center;font-size:18px;flex:none;background:linear-gradient(150deg,rgba(43,155,255,.18),rgba(43,155,255,.04));border:1px solid var(--line)}
.agent-row .an{font-weight:700;font-size:13.5px} .agent-row .ad{font-size:11px;color:var(--ink3)}
```

## 8. 채팅
```css
.chat{display:flex;flex-direction:column;height:100%}
.chat-log{flex:1;overflow:auto;display:flex;flex-direction:column;gap:14px;padding:6px 4px}
.msg{display:flex;gap:11px;max-width:82%;animation:fadeIn .4s ease}
.msg .mav{width:30px;height:30px;border-radius:8px;flex:none;display:grid;place-items:center;font-size:14px}
.msg.bot .mav{background:linear-gradient(150deg,var(--blue2),var(--violet))}
.msg.me{margin-left:auto;flex-direction:row-reverse} .msg.me .mav{background:linear-gradient(150deg,#2b9bff,#27e0d8)}
.msg .mb{padding:12px 15px;border-radius:13px;font-size:13.5px;line-height:1.6}
.msg.bot .mb{background:var(--panel);border:1px solid var(--line);border-top-left-radius:4px}
.msg.me .mb{background:linear-gradient(120deg,rgba(43,155,255,.2),rgba(39,224,216,.12));border:1px solid rgba(43,155,255,.3);border-top-right-radius:4px}
.msg .mb .stat{display:flex;gap:16px;margin-top:10px;flex-wrap:wrap} .msg .mb .stat .s{font-size:11px;color:var(--ink3)} .msg .mb .stat .sv{font-size:18px;font-weight:800}
.typing .mb{display:flex;gap:4px;padding:14px 16px} .typing span{width:7px;height:7px;border-radius:50%;background:var(--ink3);animation:blink 1.2s infinite}
.typing span:nth-child(2){animation-delay:.2s} .typing span:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,60%,100%{opacity:.3}30%{opacity:1}}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 10px}
.composer{display:flex;gap:10px;padding-top:12px;border-top:1px solid var(--line)}
.composer input{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:13px 15px;color:var(--ink);font-family:var(--font);font-size:13.5px;outline:none}
.composer input:focus{border-color:var(--blue)}
```

## 9. 토스트 · 진행 스텝 · 막대 · 칸반 · 플로우
```css
.toasts{position:fixed;right:20px;bottom:20px;display:flex;flex-direction:column;gap:10px;z-index:100}
.toast{display:flex;align-items:center;gap:11px;padding:13px 16px;border-radius:12px;background:rgba(17,24,39,.96);border:1px solid var(--line);box-shadow:0 12px 40px rgba(0,0,0,.5);min-width:290px;animation:slideUp .4s ease}
@keyframes slideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.toast.out{animation:fadeOut .4s ease forwards}@keyframes fadeOut{to{opacity:0;transform:translateX(20px)}}
.toast .ti{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-size:15px}
.steps{display:flex;flex-direction:column;gap:9px}
.step{display:flex;gap:10px;align-items:flex-start;font-size:12.5px;opacity:0;transform:translateY(6px);transition:.4s}
.step.show{opacity:1;transform:none} .step .si{width:22px;height:22px;border-radius:6px;display:grid;place-items:center;font-size:12px;flex:none;background:rgba(52,226,155,.14);color:var(--green)}
.bars{display:flex;flex-direction:column;gap:11px} .bar{display:flex;align-items:center;gap:12px}
.bar .bn{width:130px;font-size:12.5px;font-weight:600;color:var(--ink2);flex:none}
.bar .bt{flex:1;height:13px;border-radius:7px;background:rgba(255,255,255,.07);overflow:hidden}
.bar .bf{height:100%;width:0;border-radius:7px;transition:width 1.1s cubic-bezier(.2,.8,.3,1)} .bar .bv{width:44px;text-align:right;font-weight:800;font-size:12.5px}
.kanban{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.kcol{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px} .kcol .kh{font-size:12px;font-weight:700;color:var(--ink2);margin-bottom:10px;display:flex;justify-content:space-between}
.kcard{background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:9px;padding:11px;margin-bottom:8px;font-size:12.5px}
.statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:14px}
.statgrid .st{padding:14px;border-radius:11px;background:var(--panel2);border:1px solid var(--line)} .statgrid .st .sl{font-size:11.5px;color:var(--ink3)} .statgrid .st .sv{font-size:24px;font-weight:800;margin-top:5px}
.flow{position:relative;height:300px}
.fnode{position:absolute;transform:translate(-50%,-50%);text-align:center;width:96px}
.fnode .fb{width:56px;height:56px;border-radius:14px;margin:0 auto 6px;display:grid;place-items:center;font-size:23px;background:linear-gradient(150deg,var(--panel),var(--panel2));border:1px solid var(--line);transition:.3s}
.fnode .fl{font-size:11px;font-weight:700;color:var(--ink2)} .fnode.core .fb{background:linear-gradient(150deg,var(--blue2),#0a3a78);border-color:var(--blue)}
.fnode.hot .fb{border-color:var(--cyan);box-shadow:0 0 22px rgba(39,224,216,.5);transform:scale(1.08)}
.map-wrap{position:relative;border-radius:14px;overflow:hidden;background:radial-gradient(900px 500px at 60% 30%,rgba(43,155,255,.06),transparent),#0a1120;border:1px solid var(--line)}
.code{font-family:var(--mono);font-size:12px;line-height:1.7;white-space:pre-wrap;overflow:auto}
.code .add{color:var(--green)} .code .del{color:#ff7b72;opacity:.75} .code .cm{color:var(--ink3)} .code .kw{color:var(--violet)}
.section-t{font-size:12px;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:4px 0 12px}
```

## 컬러 사용 규칙
- `--brand`: 로고·주요 강조 역할. 고객별 변경은 brand뿐 아니라 canvas·surface·ink·accent·semantic role을 함께 설계한다.
- `--blue`: 주요 액션·링크·차트 기본. `--cyan`: 라이브/하이라이트. `--green/amber/bad`: 상태(정상/주의/위험).
- 상태 매핑 일관: ok=green, warn=amber, bad=red, info=blue, AI/governance=violet.
