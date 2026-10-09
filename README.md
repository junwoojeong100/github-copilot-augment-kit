# GitHub Copilot Augment Kit

GitHub Copilot을 특정 모델에 종속되지 않는 **고성능 엔지니어링 에이전트**로 확장하는 경량 커스터마이징 킷입니다. 단일 지침 파일과 온디맨드 스킬로 사고·소통·안전·코딩·Git·팩트체크·웹 조사·PPTX 제작 워크플로를 제공하며, 모든 결과는 결론과 다음 행동이 먼저 보이는 **Straightforward** 형식을 우선합니다.

이 리포의 `.github/` 폴더를 프로젝트에 두면 GitHub Copilot(VS Code Chat의 Agent mode·터미널 CLI)이
지침과 스킬을 자동으로 읽습니다. `.vscode/mcp.json`까지 적용하면 VS Code Agent mode에서도
Microsoft Learn MCP를 사용할 수 있습니다.

> **Augment**는 GitHub Copilot의 역량을 지침·스킬·MCP로 보강한다는 뜻입니다. 특정 모델명은 저장소 정체성에 포함하지 않으며, `/model` 또는 모델 선택기에서 현재 작업에 가장 적합한 모델로 언제든 교체할 수 있습니다.
>
> **GPT-6 Astra 대응**: 완료 조건 중심 실행, 필요한 참조만 읽기, 독립 도구 호출의 병렬화, 검증 실패의 명시적 처리를 강화했습니다. 모델의 내부 특성이나 특정 reasoning 설정에 의존하지 않습니다. 기존 GPT-5.6 Sol 검증 기록(2026-07-15)은 과거 이력이며, GPT-6 Astra의 실제 품질·속도 향상을 입증하는 비교 평가는 아닙니다.

---

## 이게 뭔가요? (3줄 요약)

- **무엇**: GitHub Copilot에 입힐 수 있는 단일 지침 + 전문 스킬 모음입니다.
- **왜**: 기반 모델이 바뀌어도 Straightforward한 결과와 일관된 품질·안전·전문 워크플로를 유지하도록 Copilot의 실행 방식을 보강합니다.
- **어떻게**: `.github/`를 두면 지침·스킬이 자동 로드되고, 조사·스토리라인·PPTX 제작에 통합 QA Runner를 연결해 반복 작업을 줄입니다.

---

## 무엇이 들어있나 — 3가지 빌딩 블록

| 블록 | 위치 | 동작 방식 | 내용 |
|------|------|----------|------|
| **Instructions** | `.github/copilot-instructions.md` | 매 대화 **자동 로드** | Straightforward 결과 · 페르소나 · 사고 · 소통 · 안전 · 코딩 · Git · MS/GitHub 가치 · 팩트체크 · 출처 |
| **Skills** | `.github/skills/` | 관련 질문 시 **자동 활성화** 또는 `/skill-name` | 결론 우선 실시간 검색 · 적응형 PPTX 생성 |
| **MCP (사전 번들)** | `.github/mcp.json` · `.vscode/mcp.json` | clone 후 신뢰/Start 승인 시 활성화 | Microsoft Learn MCP — 공식 문서·코드 샘플 검색 (Azure 실습용 MCP는 선택 연결) |

> 상시 적용 원칙은 **단일 파일로 통합**해 중복을 줄이고, 상세 워크플로는 관련 작업에서만 스킬로 불러옵니다.

---

## 5분 빠른 시작

### 1) 먼저 체험해보기

```bash
git clone https://github.com/junwoojeong100/github-copilot-augment-kit.git
cd github-copilot-augment-kit
code .
```

VS Code에서 Copilot Chat을 **Agent mode**로 열고 **모델 선택기(Model Picker)** 에서 작업에 적합한
모델을 선택합니다. 모델이 바뀌어도 동일한 지침과 스킬이 적용됩니다.

### 2) 내 프로젝트에 적용하기

전체 킷을 적용하려면 **`.github/`와 `.vscode/mcp.json`**을 프로젝트 루트에 복사합니다.
아래 명령은 대상 프로젝트에 같은 이름의 설정 파일이 없을 때만 사용하세요.

```bash
cp -R github-copilot-augment-kit/.github /path/to/my-project/
mkdir -p /path/to/my-project/.vscode
cp github-copilot-augment-kit/.vscode/mcp.json /path/to/my-project/.vscode/mcp.json
```

> **기존 프로젝트 주의**: `.github/copilot-instructions.md`, `.github/mcp.json`,
> `.vscode/mcp.json` 또는 같은 이름의 스킬이 이미 있으면 위 명령을 그대로 실행하지 말고 내용을
> 검토해 병합하세요. repository-wide `copilot-instructions.md`는 하나지만,
> `.github/instructions/**/*.instructions.md`와 `AGENTS.md`는 함께 사용할 수 있습니다.

터미널(Copilot CLI)로 시작하거나, 스킬을 개인 환경에 설치하고 MCP를 확인·추가하는 단계별 안내는
**[설치·사용 가이드](SETUP-GUIDE.md)**를 참고하세요.

---

## 어디서 쓸 수 있나 — VS Code Agent mode & 터미널(CLI)

이 킷은 **VS Code Copilot Chat의 Agent mode**와 터미널용
**[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/copilot-cli/about-copilot-cli)**
양쪽에서 동작합니다.

### Copilot CLI 설치

활성 GitHub Copilot 구독이 필요합니다. 공식 설치 방법은
[GitHub Docs](https://docs.github.com/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)를
기준으로 확인하세요.

```bash
# macOS / Linux (Homebrew)
brew install --cask copilot-cli

# 크로스 플랫폼 (npm, Node.js 22+)
npm install -g @github/copilot
```

설치 후 리포 디렉토리에서 `copilot`을 실행하고, 첫 실행 시 `/login`으로 인증합니다.

| 명령 | 설명 |
|------|------|
| `/model` | 작업에 사용할 AI 모델 선택 또는 Auto 설정 |
| `/diff` | 변경사항 리뷰 |
| `/plan` | 구현 계획 수립 |
| `/help` | 전체 명령 보기 |

### VS Code Agent mode vs Copilot CLI

| 항목 | VS Code Copilot Chat (Agent mode) | GitHub Copilot CLI |
|------|---------------------|-------------------|
| `copilot-instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `skills/` | ✅ 자동 활성화 · `/skill-name` | ✅ 자동 활성화 · `/skill-name` |
| Microsoft Learn MCP | `.vscode/mcp.json`에서 Start | `.github/mcp.json`을 신뢰 후 자동 로드 |
| 범용 최신 웹 검색 | 공식 도메인 검색 → Copilot web search(Research는 요청·지시 시) | 공식 도메인 검색 → 내장 web search(Research는 요청·지시 시) |

---

## 설계 원칙 — 변동 지식은 최소화하고, 필요할 때 최신 확인

이 킷의 지침·스킬은 주로 **방향(무엇을 다룰지), 형식(어떻게 정리할지), 재사용 가능한
워크플로**를 정의합니다. 서비스명과 예시는 포함하지만, 자주 바뀌는 기능 상태·가격·수치·규제
조항은 가능한 한 고정하지 않습니다.

- **왜?** 클라우드·AI·규제는 빠르게 변합니다. 박제된 내용은 금방 낡고 토큰만 소모합니다.
- **대신** 답변 시점에 공식 문서(`learn.microsoft.com` · `docs.github.com`)와 client가 제공하는 web
  search/Research 도구 또는 승인된 search MCP로 최신 정보를 확인합니다.
- **효과**: 최신성 오류와 유지보수 부담을 줄입니다. 검색 가능 여부와 원문 갱신 시점에 따라 최신성에는 한계가 있을 수 있습니다.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md              # 단일 핵심 지침 (매 대화 자동 로드)
├── mcp.json                             # Microsoft Learn MCP 사전 번들 (CLI 워크스페이스 자동 로드)
├── mcp.enghub.example.json              # Microsoft 사내 EngHub MCP 예시 (임직원이 복사해서 사용)
└── skills/                              # 전문 스킬 (온디맨드)
    ├── web-search/                      # 실시간 웹·공식 문서 검색과 구조화 수집
    │   ├── SKILL.md
    │   ├── schema/                      # machine-readable Fact Ledger 계약
    │   ├── scripts/                     # Fact Ledger schema·semantic validator
    │   ├── examples/                    # Fact Ledger JSON 예제
    │   └── tests/                       # 검색·수집 정책 계약 테스트
    └── adaptive-presentation/           # 주제·청중별 PPTX 생성기(조사·스토리라인 중심)
        ├── SKILL.md                     # 조사→Deck Spec→자유 제작→revision-bound 검증
        ├── schema/                      # Deck Spec·template·finding 예외·시각 검토 계약
        ├── reference/                   # 스토리라인·제작·검증·Deck Spec 가이드
        ├── scripts/                     # template/font adapter·통합 QA·렌더링
        └── tests/                       # 계약·adapter·검증 Runner 회귀/E2E 테스트
.vscode/
└── mcp.json                             # VS Code Copilot Agent용 MCP 번들
SETUP-GUIDE.md                           # Copilot CLI·스킬·MCP 설치·사용 + Azure 실습용 MCP 가이드
```

---

## 구성 요소 자세히

### Instructions — `copilot-instructions.md` (자동 적용)

매 대화에 자동 로드되는 단일 지침. 아래 원칙을 압축해 담습니다.

| 섹션 | 핵심 |
|------|------|
| 페르소나 & 사고 | 지적 겸손, 위험·복잡도에 비례한 판단, 불확실성 표기 |
| 실행 계약 | 산출물·제약·완료 조건 확정 → 현재 상태 확인 → 최소 변경 → 요청한 동작 직접 검증 |
| 도구·컨텍스트 | 현재 도구 schema 확인, 단계별 참조 로딩, 독립 호출 병렬화, 요청·지시된 경우에만 위임 |
| 커뮤니케이션 | Straightforward 결과, 결론 우선(BLUF), 적응적 소통, 한국어 존댓말+영문 병기 |
| 안전 & 윤리 | 해로운 콘텐츠 거부, PII/시크릿 보호 |
| 코딩 | 가독성·보안(OWASP) 우선, 언어별 베스트 프랙티스 |
| Git 워크플로우 | 영어 커밋, Conventional Commits, PR 규칙 |
| MS/GitHub 가치 | 구체 서비스로 통제·가치 매핑(Foundry·Agent Framework·GitHub Platform·AKS·ACA 등) |
| 팩트체크 · 출처 | 최신·수치·논쟁·의사결정 핵심 주장만 검증 표, 실제 참조한 출처 명시 |

### [Skills](https://docs.github.com/copilot/concepts/agents/about-agent-skills) — 자연어 또는 `/skill-name`

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **web-search** | "최신 버전 알려줘", "고객·산업 기초자료 수집해줘" | 공식 원문을 검증하고 JSON Fact Ledger를 정본으로 관리하며 Markdown 뷰를 자동 생성해 downstream 스킬에 전달 |
| **adaptive-presentation** | "병원 경영진 대상 의료 AI 전략 PPT 20장", "기술 발표자료 만들어줘", "제품 소개 슬라이드" | 결론·다음 행동 우선 스토리라인 + 필요한 외부 조사 + python-pptx 자유 제작 + 통합 QA Runner → 편집 가능한 PPTX |

`web-search`는 단순 사실 확인에 파일을 만들지 않고, 비교·다중 주장·고위험 판단·후속 산출물에만
Research Brief와 Fact Ledger를 적용합니다. 같은 요청의 동일 조건에서 확인한 원문은 공유하되,
JSON 검증 통과를 사실성의 증명으로 취급하지 않습니다.

---

## 적응형 PPT 스킬 (`adaptive-presentation`)

임원 보고, 고객 제안, 제품 소개, 기술 아키텍처, 교육·세미나 등 다른 주제와 청중에도 실제 `.pptx`를
생성합니다.

이 스킬의 무게 중심은 **① 필요한 근거 수집(Fact Ledger)** 과 **② 목적에 맞는 스토리라인 설계**입니다.
슬라이드 시각화는 고정 템플릿이나 고정 생성 프레임워크에 의존하지 않고, 매 요청마다 주제에 맞게
**자유롭고 다양하게** `python-pptx`로 직접 구성하되 제작·검증 시간은 최소화합니다. 표지와 첫 본문
슬라이드에서 결론·가치·다음 행동이 보이고, 이후 장은 그 결론에 필요한 근거만 쌓는 Straightforward
구성을 최우선으로 합니다.

진행 순서: ① 신규/개선·조사 필요 여부 판단과 도구·폰트 사전 점검 → ② 필요한 공식 자료 조사·Fact Ledger →
③ Deck Spec 검증과 Storyline 확정 → ④ 템플릿 profile·설치 폰트를 반영한 `python-pptx` 제작 →
⑤ capability-aware QA와 revision-bound 시각 검토 순입니다. 도구·권한 때문에 검증하지 못한 결과는
완료본이 아니라 초안으로 구분합니다.

```text
필요한 경우 Fact Ledger
  → Deck Spec + Storyline(슬라이드별 결론·Fact ID·시각 형태)
  → python-pptx 자유 제작(제공 템플릿은 master·layout·theme·canvas 보존)
  → 편집 가능한 PPTX
  → 통합 QA Runner + finding 단위 예외 + SHA-256 시각 검토 증거
```

**슬라이드는 고정 생성 엔진 없이 `python-pptx`로 직접 만듭니다.** 정보 관계(숫자·흐름·비교·계층·사례)에
맞는 시각 형태를 슬라이드마다 자유롭게 선택하고, 같은 구조를 기계적으로 반복하지 않습니다. 템플릿이
있으면 profile을 추출해 원본 master와 theme을 보존하고, 없으면 환경에서 확인한 언어별 설치 폰트를
선택합니다. [타이포그래피](.github/skills/adaptive-presentation/reference/pptx-production.md#typography)·
[대비](.github/skills/adaptive-presentation/reference/pptx-production.md#contrast)·
[발표 노트](.github/skills/adaptive-presentation/reference/pptx-production.md#speaker-notes)의 상세 기준은 제작 가이드에서 관리합니다.
출처 footer는 발행자·문서명·원문 링크로 표시합니다. 내부 Fact ID와 원본 확인 날짜는 화면에서 기본
생략하되 근거 기록과 해석에 필요한 날짜·버전은 보존합니다. 아이디어가 필요하면 `reference/slide-blueprints.md`의 관계형 패턴을
선택적으로 참고하되 그대로 복제하지 않습니다.

기존 덱 개선은 [refinement 가이드](.github/skills/adaptive-presentation/reference/refinement.md)에 따라
내용 원본과 디자인 참고를 분리하고, 사례·수치·조건을 항목별로 대응시킨 뒤 원본을 보존한 새 버전으로
전달합니다. 고객 사례는 공개 성과·협력 발표·미확인 후보를 구분하며 수치의 분모·기간·초기 결과 조건을
함께 표시합니다. 대비·의미 보존·발표 시간은 자동 QA와 별도의 편집 검토로 확인합니다.

외부 사실 조사의 backend와 원문 검증은 `web-search` 계약을 따릅니다. 이전 Fact Ledger와 URL은 검색
출발점으로만 사용하며, 기능 상태·가격·규제·고객 성과는 발표 요청마다 현재 공식 원문으로 다시
확인합니다. 사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱에는 웹 조사를 강제하지
않습니다.

복합 조사에서는 검증된 `fact-ledger.json`이 근거의 정본이며, 읽기용 Markdown을 별도로 다시 작성하지 않습니다.

```bash
python3 -B .github/skills/web-search/scripts/validate_fact_ledger.py \
  <session>/<deck>-work/fact-ledger.json \
  --markdown-output <session>/<deck>-work/fact-ledger.md
```

재생성 Python 스크립트와 QA 파일은 세션 작업 폴더에 격리하며 저장소와 최종 출력 폴더에는 사용자가
요청한 최종 파일 외 중간 자산을 남기지 않습니다. 중간 PDF는 manifest의 PPTX·PDF SHA-256이 모두
일치할 때만 상세 슬라이드 렌더에 재사용합니다. 수정 후에는 변경 부분을 먼저 확인하되 완료 전 요구되는
구조·시각 검증을 다시 수행합니다.

```text
> 병원 경영진 대상 의료 AI 전략 발표자료 20장 만들어줘.
> 청중은 개발자야. 이벤트 기반 아키텍처를 교육하는 기술 PPT 15장으로 만들어줘.
> 이 기존 PPT는 내용은 유지하고, 투자위원회 대상의 절제된 디자인으로 재구성해줘.
```

슬라이드 시각화는 주제·내용에 따라 매번 다르게 구성하며 **정해진 템플릿·색상·카드 스타일을 복제하지
않습니다.**

통합 검증:

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx --out <session>/<deck>-work \
  --deck-spec <session>/<deck>-work/deck-spec.json --reuse-render
```

Runner는 구조 감사와 전체 렌더를 병렬 실행하고 그룹 자식·표 셀을 semantic frame으로 매핑합니다.
chart·SmartArt·unmapped text·overflow는 성공으로 숨기지 않고 finding ID를 발급합니다. 확대 검토한
의도적 예외만 ID와 이유를 manifest에 남기며, 최종 contact sheet 검토는 현재 PPTX SHA-256과 연결된
`visual-review-rNNN.json`으로 증명합니다. 수정마다 기존 증거를 보존하고
[revision별 새 파일](.github/skills/adaptive-presentation/reference/verification.md#visual-review-revisions)의
경로를 `--visual-review`로 지정합니다. QA Runner는 비어 있지 않은 일반 출력 디렉터리를 덮어쓰지 않습니다.

`--reuse-render`는 같은 입력·렌더 환경·옵션과 검증된 산출물 해시가 일치할 때 전체 PDF·contact sheet를
재사용합니다. 입력이 달라지면 새로 렌더하고, 손상된 캐시는 오류로 처리합니다. 구조·근거·언어·notes·
시각 검토 판단은 매번 다시 검사합니다. 옵션 없는 기존 CLI 동작은 유지합니다.

모든 프로젝트에서 쓰는 개인 설치는 [설치·사용 가이드](SETUP-GUIDE.md#skills-personal)를 따르세요.
`adaptive-presentation`은 `web-search`의 검증 스크립트를 참조하므로 두 스킬을 함께 설치해야 합니다.

---

## PPT 제작 시간을 줄이는 실행 구조

`adaptive-presentation`은 기본적으로 **FULL-OPTIMIZED** 정책을 사용합니다. 조사·스토리라인·제작·전체 QA를
생략하는 대신, 안전한 병렬화·캐시·중간 산출물 재사용과 결함 일괄 수정으로 중복 작업과 wall-clock
time을 줄입니다.

| 최적화 | `adaptive-presentation` |
|---|---|
| **생성 메커니즘 재사용** | 고정 생성 엔진 대신 python-pptx로 직접 제작하고 조사·검증·렌더 스크립트만 재사용 |
| **요청별 변경 surface 축소** | 외부 조사가 필요하면 Fact Ledger를 만들고, 스토리라인을 먼저 확정한 뒤 슬라이드는 주제에 맞게 자유 제작 |
| **안전한 병렬 실행** | 동일 PPTX의 감사·렌더를 읽기 전용 병렬 실행. 파일별 위임을 요청받으면 공통 근거를 공유하고 덱마다 단일 담당자가 제작·QA, 메인이 전달 |
| **도구 캐시** | 저장소 밖 Python·렌더링 도구·폰트 탐색 캐시를 재사용 |
| **중간 산출물 재사용** | `--reuse-render`로 입력·환경·옵션·산출물 해시가 일치하는 전체 렌더 재사용; QA 판단은 항상 새로 검사 |
| **수정 루프 단축** | 결함을 모아 일괄 수정 → 위험 슬라이드 확인 → 변경 시에만 최종 전체 render |
| **측정(선택)** | 성능 비교를 요청받거나 병목을 분석할 때만 단계별 시간·PDF reuse·cache hit·repair cycle을 세션 `metrics.json`에 기록 |

공용 캐시에는 고객 데이터·시크릿·생성 결과를 넣지 않으며, 검증 스크립트와 QA 파일은 세션 작업
폴더에 격리합니다. 최종 산출물 폴더에는 사용자가 요청한 최종 파일만 남깁니다.
여기서 `<session>`은 클라이언트가 제공하는 세션 artifact 경로를 뜻합니다. 그런 경로가 없는
VS Code 환경에서는 저장소와 최종 출력 폴더 밖의 OS 임시 디렉터리를 사용합니다.

### 지침·스킬 변경 검증

```bash
python3 -B -m unittest discover -s .github/skills/web-search/tests -p 'test_skill_policy.py' -q
python3 -B -m unittest discover -s .github/skills/adaptive-presentation/tests -p 'test_presentation_policy.py' -q
```

정책 테스트는 스킬별 경계·길이·트리거·참조 링크와 문서화된 CLI 연결을 검사합니다.
동작 회귀는 각 스킬의 전체 테스트로 확인합니다. authoring schema 검사는 `jsonschema`가 설치되어
있을 때 실행하며, 없으면 skip을 명시합니다. 런타임의 `deck_spec.py` 검증은 이 패키지에 의존하지 않습니다.
모델 성능이나 실제 웹 조사·PPTX 품질을 평가하는 테스트는 아닙니다. 그런 개선은 같은 입력·환경·완료
조건으로 별도 비교해야 하며, 테스트 통과만으로 더 빠르거나 정확해졌다고 주장하지 않습니다.

---

## MCP 서버 (사전 번들 · clone 후 승인하면 동작)

MCP(Model Context Protocol) 서버는 Copilot에 **구조화된 외부 도구 접근**(공식 문서·GitHub 이슈/PR/코드)을
붙여 줍니다. 이 킷은 **[Microsoft Learn MCP](https://learn.microsoft.com/training/support/mcp)를 사전
번들**하며, clone 후 폴더 신뢰 또는 서버 Start를 승인하면 활성화됩니다. 연결 설정만 저장하고 문서 내용은
저장소에 복제하지 않습니다.

범용 최신 웹 검색은 클라이언트가 제공하는 web search capability를 우선 사용하며, 요청·지시된 독립
조사 축에만 `/research`·Research agent를 사용합니다. 이 킷의 `web-search` 스킬은 검색 전략·검증·
Fact Ledger 계약을 맡고 검색 backend 자체는 제공하지 않습니다.

### 번들된 서버

| 서버 | 역할 | 인증 | 어떻게 연결되나 |
|------|------|------|------|
| **GitHub MCP** | 이슈·PR·코드·릴리스 조회/작성 | GitHub 로그인 | **Copilot CLI에 내장** — 설정 불필요 |
| **Microsoft Learn MCP** | `learn.microsoft.com` 공식 문서·코드 샘플 조회 | **불필요 · 무료 공개 엔드포인트** | **리포에 번들** — 클라이언트 승인 후 활성화 |

활성화 확인, 다른 서버 추가, 보안은 [설치·사용 가이드의 MCP 장](SETUP-GUIDE.md#mcp)에서,
Azure 리소스 실습에 필요한 MCP(Azure MCP·Foundry MCP·AKS MCP·Playwright·Computer Use) 연결은
[실습 장](SETUP-GUIDE.md#azure-lab)에서 안내합니다.

---

## 자주 묻는 질문

**Q. 어떤 Copilot 플랜이 필요한가요?**
이 킷은 특정 모델을 요구하지 않습니다. 사용하려는 GitHub Copilot Chat·Agent·CLI 기능을 지원하는 플랜과 최신 클라이언트를 사용하면 됩니다.

**Q. 내 프로젝트에 어떻게 적용하나요?**
지침·스킬은 `.github/`에, VS Code MCP 설정은 `.vscode/mcp.json`에 둡니다. 기존 설정이나 같은
이름의 스킬이 있으면 복사 명령으로 덮어쓰지 말고 내용을 병합하세요.

**Q. 스킬이 동작하지 않아요.**
최신 VS Code + GitHub Copilot Chat의 Agent mode를 사용하고, `SKILL.md`의 `name`이 폴더명과
일치하며 `description`에 트리거 키워드가 있는지 확인하세요.

**Q. 지침이 로드되지 않아요.**
`.github/copilot-instructions.md` 경로가 맞는지, 프로젝트 루트에 `.github/`가 있는지 확인하세요. Copilot CLI도 이 파일을 자동으로 읽습니다.

**Q. MCP 서버는 어떻게 붙이나요?**
Microsoft Learn MCP는 이 킷에 번들되어 폴더 신뢰 또는 Start 승인 후 활성화되고, GitHub MCP는 Copilot CLI에
내장돼 있습니다. 활성화 확인과 서버 추가는 [설치·사용 가이드](SETUP-GUIDE.md#mcp)를, Azure 실습에 필요한
MCP 연결은 [실습 장](SETUP-GUIDE.md#azure-lab)을 따르세요. 범용 최신 웹 검색은 GitHub Copilot의 web search 또는
Research capability를 사용합니다.

---

## 라이선스

[MIT](LICENSE)
