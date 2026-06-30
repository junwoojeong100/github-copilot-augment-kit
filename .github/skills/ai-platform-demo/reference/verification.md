# Verification (puppeteer 자동 검증)

데모는 **반드시 자동 검증**한다. macOS에 Chrome이 없을 수 있으므로 puppeteer(자체 Chromium)를 임시 설치하고,
끝나면 부산물을 정리한다.

## 0. 전제 — 해시 라우팅 + `hashchange`
앱은 `location.hash`로 라우팅하고 `addEventListener('hashchange',navigate)`가 있어야 한다.
그래야 검증 스크립트가 `location.hash=route`로 각 화면을 띄울 수 있다.

## 1. 설치 (임시)
```bash
cd <repo> && npm install puppeteer   # 자체 Chromium 다운로드 (≈1~2분)
```

## 2. 검증 스크립트 (`verify.js`)
```js
const puppeteer=require('puppeteer'), path=require('path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const routes=['dashboard','ops','predict','improve','finance','devops','agents','governance']; // 실제 ROUTES와 일치
(async()=>{
  const file='file://'+path.resolve('<APP>.html');
  const b=await puppeteer.launch({args:['--no-sandbox']});
  const page=await b.newPage();
  const errors=[];
  page.on('console',m=>{if(m.type()==='error')errors.push('CONSOLE: '+m.text())});
  page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message));
  await page.setViewport({width:1440,height:900});
  await page.goto(file,{waitUntil:'networkidle0'});

  // (1) 각 화면 스크린샷 + 데모 버튼 클릭
  for(const r of routes){
    await page.evaluate(rt=>location.hash=rt, r); await sleep(800);
    await page.evaluate(()=>['reopt','orchRun','assign','runSix','run'].forEach(id=>{const x=document.getElementById(id);if(x)x.click()}));
    await sleep(300);
    await page.screenshot({path:'shots/'+r+'.png'});
  }
  // (2) 빠른 전환 스트레스 테스트 (null 접근·리스너 누수 적발)
  for(let k=0;k<4;k++)for(const r of routes){await page.evaluate(rt=>location.hash=rt,r);await sleep(90)}
  await sleep(1200);
  // (3) 에이전트 전환 + 자유질문
  await page.evaluate(()=>location.hash='agents'); await sleep(700);
  const agentSwitch=await page.evaluate(()=>{const out=[];const rows=[...document.querySelectorAll('#agentList .agent-row')];
    rows.forEach((row,i)=>{row.click();out.push(document.getElementById('chatTitle')?.textContent||'')});return out;});
  await page.evaluate(()=>{const i=document.getElementById('chatInput');if(i){i.value='__free_q__';document.getElementById('sendBtn').click()}}); await sleep(1200);

  console.log('agentTitles:',agentSwitch);
  console.log('ERRORS:',errors.length?errors:'NONE');
  await b.close();
})();
```
```bash
mkdir -p shots && node verify.js
```

## 3. 합격 기준
- **`ERRORS: NONE`** (콘솔/페이지 에러 0건) — 빠른 전환 후에도.
- `agentTitles`에 **모든 에이전트가 서로 다르게** 찍힘(클릭 전환 정상).
- 8개 스크린샷을 **이미지로 직접 확인**: 텍스트 잘림/겹침, 차트·게이지·맵·도넛 렌더, KPI에 `NaN`/`undefined` 없음, 토프바·사이드바·푸터 겹침 없음.

## 4. 자주 나오는 실패 → 원인
| 증상 | 원인/수정 |
|---|---|
| 모든 화면이 첫 화면과 동일 | puppeteer가 hash-only 변경을 리로드 안 함 → `hashchange` 리스너 필수, 또는 스크립트에서 `page.evaluate(()=>navigate())` 호출 |
| `KPI: NaN` | `countUp`은 `data-count`, 트윈은 `data-from/to` — 헬퍼와 속성 불일치 |
| `Cannot set properties of null` | 전환 후 비동기 콜백의 DOM 접근 → `if(!el)return` 가드 + `addTimer` |
| 차트 곡선 안 보임 | 인라인 `stroke-dashoffset`이 CSS를 덮음 → JS로 직접 `el.style.strokeDashoffset='0'` |
| 컨트롤·푸터 겹침 | 고정 UI는 화면 가장자리/빈 영역에 배치, z-index 정리 |

## 5. 정리 (필수)
검증이 끝나면 결과 HTML만 남기고 부산물 삭제:
```bash
rm -rf node_modules package.json package-lock.json verify.js shots
```
> 시각 검증용 스크린샷이 사용자에게 유용하면 보여준 뒤 정리한다. 저장소에는 **결과 `.html` 하나만** 남긴다.
