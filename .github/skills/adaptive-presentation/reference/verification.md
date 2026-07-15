# Verification

생성 성공은 완료가 아니다. PPTX는 **구조 감사 + 전체 렌더 + 시각 확인**을 거친 뒤에야 완료다.
목표는 **한 번의 전체 패스**로 결함을 찾아 일괄 수정하고, 변경이 있을 때만 다시 렌더하는 것이다.

기본 실행:

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx --out <work-dir> --expected-slides 30 --strict
```

Runner가 구조 감사와 전체 렌더를 읽기 전용으로 병렬 실행하고, risk score가 높은 슬라이드를 같은 PDF로
상세 렌더한다. `verification-report.json`, `qa/contact-*.jpg`, `qa-detail/slide-*.jpg`를 확인한 뒤
결함을 일괄 수정한다. `--strict`는 작은 본문 후보와 title risk를 실패 처리한다. 사람이 확인한 의도적
보조 텍스트가 있을 때만 `--allow-small-text`를 쓴다.

## 1. 구조 감사

```bash
python3 -B .github/skills/adaptive-presentation/scripts/audit_pptx.py deck.pptx
```

검사 항목(임의 PPTX 대상, 생성 방식과 무관):

- 슬라이드 장수와 화면비
- PowerPoint 압축 구조(ZIP integrity)
- 슬라이드 경계를 벗어난 도형
- 사용 글꼴과 크기 분포
- 출처를 제외한 작은 텍스트 후보
- 슬라이드별 텍스트 문자 수
- 비어 있는 텍스트 프레임

감사 스크립트는 주요 본문과 짧은 label/chip 후보를 분리해 보고한다. label 경고는 시각 검토 대상이며
그 자체가 실패는 아니다. 그룹 도형이 있으면 내부 텍스트는 검사하지만 자식 좌표의 시각적 경계는 렌더로
확인한다. 장식 도형의 intentional bleed는 허용할 수 있다. 감사 결과를 맹목적으로 통과시키지 말고
항목별로 판단한다.

## 2. 전체 렌더

필요 도구: LibreOffice `soffice`, PyMuPDF `fitz`, Pillow.

```bash
# 기본: 30장 단위 overview JPEG만 남김
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --out <session>/files/<deck>-work/qa --keep-pdf
```

결과:

- 30장 단위 `contact-01-30.jpg`
- 개별 slide JPEG는 contact sheet 생성 후 삭제
- 중간 PDF도 렌더 후 삭제(위 예시는 `--keep-pdf`로 상세 검사 동안만 유지)

기본 JPEG는 파일당 900KiB 이하로 압축된다. PPTX와 PDF는 렌더 입력/중간 산출물일 뿐 `view`로 열지 않는다.

## 3. contact sheet 검사

전체 흐름은 compact overview JPEG **한 장씩** 본다.

- 섹션 리듬이 있는가?
- 모든 장이 같은 카드 그리드처럼 보이지 않는가? (같은 구조 반복이면 일부를 다른 관계형 형태로 교체)
- 제목 길이와 위치가 안정적인가?
- 시각적 밀도가 한 구간에 몰리지 않는가?

## 4. 위험 슬라이드 확인

의심 슬라이드만 기존 PDF를 재사용해 개별 JPEG로 다시 렌더한다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --reuse-pdf <session>/files/<deck>-work/qa/<deck>.pdf \
  --slides 8,16,22 --keep-slide-images \
  --out <session>/files/<deck>-work/qa-detail
```

이 상세 검사는 PPTX를 수정하기 전에 수행한다. `--reuse-pdf`는 manifest의 PPTX SHA-256을 검사하며,
파일이 달라지면 실패하므로 오래된 PDF를 쓸 수 없다. 한 응답에서 full-slide 이미지는 최대 2~3개만
확인한다.

확인:

- 텍스트가 도형 밖으로 넘치는가?
- 텍스트 프레임 높이가 줄 수를 수용하는가?
- 연결선이 글자를 가리는가?
- source와 page number가 겹치는가?
- 한글 조사와 영문 혼용이 이상하게 줄바꿈되는가?
- 대비가 충분한가?
- 정렬이 흔들리지 않는가?

## 5. 합격 임계치

| 항목 | 기준 |
|---|---|
| Slide count | 요청과 정확히 일치 |
| Bounds | 의도하지 않은 out-of-bounds 0 |
| Primary body | 원칙적으로 18pt+, 최소 16pt |
| Source/footer | 8.5~10pt 허용 |
| 다양성 | 같은 구조를 기계적으로 반복하지 않음(정보 유형에 맞게 형태를 바꿈) |
| Claims | 숫자·상태·고객 성과에 source |
| Preview/demo | 텍스트 라벨 존재 |
| Render | 전체 compact overview 생성 + 위험 슬라이드 선택 렌더 |
| Integrity | `unzip -t` 오류 0 |

## 6. 수정 루프 (시간 최소화)

1. 결함을 슬라이드 번호와 유형으로 기록한다.
2. 원인을 구분한다: content density / geometry / typography / contrast / narrative.
3. 폰트 축소보다 내용·레이아웃 수정을 우선한다.
4. 모든 결함을 모아 세션 작업 폴더의 `build_<deck>.py`를 **한 번에** 수정한다.
5. PPTX를 재생성한다.
6. 변경 슬라이드만 빠르게 회귀 확인한다.
7. 변경이 있었을 때만 전체 렌더와 전체 contact sheet를 다시 생성한다. 변경이 없으면 최초 전체 렌더가
   최종 검증이다.

## 7. 정리

```bash
rm -rf <session>/files/<deck>-work/qa <session>/files/<deck>-work/qa-detail
```

재생성 스크립트는 세션 작업 폴더에만 둔다. 저장소와 최종 출력 폴더에는 사용자가 요청한 최종 PPTX/PDF만
남기며, `.py`, `.pyc`, `__pycache__`, 중간 PDF, QA 이미지는 남기지 않는다.
