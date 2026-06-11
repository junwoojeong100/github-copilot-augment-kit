# Troubleshooting Flowchart — 진단 흐름 형식

> 이 파일은 **방향(무엇을 점검/선택/진단할지)과 형식(어떻게 정리할지)**만 정의합니다.
> 구체 수치·기능·SKU·가격·설정값·트러블슈팅 절차는 박제하지 않으며, 실행 시점에
> `microsoft_docs_search`/`microsoft_docs_fetch`(learn.microsoft.com) · `google-web-search`로 **최신화**합니다.

서비스 장애·성능·배포 문제를 체계적으로 좁히는 단계와 분기 구조입니다. 구체 명령과 해결책은 공식 진단 문서를 참조합니다.

## 공통 진단 흐름
1. Azure 서비스 상태 확인 (`https://status.azure.com`, Service Health)
2. Resource Health 확인
3. 최근 변경 이력 확인
4. 카테고리별 진단으로 분기
5. 해결 또는 Microsoft 지원 에스컬레이션

## 네트워크 진단 흐름
1. DNS 해석 확인
2. 포트·경로 연결 확인
3. TLS/인증서 확인
4. 애플리케이션 연결 설정 확인
5. 공식 네트워크 진단 문서 참조

## 인증/권한 진단 흐름
1. 인증 방식 식별: Managed Identity / Service Principal·App Registration / SAS·Access Key
2. ID 활성화·자격 증명·권한 범위 확인
3. 대상 서비스 접근 정책 확인
4. 네트워크 레벨 차단 확인
5. 공식 Entra/RBAC/서비스별 진단 문서 참조

## 성능 진단 흐름
1. 핵심 메트릭 확인
2. Application Insights/APM 확인
3. 의존성·데이터베이스 병목 확인
4. 네트워크 지연·대역폭 확인
5. 공식 성능 진단 문서 참조

## 배포 진단 흐름
1. 배포 로그 확인
2. 리소스 제한·쿼터 확인
3. 이미지·아티팩트·설정 확인
4. Health probe·롤아웃 상태 확인
5. IaC 검증·What-if/Plan 확인
6. 공식 배포 진단 문서 참조

## 데이터 진단 흐름
1. 일관성·복제 상태 확인
2. 백업·복구 가능성 확인
3. 변경 이력·감사 로그 확인
4. 인덱스·쿼리·연결 풀 확인
5. 공식 데이터 서비스 진단 문서 참조

## KQL 진단 쿼리 형식
| 목적 | 테이블 | 필터 축 | 집계 축 | 시각화 |
|------|--------|---------|---------|--------|
→ 구체 쿼리는 실행 시점 스키마와 공식 문서 기준으로 작성

### 공식 소스
- https://status.azure.com/
- https://learn.microsoft.com/azure/service-health/
- https://learn.microsoft.com/azure/azure-monitor/
- https://learn.microsoft.com/azure/azure-resource-manager/troubleshooting/
