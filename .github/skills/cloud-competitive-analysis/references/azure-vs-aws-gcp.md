# Azure vs AWS vs GCP — 카테고리별 비교 축

> 이 파일은 **방향(무엇을 비교/다룰지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·가격·비교 셀·서비스 매핑은 박제하지 않으며, 실행 시점에
> `google-web-search` 스킬과 공식 소스(`learn.microsoft.com`·`azure.microsoft.com`·`docs.github.com`·각 클라우드 공식 문서)로 **최신화**합니다.

Azure·AWS·GCP 비교 시 워크로드별 확인 축과 출력 형식을 정의합니다. 기능·가격·가용성은 공식 문서와 가격 계산기로 실행 시점에 확인하세요.

## 1. Compute
비교 축: Virtual Machines · Serverless Functions · Container Orchestration · GPU/HPC · 예약/스팟 · 하이브리드 라이선스.

| 항목 | Azure | AWS | GCP | 확인 관점 |
|------|-------|-----|-----|-----------|

→ 각 셀은 실행 시점에 공식 소스로 최신 조사.

## 2. Database
비교 축: Relational · NoSQL/Multi-model · Cache · Migration · 관리 수준 · 호환성 · 스케일링 · HA/DR.

| 항목 | Azure | AWS | GCP | 확인 관점 |
|------|-------|-----|-----|-----------|

## 3. AI & Machine Learning
비교 축: 모델 카탈로그 · Agent/RAG · 문서/음성/비전 API · 평가/관측 · Responsible AI · 거버넌스.

| 항목 | Azure/Microsoft | AWS | GCP | 확인 관점 |
|------|-----------------|-----|-----|-----------|

## 4. Networking
비교 축: DNS · CDN/글로벌 LB · L4/L7 LB · Private Connectivity · Firewall/WAF · DDoS · 관측/진단.

| 항목 | Azure | AWS | GCP | 확인 관점 |
|------|-------|-----|-----|-----------|

## 5. Identity & Security
비교 축: Identity · RBAC/IAM · Secrets/Keys · CSPM/CWPP · SIEM/SOAR · Data Governance · Compliance Evidence.

| 항목 | Azure/Microsoft | AWS | GCP | 확인 관점 |
|------|-----------------|-----|-----|-----------|

## 6. Hybrid & Multi-cloud
비교 축: 온프레미스 확장 · 멀티클라우드 관리 · Edge · Kubernetes/VM 관리 · 정책/거버넌스.

| 항목 | Azure | AWS | GCP | 확인 관점 |
|------|-------|-----|-----|-----------|

## 7. 비용 비교 가이드
동일 워크로드·리전·사용량·할인 조건을 명시하고, 아래 계산기로 기준 시점을 남깁니다.

| 클라우드 | 가격 계산기 |
|---------|-----------|
| Azure | [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) |
| AWS | [AWS Pricing Calculator](https://calculator.aws/) |
| GCP | [GCP Pricing Calculator](https://cloud.google.com/products/calculator) |

## 8. 통합 생태계 — Microsoft 차별화 렌즈
Microsoft 365 · Entra · GitHub · Defender · Purview · Power Platform · Azure의 통합 가치를 고객 맥락에 맞춰 검증해 설명합니다.

> 상세 서비스 매핑은 `service-mapping.md`, AI 전략/거버넌스는 `it-ai-strategy-advisory`와 교차 확인.
