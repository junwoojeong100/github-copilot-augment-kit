# Verification

PPTX는 생성 후 반드시 **구조 감사 + 전체 렌더 + 시각 수정**을 거친다.

## 1. 구조 감사

```bash
python3 -B .github/skills/adaptive-presentation/scripts/audit_pptx.py deck.pptx
```

검사 항목:

- 슬라이드 장수와 화면비
- PowerPoint 압축 구조
- 슬라이드 경계를 벗어난 도형
- 사용 글꼴과 크기 분포
- 출처를 제외한 작은 텍스트 후보
- 슬라이드별 텍스트 문자 수
- 비어 있는 텍스트 프레임

감사 스크립트는 주요 본문과 짧은 label/chip 후보를 분리해 보고한다. label 경고는 시각 검토 대상이며
그 자체가 실패는 아니다. 그룹 도형이 있으면 내부 텍스트는 검사하지만 자식 좌표의 시각적 경계는 렌더로 확인한다.

장식 도형의 intentional bleed는 허용할 수 있다. 감사 결과를 맹목적으로 통과시키지 말고 항목별로 판단한다.

## 2. 전체 렌더

필요 도구:

- LibreOffice `soffice`
- PyMuPDF `fitz`
- Pillow

```bash
# 기본: 30장 단위 overview JPEG만 남김
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --out <session>/files/<deck>-work/qa --keep-pdf
```

결과:

- 30장 단위 `contact-01-30.jpg`
- 개별 slide JPEG는 기본적으로 contact sheet 생성 후 삭제
- 중간 PDF도 기본적으로 렌더 후 삭제

기본 JPEG는 파일당 900KiB 이하로 압축된다. PPTX와 PDF는 렌더 입력/중간 산출물일 뿐 `view`로 열지 않는다.

## 3. contact sheet 검사

전체 흐름은 compact overview JPEG **한 장씩** 본다.

- 섹션 리듬이 존재하는가?
- 모든 장이 같은 카드 그리드처럼 보이지 않는가?
- 제목 길이와 위치가 안정적인가?
- 배경 전환이 의도적인가?
- 강조색이 너무 자주 바뀌지 않는가?
- 시각적 밀도가 한 구간에 몰리지 않는가?

## 4. 원본 크기 검사

다음 슬라이드는 필요한 것만 개별 JPEG로 다시 렌더해 본다.

- 가장 텍스트가 많은 장
- 표·코드·복잡한 아키텍처
- 긴 제목
- 고객 사례와 큰 숫자
- 섹션 표지와 마지막 장
- contact sheet에서 조금이라도 어색한 장

```bash
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --reuse-pdf <session>/files/<deck>-work/qa/<deck>.pdf \
  --slides 8,16,22 --keep-slide-images \
  --out <session>/files/<deck>-work/qa-detail
```

이 상세 검사는 PPTX를 수정하기 전에 수행한다. `--reuse-pdf`는 manifest의 PPTX SHA-256을 검사하며,
파일이 달라지면 실패하므로 오래된 PDF를 사용할 수 없다.

한 응답에서 full-slide 이미지는 최대 2~3개만 확인한다. 여러 장을 병렬로 `view`하면 다음 요청에서
`Images and/or native document attachments were removed ...` 메시지가 발생할 수 있다.

확인:

- 텍스트가 카드/도형 밖으로 넘치는가?
- 텍스트 프레임 높이가 줄 수를 수용하는가?
- 연결선이 글자를 가리는가?
- source와 page number가 겹치는가?
- 한글 조사와 영문 혼용이 이상하게 줄바꿈되는가?
- 대비가 충분한가?
- 정렬이 2~3px 수준으로 흔들리지 않는가?

## 5. 합격 임계치

| 항목 | 기준 |
|---|---|
| Slide count | 요청과 정확히 일치 |
| Bounds | 의도하지 않은 out-of-bounds 0 |
| Primary body | 원칙적으로 18pt+, 최소 16pt |
| Source/footer | 8.5~10pt 허용 |
| Layout diversity | 20장 이상 8 family+, 10~19장 5 family+ |
| Repetition | 동일 family 2장 연속 권장, 3장 연속은 의도 설명 필요 |
| Card grids | 전체의 약 35% 이하 권장 |
| Claims | 숫자·상태·고객 성과에 source |
| Preview/demo | 텍스트 라벨 존재 |
| Render | 전체 compact overview 생성 + 위험 슬라이드 선택 렌더 |
| Integrity | `unzip -t` 오류 0 |

## 6. 수정 루프

1. 결함을 슬라이드 번호와 유형으로 기록
2. 원인을 구분: content density / geometry / typography / contrast / narrative
3. 폰트 축소보다 내용·레이아웃 수정 우선
4. 모든 결함을 `defects.md`에 모은 뒤 세션 작업 폴더의 생성 스크립트를 한 번에 수정
5. PPTX 재생성
6. 구조 감사와 변경 슬라이드 검사를 수행
7. 변경이 있었다면 전체 렌더와 전체 contact sheet를 다시 생성

최초 PPTX의 구조 감사와 전체 렌더는 서로 읽기 전용이므로 병렬 실행한다. 수정 후에는 영향 슬라이드
검사로 빠르게 회귀를 확인하되, 완료 판정은 마지막 전체 렌더 이후에만 한다.

## 7. 디자인 적응성 검사

같은 저장소의 최근 덱 또는 사용자가 제공한 이전 자료와 비교한다.

- Canvas/Primary/Accent가 사실상 동일한가?
- 같은 커버 구도·섹션 바·카드 반경을 그대로 썼는가?
- 주제가 바뀌었는데도 동일한 SaaS UI처럼 보이는가?
- 새 Design DNA의 concept words가 실제 도형·타이포·리듬에 나타나는가?

동일해 보인다면 단순 색상 교체가 아니라 시각 은유와 layout rhythm을 다시 설계한다.

## 8. 정리

```bash
rm -rf <session>/files/<deck>-work/qa <session>/files/<deck>-work/qa-detail
```

재생성 스크립트와 프롬프트는 세션 작업 폴더에만 둔다. 저장소와 최종 출력 폴더에는 사용자가 요청한
최종 PPTX/PDF만 남기며, `.py`, `.pyc`, `__pycache__`, 중간 PDF, QA 이미지는 남기지 않는다.

단계별 시간과 `pdf_reused`, `tool_cache_hit`, `repair_cycles`는 세션 작업 폴더의 `metrics.json`에 기록한다.
