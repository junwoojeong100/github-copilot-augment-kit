# Copilot × Claude Kit

GitHub Copilot을 **Claude AI + Claude Code**처럼 쓰기 위한 **경량 커스터마이징 킷**입니다. 단일 지침 파일(`copilot-instructions.md`)에 페르소나·사고·소통·안전·코딩·Git·Microsoft/GitHub 가치 강조·팩트체크 원칙을 압축해 담고, 실시간 웹·공식 문서 검색 스킬을 제공합니다.

이 리포의 `.github/` 폴더를 프로젝트에 두면, GitHub Copilot(VS Code Chat·터미널 CLI)이 자동으로 읽어 **더 일관되고 똑똑한 어시스턴트**가 됩니다.

> 별도 Anthropic 구독 없이, **GitHub Copilot이 제공하는 Claude 모델**(Sonnet · Opus 등)을 그대로 활용합니다. **모델 선택기에 Claude가 보이면** 이 킷을 바로 쓸 수 있습니다.

---

## 이게 뭔가요? (3줄 요약)

- **무엇**: GitHub Copilot에 입힐 수 있는 단일 지침 + 전문 스킬 모음입니다.
- **왜**: Copilot의 Claude 모델 위에 일관된 페르소나·규칙·전문 워크플로를 얹어 **Claude AI + Claude Code 같은 경험**을 만듭니다.
- **어떻게**: `.github/` 폴더만 있으면 Copilot이 자동으로 읽습니다. 설치·설정이 거의 없습니다.

---

## 무엇이 들어있나 — 2가지 빌딩 블록

| 블록 | 위치 | 동작 방식 | 내용 |
|------|------|----------|------|
| **Instructions** | `copilot-instructions.md` | 매 대화 **자동 로드** | 페르소나 · 사고 · 소통 · 안전 · 코딩 · Git · MS/GitHub 가치 · 팩트체크 · 출처 |
| **Skills** | `skills/` | 관련 질문 시 **자동 활성화**(또는 `/명령`) | 실시간 웹·공식 문서 검색 |

> 모든 상시 지침을 **단일 파일로 통합**해 토큰을 절약하고 응답·생성 품질을 높였습니다. 스킬은 필요할 때만 불러 씁니다.

---

## 5분 빠른 시작

### 1) 먼저 체험해보기

```bash
git clone https://github.com/junwoojeong100/copilot-claude-kit.git
cd copilot-claude-kit
code .
```

VS Code에서 Copilot Chat을 열고, 하단 **모델 선택기(Model Picker)** 에서 `Claude Sonnet` 또는 `Claude Opus`를 선택합니다. 이제 그냥 대화하면 지침이 자동 적용됩니다.

### 2) 내 프로젝트에 적용하기

이 리포의 **`.github/` 폴더를 내 프로젝트 루트에 복사**하면 끝입니다.

```bash
cp -r copilot-claude-kit/.github /path/to/my-project/
```

> 이미 `copilot-instructions.md`가 있다면 내용을 병합하세요(프로젝트당 하나만 인식됩니다).

---

## 어디서 쓸 수 있나 — VS Code & 터미널(CLI)

이 킷은 **VS Code Copilot Chat**과 터미널용 **[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)** 양쪽에서 동작합니다.

### Copilot CLI 설치

```bash
# macOS / Linux (Homebrew)
brew install copilot-cli

# 크로스 플랫폼 (npm)
npm install -g @github/copilot
```

설치 후 리포 디렉토리에서 `copilot`을 실행하고, 첫 실행 시 `/login`으로 인증합니다.

| 명령 | 설명 |
|------|------|
| `/model` | AI 모델 선택 (Claude Sonnet/Opus 등) |
| `/diff` | 변경사항 리뷰 |
| `/plan` | 구현 계획 수립 |
| `/help` | 전체 명령 보기 |

### VS Code Chat vs Copilot CLI

| 항목 | VS Code Copilot Chat | GitHub Copilot CLI |
|------|---------------------|-------------------|
| `copilot-instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `skills/` | ✅ SKILL.md 자동 활성화 | ⚠️ `/skills`(MCP 기반) |

---

## 설계 원칙 — 지식은 박제하지 않고, 실시간 최신화

이 킷의 **지침·스킬·references는 "방향(무엇을 다룰지)과 형식(어떻게 정리할지)"만 정의**하고, 구체적 사실(서비스 기능·가격·수치·규제 조항)은 **의도적으로 담지 않습니다.**

- **왜?** 클라우드·AI·규제는 빠르게 변합니다. 박제된 내용은 금방 낡고 토큰만 소모합니다.
- **대신** 답변 시점에 공식 문서(`learn.microsoft.com` · `docs.github.com`)와 웹 검색으로 **최신 내용을 가져와** 정리합니다.
- **효과**: 항상 최신 기반 답변 + 토큰 절약 + 유지보수 최소화.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md              # 단일 핵심 지침 (매 대화 자동 로드)
└── skills/                              # 전문 스킬 (온디맨드)
    └── google-web-search/               # 실시간 웹·공식 문서 검색
        └── SKILL.md
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

### Skills — 자연어 또는 `/명령`

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트" | 공식 소스 우선 실시간 웹·문서 검색 |

---

## 자주 묻는 질문

**Q. 어떤 Copilot 플랜이 필요한가요?**
GitHub Copilot에서 **Claude 모델이 모델 선택기에 보이면** 됩니다. 지침/스킬 자체는 모델과 무관하게 동작합니다.

**Q. 내 프로젝트에 어떻게 적용하나요?**
`.github/` 폴더를 프로젝트 루트에 복사하면 Copilot이 자동 인식합니다. 기존 `copilot-instructions.md`가 있으면 병합하세요.

**Q. 스킬이 동작하지 않아요.**
최신 VS Code + GitHub Copilot Chat을 사용하고, `SKILL.md`의 `name`이 폴더명과 일치하며 `description`에 트리거 키워드가 있는지 확인하세요.

**Q. 지침이 로드되지 않아요.**
`.github/copilot-instructions.md` 경로가 맞는지, 프로젝트 루트에 `.github/`가 있는지 확인하세요. Copilot CLI도 이 파일을 자동으로 읽습니다.

---

## 라이선스

MIT
