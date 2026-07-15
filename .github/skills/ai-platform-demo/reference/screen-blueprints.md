# Screen Blueprints + 산업 매핑

8개 화면의 **고정 골격**과 **산업별 콘텐츠 매핑**. 골격은 그대로 두고, 표의 산업 열을 보고
도메인 3~4개·에이전트·KPI·시뮬레이터·채팅을 고객 산업으로 채운다.

---

## 화면 1 — 대시보드 (필수)
**목적**: "전사가 실시간으로 돌고 있다"는 첫인상.
**구성**: 환영 `hero` → KPI 4개(`.grid-4`, 스파크라인+실시간 변동) → `.grid-2`[스트리밍 라인차트 | 활동 피드] → `.grid-2`[에이전트 상태 | 부문/권역 테이블].
**실시간**: KPI 미세 변동(2s), 차트 스트리밍(1.8s), 피드 prepend(3.5s), 주기 토스트(9s).

## 화면 2 — 운영 콘솔 (도메인 1, 필수) · **실시간 시각화**
**목적**: 핵심 현장 운영을 살아있는 화면으로.
**구성**: KPI 4 → `.grid-2`[SVG 맵/흐름(움직이는 객체) + "AI 재최적화" 액션 | 실시간 상태 테이블].
**패턴**: 노드(거점)·엣지(경로)를 SVG로, 객체를 `addTimer`로 경로 따라 이동. 액션 클릭 시 경로 재배열 + KPI 갱신 + 토스트.

## 화면 3 — 예측/시뮬레이터 (도메인 2, 권장) · **슬라이더→게이지**
**목적**: 입력을 바꾸면 결과를 미리 본다("사고 전에 예측").
**구성**: `.grid-2`[슬라이더 3개 | 반원 게이지 + 합격/주의/위험 배지] → 분포 히스토그램 + 통계 → 최근 이력 테이블.
**패턴**: 간단한 모델식 `calc()` → `gauge(v)`로 색/배지. 슬라이더 `oninput`.

## 화면 4 — 분석/개선 (도메인 3, 권장) · **실행→차트/칸반**
**목적**: 문제의 근본원인을 자동 분석하고 개선과제를 추적.
**구성**: `hero`+실행버튼 → `.grid-2`[진행 스텝(타이핑) + Top-N 기여요인 막대 | 효과 KPI + 보드(발굴/진행/완료)].
**패턴**: 버튼/진입 시 `.step` 순차 표시 + `.bar-fill` 막대 채움. 자동 1회 실행은 `addTimer(setTimeout(()=>{const b=$('#runAnalysis');if(b)b.click()},480))`.

## 화면 5 — 재무 인사이트 (권장)
**구성**: `.grid-2`[What-if 슬라이더(원가 변수) → 큰 마진 숫자+상태 | 원가 도넛] → 이상탐지 테이블(전월비·AI 코멘트·상태 배지). 24시간 자율 감시 톤.

## 화면 6 — 개발 가속 / GitHub Copilot (권장)
**구성**: `hero`+"Copilot cloud agent에 이슈 배정" → KPI 4(리드타임·자동 PR·보안스캔·리뷰) → `.grid-2`[코드 diff 타이핑(`.code .add/.delete`) | 진행 스텝 + 이슈 테이블(상태→PR#)].
**핵심 메시지**: 레거시 현대화·Issue→PR 자동화로 고객 **IT 자체 역량** 강화.

## 화면 7 — AI 에이전트 스튜디오 (필수·데모의 하이라이트)
**목적**: 임원이 직접 질문하고, 에이전트들이 협업하는 모습.
**구성**: `.agent-layout`(310px 1fr)[에이전트 목록 + 오케스트레이션 플로우 + "시나리오 실행" 버튼 | 채팅(헤더·로그·추천칩·입력)].
**★ 필수**: 목록의 **모든 행 클릭 시 그 에이전트로 전환**(헤더·아바타·인사·추천질문·답변). 누락하면 "첫 행만 동작"하는 버그.
실제 구현은 `runtime/runtime.js`의 `renderAgents()`가 source of truth다. Extension에서도 아래 lifecycle을 유지한다:
```js
let current = 0;
let conversationVersion = 0;
function selectAgent(index) {
  conversationVersion += 1; // 이전 Agent의 지연 응답 무효화
  current = index;
  renderAgentRows(); // profile 문자열은 escapeHtml 후 렌더
  bindAgentRows();
  renderConversation();
}
function bindAgentRows() {
  $$('#agentList .agent-row').forEach(row => {
    row.onclick = () => selectAgent(Number(row.dataset.index));
  });
}
function ask(question) {
  const originAgent = current;
  const originVersion = conversationVersion;
  addTimer(setTimeout(() => {
    if (originVersion !== conversationVersion || originAgent !== current) return;
    renderSanitizedAnswer();
  }, 800));
}
```
Rich text는 Renderer가 허용한 태그/class만 사용하고, 사용자 입력·일반 spec 문자열은 반드시
`escapeHtml`을 거친다. **오케스트레이션**은 중앙 `.flow-node.core` + 도메인 노드로 구성하고,
"시나리오 실행" 시 노드 순차 `hot` + `<animateMotion>` 펄스 + assistant bubble을 사용한다.

## 화면 8 — 거버넌스 (필수)
**목적**: "모델은 빌리되 전문성·데이터는 고객이 소유"(주권).
**구성**: `hero` → `.grid-3`[고객 평가셋 점수 | 제도적 기억/증거 | 정책 범위] →
`.grid-2`[보안 통제 테이블(Microsoft Entra ID·Microsoft Purview·Azure AI Content Safety·Microsoft Defender·GitHub AI Controls·observability) |
평가 trace + 고객 소유 memory] → 4단계 Learning Loop.
이 화면의 골격은 산업과 무관하게 고정하되, 통제 항목·상태·설명은 고객의 검증된 현재 환경 또는
명시적인 목표 아키텍처 가정에 맞춘다. 제품을 나열하는 것만으로 현재 배포 상태를 주장하지 않는다.

---

## 산업 → 도메인 3종 + 에이전트 매핑 예시
| 산업 | 운영 콘솔(실시간) | 시뮬레이터(예측) | 분석/개선 | 도메인 에이전트(5~6) | 핵심 KPI·단위 |
|---|---|---|---|---|---|
| **레미콘/건설소재** | 레미콘 배차 관제(트럭 이동) | 28일 압축강도 예측 | 공정개선 Six Sigma | 배차·품질·공정·재무·안전·Copilot | 출하 ㎥·배차분·MPa·합격% |
| **은행/리테일금융** | 실시간 거래/이상거래 관제 | 여신 부도확률 예측 | 연체/콜센터 개선 | 여신·리스크·이상거래·마케팅·컴플라이언스·Copilot | 거래건·승인율·연체%·VaR |
| **유통/리테일** | 매장·물류 실시간 현황 | 수요예측 시뮬 | 재고/폐기 개선 | 수요·재고·가격·CRM·물류·Copilot | 매출·회전율·결품%·폐기 |
| **물류/3PL** | 차량·허브 실시간 관제(맵) | ETA/적재율 예측 | 라스트마일 개선 | 배차·적재·경로·창고·정산·Copilot | 적재율%·리드타임·정시율 |
| **제조(일반)** | 라인 OEE 실시간 모니터 | 수율/불량 예측 | 설비예지보전 | 생산·품질·설비·SCM·안전·Copilot | OEE%·수율%·불량ppm |
| **에너지/유틸리티** | 발전·수요 실시간 밸런싱 | 수요/발전량 예측 | 손실/정비 최적화 | 수급·정비·거래·탄소·안전·Copilot | MWh·피크·손실%·탄소t |
| **헬스케어/제약** | 병상/검사 실시간 현황 | 재원일/리스크 예측 | 동선/대기 개선 | 진료·검사·약제·청구·안전·Copilot | 가동률·대기시간·재입원% |

> 매핑 원칙: ① 운영 콘솔은 **움직이는 시각화**가 가능한 업무, ② 시뮬레이터는 **입력→결과** 인과가 분명한 업무,
> ③ 분석/개선은 **근본원인→과제** 흐름, ④ 에이전트는 위 도메인 + 재무/안전·컴플라이언스 + Copilot.
> 모든 화면에 그 산업의 **실제 용어·단위**를 써야 현실감이 산다. 숫자는 리서치로 현실 범위에 맞추되 `DEMO DATA`.

## 서사 프레임(거버넌스/대시보드 hero에 1줄)
> "<CUSTOMER>는 AI를 '쓰는' 회사가 아니라, <INDUSTRY> 수십 년 노하우를 복리로 키우는 **학습 루프(Learning Loop)를 '소유'**하는 회사가 됩니다." — Nadella의 *Frontier Ecosystem*(Human+Token Capital) 프레임을 고객 사업으로 번역.
