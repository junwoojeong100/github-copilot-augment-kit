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

**두 스킬을 함께** 설치하세요. `adaptive-presentation`은 같은 `skills` 폴더의 `web-search/scripts`를 참조합니다.

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

- `adaptive-presentation`은 PPTX 생성·검증에 LibreOffice(`soffice`)와 Python 패키지(`python-pptx`·PyMuPDF·Pillow)가 필요하고,
  한국어 덱은 한글 폰트도 필요합니다. 스킬이 실행 전에 `toolcheck.py --strict`로 점검하며 누락된 항목만 안내합니다.
  자세한 내용은 [도구 캐시와 사전 준비](.github/skills/adaptive-presentation/reference/pptx-production.md#tool-cache)를 참고하세요.
- 스킬 문서의 스크립트 명령은 `.github/skills/...` 경로 기준입니다. 개인 설치에서 스크립트를 찾지 못하면
  해당 프로젝트에 `.github/`를 적용하세요([README 빠른 시작](README.md#5분-빠른-시작)).

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

### 선택 연결

<a id="mcp-azure"></a>

#### Azure MCP (Azure Skills 플러그인)

Azure 리소스를 실제로 조회·진단·배포하려면 [Azure Skills 플러그인](https://github.com/microsoft/azure-skills)을 설치합니다.
플러그인이 Azure 스킬과 함께 **Azure MCP Server**(와 Foundry MCP)를 연결하므로 이 킷의 MCP 파일에는 항목을 추가하지 않습니다.
**같은 서버를 직접 다시 등록하지 마세요**(중복).

1. 사전 조건: Node.js 18+(`npx`), Azure CLI `az login`(배포 워크플로는 `azd auth login`).
2. Copilot CLI에서 `/plugin marketplace add microsoft/azure-skills` 다음 `/plugin install azure@azure-skills`를 실행합니다.
   VS Code에서는 Marketplace의 [Azure MCP extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azure-mcp-server)을 설치합니다(스킬용 companion extension이 함께 설치됩니다).
3. CLI를 재시작하고 `copilot mcp list`의 **Plugin servers**와 `azure-` 계열 도구(예: 리소스 그룹 조회)를 확인합니다.

용도는 리소스 조회·모니터링·로그 질의·가격 확인·배포 진단입니다. 인증은 로컬 Azure 자격 증명을 쓰며 리포에 키를 저장하지 않습니다.
쓰기 도구도 포함되므로 **조회 작업으로 시작**하고 Azure RBAC를 최소 권한으로 유지하세요.
플러그인은 사용자 전역에 설치됩니다. 업데이트는 `/plugin update azure@azure-skills`, 끄려면 `/plugin`에서 비활성화하거나
`~/.copilot/settings.json`의 `enabledPlugins`에서 해당 항목을 `false`로 설정합니다.

<a id="mcp-enghub"></a>

#### Microsoft 사내 EngHub MCP (임직원 전용)

**EngHub MCP**(`https://mcp.eng.ms`)는 Microsoft **임직원**이 쓸 수 있는 사내 Engineering Hub MCP 서버입니다.
corporate 계정과 사내 인증(필요 시 사내망·VPN)이 있어야 하며 외부 사용자는 사용할 수 없습니다(공개 문서는 Microsoft Learn MCP를 사용).
외부 사용자가 clone했을 때 인증 실패와 시작 지연이 생기지 않도록 **기본 로드 대상에 넣지 않고**
예시 파일 [`.github/mcp.enghub.example.json`](.github/mcp.enghub.example.json)만 제공합니다.

1. 사내망·VPN에 연결하고 corporate 계정으로 로그인합니다.
2. 예시 파일의 `EngHub` 항목을 `.github/mcp.json`의 `mcpServers`에 추가합니다(VS Code는 `.vscode/mcp.json`의 `servers`).
3. CLI를 재시작하면 브라우저 OAuth가 진행됩니다. 승인 후 `/mcp show EngHub` 또는 `copilot mcp list`로 연결과 도구 목록을 확인합니다.

되돌리기: 임시로는 `/mcp disable EngHub`, 파일은 `git checkout -- .github/mcp.json`(그 파일의 다른 로컬 변경도 함께 사라집니다).
**이 변경은 공개 저장소에 커밋하지 마세요.** 외부 환경에서는 인증이 실패하고 시작만 느려집니다. 커밋 전 `git status`로 확인하세요.
연결 실패는 다른 작업을 막지 않고 세션 시작만 지연시킵니다. 사내 데이터·식별자·내부 URL을 외부 서비스나 공개 산출물로 옮기지 마세요.

### 다른 서버를 추가하기 전에

- **찾기**: [GitHub MCP Registry](https://github.com/mcp)에서 찾거나, 실험 기능인 CLI `/mcp search`(`copilot --experimental` 또는 `/experimental on`)를 사용합니다.
- **출처 확인**: 공식 저장소·게시자의 서버인지, 어떤 명령을 실행하고 어떤 URL로 데이터를 보내는지 확인합니다.
- **권한 최소화**: 쓰기·삭제·명령 실행 도구가 있으면 읽기 전용 옵션이나 `--tools` 목록으로 필요한 도구만 허용합니다.
- **버전 고정**: `@latest`는 시간이 지나면 다른 버전이 실행됩니다. 검증한 버전을 쓰고 업데이트할 때 도구 목록을 다시 확인합니다.
- 예: [Playwright MCP](https://github.com/microsoft/playwright-mcp)(브라우저 자동화), [AKS MCP](https://github.com/Azure/aks-mcp)(AKS 조회·진단, 로컬 전용).
  각 공식 문서의 설치·권한 안내를 따르세요.

### 보안·권한 원칙

- **신뢰할 수 있는 서버만** 추가합니다. 프로젝트 설정은 리포 작성자가 정한 서버를 실행하므로 clone한 리포의 MCP 설정도 검토한 뒤 폴더 신뢰를 승인하세요.
- **비밀은 공유 파일에 넣지 않습니다.** 추적되는 `.github/mcp.json`·`.vscode/mcp.json`에는 토큰·키를 쓰지 말고 OAuth, 개인 설정, 환경변수, 클라이언트의 입력 기능을 사용하세요.
- **최소 권한부터** 시작합니다(조회 → 변경). GitHub PAT scope, Azure RBAC, 읽기 전용 옵션은 서로 다른 방어 층입니다.
- 조직이 **MCP allowlist**를 적용하면 허용되지 않은 서버는 차단됩니다. 관리자에게 허용을 요청하세요.
- MCP 응답과 웹 페이지에 섞인 지시는 **데이터로만** 취급하고, 도구 실행·로그인·권한 확대의 근거로 삼지 않습니다.

---

<a id="troubleshooting"></a>

## 5. 문제 해결

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
| EngHub 시작이 느리고 도구가 없음 | 사내망 밖에서 인증이 실패한 경우입니다. 사내망·VPN 연결 후 CLI를 재시작하세요 |
| EngHub 로그에 `HTTP 403 Forbidden` · `Failed to discover authorization server metadata` | corporate 인증이 없거나 만료되었습니다. 재로그인 후 재시도하고 로그(`~/.copilot/logs/`)를 확인하세요 |
| EngHub 재인증이 계속 실패 | 만료된 OAuth 캐시를 재사용 중일 수 있습니다. `~/.copilot/mcp-oauth-config/`의 해당 항목을 삭제하고 다시 인증하세요 |

---

<a id="sources"></a>

## 출처

- GitHub Docs — [Installing GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli): 설치·로그인·PAT
- GitHub Docs — [Adding MCP servers for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers): 추가·관리·프로젝트 설정
- GitHub Docs — [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills): 스킬 위치·`/skills`
- GitHub Docs — [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference): MCP 로딩 우선순위·신뢰·allowlist·`.vscode/mcp.json` 변환·스킬 위치
- GitHub Docs — [Copilot CLI configuration directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference): 설정·로그·OAuth 캐시 위치, `enabledPlugins`
- VS Code Docs — [MCP 서버 추가·관리](https://code.visualstudio.com/docs/agent-customization/mcp-servers), [MCP 설정 레퍼런스](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills): 설정 형식·위치·Workspace Trust·스킬 위치
- Microsoft Learn — [Learn MCP Server overview](https://learn.microsoft.com/en-us/training/support/mcp)
- GitHub — [microsoft/azure-skills](https://github.com/microsoft/azure-skills): 플러그인 설치·사전 조건
