# Copilot × Claude Kit

GitHub Copilot을 **Claude AI + Claude Code**처럼 쓰기 위한 **커스터마이징 킷**입니다. 페르소나·코딩·안전 지침에 더해 Azure 아키텍처·AI/AX 전략·경쟁 분석·웹 검색·슬라이드 생성 같은 전문 스킬을 제공합니다.

이 리포의 `.github/` 폴더를 프로젝트에 두면, GitHub Copilot(VS Code Chat·터미널 CLI)이 자동으로 읽어 **더 일관되고 똑똑한 어시스턴트**가 됩니다.

> 별도 Anthropic 구독 없이, **GitHub Copilot이 제공하는 Claude 모델**(Sonnet · Opus 등)을 그대로 활용합니다. 모델 가용성은 Copilot 플랜·조직 정책에 따라 다를 수 있으며, **모델 선택기에 Claude가 보이면** 이 킷을 바로 쓸 수 있습니다.

---

## 이게 뭔가요? (3줄 요약)

- **무엇**: GitHub Copilot에 입힐 수 있는 지침·프롬프트·스킬·에이전트 모음입니다.
- **왜**: Copilot의 Claude 모델 위에 일관된 페르소나·코딩 규칙·전문 워크플로를 얹어 **Claude AI + Claude Code 같은 경험**을 만듭니다.
- **어떻게**: `.github/` 폴더만 있으면 Copilot이 자동으로 읽습니다. 별도 설치·설정이 거의 없습니다.

---

## 무엇이 들어있나 — 4가지 빌딩 블록

| 블록 | 폴더 | 동작 방식 | 예시 |
|------|------|----------|------|
| **Instructions** | `instructions/` | 파일을 열면 **자동 적용** | 페르소나, 사고방식, 소통, 안전, 코딩, Git 워크플로 |
| **Prompts** | `prompts/` | 프롬프트 선택기에서 **골라 사용** | 코드 리뷰, 디버그, 아키텍처, 설명, 리팩터링 |
| **Skills** | `skills/` | 관련 질문 시 **자동 활성화**(또는 `/명령`) | Azure 설계·지원, 경쟁 분석, AI/AX 전략, 웹 검색, 슬라이드 생성 |
| **Agents** | `agents/` | 에이전트 선택기에서 **호출** | 지침 품질 점검, 새 스킬 생성 |

> Instructions는 항상 배경에서 동작하고, Prompts·Skills·Agents는 필요할 때만 불러 씁니다.

---

## 5분 빠른 시작

### 1) 먼저 체험해보기

```bash
git clone https://github.com/junwoojeong100/copilot-claude-kit.git
cd copilot-claude-kit
code .
```

VS Code에서 Copilot Chat을 열고, 하단 **모델 선택기(Model Picker)** 에서 `Claude Sonnet` 또는 `Claude Opus`를 선택합니다. 이제 그냥 대화하면 모든 지침이 자동 적용됩니다.

### 2) 내 프로젝트에 적용하기

이 리포의 **`.github/` 폴더를 내 프로젝트 루트에 복사**하면 끝입니다. Copilot이 `copilot-instructions.md`와 `instructions/`를 자동 인식합니다.

```bash
cp -r copilot-claude-kit/.github /path/to/my-project/
```

> 이미 `copilot-instructions.md`가 있다면 내용을 병합하세요(프로젝트당 하나만 인식됩니다).

---

## 어디서 쓸 수 있나 — VS Code & 터미널(CLI)

이 킷은 **VS Code Copilot Chat**과 터미널용 **[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)** 양쪽에서 동작합니다.

### Copilot CLI 설치

```bash
# macOS / Linux (스크립트)
curl -fsSL https://gh.io/copilot-install | bash

# macOS / Linux (Homebrew)
brew install copilot-cli

# Windows (WinGet)
winget install GitHub.Copilot

# 크로스 플랫폼 (npm)
npm install -g @github/copilot
```

설치 후 리포 디렉토리에서 `copilot`을 실행하고, 첫 실행 시 `/login`으로 인증합니다.

**자주 쓰는 CLI 명령**

| 명령 | 설명 |
|------|------|
| `/model` | AI 모델 선택 (Claude Sonnet/Opus 등) |
| `/diff` | 변경사항 리뷰 |
| `/pr` | 현재 브랜치의 PR 작업 |
| `/plan` | 구현 계획 수립 |
| `/research` | GitHub + 웹 심층 조사 |
| `/help` | 전체 명령 보기 |

### VS Code Chat vs Copilot CLI

| 항목 | VS Code Copilot Chat | GitHub Copilot CLI |
|------|---------------------|-------------------|
| `copilot-instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `instructions/*.instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `prompts/` | ✅ 프롬프트 선택기 | ⚠️ `@`로 파일 직접 참조 |
| `skills/` | ✅ SKILL.md 자동 활성화 | ⚠️ `/skills`(MCP 기반) |
| `agents/` | ✅ `.agent.md` 선택기 | ⚠️ `/agent` + `AGENTS.md` |

> **요약**: `instructions/`와 `copilot-instructions.md`는 두 환경에서 동일하게 적용됩니다. `skills/`·`agents/`는 양쪽 모두 지원하지만 형식이 다르고, `prompts/`는 CLI에서 `@`로 참조합니다.

---

## 설계 원칙 — 지식은 박제하지 않고, 실시간 최신화

이 킷의 **instructions · skills · references는 "방향(무엇을 다룰지)과 형식(어떻게 정리할지)"만 정의**하고, 구체적 사실(서비스 기능·가격·수치·규제 조항·비교 데이터)은 **의도적으로 담지 않습니다.**

- **왜?** 클라우드·AI·규제는 매우 빠르게 변합니다. 박제된 내용은 금방 낡고, 토큰만 소모합니다.
- **대신** 답변 시점에 `microsoft_docs_search`(MS Learn) · `docs.github.com` · 웹 검색으로 **최신 내용을 가져와** 정리합니다.
- **효과**: 항상 최신 기반 답변 + 토큰 절약 + 유지보수 최소화.

> 그래서 `references/` 파일을 열면 **조사 축 · 표 헤더(형식) · 공식 소스 링크**만 보이고 구체 데이터는 비어 있습니다 — 의도된 설계입니다.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md            # 핵심 지침 (매 대화 자동 로드)
│
├── agents/                            # 커스텀 에이전트 (온디맨드)
│   ├── instruction-reviewer.agent.md  # 커스터마이징 파일 품질 점검
│   └── skill-scaffolder.agent.md      # 새 스킬 표준 구조 생성
│
├── instructions/                      # 자동 적용 지침 (applyTo 패턴)
│   ├── coding.instructions.md         # 코드 품질·보안·스타일
│   ├── safety.instructions.md         # 안전·윤리
│   ├── persona.instructions.md        # AI 페르소나
│   ├── thinking.instructions.md       # 사고방식·추론
│   ├── communication.instructions.md  # 커뮤니케이션 스타일
│   └── git-workflow.instructions.md   # 커밋·브랜치·PR 규칙
│
├── prompts/                           # 재사용 프롬프트 (온디맨드)
│   ├── code-review.prompt.md
│   ├── debug.prompt.md
│   ├── architecture.prompt.md
│   ├── explain.prompt.md
│   └── refactor.prompt.md
│
└── skills/                            # 전문 스킬 (온디맨드)
    ├── azure-architecture-review/     # Azure 설계 & WAF 리뷰
    ├── azure-support-guide/           # Azure 사용법 & 트러블슈팅
    ├── cloud-competitive-analysis/    # Azure/GitHub 경쟁 비교
    ├── fact-check/                    # 답변 팩트체크 (항상 적용)
    ├── foundry-agent-project/         # Foundry 에이전트 프로젝트
    ├── google-web-search/             # 실시간 웹 검색
    ├── it-ai-strategy-advisory/       # IT·AI·AX 전략 자문
    └── slide-generator/               # 가독성 높은 PPT 생성
```

---

## 구성 요소 자세히

### Instructions — 자동 적용 (조작 불필요)

`applyTo` 패턴에 맞는 파일을 열거나 편집하면 자동으로 Copilot 컨텍스트에 로드됩니다.

| 파일 | 적용 범위 | 핵심 |
|------|----------|------|
| `coding` | 코드·설정 파일 | 가독성 우선, 언어별 베스트 프랙티스 |
| `safety` | 모든 파일 | OWASP 대응, 보안 코딩, 윤리 |
| `persona` | 모든 파일 | 지적 겸손, 호기심, 균형 |
| `thinking` | 모든 파일 | 단계적 사고, 불확실성 인정 |
| `communication` | 모든 파일 | 결론 우선, 적응적 소통 |
| `git-workflow` | 모든 파일 | 영어 커밋, 브랜치 전략, PR 생성 |

### Prompts — 프롬프트 선택기에서 선택

VS Code Chat 입력창의 📎 → **Prompt** 에서 선택합니다.

| 프롬프트 | 역할 |
|---------|------|
| `code-review` | 보안·성능·가독성 관점 리뷰 |
| `debug` | 증상 → 근본 원인 분석 |
| `architecture` | 요구사항 → 트레이드오프 → 추천 |
| `explain` | 수준에 맞춘 개념 설명 |
| `refactor` | 동작 유지하며 품질 개선 |

### Skills — 자연어 또는 `/명령`

관련 키워드로 질문하면 자동 활성화되고, `/`로 직접 호출할 수도 있습니다.

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **azure-architecture-review** | "Azure 아키텍처 설계해줘", "WAF 리뷰" | 설계 + 다이어그램 + WAF 5 Pillar 평가 |
| **azure-support-guide** | "App Service 502 에러", "Azure 사용법" | 체계적 트러블슈팅 + 모범 사례 |
| **cloud-competitive-analysis** | "Azure vs AWS", "Copilot vs Claude Code" | 서비스 매핑 + 비교 + 차별화 포인트 |
| **fact-check** | (모든 답변에 자동) | 사실 주장 검증 + 신뢰도 표시 |
| **foundry-agent-project** | "Foundry 에이전트 만들어줘" | Foundry + Agent Framework 프로젝트 생성 |
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트" | 공식 소스 우선 실시간 웹 검색 |
| **it-ai-strategy-advisory** | "AI 도입 전략", "클라우드/AX 전략" | 진단 → 옵션 → 로드맵 → 거버넌스 → ROI |
| **slide-generator** | "이 내용으로 PPT 만들어줘" | `.pptx` 생성 (아키텍처 다이어그램·프로세스 플로우·KPI·타임라인 등 다양한 슬라이드 타입) |

### Agents — 에이전트 선택기에서 호출

| 에이전트 | 설명 |
|----------|------|
| `instruction-reviewer` | instructions/prompts/skills 품질·일관성·중복 점검 |
| `skill-scaffolder` | 새 스킬을 표준 디렉토리 구조로 생성 |

---

## 자주 묻는 질문

**Q. 어떤 Copilot 플랜이 필요한가요?**
GitHub Copilot에서 **Claude 모델이 모델 선택기에 보이면** 됩니다. 모델 가용성은 플랜·조직 정책에 따라 다르므로, 모델 선택기를 먼저 확인하세요. 지침/프롬프트/스킬 자체는 모델과 무관하게 동작합니다.

**Q. 내 프로젝트에 어떻게 적용하나요?**
`.github/` 폴더를 프로젝트 루트에 복사하면 Copilot이 자동 인식합니다. 기존 `copilot-instructions.md`가 있으면 병합하세요.

**Q. references 파일이 거의 비어 있어요. 정상인가요?**
네, **의도된 설계**입니다. references는 "무엇을 조사하고 어떤 형식으로 정리할지"만 담고, 구체 내용은 답변 시점에 MS Learn·GitHub Docs·웹 검색으로 최신화합니다. 위 [설계 원칙](#설계-원칙--지식은-박제하지-않고-실시간-최신화) 참고.

**Q. 스킬이 동작하지 않아요.**
최신 VS Code + GitHub Copilot Chat을 사용하고, `SKILL.md`의 `name`이 폴더명과 일치하며 `description`에 트리거 키워드가 있는지 확인하세요.

**Q. instructions가 로드되지 않아요.**
확장자가 `.instructions.md`인지, `applyTo` 패턴이 올바른 glob인지, `.github/instructions/` 경로에 있는지 확인하세요.

**Q. 터미널(CLI)에서도 적용되나요?**
네. Copilot CLI는 `.github/copilot-instructions.md`와 `.github/instructions/**/*.instructions.md`를 자동으로 읽습니다.

---

## 라이선스

MIT
