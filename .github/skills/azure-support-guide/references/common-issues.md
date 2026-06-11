# Common Issues & Solutions — 진단 축 & 형식

> 이 파일은 **방향(무엇을 점검/선택/진단할지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·SKU·가격·설정값·트러블슈팅 절차는 박제하지 않으며, 실행 시점에
> `microsoft_docs_search`/`microsoft_docs_fetch`(learn.microsoft.com) · `google-web-search`로 **최신화**합니다.

자주 발생하는 문제를 분류하고 공식 진단 문서로 연결하기 위한 형식입니다. 명령·해결책 본문은 저장하지 않습니다.

## 공통 이슈 정리 형식
| 서비스 | 증상 | 가능 원인 범주 | 확인할 로그·메트릭 | 공식 진단 문서 | 권장 다음 단계 |
|--------|------|----------------|--------------------|----------------|----------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## App Service
- 배포 후 5xx
- 느려짐·간헐적 타임아웃
- 시작 실패·Health check 실패

## Azure Functions
- 트리거 미동작
- Cold start 지연
- 바인딩·앱 설정 오류

## Container Apps
- 컨테이너 시작 실패
- Ingress 5xx
- Revision·스케일 문제

## Azure SQL Database
- 연결 실패
- 리소스 제한·쿼리 성능 저하
- 방화벽·Private Endpoint 접근 문제

## Azure Storage
- 403 AuthorizationFailure
- SAS·RBAC·네트워크 규칙 문제

## Key Vault
- 403 Forbidden
- RBAC·Access Policy·네트워크 제한 문제

## Cosmos DB
- 429 Too Many Requests
- 파티션·쿼리·처리량 문제

## VNet / Private Endpoint
- Private Endpoint 연결 후 접근 불가
- DNS·라우팅·방화벽 문제

## Managed Identity
- 인증 실패
- ID 활성화·역할 할당·토큰 갱신 문제

## AKS
- kubectl 연결 실패
- Pod Pending·CrashLoop·이미지 풀 문제

## Azure Managed Redis / Azure Cache for Redis
- 연결 끊김
- 높은 메모리 사용률
- 느린 명령
- 신규·기존 서비스 전환 일정은 공식 문서로 최신 확인

### 공식 소스
- https://learn.microsoft.com/azure/azure-resource-manager/troubleshooting/
- https://learn.microsoft.com/azure/service-health/
- https://status.azure.com/
