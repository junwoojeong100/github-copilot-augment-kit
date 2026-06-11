# Copilot × Claude Kit

GitHub Copilot을 **Claude AI + Claude Code**처럼 쓰기 위한 **커스터마이징 킷**입니다. 페르소나·코딩·안전 지침에 더해 Azure 아키텍처·AI/AX 전략·경쟁 분석·웹 검색·슬라이드 생성 등 전문 스킬을 제공합니다.

> **Microsoft FTE를 위한 프로젝트**: Microsoft 정직원(FTE)에게 무료 제공되는 **GitHub Copilot Business** 라이선스로, **별도 Anthropic 구독 없이** Claude Sonnet · Claude Opus 등의 모델을 VS Code Copilot Chat에서 사용할 수 있습니다.

이 리포지토리는 여기에 **커스텀 인스트럭션을 추가**하여, 페르소나·코딩 스타일·보안 규칙과 Azure/GitHub 전문 스킬까지 갖춘 코딩 어시스턴트로 만들어 줍니다.

> **목표**: GitHub Copilot을 **Claude AI + Claude Code**처럼 사용하는 것. Anthropic 유료 구독 없이도, Copilot의 Claude 모델 + 커스텀 인스트럭션 조합으로 동일한 경험을 구현합니다.

## 왜 이 리포가 필요한가?

| 구성 요소 | 설명 |
|-----------|------|
| **GitHub Copilot Business** (MS FTE 무료) | Claude 모델 접근 권한 제공 |
| **VS Code Model Picker** | Copilot Chat에서 Claude Opus/Sonnet 모델 선택 |
| **GitHub Copilot CLI** | 터미널에서 직접 AI 에이전트와 대화하며 코딩 |
| **이 리포의 Custom Instructions** | 페르소나·코딩·안전 지침 + Azure·AI/AX 전략·슬라이드 생성 등 전문 스킬 |

→ 결과: **VS Code와 터미널 모두에서 무료로 Claude AI + Azure 전문가 경험**을 얻을 수 있습니다.

---

## 설계 원칙 — 지식은 박제하지 않고, 실시간 최신화

이 킷의 **instructions · skills · references는 "방향(무엇을 다룰지)과 형식(어떻게 정리할지)"만 정의**하고, 구체적 사실(서비스 기능·SKU·가격·수치·규제 조항·비교 데이터)은 **의도적으로 담지 않습니다.**

- **왜?** 클라우드·AI·규제는 매우 빠르게 변합니다. 박제된 내용은 금방 낡고, 토큰만 소모합니다.
- **대신** 답변이 필요할 때마다 `microsoft_docs_search`/`microsoft_docs_fetch`(MS Learn) · `docs.github.com` · `google-web-search`(공식 1차 소스)로 **최신 내용을 가져와** 정리합니다.
- **효과**: 항상 최신 기반 답변 + 토큰 절약 + 유지보수 최소화.

> 그래서 `references/` 파일을 열면 **조사 축 · 표의 헤더(형식) · 공식 소스 링크**만 보이고 구체 데이터 셀은 비어 있습니다 — 이는 의도된 설계입니다. 내용은 실행 시점에 채워집니다.

---

## 빠른 시작

### 1. 리포지토리 클론

```bash
git clone https://github.com/junwoojeong100/copilot-claude-kit.git
cd copilot-claude-kit
```

### 2. VS Code로 열기

```bash
code .
```

### 3. Claude 모델 선택

VS Code에서 Copilot Chat 패널을 열고, 하단의 **모델 선택기(Model Picker)** 에서 `Claude Sonnet` 또는 `Claude Opus`를 선택합니다.

### 4. 바로 사용

별도 설정 없이 Copilot Chat에서 대화하면 모든 지침이 자동으로 적용됩니다.

- **일반 대화**: `copilot-instructions.md` + `instructions/` 자동 적용
- **코드 작업**: `instructions/` 파일이 패턴 매칭으로 자동 로드
- **프롬프트 템플릿**: `prompts/` 파일을 VS Code 프롬프트 선택기에서 선택
- **전문 스킬**: 관련 질문 시 자동 활성화

---

## GitHub Copilot CLI에서도 사용하기

이 리포의 커스텀 인스트럭션은 **VS Code Copilot Chat뿐 아니라 터미널 기반 [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)에서도 자동 적용**됩니다.

> **Copilot CLI란?** GitHub Copilot의 에이전트 기능을 터미널에서 사용할 수 있는 CLI 도구입니다. 코드 편집, 디버깅, 리팩토링, Git 작업 등을 자연어로 요청할 수 있으며, 실행 전 모든 액션을 미리 확인할 수 있습니다.

### 설치

**macOS / Linux** (Install Script):

```bash
curl -fsSL https://gh.io/copilot-install | bash
```

**macOS / Linux** (Homebrew):

```bash
brew install copilot-cli
```

**Windows** (WinGet):

```bash
winget install GitHub.Copilot
```

**크로스 플랫폼** (npm):

```bash
npm install -g @github/copilot
```

### 사용법

```bash
# 이 리포 디렉토리에서 실행
cd copilot-claude-kit
copilot
```

첫 실행 시 `/login` 명령으로 GitHub 인증을 진행합니다. 이후 자연어로 대화하며 코딩할 수 있습니다.

**주요 명령어:**

| 명령어 | 설명 |
|--------|------|
| `/model` | AI 모델 선택 (Claude Sonnet, Claude Opus, GPT 등) |
| `/diff` | 현재 디렉토리 변경사항 리뷰 |
| `/pr` | 현재 브랜치의 PR 작업 |
| `/plan` | 코딩 전 구현 계획 수립 |
| `/research` | GitHub 검색 + 웹 소스로 심층 조사 |
| `/compact` | 대화 히스토리 요약으로 컨텍스트 절약 |
| `/help` | 전체 명령어 목록 보기 |

### 이 리포와의 관계

Copilot CLI는 다음 경로의 인스트럭션 파일을 **자동으로 읽습니다**:

- `.github/copilot-instructions.md`
- `.github/instructions/**/*.instructions.md`

따라서 이 리포를 클론한 디렉토리에서 `copilot` 명령을 실행하면, **persona, thinking, communication, safety, coding, git-workflow 지침이 모두 자동 적용**됩니다.

### VS Code Chat vs Copilot CLI 비교

| 항목 | VS Code Copilot Chat | GitHub Copilot CLI |
|------|---------------------|-------------------|
| **환경** | VS Code GUI | 터미널 |
| **copilot-instructions.md** | ✅ 자동 적용 | ✅ 자동 적용 |
| **instructions/*.instructions.md** | ✅ 자동 적용 | ✅ 자동 적용 |
| **prompts/ (프롬프트 템플릿)** | ✅ 프롬프트 선택기에서 사용 | ⚠️ `@`로 파일 직접 참조 가능 |
| **skills/ (전문 스킬)** | ✅ SKILL.md 기반 자동 활성화 | ⚠️ `/skills` 명령 (MCP 기반, 별도 구조) |
| **agents/ (커스텀 에이전트)** | ✅ .agent.md 기반 선택기 | ⚠️ `/agent` 명령 + `AGENTS.md` (별도 구조) |
| **MCP 서버 확장** | ✅ 지원 | ✅ 지원 |
| **파일 편집** | IDE 내 직접 편집 | 에이전트가 파일 수정 (승인 후) |
| **Git 작업** | 확장 기능 연동 | `/diff`, `/pr` 등 내장 명령 |

> **요약**: `instructions/`와 `copilot-instructions.md`는 **두 환경 모두에서 동일하게 적용**됩니다. `skills/`와 `agents/`는 두 환경 모두 지원하지만 **파일 형식과 동작 방식이 다릅니다** (VS Code: SKILL.md/.agent.md, CLI: MCP 기반 /skills + AGENTS.md). `prompts/`는 VS Code에서는 프롬프트 선택기로 사용하고, CLI에서는 `@` 명령으로 파일을 직접 참조하여 활용할 수 있습니다.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md                          # 핵심 지침 (매 대화 자동 로드)
│
├── agents/                                           # 커스텀 에이전트 (온디맨드)
│   ├── instruction-reviewer.agent.md                # 커스터마이징 파일 품질 점검
│   └── skill-scaffolder.agent.md                    # 새 스킬 표준 구조 생성
│
├── instructions/                                     # 자동 적용 지침 (applyTo 패턴)
│   ├── coding.instructions.md                       # 코드 품질·보안·스타일
│   ├── safety.instructions.md                       # 안전·윤리 가이드라인
│   ├── persona.instructions.md                      # AI 페르소나 정의
│   ├── thinking.instructions.md                     # 사고방식·추론 프로세스
│   ├── communication.instructions.md                # 커뮤니케이션 스타일
│   └── git-workflow.instructions.md                 # Git 커밋·브랜치·PR 규칙
│
├── prompts/                                          # 재사용 프롬프트 (온디맨드)
│   ├── code-review.prompt.md                        # 코드 리뷰 요청
│   ├── debug.prompt.md                              # 버그 디버깅
│   ├── architecture.prompt.md                       # 아키텍처 설계
│   ├── explain.prompt.md                            # 학습/설명 요청
│   └── refactor.prompt.md                           # 리팩토링 요청
│
└── skills/                                           # 전문 스킬 (온디맨드)
    ├── azure-architecture-review/                   # Azure 아키텍처 설계 & WAF 리뷰
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── architecture-patterns.md
    │   │   ├── service-selection-guide.md
    │   │   └── waf-review-checklist.md
    │   └── assets/
    │       └── review-report-template.md
    │
    ├── azure-support-guide/                         # Azure 사용법 안내 & 트러블슈팅
    │   ├── SKILL.md
    │   └── references/
    │       ├── troubleshooting-flowchart.md
    │       ├── common-issues.md
    │       └── best-practices-by-service.md
    │
    ├── cloud-competitive-analysis/                  # Azure/GitHub 경쟁사 비교 분석
    │   ├── SKILL.md
    │   └── references/
    │       ├── azure-vs-aws-gcp.md
    │       ├── github-vs-competitors.md
    │       ├── github-services-overview.md
    │       ├── foundry-vs-competitors.md
    │       ├── copilot-vs-claude-code.md
    │       └── service-mapping.md
    │
    ├── fact-check/                                  # 모든 답변 팩트체크 (항상 적용)
    │   └── SKILL.md
    │
    ├── foundry-agent-project/                       # Foundry 에이전트 프로젝트 생성
    │   └── SKILL.md
    │
    ├── google-web-search/                           # 동적 소스 선택 기반 웹 검색
    │   └── SKILL.md
    │
    ├── it-ai-strategy-advisory/                     # IT·AI·AX 전략 자문
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── strategy-frameworks.md
    │   │   ├── microsoft-solution-mapping.md
    │   │   └── governance-and-regulation.md
    │   └── assets/
    │       └── strategy-report-template.md
    │
    └── slide-generator/                             # 가독성 높은 PPT 슬라이드 생성
        ├── SKILL.md
        ├── references/
        │   └── slide-design-guide.md
        └── assets/
            ├── slide_builder.py
            ├── requirements.txt
            ├── sample_deck.json
            └── sample_deck.pptx
```

---

## 구성 요소 설명

### `copilot-instructions.md` — 핵심 지침

Copilot이 **매 대화마다** 자동으로 읽는 파일입니다.  
정직성, 깊이 있는 사고, 안전 우선 등 핵심 원칙과 전체 파일 구조 참조를 포함합니다.

### `agents/` — 커스텀 에이전트

특정 워크플로우에 특화된 에이전트입니다. Chat에서 `@` 또는 에이전트 선택기로 호출합니다.

| 에이전트 | 도구 | 설명 |
|----------|------|------|
| `instruction-reviewer` | 읽기, 검색 | instructions/prompts/skills 파일의 품질·일관성·중복을 점검하고 보고서 제공 |
| `skill-scaffolder` | 읽기, 편집, 검색, 에이전트 | 새 스킬을 표준 디렉토리 구조로 생성 (instruction-reviewer 연동) |

### `instructions/` — 자동 적용 지침

| 파일 | 적용 범위 | 설명 |
|------|----------|------|
| `coding` | 코드·설정 파일 | 가독성 우선, 언어별 베스트 프랙티스 |
| `safety` | 모든 파일 | OWASP Top 10 대응, 보안 코딩, 윤리적 AI 사용 |
| `persona` | 모든 파일 | 지적 겸손, 호기심, 균형 잡힌 시각 등 AI 성격 |
| `thinking` | 모든 파일 | 단계적 사고, 불확실성 인정, 메타인지 |
| `communication` | 모든 파일 | 결론 우선, 적응적 소통, 톤 가이드라인 |
| `git-workflow` | 모든 파일 | 영어 커밋 메시지, 브랜치 전략, `main` 대상 PR 생성 |

> **적용 범위 상세**: `coding`은 `*.{py,js,ts,jsx,tsx,java,cs,go,...}` 등 주요 코드·설정 파일에 적용되고, 나머지는 모든 파일(`**`)에 적용됩니다.

> `.instructions.md` 파일은 `applyTo` 프론트매터 패턴에 매칭되는 파일을 열거나 편집할 때 자동으로 Copilot 컨텍스트에 추가됩니다.

### `prompts/` — 재사용 프롬프트

VS Code 프롬프트 선택기(📎 → Prompt)에서 선택하여 사용하는 템플릿입니다.

| 프롬프트 | 역할 | 사용 예시 |
|---------|------|----------|
| `code-review` | 보안·성능·가독성 관점 코드 리뷰 | 현재 파일의 코드 품질 점검 |
| `debug` | 증상 파악 → 근본 원인 분석 | 에러 메시지와 함께 원인 추적 |
| `architecture` | 요구사항 → 트레이드오프 → 추천 | 시스템 설계 방향 결정 |
| `explain` | 사용자 수준에 맞춤 개념 설명 | 코드나 개념을 쉽게 이해 |
| `refactor` | 기존 동작 유지하며 품질 개선 | 복잡한 코드 정리 |

### `skills/` — 전문 스킬

슬래시 명령(`/`) 또는 관련 키워드 질문 시 자동 활성화되는 온디맨드 워크플로우입니다.

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **azure-architecture-review** | "Azure 아키텍처 설계해줘", "WAF 리뷰" | 아키텍처 설계 + Mermaid 다이어그램 + WAF 5 Pillar 평가 보고서 |
| **azure-support-guide** | "App Service 502 에러", "Azure 사용법" | 체계적 트러블슈팅 + 서비스별 Best Practices + 서비스 비교 |
| **cloud-competitive-analysis** | "Azure vs AWS", "Copilot vs Claude Code" | 서비스 매핑 + 기능/가격 비교 + Microsoft 차별화 포인트 |
| **fact-check** | 모든 답변에 자동 적용 | 답변 내 사실적 주장 검증 + 신뢰도 표시 |
| **foundry-agent-project** | "Foundry 에이전트 만들어줘", "Agent Framework 프로젝트" | Microsoft Foundry + Agent Framework 기반 커스텀 에이전트 프로젝트 생성 |
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트", "web search" | 동적 소스 선택 기반 웹 검색 + 출처 기반 요약 |
| **it-ai-strategy-advisory** | "AI 도입 전략 세워줘", "클라우드 전략", "AX 전략" | 현황 진단 → 옵션 → 솔루션 매핑 → 로드맵 → 거버넌스/규제 → ROI 전략 보고서 |
| **slide-generator** | "이 내용으로 PPT 만들어줘", "발표자료", "슬라이드 deck" | 정리된 콘텐츠를 가독성 높은 `.pptx`로 생성 (python-pptx 기반). title·bullets·cards·kpi·timeline·table·**architecture(레이어 다이어그램)**·**process(플로우)**·callout(다크 강조)·closing 등 다양한 슬라이드 타입 |

> **검색 소스 정책**: `google-web-search` 스킬은 **고정 허용목록 대신 동적 소스 선택 정책**을 사용합니다.
> - 질문 주제에 맞는 **가장 권위 있는 1차 출처를 그때그때 탐색·검증**하여 사용합니다 (기관 도메인 변경·신규 주제에 유연하게 대응).
> - **신뢰도 평가 기준**: 1차성(공식·관할 주체) · 권위 · 검증가능성 · 최신성 · 교차검증.
> - **우선순위**: ① 1차 출처(공식 문서·법령 원문·규제기관) → ② 공신력 있는 2차(표준기구·분석기관·학술·주요 언론) → ③ 커뮤니티(교차검증 필수).
> - **자주 쓰는 앵커(예시, 비한정)**: Microsoft/Azure/GitHub 공식, 주요 AI 벤더, 글로벌·국내 규제기관(EU·NIST·ISO, `law.go.kr`·`pipc.go.kr`·`kisa.or.kr`·`fsc.go.kr`·`fss.or.kr`·`motie.go.kr` 등), 전략·분석기관.
> - 작성 주체·날짜 불명 블로그, SEO 스팸·콘텐츠팜 등 신뢰도 미달 소스는 사용하지 않습니다.

---

## 사용법

### Instructions — 자동 적용

**별도 조작 없이 자동으로 동작합니다.** `.github/instructions/` 의 지침 파일들은 `applyTo` 패턴에 매칭되는 파일을 열거나 편집할 때 Copilot 컨텍스트에 자동 로드됩니다.

- 코드 파일(`.py`, `.ts`, `.java` 등)을 열면 → `coding` 지침 자동 적용
- 어떤 파일이든 열면 → `persona`, `thinking`, `communication`, `safety` 지침 자동 적용

> 사용자가 직접 호출할 필요가 없습니다. Copilot이 알아서 적용합니다.

### Prompts — 프롬프트 선택기

1. Copilot Chat 입력창의 📎 (Attach) 버튼을 클릭합니다.
2. **Prompt...** 항목을 선택하면 사용 가능한 프롬프트 목록이 표시됩니다.
3. 원하는 프롬프트를 선택하고, 입력창에 질문이나 요청을 입력해 전송합니다.

```
📎 → Prompt → code-review 선택 → "이 파일 봐줘"
📎 → Prompt → debug 선택 → "TypeError: Cannot read property 'map' of undefined"
📎 → Prompt → architecture 선택 → "실시간 알림 시스템을 설계하고 싶어"
📎 → Prompt → refactor 선택 → "이 함수가 너무 길어"
📎 → Prompt → explain 선택 → "이 코드가 뭘 하는 건지 설명해줘"
```

> **참고**: 프롬프트 내용은 입력창에 텍스트로 나타나지 않습니다. Copilot이 배후에서 프롬프트 지침과 사용자 입력을 합쳐서 처리합니다.

### Skills — 슬래시 명령 또는 자연어

**방법 1: 슬래시 명령**

Copilot Chat에서 `/`를 입력하면 사용 가능한 스킬 목록이 표시됩니다.

```
/azure-architecture-review 전자상거래 플랫폼 아키텍처를 설계해줘
/azure-support-guide Container Apps에서 502 에러가 발생합니다
/cloud-competitive-analysis Azure Functions vs AWS Lambda 비교해줘
/google-web-search React 최신 버전과 변경사항 알려줘
/it-ai-strategy-advisory 제조업 고객의 생성형 AI 도입 전략을 세워줘
/slide-generator 위 비교 내용을 고객 발표용 슬라이드로 만들어줘
```

**방법 2: 자연어 질문 (자동 활성화)**

스킬의 `description`에 포함된 키워드로 질문하면 자동으로 해당 스킬이 로드됩니다.

```
"Azure 아키텍처 리뷰해줘"              → azure-architecture-review 활성화
"Redis 연결이 끊기는데 어떻게 해야 해?"  → azure-support-guide 활성화
"GitHub vs GitLab 비교해줘"            → cloud-competitive-analysis 활성화
"Foundry vs Bedrock 차이가 뭐야?"      → cloud-competitive-analysis 활성화
"Python 3.13 최신 변경사항 알려줘"       → google-web-search 활성화
"Azure 최근 업데이트가 뭐야?"            → google-web-search 활성화
"우리 회사 AI 전환 전략 도와줘"          → it-ai-strategy-advisory 활성화
"클라우드 도입 로드맵 짜줘"              → it-ai-strategy-advisory 활성화
"이 아키텍처 리뷰를 발표자료로 만들어줘"   → slide-generator 활성화
```

### Agents — 에이전트 선택기

Copilot Chat 상단의 에이전트 선택기에서 원하는 에이전트를 선택하거나, `@`로 호출합니다.

```
에이전트 선택기 → instruction-reviewer → "현재 instructions 파일들 점검해줘"
에이전트 선택기 → skill-scaffolder → "azure-monitoring 스킬을 만들어줘"
```

> 에이전트는 허용된 도구만 사용할 수 있어, 일반 Copilot Chat보다 **제한된 범위에서 안전하게** 동작합니다.

---

## 자주 묻는 질문

### Q: 이 프로젝트를 내 리포에 적용하려면?

`.github/` 폴더 전체를 원하는 프로젝트의 루트에 복사하면 됩니다.  
Copilot이 자동으로 `copilot-instructions.md`를 인식합니다.

### Q: references 파일이 거의 비어 있어요. 정상인가요?

네, **의도된 설계**입니다. 이 킷은 지식을 박제하지 않습니다. `references/`는 "무엇을 조사하고 어떤 형식으로 정리할지"(방향·형식)만 담고, 구체 내용은 답변 시점에 MS Learn · GitHub Docs · 웹 검색으로 최신화합니다. 자세한 이유는 위 [설계 원칙](#설계-원칙--지식은-박제하지-않고-실시간-최신화)을 참고하세요.

### Q: 스킬이 동작하지 않습니다

- VS Code Insiders + GitHub Copilot Chat 최신 버전이 필요합니다.
- `SKILL.md`의 `name` 필드가 폴더명과 일치하는지 확인하세요.
- `description`에 트리거 키워드가 포함되어 있는지 확인하세요.

### Q: instructions 파일이 로드되지 않습니다

- 파일 확장자가 `.instructions.md`인지 확인하세요.
- `applyTo` 패턴이 올바른 glob 형식인지 확인하세요.
- `.github/instructions/` 경로에 위치하는지 확인하세요.

### Q: 기존 copilot-instructions.md와 충돌하나요?

`copilot-instructions.md`는 프로젝트당 하나만 인식됩니다. 기존 파일이 있다면 내용을 병합하세요.

### Q: Copilot CLI에서도 이 커스텀 인스트럭션이 적용되나요?

네. Copilot CLI는 `.github/copilot-instructions.md`와 `.github/instructions/**/*.instructions.md`를 자동으로 읽습니다. 이 리포를 클론한 디렉토리에서 `copilot` 명령을 실행하면 persona, thinking, communication, safety, coding, git-workflow 지침이 모두 적용됩니다. `skills/`와 `agents/`는 CLI에서도 지원하지만 파일 형식이 다르고(CLI는 MCP 기반 `/skills` + `AGENTS.md`), `prompts/`는 CLI에서 `@` 명령으로 파일을 직접 참조하여 활용할 수 있습니다.

---

## 라이선스

MIT
