---
name: google-web-search
description: "최신 정보가 필요할 때 Google 웹 검색을 수행하여 실시간 정보를 수집하고 요약합니다. 학습 데이터 이후의 최신 뉴스, 기술 업데이트, 릴리스 정보, 가격 변경, 이벤트, 규제 동향, 전략 리포트 등을 검색합니다. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, 최신 뉴스, 최근 업데이트, 릴리스 노트, 최신 버전, 현재 가격, 현재 상태, latest news, recent updates, current price, what's new, release notes, changelog, web search, search the web, look up online, 오늘 날짜 기준 정보, 2024년 이후 정보, 최신 트렌드, 기술 동향, 최근 발표, 공식 발표, 최신 문서, AI 규제 동향, EU AI Act, GDPR, 컴플라이언스 요구사항, 규정 준수, 개인정보보호법, ISO 27001, NIST, 최신 IT 전략 동향, AX 전략 리포트 검색, 클라우드 전략 동향, AI 도입 사례, 시장 동향 분석, 산업 전략 리포트."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# Google 웹 검색 스킬

학습 데이터 컷오프 이후의 **최신 정보**(버전 · 뉴스 · 가격 · 문서 · 규제 · 동향)가 필요할 때 웹 검색으로 실시간 수집·정리합니다.

## Workflow

### 1) 쿼리 구성
핵심 키워드를 **영어**로, **현재 연도**를 포함, 구체적 기술 용어 사용, 불필요한 조사·접속사 제거. 사용자가 특정 도메인을 지정하면 우선 사용합니다.

### 2) 소스 선택 (동적 — 고정 화이트리스트 아님)
주제에 맞는 **가장 권위 있는 1차 출처를 그때그때 탐색·검증**합니다. 신뢰도 기준:

| 기준 | 판단 질문 |
|------|----------|
| 1차성 | 주제를 직접 관할/생산하는 주체인가? (벤더 공식문서 · 법령 원문 · 규제기관 · 표준) |
| 권위 | 공인 기관/매체인가? (`*.go.kr` · `*.gov` · `europa.eu` · 표준기구 · 공식 벤더) |
| 검증가능성 | 작성주체 · 게시일이 명확한가? |
| 최신성 | 주제 대비 충분히 최신인가? |
| 교차검증 | 독립된 다른 신뢰 소스와 일치하는가? |

우선순위: ① 1차 출처(공식문서 · 법령 · 규제 공지 · 표준) → ② 공신력 2차(표준기구 · 주요 분석기관 · arXiv · 주요 언론) → ③ 커뮤니티(반드시 ①②로 교차검증).

**앵커 소스 (출발점일 뿐 — 더 권위 있는 1차 출처 발견 시 우선):**
- MS/Azure/GitHub: `learn.microsoft.com` · `azure.microsoft.com` · `devblogs.microsoft.com` · `techcommunity.microsoft.com` · `servicetrust.microsoft.com` · `github.blog` · `docs.github.com`
- AI · 연구: `openai.com` · `anthropic.com` · `ai.google.dev` · `huggingface.co` · `arxiv.org`
- 규제 · 표준: `eur-lex.europa.eu` · `digital-strategy.ec.europa.eu` · `iso.org` · `nist.gov` / 국내 `law.go.kr` · `pipc.go.kr` · `kisa.or.kr` · `msit.go.kr` · `fsc.go.kr` · `fss.or.kr` · `fsec.or.kr` · `motie.go.kr`
- 전략 · 분석: `oecd.org` · `weforum.org` · `gartner.com` · `mckinsey.com`(일부 페이월)

> 도메인 개편 · 리다이렉트 가능성을 항상 고려하고, 검색으로 현재 유효한 공식 URL을 확인합니다.

**Microsoft/Azure/GitHub 주제**면 일반어가 아니라 **정확한 서비스명**(예: Microsoft Foundry · Azure AI Search · Content Safety · Entra · Purview · Defender · GitHub Copilot/Advanced Security)으로 기능 · 통제 · 가치를 함께 수집합니다. 금융·공공·의료면 데이터 레지던시 · 인증(K-ISMS · CSAP) · 감사 자료를 보강합니다. (슬라이드 · 경쟁분석 스킬과 연계)

### 3) 검색 수행
`fetch_webpage`로 수행합니다. 봇 차단되는 `google.com/search` 대신 용도별 엔드포인트 사용:
- **뉴스/최신**: `https://news.google.com/search?q={q}&hl=en-US&gl=US&ceid=US:en`
- **일반 문서**: `https://html.duckduckgo.com/html/?q={q}` (봇 감지 없음, fetch 호환)
- **공식 소스 직접**: `learn.microsoft.com/...` · `github.blog/tag/...` · `github.com/{owner}/{repo}/releases`

> 검색 엔진은 URL 발견용, 상세 fetch는 **신뢰도 기준을 통과한 소스만**. JS 챌린지/봇 차단 시 재시도 없이 다른 방법으로 전환. `fetch_webpage` 불가 시 `curl` 등으로 대체하고, 모두 불가하면 "실시간 검색 불가, 학습 데이터 기준"이라 명시합니다.

### 4) 결과 정리
```markdown
## 검색 결과: {주제}
**검색일**: {날짜} | **쿼리**: `{쿼리}`
### 핵심 요약
{1–3문장}
### 상세 내용
{구조화}
### 출처
- [제목](URL) — {설명}
> ⚠️ 검색 시점 기준이며 정확성을 보장하지 않습니다. 중요한 의사결정은 공식 문서를 확인하세요.
```

## 고급 연산자
`site:` · `"exact phrase"` · `after:YYYY-MM-DD` · `filetype:` · `-keyword` · `OR`.

## Error Handling
| 상황 | 처리 |
|------|------|
| 검색엔진 접근 불가 | Google News → DuckDuckGo HTML → 공식 소스 직접 폴백. 모두 실패 시 "실시간 검색 불가, 학습 데이터 기준" 명시 |
| 결과 없음 | 쿼리 재구성 후 1회 재시도, 그래도 없으면 안내 |
| 비신뢰 소스만 반환 | 사용하지 않고 "공식 소스 미발견, 공식 문서 직접 확인" 안내 |
| 결과 상충 | 양쪽 제시 + 공식 소스 우선 표시 |
| 페이월/403 | 건너뛰고 대체 소스, 필요 시 "스니펫 기준" 안내 |

## 주의
공식 소스 우선 · 교차검증 · 게시일 확인(1년+ 재확인) · 불확실성 표시 · 쿼리에 개인정보 금지 · SEO 스팸/콘텐츠팜 회피.
