# GitHub Copilot Augment Kit

GitHub Copilot을 특정 모델에 종속되지 않는 **고성능 엔지니어링 에이전트**로 확장하는 경량 커스터마이징 킷입니다. 단일 지침 파일과 온디맨드 스킬, 재사용 가능한 생성 엔진으로 사고·소통·안전·코딩·Git·팩트체크·웹 조사·고객 데모·PPTX 제작 워크플로를 제공합니다.

이 리포의 `.github/` 폴더를 프로젝트에 두면 GitHub Copilot(VS Code Chat·터미널 CLI)이 지침과 스킬을 자동으로 읽습니다. `.vscode/mcp.json`까지 적용하면 VS Code에서도 Microsoft Learn MCP를 사용할 수 있습니다.

> **Augment**는 GitHub Copilot의 역량을 지침·스킬·MCP로 보강한다는 뜻입니다. 특정 모델명은 저장소 정체성에 포함하지 않으며, `/model` 또는 모델 선택기에서 현재 작업에 가장 적합한 모델로 언제든 교체할 수 있습니다.
>
> **현재 검증 기준(2026-07-15)**: 이 버전의 지침·스킬·예제 워크플로는 **GPT-5.6 Sol**로 최종 end-to-end 테스트와 품질 검증을 수행했습니다. GPT-5.6 Sol은 고정 런타임 의존성이 아닙니다. 더 적합한 최신 모델이 제공되면 계속 재검증·업데이트하되, 지침·Skills·MCP 워크플로가 특정 모델에 종속되지 않는 설계 원칙을 유지합니다.

---

## 이게 뭔가요? (3줄 요약)

- **무엇**: GitHub Copilot에 입힐 수 있는 단일 지침 + 전문 스킬 모음입니다.
- **왜**: 기반 모델이 바뀌어도 일관된 품질·안전·전문 워크플로를 유지하도록 Copilot의 실행 방식을 보강합니다.
- **어떻게**: `.github/`를 두면 지침·스킬이 자동 로드되고, 생성 스킬은 고객별 Spec·Design DNA와 검증된 Runtime·Compiler를 조합해 반복 구현 시간을 줄입니다.

---

## 무엇이 들어있나 — 3가지 빌딩 블록

| 블록 | 위치 | 동작 방식 | 내용 |
|------|------|----------|------|
| **Instructions** | `.github/copilot-instructions.md` | 매 대화 **자동 로드** | 페르소나 · 사고 · 소통 · 안전 · 코딩 · Git · MS/GitHub 가치 · 팩트체크 · 출처 |
| **Skills** | `.github/skills/` | 관련 질문 시 **자동 활성화** 또는 `/skill-name` | 실시간 웹·공식 문서 검색 · 고객·산업별 AI 플랫폼 데모 · 적응형 PPTX 생성 |
| **MCP (사전 번들)** | `.github/mcp.json` · `.vscode/mcp.json` | clone 후 신뢰/Start 승인 시 활성화 | Microsoft Learn MCP — 공식 문서·코드 샘플 검색 |

> 상시 적용 원칙은 **단일 파일로 통합**해 중복을 줄이고, 상세 워크플로는 관련 작업에서만 스킬로 불러옵니다.

---

## 5분 빠른 시작

### 1) 먼저 체험해보기

```bash
git clone https://github.com/junwoojeong100/github-copilot-augment-kit.git
cd github-copilot-augment-kit
code .
```

VS Code에서 Copilot Chat을 열고 **모델 선택기(Model Picker)** 에서 작업에 적합한 모델을 선택합니다. 모델이 바뀌어도 동일한 지침과 스킬이 적용됩니다.

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

---

## 어디서 쓸 수 있나 — VS Code & 터미널(CLI)

이 킷은 **VS Code Copilot Chat**과 터미널용 **[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/copilot-cli/about-copilot-cli)** 양쪽에서 동작합니다.

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

### VS Code Chat vs Copilot CLI

| 항목 | VS Code Copilot Chat | GitHub Copilot CLI |
|------|---------------------|-------------------|
| `copilot-instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `skills/` | ✅ 자동 활성화 · `/skill-name` | ✅ 자동 활성화 · `/skill-name` |
| Microsoft Learn MCP | `.vscode/mcp.json`에서 Start | `.github/mcp.json`을 신뢰 후 자동 로드 |

---

## 설계 원칙 — 변동 지식은 최소화하고, 필요할 때 최신 확인

이 킷의 지침·스킬은 주로 **방향(무엇을 다룰지), 형식(어떻게 정리할지), 재사용 가능한
워크플로**를 정의합니다. 서비스명과 예시는 포함하지만, 자주 바뀌는 기능 상태·가격·수치·규제
조항은 가능한 한 고정하지 않습니다.

- **왜?** 클라우드·AI·규제는 빠르게 변합니다. 박제된 내용은 금방 낡고 토큰만 소모합니다.
- **대신** 답변 시점에 공식 문서(`learn.microsoft.com` · `docs.github.com`)와 웹 검색으로 최신 정보를 확인합니다.
- **효과**: 최신성 오류와 유지보수 부담을 줄입니다. 검색 가능 여부와 원문 갱신 시점에 따라 최신성에는 한계가 있을 수 있습니다.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md              # 단일 핵심 지침 (매 대화 자동 로드)
├── mcp.json                             # Microsoft Learn MCP 사전 번들 (CLI 워크스페이스 자동 로드)
└── skills/                              # 전문 스킬 (온디맨드)
    ├── google-web-search/               # 실시간 웹·공식 문서 검색
    │   └── SKILL.md
    ├── ai-platform-demo/                # 고객·산업별 AI 플랫폼 데모(단일 HTML) 생성기
    │   ├── SKILL.md                     # 실시간 리서치→Design DNA→Overlay 합성→검증
    │   ├── runtime/                     # 검증된 SPA shell·CSS·JavaScript Golden Runtime
    │   ├── packs/                       # 디자인·고객 사실을 고정하지 않는 산업별 기본 구조
    │   ├── schema/                      # 고객별 demo-spec JSON Schema
    │   ├── scripts/                     # Overlay Composer·Spec Renderer·브라우저 검증기
    │   ├── tests/                       # Composition·Design DNA gate 회귀 테스트
    │   ├── examples/                    # 전체 Spec·compact Customer Overlay 구조 예제
    │   └── reference/                   # Design DNA·화면 청사진·Runtime·검증 절차
    └── adaptive-presentation/           # 주제·청중별 고품질 PPTX 생성기
        ├── SKILL.md                     # 조사→서사→Design DNA→PPTX→렌더 QA
        ├── pptx_compiler/               # Recipe·components·font metrics·theme-agnostic Compiler
        ├── examples/                    # 동일 Recipe/semantic deck의 Design DNA 변형 예제
        ├── reference/                   # 서사·Design DNA·Recipe·청사진·Compiler 사용법
        └── scripts/                     # 통합 QA Runner·구조 감사·JPEG/contact sheet 렌더링
.vscode/
└── mcp.json                             # VS Code Copilot Agent용 MCP 번들
```

---

## 구성 요소 자세히

### Instructions — `copilot-instructions.md` (자동 적용)

매 대화에 자동 로드되는 단일 지침. 아래 원칙을 압축해 담습니다.

| 섹션 | 핵심 |
|------|------|
| 페르소나 & 사고 | 지적 겸손, 단계적 추론, 불확실성 표기 |
| 커뮤니케이션 | 결론 우선(BLUF), 적응적 소통, 한국어 존댓말+영문 병기 |
| 안전 & 윤리 | 해로운 콘텐츠 거부, PII/시크릿 보호 |
| 코딩 | 가독성·보안(OWASP) 우선, 언어별 베스트 프랙티스 |
| Git 워크플로우 | 영어 커밋, Conventional Commits, PR 규칙 |
| MS/GitHub 가치 | 구체 서비스로 통제·가치 매핑(Foundry·Entra·Purview·Copilot 등) |
| 팩트체크 · 출처 | 답변 끝 사실 검증 표, 출처 명시 |

### Skills — 자연어 또는 `/skill-name`

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트" | 공식 소스 우선 실시간 웹·문서 검색 |
| **ai-platform-demo** | "○○ 고객 △△ 산업 AI 데모 만들어줘", "임원 데모", "운영 대시보드 데모" | 실시간 조사 + Customer Overlay + Industry Pack + Golden Runtime → 실제 동작하는 단일 HTML SaaS 데모(8화면) 생성·전체 QA |
| **adaptive-presentation** | "병원 경영진 대상 의료 AI 전략 PPT 20장", "기술 발표자료 만들어줘", "기존 PPT 재디자인" | 매번 새로운 Design DNA + 재사용 Slide Compiler → 편집 가능한 PPTX 생성·preflight·렌더 QA |

---

## AI 플랫폼 데모 스킬 (`ai-platform-demo`)

고객사 임원 보고·영업용 **"실제로 동작하는" AI 운영 플랫폼 데모를 단일 HTML 하나**로 생성합니다. 슬라이드가 아니라, 임원이 직접 클릭·질문·조작하는 SaaS 앱입니다.

**무엇을 만드나** — 사이드바 + 실시간 대시보드 + 도메인 운영 콘솔 + AI 에이전트 채팅 + 거버넌스 등 **8개 화면 SPA**. 실시간 KPI·스트리밍 차트·움직이는 객체·토스트·멀티에이전트 협업까지 동작합니다.

**사용법** — 자연어로 고객과 산업만 알려주면 됩니다.

```
> 현대제철 대상으로 철강 제조 AI 운영 플랫폼 데모 만들어줘. 청중은 CDO·생산본부장.
```

스킬이 자동 로드되어 ① **매 요청 실시간** 고객·산업 리서치 → ② Storyline·Adaptive Design DNA·8개 화면 계약 →
③ compact `customer-overlay.json` 작성 → ④ Industry Pack과 합성해 Spec·HTML 생성 → ⑤ Puppeteer 전체 QA까지
수행합니다.

```text
실시간 Fact Ledger + Storyline + 고객별 Design DNA
  → Customer Overlay + Industry Pack
  → validated demo-spec.json
  → Golden Runtime (shell.tmpl + runtime.css + runtime.js)
  → 고객별 단일 HTML
  → 8개 화면·전체 인터랙션 브라우저 QA
```

**Golden Runtime은 고정 디자인 템플릿이 아니라 검증된 동작 엔진**입니다. 라우터, timer/listener
정리, 실시간 차트, 시뮬레이터, 에이전트 채팅, HTML escaping, 안정적인 QA ID처럼 고객과 무관한
메커니즘만 재사용합니다. 고객별 브랜드·화면 구성·KPI·공식·에이전트·서사는 Spec과 Design DNA에서
매번 새로 결정하므로 HTML·CSS·JavaScript를 처음부터 다시 쓰는 시간을 줄이면서도 고객별 차별성을
유지합니다.

**Industry Pack도 디자인을 고정하지 않습니다.** Pack은 산업 terminology·KPI 공식·Agent 역할의
출발점만 제공하며 고객명·Storyline·Design DNA를 포함할 수 없습니다. Composer는 Customer Overlay에
전체 `design`이 없거나 실시간 research metadata가 오래됐거나 핵심 고객 path가 빠지면 실패합니다.
따라서 같은 에너지 산업이라도 고객별 palette, light/dark theme, density, shape, chart grammar,
운영 flow와 climax가 달라집니다.

```bash
python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
  --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
  --pack .github/skills/ai-platform-demo/packs/renewable-energy-holdings.pack.json \
  --customer <session>/files/<app>-work/customer-overlay.json \
  --output <session>/files/<app>-work/demo-spec.json \
  --html-output <session>/files/<app>-work/<app>.html
```

적합한 Industry Pack이 없으면 전체 `demo-spec.json`을 직접 작성하는 기존 경로를 사용합니다. 속도를
위해 고객과 맞지 않는 Pack을 사용하지 않으며 최종 8화면 QA는 항상 유지합니다.

| 입력 | 예시 |
|------|------|
| 고객명 / 산업 | "삼표산업 / 레미콘·골재·시멘트" |
| 청중(임원) | "CIO, 재무팀장, CI팀장" |
| 강조 서비스 | Microsoft Foundry · Agent Framework · GitHub Copilot |

> 산출물은 **단일 `.html`**(인라인 CSS/JS, 오프라인 동작). 모든 화면에 `● DEMO DATA` 배지로 시연 데이터임을 명시합니다.

### 개인/팀에 설치

```bash
# 팀 공유 — 같은 이름의 스킬이 없을 때
mkdir -p /path/to/my-project/.github/skills
cp -R github-copilot-augment-kit/.github/skills/ai-platform-demo \
  /path/to/my-project/.github/skills/

# 개인 — 같은 이름의 스킬이 없을 때, 모든 프로젝트에서 사용
mkdir -p ~/.copilot/skills
cp -R .github/skills/ai-platform-demo ~/.copilot/skills/
```

같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 내용을 비교해 병합하세요.

확인: CLI에서 `/skills list` · `/skills info ai-platform-demo` · `/env`.

---

## 적응형 PPT 스킬 (`adaptive-presentation`)

임원 보고, 고객 제안, 제품 소개, 기술 아키텍처, 교육·세미나 등 **다른 주제와 청중에도 같은 품질 기준**으로
실제 `.pptx`를 생성합니다.

핵심은 고정 템플릿이 아닙니다. 매 요청마다 청중·목적·산업의 물성·브랜드·발표 환경에서 다음
**Design DNA**를 먼저 도출합니다.

- Concept words와 시각 은유
- Primary archetype + counter-influence
- 역할 기반 팔레트와 실제 설치 글꼴
- 도형·선·여백·이미지·차트 문법
- 최소 5~8개의 레이아웃 패밀리와 반복 방지 규칙

그 후 ① **매번 실시간 공식 자료 조사**·Fact Ledger → ② 목적별 Storyline과 slide blueprint →
③ 시각 토큰이 없는 `DeckRecipe`로 표준 슬라이드 구조화 → ④ Design DNA를 입력받는
`pptx_compiler`로 편집 가능한 PPTX 생성 → ⑤ 통합 QA Runner의 전체 렌더 및 contact sheet 검수
순으로 진행합니다.

```text
Realtime Fact Ledger + Deck Spec
  → semantic Deck Recipe

Design DNA + Deck Recipe
  → Adaptive Layout Selector + Certified Components
  → reusable Slide Compiler + real Font Metrics
  → 편집 가능한 PPTX
  → 통합 QA Runner(구조 감사 + 전체 렌더 + risk slides)
```

**Slide Compiler도 고정 템플릿이 아닙니다.** PowerPoint 문서 생성, named region 계산, 텍스트·도형·
선·이미지 primitive, 안전 영역, 출처 footer, 레이아웃 반복 검사를 재사용합니다. 기본 팔레트가 없어
매 덱의 Design DNA를 반드시 새로 입력해야 하며, 커버·핵심 아키텍처·시각 은유는 주제에 맞게 별도
구성합니다. 저장 전 preflight가 경계 초과, 최소 글자 크기, 텍스트 overflow, 레이아웃 다양성,
과도한 카드 그리드, 대비 부족을 먼저 차단해 렌더 후 반복 수정을 줄입니다.

**Deck Recipe도 디자인을 고정하지 않습니다.** 결론·정보 관계·source key·component·blueprint intent만
저장하고 HEX, 폰트, 크기, 좌표, 모서리, 그림자를 금지합니다. 같은 Recipe도 Design DNA가 달라지면
palette·typography·spacing·corner·section rhythm이 달라집니다. Resource hierarchy, Agent anatomy,
Security layers, Quality loop 같은 certified component는 관계만 재사용하고 현재 Design DNA role로
렌더링합니다. 커버·핵심 thesis·복잡한 아키텍처·최신 업데이트·close는 custom builder로 직접 설계합니다.

외부 사실 조사는 캐시로 생략하지 않습니다. 이전 Fact Ledger와 URL은 검색 출발점으로만 사용하며,
기능 상태·가격·규제·고객 성과는 발표 요청마다 현재 공식 원문으로 다시 확인합니다.

재생성 Python 스크립트와 QA 파일은 세션 작업 폴더에 격리하며 저장소에는 최종 PPTX만 남깁니다.
독립 조사는 병렬화하고, 동일 PPTX 리비전의 중간 PDF는 SHA-256 검증 후 상세 슬라이드 렌더에
재사용합니다. 수정 후에는 변경 부분을 먼저 확인하되 완료 전 전체 구조 감사와 전체 렌더를 다시
수행합니다.

```text
> 병원 경영진 대상 의료 AI 전략 발표자료 20장 만들어줘.
> 청중은 개발자야. 이벤트 기반 아키텍처를 교육하는 기술 PPT 15장으로 만들어줘.
> 이 기존 PPT는 내용은 유지하고, 투자위원회 대상의 절제된 디자인으로 재구성해줘.
```

결과 디자인은 요청에 따라 editorial, executive, technical blueprint, data observatory, human warmth,
premium precision 등의 방향을 조합하지만 **정해진 색상·커버·카드 스타일을 복제하지 않습니다.**

통합 검증:

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx --out /tmp/deck-work --expected-slides 30 --strict
```

Runner는 구조 감사와 전체 렌더를 병렬 실행하고, 텍스트 밀도·작은 글자·title risk·group·bounds를
점수화해 위험 슬라이드를 자동으로 상세 렌더합니다. 전체 overview와 위험 슬라이드는 사람이 확인하며,
중간 PDF는 동일 PPTX SHA-256 리비전에서만 재사용합니다. `--strict`는 작은 본문 후보와 title risk도
실패 처리하며, 사람이 확인한 의도적 보조 텍스트에만 `--allow-small-text`를 사용합니다.

개인 설치(같은 이름의 스킬이 없을 때):

```bash
mkdir -p ~/.copilot/skills
cp -R .github/skills/adaptive-presentation ~/.copilot/skills/
```

기존 스킬이 있으면 덮어쓰지 말고 내용을 비교해 병합하세요. 설치 후
`/skills info adaptive-presentation`으로 로드 위치를 확인할 수 있습니다.

---

## 생성 시간을 줄이는 공통 실행 구조

두 생성 스킬은 기본적으로 **FULL-OPTIMIZED** 정책을 사용합니다. 조사·스토리라인·디자인·제작·
전체 QA를 생략하는 대신, 재사용 가능한 엔진과 안전한 병렬화·캐시·중간 산출물 재사용으로 중복
작업과 wall-clock time을 줄입니다.

| 최적화 | `ai-platform-demo` | `adaptive-presentation` |
|---|---|---|
| **생성 메커니즘 재사용** | Golden Runtime의 SPA lifecycle·interaction·QA hook 재사용 | Recipe·certified component·Slide Compiler·Font Metrics 재사용 |
| **요청별 변경 surface 축소** | 매번 실시간 조사 후 Industry Pack에는 없는 고객 사실·Design DNA·핵심 route만 Customer Overlay에 작성 | 실시간 Fact Ledger·Deck Recipe·Design DNA·핵심 custom slide만 작성 |
| **안전한 병렬 실행** | 독립 조사와 도구 준비를 병렬화하고 최종 Spec·HTML은 한 에이전트가 소유 | 독립 조사와 도구 준비를 병렬화하고 구조 감사·전체 렌더를 같은 immutable PPTX에서 병렬 실행 |
| **도구 캐시** | 저장소 밖 공용 Puppeteer·Chromium 캐시를 재사용 | 저장소 밖 Python·렌더링 도구·폰트 탐색 캐시를 재사용 |
| **중간 산출물 재사용** | 한 browser/page 세션에서 8개 route와 인터랙션을 연속 검증 | PPTX SHA-256이 같은 리비전에서만 중간 PDF를 상세 렌더에 재사용 |
| **수정 루프 단축** | 결함을 모아 일괄 수정 → 영향 route 확인 → 최종 전체 QA | 실제 font width preflight → 통합 QA Runner → 위험 슬라이드 확인 → 최종 전체 render |
| **측정** | 단계별 시간·cache hit·repair cycle을 세션 `metrics.json`에 기록 | 단계별 시간·PDF reuse·cache hit·repair cycle을 세션 `metrics.json`에 기록 |

공용 캐시에는 고객 데이터·시크릿·생성 결과를 넣지 않으며, 검증 스크립트와 QA 파일은 세션 작업
폴더에 격리합니다. 최종 산출물 폴더에는 사용자가 요청한 `.html` 또는 `.pptx`만 남깁니다.

---

## MCP 서버 (사전 번들 · clone 후 승인하면 동작)

이 킷의 `google-web-search` 스킬이 **범용 웹 검색**을 맡는다면, **MCP(Model Context Protocol) 서버**는 Copilot에 **구조화된 1차 도구 접근**(공식 문서·GitHub 이슈/PR/코드)을 붙여 줍니다. 둘은 상호 보완적입니다 — 스킬은 "어떻게 정리할지", MCP는 "어디서 정확히 가져올지".

이 킷은 **Microsoft Learn MCP를 리포에 사전 번들**합니다. clone하면 설정 파일이 인식되고,
클라이언트에서 폴더 신뢰 또는 서버 Start를 승인하면 활성화됩니다. 연결 설정만 저장하며 문서 내용을
저장소에 복제하지 않습니다.

### 번들된 서버

| 서버 | 역할 | 인증 | 어떻게 연결되나 |
|------|------|------|------|
| **GitHub MCP** | 이슈·PR·코드·릴리스 조회/작성 | GitHub 로그인 | **Copilot CLI에 내장** — 설정 불필요 |
| **Microsoft Learn MCP** | `learn.microsoft.com` 공식 문서·코드 샘플 조회 | **불필요 · 무료 공개 엔드포인트** | **리포에 번들** — 클라이언트 승인 후 활성화 |

### 인식과 활성화

- **Copilot CLI** — 리포의 `.github/mcp.json`을 **워크스페이스 서버**로 자동 로드. 첫 실행 시 폴더 신뢰(trust)에 동의하면 활성화됩니다.
  - 확인: `copilot mcp list` → `Workspace servers: microsoft-learn (http)`
- **VS Code (Copilot Chat · Agent)** — 리포의 `.vscode/mcp.json`을 인식. 파일 상단 **Start** 또는 명령 팔레트 → **MCP: List Servers**로 시작.
  - 확인: Agent 도구 목록에 `microsoft_docs_search` 등이 보이면 정상입니다.

> 별도 서버 설치나 URL 입력은 필요하지 않습니다. GitHub MCP는 Copilot CLI에 내장되어 있고,
> Microsoft Learn MCP 연결은 리포에 번들되어 있습니다. 단, 클라이언트의 신뢰/실행 승인은 필요합니다.

### 다른 MCP 서버 추가 (선택)

- **CLI**: `/mcp add`(대화형) 또는 전역 `~/.copilot/mcp-config.json`(루트 키 `mcpServers`). 관리는 `copilot mcp list` / `/mcp show` / `/mcp disable <이름>`.
- **VS Code**: `.vscode/mcp.json`(루트 키 `servers`).

> **보안**: MCP 서버는 외부 도구를 실행합니다. **신뢰할 수 있는 서버만** 추가하고, 추적되는
> `.github/mcp.json`이나 `.vscode/mcp.json`에 리터럴 키를 저장하지 마세요. 클라이언트가 지원하는
> 환경변수/secret/input 치환 또는 사용자 전역 설정을 사용하고, 구체 문법은 해당 클라이언트의
> 공식 문서를 따르세요.

---

## 자주 묻는 질문

**Q. 어떤 Copilot 플랜이 필요한가요?**
이 킷은 특정 모델을 요구하지 않습니다. 사용하려는 GitHub Copilot Chat·Agent·CLI 기능을 지원하는 플랜과 최신 클라이언트를 사용하면 됩니다.

**Q. 내 프로젝트에 어떻게 적용하나요?**
지침·스킬은 `.github/`에, VS Code MCP 설정은 `.vscode/mcp.json`에 둡니다. 기존 설정이나 같은
이름의 스킬이 있으면 복사 명령으로 덮어쓰지 말고 내용을 병합하세요.

**Q. 스킬이 동작하지 않아요.**
최신 VS Code + GitHub Copilot Chat을 사용하고, `SKILL.md`의 `name`이 폴더명과 일치하며 `description`에 트리거 키워드가 있는지 확인하세요.

**Q. 지침이 로드되지 않아요.**
`.github/copilot-instructions.md` 경로가 맞는지, 프로젝트 루트에 `.github/`가 있는지 확인하세요. Copilot CLI도 이 파일을 자동으로 읽습니다.

**Q. MCP 서버는 어떻게 붙이나요?**
**이미 사전 번들**되어 별도 서버 설치가 필요하지 않습니다. Microsoft Learn MCP 설정은 CLI의
`.github/mcp.json`과 VS Code의 `.vscode/mcp.json`에 있으며, 폴더 신뢰 또는 Start 승인 후
활성화됩니다. GitHub MCP는 Copilot CLI에 내장돼 있습니다.

---

## 라이선스

[MIT](LICENSE)
