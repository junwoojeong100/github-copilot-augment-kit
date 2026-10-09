# GitHub Copilot CLI · Skills · MCP 설치·사용 가이드

**이 리포를 clone한 폴더에서 `copilot`을 실행하고 폴더 신뢰를 승인하면 지침·스킬·Microsoft Learn MCP가 함께 로드됩니다.**
이 문서는 설치 → 확인 → 추가 연결 → 문제 해결 순서로 안내합니다. 킷에 무엇이 들어 있고 왜 그렇게
설계했는지는 [README](README.md)가 설명하므로 여기서는 반복하지 않습니다.

기준: 2026-10-09 · GitHub Copilot CLI 1.0.94. [출처](#sources)의 공식 문서와 실제 명령 출력으로 확인했습니다.
버전·미리보기 기능은 바뀔 수 있으니 차이가 있으면 공식 문서를 따르세요. 명령은 macOS/Linux(bash·zsh) 기준입니다.
처음이라면 1 → 2장을 순서대로, 이후에는 필요한 장만 보세요.

---

<a id="cli"></a>

## 1. Copilot CLI 준비

- **조건**: 활성 GitHub Copilot 구독이 필요합니다. 조직·엔터프라이즈 관리자가 CLI를 끄면 사용할 수 없습니다. Windows는 PowerShell 6 이상이 필요합니다.
- **설치**: README의 [Copilot CLI 설치](README.md#copilot-cli-설치) 명령을 쓰거나 공식 [설치 문서](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)를 따릅니다. `copilot --version`으로 확인하고 `copilot update`로 업데이트를 확인합니다.
- **로그인**: 첫 실행에서 `/login`을 입력하고 안내를 따릅니다. 자동화에는 개인 계정이 소유한 fine-grained PAT(**Copilot Requests** 권한)를 `COPILOT_GITHUB_TOKEN`·`GH_TOKEN`·`GITHUB_TOKEN`(우선순위 순) 환경변수로 제공할 수 있습니다. 토큰은 저장소나 설정 파일에 쓰지 않습니다.
- **VS Code**: Copilot Chat에 로그인하고 **Agent mode**로 엽니다. CLI 설치는 필요하지 않습니다.

---

<a id="start"></a>

## 2. 이 리포에서 시작하기

```bash
git clone https://github.com/junwoojeong100/github-copilot-augment-kit.git
cd github-copilot-augment-kit
copilot
```

첫 실행의 **폴더 신뢰(trust)** 질문에서 `Yes`(이번 세션만) 또는 `Yes, and remember this folder`를 고릅니다.
Copilot은 신뢰한 폴더의 파일을 읽고 수정·실행할 수 있으므로 내용을 확인한 폴더만 승인하세요.
**승인해야 `.github/mcp.json`의 프로젝트 MCP 서버가 로드됩니다**(신뢰하지 않은 폴더에서는 건너뜁니다).
VS Code에서는 `code .`로 폴더를 열고 Workspace Trust를 승인한 뒤 Chat을 Agent mode로 전환합니다(제한 모드에서는 워크스페이스 MCP가 시작되지 않습니다).

### 설치 확인

| 확인 대상 | Copilot CLI | VS Code (Copilot Chat) |
|---|---|---|
| 지침·스킬·MCP 로드 | `/env` | — |
| 스킬 | `/skills list` (터미널: `copilot skill list`) — `web-search`, `adaptive-presentation`이 보여야 합니다 | 채팅 입력창에서 `/skills` → **Configure Skills** |
| MCP | `/mcp show microsoft-learn` (터미널: `copilot mcp list` → **Workspace servers**의 `microsoft-learn (http)`) | `.vscode/mcp.json`의 **Start** 또는 **MCP: List Servers** → 도구 목록에 `microsoft_docs_search` 등 |

동작 확인 프롬프트:

```text
> Microsoft Learn에서 Azure Container Apps 개요를 찾아 원문 링크와 함께 요약해줘.
> Python의 현재 최신 안정 버전과 지원 종료 일정을 공식 출처로 확인해줘.
```

첫 요청은 Learn MCP 도구를, 둘째 요청은 `web-search` 스킬을 사용합니다(자동 선택되지 않으면 `/web-search`로 지정).
MCP 도구 호출은 명시적 허용이 필요합니다. 요청 내용을 읽고 허용 범위를 좁게 고르세요.

---

<a id="skills"></a>

## 3. Skills

### 로드 위치

| 범위 | 위치 | 설명 |
|---|---|---|
| 프로젝트 | `.github/skills/<이름>/SKILL.md` (`.agents/skills/`, `.claude/skills/`도 인식) | 이 리포나 `.github/`를 적용한 프로젝트에서 자동 인식 |
| 개인 | `~/.copilot/skills/` 또는 `~/.agents/skills/` | 모든 프로젝트에서 사용. 같은 이름이면 **프로젝트 스킬이 우선** |
| 추가 폴더 (CLI) | 환경변수 `COPILOT_SKILLS_DIRS`(쉼표 구분) 또는 설정 `skillDirectories` | 복사 없이 clone한 폴더를 스킬 위치로 등록 |

VS Code도 같은 프로젝트·개인 위치를 사용합니다. Copilot은 프롬프트와 `description`을 보고 스킬을 선택하며
선택이 보장되지는 않으므로, 확실히 쓰려면 `/web-search`처럼 이름을 지정하세요.
스킬별 트리거 예시는 README의 [Skills 표](README.md#구성-요소-자세히)를 참고하세요.

<a id="skills-personal"></a>

### 개인 환경(모든 프로젝트)에 설치

**두 스킬을 함께** 설치하세요. `adaptive-presentation`은 외부 조사에 `web-search` 스킬을 호출하고, Fact Ledger 검증에는
같은 `skills` 폴더의 `web-search/scripts`를 사용합니다. `web-search`가 없어도 나머지 스크립트는 실행되지만,
Fact Ledger 검증 단계에서 두 스킬을 설치하라는 메시지와 함께 멈춥니다.

**방법 A — 복사**. 같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 내용을 비교해 병합하세요.

```bash
mkdir -p ~/.copilot/skills
cp -R <clone 경로>/.github/skills/* ~/.copilot/skills/
```

복사본은 자동으로 갱신되지 않습니다. `git pull` 후 해당 스킬 폴더를 새 버전으로 교체하세요.

**방법 B — 복사 없이 등록 (Copilot CLI)**. `git pull`만으로 갱신됩니다.

```bash
export COPILOT_SKILLS_DIRS="<clone 경로>/.github/skills"   # ~/.zshrc 등에 추가
```

설치 후 `copilot skill list`에 두 스킬이 보이면 성공입니다. 세션 중에 추가했다면 `/skills reload`,
로드 위치는 `/skills info <이름>`으로 확인합니다.

- 스킬 문서의 스크립트 명령은 `<skill>/scripts/...` 형태입니다. `<skill>`은 해당 스킬의 `SKILL.md`가 있는 폴더이므로
  프로젝트 설치, 개인 설치, `COPILOT_SKILLS_DIRS` 등록에서 같은 명령을 씁니다(경로는 `copilot skill list --json`의 `path`).
  `<work>`는 세션 작업 폴더, `python3`는 환경의 Python 3입니다(Windows는 `py -3`).
- `adaptive-presentation`에는 Python 패키지(`python-pptx`·PyMuPDF·Pillow)가 필요합니다.
  `python3 -m pip install -r <skill>/requirements.txt`(`<skill>`은 `adaptive-presentation` 폴더)로 설치하세요.
  LibreOffice(`soffice`)와 한국어 덱용 한글 폰트는 pip 패키지가 아니므로 OS 패키지 관리자로 따로 설치합니다.
  스킬이 실행 전에 `toolcheck.py --strict`로 점검하고, 누락된 항목은 설치 방법을 출력합니다.
  자세한 내용은 [도구 캐시와 사전 준비](.github/skills/adaptive-presentation/reference/pptx-production.md#tool-cache)를 참고하세요.

---

<a id="mcp"></a>

## 4. MCP

### 번들·내장 서버 사용

- **Microsoft Learn MCP** (번들 · 인증 불필요): 공식 문서 검색(`microsoft_docs_search`), 문서 전문 조회(`microsoft_docs_fetch`),
  공식 코드 샘플 검색(`microsoft_code_sample_search`). `web-search` 스킬의 도구 선택 순서에도 포함된 Microsoft·Azure 공식 문서 경로입니다.
  엔드포인트(`https://learn.microsoft.com/api/mcp`)는 MCP 클라이언트 전용이라 브라우저로 열면 `405`가 나올 수 있으며 정상입니다.
- **GitHub MCP** (Copilot CLI 내장): 별도 등록 없이 이슈·PR·코드를 다룹니다.

두 서버의 역할 요약은 README의 [번들된 서버](README.md#번들된-서버)를 참고하세요.

<a id="mcp-config"></a>

### 설정 위치와 형식

| 파일 | 범위 | 읽는 클라이언트 | 루트 키 |
|---|---|---|---|
| `.github/mcp.json` | 프로젝트 (리포와 함께 공유) | Copilot CLI | `mcpServers` |
| `.vscode/mcp.json` | 프로젝트 (리포와 함께 공유) | VS Code | `servers` |
| `.mcp.json` (리포 루트) | 프로젝트 (이식형) | Copilot CLI · VS Code | `mcpServers` |
| `~/.copilot/mcp-config.json` | 개인 (모든 프로젝트, 이식형) | Copilot CLI · VS Code | `mcpServers` |

VS Code 사용자 프로필의 `mcp.json`(명령 팔레트 **MCP: Open User Configuration**)은 `.vscode/mcp.json`과 같은 VS Code 형식(`servers`)입니다.

- 이 리포는 클라이언트별 파일(`.github/mcp.json`·`.vscode/mcp.json`)을 번들합니다. **양쪽에서 쓸 서버를 새로 추가한다면 이식형 파일 하나에 두세요.**
  VS Code 문서도 새 서버에는 이식형 위치를 권장하고 `.vscode/mcp.json`은 호환용으로 표시합니다.
- CLI는 작업 디렉터리에서 Git 루트까지 `.mcp.json`·`.github/mcp.json`을 찾으며, 같은 이름이면 **프로젝트 설정이 개인 설정보다 우선**합니다.
- **CLI는 `.vscode/mcp.json`을 읽지 않습니다**(형식이 다름). VS Code 파일만 있는 프로젝트는
  `jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json`으로 변환하세요. 이미 `.mcp.json`이 있으면 덮어쓰므로 병합해야 합니다.
- CLI의 개인 설정 위치는 환경변수 `COPILOT_HOME`으로 바꿀 수 있습니다.

<a id="mcp-add"></a>

### 서버 추가와 관리

| 방법 | 사용법 |
|---|---|
| CLI 대화형 | `/mcp add` → 이름·유형(Local/STDIO 또는 HTTP)·명령 또는 URL 입력 → <kbd>Ctrl</kbd>+<kbd>S</kbd>. 재시작 없이 바로 사용됩니다. |
| CLI 터미널 | 원격: `copilot mcp add --transport http <이름> <URL>` · 로컬: `copilot mcp add <이름> -- <명령> [인자...]` — 개인 설정에 저장됩니다. |
| 프로젝트 공유 | 리포의 `.mcp.json`(CLI·VS Code) 또는 `.github/mcp.json`(CLI)의 `mcpServers`에 항목을 병합합니다(아래 예시). |
| VS Code | 명령 팔레트 **MCP: Add Server**에서 `.mcp.json`(워크스페이스) 또는 Copilot Global(`~/.copilot/mcp-config.json`)을 고르면 CLI와 공유됩니다. VS Code 전용은 `.vscode/mcp.json`의 `servers`에 추가합니다. |

```json
{
  "mcpServers": {
    "microsoft-learn": { "type": "http", "url": "https://learn.microsoft.com/api/mcp", "tools": ["*"] },
    "<이름>": { "type": "local", "command": "<명령>", "args": ["<인자>"], "tools": ["*"] }
  }
}
```

`copilot mcp add`는 `--env KEY=VALUE`, `--header "이름: 값"`, `--tools`(허용할 도구 목록, 기본 `*`), `--timeout <ms>` 옵션을 지원합니다.
`--env`·`--header` 값은 개인 설정 파일에 저장되므로 공유 파일에 넣지 마세요. `--show-secrets`는 값을 그대로 출력하니 로그에 남기지 마세요.

| 목적 | 대화형 | 터미널 |
|---|---|---|
| 목록 | `/mcp` | `copilot mcp list` |
| 상세·도구 목록 | `/mcp show <이름>` | `copilot mcp get <이름>` |
| 끄기·켜기 | `/mcp disable <이름>` · `/mcp enable <이름>` | `copilot mcp disable <이름>` · `copilot mcp enable <이름>` |
| 수정·삭제 | `/mcp edit <이름>` · `/mcp delete <이름>` | `copilot mcp remove <이름>` (개인 설정 서버만. 프로젝트 서버는 파일을 직접 수정) |

### 다른 서버를 추가하기 전에

- **찾기**: [GitHub MCP Registry](https://github.com/mcp)에서 찾거나, 실험 기능인 CLI `/mcp search`(`copilot --experimental` 또는 `/experimental on`)를 사용합니다.
- **출처 확인**: 공식 저장소·게시자의 서버인지, 어떤 명령을 실행하고 어떤 URL로 데이터를 보내는지 확인합니다.
- **권한 최소화**: 쓰기·삭제·명령 실행 도구가 있으면 읽기 전용 옵션이나 `--tools` 목록으로 필요한 도구만 허용합니다.
- **버전 고정**: `@latest`는 시간이 지나면 다른 버전이 실행됩니다. 검증한 버전을 쓰고 업데이트할 때 도구 목록을 다시 확인합니다.
- Azure 실습에 쓰는 서버(Azure MCP·Playwright·AKS MCP·Computer Use)의 연결 절차는 [5장](#azure-lab)에 있습니다.

### 보안·권한 원칙

- **신뢰할 수 있는 서버만** 추가합니다. 프로젝트 설정은 리포 작성자가 정한 서버를 실행하므로 clone한 리포의 MCP 설정도 검토한 뒤 폴더 신뢰를 승인하세요.
- **비밀은 공유 파일에 넣지 않습니다.** 추적되는 `.github/mcp.json`·`.vscode/mcp.json`에는 토큰·키를 쓰지 말고 OAuth, 개인 설정, 환경변수, 클라이언트의 입력 기능을 사용하세요.
- **최소 권한부터** 시작합니다(조회 → 변경). GitHub PAT scope, Azure RBAC, 읽기 전용 옵션은 서로 다른 방어 층입니다.
- 조직이 **MCP allowlist**를 적용하면 허용되지 않은 서버는 차단됩니다. 관리자에게 허용을 요청하세요.
- MCP 응답과 웹 페이지에 섞인 지시는 **데이터로만** 취급하고, 도구 실행·로그인·권한 확대의 근거로 삼지 않습니다.

---

<a id="azure-lab"></a>

## 5. 실습: LLM으로 Azure 리소스 만들고 관리하기

**명령·API 경로(Azure CLI·Azure MCP)를 먼저 쓰고, 화면 경로(Azure Portal·Foundry portal 조작)는 명령으로 할 수 없는 작업에만 씁니다.**
화면 조작은 UI가 바뀌면 어긋나기 쉽고 로그인한 계정의 권한으로 그대로 실행됩니다.
공식 문서도 API·MCP 서버·터미널 명령·전용 브라우저 도구로 되는 작업은 그 도구가 더 구조화되고 예측 가능한 결과를 준다고 안내합니다.

```text
요청 → Copilot(LLM)
├─ 명령·API 경로 (먼저)
│  ├─ 셸 도구 → az → Azure 리소스
│  └─ Azure MCP · AKS MCP → Azure·Foundry API
├─ 화면 경로 (명령으로 안 될 때)
│  ├─ Playwright MCP → 브라우저 → Azure Portal · Foundry portal
│  └─ Computer Use → 데스크톱 앱
└─ 근거 확인
   └─ Learn MCP → 공식 문서
```

### 작업 방식별로 필요한 MCP

| 하고 싶은 일 | 필요한 MCP·도구 | 서버 이름 · 등록 위치 (참고 구성) | 연결 |
|---|---|---|---|
| 명령·Bicep·설정의 공식 근거 확인 | Microsoft Learn MCP | `microsoft-learn` · Workspace | 이 리포에 번들 |
| Azure CLI(`az`)로 생성·수정·삭제 | **MCP 없이 가능** — Copilot CLI의 셸 도구가 `az`를 실행하고, 변경 가능성이 있는 명령은 승인을 요청합니다 | — | [1장](#cli) + Azure CLI `az login` |
| 구조화된 도구로 조회·진단·배포 | Azure MCP Server | `azure` · Plugin | [Azure MCP](#mcp-azure) |
| Foundry 에이전트·모델 배포·평가·지식 인덱스 조회 | Azure MCP Server (`foundry`·`foundryextensions` 도구) | `azure` · Plugin | [Azure MCP](#mcp-azure) |
| AKS 클러스터·Kubernetes 운영 | AKS MCP | `aks-mcp` · 필요 시 추가 | [AKS MCP](#mcp-aks) |
| Azure Portal·Foundry portal 웹 화면 조작 | Playwright MCP | `playwright` · `playwright-headless` · User | [Playwright MCP](#mcp-playwright) |
| 브라우저 밖 데스크톱 앱 조작 | Computer Use (미리보기) | `computer-use` · Builtin | [Computer Use](#mcp-computer-use) |
| 저장소·PR·Actions 조회(IaC 코드 포함) | GitHub MCP | `github-mcp-server` · Builtin | Copilot CLI 내장 |

참고 구성은 실습 기준 환경의 Copilot CLI 설정입니다. `copilot mcp list`는 서버를 **User**(개인 설정)·**Workspace**(프로젝트 설정)·**Plugin**·**Builtin** servers로 나눠 보여 주며, 표의 등록 위치가 이 구분입니다.
서버 이름은 등록할 때 정하는 별칭이라 바꿔도 됩니다.

### 예시 요청

| 경로 | 요청 예시 |
|---|---|
| Learn MCP | "Azure Storage 계정을 만드는 `az` 명령 형식을 Microsoft Learn에서 확인해 원문 링크와 함께 알려줘." |
| Azure CLI | "리소스 그룹 `rg-lab-<이름>`을 `<리전>`에 만드는 `az` 명령을 먼저 보여줘. 내가 승인하면 실행하고 결과를 확인해줘." |
| Azure MCP | "`rg-lab-<이름>`의 리소스를 조회해줘. 만들거나 바꾸지 마." |
| Azure MCP (Foundry) | "내 Foundry 프로젝트의 모델 배포 목록을 조회만 해줘." |
| Playwright MCP | "열려 있는 Azure Portal에서 `rg-lab-<이름>`의 리소스 목록을 읽기만 해줘. 만들기·삭제 버튼은 누르지 마." |

### 서버별 연결

<a id="mcp-azure"></a>

#### Azure MCP (Azure Skills 플러그인)

리소스 조회·모니터링·로그 질의·가격 확인·배포 진단, Bicep·Terraform·`azd` 지원, Foundry(`foundry`)·RBAC(`role`) 같은 서비스별 도구를 구조화된 형태로 제공합니다.
도구 범위는 [Azure MCP 도구 목록](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/)에서 확인하세요.

1. 사전 조건: Node.js 18+(`npx`), Azure CLI `az login`(배포 워크플로는 `azd auth login`).
2. Copilot CLI에서 `/plugin marketplace add microsoft/azure-skills` 다음 `/plugin install azure@azure-skills`를 실행합니다.
   VS Code에서는 Marketplace의 [Azure MCP extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azure-mcp-server)을 설치합니다(스킬용 companion extension이 함께 설치됩니다).
3. CLI를 재시작하고 `copilot mcp list`의 **Plugin servers**에 `azure`가 보이는지, 리소스 그룹 조회 같은 읽기 요청이 되는지 확인합니다.

- 플러그인이 연결하는 MCP 서버는 Azure MCP Server(`azure`) 하나이므로 이 킷의 MCP 파일에는 항목을 추가하지 않습니다. **같은 서버를 직접 다시 등록하지 마세요**(중복).
- 배포 워크플로는 플러그인의 `azure-prepare` → `azure-validate` → `azure-deploy` 스킬이 안내합니다.
- **Azure CLI와의 관계**: Azure MCP의 Azure CLI 도구(`extension`)는 `az` 명령을 찾고 설치 방법을 안내하는 용도입니다. `az`를 실제로 실행하는 것은 Copilot CLI의 셸 도구입니다.
- **Foundry 작업**은 이 서버의 `foundry`(모델 카탈로그·배포·쿼터, 에이전트, 평가, 세션, project connection, 모니터링)와 `foundryextensions`(지식 인덱스 조회, OpenAI 호환 호출, Foundry 리소스 조회) 도구로 합니다.
  2026-10-09 기준 이 도구에 없는 작업(Foundry 리소스·프로젝트 생성, 파인튜닝, AI Search 인덱스 생성·수정 — `search` 도구는 조회·질의만 지원)은 플러그인에 포함된 `microsoft-foundry` 스킬의 `az`·스크립트 워크플로나 Azure Portal로 합니다.
  각 도구의 명령 목록은 도구를 `learn` 모드로 호출해 확인합니다.
- 인증은 로컬 Azure 자격 증명(`az login`)과 Azure RBAC를 따릅니다. 구독을 지정하지 않으면 Azure CLI 프로필(`az account set`) 또는 `AZURE_SUBSCRIPTION_ID`의 구독을 쓰므로 실습 전에 대상 구독을 확인하세요.
- 쓰기를 막으려면 시작 옵션 `--read-only`를 씁니다. 플러그인이 정의한 서버는 `server start`로 고정되어 있으므로, 필요하면 `/mcp disable azure`로 끄고
  `copilot mcp add azure-readonly -- npx -y @azure/mcp@latest server start --read-only`로 따로 등록합니다(VS Code extension은 `azureMcp.readOnly` 설정).
- 업데이트는 `/plugin update azure@azure-skills`, 끄려면 `/plugin`에서 비활성화하거나 `~/.copilot/settings.json`의 `enabledPlugins`에서 해당 항목을 `false`로 설정합니다.

<a id="mcp-playwright"></a>

#### Playwright MCP (Azure Portal·Foundry portal 화면 조작)

웹 페이지를 접근성 스냅샷으로 읽고 클릭·입력합니다. Node.js 18+가 필요하며 같은 패키지를 두 프로필로 등록합니다.

| 서버 이름 | 추가 인자 | 쓰는 때 |
|---|---|---|
| `playwright` | `--browser msedge` | 화면을 보며 포털을 조작합니다. **로그인 상태가 browser profile에 남습니다.** |
| `playwright-headless` | `--browser msedge --headless --isolated` | 화면 없이 공개 페이지·문서를 점검합니다. 종료하면 profile이 사라집니다. |

```bash
copilot mcp add --timeout 180000 playwright -- npx @playwright/mcp@latest --browser msedge
copilot mcp add --timeout 180000 playwright-headless -- npx @playwright/mcp@latest --browser msedge --headless --isolated
```

개인 설정(`~/.copilot/mcp-config.json`)에는 다음처럼 저장됩니다.

```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "msedge"],
      "tools": ["*"],
      "timeout": 180000
    },
    "playwright-headless": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "msedge", "--headless", "--isolated"],
      "tools": ["*"],
      "timeout": 180000
    }
  }
}
```

- VS Code에서는 **MCP: Add Server**를 쓰거나 `code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'`를 실행합니다.
- `--browser`는 설치된 브라우저에 맞게 `chrome`·`msedge`·`firefox`·`webkit` 중에서 고릅니다.
- `--timeout`의 기본값(30000ms)은 Playwright의 페이지 이동 제한(기본 60초)보다 짧아 참고 구성은 180000ms(3분)로 늘렸습니다.

포털 조작 순서와 주의:

1. `playwright`가 연 브라우저에서 **Azure Portal 로그인(MFA 포함)은 직접** 합니다. 로그인 정보나 코드를 프롬프트에 붙여넣지 않습니다.
2. 읽기 요청으로 시작하고, 만들기·삭제 같은 변경은 단계마다 내용을 확인한 뒤 승인합니다.
3. Playwright MCP는 **보안 경계가 아닙니다**(공식 문서). 로그인한 세션은 그 계정이 포털에서 할 수 있는 모든 일을 할 수 있으므로 실습 전용 계정을 쓰고,
   끝나면 profile(macOS 기본 위치 `~/Library/Caches/ms-playwright/mcp-{channel}-{workspace-hash}`)을 삭제합니다. `--allowed-origins`도 보안 경계가 아닙니다.
4. profile은 한 번에 하나의 브라우저만 쓸 수 있습니다. 여러 client를 동시에 쓰려면 `--isolated`나 별도 `--user-data-dir`을 지정합니다.

<a id="mcp-aks"></a>

#### AKS MCP

AKS 클러스터와 Kubernetes 리소스를 `az`·`kubectl` 등으로 조회·진단·운영합니다(통합 도구 `call_az`·`call_kubectl`).

- **로컬 stdio 전용**입니다. HTTP·SSE, 컨테이너 서비스, 프록시·게이트웨이로 노출하는 구성은 공식 지원 범위 밖입니다.
- 설치(VS Code): **Azure Kubernetes Service** extension을 설치하고 명령 팔레트에서 **AKS: Setup AKS MCP Server**를 실행합니다.
- 설치(Copilot CLI): [릴리스](https://github.com/Azure/aks-mcp/releases)에서 플랫폼에 맞는 실행 파일(macOS Apple Silicon `aks-mcp-darwin-arm64`, Intel `aks-mcp-darwin-amd64`)을 받아 실행 권한을 주고 등록합니다.

```bash
copilot mcp add aks-mcp -- <aks-mcp 실행 파일 경로> --access-level readonly
```

- 사전 조건: Azure CLI `az login`과 대상 클러스터의 Azure·Kubernetes 권한. `AZURE_CLIENT_ID` 같은 인증 환경변수가 있으면 `az login`보다 먼저 쓰이므로 의도한 신원인지 확인하세요.
- `--access-level`(`readonly` 기본 · `readwrite` · `admin`)은 **실수를 줄이는 장치일 뿐 권한 경계가 아닙니다.** AKS MCP를 호출할 수 있으면 그 프로세스 신원의 Azure·Kubernetes 권한을 그대로 갖습니다. 본인 developer identity로 쓰고 필요한 권한만 부여하세요.

<a id="mcp-computer-use"></a>

#### Computer Use (Copilot CLI 내장, 공개 미리보기)

접근성 정보와 화면으로 데스크톱 앱을 읽고 클릭·입력합니다(macOS·Windows 로컬 세션). **API·MCP·명령·브라우저 도구로 할 수 없는 앱 작업에만** 쓰세요. 웹인 Azure Portal은 Playwright MCP가 더 구조적입니다.

- 기본은 꺼져 있습니다. `/computer show`로 상태를 보고 `/computer on`으로 켭니다(`/computer off`로 끔). macOS는 **손쉬운 사용(Accessibility)**과 **화면 기록(Screen Recording)** 권한 안내를 따릅니다.
- 현재 권한 모드(`/permissions show`)를 따릅니다. 앱마다 요청되는 승인 내용을 읽고 허용하며, 오동작하면 <kbd>Esc</kbd>를 두 번 눌러 중단합니다. 민감한 정보가 있는 앱에는 **Always allow**를 쓰지 마세요.
- 조직의 managed settings가 막으면 켤 수 없습니다.

### 실습 안전 수칙

- **실습 전용 구독·리소스 그룹**에서만 작업하고, 시작 전에 대상 구독을 확인합니다(`az account show`).
- **조회 → 변경 순서**로 진행합니다. 변경 전에는 실행할 `az` 명령이나 도구 파라미터(리소스 ID·구독·리소스 그룹)를 읽고 승인합니다.
- **권한은 최소로** 시작합니다(Reader → 필요한 범위의 Contributor). `--read-only`·`--access-level readonly`는 실수 방지 장치이며 권한 경계가 아닙니다.
- **승인 단계를 끄지 않습니다.** `/yolo`·`--allow-all`·Always allow는 쓰지 말고, 삭제는 `copilot --deny-tool='shell(az group delete)'`처럼 막아 두고 직접 실행합니다.
- **로그인·MFA·비밀번호·토큰은 사람이 직접** 입력하고 프롬프트에 붙여넣지 않습니다.
- 끝나면 **리소스 그룹 단위로 정리**해 비용을 멈추고 Playwright profile도 삭제합니다.

---

<a id="troubleshooting"></a>

## 6. 문제 해결

| 증상 | 확인할 것 |
|---|---|
| CLI에서 `microsoft-learn`이 보이지 않음 | 폴더 신뢰를 승인했는지, 리포(또는 하위) 디렉터리에서 실행했는지, `/mcp`에서 비활성화되어 있지 않은지 |
| `copilot -p`(비대화형)에서 MCP가 없음 | 신뢰한 폴더에서만 프로젝트 MCP를 로드합니다. 신뢰할 수 있는 리포에 한해 `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`로 로드할 수 있습니다 |
| CLI가 `.vscode/mcp.json`을 무시함 | 정상입니다. 형식이 다르므로 `.github/mcp.json`(`mcpServers`)을 쓰거나 [변환](#mcp-config)하세요 |
| VS Code에서 MCP 도구가 없음 | Workspace Trust(제한 모드에서는 워크스페이스 MCP가 차단됨), `.vscode/mcp.json`의 **Start** 또는 **MCP: List Servers**, Chat이 **Agent mode**인지, 도구 선택(**Configure Tools**)에서 서버가 켜져 있는지 |
| `MCP server "…" was blocked by your enterprise` | 조직 allowlist 정책입니다. 관리자에게 서버 허용을 요청하세요 |
| 로컬 서버가 시작되지 않음 | 실행 파일·런타임(`node`, `npx`, `uvx` 등)이 PATH에 있는지, `/mcp show <이름>`의 오류 메시지 |
| `401`·`403` | 로그인·토큰 만료, scope·RBAC 권한, 조직 정책. 토큰을 로그에 출력하지 마세요 |
| 스킬이 보이지 않음 | `/skills list`, 새로 추가했다면 `/skills reload`, `SKILL.md`의 `name`과 폴더명 일치, 같은 이름의 프로젝트 스킬이 개인 스킬을 가리는지 |
| Playwright가 시작하지 않거나 profile 오류 | Node.js 18+, `--browser`로 지정한 브라우저가 설치되어 있는지, 같은 profile을 다른 브라우저가 쓰고 있지 않은지(`--isolated` 또는 별도 `--user-data-dir`) |
| Azure MCP가 의도하지 않은 구독을 조회함 | `az account show`로 기본 구독을 확인하고 요청에 구독을 명시합니다. `AZURE_SUBSCRIPTION_ID`가 설정되어 있는지도 확인하세요 |
| Computer Use를 켤 수 없거나 동작하지 않음 | `/computer show`, 지원 OS의 로컬 세션인지, `/plugin`과 `/mcp list`에서 computer-use가 켜져 있는지, macOS의 손쉬운 사용·화면 기록 권한, 조직 정책 |

---

<a id="sources"></a>

## 출처

- GitHub Docs — [Installing GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli): 설치·로그인·PAT
- GitHub Docs — [Adding MCP servers for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers): 추가·관리·프로젝트 설정
- GitHub Docs — [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills): 스킬 위치·`/skills`
- GitHub Docs — [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference): MCP 로딩 우선순위·신뢰·allowlist·`.vscode/mcp.json` 변환·스킬 위치
- GitHub Docs — [Copilot CLI configuration directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference): 설정·로그·OAuth 캐시 위치, `enabledPlugins`
- GitHub Docs — [Allowing and denying tool use](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools): 셸 명령 승인, `--allow-tool`·`--deny-tool` 패턴
- GitHub Docs — [Computer use in Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/computer-use), [About computer use](https://docs.github.com/en/copilot/concepts/agents/computer-use): `/computer`, 권한, 한계
- VS Code Docs — [MCP 서버 추가·관리](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [MCP 설정 레퍼런스](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills): 설정 형식·위치·Workspace Trust·스킬 위치
- Microsoft Learn — [Learn MCP Server overview](https://learn.microsoft.com/en-us/training/support/mcp)
- Microsoft Learn — [Azure MCP Server 도구](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/): 시작 옵션(`--read-only`)·인증·도구 범주
- GitHub — [microsoft/azure-skills](https://github.com/microsoft/azure-skills): 플러그인 설치·사전 조건·스킬
- GitHub — [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp): 설치·옵션·profile·보안
- GitHub — [Azure/aks-mcp](https://github.com/Azure/aks-mcp): 설치·접근 수준·신뢰 경계
