#!/usr/bin/env python3
"""Probe and cache the presentation toolchain once, then reuse it.

soffice(LibreOffice), PyMuPDF(fitz), Pillow, python-pptx, 그리고 한글 폰트를 한 번 탐지해
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/{toolchain.json,fonts.txt}에
캐시한다. 같은 작업 안의 이후 빌드는 재탐색을 건너뛴다(--refresh로 강제 갱신).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

FONT_PATTERNS = r"Apple SD Gothic|Noto Sans CJK KR|Noto Sans KR|Malgun|AppleGothic|Nanum(Gothic|Myeongjo)|Source Han Sans K|Pretendard|Spoqa"


def cache_dir(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser()
    base = os.environ.get("COPILOT_CACHE_DIR") or str(Path.home() / ".copilot" / "cache")
    return Path(base) / "adaptive-presentation"


def probe() -> dict:
    info: dict = {
        "python": sys.version.split()[0],
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    info["soffice"] = shutil.which("soffice") or shutil.which("libreoffice")
    for mod in ("fitz", "PIL", "pptx"):
        try:
            __import__(mod)
            info[f"has_{mod}"] = True
        except Exception:
            info[f"has_{mod}"] = False

    fonts: list[str] = []
    fc = shutil.which("fc-list")
    if fc:
        try:
            out = subprocess.run([fc, ""], capture_output=True, text=True, timeout=25).stdout
            for line in out.splitlines():
                if re.search(FONT_PATTERNS, line, re.I):
                    name = line.split(":", 1)[1].split(",")[0].strip() if ":" in line else line.strip()
                    if name:
                        fonts.append(name)
        except Exception:
            pass
    if not fonts and Path("/System/Library/Fonts/AppleSDGothicNeo.ttc").exists():
        fonts.append("Apple SD Gothic Neo")
    info["korean_fonts"] = sorted(set(fonts))
    return info


def is_fresh(path: Path, max_age_days: float) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < max_age_days * 86400


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe/cache soffice, PyMuPDF, Pillow, python-pptx, Korean fonts.")
    ap.add_argument("--refresh", action="store_true", help="ignore cache and re-probe")
    ap.add_argument("--max-age-days", type=float, default=7.0)
    ap.add_argument("--cache-dir", help="override cache directory")
    ap.add_argument("--strict", action="store_true", help="nonzero exit if soffice/fitz/pptx missing")
    a = ap.parse_args()

    cdir = cache_dir(a.cache_dir)
    cdir.mkdir(parents=True, exist_ok=True)
    tj, ft = cdir / "toolchain.json", cdir / "fonts.txt"

    if not a.refresh and is_fresh(tj, a.max_age_days):
        info = json.loads(tj.read_text(encoding="utf-8"))
        hit = True
    else:
        info = probe()
        tj.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        ft.write_text("\n".join(info.get("korean_fonts", [])), encoding="utf-8")
        hit = False

    print(f"toolchain cache {'HIT' if hit else 'REFRESHED'}: {tj}")
    print(f"  soffice: {info.get('soffice') or 'MISSING'}")
    print(f"  PyMuPDF(fitz): {info.get('has_fitz')}  Pillow(PIL): {info.get('has_PIL')}  python-pptx: {info.get('has_pptx')}")
    print(f"  korean fonts: {', '.join(info.get('korean_fonts', [])) or 'NONE'}")

    missing = (not info.get("soffice")) or (not info.get("has_fitz")) or (not info.get("has_pptx"))
    return 1 if (a.strict and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
