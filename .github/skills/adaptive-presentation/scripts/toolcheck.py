#!/usr/bin/env python3
"""Probe and cache the presentation toolchain, then reuse its stable inventory.

soffice(LibreOffice), PyMuPDF(fitz), Pillow, python-pptx, 그리고 한글 폰트를 한 번 탐지해
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/{toolchain.json,fonts.txt}에
캐시한다. 캐시 hit에서도 실행 환경과 필수 도구는 빠르게 재확인하고, 비용이 큰 폰트 목록 탐색만
건너뛴다(--refresh로 강제 갱신).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from tooling import resolve_soffice

FONT_PATTERNS = r"Apple SD Gothic|Noto Sans CJK KR|Noto Sans KR|Malgun|AppleGothic|Nanum(Gothic|Myeongjo)|Source Han Sans K|Pretendard|Spoqa"
CACHE_VERSION = 2
MODULES = ("fitz", "PIL", "pptx")


def cache_dir(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser()
    base = os.environ.get("COPILOT_CACHE_DIR") or str(Path.home() / ".copilot" / "cache")
    return Path(base) / "adaptive-presentation"


def runtime_signature() -> dict:
    info = {
        "cache_version": CACHE_VERSION,
        "python": sys.version.split()[0],
        "python_executable": str(Path(sys.executable).resolve()),
        "path_env": os.environ.get("PATH", ""),
        "soffice": resolve_soffice(),
    }
    for mod in MODULES:
        try:
            __import__(mod)
            info[f"has_{mod}"] = True
        except Exception:
            info[f"has_{mod}"] = False
    return info


def probe() -> dict:
    info = runtime_signature()
    info["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    fonts: list[str] = []
    fc = shutil.which("fc-list")
    if fc:
        try:
            out = subprocess.run([fc], capture_output=True, text=True, timeout=25).stdout
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


def read_cache(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def cache_matches_runtime(info: dict) -> bool:
    return all(
        info.get(key) == value
        for key, value in runtime_signature().items()
    )


def missing_required(info: dict, require_korean_font: bool = False) -> list[str]:
    checks = {
        "soffice": bool(info.get("soffice")),
        "PyMuPDF (fitz)": bool(info.get("has_fitz")),
        "Pillow (PIL)": bool(info.get("has_PIL")),
        "python-pptx": bool(info.get("has_pptx")),
    }
    missing = [name for name, available in checks.items() if not available]
    if require_korean_font and not info.get("korean_fonts"):
        missing.append("Korean font")
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe/cache soffice, PyMuPDF, Pillow, python-pptx, Korean fonts.")
    ap.add_argument("--refresh", action="store_true", help="ignore cache and re-probe")
    ap.add_argument("--max-age-days", type=float, default=7.0)
    ap.add_argument("--cache-dir", help="override cache directory")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="nonzero exit if soffice, PyMuPDF, Pillow, or python-pptx is missing",
    )
    ap.add_argument(
        "--require-korean-font",
        action="store_true",
        help="with --strict, also fail when no Korean-capable font is found",
    )
    a = ap.parse_args()
    if not math.isfinite(a.max_age_days) or a.max_age_days < 0:
        ap.error("--max-age-days must be a finite non-negative number")

    cdir = cache_dir(a.cache_dir)
    cdir.mkdir(parents=True, exist_ok=True)
    tj, ft = cdir / "toolchain.json", cdir / "fonts.txt"

    cached = read_cache(tj) if not a.refresh and is_fresh(tj, a.max_age_days) else None
    if cached is not None and cache_matches_runtime(cached):
        info = cached
        if not ft.is_file():
            ft.write_text(
                "\n".join(info.get("korean_fonts", [])), encoding="utf-8"
            )
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

    missing = missing_required(info, a.require_korean_font)
    if missing:
        print(f"  missing required: {', '.join(missing)}")
    return 1 if (a.strict and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
