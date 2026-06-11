# Governance & Regulation — 점검 축 & 형식

> 이 파일은 **무엇을 점검할지(축)와 어떻게 정리할지(형식)**만 정의합니다.
> 규제 조항·시행일·세부 의무는 **박제하지 않습니다.** 규제는 자주 바뀌므로, 실행 시점에
> 아래 **공식 1차 소스**와 `google-web-search` 스킬로 **반드시 최신 확인**하고 기준 시점을 명시하세요.

## 1. 점검할 거버넌스 축
- **Responsible AI 원칙**: 공정성 · 신뢰성/안전 · 프라이버시/보안 · 포용성 · 투명성 · 책임성 → 원칙별 통제 수단을 최신 도구로 매핑
- **운영 모델**: AI CoE · 정책/표준 · 리뷰 보드 · 리스크 분류 체계

## 2. 규제 체크리스트 (적용 여부만 식별 → 내용은 1차 소스로 최신 확인)

| 영역 | 확인 대상(예시) | 1차 공식 소스 |
|------|----------------|--------------|
| 글로벌 | EU AI Act, GDPR, ISO/IEC 42001·27001, NIST AI RMF | `eur-lex.europa.eu`, `digital-strategy.ec.europa.eu`, `iso.org`, `nist.gov` |
| 국내 공통 | 개인정보보호법(PIPA), AI 기본법 | `law.go.kr`, `pipc.go.kr`, `msit.go.kr` |
| 금융 | 금융 AI 가이드라인, 클라우드/망분리 | `fsc.go.kr`, `fss.or.kr`, `fsec.or.kr` |
| 산업기술 | 산업기술보호법·국가핵심기술 | `motie.go.kr`, `kaits.or.kr`, `law.go.kr` |
| 인증 | ISMS-P 등 | `kisa.or.kr` |

> 강한 규제 산업(금융·공공·의료)·국가핵심기술 보유 고객은 데이터 해외 이전·리전 제약을 전략 초기에 검토.

## 3. 전략 반영 절차 (형식)
1. 적용 규제 식별 → 2. 데이터 분류·경계(리전) 설계 → 3. 솔루션 매핑(Purview·Defender·Entra·Service Trust Portal) → 4. `google-web-search`로 최신성 검증·기준 시점 명시 → 5. 리스크 등록부에 통합
