# PPTX Toolkit (검증된 자산 — 거의 그대로 사용)

`python-pptx`로 한글 슬라이드를 만드는 기술 토대. **한글 폰트 폴백 방지(`set_font`)**가 핵심이며, 테마 토큰만
바꿔 재사용한다. 16:9(13.333"×7.5") 기준.

## 0. 설치 (한 번)
```bash
python3 -m pip install python-pptx PyMuPDF --break-system-packages
# 렌더 검증용 LibreOffice 필요: macOS는 /opt/homebrew/bin/soffice (brew install --cask libreoffice)
```

## 1. 임포트 + 테마 토큰
```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

FONT = 'Apple SD Gothic Neo'          # Win: 'Malgun Gothic' / 크로스: 'Noto Sans KR'
MONO = 'Menlo'

def C(h): return RGBColor(h>>16 & 255, h>>8 & 255, h & 255)

# ── LIGHT 테마(기본·프로젝터 안전) ──
T = dict(
  BG=C(0xFFFFFF), PANEL=C(0xF4F6FB), PANEL2=C(0xEAEEF6),
  INK=C(0x16202E), INK2=C(0x47566B), INK3=C(0x8A98AD),
  BRAND=C(0xE2231A), BLUE=C(0x1463C9), CYAN=C(0x0E9C92),
  GREEN=C(0x1E9E63), AMBER=C(0xB8801A), VIOLET=C(0x6A4BD6),
  LINE=C(0xD8DEE9),
)
# ── DARK 테마(옵션): 아래로 교체 ──
# T = dict(BG=C(0x0A0E17),PANEL=C(0x111827),PANEL2=C(0x0F1726),INK=C(0xEEF2F9),INK2=C(0x9FB0C8),
#   INK3=C(0x64748B),BRAND=C(0xE2231A),BLUE=C(0x2B9BFF),CYAN=C(0x27E0D8),GREEN=C(0x34E29B),
#   AMBER=C(0xFFC24B),VIOLET=C(0x9B7BFF),LINE=C(0x2A3344))

W, H = 13.333, 7.5
MX = 0.7                                # 좌우 안전 여백
CW = W - 2*MX                           # 콘텐츠 폭
```

## 2. 한글 폰트 폴백 방지 (★ 가장 중요)
`run.font.name`은 **latin typeface만** 설정한다. 한글은 `a:ea`, 기호는 `a:cs`로 폴백되므로 **세 가지를 모두**
같은 폰트로 지정해야 PingFang/Arial Unicode 폴백이 사라진다.
```python
def set_font(run, name=FONT, size=None, bold=None, italic=None, color=None):
    run.font.name = name                       # a:latin
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):               # 한글(ea)·기호(cs) → 동일 폰트
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {}); rPr.append(el)
        el.set('typeface', name)
    if size   is not None: run.font.size = Pt(size)
    if bold   is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color  is not None: run.font.color.rgb = color
```
> 검증 단계에서 fitz span 폰트에 `PingFang`/`Arial`이 남으면 `set_font` 누락 또는 폰트 미지원 기호(✗ 등) 때문이다.

## 3. 슬라이드·도형·텍스트 헬퍼
```python
def new_deck():
    prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(H); return prs

def slide(prs, bg=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])    # 빈 레이아웃
    rect(s, 0, 0, W, H, fill=(bg or T['BG']))         # 풀블리드 배경
    return s

def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, radius=False):
    shp = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.shadow.inherit = False
    if fill is None: shp.fill.background()
    else: shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb = line; shp.line.width = Pt(lw)
    return shp

def text(s, x, y, w, h, content, size=18, bold=False, color=None, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, leading=1.12, wrap=True):
    """content = 문자열 또는 [(텍스트, {override}), ...] 런 리스트"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap; tf.vertical_anchor = anchor
    for m in (tf.margin_left, ): pass
    tf.margin_left = tf.margin_right = Pt(0); tf.margin_top = tf.margin_bottom = Pt(0)
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = leading
    items = [(content, {})] if isinstance(content, str) else content
    for txt, ov in items:
        r = p.add_run(); r.text = txt
        set_font(r, size=ov.get('size', size), bold=ov.get('bold', bold),
                 color=ov.get('color', color or T['INK']))
    return tb

def bullets(s, x, y, w, h, items, size=18, color=None, gap=10, leading=1.15, mark='•'):
    """items = ['텍스트', (1,'하위 레벨 텍스트'), ...] — 정수는 들여쓰기 레벨"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        lvl, txt = it if isinstance(it, tuple) else (0, it)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl; p.space_after = Pt(gap); p.line_spacing = leading
        pre = ('   ' * lvl) + (f'{mark} ' if mark else '')
        r = p.add_run(); r.text = pre + txt
        set_font(r, size=size - lvl, color=(color or T['INK']))
    return tb

def hline(s, x, y, w, color=None, weight=1.5):
    rect(s, x, y, w, weight/72.0, fill=(color or T['LINE']))

def hyperlink(run, url):
    run.hyperlink.address = url        # soffice PDF 변환 후에도 유지 (fitz get_links로 검증)
```

## 4. 복합 컴포넌트 (KPI·풋터·표지·섹션·출처)
```python
def kpi(s, x, y, w, h, value, label, accent=None):
    rect(s, x, y, w, h, fill=T['PANEL'], line=T['LINE'], radius=True)
    text(s, x+0.25, y+0.22, w-0.5, 0.9, value, size=33, bold=True,
         color=(accent or T['BLUE']), anchor=MSO_ANCHOR.MIDDLE)
    text(s, x+0.25, y+h-0.62, w-0.5, 0.45, label, size=12.5, color=T['INK2'])

def footer(s, idx, total, source=None):
    hline(s, MX, H-0.55, CW, color=T['LINE'], weight=1)
    if source: text(s, MX, H-0.48, CW-1.2, 0.35, source, size=9, color=T['INK3'])
    text(s, W-MX-1.0, H-0.48, 1.0, 0.35, f'{idx} / {total}', size=10,
         color=T['INK3'], align=PP_ALIGN.RIGHT)

def title_slide(prs, title, subtitle, tag=None):
    s = slide(prs); rect(s, 0, H-1.5, W, 1.5, fill=T['PANEL'])
    rect(s, MX, 2.5, 0.16, 1.6, fill=T['BRAND'])         # 좌측 액센트 바
    if tag: text(s, MX+0.4, 2.35, CW, 0.5, tag, size=14, bold=True, color=T['BRAND'])
    text(s, MX+0.4, 2.8, CW, 1.4, title, size=40, bold=True, color=T['INK'])
    text(s, MX+0.4, 4.25, CW, 1.0, subtitle, size=18, color=T['INK2'], leading=1.3)
    return s

def section_slide(prs, num, title):
    s = slide(prs, bg=T['INK'])                          # 짙은 배경의 구분 슬라이드
    text(s, MX, 3.0, 2.0, 1.2, f'{num:02d}', size=54, bold=True, color=T['BRAND'])
    text(s, MX+1.7, 3.15, CW-1.7, 1.2, title, size=32, bold=True, color=C(0xFFFFFF))
    return s

def header(s, title, kicker=None):
    if kicker: text(s, MX, 0.5, CW, 0.4, kicker, size=13, bold=True, color=T['BRAND'])
    text(s, MX, 0.85, CW, 0.8, title, size=26, bold=True, color=T['INK'])
    hline(s, MX, 1.62, CW, color=T['LINE'], weight=1.5)

def references_slide(prs, idx, total, refs):
    """refs = [(제목, url), ...]"""
    s = slide(prs); header(s, '출처 (References)')
    y = 1.9
    for i, (t, u) in enumerate(refs, 1):
        text(s, MX, y, CW, 0.4, f'{i}. {t}', size=13, color=T['INK'])
        r = text(s, MX, y+0.32, CW, 0.35, [(u, {'size':11, 'color':T['BLUE']})]).text_frame.paragraphs[0].runs[0]
        hyperlink(r, u); y += 0.78
    footer(s, idx, total); return s
```

## 5. 빌드 패턴 (예시)
```python
prs = new_deck()
title_slide(prs, 'Azure AI 도입 전략', '제조 현장의 AI 전환 — 근거와 로드맵', tag='임원 보고 · 2026')

s = slide(prs); header(s, '왜 지금인가', kicker='시장 신호')
bullets(s, MX, 1.9, CW*0.58, 4.5, [
    '건설·제조 원가 압박 심화 — 생산성 혁신 시급',
    '경쟁사 AI 현장 적용 가속(배차·품질·안전)',
    (1, '리서치 출처의 구체 사례를 인용'),
], size=18)
kpi(s, MX+CW*0.62, 1.9, CW*0.18, 1.6, '-42%', '개발 리드타임')   # ASCII '-' (U+2212 '−'는 한글폰트에 없어 폴백)
kpi(s, MX+CW*0.81, 1.9, CW*0.18, 1.6, '+3.2%', '출하 효율')
footer(s, 2, 15, '출처: <기관/URL> · 수치는 예시(가정)')

# … 섹션·본문·비교표·아키텍처·타임라인·마무리 …
references_slide(prs, 15, 15, [('제목 A', 'https://learn.microsoft.com/...'), ('제목 B', 'https://...')])
prs.save('deck.pptx')
```

## 6. 규칙
- **폰트**: 모든 런은 `set_font`로 latin+ea+cs 지정. 본문 16~20pt, 소제목 22~26pt, 표지 36~44pt, 캡션/풋터 9~12pt.
- **색·대비**: 테마 토큰만 사용. 라이트=짙은 잉크/밝은 배경, 다크=반대. 포인트 컬러(BRAND)는 강조에만.
- **여백·정렬**: 좌우 `MX=0.7"`, 콘텐츠 폭 `CW`. 요소는 그리드에 정렬, 슬라이드당 1메시지·6불릿 이내.
- **도식**: KPI·박스·화살표는 도형으로. 복잡한 다이어그램은 `rect`+`text`+`hline`/커넥터 조합.
- **출처**: 변동·인용 수치는 풋터 또는 출처 슬라이드에 URL. 추정치는 "가정/추정" 명시.
