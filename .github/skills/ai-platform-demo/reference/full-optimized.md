# FULL-OPTIMIZED Execution

리서치·스토리라인·화면 설계·빌드·전체 검증을 모두 유지하면서 반복 설치와 중복 검증을 줄이는
기본 실행 방식이다.

## 1. 불변 원칙

- 5단계 순서를 유지하며 리서치가 합쳐지기 전에는 스토리라인을 시작하지 않는다.
- 스토리라인, Adaptive Design DNA, 화면 계약, 고객 Demo Spec, 최종 단일 HTML은 한 에이전트가 소유한다.
- 공통 shell·CSS·JavaScript는 Golden Runtime에서 재사용하며 고객별로 다시 작성하지 않는다.
- `/fleet` 또는 병렬 subagent는 독립적인 조사와 읽기 전용 검사에만 사용한다.
- 수정 중에는 변경 화면만 빠르게 확인할 수 있지만, 완료 전에는 8개 화면·스트레스 전환·에이전트
  전환·채팅을 포함한 전체 검증을 다시 수행한다.
- 저장소와 최종 출력 폴더에는 결과 HTML 하나만 남긴다.

## 2. 세션 작업 계약

```text
<session>/files/<app>-work/
  fact-ledger.md
  storyline.md
  design-dna.md
  view-contract.md
  customer-overlay.json
  demo-spec.json
  defects.md
  metrics.json
  shots/
```

`view-contract.md`에는 각 route의 KPI, 필수 DOM ID, 클릭 동작, 시뮬레이터 입력, 예상 결과,
에이전트 전환 조건을 기록한다. `design-dna.md`에는 고객별 archetype·token·density·avoid를 기록하고,
실시간 Fact Ledger와 함께 `customer-overlay.json`으로 합친다. Composer가 Industry Pack과 Overlay를
`demo-spec.json`으로 만들며 이후 수정 surface는 HTML이나 전체 Spec보다 Overlay를 우선한다.

## 3. 리서치 병렬화

다음 세 축은 같은 리서치 단계 안에서 동시에 수행할 수 있다.

1. 고객 사업·제품·규모 수치
2. 고객의 DX·AI 현황과 최근 이슈
3. Microsoft·GitHub 서비스의 현재 상태

각 조사자는 1차 출처 URL·확인일·핵심 근거만 반환한다. 메인 에이전트가 결과를 하나의 Fact Ledger로
합치고 충돌을 해결한 뒤에만 스토리라인을 시작한다. 기존 원장이 있으면 안정적인 회사 사실은 출처를
찾는 참고로만 사용하고, **고객 요청마다 공식 원문을 실시간으로 다시 확인한다.** 이전 Fact Ledger나
Industry Pack의 사실이 새 조사를 대체하면 안 된다.

## 4. Puppeteer 공용 캐시

```text
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/ai-platform-demo/puppeteer/
  package.json
  package-lock.json
  node_modules/
  chromium/
```

- 공용 캐시는 저장소 밖에 두며 작업 종료 시 삭제하지 않는다.
- Puppeteer와 Chromium은 캐시에 없을 때만 설치한다.
- `verify.js`, screenshots, 고객별 HTML은 캐시하지 않고 세션 작업 폴더에 둔다.
- 캐시에 고객 데이터, 시크릿, 브라우저 프로필을 보관하지 않는다.
- 도구 사전 준비는 콘텐츠를 만들지 않으므로 리서치와 병렬로 실행할 수 있다.

## 5. Golden Runtime 기반 단일 소유 빌드

- 조사 subagent가 화면별 HTML/CSS/JS를 따로 작성하지 않는다.
- 메인 에이전트가 잠긴 storyline·Design DNA·view contract와 실시간 research metadata를
  `customer-overlay.json`으로 작성한다.
- `scripts/compose_demo_spec.py`가 base + Industry Pack + Customer Overlay를 합치고
  `scripts/render_demo.py` validation을 거쳐 단일 HTML까지 생성한다.
- Industry Pack은 `meta`, `story`, `design`을 소유하지 않으며 고객 Overlay가 전체 Design DNA를
  제공하지 않으면 Composer가 실패한다.
- 고객 콘텐츠·브랜드 표현·산업 공식·Agent는 spec에서 새로 매핑하고 runtime engine은 재사용한다.
- 기본 수정은 Overlay→재합성으로 수행한다. 핵심 장면이 runtime variant로 표현되지 않을 때만 해당
  route를 bespoke patch한다.
- 여러 에이전트가 같은 spec·HTML을 동시에 편집하지 않는다.

## 6. 검증 최적화

1. 최초 빌드 후 `FULL_QA=1`로 8개 화면, 스트레스 전환, 모든 에이전트, 채팅을 한 브라우저 세션에서 검사한다.
2. 8개 스크린샷과 오류를 모두 검토해 `defects.md`에 모은다.
3. 결함을 한 번에 수정한다.
4. 수정 중에는 `VERIFY_ROUTES`와 `FULL_QA=0`으로 영향받은 화면만 빠르게 확인한다.
5. 완료 전에는 다시 `FULL_QA=1`로 전체 검증한다. 수정이 없으면 최초 전체 검증이 최종 검증이다.

화면마다 브라우저를 새로 시작하지 않는다. 한 번의 검증 실행에서 같은 browser/page를 재사용하고,
route만 전환한다.

## 7. 시간 측정

```json
{
  "research_seconds": 0,
  "storyline_design_seconds": 0,
  "customer_overlay_seconds": 0,
  "spec_compose_seconds": 0,
  "build_seconds": 0,
  "runtime_render_seconds": 0,
  "bespoke_extension_routes": 0,
  "first_full_qa_seconds": 0,
  "repair_cycles": 0,
  "targeted_qa_seconds": 0,
  "final_full_qa_seconds": 0,
  "puppeteer_cache_hit": false
}
```

`metrics.json`은 세션 작업 폴더에만 두고 다음 최적화의 근거로 사용한다.
