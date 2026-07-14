# FULL-OPTIMIZED Execution

리서치·스토리라인·화면 설계·빌드·전체 검증을 모두 유지하면서 반복 설치와 중복 검증을 줄이는
기본 실행 방식이다.

## 1. 불변 원칙

- 5단계 순서를 유지하며 리서치가 합쳐지기 전에는 스토리라인을 시작하지 않는다.
- 스토리라인, 화면 계약, 디자인 토큰, 최종 단일 HTML은 한 에이전트가 소유한다.
- `/fleet` 또는 병렬 subagent는 독립적인 조사와 읽기 전용 검사에만 사용한다.
- 수정 중에는 변경 화면만 빠르게 확인할 수 있지만, 완료 전에는 8개 화면·스트레스 전환·에이전트
  전환·채팅을 포함한 전체 검증을 다시 수행한다.
- 저장소와 최종 출력 폴더에는 결과 HTML 하나만 남긴다.

## 2. 세션 작업 계약

```text
<session>/files/<app>-work/
  fact-ledger.md
  storyline.md
  view-contract.md
  defects.md
  metrics.json
  verify.js
  shots/
```

`view-contract.md`에는 각 route의 KPI, 필수 DOM ID, 클릭 동작, 시뮬레이터 입력, 예상 결과,
에이전트 전환 조건을 기록한다. 이 계약을 확정한 뒤 HTML을 조립하면 후기 DOM 변경과 검증 스크립트
수정을 줄일 수 있다.

## 3. 리서치 병렬화

다음 세 축은 같은 리서치 단계 안에서 동시에 수행할 수 있다.

1. 고객 사업·제품·규모 수치
2. 고객의 DX·AI 현황과 최근 이슈
3. Microsoft·GitHub 서비스의 현재 상태

각 조사자는 1차 출처 URL·확인일·핵심 근거만 반환한다. 메인 에이전트가 결과를 하나의 Fact Ledger로
합치고 충돌을 해결한 뒤에만 스토리라인을 시작한다. 기존 원장이 있으면 안정적인 회사 사실은 출처를
재확인하고, 최근 뉴스와 제품 상태는 항상 새로 확인한다.

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

## 5. 단일 소유 빌드

- 조사 subagent가 화면별 HTML/CSS/JS를 따로 작성하지 않는다.
- 메인 에이전트가 잠긴 storyline과 view contract를 기준으로 단일 파일을 조립한다.
- 검증된 app shell, router, timer cleanup, SVG helper는 재사용하되 고객 콘텐츠와 브랜드 표현은
  새로 매핑한다.
- 여러 에이전트가 같은 HTML을 동시에 편집하지 않는다.

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
  "build_seconds": 0,
  "first_full_qa_seconds": 0,
  "repair_cycles": 0,
  "targeted_qa_seconds": 0,
  "final_full_qa_seconds": 0,
  "puppeteer_cache_hit": false
}
```

`metrics.json`은 세션 작업 폴더에만 두고 다음 최적화의 근거로 사용한다.
