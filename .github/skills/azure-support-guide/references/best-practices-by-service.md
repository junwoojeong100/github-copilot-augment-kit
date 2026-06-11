# Best Practices by Service — 점검 축 & 형식

> 이 파일은 **방향(무엇을 점검/선택/진단할지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·SKU·가격·설정값·트러블슈팅 절차는 박제하지 않으며, 실행 시점에
> `microsoft_docs_search`/`microsoft_docs_fetch`(learn.microsoft.com) · `google-web-search`로 **최신화**합니다.

Azure 서비스별 모범 사례를 정리할 때 사용할 공통 축입니다. 권장 설정·SKU·수치는 공식 문서로 최신 확인합니다.

## 공통 출력 형식
| 서비스 | 보안 | 가용성 | 성능 | 비용 | 운영 | 최신 확인 소스 |
|--------|------|--------|------|------|------|----------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## App Service
- 보안 / 가용성 / 성능 / 운영 / 비용

## Azure Functions
- 보안 / 성능 / 비용 / 운영 / 설계

## Container Apps
- 보안 / 가용성 / 성능 / 운영 / 네트워킹

## Azure Container Registry (ACR)
- 보안 / 성능 / 가용성 / 운영 / 거버넌스

## Azure SQL Database
- 보안 / 가용성 / 성능 / 비용 / 운영

## Cosmos DB
- 설계 / 성능 / 가용성 / 비용 / 보안

## Azure Managed Redis / Azure Cache for Redis
- 보안 / 성능 / 가용성 / 비용 / 운영
- 신규·기존 서비스 권고와 전환 일정은 실행 시점 공식 문서로 확인

## Storage Account
- 보안 / 가용성 / 성능 / 비용 / 운영

## Key Vault
- 보안 / 운영 / 접근 / 설계

## AKS
- 보안 / 가용성 / 성능 / 비용 / 운영

## VNet / Networking
- 설계 / 보안 / 연결 / 관리

## Azure Front Door
- 보안 / 가용성 / 성능 / TLS / 운영

## API Management
- 보안 / 보호 / 백엔드 연동 / 운영 / 네트워킹

## Monitoring (Application Insights + Log Analytics)
- 수집 / 경보 / 대시보드 / 비용 / 분석

### 공식 소스
- https://learn.microsoft.com/azure/
- https://learn.microsoft.com/azure/well-architected/
