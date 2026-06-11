---
name: google-web-search
description: "최신 정보가 필요할 때 Google 웹 검색을 수행하여 실시간 정보를 수집하고 요약합니다. 학습 데이터 이후의 최신 뉴스, 기술 업데이트, 릴리스 정보, 가격 변경, 이벤트, 규제 동향, 전략 리포트 등을 검색합니다. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, 최신 뉴스, 최근 업데이트, 릴리스 노트, 최신 버전, 현재 가격, 현재 상태, latest news, recent updates, current price, what's new, release notes, changelog, web search, search the web, look up online, 오늘 날짜 기준 정보, 2024년 이후 정보, 최신 트렌드, 기술 동향, 최근 발표, 공식 발표, 최신 문서, AI 규제 동향, EU AI Act, GDPR, 컴플라이언스 요구사항, 규정 준수, 개인정보보호법, ISO 27001, NIST, 최신 IT 전략 동향, AX 전략 리포트 검색, 클라우드 전략 동향, AI 도입 사례, 시장 동향 분석, 산업 전략 리포트."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# Google 웹 검색 스킬

AI 모델의 학습 데이터 컷오프 이후의 **최신 정보**가 필요할 때, 웹 검색을 통해 실시간 정보를 수집하고 정리합니다.

## When to Use

- **최신 버전/릴리스 확인**: 라이브러리, 프레임워크, 서비스의 최신 버전 정보
- **최근 뉴스/발표**: 기술 업데이트, 서비스 변경, 정책 변경 등
- **현재 가격/요금**: 클라우드 서비스, API 요금 등 실시간 가격 정보
- **최신 문서/가이드**: 공식 문서의 최신 내용 확인
- **트렌드/동향**: 최신 기술 트렌드, 시장 동향
- **이벤트/컨퍼런스**: 예정된 또는 최근 이벤트 정보
- **버그/이슈 상태**: 특정 이슈의 현재 상태 확인
- **규제/컴플라이언스**: EU AI Act, GDPR, 개인정보보호법(PIPA), ISO/NIST 표준 등 규제 요건 확인
- **전략/시장 동향**: IT·AX·클라우드·AI 도입 전략, 산업 분석 리포트 확인

## Workflow

### Step 1: 검색 쿼리 구성

사용자의 질문을 분석하여 효과적인 검색 쿼리를 구성합니다.

**쿼리 구성 원칙:**
- 핵심 키워드를 영어로 변환 (영어 결과가 더 풍부)
- 연도/날짜를 포함하여 최신 결과 유도 (예: "2025", "2026")
- 구체적인 기술 용어 사용
- 불필요한 조사/접속사 제거

**소스 선택 정책 (동적):**

검색 소스는 **고정 허용목록으로 미리 한정하지 않습니다.** 질문 주제에 맞는 **가장 권위 있는 1차 출처를 그때그때 탐색·검증하여 선택**합니다. 이렇게 하면 기관 도메인이 바뀌거나(예: 부처 도메인 개편) 처음 다루는 주제가 나와도 유연하게 대응할 수 있습니다. 고정 목록을 계속 늘리는 대신, **신뢰도 평가 기준**으로 소스를 판단합니다.

### 소스 신뢰도 평가 기준

후보 소스를 fetch하기 전에 아래 기준으로 신뢰도를 판단합니다:

| 기준 | 판단 질문 |
|------|----------|
| **1차성(Primary)** | 해당 주제를 직접 만들거나 관할하는 주체인가? (벤더 공식 문서, 법령 원문, 규제기관 공식 사이트, 표준화 기구) |
| **권위(Authority)** | 공식·공인된 기관/매체인가? 정부(`*.go.kr`, `*.gov`, `europa.eu`), 표준기구, 공식 벤더 도메인인가? |
| **검증가능성(Verifiability)** | 작성 주체·게시일이 명확하고 출처 추적이 가능한가? |
| **최신성(Recency)** | 게시/갱신 날짜가 주제에 비추어 충분히 최신인가? |
| **교차검증(Corroboration)** | 독립된 다른 신뢰 소스와 일치하는가? |

### 소스 우선순위 (동적 적용)

1. **1차 출처** — 주제 관할 주체의 공식 문서·법령 원문·규제기관 공지·표준 문서
2. **공신력 있는 2차 출처** — 표준기구, 주요 분석기관, 학술(arXiv 등), 주요 언론
3. **커뮤니티/실무 소스** — 기술 Q&A, 기술 블로그 (반드시 1·2차 출처로 교차검증)

### 자주 쓰는 앵커 소스 (예시 — 이에 한정하지 않음)

빠른 시작을 위한 **참고 목록일 뿐**이며, 더 적합한 공식 소스를 발견하면 신뢰도 기준을 통과하는 한 자유롭게 탐색·사용합니다.

- **Microsoft/Azure/GitHub**: `learn.microsoft.com`, `azure.microsoft.com`, `devblogs.microsoft.com`, `techcommunity.microsoft.com`, `servicetrust.microsoft.com`, `github.blog`, `docs.github.com`
- **AI 벤더/연구**: `openai.com`, `anthropic.com`, `ai.google.dev`, `huggingface.co`, `arxiv.org`, `nvidia.com`
- **비교용 클라우드/도구**: `aws.amazon.com`, `cloud.google.com`, `docs.gitlab.com`, `kubernetes.io`, `terraform.io`
- **규제·표준 (글로벌)**: `eur-lex.europa.eu`, `digital-strategy.ec.europa.eu`, `iso.org`, `nist.gov`
- **규제 (국내)**: `law.go.kr`(법령 원문), `pipc.go.kr`(개인정보), `kisa.or.kr`(보안·ISMS-P), `msit.go.kr`(ICT·AI), `fsc.go.kr`(금융위원회), `fss.or.kr`(금융감독원), `fsec.or.kr`(금융보안원), `motie.go.kr`(산업통상자원부·국가핵심기술), `kaits.or.kr`(산업기술보호협회)
- **전략·분석**: `oecd.org`, `weforum.org`, `imf.org`, `worldbank.org`, `gartner.com`·`mckinsey.com`(일부 페이월)

> ⚠️ 위 도메인은 **출발점**이며 닫힌 화이트리스트가 아닙니다. 정부 기관·표준 문서 등 주제별 더 권위 있는 1차 출처를 발견하면 우선 사용하고, 도메인 변경·리다이렉트 가능성(예: 부처 개편으로 기존 도메인이 새 도메인으로 이전)을 항상 고려합니다.

### 동적 소스 탐색 절차

1. 질문에서 **주제 영역**과 **권위 주체 유형**을 식별합니다. (예: "국가핵심기술" → 소관 부처·산업기술보호법)
2. 검색 엔진으로 **현재 유효한 공식 소스 URL**을 발견합니다. (도메인 개편·이전 가능성 고려)
3. 위 신뢰도 평가 기준으로 후보를 선별합니다.
4. 1차 출처를 우선 fetch하고, 2차 출처로 교차검증합니다.

**사용자 지정 도메인:** 사용자가 특정 도메인을 명시하면 해당 도메인을 우선 사용합니다.

### Microsoft/Azure/GitHub 주제 — 가치·서비스 수집 가이드

클라우드·AI 전략, 솔루션 조사, 경쟁 비교, 발표자료 기초 조사 등에서 주제가 Microsoft/Azure/GitHub와 관련되면, 단순 사실 확인을 넘어 **구체적인 서비스 역량과 차별화 가치**까지 함께 수집합니다.

1. **공식 1차 소스 우선**: `learn.microsoft.com`, `azure.microsoft.com`, `devblogs.microsoft.com`, `techcommunity.microsoft.com`, `servicetrust.microsoft.com`, `github.blog`, `docs.github.com`을 우선 fetch합니다.
2. **구체 서비스명으로 수집**: "AI"·"클라우드" 같은 일반어가 아니라 **정확한 서비스명**(예: Microsoft Foundry, Azure AI Search, Azure AI Content Safety, Prompt Shields, Confidential Computing, Microsoft Entra/Entra Agent ID, Microsoft Purview, Microsoft Defender for Cloud, GitHub Copilot/Advanced Security, Microsoft Fabric)으로 기능·가치·근거를 정리합니다.
3. **가치 포인트 캡처**: 각 서비스가 주는 *통제·보안·생산성·통합·규제 대응* 가치를 한 줄로 요약해 둡니다. (전략/슬라이드 산출물에서 바로 활용)
4. **규제 산업 보강**: 금융·공공·의료 주제면 데이터 레지던시·인증(K-ISMS, CSAP 등)·감사·기밀 컴퓨팅 관련 공식 문서를 추가로 확인합니다.
5. **객관성 유지**: 경쟁사 대비 우열 주장은 1차 출처로 교차검증하고, 비교가 핵심이면 `cloud-competitive-analysis` 스킬과 연계합니다. 과장 없이 사실 기반으로 정리합니다.

> 이 가이드는 `it-ai-strategy-advisory`·`cloud-competitive-analysis`·`slide-generator` 스킬의 기초 자료 조사를 강화하기 위한 것입니다.

**제외 기준:** 작성 주체·날짜가 불명한 개인 블로그, SEO 스팸·콘텐츠팜, 출처를 추적할 수 없는 사이트 등 신뢰도 기준을 충족하지 못하는 소스는 사용하지 않습니다.

**검색 쿼리 예시:**

> ⚠️ 검색 쿼리의 연도는 반드시 **현재 연도**를 사용합니다. 아래 예시의 연도는 설명용입니다.

| 사용자 질문 | 최적화된 쿼리 |
|------------|-------------|
| "React 최신 버전이 뭐야?" | `React latest version {current_year} site:react.dev OR site:github.com/facebook/react` |
| "Azure Functions 요금 변경됐어?" | `Azure Functions pricing changes {current_year} site:microsoft.com` |
| "Python 3.13 새 기능" | `Python 3.13 new features changelog site:python.org OR site:github.com` |
| "Kubernetes 최신 동향" | `Kubernetes latest trends {current_year} site:kubernetes.io OR site:github.com` |
| "EU AI Act 고위험 AI 의무" | `EU AI Act high-risk obligations site:eur-lex.europa.eu OR site:digital-strategy.ec.europa.eu` |
| "Azure 규정 준수 인증 목록" | `Azure compliance certifications site:learn.microsoft.com OR site:servicetrust.microsoft.com` |
| "생성형 AI 도입 전략 동향" | `generative AI adoption strategy {current_year} site:weforum.org OR site:oecd.org OR site:mckinsey.com` |

### Step 2: 웹 검색 수행

`fetch_webpage` 도구를 사용하여 검색을 수행합니다.

> **⚠️ `fetch_webpage` 도구를 사용할 수 없는 경우**: MCP 도구(`mcp_microsoft_pla_browser_navigate` 등)나 `run_in_terminal`의 `curl` 명령으로 대체합니다. 어떤 웹 접근 도구도 사용할 수 없다면, 학습 데이터 기반으로 답변하되 "실시간 검색을 수행할 수 없어 학습 데이터 기준으로 답변합니다"라고 명시합니다.

**검색 전략 (용도별):**

`google.com/search`는 봇 감지로 결과를 반환하지 않는 경우가 많으므로, 용도에 맞는 검색 엔드포인트를 사용합니다.

**뉴스/최신 정보 → Google News (가장 안정적)**
```
https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en
```
- 최신 뉴스, 속보, 기술 업데이트, 릴리스 발표 등에 적합

**일반 웹 문서 → DuckDuckGo HTML (봇 감지 없음)**
```
https://html.duckduckgo.com/html/?q={encoded_query}
```
- 공식 문서, 기술 블로그, 가이드, 릴리스 노트 등 일반 웹 문서 검색에 적합
- JavaScript가 불필요한 순수 HTML 버전이라 `fetch_webpage`와 100% 호환
- 검색 결과에서 URL을 추출한 뒤, **신뢰도 기준을 통과한 1차·공신력 소스의 링크만 상세 fetch**

**공식 소스 직접 접근 (URL을 이미 알거나 추론 가능한 경우)**
검색 주제에 따라 신뢰할 수 있는 공식 페이지를 직접 fetch합니다:
- `https://github.blog/tag/{topic}/` — GitHub 관련 뉴스
- `https://learn.microsoft.com/en-us/{path}` — Microsoft/Azure 공식 문서
- `https://devblogs.microsoft.com/{path}` — Microsoft 개발자 블로그
- `https://github.com/{owner}/{repo}/releases` — 릴리스 정보

**Google 검색 (최후의 수단)**
```
https://www.google.com/search?q={encoded_query}
```
> ⚠️ `google.com/search`가 JavaScript 챌린지 페이지를 반환하면, 재시도하지 않고 즉시 다른 방법으로 전환합니다.

**⚠️ 검색 엔진 vs 결과 소스 구분:**
- **검색 엔진** (URL 발견용): Google News, DuckDuckGo HTML, Google Search 모두 사용 가능
- **결과 소스** (상세 내용 fetch용): 신뢰도 평가 기준을 통과한 1차·공신력 소스만 fetch (신뢰도 미달 소스는 fetch 금지)

**검색 실행 예시:**

```
# 뉴스/최신 정보
fetch_webpage:
- urls: ["https://news.google.com/search?q={검색어}&hl=en-US&gl=US&ceid=US:en"]
- query: "찾고자 하는 정보"

# 일반 웹 문서/기술 문서
fetch_webpage:
- urls: ["https://html.duckduckgo.com/html/?q={검색어}"]
- query: "찾고자 하는 정보"
```

### Step 3: 상세 정보 수집

검색 결과에서 유망한 링크를 식별하고, 해당 페이지의 상세 내용을 가져옵니다.

```
fetch_webpage 도구를 사용:
- urls: ["발견된 관련 URL 1", "발견된 관련 URL 2"]
- query: "찾고자 하는 구체적인 정보"
```

**소스 우선순위:**
1. **공식 프로젝트 사이트** — 해당 기술의 공식 도메인 (react.dev, python.org, kubernetes.io 등)
2. **Microsoft 공식 문서** — `learn.microsoft.com`, `devblogs.microsoft.com`
3. **GitHub 공식 블로그/릴리스** — `github.blog`, `github.com/{owner}/{repo}/releases`
4. **패키지 레지스트리** — `npmjs.com`, `pypi.org` 등
5. **YouTube 공식 채널** — 데모, 튜토리얼
6. **커뮤니티** — `stackoverflow.com`, `dev.to` (교차 검증 후 사용)

> ⚠️ 비공식 소스(dev.to, medium.com, stackoverflow.com)의 정보는 공식 문서와 교차 검증하여 정확성을 확인합니다.

### Step 4: 결과 정리 및 응답

수집된 정보를 다음 형식으로 정리합니다:

```markdown
## 검색 결과: {주제}

**검색일**: {현재 날짜}
**검색 쿼리**: `{사용된 쿼리}`

### 핵심 요약
{1-3문장으로 핵심 답변}

### 상세 내용
{구조화된 상세 정보}

### 출처
- [출처 제목 1](URL1) — {간략 설명}
- [출처 제목 2](URL2) — {간략 설명}

> ⚠️ 웹 검색 결과는 검색 시점 기준이며, 정확성을 보장하지 않습니다.
> 중요한 의사결정에는 공식 문서를 직접 확인하시기 바랍니다.
```

## 검색 전략

### 기본 검색
단일 쿼리로 빠르게 결과를 얻습니다.

### 심화 검색
하나의 주제에 대해 여러 각도로 검색합니다. 아래 `site:` 예시는 **고정 규칙이 아니라 출발점**이며, 주제에 더 맞는 공식 소스를 발견하면 그쪽을 우선합니다:
1. **개요 파악**: 주제 관할 주체의 공식 도메인에서 개요 파악
2. **공식 문서 검색**: 벤더/기관 공식 문서로 한정 (예: `site:learn.microsoft.com`, `site:docs.github.com`)
3. **1차 출처 확인**: 법령·표준·릴리스 원문 직접 확인 (예: `site:eur-lex.europa.eu`, `site:law.go.kr`)
4. **영상 콘텐츠 검색**: `site:youtube.com` 한정 (데모, 튜토리얼)
5. **AI 연구 검색**: `site:arxiv.org OR site:huggingface.co` 한정
6. **규제/컴플라이언스 검색**: 관할 기관·법령으로 동적 한정 (예: `site:digital-strategy.ec.europa.eu`, `site:pipc.go.kr`, `site:fsc.go.kr`, `site:motie.go.kr`)
7. **전략/분석 검색**: `site:oecd.org OR site:weforum.org OR site:gartner.com OR site:mckinsey.com` 한정

### 비교 검색
두 가지 이상의 대안을 비교할 때:
1. 각 대안별 개별 검색
2. 비교 키워드로 통합 검색 (`A vs B 2026`)
3. 벤치마크/리뷰 검색

## Google 검색 고급 연산자

유용한 검색 연산자를 활용합니다:

| 연산자 | 용도 | 예시 |
|--------|------|------|
| `site:` | 특정 사이트 내 검색 | `site:github.com kubernetes release` |
| `"exact phrase"` | 정확한 문구 검색 | `"breaking changes" React 19` |
| `after:` | 특정 날짜 이후 결과 | `Azure updates after:2025-01-01` |
| `filetype:` | 파일 유형 필터 | `kubernetes best practices filetype:pdf` |
| `-keyword` | 특정 키워드 제외 | `python web framework -django` |
| `OR` | 여러 키워드 중 하나 | `(React OR Vue) state management 2026` |

## Error Handling

| 상황 | 처리 방법 |
|------|----------|
| 검색 엔진 접근 불가 | Google News → DuckDuckGo HTML → 공식 소스 직접 접근 순으로 폴백. 모두 실패 시 학습 데이터 기반으로 답변하되 "실시간 검색을 수행할 수 없어 학습 데이터 기준으로 답변합니다"라고 명시 |
| 검색 결과 없음 | 쿼리를 재구성(키워드 변경, 범위 확대)하여 1회 재시도. 그래도 없으면 "해당 주제에 대한 최신 검색 결과를 찾지 못했습니다"라고 안내 |
| 비신뢰 소스만 반환 | 비공식 소스의 정보를 사용하지 않고, "신뢰할 수 있는 공식 소스에서 관련 정보를 찾지 못했습니다. 공식 문서를 직접 확인하시기 바랍니다"라고 안내 |
| JavaScript 챌린지/봇 차단 | 해당 엔드포인트를 재시도하지 않고 즉시 다른 검색 방법으로 전환 |
| 검색 결과 상충 | 출처 간 정보가 상충할 경우 양쪽 정보를 모두 제시하고, 공식 소스를 우선하여 어느 쪽이 더 신뢰할 수 있는지 표시 |
| 페이월/403 응답 | 해당 URL을 건너뛰고 대체 소스를 검색. 검색 결과 스니펫만으로 충분한 정보가 있으면 "전문은 접근 불가하나 검색 스니펫 기준"으로 안내 |

## 주의사항

1. **공식 소스 우선**: 해당 기술의 공식 사이트 → 공식 문서 → 패키지 레지스트리 → 커뮤니티 순으로 우선합니다.
2. **교차 검증**: 단일 출처에 의존하지 않고, 가능한 여러 출처를 교차 검증합니다. 비공식 소스는 반드시 공식 문서와 대조합니다.
3. **날짜 확인**: 검색 결과의 게시 날짜를 확인하여 최신성을 판단합니다. 1년 이상 된 정보는 변경 여부를 재확인합니다.
4. **불확실성 표시**: 검색 결과가 상충하거나 불확실할 경우 명시합니다.
5. **개인정보 보호**: 검색 쿼리에 사용자의 개인정보를 포함하지 않습니다.
6. **신뢰할 수 없는 소스 회피**: 출처가 불명한 개인 블로그, SEO 스팸 사이트, 클릭베이트 사이트의 정보는 사용하지 않습니다.
