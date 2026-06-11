# Azure Service Selection Guide — 선택 축 & 형식

> 이 파일은 **방향(무엇을 점검/선택/진단할지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·SKU·가격·설정값·트러블슈팅 절차는 박제하지 않으며, 실행 시점에
> `microsoft_docs_search`/`microsoft_docs_fetch`(learn.microsoft.com) · `google-web-search`로 **최신화**합니다.

워크로드 요구사항을 분류하고 Azure 서비스 후보를 비교하는 형식입니다. 최종 선택은 리전 가용성·SKU·SLA·가격·제약을 공식 문서로 확인합니다.

## Requirement → Service Quick Map
| 고객 요구사항 | 1차 후보 서비스/패턴 | 선택 근거 관점 | 확인 포인트 | 최신 확인 소스 |
|---------------|----------------------|----------------|-------------|----------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## Compute
| 서비스 후보 | 적합한 경우 | 비적합한 경우 | 확인 포인트 |
|-------------|-------------|----------------|-------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

### Compute Decision Matrix (형식)
1. 컨테이너 여부 → 2. 이벤트 기반 여부 → 3. OS/Kubernetes 제어 필요성 → 4. 관리형 선호도 → 5. 비용·운영 역량 검증

## Database
| 서비스 후보 | 데이터 모델 | 적합한 워크로드 | 가용성·SLA 확인 소스 |
|-------------|-------------|-----------------|----------------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

### Database Decision Matrix (형식)
1. 데이터 모델 → 2. 일관성·분산 요구 → 3. 호환성 요구 → 4. 성능·비용 모델 → 5. 공식 SLA·제한 확인

## Messaging & Events
| 서비스 후보 | 용도 | 순서·트랜잭션 관점 | 처리량·크기 확인 소스 |
|-------------|------|--------------------|-----------------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## Networking
| 서비스 후보 | 용도 | 글로벌/리전 관점 | 보안·연결 확인 포인트 |
|-------------|------|-------------------|-----------------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## Security & Identity
| 서비스 후보 | 용도 | 확인 포인트 |
|-------------|------|-------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## Monitoring & Operations
| 서비스 후보 | 용도 | 확인 포인트 |
|-------------|------|-------------|
→ 실행 시점 MS Learn/웹으로 최신 조사

## SKU/Tier 선택 가이드
| 서비스 | Dev/Test 관점 | Production 관점 | Enterprise 관점 | 공식 확인 소스 |
|--------|---------------|------------------|------------------|----------------|
→ SKU·가격·SLA·리전 가용성은 실행 시점 MS Learn/가격 계산기/SLA 문서로 최신 조사

### 공식 소스
- https://learn.microsoft.com/azure/
- https://azure.microsoft.com/pricing/calculator/
- https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services
