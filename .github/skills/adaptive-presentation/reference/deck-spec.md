# Deck Spec Contract

`deck-spec.json`은 요청·스토리라인·Fact Ledger·템플릿·폰트·QA를 연결하는 authoritative contract다.
생성 코드와 verifier는 이 파일을 함께 사용하며, CLI 플래그가 충돌하면 spec을 우선하고 실패한다.
`storyline.md`에는 메시지·다음 행동·시각 형태·발표 흐름을 두고, spec에는 검증에 필요한 값만 기록한다.

## 최소 구조

외부 사실이나 템플릿이 없는 2장 덱의 완결된 입력이다. 정책 기본값을 생략해도 검증은 유지된다.

```json
{
  "schemaVersion": 1,
  "request": {
    "topic": "업무 개선 실행 계획",
    "audience": "CIO",
    "purpose": "의사결정",
    "language": "ko-KR",
    "slideCount": 2
  },
  "canvas": {"source": "default", "widthIn": 13.333, "heightIn": 7.5},
  "fontPolicy": {
    "selected": "Apple SD Gothic Neo",
    "fallbacks": [],
    "requireAvailable": true,
    "requireRenderedMatch": true
  },
  "slides": [
    {
      "number": 1,
      "role": "cover",
      "title": "반복 작업과 검토 흐름을 먼저 정리합니다",
      "claimIds": [],
      "stateLabels": []
    },
    {
      "number": 2,
      "role": "recommendation",
      "title": "작은 실행부터 개선 범위를 확인합니다",
      "claimIds": [],
      "stateLabels": []
    }
  ],
  "qa": {
    "strict": true,
    "minBodyPt": 15,
    "minTitlePt": 26,
    "maxUnmappedTextSpans": 0,
    "failRenderedOverflow": true,
    "requireVisualReview": true
  }
}
```

## 기본값과 필요한 override

[schema](../schema/deck-spec.schema.json)는 작성 입력의 필드·타입을 검사한다.
`deck_spec.py`는 생략한 정책 값을 채운 뒤 임계치 순서·mode별 필드·출처 참조·장수를 검사한다.
schema 통과만으로 완료하거나 semantic validation을 생략하지 않는다.
기본값 전체를 spec에 복사하지 말고 바꾸거나 덱별로 지정해야 하는 값만 쓴다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/deck_spec.py <work>/deck-spec.json --json
```

| 조건 | 기록할 값 |
|---|---|
| 한국어 덱 | `languagePolicy`·`speakerNotesPolicy`를 생략하거나 부분 지정하면 각 기본 정책이 적용됨 |
| 공식명·기술 용어 사용 | 실제로 쓰는 명칭만 `languagePolicy.protectedTerms`에 기록 |
| 브랜드·템플릿 글꼴 | 설치된 글꼴을 `fontPolicy.selected`로 지정; `leadingMessage` 생략 시 selected와 기본 스타일 적용 |
| 외부 사실 인용 | `factLedger` 경로와 장별 `claimIds`; Accepted Fact만 참조 |
| 템플릿 사용 | `templateProfile` 경로와 `canvas.source=template`; 원본 canvas 유지 |
| 의도적 QA 예외 | 검토 후 `qa.exceptionManifest`에 finding별 이유 기록 |

아래 JSON은 실제로 두 공식명을 사용하며 진행 질문·전환 cue를 **사용자가 요청한 경우**에만 위 최소
spec에 병합하는 선택적 override다. 일반 발표 notes는 `core-only`를 유지한다.

```json
{
  "languagePolicy": {"protectedTerms": ["GitHub Copilot", "Microsoft Foundry"]},
  "speakerNotesPolicy": {"mode": "guided-flow"}
}
```

전체 필드·타입은 schema, 편집 기준은 [글꼴](./pptx-production.md#fonts)·
[타이포그래피](./pptx-production.md#typography)·[언어](./pptx-production.md#language)·
[발표 노트 계약](./pptx-production.md#speaker-notes)을 따른다.
`requireAllTextFont=true`이면 모든 visible run과 `leadingMessage.fontFamily`가 `selected`와 같아야 한다.
`fallbacks`는 렌더 대체만 허용하며 PPTX 내부의 혼용 글꼴로 쓸 수 없다.
`protectedTerms`는 존재 여부를 검사하고 영문 비율에서 중립 처리한다. 해당 장에는 쉬운 한글 설명도
필요하다. 높은 영문 비율의 의도적 예외는 contact sheet와 확대 화면을 검토한 뒤에만 지정한다.
legacy notes의 질문·전환 필드가 있으면 생략한 `mode`를 `guided-flow`로 인식하는 호환성은 유지한다.

## 슬라이드와 근거

`slides`는 `request.slideCount`와 정확히 일치하고 1부터 연속 번호를 사용한다. `claimIds`는 공통
Fact Ledger JSON의 `Accepted`인 `Fact` ID만 참조한다. Inference는 근거 Fact ID를 연결하고 Assumption은
`stateLabels`로 표시한다. `claimIds`는 machine contract와 Fact Ledger에만 남기며 speaker notes에는
넣지 않는다. 해당 슬라이드 footer에는 `출처: Publisher · Document title`처럼 발행자와 문서명을
표시한다. Preview·가정·시연 수치는 `stateLabels`에 기록하고 실제 슬라이드에도 같은 텍스트를 보여준다.
footer는 문서명과 원문 hyperlink로 연결한다. 원본 확인 날짜는 화면에서 기본 생략하고
Fact Ledger의 `accessed`에 보존하되 발행 연도·수치 기준일·버전·시행일은 유지한다.
Fact ID·URL·출처 블록은 notes에 넣지 않는다. 외부 사실이 없는 진단·실행 장은 Recommendation·
ASSUMPTION 같은 성격과 검증 조건을 표시한다.
내용 보존표·장별 발표 시간 합계·대비 측정은 세션의 별도 검토 기록이다. 이를 기록하기 위해
schema에 없는 필드를 추가하거나 canonical verifier가 자동 검증한다고 가정하지 않는다.

## 템플릿

PPTX/POTX 템플릿이 있으면 먼저 profile을 만든다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/inspect_template.py template.pptx \
  --out <work>/template-profile.json
```

`canvas.source`를 `template`로 두고 `templateProfile`을 지정한다. 생성기는 템플릿을 열어 기존
master·layout·theme·canvas를 보존하고 필요한 경우 기존 예시 슬라이드만 제거한다. verifier는 최종
deck의 canvas와 theme fingerprint가 profile과 일치하는지 확인한다.
POTX는 원본을 변경하지 않고 메모리에서 presentation content type으로 로딩한 뒤 새 PPTX로 저장한다.
XML fingerprint는 들여쓰기·속성 순서 같은 직렬화 차이를 정규화하지만 의미 있는 텍스트·속성과
연결된 binary 자산의 변경은 유지한다. 이전 검증기의 raw XML fingerprint로 만든 profile은 원본
템플릿에서 새 파일로 다시 추출하고 `templateProfile` 경로를 갱신한다.

## QA 증거

`qa.exceptionManifest`는 검토한 finding의 `findingId`와 이유를 연결한다. 슬라이드 전체 예외는
레거시 호환용이며 새 작업에서는 쓰지 않는다. 최종 deck과 검토한 렌더 환경의 해시에 묶인 증거가
필요하며, 기존 증거를 덮어쓰지 않는다.
실행 명령·캐시·수정 후 증거 생성은 [검증 가이드](./verification.md)와
[revision별 증거 절차](./verification.md#visual-review-revisions) 한 곳에서 따른다.
