---
name: google-web-search
description: "최신 정보가 필요할 때 Google 웹 검색을 수행하여 실시간 정보를 수집하고 요약합니다. 학습 데이터 이후의 최신 뉴스, 기술 업데이트, 릴리스 정보, 가격 변경, 이벤트, 규제 동향, 전략 리포트 등을 검색합니다. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, 최신 뉴스, 최근 업데이트, 릴리스 노트, 최신 버전, 현재 가격, 현재 상태, latest news, recent updates, current price, what's new, release notes, changelog, web search, search the web, look up online, 오늘 날짜 기준 정보, 2024년 이후 정보, 최신 트렌드, 기술 동향, 최근 발표, 공식 발표, 최신 문서, AI 규제 동향, EU AI Act, GDPR, 컴플라이언스 요구사항, 규정 준수, 개인정보보호법, ISO 27001, NIST, 최신 IT 전략 동향, AX 전략 리포트 검색, 클라우드 전략 동향, AI 도입 사례, 시장 동향 분석, 산업 전략 리포트."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# Google 웹 검색

학습 컷오프 이후 최신 정보(버전·뉴스·가격·문서·규제·동향) 실시간 수집·정리.

## 절차
1. **쿼리**: 핵심 키워드 영어 + 현재 연도 + 구체 용어. 사용자 지정 도메인 우선.
2. **소스(동적, 고정 화이트리스트 아님)**: 주제별 가장 권위 있는 1차 출처를 탐색·검증.
   - 신뢰 기준: 1차성 · 권위(`*.go.kr`/`*.gov`/`europa.eu`/표준기구/공식 벤더) · 검증가능(작성주체·게시일) · 최신성 · 교차검증.
   - 우선순위: ① 1차(공식문서·법령·규제공지·표준) → ② 공신력 2차(표준기구·분석기관·arXiv·주요 언론) → ③ 커뮤니티(①②로 교차검증).
   - 앵커(출발점, 더 권위 있는 1차 발견 시 우선): `learn.microsoft.com`·`azure.microsoft.com`·`devblogs.microsoft.com`·`github.blog`·`docs.github.com`; 규제 `eur-lex.europa.eu`·`law.go.kr`·`fsc.go.kr`·`fsec.or.kr`·`pipc.go.kr`·`nist.gov`·`iso.org`; 연구 `arxiv.org`. 도메인 개편·리다이렉트 고려.
   - MS/Azure/GitHub 주제: 일반어 대신 구체 서비스명(Foundry·AI Search·Content Safety·Entra·Purview·Defender·GitHub Copilot/Advanced Security)으로 기능·통제·가치 수집.
3. **검색(`fetch_webpage`)**: 뉴스 `news.google.com/search?q={q}&hl=en-US&gl=US&ceid=US:en` · 일반 `html.duckduckgo.com/html/?q={q}`(봇 감지 없음) · 공식 직접(`learn.microsoft.com/...`·`github.blog/tag/...`). 검색엔진=URL 발견용, fetch=신뢰 통과 소스만. JS 챌린지/봇 차단→재시도 없이 전환. 도구 불가→`curl`; 모두 불가→"실시간 검색 불가, 학습 데이터 기준" 명시.
4. **정리**: `## 검색 결과` + 검색일·쿼리 + 핵심요약(1~3문장) + 상세 + `### 출처`(제목·URL·설명). "검색 시점 기준, 공식 문서 확인 권장" 주석.

## 연산자
`site:` · `"exact"` · `after:YYYY-MM-DD` · `filetype:` · `-kw` · `OR`.

## 처리
접근 불가→News→DuckDuckGo→공식 직접 폴백, 모두 실패 시 학습 기준 명시. 결과 없음→쿼리 재구성 1회. 비신뢰만→사용 금지·공식 확인 안내. 상충→양쪽 제시·공식 우선. 페이월/403→스니펫 기준. 게시일 1년+ 재확인. 쿼리에 개인정보 금지.
