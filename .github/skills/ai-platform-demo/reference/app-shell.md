# App Shell · Router · Realtime (산업 중립 뼈대)

단일 HTML의 구조와 핵심 JS. **이 골격은 고객이 바뀌어도 거의 그대로** 쓰고, `ROUTES`와 `VIEWS`의
내용만 산업에 맞게 채운다.

## 1. HTML 골격 (`<body>`)
```html
<div id="app">
  <aside id="sidebar">
    <div class="brand"><div class="sq">{{INITIAL}}</div>
      <div><div class="bn">{{APP_NAME}}</div><div class="bs">{{CUSTOMER}} AI 운영 플랫폼</div></div></div>
    <div class="navsec">운영 인텔리전스</div>
    <nav class="nav" id="nav"></nav>
    <!-- 선택: 'Learning Loop' 위젯(쓸수록 커지는 고객 소유 AI 자산 카운터) -->
    <div class="side-foot"><div class="av">{{INITIAL}}</div>
      <div><div class="un">{{CUSTOMER}} 임원</div><div class="ur">{{CUSTOMER}} · 관리자</div></div></div>
  </aside>
  <div id="main">
    <header id="topbar">
      <div><div class="ttl" id="tbTitle">대시보드</div><div class="crumb" id="tbCrumb"></div></div>
      <div class="tb-spacer"></div>
      <span class="demo-badge">● DEMO DATA</span>
      <div class="tb-item"><span class="dot-live"></span> Azure Korea Central · Foundry</div>
      <div class="tb-item mono" id="clock">--:--:--</div>
      <div class="bell" id="bell">🔔<span class="bdg" id="bellBdg">3</span></div>
    </header>
    <div id="view"></div>
  </div>
</div>
<div class="toasts" id="toasts"></div>
```
> 실명 금지. 사용자 표기는 `{{CUSTOMER}} 임원` 같은 직무/회사명.

## 2. 라우트 정의 + 사이드바 렌더
```js
const ROUTES=[
  {id:'dashboard', ic:'📊', nm:'대시보드',  sb:'Overview',    crumb:'Overview'},
  {id:'ops',       ic:'🚚', nm:'{{DOMAIN1}}', sb:'{{D1}} IQ', crumb:'{{D1}} IQ'},
  {id:'predict',   ic:'🧪', nm:'{{DOMAIN2}}', sb:'{{D2}} IQ', crumb:'{{D2}} IQ'},
  {id:'improve',   ic:'⚙️', nm:'{{DOMAIN3}}', sb:'{{D3}} IQ', crumb:'{{D3}} IQ'},
  {id:'finance',   ic:'💰', nm:'재무 인사이트', sb:'Finance IQ', crumb:'Finance IQ'},
  {id:'devops',    ic:'🐙', nm:'개발 가속',   sb:'GitHub Copilot', crumb:'GitHub Copilot'},
  {id:'agents',    ic:'🧭', nm:'AI 에이전트', sb:'Agent Studio',   crumb:'Agent Studio'},
  {id:'governance',ic:'🛡️', nm:'거버넌스',    sb:'Trust',          crumb:'Trust & Sovereignty'},
];
const navEl=document.getElementById('nav');
navEl.innerHTML=ROUTES.map(r=>`<a data-id="${r.id}"><span class="ic">${r.ic}</span><span class="nm">${r.nm}</span><span class="sb">${r.sb}</span></a>`).join('');
navEl.querySelectorAll('a').forEach(a=>a.onclick=()=>location.hash=a.dataset.id);
```

## 3. 헬퍼 + 타이머/클린업 레지스트리 (★ 누수·null 방지의 핵심)
```js
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const rnd=(a,b)=>a+Math.random()*(b-a);
const fmt=n=>n.toLocaleString('ko-KR');
let viewTimers=[], viewCleanups=[];
function addTimer(t){viewTimers.push(t);return t}            // setInterval/Timeout 전부 등록
function addCleanup(fn){viewCleanups.push(fn)}               // addEventListener 해제 등록
function clearViewTimers(){viewTimers.forEach(clearInterval);viewTimers=[];viewCleanups.forEach(fn=>{try{fn()}catch(e){}});viewCleanups=[]}
```
규칙: **뷰 안의 모든 `setInterval`/자동 `setTimeout`은 `addTimer(...)`로 감싸고**, 모든 `addEventListener`는
`addCleanup(()=>removeEventListener(...))`로 등록한다. 라우트 전환 시 자동 정리된다.

## 4. 라우터
```js
const VIEWS={};
function navigate(){
  const id=(location.hash.slice(1))||'dashboard';
  const r=ROUTES.find(x=>x.id===id)||ROUTES[0];
  clearViewTimers();
  $$('#nav a').forEach(a=>a.classList.toggle('on',a.dataset.id===r.id));
  $('#tbTitle').textContent=r.nm; $('#tbCrumb').textContent='{{APP_NAME}} · '+r.crumb;
  const v=document.getElementById('view');
  const def=(VIEWS[r.id]||VIEWS.dashboard)();
  v.innerHTML=`<div class="view-anim">${def.html}</div>`;
  if(def.init)def.init();
  v.scrollTop=0;
}
addEventListener('hashchange',navigate);
```

## 5. 전역 틱 (앱 전체 — 정리하지 않음)
```js
setInterval(()=>{$('#clock').textContent=new Date().toLocaleTimeString('ko-KR',{hour12:false})},1000);
const toastData=[ /* {i:'🚚',c:'#2b9bff',t:'제목',s:'부제'} … 산업 이벤트 6개 */ ];
function toast(d){const el=document.createElement('div');el.className='toast';
  el.innerHTML=`<div class="ti" style="background:${d.c}22;color:${d.c}">${d.i}</div><div><div class="tt">${d.t}</div><div class="ts">${d.s}</div></div>`;
  $('#toasts').appendChild(el); setTimeout(()=>{el.classList.add('out');setTimeout(()=>el.remove(),400)},4200);}
setInterval(()=>toast(toastData[Math.floor(rnd(0,toastData.length))]), 9000);
setTimeout(()=>toast(toastData[0]),2500);
$('#bell').onclick=()=>{$('#bellBdg').style.display='none';toast({i:'🔔',c:'#2b9bff',t:'알림',s:'…'});};
```

## 6. 차트 유틸 (순수 SVG — 외부 라이브러리 금지)
```js
// 스파크라인(KPI 카드 우하단)
function sparkline(values,w=90,h=42,color='#34e29b'){
  const mn=Math.min(...values),mx=Math.max(...values),rng=(mx-mn)||1;
  const pts=values.map((v,i)=>[i/(values.length-1)*w, h-4-((v-mn)/rng)*(h-8)]);
  const d=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:100%">
    <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${color}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
    <path d="${d} L${w},${h} L0,${h} Z" fill="url(#sg)" opacity=".25"/><path d="${d}" fill="none" stroke="${color}" stroke-width="2"/></svg>`;
}
// 카운트업/트윈 — KPI 애니메이션
function countUp(el){const to=parseFloat(el.dataset.count),pre=el.dataset.pre||'',suf=el.dataset.suf||'',dec=(to%1?1:0),t0=performance.now();
  (function f(t){let p=Math.min(1,(t-t0)/1100);p=1-Math.pow(1-p,3);el.textContent=pre+(to*p).toFixed(dec)+suf;if(p<1)requestAnimationFrame(f)})(t0);}
```
- **스트리밍 라인차트**: 데이터 배열을 `addTimer(setInterval(... data.push(); data.shift(); redraw() ,1800))`로 흘린다. 마지막 점에 `<animate>` 펄스.
- **게이지(반원)**: `M30,110 A80,80 0 0,1 …` 아크 + 색상(ok/warn/bad). 슬라이더 oninput으로 갱신.
- **도넛**: `<circle stroke-dasharray>` 누적 오프셋. **막대**: `.bf{width:0;transition}` → 실행 시 `width=%`.

## 7. VIEW 패턴 (각 화면)
```js
VIEWS.dashboard=()=>({
  html:`…`,                       // 템플릿 문자열(컴포넌트 조립)
  init(){
    // 데이터/이벤트 바인딩. 모든 타이머는 addTimer(...), 리스너는 addCleanup(...)
    addTimer(setInterval(()=>{/* KPI 미세 변동 */},2000));
    // 차트/피드/맵 …
  }
});
```

## 8. 부팅
```js
function fit(){} // (앱은 100vh grid라 별도 스케일 불필요)
navigate();      // 초기 라우트 렌더
```

## 정리 — 반드시 지킬 4가지
1. 뷰 타이머는 `addTimer`, 리스너는 `addCleanup`.
2. 비동기 콜백/체인에서 DOM 접근 전 `const el=$('#x'); if(!el)return;`.
3. 외부 차트 라이브러리 금지(SVG 직접).
4. 클릭 가능한 목록 행에는 반드시 `onclick` 바인딩(렌더 직후 `$$().forEach`).
