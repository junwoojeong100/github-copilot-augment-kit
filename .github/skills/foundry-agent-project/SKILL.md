---
name: foundry-agent-project
description: "Microsoft Foundry로 에이전트를 정의하고, Microsoft Agent Framework(Python SDK)로 워크플로우를 구성하는 프로젝트를 처음부터 생성·가이드·배포합니다. 기존 Foundry 샘플이 아닌 커스텀 프로젝트 구조를 직접 설계합니다. WHEN: Foundry 에이전트 프로젝트 생성, Agent Framework 프로젝트 시작, Foundry 워크플로우 프로젝트, create Foundry agent project, scaffold agent project, new agent app, Foundry agent from scratch, multi-agent workflow project, create agent workflow, 에이전트 앱 만들기, 에이전트 프로젝트 초기화, Agent Framework 워크플로우, Foundry 프로젝트 세팅, 에이전트 배포 프로젝트, bootstrap agent app, init agent project, agent project template, Foundry starter project, setup agent dev environment, agent boilerplate."
argument-hint: "에이전트의 목적과 사용할 도구/데이터 소스를 설명하세요"
---

# Foundry Agent Project

Microsoft Foundry + Microsoft Agent Framework(Python SDK) 기반 에이전트 프로젝트를 처음부터 생성하고, 워크플로우를 구성하며, Foundry에 배포하는 전체 워크플로우를 안내합니다.

## When to Use

- **커스텀 프로젝트 설계**: Foundry 샘플이 아닌, 요구사항에 맞는 프로젝트 구조를 처음부터 설계할 때
- **멀티에이전트 워크플로우**: 여러 에이전트를 조합한 워크플로우 프로젝트를 구성할 때
- **기존 앱 에이전트화**: 기존 Python 앱에 에이전트 기능을 추가할 때
- **프로젝트 템플릿**: Agent Framework 프로젝트의 표준 구조가 필요할 때

> **기존 스킬과의 차이**: `microsoft-foundry` → `create`는 Foundry 공식 샘플을 다운로드하여 시작합니다. 이 스킬은 사용자 요구사항을 인터뷰하여 **커스텀 구조를 직접 설계**합니다. `microsoft-foundry-agent-framework-code-gen`은 이미 존재하는 코드의 수정/개선에 초점을 맞춥니다.

## DO NOT USE FOR

> 아래에서 참조하는 `microsoft-foundry`, `microsoft-foundry-agent-framework-code-gen`, `azure-prepare` 등은 VS Code Copilot의 내장 스킬(built-in)이며, 이 리포지토리에는 포함되어 있지 않습니다.

- 이미 코드가 있는 에이전트 배포만 → `microsoft-foundry` 스킬의 `deploy` 서브스킬 사용
- 기존 에이전트 코드의 수정/디버그/개선 → `microsoft-foundry-agent-framework-code-gen` 스킬 사용
- Foundry 공식 샘플 기반 빠른 시작 → `microsoft-foundry` → `create` 서브스킬 사용
- Foundry 리소스/RBAC/모델 관리 → `microsoft-foundry` 스킬 사용
- Azure Functions/App Service 배포 → `azure-prepare` 스킬 사용

## Workflow

### Phase 1: 요구사항 수집

사용자에게 다음을 확인합니다:

| 항목 | 설명 | 예시 |
|------|------|------|
| **에이전트 목적** | 에이전트가 수행할 핵심 작업 | "고객 문의 자동 응답", "코드 리뷰 자동화" |
| **도구(Tools)** | 에이전트가 사용할 외부 도구/API | Bing Search, Azure AI Search, Code Interpreter |
| **데이터 소스** | 참조할 데이터/지식 베이스 | Azure Blob, SharePoint, Custom API |
| **에이전트 수** | 단일 에이전트 vs 멀티에이전트 | 단일 / 2~3개 조합 |
| **워크플로우 패턴** | 에이전트 간 협업 방식 | Sequential, Parallel, Router, Handoff |
| **Foundry 프로젝트** | 기존 Foundry 프로젝트 유무 | 신규 생성 / 기존 사용 |

### Phase 2: 프로젝트 스캐폴딩

#### Step 1: 프로젝트 구조 생성

```
<project-root>/
├── pyproject.toml              # 패키지 정의 및 의존성
├── Dockerfile                  # 컨테이너 빌드
├── .env.example                # 환경변수 템플릿
├── .foundry/
│   └── agent-metadata.yaml     # Foundry 메타데이터
├── src/
│   └── <project_name>/
│       ├── __init__.py
│       ├── app.py              # HTTP 서버 엔트리포인트
│       ├── agents/
│       │   ├── __init__.py
│       │   └── <agent_name>.py # 에이전트 정의
│       ├── tools/
│       │   ├── __init__.py
│       │   └── <tool_name>.py  # 커스텀 도구 정의
│       └── workflows/
│           ├── __init__.py
│           └── <workflow>.py   # 워크플로우 오케스트레이션
└── tests/
    ├── __init__.py
    └── test_<agent_name>.py    # 에이전트 테스트
```

#### Step 2: 핵심 파일 생성

**pyproject.toml** — 최신 SDK 의존성 선언:
```toml
[project]
name = "<project-name>"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "agent-framework",   # 전체 통합 설치 (경량 대안: agent-framework-core + agent-framework-foundry)
    "azure-identity",    # AzureCliCredential / DefaultAzureCredential
    "aiohttp",           # HTTP 서버 엔트리포인트(선택)
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

> 📌 패키지·API는 계속 진화하므로, 최신 버전·패턴은 공식 [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) 문서/샘플에서 확인하세요. (AI Toolkit의 `aitk-*` 도구가 있는 환경에서는 함께 활용)

**Dockerfile** — Foundry 호스팅 호환:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .
EXPOSE 8080
CMD ["python", "-m", "<project_name>.app"]
```

**.env.example** — 필수 환경변수 문서화:
```env
# Microsoft Foundry (Azure AI Foundry) 프로젝트
FOUNDRY_PROJECT_ENDPOINT=
FOUNDRY_MODEL=gpt-4o

# 대안: Azure OpenAI 직접 사용
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_MODEL=
# 인증: az login 기반 AzureCliCredential 권장 (키 사용 시에만 AZURE_OPENAI_API_KEY)
```

#### Step 3: 에이전트 정의

Microsoft Foundry 프로젝트의 모델에 `FoundryChatClient`로 연결하여 에이전트를 정의합니다.

단일 에이전트 패턴:
```python
# src/<project_name>/agents/<agent_name>.py
import os
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential


def create_agent() -> Agent:
    return Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
            credential=AzureCliCredential(),
        ),
        name="<agent-name>",
        instructions="""
        <에이전트 역할과 지침을 여기에 정의>
        """,
        tools=[
            # Foundry 호스티드 도구 팩토리
            FoundryChatClient.get_web_search_tool(),
            FoundryChatClient.get_code_interpreter_tool(),
            # 커스텀 함수 도구는 @tool 데코레이터 함수를 직접 전달
            # 지식 검색: FoundryChatClient.get_azure_ai_search_tool(index_connection_id=..., index_name=...)
        ],
    )
```

#### Step 4: 워크플로우 구성 (멀티에이전트 시)

여러 에이전트를 조합할 때는 `agent_framework.orchestrations`의 빌더를 사용합니다.

| 패턴 | 빌더 | 사용 시기 |
|------|------|----------|
| **Sequential** | `SequentialBuilder` | A → B → C 순차 처리 파이프라인 |
| **Concurrent** | `ConcurrentBuilder` | 독립 하위 작업 병렬 처리 후 집계 |
| **Group Chat** | `GroupChatBuilder` | 여러 에이전트의 협업 대화 |
| **Handoff / Magentic** | (고급 패턴) | 동적 위임·플래너 기반 오케스트레이션 |

**Sequential 워크플로우 예시:**
```python
# src/<project_name>/workflows/sequential.py
from agent_framework.orchestrations import SequentialBuilder

async def run_pipeline(user_input: str):
    """Writer → Reviewer 순차 파이프라인"""
    writer = create_writer_agent()
    reviewer = create_reviewer_agent()

    workflow = SequentialBuilder(participants=[writer, reviewer]).build()
    result = await workflow.run(user_input)
    return result
```

**Concurrent(병렬) 워크플로우 예시:**
```python
# src/<project_name>/workflows/concurrent.py
from agent_framework.orchestrations import ConcurrentBuilder

async def run_parallel(user_input: str):
    """여러 전문가 에이전트를 병렬 실행 후 집계"""
    workflow = ConcurrentBuilder(
        participants=[create_research_agent(), create_market_agent(), create_legal_agent()],
    ).build()
    result = await workflow.run(user_input)
    return result
```

> 📌 Group Chat·Handoff·Magentic 등 고급 패턴과 커스텀 그래프(`WorkflowBuilder`)는 공식 [Agent Framework 샘플](https://github.com/microsoft/agent-framework/tree/main/python/samples)을 참조하세요. `workflows/` 디렉토리는 `agents/`에 정의된 에이전트를 조합하는 오케스트레이션 로직을 담습니다.

#### Step 5: HTTP 서버 엔트리포인트

```python
# src/<project_name>/app.py
from aiohttp import web
from .agents.<agent_name> import create_agent

agent = create_agent()

async def handle_message(request: web.Request) -> web.Response:
    body = await request.json()
    result = await agent.run(body.get("message", ""))
    return web.json_response({"reply": result.text})

app = web.Application()
app.router.add_post("/api/messages", handle_message)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
```

> 호스팅 대안: 로컬 디버깅 UI는 `agent-framework-devui`, Foundry 호스팅은 `agent-framework-foundry-hosting`(foundry_hosting) 패키지를 검토하세요.

### Phase 3: 로컬 개발 및 테스트

#### Step 1: 환경 설정

```bash
# 가상환경 생성 및 의존성 설치
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 환경변수 설정
cp .env.example .env
# .env 파일에 실제 값 입력
```

#### Step 2: 로컬 실행

```bash
python -m <project_name>.app
```

#### Step 3: 테스트

```bash
pytest tests/ -v
```

### Phase 4: Foundry 배포

> 이 단계에서는 `microsoft-foundry` 스킬의 서브스킬들을 순서대로 활용합니다.

#### Step 1: Foundry 프로젝트 준비

기존 프로젝트가 없으면 `microsoft-foundry` → `project/create` 서브스킬로 생성합니다.

#### Step 2: `.foundry/agent-metadata.yaml` 설정

```yaml
project:
  subscription_id: "<subscription-id>"
  resource_group: "<resource-group>"
  project_name: "<foundry-project-name>"

agent:
  name: "<agent-name>"
  description: "<에이전트 설명>"

registry:
  acr_name: "<acr-name>"
  image_name: "<project-name>"
  image_tag: "latest"
```

#### Step 3: 빌드 및 배포

`microsoft-foundry` → `deploy` 서브스킬을 호출하여 다음을 수행합니다:

1. Docker 이미지 빌드
2. ACR에 푸시
3. Foundry 에이전트 생성/업데이트
4. 컨테이너 시작

> **⚠️ 시크릿 관리**: `.env` 파일은 로컬 개발 전용입니다. 프로덕션 배포 시에는 Azure Managed Identity 인증과 Key Vault 참조를 사용하여 시크릿을 관리하세요.

#### Step 4: 배포 검증

`microsoft-foundry` → `invoke` 서브스킬로 배포된 에이전트를 테스트합니다.

### Phase 5: 평가 및 최적화 (선택)

배포 후 에이전트 품질 개선이 필요하면:

1. `microsoft-foundry` → `observe` 서브스킬로 평가 실행
2. 프롬프트 최적화 수행
3. 재배포

## Error Handling

| 상황 | 처리 방법 |
|------|----------|
| `aitk-*` 도구 사용 불가 | 공식 Agent Framework 문서/샘플(github.com/microsoft/agent-framework) 기준으로 코드를 생성·검증하고, 그대로 진행 |
| Foundry 프로젝트 접근 불가 | 로컬 개발 환경(pyproject.toml, src/, tests/)까지만 구성하고, 배포 단계는 Foundry 접근 확보 후 진행하도록 안내 |
| Docker 미설치 | Dockerfile은 생성하되, 로컬 실행(`python -m`)까지만 안내. 컨테이너 빌드·배포는 Docker 설치 후 진행 |
| SDK 호환성 문제 | pyproject.toml에 버전을 핀하지 않고, 사용자에게 최신 호환 버전 확인을 요청 |

## Output Format

프로젝트 생성 완료 시 아래 형식으로 요약합니다:

```markdown
## ✅ 프로젝트 생성 완료

**프로젝트명**: <project-name>
**에이전트**: <에이전트 이름 및 역할>
**워크플로우**: <패턴 유형>
**언어**: Python (Microsoft Agent Framework)

### 생성된 파일
- `pyproject.toml` — 패키지 및 의존성
- `Dockerfile` — 컨테이너 빌드
- `src/<project_name>/agents/` — 에이전트 정의
- `src/<project_name>/workflows/` — 워크플로우 구성
- `.foundry/agent-metadata.yaml` — Foundry 메타데이터

### 다음 단계
1. `.env`에 `FOUNDRY_PROJECT_ENDPOINT` 등 Microsoft Foundry 연결 정보 입력
2. `pip install -e ".[dev]"` 로 의존성 설치
3. 로컬에서 테스트 후 Foundry 배포
```

## 사전 조건

| 항목 | 설명 |
|------|------|
| Python | 3.10 이상 |
| Azure 구독 | Microsoft Foundry(Azure AI Foundry) 프로젝트 접근 가능 |
| Docker | 컨테이너 빌드용 (배포 시 필요) |
| Azure CLI | `az login` 완료 상태 |
