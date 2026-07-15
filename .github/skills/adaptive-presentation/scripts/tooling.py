#!/usr/bin/env python3
"""Shared dependency resolvers for adaptive-presentation scripts."""

from __future__ import annotations

import shutil
from pathlib import Path


SOFFICE_CANDIDATES = (
    "/opt/homebrew/bin/soffice",
    "/usr/local/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
)


def resolve_soffice(explicit: Path | None = None) -> str | None:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return str(path)

    from_path = shutil.which("soffice") or shutil.which("libreoffice")
    if from_path:
        return str(Path(from_path).resolve())

    for candidate in SOFFICE_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None


def paths_collide(first: Path, second: Path) -> bool:
    first_resolved = first.expanduser().resolve()
    second_resolved = second.expanduser().resolve()
    if str(first_resolved).casefold() == str(second_resolved).casefold():
        return True
    try:
        return first_resolved.exists() and second_resolved.exists() and first_resolved.samefile(second_resolved)
    except OSError:
        return False


def path_is_within(child: Path, parent: Path) -> bool:
    child_resolved = child.expanduser().resolve()
    parent_resolved = parent.expanduser().resolve()
    child_parts = tuple(part.casefold() for part in child_resolved.parts)
    parent_parts = tuple(part.casefold() for part in parent_resolved.parts)
    if child_parts[: len(parent_parts)] == parent_parts:
        return True
    if not parent_resolved.exists():
        return False
    current = child_resolved
    while current != current.parent:
        try:
            if current.exists() and current.samefile(parent_resolved):
                return True
        except OSError:
            pass
        current = current.parent
    return False
