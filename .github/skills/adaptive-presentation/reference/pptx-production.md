# PPTX Production

## 1. 도구 선택

1. 저장소의 `pptx_compiler`를 기본 생성 엔진으로 사용하고, 디자인 토큰은 매 요청의 새 Design DNA로 주입한다.
2. Python 환경에서는 `python-pptx`를 우선한다.
3. 대량 차트나 데이터 처리에는 pandas/matplotlib를 사용할 수 있으나 결과가 편집 가능해야 하는 핵심 도표는
   PowerPoint 도형으로 만든다.
4. 외부 이미지가 필요한 경우 사용권과 원본 URL을 기록한다.

`reference/full-optimized.md`의 실행 규칙을 기본값으로 사용한다. 도구 탐색과 의존성 준비는 저장소
밖 캐시에서 재사용하며, 조사·Design DNA·최종 조립은 별도의 에이전트가 중복 수행하지 않는다.

## 2. 권장 파일 구조

```text
<output>/<deck>.pptx             # 사용자에게 보이는 기본 산출물

<session>/files/<deck>-work/
  fact-ledger.md
  deck-spec.md
  design-dna.md
  build_<deck>.py
  compiler-report.json
  <deck>_generation_prompt.txt   # 필요할 때만
  defects.md
  metrics.json
  qa/
    contact-01-30.jpg
    slide-08.jpg                 # 선택 검수 시에만
```

생성 스크립트·프롬프트·QA 산출물을 저장소 루트나 최종 출력 폴더에 두지 않는다. 사용자가 해당
파일을 명시적으로 요청한 경우에만 세션 작업 폴더에서 최종 출력 위치로 복사한다.
최초 전체 렌더의 중간 PDF는 같은 PPTX 리비전의 상세 검사가 끝날 때까지만 유지하고 최종 정리에서
삭제한다. 사용자가 PDF 산출물을 요청한 경우에만 최종 출력 위치로 복사한다.
Python은 `python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 저장소에 `__pycache__`와
`.pyc`가 생기지 않게 한다.

## 3. 생성 스크립트 구조

```python
import os
import sys
from pathlib import Path

SKILL_DIR = Path("<absolute-skill-dir>")
sys.path.insert(0, str(SKILL_DIR))

from pptx_compiler import (
    DesignDNA,
    Palette,
    ShapeLanguage,
    SlideCompiler,
    SlideFrame,
    Typography,
)

OUT = Path(os.environ["PPTX_OUT"])
WORK = Path(os.environ["PPTX_WORK"])

def build():
    design = DesignDNA(...)  # 이번 deck의 design-dna.md에서 생성
    compiler = SlideCompiler(design, title="...")
    slide = compiler.begin_slide(
        SlideFrame(title="결론형 제목", section="WHY", number=1),
        family="statement",
        variant="hero-left",
    )
    slide.text("hero", "...", role="metric")
    compiler.save(
        OUT,
        expected_slides=30,
        min_layout_families=8,
        report_path=WORK / "compiler-report.json",
    )
```

권장 분리:

- Design DNA 객체: 색, 폰트, 선, 여백, 반경
- Compiler primitive: text, shape, line, arrow, image, source, badge, chip
- semantic blueprint: cover, statement, comparison, process, layered, matrix, architecture, code, roadmap
- semantic component: metric, status, timeline node, decision gate
- slide function: 한 슬라이드의 구성
- build/validate entry point

Compiler는 생성 메커니즘만 재사용한다. 샘플 팔레트·고정 커버·기본 카드 구도를 복사하지 않으며,
슬라이드 내용을 거대한 JSON 하나에 넣어 모든 장을 같은 레이아웃으로 렌더하지 않는다.

## 4. 화면과 안전 영역

- 기본: 13.333 × 7.5 inch
- 좌우 여백: 0.6~0.8 inch
- 제목 영역: 상단 0.4~1.45 inch
- 본문 영역: 약 1.6~6.75 inch
- 출처/페이지: 7.0 inch 부근
- 장식 도형은 의도적으로 bleed할 수 있지만 텍스트는 안전 영역 안에 둔다

슬라이드 경계 검사는 EMU 좌표로 수행한다.

## 5. 텍스트

### 규칙

- `word_wrap=True`, `auto_size=NONE`
- 텍스트 프레임 margin을 명시
- 모든 run에 font name/size/color를 직접 적용
- 한글과 영문 혼용 렌더를 실제 PDF에서 확인
- 줄 간격과 paragraph spacing을 명시

### 크기

- 제목 28~40pt
- 주요 본문 18~24pt
- 보조 14~17pt
- 출처 8.5~10pt

16pt 미만 본문이 필요하면 정보가 과밀하다는 신호다.

### 텍스트 밀도

- 일반 슬라이드: 주요 본문 35~55단어
- 기술 슬라이드: 구조화된 짧은 라벨을 포함해도 문장 수는 제한
- 표/부록: 목적상 밀도가 필요하면 명확히 Appendix로 구분

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

- HEX는 Design DNA에서 주입
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
- 그림자와 라운드 사각형은 Design DNA에 있을 때만 사용

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
- 대체 텍스트 또는 캡션이 필요한 환경인지 고려
- 공식 제품 UI 스크린샷은 날짜와 버전을 확인
- 고객 로고는 공식 자산만 사용

## 12. 출처

주장 슬라이드의 footer에 직접 표시한다.

```text
Source: Organization · Document title (accessed YYYY-MM-DD)
```

- 긴 URL은 제목에 hyperlink를 걸거나 짧은 경로로 표시
- 여러 출처는 2개를 넘기지 않도록 핵심 근거를 선택
- 상세 출처 목록은 Appendix 또는 prompt/source artifact에 제공
- 생성형 AI로 만든 그림이나 DEMO DATA는 명시

## 13. 상태·불확실성

- GA: green 계열 + `GA`
- Partial GA: amber 계열 + `PARTIAL GA`
- Preview: 별도 accent + `PREVIEW`
- 가정: `ASSUMPTION`
- 시연 수치: `DEMO DATA`

색상은 Design DNA에 맞춰 조정하되 텍스트 라벨은 유지한다.

## 14. 성능과 파일 크기

- 동일 이미지를 여러 번 삽입하면 재사용 여부를 검토
- 지나치게 큰 PNG 대신 적정 해상도 사용
- SVG 지원이 불안정한 환경이면 검증된 PNG 또는 PowerPoint 도형 사용
- 중복되지 않는 수백 개 도형은 편집성과 렌더 성능을 모두 고려

## 15. 완성 직전

```bash
python3 -B -c 'import ast,pathlib; ast.parse(pathlib.Path("<work-dir>/build_<deck>.py").read_text(encoding="utf-8"))'
PPTX_OUT="<absolute-output>/<deck>.pptx" PPTX_WORK="<work-dir>" \
  python3 -B <work-dir>/build_<deck>.py
# 다음 두 검사는 같은 immutable PPTX를 읽으므로 병렬 실행 가능
python3 -B .github/skills/adaptive-presentation/scripts/audit_pptx.py <absolute-output>/<deck>.pptx
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  <absolute-output>/<deck>.pptx --out <work-dir>/qa --keep-pdf
# PPTX를 수정하기 전, 의심 슬라이드는 기존 PDF를 재사용해 개별 JPEG로 확인
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  <absolute-output>/<deck>.pptx --reuse-pdf <work-dir>/qa/<deck>.pdf \
  --slides 8,16 --keep-slide-images --out <work-dir>/qa-detail
unzip -t <absolute-output>/<deck>.pptx
```

`py_compile`은 `.pyc`를 만들 수 있으므로 사용하지 않는다. 문법 검사는 위처럼 `ast.parse`로 수행하고,
실행·감사·렌더 명령에는 모두 `-B`를 사용한다.

`--reuse-pdf`는 sibling `manifest.json`의 PPTX SHA-256과 현재 파일이 일치할 때만 PDF를 재사용한다.
PPTX를 수정한 뒤에는 기존 PDF를 재사용하지 말고 새 전체 렌더를 수행한다.
