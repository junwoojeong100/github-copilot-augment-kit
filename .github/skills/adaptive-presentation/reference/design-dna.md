# Design DNA

매 덱의 디자인을 고정 템플릿이 아니라 **입력 맥락에서 도출**하기 위한 절차다. 결과는 새로워야 하지만
자의적이면 안 된다. 아래 결정은 슬라이드 제작 전에 끝낸다.

## 1. 입력 신호 추출

요청에서 다음 신호를 각각 한 줄로 정리한다.

| 신호 | 질문 |
|---|---|
| Audience power | 청중이 승인권자, 실무자, 학습자, 고객 중 누구인가? |
| Cognitive load | 내용을 처음 접하는가, 이미 전문지식이 있는가? |
| Decision horizon | 오늘 결정, 분기 계획, 장기 비전 중 무엇인가? |
| Emotional goal | 신뢰, 긴급성, 낙관, 경외, 안정, 친밀 중 무엇을 느껴야 하는가? |
| Topic materiality | 주제가 소프트웨어, 금융, 제조, 의료, 문화, 과학처럼 어떤 물성을 갖는가? |
| Presentation environment | 대형 스크린, 회의실, 온라인 공유, 출력물 중 어디에서 보는가? |
| Brand constraint | 강한 브랜드 가이드가 있는가, 중립 자료인가? |
| Evidence profile | 정량 데이터, 아키텍처, 사례, 비전 중 무엇이 중심인가? |

## 2. Concept words와 시각 은유

### Concept words

서로 중복되지 않는 형용사 3개를 고른다.

- 좋은 예: `정밀함 · 절제 · 전진`
- 나쁜 예: `혁신 · 미래 · AI` — 구체적인 시각 결정을 만들지 못함

각 단어는 디자인 결정으로 번역한다.

| 단어 | 디자인 번역 예 |
|---|---|
| 정밀함 | 얇은 선, 강한 그리드, 제한된 색, 정확한 수치 정렬 |
| 인간적 | 따뜻한 중립색, 넓은 행간, 얼굴/현장 이미지, 완만한 곡선 |
| 긴급함 | 높은 대비, 짧은 제목, 비대칭 구도, 명확한 액션 색 |
| 안정 | 낮은 채도, 수평 구조, 충분한 여백, 예측 가능한 리듬 |
| 탐험 | 깊이감, 경로·좌표·레이어, 점진적 공개 |

### Visual metaphor

전체 덱의 관계를 설명하는 은유 1개를 선택한다. 장식이 아니라 레이아웃과 전환에 영향을 줘야 한다.

- 항해도: 방향·경로·이정표·도착점
- 설계도: 계층·치수·모듈·인터페이스
- 편집 매거진: 강한 타이포·사진·리듬·여백
- 신호망: 노드·흐름·상태·관찰성
- 운영실: 계기·우선순위·이상 징후·행동
- 연구 노트: 가설·근거·실험·결론
- 공급망/생산라인: 입력·변환·검사·출력

은유를 모든 슬라이드에 문자 그대로 넣지 않는다. 섹션 표지, 선, 진행 구조, 도형 언어에 은근히 반영한다.

## 3. 디자인 아키타입 조합

아래는 완성된 테마가 아니라 **출발 방향**이다. 하나를 primary, 하나를 counter-influence로 선택한다.
counter-influence는 단조로움을 막되 일관성을 깨지 않아야 한다.

| 아키타입 | 적합한 상황 | 시각적 성향 | 피해야 할 상황 |
|---|---|---|---|
| Editorial clarity | 전략·트렌드·보고서 | 강한 헤드라인, 비대칭 여백, 제한된 색 | 데이터 표가 대부분인 운영 보고 |
| Executive contrast | 의사결정·이사회 | 큰 결론, 고대비, 적은 요소 | 장시간 교육 자료 |
| Technical blueprint | 아키텍처·개발 | 그리드, 연결선, 모듈, 코드/규격 | 감성 브랜드·문화 주제 |
| Data observatory | KPI·분석·운영 | 정량 계층, 작은 배수, 상태 신호 | 수치가 거의 없는 비전 발표 |
| Human warmth | 변화관리·의료·교육 | 따뜻한 중립, 사진, 곡선, 사례 | 매우 기밀한 보안·감사 보고 |
| Premium precision | 투자·고급 제안 | 절제, 깊은 중립, 세밀한 타이포 | 빠른 실무 워크숍 |
| Industrial systems | 제조·물류·에너지 | 흐름, 구조, 물성, 단위 중심 | 순수 소비자 라이프스타일 |
| Scientific institutional | 연구·공공·규제 | 명료한 근거, 차분한 색, 도식 | 공격적 영업 피치 |

예:

- 병원 경영진 AI 전략: `Scientific institutional + Human warmth`
- 개발자 대상 플랫폼 소개: `Technical blueprint + Editorial clarity`
- 회장 보고 제조 혁신: `Executive contrast + Industrial systems`
- 럭셔리 브랜드 제안: `Premium precision + Editorial clarity`

## 4. 역할 기반 팔레트 생성

고정 HEX를 복사하지 말고 다음 역할을 채운다.

| 역할 | 용도 |
|---|---|
| Canvas | 전체 배경. 밝거나 어두운 한 축을 선택 |
| Surface | 카드·도표·보조 영역 |
| Ink | 본문과 제목 |
| Muted ink | 설명·축·보조 정보 |
| Primary | 핵심 메시지·진행·주요 데이터 |
| Secondary | 비교 대상·다른 계층 |
| Accent | 한 슬라이드의 단 하나의 강조 |
| Semantic | 성공·주의·위험·정보 상태 |

### 팔레트 규칙

1. Primary는 Concept words와 브랜드에서 도출한다.
2. Canvas와 Ink는 WCAG 대비 7:1을 목표로, 본문은 최소 4.5:1을 확보한다.
3. Primary·Secondary·Accent는 색상환에서 서로 역할이 구분되어야 하지만 모두 고채도일 필요는 없다.
4. 상태 색은 브랜드 색과 독립적으로 일관되게 사용한다.
5. 한 슬라이드에서 강한 색은 1~2개만 사용한다.
6. 브랜드 색이 강하면 Surface와 Canvas는 중립화하여 호흡을 만든다.
7. 산업의 상투색을 자동 선택하지 않는다. 금융=파랑, 의료=청록 같은 기계적 매핑을 피한다.
8. 이전 덱과 Primary/Canvas/Accent 조합이 사실상 같다면 이유가 없는 한 다시 선택한다.

### 팔레트 도출 예시

`신뢰 · 생명 · 명료함`이라는 Concept words를 받았다고 해서 의료용 청록색을 바로 선택하지 않는다.

1. 신뢰 → 낮은 채도의 깊은 Ink
2. 생명 → 따뜻하거나 자연스러운 Accent
3. 명료함 → 높은 Canvas 대비와 단순한 Surface
4. 병원 브랜드 → 로고 색은 Primary가 아니라 Accent가 될 수도 있음
5. 최종 HEX는 화면 렌더로 대비를 확인

## 5. 타이포그래피

### 글꼴 선택

1. 운영체제에서 실제 설치된 글꼴을 확인한다.
2. 한국어는 한글 자소·숫자·영문 혼용 렌더를 함께 확인한다.
3. 한 덱에서 글꼴 패밀리는 1~2개로 제한한다.
4. 브랜드 글꼴이 없으면 시스템 폴백을 명시한다.
5. 코드·수치용 모노스페이스는 기술 자료에서만 보조적으로 사용한다.

### 권장 계층

| 역할 | 범위 |
|---|---|
| Cover title | 34~48pt |
| Slide title | 28~40pt |
| Key number | 34~60pt |
| Primary body | 18~24pt |
| Secondary label | 14~17pt |
| Source/footer | 8.5~10pt |

크기는 규칙이 아니라 하한선이다. 글씨를 줄여 맞추지 말고 내용을 줄인다.

## 6. Shape language

다음 다섯 요소를 한 세트로 정한다.

1. Corner: square / subtle / rounded / pill
2. Line: none / hairline / technical / expressive
3. Depth: flat / border / subtle shadow / layered
4. Spacing: compact / balanced / spacious
5. Motion implication: static / directional / radial / stacked

예:

- `Technical blueprint`: subtle corner, technical line, flat, compact, directional
- `Human warmth`: rounded, minimal line, subtle shadow, spacious, radial

카드마다 임의의 모서리와 그림자를 섞지 않는다.

## 7. 이미지와 차트 전략

### 이미지

- 사진 중심: 현장·인간 경험이 설득의 핵심일 때
- 아이콘 중심: 추상 기능을 빠르게 구분할 때
- 추상 도형 중심: 민감한 고객·기술 비전·브랜드 독립 자료
- 다이어그램 중심: 구조·흐름·책임 관계가 핵심일 때

사진을 사용할 때는 라이선스·출처·크롭 일관성을 확인한다. 품질 낮은 스톡 사진보다 도형이 낫다.

### 차트

- Primary는 핵심 계열 1개에만 사용
- 비교 계열은 중립색, 선택 계열만 강조
- 3D·과도한 그라데이션·불필요한 범례 금지
- 데이터 라벨은 결론을 돕는 값만
- 축을 자르면 명확히 표시
- 실제 데이터가 없으면 정량 차트처럼 보이는 가짜 그래프를 만들지 않는다

## 8. Layout rhythm

20장 기준 예시:

- 2장: 강한 타이포/섹션 표지
- 3장: 흐름·타임라인
- 3장: 비교·결정
- 3장: 계층·아키텍처
- 3장: 숫자·데이터
- 2장: 사례·인용
- 2장: 프로세스·로드맵
- 2장: 요약·행동

이 비율은 내용에 따라 달라진다. 핵심은 동일 카드 구조가 기본값이 되지 않는 것이다.

## 9. Design DNA 기록 템플릿

```text
Audience:
Purpose:
Environment:
Concept words:
Visual metaphor:
Primary archetype:
Counter-influence:
Canvas / Ink / Primary / Secondary / Accent:
Semantic colors:
Typography:
Shape language:
Image strategy:
Chart grammar:
Layout families:
Avoid list:
Why this fits:
```

## 10. 적응성 최종 검사

- 회사명과 주제만 바꾸면 이전 덱과 동일해 보이는가? 그러면 실패다.
- 팔레트 선택 이유를 청중·목적과 연결해 설명할 수 있는가?
- 카드·배지·라운드 사각형을 제거해도 서사가 유지되는가?
- 섹션마다 리듬이 변하지만 같은 덱으로 느껴지는가?
- 디자인이 정보보다 먼저 보이지 않는가?

