# FULL-OPTIMIZED Execution

조사·스토리라인·제작·검증 단계를 유지하면서 wall-clock time과 반복 작업을 줄이는 기본 실행 방식이다.
단계 생략이나 검증 축소가 아니라 **독립 작업의 병렬화, 동일 리비전의 중간 산출물 재사용, 결함 일괄
수정**으로 최적화한다.

## 1. 불변 원칙

- 외부 사실이 필요할 때만 데이터 수집 → Fact Ledger를 수행하고, 이후 deck spec → 스토리라인 →
  슬라이드 제작 → 전체 QA 순서를 유지한다.
- 각 덱의 deck spec, storyline, 생성 스크립트, 최종 PPTX는 한 담당자가 일관되게 소유한다.
  여러 덱에서 공유하는 Fact Ledger·스타일 helper는 메인 에이전트가 관리한다.
- 조사 backend 선택과 원문 검증은 `web-search` 계약을 따른다. 이 가이드에서 특정 backend를 추가로
  금지하거나 강제하지 않는다.
- 수정 후에는 항상 새 PPTX에서 PDF를 다시 변환한다. 국소·비구조 수정은 변경 슬라이드만 이미지로
  렌더하고, 다수 슬라이드나 구조 변경은 전체 contact sheet까지 다시 생성한다.
- 저장소와 최종 출력 폴더에는 사용자가 요청한 PPTX/PDF만 남긴다.

## 2. 세션 작업 계약

`<session>`은 [`SKILL.md`](../SKILL.md)의 세션 작업 정의를 따른다. 클라이언트 고유의 `files`
하위 디렉터리를 가정하지 않으며 저장소·최종 출력 폴더 밖에 있어야 한다.

```text
<session>/<deck>-work/
  fact-ledger.json                # 검증된 근거 정본
  fact-ledger.md                  # JSON에서 자동 생성한 읽기용 뷰
  deck-spec.json
  storyline.md
  template-profile.json          # 템플릿이 있을 때만
  build_<deck>.py
  defects.md
  qa-exceptions.json             # 검토 후 허용할 finding이 있을 때만
  visual-review.json
  metrics.json                  # 성능 측정이 필요한 경우만
  qa/
  qa-detail/
```

- `storyline.md`에는 슬라이드별 제목, 핵심 메시지, 근거, 시각 형태, 이전/다음 연결을 확정한다.
- 코드 작성 전에 `storyline.md`와 `deck-spec.json`을 잠근다. 새 근거나 시각적 blocker가 발견되면 두
  파일을 함께 갱신하고 변경 이유를 기록한다.
- `defects.md`에는 발견 즉시 고치지 말고 슬라이드 번호와 결함 유형을 모아 한 번에 수정한다.

## 3. 조사 병렬화

외부 사실이 필요하면 관련 조사 축만 먼저 나열하고 한 번의 병렬 배치로 실행한다.

1. 주제·고객·산업 사실과 핵심 수치
2. 제품·기술·규제의 현재 상태
3. 사례·성과·경쟁 또는 도입 근거

필요하지 않은 축을 장수 채우기 목적으로 추가하지 않는다. 각 축에서는 `web-search`의 공통 Fact
Ledger 계약으로 근거를 수집하고 슬라이드 매핑은 storyline과 deck spec에 기록한다.
메인 에이전트가 결과를 하나의 Fact Ledger JSON으로 합치고 `web-search` 검증기의 `--markdown-output`으로
읽기용 뷰를 만든 뒤 스토리라인을 시작한다. 두 형식을 따로 수정하지 않는다.
`web-search`의 충분성·완료 기준을 만족하면 탐색을 종료한다.
이전 Fact Ledger와 canonical URL은
검색 출발점으로만 쓰고, 발표에 들어가는 외부 사실은 매 요청 시점의 공식 원문으로 다시 검증한다.
같은 요청에서 이미 검증한 주장·조건·원문은 여러 덱이 공유하며 파일별로 같은 조사를 반복하지 않는다.
현재 자료로 확인하지 못한 항목은 범위를 표시하고 source budget을 넘어 계속 탐색하지 않는다.

## 4. 도구 캐시와 사전 준비

```text
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/
  toolchain.json
  fonts.txt
  .venv/                       # 검증된 환경이 필요할 때만
```

- 캐시는 저장소 밖에 둔다.
- `scripts/toolcheck.py`로 Python·`soffice`·PyMuPDF·Pillow·python-pptx·폰트를 탐지해
  `toolchain.json`/`fonts.txt`에 캐시한다. cache hit에서는 interpreter·PATH·필수 import와 실행 파일을
  빠르게 재확인하고 비용이 큰 폰트 목록 탐색만 생략한다.
- 의존성 설치는 import 실패 또는 도구 부재가 확인될 때만 수행하고 검증된 캐시 환경을 재사용한다.
- 고객 자료·시크릿·생성 산출물은 공용 도구 캐시에 넣지 않는다.
- 도구 사전 준비는 콘텐츠를 만들지 않으므로 조사와 병렬로 실행할 수 있다.

## 5. 단일 소유 제작

- 조사 단계에서는 슬라이드 코드를 작성하지 않는다.
- 해당 덱의 담당자가 검증된 `deck-spec.json`과 잠긴 `storyline.md`를 기준으로 `build_<deck>.py`를
  한 번에 작성한다.
- 슬라이드는 `python-pptx`로 직접 만들고, 정보 유형에 맞는 시각 형태를 매번 다양하게 구성한다.
  고정 템플릿·고정 컴포넌트를 강제하지 않는다.
- (선택) `pptx_helpers`(디자인 중립 프리미티브)를 import해 보일러플레이트만 줄이고, 색·레이아웃은 매 덱 자유 구성한다.
- 여러 에이전트가 같은 생성 스크립트를 동시에 수정하지 않는다.

### 여러 파일의 요청된 병렬 제작

- 여러 파일이라는 이유만으로 위임하지 않는다. 사용자가 파일별 subagent를 요청한 경우에만 필요한 수로
  나누고, 한 파일의 연속적인 조사·제작·수정은 한 담당자가 끝까지 맡는다.
- 메인 에이전트가 먼저 원본 목록·공통 Fact Ledger·스타일·완료 기준을 준비한다. 담당자마다 내용 보존
  목록, 작업 디렉터리, 출력명, 장수·시간, 필요한 source/Fact ID, QA·반환 형식을 전달한다.
- 공통 근거와 helper는 읽기 전용으로 공유한다. 담당자는 자기 덱의 계획·spec·생성 스크립트·QA만 수정한다.
  공통 수정은 메인 에이전트가 조정하고, 제작 중 준비 스크립트를 재실행해 담당자의 계획을 덮어쓰지 않는다.
- 각 담당자는 PPTX 경로·SHA-256·장수·내용 보존 결과·QA 보고서·revision-bound 시각 검토를 반환한다.
  최종 출력 폴더 복사와 전체 완료 선언은 메인 에이전트만 수행한다.
- 메인은 위임한 제작·조사를 중복하지 않고, 반환된 근거로 파일별 전달 검사를 수행한다.
  보완은 같은 담당자에게 구체적으로 요청하며 한 파일의 PASS를 다른 파일에 재사용하지 않는다.

## 6. QA 최적화

1. `verify_deck.py --deck-spec --reuse-render`로 최초 구조 감사와 전체 렌더를 읽기 전용 병렬 실행한다.
2. Runner가 최초 전체 렌더의 PDF를 세션 QA 폴더에 유지한다(`render_pptx.py`를 직접 실행할 때는
   `--keep-pdf` 사용).
3. audit risk score로 선택된 슬라이드를 같은 PDF로 자동 상세 렌더하고 contact sheet와 함께 확인한다.
4. 모든 결함을 `defects.md`에 모은 뒤 생성 스크립트를 한 번에 수정한다. chart·SmartArt처럼 자동
   매핑이 불가능한 finding은 확대 검토 후 finding ID와 이유를 exception manifest에 기록한다.
5. PPTX를 재생성하고 새 PDF로 변환한다. 국소·비구조 수정이면 `--slides`로 변경 슬라이드만 이미지화해
   확인하고 전체 contact sheet는 다시 만들지 않는다.
6. 최종 revision의 contact sheet와 위험 슬라이드를 확인하고 deck SHA-256에 묶인 visual-review
   evidence를 만든 뒤 같은 `--out`·`--reuse-render`로 verifier를 다시 실행한다. 일치하는 전체 렌더만
   재사용하고 계약·시각 검토 판단은 다시 검사한다. 상세 조건은 [렌더 재사용](./verification.md#render-reuse)을 따른다.

`--reuse-pdf`는 PPTX와 PDF SHA-256이 manifest와 모두 일치할 때만 동작한다. 어느 파일이든 변경되면
실패하도록 설계되어 오래되거나 부분 생성된 PDF로 검수하는 품질 저하를 막는다.

## 7. 선택적 시간 측정

반복 최적화나 benchmark가 필요한 작업에서만 `metrics.json`을 기록한다. 일반 덱 생성의 완료 조건은
아니며, 기록할 때는 다음 필드를 사용할 수 있다.

```json
{
  "research_seconds": 0,
  "storyline_seconds": 0,
  "build_seconds": 0,
  "first_full_qa_seconds": 0,
  "repair_cycles": 0,
  "final_full_qa_seconds": 0,
  "pdf_reused": false,
  "tool_cache_hit": false
}
```

측정 파일은 세션 작업 폴더에만 둔다. 실제 병목이 조사, 생성, LibreOffice 변환, 시각 수정 중 어디인지
판단할 때만 사용한다.
