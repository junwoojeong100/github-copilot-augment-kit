"""Revision-bound reuse of complete verifier renders, never of QA decisions."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import locale
import math
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24.3; the legacy `fitz` module name is deprecated
except ImportError:
    import fitz
import PIL

import render_pptx
import tooling


CACHE_NAME = "render-cache.json"
CACHE_VERSION = 1
RENDER_OPTIONS = (
    "slides", "scale", "per_sheet", "columns", "thumb_width", "thumb_height",
    "image_format", "quality", "max_image_kb", "keep_slide_images", "keep_pdf",
)


def _digest(value: object) -> str:
    content = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _run_probe(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=25,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"Render environment probe failed: {command[0]}") from error
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            f"Render environment probe failed: {command[0]} "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _resource_files(roots: list[Path]) -> set[Path]:
    files: set[Path] = set()
    visited: set[Path] = set()

    def fail(error: OSError) -> None:
        raise error

    for root in roots:
        try:
            root.stat()
        except FileNotFoundError:
            continue
        if root.is_file():
            files.add(root.resolve())
            continue
        for directory, children, names in os.walk(
            root, followlinks=True, onerror=fail,
        ):
            resolved = Path(directory).resolve()
            if resolved in visited:
                children[:] = []
                continue
            visited.add(resolved)
            for name in names:
                path = resolved / name
                if path.is_file():
                    files.add(path.resolve())
    return files


def _native_font_inventory() -> tuple[set[Path], list[str]]:
    files: set[Path] = set()
    state: list[str] = []
    if sys.platform == "darwin":
        base = "/System/Library/Frameworks"
        text = ctypes.CDLL(f"{base}/CoreText.framework/CoreText")
        foundation = ctypes.CDLL(f"{base}/CoreFoundation.framework/CoreFoundation")
        foundation.CFArrayGetCount.argtypes = [ctypes.c_void_p]
        foundation.CFArrayGetCount.restype = ctypes.c_long
        foundation.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
        foundation.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
        foundation.CFRelease.argtypes = [ctypes.c_void_p]
        foundation.CFRelease.restype = None
        foundation.CFURLGetFileSystemRepresentation.argtypes = [
            ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p, ctypes.c_long,
        ]
        foundation.CFURLGetFileSystemRepresentation.restype = ctypes.c_bool
        foundation.CFStringGetCString.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_uint32,
        ]
        foundation.CFStringGetCString.restype = ctypes.c_bool
        for name, urls in (
            ("CTFontManagerCopyAvailableFontURLs", True),
            ("CTFontManagerCopyAvailablePostScriptNames", False),
        ):
            function = getattr(text, name)
            function.argtypes = []
            function.restype = ctypes.c_void_p
            array = function()
            if not array:
                raise RuntimeError("CoreText font inventory is unavailable")
            try:
                buffer = ctypes.create_string_buffer(32768)
                for index in range(foundation.CFArrayGetCount(array)):
                    item = foundation.CFArrayGetValueAtIndex(array, index)
                    if urls:
                        success = foundation.CFURLGetFileSystemRepresentation(
                            item, True, buffer, len(buffer),
                        )
                    else:
                        success = foundation.CFStringGetCString(
                            item, buffer, len(buffer), 0x08000100,
                        )
                    if not success:
                        raise RuntimeError("Cannot decode CoreText font inventory")
                    value = os.fsdecode(buffer.value)
                    if urls:
                        files.add(Path(value).resolve())
                    else:
                        state.append(value)
            finally:
                foundation.CFRelease(array)
    elif sys.platform == "win32":
        import winreg

        for hive_name, hive in (
            ("HKLM", winreg.HKEY_LOCAL_MACHINE), ("HKCU", winreg.HKEY_CURRENT_USER),
        ):
            for suffix in ("Fonts", "FontSubstitutes", r"FontLink\SystemLink"):
                key_path = rf"SOFTWARE\Microsoft\Windows NT\CurrentVersion\{suffix}"
                try:
                    key = winreg.OpenKey(hive, key_path)
                except FileNotFoundError:
                    continue
                with key:
                    for index in range(winreg.QueryInfoKey(key)[1]):
                        name, value, kind = winreg.EnumValue(key, index)
                        state.append(json.dumps([hive_name, suffix, name, kind, repr(value)]))
                        if suffix == "Fonts" and isinstance(value, str):
                            path = Path(os.path.expandvars(value))
                            candidates = (
                                [path] if path.is_absolute()
                                else [root / path for root in tooling.font_directories()]
                            )
                            files.update(candidate.resolve() for candidate in candidates if candidate.is_file())
    return files, sorted(state)


def environment_fingerprint(soffice: str) -> str:
    executable = Path(soffice).resolve()
    installation = executable.parent.parent
    font_files, native_state = _native_font_inventory()
    font_roots = [
        installation / "share" / "fonts",
        installation / "Resources" / "fonts",
    ]
    if not font_files:
        font_roots.extend(tooling.font_directories())
    font_files.update(_resource_files(font_roots))
    fc_list = shutil.which("fc-list")
    if fc_list:
        listed = _run_probe([fc_list, "--format", "%{file}\n"])
        for name in listed.splitlines():
            path = Path(name).expanduser().resolve()
            if not path.is_file():
                raise RuntimeError(f"Font inventory contains an unavailable file: {path}")
            font_files.add(path)
    if not font_files:
        raise RuntimeError(
            "Cannot fingerprint installed fonts. Run without --reuse-render."
        )

    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_roots = [
        Path("/etc/fonts"), config_home / "fontconfig",
        Path.home() / ".fonts.conf", Path.home() / ".fonts.conf.d",
        installation / "share" / "registry",
        installation / "Resources" / "registry",
    ]
    for name in ("FONTCONFIG_FILE", "FONTCONFIG_PATH"):
        if os.environ.get(name):
            for value in os.environ[name].split(os.pathsep):
                path = Path(value).expanduser()
                if not path.is_absolute() or not path.exists():
                    raise RuntimeError(
                        f"Cannot fingerprint {name}; use existing absolute paths "
                        "or run without --reuse-render."
                    )
                config_roots.append(path)
    resources = font_files | _resource_files(config_roots) | {
        executable, Path(__file__).resolve(), Path(render_pptx.__file__).resolve(),
        Path(tooling.__file__).resolve(),
    }
    if fc_list:
        resources.add(Path(fc_list).resolve())
    environment = {
        name: value for name, value in os.environ.items()
        if name.startswith(("LC_", "FONTCONFIG_", "SAL_", "OOO_", "XDG_", "LD_", "DYLD_"))
        or name in {
            "LANG", "LANGUAGE", "TZ", "PATH", "HOME", "USERPROFILE", "APPDATA",
            "LOCALAPPDATA", "WINDIR", "PYTHONHOME", "PYTHONPATH",
        }
    }
    return _digest({
        "platform": platform.platform(),
        "python": sys.version,
        "python_executable": str(Path(sys.executable).resolve()),
        "locale": locale.getlocale(),
        "libreoffice": _run_probe([soffice, "--version"]),
        "pymupdf": [fitz.VersionBind, fitz.VersionFitz],
        "pillow": PIL.__version__,
        "native_fonts": native_state,
        "environment": environment,
        "resources": [
            [str(path), render_pptx.sha256_file(path)]
            for path in sorted(resources)
        ],
    })


def signature(args: argparse.Namespace) -> dict[str, str]:
    deck = args.deck.expanduser().resolve()
    return {
        "deck": _digest([str(deck), render_pptx.sha256_file(deck)]),
        "environment": environment_fingerprint(render_pptx.find_soffice(args.soffice)),
        "options": _digest({name: getattr(args, name) for name in RENDER_OPTIONS}),
    }


def _owned_root(args: argparse.Namespace) -> Path:
    root = args.out.expanduser()
    if root.is_symlink() or not render_pptx.output_dir_is_owned(root):
        raise RuntimeError(f"Render cache requires an owned, non-symlinked QA directory: {root}")
    return root.resolve()


def _checked_file(path: Path, root: Path) -> Path:
    if path.is_symlink() or path.parent.resolve() != root:
        raise RuntimeError(f"Render cache artifact must stay inside its QA directory: {path}")
    if not path.is_file() or path.stat().st_nlink != 1:
        raise RuntimeError(f"Render cache artifact is missing or linked: {path}")
    return path


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Invalid render cache file: {path}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"Render cache file must contain an object: {path}")
    return value


def _artifacts(args: argparse.Namespace, manifest: dict, root: Path) -> list[Path]:
    deck = args.deck.expanduser().resolve()
    count = manifest.get("total_slides")
    if (
        type(count) is not int or count <= 0
        or manifest.get("rendered_slides") != list(range(1, count + 1))
        or not all(type(number) is int for number in manifest["rendered_slides"])
        or manifest.get("deck") != str(deck)
        or manifest.get("deck_sha256") != render_pptx.sha256_file(deck)
        or manifest.get("pdf") != str(root / f"{deck.stem}.pdf")
        or not manifest.get("kept_pdf")
    ):
        raise RuntimeError("Render cache is not a complete render of the current PPTX")
    sheets = manifest.get("contact_sheets")
    images = manifest.get("slide_images")
    if (
        not isinstance(sheets, list) or len(sheets) != math.ceil(count / args.per_sheet)
        or not isinstance(images, list)
        or len(images) != (count if args.keep_slide_images else 0)
    ):
        raise RuntimeError("Render cache has incomplete preview coverage")
    previews = sheets + images
    if not all(isinstance(path, str) for path in previews):
        raise RuntimeError("Render cache preview paths must be strings")
    if len(set(previews)) != len(previews):
        raise RuntimeError("Render cache has duplicated previews")
    for name in previews:
        path = Path(name)
        if (
            not path.is_absolute() or path.suffix != f".{args.image_format}"
            or not path.name.startswith(("contact-", "slide-"))
        ):
            raise RuntimeError(f"Invalid render cache preview path: {name}")
    paths = [_checked_file(root / f"{deck.stem}.pdf", root)]
    paths.extend(_checked_file(Path(name), root) for name in previews)
    render_pptx.validate_reusable_pdf(deck, paths[0], manifest["deck_sha256"])
    return paths


def load(
    args: argparse.Namespace, current: dict[str, str],
) -> tuple[dict | None, str]:
    cache_path = args.out.expanduser() / CACHE_NAME
    if not cache_path.exists() and not cache_path.is_symlink():
        return None, "no recorded render"
    root = _owned_root(args)
    metadata = _read_json(_checked_file(root / CACHE_NAME, root))
    previous = metadata.get("signature")
    if (
        type(metadata.get("schemaVersion")) is not int
        or metadata["schemaVersion"] != CACHE_VERSION
        or not isinstance(previous, dict) or set(previous) != set(current)
        or not all(
            isinstance(value, str) and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            for value in previous.values()
        )
    ):
        raise RuntimeError("Invalid render cache signature; run without --reuse-render")
    changed = [name for name in current if previous[name] != current[name]]
    if changed:
        return None, f"changed {', '.join(changed)}"
    manifest_path = _checked_file(root / "manifest.json", root)
    if metadata.get("manifestSha256") != render_pptx.sha256_file(manifest_path):
        raise RuntimeError("Render manifest changed; run without --reuse-render")
    manifest = _read_json(manifest_path)
    paths = _artifacts(args, manifest, root)
    hashes = metadata.get("artifacts")
    if not isinstance(hashes, dict) or set(hashes) != {path.name for path in paths}:
        raise RuntimeError("Render cache artifact inventory is incomplete")
    for path in paths:
        if hashes[path.name] != render_pptx.sha256_file(path):
            raise RuntimeError(f"Render cache artifact changed: {path}")
    return manifest, "matching input, environment, options, and artifacts"


def store(args: argparse.Namespace, current: dict[str, str], manifest: dict) -> None:
    root = _owned_root(args)
    paths = _artifacts(args, manifest, root)
    manifest_path = _checked_file(root / "manifest.json", root)
    if _read_json(manifest_path) != manifest:
        raise RuntimeError("Render manifest changed before cache recording")
    metadata = {
        "schemaVersion": CACHE_VERSION,
        "signature": current,
        "manifestSha256": render_pptx.sha256_file(manifest_path),
        "artifacts": {path.name: render_pptx.sha256_file(path) for path in paths},
    }
    tooling.write_json_atomic(root / CACHE_NAME, metadata)
