# PPTX Production

슬라이드는 고정 생성 엔진이나 컴포넌트 라이브러리 없이 **`python-pptx`로 직접** 만든다. 매 덱마다
주제에 맞는 시각 형태를 자유롭게 구성하되, 아래 품질·위생 기준은 지킨다.

## 1. 도구

1. Python 환경에서 `python-pptx`를 기본으로 사용한다.
2. 대량 데이터 처리·차트 계산에는 pandas/matplotlib를 쓸 수 있으나, 발표에 들어가는 핵심 도표는
   가능하면 PowerPoint 도형/네이티브 차트로 만들어 편집 가능하게 한다.
3. 외부 이미지가 필요하면 사용권과 원본 URL을 기록한다.
4. 도구 탐색·의존성 준비는 `reference/full-optimized.md`의 캐시 규칙을 따른다.

## 2. 파일 구조

```text
<output>/<deck>.pptx                 # 사용자에게 보이는 기본 산출물

<session>/files/<deck>-work/
  fact-ledger.md
  storyline.md
  build_<deck>.py                    # python-pptx 직접 생성 스크립트
  qa/
    contact-01-30.jpg
    slide-08.jpg                     # 선택 검수 시에만
```

생성 스크립트·QA 산출물을 저장소 루트나 최종 출력 폴더에 두지 않는다. 사용자가 요청한 경우에만 세션
작업 폴더에서 최종 출력 위치로 복사한다. 중간 PDF는 QA가 끝날 때까지만 두고 정리한다. Python은
`python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 저장소에 `__pycache__`·`.pyc`가 생기지 않게 한다.

## 3. 생성 스크립트 골격

`python-pptx`를 직접 사용하는 최소 골격이다. 슬라이드마다 필요한 도형·텍스트·차트를 자유롭게 배치한다.

```python
import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

OUT = Path(os.environ["PPTX_OUT"])

# 주제·브랜드에 맞게 자유롭게 정하는 값 (고정 팔레트 아님)
INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x0F, 0x62, 0xFE)
CANVAS = RGBColor(0xFF, 0xFF, 0xFF)
BODY_FONT = "Apple SD Gothic Neo"

def textbox(slide, text, x, y, w, h, size, *, color=INK, bold=False,
            align=PP_ALIGN.LEFT, font=BODY_FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font
    run.font.color.rgb = color
    return box

def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 슬라이드마다 정보 관계에 맞는 형태를 직접 구성한다.
    slide = prs.slides.add_slide(blank)
    textbox(slide, "결론형 제목", 0.72, 0.5, 11.9, 1.0, 34, bold=True)
    # ... 도형·차트·출처 footer 등 자유 배치 ...

    prs.save(OUT)

if __name__ == "__main__":
    build()
```

거대한 JSON 하나로 모든 장을 같은 레이아웃으로 렌더하지 않는다. 슬라이드마다 함수/구성을 나눠
정보 유형에 맞는 형태를 만든다.

## 4. 화면과 안전 영역

- 기본: 13.333 × 7.5 inch
- 좌우 여백: 0.6~0.8 inch
- 제목 영역: 상단 0.4~1.45 inch
- 본문 영역: 약 1.6~6.75 inch
- 출처/페이지: 7.0 inch 부근
- 장식 도형은 의도적으로 bleed할 수 있지만 텍스트는 안전 영역 안에 둔다

## 5. 텍스트

- `word_wrap=True`, `auto_size=NONE`
- 텍스트 프레임 margin을 명시
- 모든 run에 font name/size/color를 직접 적용
- 한글과 영문 혼용 렌더를 실제 PDF에서 확인
- 줄 간격과 paragraph spacing을 명시

크기:

- 제목 28~40pt
- 주요 본문 18~24pt
- 보조 14~17pt
- 출처 8.5~10pt

16pt 미만 본문이 필요하면 정보가 과밀하다는 신호다. 폰트를 줄이지 말고 내용을 줄인다.

밀도: 일반 슬라이드는 주요 본문 35~55단어, 기술 슬라이드도 문장 수를 제한한다. 표/부록은 필요하면
명확히 Appendix로 구분한다.

## 6. 한글 폰트

실행 환경에서 폰트를 검색한다.

```bash
(fc-list 2>/dev/null || true) | grep -Ei 'Noto Sans|Apple SD Gothic|Malgun|Aptos|Segoe'
```

예시 폴백:

- macOS: Apple SD Gothic Neo
- Windows: Malgun Gothic
- 공통 배포 환경: Noto Sans CJK KR 설치 여부 확인

폰트를 PPTX에 임베드할 수 있다고 가정하지 않는다.

## 7. 색과 대비

- 색은 주제와 (있다면) 사용자 브랜드에서 자유롭게 정한다. 고정 팔레트를 강제하지 않는다.
- 본문과 배경 대비 최소 4.5:1
- 제목은 크더라도 낮은 대비 회색으로 두지 않는다
- 색만으로 상태를 전달하지 않고 GA/PREVIEW/위험 텍스트를 병기
- PDF 변환에서 색이 달라질 수 있으므로 렌더를 확인

## 8. 도형과 연결선

- 도형은 정보 계층을 표현해야 한다
- 선은 시작과 끝의 의미가 명확해야 한다
- 교차선 최소화
- 화살표 방향은 발표 흐름과 일치
- 포함 관계와 연결 관계를 다른 스타일로 표현

## 9. 표

- 6행×5열을 기본 상한으로 권장
- 공통 비교 축을 왼쪽에 고정
- 숫자 정렬과 단위 통일
- 긴 문장을 셀에 넣지 않는다
- 표가 핵심 메시지를 숨기면 비교 카드·dot plot·decision tree로 전환

## 10. 차트

- 실제 데이터와 기준일을 사용
- 차트 제목은 데이터 이름이 아니라 결론
- 단위, 축 범위, 표본/출처 표시
- 선택 계열 1개만 강한 색
- 단순 막대·선·dot plot을 우선
- 파이/도넛은 5개 이하의 구성비에서만
- 3D 차트 금지

편집 가능성이 중요하면 PowerPoint 기본 chart API 또는 도형 기반 차트를 사용한다.

## 11. 이미지

- 낮은 해상도 이미지를 늘리지 않는다
- 크롭 비율을 통일
- 텍스트 위에 복잡한 이미지를 직접 깔지 않는다
- 공식 제품 UI 스크린샷은 날짜와 버전을 확인
- 고객 로고는 공식 자산만 사용

## 12. 출처

주장 슬라이드의 footer에 직접 표시한다.

```text
Source: Organization · Document title (accessed YYYY-MM-DD)
```

- 긴 URL은 제목에 hyperlink를 걸거나 짧은 경로로 표시
- 여러 출처는 2개를 넘기지 않도록 핵심 근거를 선택
- 생성형 AI로 만든 그림이나 DEMO DATA는 명시

## 13. 상태·불확실성

- GA: green 계열 + `GA`
- Partial GA: amber 계열 + `PARTIAL GA`
- Preview: 별도 accent + `PREVIEW`
- 가정: `ASSUMPTION`
- 시연 수치: `DEMO DATA`

색은 자유롭게 조정하되 텍스트 라벨은 반드시 유지한다.

## 14. 완성 직전

```bash
# 문법 검사 (.pyc를 만들지 않도록 py_compile 대신 ast.parse 사용)
python3 -B -c 'import ast,pathlib; ast.parse(pathlib.Path("<work-dir>/build_<deck>.py").read_text(encoding="utf-8"))'

# 생성
PPTX_OUT="<absolute-output>/<deck>.pptx" python3 -B <work-dir>/build_<deck>.py

# 감사와 렌더는 같은 immutable PPTX를 읽으므로 병렬 실행 가능
python3 -B .github/skills/adaptive-presentation/scripts/audit_pptx.py <absolute-output>/<deck>.pptx
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  <absolute-output>/<deck>.pptx --out <work-dir>/qa --keep-pdf

# 의심 슬라이드는 기존 PDF를 재사용해 개별 JPEG로 확인
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  <absolute-output>/<deck>.pptx --reuse-pdf <work-dir>/qa/<deck>.pdf \
  --slides 8,16 --keep-slide-images --out <work-dir>/qa-detail

unzip -t <absolute-output>/<deck>.pptx
```

`--reuse-pdf`는 sibling manifest의 PPTX SHA-256과 현재 파일이 일치할 때만 PDF를 재사용한다. PPTX를
수정한 뒤에는 기존 PDF를 재사용하지 말고 새 전체 렌더를 수행한다.
