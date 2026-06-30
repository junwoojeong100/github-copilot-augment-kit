# Verification (렌더 + 폰트 감사 + 하이퍼링크)

PPTX는 **반드시 실제로 렌더링해 시각 검증**한다. macOS에 PowerPoint가 없어도 `soffice`(LibreOffice)로 PDF 변환 후
`PyMuPDF(fitz)`로 PNG를 떠서 눈으로 확인하고, 폰트 폴백·하이퍼링크를 자동 점검한다. 끝나면 부산물을 정리한다.

## 0. 전제
- LibreOffice 설치(macOS: `/opt/homebrew/bin/soffice`). `python3 -m pip install PyMuPDF --break-system-packages`.

## 1. PDF 변환 + PNG 렌더
```bash
SOFFICE=/opt/homebrew/bin/soffice            # 경로 다르면 `which soffice`
"$SOFFICE" --headless --convert-to pdf --outdir . deck.pptx
mkdir -p shots
python3 - <<'PY'
import fitz
doc = fitz.open('deck.pdf')
for i, page in enumerate(doc, 1):
    pix = page.get_pixmap(dpi=130)
    pix.save(f'shots/slide{i:02d}.png')
print('rendered', doc.page_count, 'slides')
PY
```
→ `shots/slideNN.png`를 **이미지로 직접 확인**: 텍스트 잘림·겹침, 대비, 정렬, 빈 영역, 표/도식 깨짐, KPI에 빈값 없는지.

## 2. 폰트 감사 (PingFang/Arial 폴백 0)
```python
import fitz
doc = fitz.open('deck.pdf'); bad = {}
for pno, page in enumerate(doc, 1):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for sp in l.get('spans', []):
                f = sp['font']
                if ('PingFang' in f) or ('Arial' in f) or ('Helvetica' in f) or ('Sans-serif' in f):
                    bad.setdefault(f, set()).add(sp['text'][:12])
print('FALLBACK FONTS:', {k: list(v)[:5] for k, v in bad.items()} or 'NONE')
```
- **`NONE`이어야 합격**. 폴백이 남으면: (a) 한글이 PingFang 등 → 해당 런에 `set_font` 누락 → 추가, (b) Helvetica/Arial가 한두 글자에만 → 폰트 미지원 기호(✗·✓·유니코드 마이너스 −(U+2212)·화살표) → **ASCII `-`·O/X** 등으로 치환하거나 지원 글리프만 사용. (latin도 `set_font`로 한글 폰트 지정하므로 Helvetica 등장 = 미지원 글리프 신호)

## 3. 하이퍼링크 검증
```python
import fitz
doc = fitz.open('deck.pdf'); uris = []
for page in doc:
    uris += [l['uri'] for l in page.get_links() if l.get('uri')]
print('LINKS:', len(uris)); [print(' -', u) for u in uris[:10]]
```
- 출처/링크 슬라이드의 URL이 기대 개수만큼 잡히는지 확인(`hyperlink()`는 PDF 변환 후에도 유지).

## 4. 합격 기준
- 전 슬라이드 렌더 이미지에 **텍스트 잘림·겹침·저대비·빈값 없음**.
- 폰트 감사 **FALLBACK FONTS: NONE**(한글이 의도한 폰트로 렌더).
- 하이퍼링크 개수가 기대치와 일치.
- 장수·제목·페이지 번호가 아웃라인과 일치.

## 5. 자주 나오는 실패 → 원인
| 증상 | 원인/수정 |
|---|---|
| 한글이 다른 폰트로(네모·다른 모양) | `set_font` 미적용 → 모든 런에 latin+ea+cs 지정 |
| 특정 기호만 폰트 다름 | 폰트 미지원 글리프(✗ 등) → ASCII/지원 글자로 치환 |
| 텍스트가 박스 밖으로 잘림 | 폰트 과대/박스 과소 → 크기↓·박스↑·문장 분할, `word_wrap=True` |
| soffice 변환 실패 | 경로/미설치 → `which soffice` 확인, LibreOffice 설치 |
| 링크가 안 잡힘 | `run.hyperlink.address` 누락 → 출처 런에 설정 |

## 6. 정리 (필수)
검증이 끝나면 결과 `.pptx`만 남기고 부산물 삭제:
```bash
rm -rf deck.pdf shots verify_fonts.py
```
> 시각 검증 PNG가 사용자에게 유용하면 보여준 뒤 정리한다. 저장소/산출물에는 **결과 `.pptx` 하나**만 남긴다.
