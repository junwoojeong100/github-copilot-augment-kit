# 이 랩탑의 MCP 설치·연결·사용 가이드

**문서 검색은 Microsoft Learn, GitHub 맥락은 GitHub MCP, Azure 운영은 Azure/AKS MCP,
웹 자동화는 Playwright, 데스크톱 앱 조작은 Computer Use를 선택합니다.**
아래 내용은 특정 저장소에 종속되지 않는 macOS용 안내입니다.

확인일: **2026-10-09**. 실제 설정 파일·설치 패키지·실행 파일 경로와 공식 문서를 대조했습니다.
설치·설정·로그인·클라우드 리소스는 변경하지 않았으며, 시크릿과 개인 절대 경로는 기록하지 않았습니다.

## 1. 확인된 구성과 먼저 알아둘 사항

**등록된 이름, 설치된 실행 파일, 연결 성공은 서로 다릅니다.** 9개 서버/실행 프로필 구성을 확인했지만
모두 정상 실행되는 것은 아닙니다. 이 대화에서는 Azure, Computer Use, GitHub, Microsoft Learn,
Playwright 두 프로필의 도구가 노출되어 있습니다. 도구 노출만으로 인증·브라우저·OS 권한이 검증되지는 않습니다.

| 서버 / 프로필 | 주 용도 | 로컬에서 확인한 구성 | 확인 상태 |
|---|---|---|---|
| Microsoft Learn | Microsoft 공식 문서·코드 샘플 검색과 원문 조회 | Copilot CLI, VS Code/Insiders, Codex의 원격 HTTP 등록 | 로컬 서버 설치가 아닌 원격 연결 |
| GitHub MCP | 저장소·PR·이슈·Actions·Copilot Spaces 등 GitHub 맥락 | VS Code Insiders HTTP 등록, Codex의 `/readonly` 등록; Copilot CLI에는 기본 제공 | 실제 노출 도구는 client·toolset·계정 정책에 따라 다름 |
| Azure MCP | Azure 리소스 조회·진단·관리 | VS Code Insiders의 `npx`; Codex의 로컬 `azmcp` 실행 파일 | 로컬 패키지 `3.0.0-beta.40`, 실행 파일 존재; `server start --help` 확인 |
| AKS MCP | AKS·Kubernetes 조회와 진단 | VS Code Insiders의 Docker 등록 | **인자 중복 확인. 정상 기동 미검증** |
| Azure AI Foundry — 구형 | 모델·검색·평가·에이전트 작업 | Copilot CLI의 `uvx` + `azure-ai-foundry/mcp-foundry` | **상류 저장소에서 deprecated 공지. 신규 설치 비권장** |
| Playwright | 화면을 보며 웹 UI 탐색·재현 | Copilot CLI/Codex의 로컬 Node 실행, VS Code Insiders의 `npx` | 로컬 패키지 `0.0.80`; Edge 채널 사용 |
| Playwright Headless | 화면 없이 웹 검사·반복 자동화 | 같은 패키지에 `--headless --isolated` 추가 | 별도 제품이 아닌 실행 프로필 |
| Computer Use | PowerPoint·편집기 등 로컬 앱의 접근성 기반 UI 조작 | 현재 호스트의 도구 노출; Codex에는 Copilot 캐시의 실행 파일 등록 | **Codex가 가리키는 구형 캐시 실행 파일은 없음** |
| `node_repl` | 등록명 기준 Node 실행 보조로 추정 | Codex가 ChatGPT 앱 내부 실행 파일을 참조 | **앱과 실행 파일이 없음. 상세 도구·독립 설치 방법 미확인** |

**이 랩탑에서 주의할 구성**

- VS Code Insiders의 Learn 등록 두 개가 같은 endpoint를 가리킵니다. 중복 도구가 필요하지 않다면 하나만
  사용하는 편이 명확합니다. 이 문서 작성 중 삭제하지 않았습니다.
- AKS의 `args`에 `run -i --rm` 블록과 이미지가 각각 두 번 들어 있습니다. 그대로 실행하지 말고
  아래의 정상 설치 방식과 비교해야 합니다.
- 구형 Foundry의 Git 저장소 기반 설치를 현재 권장 방식으로 복사하지 마십시오. 대체 서비스는
  **Foundry MCP Server public preview**입니다.
- Computer Use의 Codex 등록은 Copilot `1.0.87-0` 캐시 경로, `node_repl`은
  `/Applications/ChatGPT.app/Contents/Resources/cua_node/bin/node_repl`을 가리키지만 해당 파일은 없습니다.
  다른 호스트에서 도구가 보인다고 이 등록까지 정상인 것은 아닙니다.

확인 범위는 아래의 주요 client 설정과 해당 설정이 참조한 패키지/실행 파일입니다.
별도 VS Code profile, 원격 개발 환경, 모든 앱의 플러그인까지 전수 조사한 목록은 아닙니다.

## 2. 어느 설정 파일에 등록하는가

| Client / 범위 | macOS 위치 | 서버 목록의 형식 |
|---|---|---|
| Copilot CLI — 개인 공통 | `~/.copilot/mcp-config.json` | JSON `mcpServers` |
| Copilot CLI — 프로젝트 | 프로젝트 `.mcp.json` 또는 `.github/mcp.json` | JSON `mcpServers` 또는 client가 지원하는 bare 형식 |
| VS Code — 개인 profile | **MCP: Open User Configuration**으로 열기; 기본 profile은 `~/Library/Application Support/Code/User/mcp.json` | JSON `servers` |
| VS Code Insiders — 개인 profile | `~/Library/Application Support/Code - Insiders/User/mcp.json` | JSON `servers` |
| VS Code — 프로젝트 | `.vscode/mcp.json`; 최신 문서는 portable `.mcp.json`도 지원 | native 형식은 `servers`, portable 형식은 `mcpServers` |
| Codex — 개인 공통 | `~/.codex/config.toml` | TOML `[mcp_servers.<name>]` |

Copilot CLI는 `COPILOT_HOME`이 설정되면 개인 설정 위치가 달라집니다. 이 랩탑에서는 unset 상태입니다.
프로젝트의 같은 이름 서버는 개인 설정보다 우선할 수 있으므로, 다른 저장소에서 동작이 달라지면
프로젝트 설정도 확인하십시오. **Copilot CLI가 `.vscode/mcp.json`을 직접 읽는 것은 아닙니다.**

현재 VS Code Stable의 기본 user MCP 파일은 없고, **Insiders user 파일**에 여러 서버가 있습니다.
Stable과 Insiders의 설정을 혼동하지 마십시오. Claude Desktop 설정에는 MCP 등록이 없었으며,
확인한 Cursor·Gemini·Antigravity·Windsurf의 표준 MCP 설정 경로도 없었습니다.
이는 해당 앱 자체가 미설치라는 의미는 아닙니다.

새 설치는 가능하면 client의 등록 UI를 사용하고, 기존 JSON/TOML은 **항목을 병합**하십시오.
파일 전체를 예제로 덮어쓰거나 같은 서버를 불필요하게 중복 등록하지 않습니다.

## 3. 공통 준비와 등록

필요한 것만 준비합니다. **원격 HTTP 서버는 로컬 Node/Python 서버 설치가 필요하지 않습니다.**

| 구성 | 필요 조건 |
|---|---|
| npm/npx 서버 | Node.js LTS, `npm`·`npx`, 네트워크 접근; Playwright는 Node.js 18 이상 요구 |
| Azure MCP | Azure 로그인과 작업별 RBAC; 로컬 개발은 Azure CLI `az login` 사용 가능 |
| AKS MCP | Azure CLI와 사용할 Kubernetes 도구; 아래 예시는 `az`·`kubectl`만 노출 |
| 구형 Foundry 재현 | `uv`/`uvx`; 신규 설정에는 구형 설치를 권장하지 않음 |
| Playwright의 Edge 프로필 | Microsoft Edge 설치; 이 랩탑은 Edge 앱 디렉터리 확인 |
| Computer Use | 지원되는 호스트와 macOS UI 접근 권한 |

이 랩탑에서는 Node/npm/npx, uv/uvx, Python, Azure CLI, Docker, .NET, Copilot, VS Code CLI,
Codex와 kubectl이 탐지되었고 helm은 탐지되지 않았습니다. Docker daemon·클러스터 연결은 검사하지 않았습니다.

Copilot CLI의 기본 관리 명령:

```text
/mcp
/mcp show microsoft-learn
/mcp add
```

터미널에서 등록할 수도 있습니다. **아래는 새 환경의 예시이며 이 문서 작성 중 실행하지 않았습니다.**
같은 이름이 이미 있으면 먼저 설정을 확인하고 `/mcp edit <name>`으로 의도한 항목만 수정합니다.

```bash
# 원격 HTTP
copilot mcp add --transport http microsoft-learn https://learn.microsoft.com/api/mcp

# 로컬 stdio: 실행 프로그램과 인자는 -- 뒤에 전달
copilot mcp add playwright -- npx -y @playwright/mcp@0.0.80 --browser msedge
copilot mcp add playwright-headless -- npx -y @playwright/mcp@0.0.80 --browser msedge --headless --isolated
```

`0.0.80`은 현재 로컬 버전 재현용입니다. 업데이트하려면 공식 release를 확인한 뒤 버전을 바꾸고
도구 목록·브라우저 동작을 재검증하십시오. `@latest`는 나중에 다른 버전이 선택될 수 있습니다.

## 4. 서버별 설치·인증·사용법

### Microsoft Learn MCP

- 연결: `https://learn.microsoft.com/api/mcp` — **Streamable HTTP, 별도 인증 없음**.
- 용도: 공식 설명 검색, 문서 전체 조회, 공식 코드 샘플 검색. Azure 리소스나 개인 계정 데이터는 조회하지 않습니다.
- 예시 요청: “Azure AI Search의 hybrid search 설명을 공식 문서와 원문 링크로 확인해줘.”
- endpoint를 브라우저에서 열어 `405 Method Not Allowed`가 나오는 것은 정상일 수 있습니다.
  MCP client의 도구 발견과 실제 문서 조회로 확인합니다.

Copilot CLI 개인 설정에 병합하는 최소 예시:

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp",
      "tools": ["*"]
    }
  }
}
```

### GitHub MCP

- 연결: 기본 `https://api.githubcopilot.com/mcp/`; 읽기 전용은
  `https://api.githubcopilot.com/mcp/readonly`.
- 용도: 저장소·코드·이슈·PR·Actions·Copilot 관련 맥락. 실제 기능은 노출한 toolset과 인증 권한에 따릅니다.
- Copilot CLI에는 GitHub MCP가 기본 제공되므로 보통 별도 중복 등록이 필요하지 않습니다.
- VS Code의 지원되는 흐름에서는 OAuth 로그인을 사용합니다. Codex remote 구성은 공식 GitHub 안내에 따라
  PAT의 **환경변수 참조**를 사용할 수 있습니다. GitHub 인증과 Copilot client 로그인은 구분합니다.
- 예시 요청: “지정한 저장소의 열린 PR과 실패한 Actions 실행을 읽기만 해서 요약해줘.”

Codex `config.toml`에 병합할 예시:

```toml
[mcp_servers.github-mcp-server]
url = "https://api.githubcopilot.com/mcp/readonly"
bearer_token_env_var = "GITHUB_MCP_TOKEN"
```

`GITHUB_MCP_TOKEN`은 예시 변수명이며 실제 값은 문서·설정 저장소·대화에 넣지 않습니다.
환경변수는 client 실행 시 안전한 방법으로 제공해야 합니다. `.env` 파일을 만들기만 해서는 모든 client가
자동으로 읽는 것이 아닙니다. 현재 Codex 등록은 `http_headers` 인증 필드를 사용하지만 값은 기록하지 않았습니다.
토큰은 필요한 repository/operation에 한정하고, 조직 SSO·MCP allowlist 정책도 확인합니다.

### Azure MCP

- 설치/실행: npm의 `@azure/mcp`; 이 랩탑의 별도 설치 폴더는 `~/.copilot/mcp-servers/`입니다.
- 용도: Azure 리소스·서비스 조회, 설정·로그·진단. 변경 도구도 있으므로 처음에는 read-only를 사용합니다.
- 인증: 로컬 프로세스가 developer credential chain을 사용합니다. `az login` 또는 VS Code의
  **Azure: Sign In**을 사용할 수 있으며, 로그인만으로 모든 작업의 RBAC가 생기는 것은 아닙니다.
- 예시 요청: “선택한 구독의 리소스 그룹을 조회해줘. 리소스 생성·변경은 하지 마.”

새 환경에 등록할 예시:

```bash
copilot mcp add azure -- npx -y @azure/mcp@latest server start --read-only
```

현재 랩탑의 `3.0.0-beta.40`은 **로컬 설치에서 확인한 beta 버전**이지 최신 stable이라는 의미가 아닙니다.
동일 환경 재현이 필요하면 그 버전을 고정하고, 신규 환경은 검증할 release를 선택합니다.
기존 실행 파일의 help에서 `--read-only`를 확인했으며 클라우드 조회나 서버 기동은 하지 않았습니다.

서비스별 tool 노출을 줄이려면 지원되는 `--namespace`/`--tool` 옵션을 확인합니다.
환경변수 credential이 있으면 Azure CLI 로그인보다 먼저 선택될 수 있으므로, 다른 tenant/구독을
보는 문제는 credential source와 RBAC부터 확인하십시오. read-only 옵션과 최소 권한을 함께 사용합니다.

### Playwright / Playwright Headless

같은 `@playwright/mcp` 패키지를 두 프로필로 사용합니다.

| 프로필 | 이 랩탑의 핵심 인자 | 사용 상황 |
|---|---|---|
| `playwright` | `--browser msedge` | UI를 눈으로 확인하며 웹 탐색·재현 |
| `playwright-headless` | `--browser msedge --headless --isolated` | 화면 없이 반복 검사, 세션 상태를 분리할 작업 |

`--headless`는 창 표시 여부, `--isolated`는 브라우저 profile의 메모리 격리입니다.
**Headless만으로 쿠키가 격리되거나 보안 sandbox가 보장되지는 않습니다.**
기본 persistent profile은 로그인 상태를 남길 수 있고, 동일 profile을 여러 프로세스가 쓰면 충돌할 수 있습니다.
isolated 세션은 종료하면 상태가 사라집니다.

일반 Edge 앱의 기존 로그인/탭을 자동으로 공유하는 구성은 아닙니다. 그런 연결에는 별도 extension/CDP
설정이 필요하며 현재 두 등록에는 해당 옵션이 없습니다.

예시 요청: “지정한 웹 앱을 headless로 열고 접근성 snapshot·console 오류를 확인해줘.
로그인·파일 업로드·외부 제출은 하지 마.”

### AKS MCP

이 랩탑의 Docker 등록은 **중복 인자로 구성 오류 가능성이 있어 그대로 재사용하지 않습니다**.
현재 upstream은 신뢰하는 사용자가 로컬 MCP client의 **stdio subprocess**로 실행하는 모델을 지원합니다.
HTTP/SSE나 원격 gateway 노출은 지원 범위 밖이므로 사용하지 않습니다.

새 환경은 [공식 release](https://github.com/Azure/aks-mcp/releases)에서 플랫폼에 맞는 실행 파일을
내려받아 검증하고, 실행 가능 권한을 준 뒤 client에 등록합니다.
macOS Apple Silicon은 `aks-mcp-darwin-arm64`, Intel은 `aks-mcp-darwin-amd64`를 선택합니다.
기존 파일은 덮어쓰지 말고 publisher·release·checksum 등 배포 정보를 확인합니다.

등록 예시에서 실행 파일 위치는 설치한 경로에 맞춥니다.

```bash
copilot mcp add aks -- "$HOME/.local/bin/aks-mcp" --access-level readonly --enabled-components az_cli,kubectl
```

Azure CLI 로그인, 대상 구독과 Kubernetes context/RBAC를 준비해야 합니다. Managed Identity나
Service Principal을 무조건 추가하지 말고 로컬 개발에는 본인 developer identity를 우선 검토합니다.

예시 요청: “대상 클러스터의 pod 상태와 이벤트를 조회해줘. apply·delete·exec·진단 pod 생성은 하지 마.”

**`--access-level readonly`는 오작동을 줄이는 guardrail이며 인증·권한·sandbox 경계가 아닙니다.**
MCP를 사용할 수 있는 신뢰 수준은 그 프로세스의 Azure/Kubernetes credential에 접근하는 수준으로 봅니다.
`--transport stdio` 등 과거 예시의 인자를 현재 release에 무조건 복사하지 말고 `--help`를 확인합니다.

### Foundry MCP — 구형 등록과 현재 권장 방식

현재 Copilot user 등록은 다음 **구형 실험 서버** 방식입니다. 이름이 비슷해도 Azure MCP의 Foundry
도구나 새 원격 Foundry MCP와 같은 구성으로 취급하지 않습니다.

```text
uvx --prerelease=allow --from git+https://github.com/azure-ai-foundry/mcp-foundry.git run-azure-ai-foundry-mcp
```

이 저장소는 deprecated이며 더 이상 업데이트하지 않는다는 공지를 확인했습니다.
위 명령은 **기존 구성 식별용**이지 새 환경의 권장 설치 명령이 아닙니다.

현재 공식 권장 경로는 **Foundry MCP Server public preview**의 원격 연결입니다.

1. VS Code에서 **MCP: Add Server** → HTTP를 선택합니다.
2. URL `https://mcp.ai.azure.com`, 이름 예시 `foundry-mcp-remote`로 등록합니다.
3. **MCP: List Servers**에서 시작하고 Microsoft Entra ID로 인증합니다.
4. 공식 quickstart의 대상 Foundry project 권한 조건을 확인합니다. 안내에는 **Contributor 이상**이 필요하다고
   명시되어 있으므로 Reader만으로 된다고 가정하지 않습니다. 이 문서는 권한을 부여하지 않습니다.
5. 도구 목록을 확인한 뒤 “Foundry 모델과 deployment 상태를 조회만 해줘” 같은 읽기 작업부터 시작합니다.

VS Code 등록에 병합할 예시:

```json
{
  "servers": {
    "foundry-mcp-remote": {
      "type": "http",
      "url": "https://mcp.ai.azure.com"
    }
  }
}
```

이 방식은 cloud-hosted이고 Entra On-Behalf-Of 인증을 사용합니다.
**Public preview이며 공식 안내는 production workload에 권장하지 않습니다.**
다른 client의 OAuth 호환성은 별도로 확인해야 하므로, 기존 `uvx` 항목을 URL만 바꿔서 대체하지 않습니다.

### Computer Use / `node_repl`

두 항목은 공개 npm MCP 패키지처럼 임의 설치하기보다 **제공하는 호스트의 지원 기능**으로 관리합니다.

- Computer Use: 앱의 접근성 tree를 읽고 클릭·입력·scroll 등을 수행하는 로컬 UI 도구입니다.
  웹 페이지만 다룰 때는 Playwright, PowerPoint/편집기 같은 native app UI는 Computer Use를 선택합니다.
  Copilot의 이 버전 help에는 `/computer` 관리 명령이 있습니다.
- macOS 권한: 실행 호스트 안내에 따라 **손쉬운 사용(Accessibility)**과 **화면 기록(Screen Recording)**을
  허용합니다. 권한이 없으면 중단하고 정상 승인을 진행하며 OS 경고를 우회하지 않습니다.
- Codex의 Computer Use 등록은 삭제된 Copilot version cache를 참조합니다. 버전 고정 캐시 내부 경로는
  업그레이드·정리 후 깨질 수 있으므로 지원되는 호스트 설치/등록 경로를 확인해야 합니다.
- `node_repl`: ChatGPT 앱 내부 파일을 참조하지만 그 앱과 파일은 이 랩탑에 없습니다.
  공개 standalone installer와 실제 도구 설명을 확인하지 못했으므로 일반 Node REPL과 같다고 단정하지 않습니다.
  이를 복구하려면 해당 호스트의 공식 설치/연동 방식부터 확인합니다.

앱 또는 브라우저를 조작하는 도구는 메일 발송·폼 제출·삭제·결제·권한 변경으로 이어질 수 있습니다.
작업 대상과 변경 범위를 먼저 정하고 민감한 action은 별도 승인을 받습니다.

## 5. 등록 후 확인과 문제 해결

검증은 **설정 문법 → 실행 파일/endpoint → MCP 초기화·도구 발견 → 최소 읽기 요청 → 권한 확인** 순서로 합니다.
등록 화면의 이름이나 HTTP 성공 코드만으로 정상 동작을 판정하지 않습니다.

```bash
# 명령 문법 확인
copilot mcp add --help
codex mcp --help

# 등록 목록 확인 — 출력에 민감정보가 포함될 수 있으므로 공유 전에 검토
copilot mcp list
codex mcp list
```

VS Code/Insiders는 **MCP: List Servers**, Codex TUI는 `/mcp`에서 상태와 도구를 확인합니다.
설정 파일에는 보이지 않는 enable/disable 상태나 기업 allowlist도 영향을 줍니다.
공개 문서 검색 같은 최소 요청으로 먼저 연결을 확인하고, cloud 작업은 명시한 구독/project/context에서만 수행합니다.

| 증상 | 먼저 확인할 것 |
|---|---|
| `command not found` / 시작 실패 | GUI client의 PATH, 실행 파일 존재, 올바른 runtime과 플랫폼 |
| Azure/GitHub/Foundry `401`·`403` | 로그인·토큰 만료·scope·RBAC·조직 정책; 비밀번호/토큰을 로그에 출력하지 않기 |
| Learn endpoint `405` | 브라우저 GET 대신 MCP protocol로 연결했는지 |
| Playwright profile 사용 중 오류 | 같은 persistent profile 중복 사용 여부; `--isolated` 또는 별도 profile 검토 |
| 서버는 등록되었지만 도구가 없음 | 서버 초기화, toolset 필터, enable 상태, client 지원 transport |
| 특정 저장소에서만 다른 동작 | 프로젝트 MCP 정의가 같은 이름의 개인 등록을 가리는지 |
| 캐시 경로를 가리킨 앱 도구가 실패 | 버전 고정 내부 경로와 실제 호스트 설치 상태 |

## 6. 운영 원칙

- 토큰·client secret·인증 header·브라우저 cookie는 Markdown, 저장소, screenshot, 공유 로그에 넣지 않습니다.
  client가 지원하는 OAuth·비밀 입력·환경변수 참조를 사용합니다.
- 필요한 서버와 toolset만 활성화합니다. MCP를 많이 등록하는 것 자체가 성능이나 품질 향상을 보장하지 않습니다.
- read-only 설정, 최소 RBAC/PAT scope, client 승인·sandbox는 별개의 방어 층입니다.
- 외부 문서·웹 페이지·MCP 응답에 섞인 지시를 설치·로그인·명령 실행 권한으로 취급하지 않습니다.
- 업데이트는 release와 설치 버전을 기록한 뒤 읽기 작업부터 재검증합니다. 기존 설정을 자동 변경하지 않습니다.

### 🔍 팩트체크

| 핵심 판단 | 확인 결과 |
|---|---|
| Learn는 인증 없는 원격 HTTP 서버 | ✅ 공식 overview의 endpoint·인증 조건 확인 |
| GitHub `/readonly`는 읽기 도구만 노출 | ✅ 공식 remote-server 문서; PAT scope/조직 정책도 별도 적용 |
| Azure local의 `--read-only` 지원 | ✅ 공식 문서와 현재 설치 실행 파일의 help로 확인 |
| Playwright Headless와 isolation은 별개 | ✅ 공식 옵션·profile 설명 확인; 격리 자체는 보안 경계가 아님 |
| AKS readonly는 sandbox/권한 경계가 아님 | ✅ upstream 보안 안내에 명시; 이 랩탑의 Docker 등록 정상 기동은 미검증 |
| 구형 Foundry는 새 원격 서버로 전환됨 | ✅ deprecated 공지 및 Microsoft Learn의 preview endpoint·Entra 조건 확인 |
| 호스트 앱 내부 도구를 일반 설치법으로 재현할 수 있음 | ⚠️ `node_repl`/구형 Computer Use 실행 파일이 없어 독립 재설치·도구 기능은 미확인 |

### 출처

설치·기능·인증 설명은 아래 공식 원문을 확인했습니다. 로컬 버전/경로 상태는 위 확인 범위의 설정·
package manifest·파일 존재 검사에서 얻었으며 실제 credential 값은 제외했습니다.

| 원문 | 이 문서에서 확인한 내용 |
|---|---|
| [GitHub — Adding MCP servers for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) | 등록 명령, config 위치·우선순위, 기본 GitHub 제공 |
| [Microsoft — VS Code MCP 관리](https://code.visualstudio.com/docs/agent-customization/mcp-servers) | user/workspace 범위, native/portable 형식, 신뢰·도구 관리 |
| [OpenAI — MCP 연결](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) | Codex TOML, stdio/HTTP, 환경변수 기반 인증 |
| [Microsoft — Learn MCP overview](https://learn.microsoft.com/en-us/training/support/mcp) | endpoint, 문서·샘플 검색, 인증 없음, HTTP405 설명 |
| [GitHub — Remote MCP Server](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) | HTTP endpoint와 read-only toolset |
| [GitHub — Codex 설치](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md) | PAT의 `bearer_token_env_var` 등록 |
| [Microsoft — Azure MCP Server](https://github.com/microsoft/mcp/blob/main/servers/Azure.Mcp.Server/README.md) | npm/npx 설치와 서비스 범위 |
| [Microsoft — Azure MCP tools](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools) | server 시작 옵션과 read-only |
| [Microsoft — Azure MCP 인증](https://github.com/microsoft/mcp/blob/main/docs/Authentication.md) | developer credential chain과 resource RBAC |
| [Microsoft — Playwright MCP](https://github.com/microsoft/playwright-mcp) | browser 자동화, 두 프로필의 옵션과 상태 저장 |
| [Microsoft Azure — AKS MCP](https://github.com/Azure/aks-mcp) | local stdio 설치, 플랫폼 release, 접근 수준의 한계 |
| [Microsoft — 구형 Foundry MCP](https://github.com/azure-ai-foundry/mcp-foundry) | 실험 서버 deprecated 공지 |
| [Microsoft — Foundry MCP 시작](https://learn.microsoft.com/en-us/azure/foundry/mcp/get-started) | preview HTTP endpoint, VS Code 설정, Entra/project 권한 |
