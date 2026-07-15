# FULL-OPTIMIZED Execution

모든 조사·서사·디자인·제작·검증 단계를 유지하면서 wall-clock time과 반복 작업을 줄이는 기본
실행 방식이다. 단계 생략이나 검증 축소가 아니라 **독립 작업의 병렬화, 동일 리비전의 중간 산출물
재사용, 결함 일괄 수정**으로 최적화한다.

## 1. 불변 원칙

- 조사 → Fact Ledger → 서사 → Design DNA → 청사진 → 제작 → 전체 QA 순서를 유지한다.
- Storyline, Design DNA, 생성 스크립트, 최종 PPTX는 한 에이전트가 일관되게 소유한다.
- `/fleet` 또는 병렬 subagent는 서로 독립적인 조사와 읽기 전용 검사에만 사용한다.
- 수정 중에는 증분 검사를 허용하지만, 완료 전에는 반드시 전체 구조 감사와 전체 렌더를 다시 수행한다.
- 저장소와 최종 출력 폴더에는 사용자가 요청한 PPTX/PDF만 남긴다.

## 2. 세션 작업 계약

```text
<session>/files/<deck>-work/
  fact-ledger.md
  deck-spec.md
  design-dna.md
  build_<deck>.py
  defects.md
  metrics.json
  qa/
  qa-detail/
```

- `deck-spec.md`에는 슬라이드별 제목, 핵심 메시지, 시각 구조, 근거, 이전/다음 연결을 확정한다.
- 코드 작성 전에 `deck-spec.md`와 `design-dna.md`를 잠가 후기 구조 변경을 줄인다.
- `defects.md`에는 발견 즉시 수정하지 말고 슬라이드 번호와 결함 유형을 모아 한 번에 수정한다.

## 3. 조사 병렬화

입력 확정 후 다음 조사 축을 최대 2~3개로 나눠 동시에 수행할 수 있다.

1. 주제·고객·산업 사실과 핵심 수치
2. 제품·기술·규제의 현재 상태
3. 사례·성과·경쟁 또는 도입 근거

각 조사자는 URL·확인일·인용 가능한 근거만 반환한다. 메인 에이전트가 결과를 하나의 Fact Ledger로
합친 후에만 서사를 시작한다. 기존 원장이 있으면 사업 영역처럼 안정적인 사실은 출처를 재확인하고,
가격·제품 상태·규제·최근 뉴스처럼 변동성이 큰 사실은 항상 새로 확인한다.

조사 자체는 캐시로 생략하지 않는다. 이전 Fact Ledger와 canonical URL은 검색 출발점으로만 사용하고,
발표에 들어가는 외부 사실은 매 요청 시점의 공식 원문으로 다시 검증한다.

## 4. 도구 캐시와 사전 준비

```text
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/
  toolchain.json
  fonts.txt
  .venv/                       # 검증된 환경이 필요할 때만
```

- 캐시는 저장소 밖에 둔다.
- Python, `soffice`, PyMuPDF, Pillow, 폰트 경로를 한 번 확인한 뒤 같은 작업에서는 반복 탐색하지 않는다.
- 의존성 설치는 import 실패 또는 도구 부재가 확인될 때만 수행하고, 검증된 캐시 환경을 재사용한다.
- 고객 자료, 시크릿, 생성 산출물은 공용 도구 캐시에 넣지 않는다.
- 도구 사전 준비는 콘텐츠를 만들지 않으므로 조사와 병렬로 실행할 수 있다.

## 5. 단일 소유 제작

- 조사 subagent가 슬라이드 코드나 Design DNA를 작성하지 않는다.
- 메인 에이전트가 잠긴 `deck-spec.md`를 기준으로 생성 스크립트를 한 번에 작성한다.
- `pptx_compiler`의 검증된 primitive·semantic blueprint와 audit/render 도구를 재사용한다.
- 표준 슬라이드는 시각 토큰이 없는 `DeckRecipe`와 certified component로 조립한다.
- Recipe selector는 family 사용량·최근 반복·density·slot 수를 반영하고 핵심 슬라이드는 explicit override/custom builder로 구성한다.
- Compiler에는 기본 테마를 두지 않고 팔레트·타이포·시각 은유·layout rhythm은 매 요청에서 새로 만든다.
- Compiler preflight로 경계·텍스트 하한·레이아웃 다양성을 먼저 차단한 뒤 외부 audit/render QA를 수행한다.
- 여러 에이전트가 같은 생성 스크립트를 동시에 수정하지 않는다.

## 6. QA 최적화

1. `verify_deck.py`로 구조 감사와 전체 렌더를 읽기 전용 병렬 실행한다.
2. 최초 전체 렌더는 `--keep-pdf`로 세션 QA 폴더에 PDF를 유지한다.
3. audit risk score로 선택된 슬라이드를 같은 PDF로 자동 상세 렌더하고 contact sheet와 함께 사람이 확인한다.
4. 모든 결함을 `defects.md`에 모은 뒤 생성 스크립트를 한 번에 수정한다.
5. PPTX를 재생성하고 구조 감사와 변경 슬라이드 검사를 수행한다.
6. 변경이 있었다면 마지막에 전체 렌더와 전체 contact sheet를 다시 생성한다. 변경이 없으면 최초 전체
   렌더가 최종 검증이다.

`--reuse-pdf`는 PPTX SHA-256이 manifest와 일치할 때만 동작한다. PPTX가 변경되면 실패하도록
설계되어 있으므로 오래된 PDF로 검수하는 품질 저하를 막는다.

## 7. 시간 측정

`metrics.json`에는 최소한 다음을 기록한다.

```json
{
  "research_seconds": 0,
  "storyline_design_seconds": 0,
  "build_seconds": 0,
  "first_full_qa_seconds": 0,
  "repair_cycles": 0,
  "final_full_qa_seconds": 0,
  "pdf_reused": false,
  "tool_cache_hit": false
}
```

측정 파일은 세션 작업 폴더에만 둔다. 다음 작업에서는 실제 병목이 조사, 생성, LibreOffice 변환,
시각 수정 중 어디인지 판단하는 근거로 사용한다.
