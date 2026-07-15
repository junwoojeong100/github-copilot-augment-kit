# Verification (puppeteer 자동 검증)

데모는 **반드시 자동 검증**한다. macOS에 Chrome이 없을 수 있으므로 puppeteer와 자체 Chromium을
저장소 밖 공용 캐시에 설치하고 재사용한다. 고객별 검증 스크립트와 screenshots만 세션 작업 폴더에
두며, 저장소나 최종 HTML 출력 폴더에서 `npm install`을 실행하지 않는다.

## 0. 전제 — Spec validation + Golden Runtime

브라우저를 열기 전에 Customer Overlay composition, 최종 Spec, 공통 Runtime을 먼저 검사한다.

```bash
python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
  --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
  --pack .github/skills/ai-platform-demo/packs/<industry>.pack.json \
  --customer <session>/files/<app>-work/customer-overlay.json \
  --output <session>/files/<app>-work/demo-spec.json \
  --html-output <session>/files/<app>-work/<app>.html

python3 -B .github/skills/ai-platform-demo/scripts/render_demo.py \
  --spec <session>/files/<app>-work/demo-spec.json \
  --validate-only

node --check .github/skills/ai-platform-demo/runtime/runtime.js
```

## 0.1 해시 라우팅 + `hashchange`
앱은 `location.hash`로 라우팅하고 `addEventListener('hashchange',navigate)`가 있어야 한다.
그래야 검증 스크립트가 `location.hash=route`로 각 화면을 띄울 수 있다.

## 1. 공용 캐시 준비
```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/files/<app>-work"

mkdir -p "$PUPPETEER_HOME" "$WORK_DIR"
if [ ! -f "$PUPPETEER_HOME/package.json" ]; then
  (cd "$PUPPETEER_HOME" && npm init -y)
fi
if [ ! -d "$PUPPETEER_HOME/node_modules/puppeteer" ]; then
  (cd "$PUPPETEER_HOME" && \
    PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
    npm install --save-exact puppeteer)
fi
```

공용 캐시는 작업 종료 시 삭제하지 않는다. `node_modules`, Chromium, package lock은 이 경로에만
두고 고객 HTML·스크린샷·브라우저 프로필은 저장하지 않는다.

## 2. 검증 스크립트

기본은 skill의 재사용 verifier를 실행한다. 고객별 `verify.js`를 매번 다시 작성하지 않는다.

```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/files/<app>-work"

NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="$WORK_DIR/<app>.html" \
SHOTS_DIR="$WORK_DIR/shots" \
FULL_QA=1 \
node .github/skills/ai-platform-demo/scripts/verify_demo.js
```

아래 코드는 verifier의 핵심 동작을 설명하는 참고다.
```js
const puppeteer=require('puppeteer'), path=require('path');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const allRoutes=['dashboard','operations','simulator','improvement','finance','devops','agents','governance']; // Golden Runtime contract
const routes=(process.env.VERIFY_ROUTES||allRoutes.join(',')).split(',').map(x=>x.trim()).filter(Boolean);
const fullQa=process.env.FULL_QA!=='0';
(async()=>{
  const file='file://'+path.resolve(process.env.APP_HTML);
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
    await page.evaluate(()=>['reopt','orchRun','assignIssue','runAnalysis','evalRun'].forEach(id=>{const x=document.getElementById(id);if(x)x.click()}));
    await sleep(300);
    await page.screenshot({path:'shots/'+r+'.png'});
  }
  let agentSwitch=[];
  if(fullQa){
    // (2) 빠른 전환 스트레스 테스트 (null 접근·리스너 누수 적발)
    for(let k=0;k<4;k++)for(const r of allRoutes){await page.evaluate(rt=>location.hash=rt,r);await sleep(90)}
    await sleep(1200);
    // (3) 에이전트 전환 + 자유질문
    await page.evaluate(()=>location.hash='agents'); await sleep(700);
    agentSwitch=await page.evaluate(()=>{const out=[];const rows=[...document.querySelectorAll('#agentList .agent-row')];
      rows.forEach(row=>{row.click();out.push(document.getElementById('chatTitle')?.textContent||'')});return out;});
    await page.evaluate(()=>{const i=document.getElementById('chatInput');if(i){i.value='__free_q__';document.getElementById('sendBtn').click()}}); await sleep(1200);
  }

  console.log('mode:',fullQa?'FULL':'TARGETED');
  console.log('agentTitles:',agentSwitch);
  console.log('ERRORS:',errors.length?errors:'NONE');
  await b.close();
})();
```
```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/files/<app>-work"
REPO_ROOT="<repo-root>"

mkdir -p "$WORK_DIR/shots"
NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="$WORK_DIR/<APP>.html" \
SHOTS_DIR="$WORK_DIR/shots" \
FULL_QA=1 \
node "$REPO_ROOT/.github/skills/ai-platform-demo/scripts/verify_demo.js"
```

수정 중 영향 route만 빠르게 확인:

```bash
NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="<absolute-path>/<APP>.html" \
SHOTS_DIR="<session>/files/<app>-work/shots-targeted" \
VERIFY_ROUTES="finance,agents" \
FULL_QA=0 \
node "<repo-root>/.github/skills/ai-platform-demo/scripts/verify_demo.js"
```

완료 전에는 `VERIFY_ROUTES`를 비우고 `FULL_QA=1`로 다시 실행한다.

## 3. 합격 기준
- **`ERRORS: NONE`** (콘솔/페이지 에러 0건) — 빠른 전환 후에도.
- `agentTitles`에 **모든 에이전트가 서로 다르게** 찍힘(클릭 전환 정상).
- 8개 스크린샷을 **이미지로 직접 확인**: 텍스트 잘림/겹침, 차트·게이지·맵·도넛 렌더, KPI에 `NaN`/`undefined` 없음, 토프바·사이드바·푸터 겹침 없음.

위 합격 기준은 `FULL_QA=1` 결과에만 적용한다. `FULL_QA=0`은 수정 중 회귀 확인용이며 완료 판정에
사용하지 않는다.

## 4. 자주 나오는 실패 → 원인
| 증상 | 원인/수정 |
|---|---|
| 모든 화면이 첫 화면과 동일 | puppeteer가 hash-only 변경을 리로드 안 함 → `hashchange` 리스너 필수, 또는 스크립트에서 `page.evaluate(()=>navigate())` 호출 |
| `KPI: NaN` | `countUp`은 `data-count`, 트윈은 `data-from/to` — 헬퍼와 속성 불일치 |
| `Cannot set properties of null` | 전환 후 비동기 콜백의 DOM 접근 → `if(!el)return` 가드 + `addTimer` |
| 차트 곡선 안 보임 | 인라인 `stroke-dashoffset`이 CSS를 덮음 → JS로 직접 `el.style.strokeDashoffset='0'` |
| 컨트롤·푸터 겹침 | 고정 UI는 화면 가장자리/빈 영역에 배치, z-index 정리 |

## 5. 정리 (필수)
검증이 끝나면 무거운 검증 부산물만 삭제하고 Fact Ledger와 metrics는 세션 폴더에 유지:
```bash
rm -rf <session>/files/<app>-work/shots
```
> 시각 검증용 스크린샷이 사용자에게 유용하면 보여준 뒤 정리한다. 저장소와 최종 출력 폴더에는
> **결과 `.html` 하나만** 남긴다. Python 보조 스크립트가 필요하면 같은 세션 작업 폴더에서
> `python3 -B`로 실행하고 저장소에는 `.py`, `.pyc`, `__pycache__`를 만들지 않는다.
> 공용 Puppeteer 캐시는 삭제하지 않는다. 단계별 시간과 `puppeteer_cache_hit`, `repair_cycles`는
> 세션 작업 폴더의 `metrics.json`에 기록한다.
