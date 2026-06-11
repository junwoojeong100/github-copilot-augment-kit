# WAF Review Checklist — 점검 축 & 형식

> 이 파일은 **방향(무엇을 점검/선택/진단할지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·SKU·가격·설정값·트러블슈팅 절차는 박제하지 않으며, 실행 시점에
> `microsoft_docs_search`/`microsoft_docs_fetch`(learn.microsoft.com) · `google-web-search`로 **최신화**합니다.

Azure Well-Architected Framework 5대 Pillar 기준 리뷰 형식입니다. 항목명만 유지하고 세부 기준은 실행 시점 공식 문서로 확인합니다.

## 1. 신뢰성 (Reliability)
### 가용성
- [ ] 단일 장애점(SPOF)
- [ ] SLA·복합 SLA
- [ ] 가용성 영역·리전 전략
### 복원력
- [ ] 재시도·타임아웃
- [ ] Circuit breaker
- [ ] Graceful degradation
### 재해 복구
- [ ] RPO/RTO
- [ ] 백업·복제
- [ ] DR 훈련
### Health Monitoring
- [ ] Health check
- [ ] 의존 서비스 감지
- [ ] 자동 복구

## 2. 보안 (Security)
### Identity & Access
- [ ] Managed Identity
- [ ] RBAC·최소 권한
- [ ] MFA·조건부 액세스
- [ ] 자격 증명 수명주기
### 네트워크 보안
- [ ] Private Endpoint/Private Link
- [ ] NSG·Firewall
- [ ] 공용 노출 최소화
- [ ] WAF·DDoS
### 데이터 보호
- [ ] 저장·전송 암호화
- [ ] Key Vault
- [ ] CMK 필요성
### 위협 탐지
- [ ] Defender for Cloud
- [ ] 보안 경고
- [ ] 중앙 로그

## 3. 비용 최적화 (Cost Optimization)
- [ ] Right-sizing
- [ ] 구매·할인 모델
- [ ] 자동 확장·축소
- [ ] Budget·태그·고아 리소스

## 4. 운영 우수성 (Operational Excellence)
- [ ] IaC
- [ ] CI/CD·배포 전략
- [ ] 모니터링·분산 추적
- [ ] Alert·Runbook·Incident Response
- [ ] 구성·Feature flag 관리

## 5. 성능 효율 (Performance Efficiency)
- [ ] 수평 확장·상태 비저장
- [ ] 캐싱·CDN
- [ ] 데이터베이스 성능
- [ ] 네트워크 지연·병목
- [ ] 비동기·배치 처리

## 6. AI 워크로드 추가 점검 (Responsible AI)
- [ ] 콘텐츠 안전·프롬프트 공격 방어
- [ ] Grounding·인용·환각 완화
- [ ] 평가·회귀 테스트
- [ ] 데이터·모델·프롬프트 거버넌스
- [ ] Human-in-the-loop·에스컬레이션
- [ ] 토큰·비용·지연·오류 관측성

## 복합 SLA 계산 (형식)
| 구성 | 개별 SLA | 복합 SLA | 공식 확인 소스 |
|------|---------|----------|----------------|
→ 수치 예시는 박제하지 않음. 실행 시점 공식 SLA 문서로 최신 조사

## 평가 등급 기준 (형식)
| 등급 | 기준 관점 | 근거 |
|------|-----------|------|
→ 임계치·점수 기준은 고객 합의와 최신 WAF 문서 기준으로 정의

### 공식 소스
- https://learn.microsoft.com/azure/well-architected/
- https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services
