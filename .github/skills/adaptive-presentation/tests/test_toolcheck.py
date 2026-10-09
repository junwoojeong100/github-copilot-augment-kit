from __future__ import annotations

import contextlib
import io
import os
import shlex
import shutil
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import toolcheck  # noqa: E402
import tooling  # noqa: E402


class ToolcheckTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent / ".test-work"
        self.work_dir = root / self._testMethodName
        shutil.rmtree(self.work_dir, ignore_errors=True)
        self.work_dir.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.work_dir, True)

    def test_invalid_cache_is_ignored(self):
        cache = self.work_dir / "cache.json"
        cache.write_text("{broken", encoding="utf-8")
        self.assertIsNone(toolcheck.read_cache(cache))

    def test_strict_requirements_include_pillow(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": False,
            "has_pptx": True,
        }
        self.assertEqual(toolcheck.missing_required(info), ["Pillow (PIL)"])

    def test_korean_font_can_be_required(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": True,
            "has_pptx": True,
            "korean_fonts": [],
        }
        self.assertEqual(
            toolcheck.missing_required(info, require_korean_font=True),
            ["Korean font"],
        )

    def test_cache_is_bound_to_current_runtime(self):
        info = toolcheck.runtime_signature()
        self.assertTrue(toolcheck.cache_matches_runtime(info))
        changed = dict(info, python_executable="/different/python")
        self.assertFalse(toolcheck.cache_matches_runtime(changed))

    def test_pymupdf_is_detected_under_either_import_name(self):
        real_import = __import__

        def only(*available: str):
            def fake_import(name, *args, **kwargs):
                if name in ("pymupdf", "fitz"):
                    if name in available:
                        return types.ModuleType(name)
                    raise ImportError(name)
                return real_import(name, *args, **kwargs)
            return fake_import

        for available, expected in (
            (("pymupdf",), True), (("fitz",), True), ((), False),
        ):
            with self.subTest(available=available):
                with patch("builtins.__import__", only(*available)):
                    info = toolcheck.runtime_signature()
                self.assertIs(info["has_fitz"], expected)

    def test_path_containment_is_case_normalized(self):
        self.assertTrue(
            tooling.path_is_within(
                Path("/users/example/QA/deck.pptx"),
                Path("/Users/Example/qa"),
            )
        )

    def test_language_aware_font_resolution_is_deterministic(self):
        available = [
            "Arial",
            "Noto Sans KR",
            "Apple SD Gothic Neo",
            "Liberation Sans",
        ]
        self.assertEqual(
            toolcheck.select_font(available, language="ko-KR"),
            "Apple SD Gothic Neo",
        )
        self.assertEqual(
            toolcheck.select_font(reversed(available), language="ko-KR"),
            "Apple SD Gothic Neo",
        )
        self.assertEqual(
            toolcheck.select_font(available, language="en-US"),
            "Arial",
        )
        self.assertEqual(
            toolcheck.select_font(
                available,
                preferred=["Missing Font"],
                fallbacks=["liberation sans"],
                language="ko",
            ),
            "Liberation Sans",
        )

    def test_font_probe_surfaces_timeout_warning(self):
        with (
            patch.object(toolcheck.shutil, "which", return_value="/usr/bin/fc-list"),
            patch.object(
                toolcheck.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired("fc-list", 25),
            ),
            patch.object(toolcheck, "_font_directories", return_value=[]),
        ):
            info = toolcheck.enumerate_fonts()

        self.assertEqual(info["fonts"], [])
        self.assertTrue(
            any("fc-list probe failed" in warning for warning in info["warnings"])
        )

    def test_windows_font_directories_and_common_filenames(self):
        with (
            patch.object(toolcheck.sys, "platform", "win32"),
            patch.dict(
                os.environ,
                {
                    "WINDIR": r"C:\Windows",
                    "LOCALAPPDATA": r"C:\Users\Example\AppData\Local",
                },
                clear=False,
            ),
        ):
            directories = toolcheck._font_directories()

        self.assertIn(Path(r"C:\Windows") / "Fonts", directories)
        self.assertEqual(
            toolcheck._font_family_from_filename(Path("malgunbd.ttf")),
            "Malgun Gothic",
        )
        self.assertEqual(
            toolcheck._font_family_from_filename(Path("NotoSansKR-Regular.otf")),
            "Noto Sans KR",
        )

    def test_windows_registry_fonts_are_included(self):
        with (
            patch.object(toolcheck.shutil, "which", return_value=None),
            patch.object(toolcheck, "_font_directories", return_value=[]),
            patch.object(
                toolcheck,
                "_font_names_from_windows_registry",
                return_value=({"Segoe UI", "Aptos"}, []),
            ),
        ):
            info = toolcheck.enumerate_fonts()

        self.assertEqual(info["fonts"], ["Aptos", "Segoe UI"])
        self.assertIn("Windows font registry", info["sources"])

    def tool_info(self, **overrides) -> dict:
        info = {
            "soffice": "/usr/bin/soffice",
            "has_fitz": True,
            "has_PIL": True,
            "has_pptx": True,
            "font_names": ["Apple SD Gothic Neo"],
            "korean_fonts": ["Apple SD Gothic Neo"],
            "selected_fonts": {"ko": "Apple SD Gothic Neo", "latin": "Arial"},
            "probe_warnings": [],
        }
        info.update(overrides)
        return info

    def run_main(self, info: dict, *args: str) -> tuple[int, list[str]]:
        argv = [
            "toolcheck.py",
            "--refresh",
            "--cache-dir",
            str(self.work_dir / "cache"),
            *args,
        ]
        output = io.StringIO()
        with (
            patch.object(toolcheck, "probe", return_value=info),
            patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(output),
        ):
            code = toolcheck.main()
        return code, output.getvalue().splitlines()

    def test_install_hints_are_empty_when_nothing_is_missing(self):
        self.assertEqual(toolcheck.install_hints([]), [])

    def test_soffice_hint_uses_the_platform_package_manager(self):
        for platform, command in (
            ("darwin", "brew install --cask libreoffice"),
            ("win32", "winget install TheDocumentFoundation.LibreOffice"),
            ("linux", "sudo apt-get install libreoffice-impress"),
        ):
            with self.subTest(platform=platform):
                hints = toolcheck.install_hints(["soffice"], platform=platform)
                self.assertEqual(len(hints), 1)
                self.assertTrue(hints[0].endswith(command), hints[0])
        self.assertIn("Debian/Ubuntu", toolcheck.install_hints(["soffice"], "linux")[0])
        generic = toolcheck.install_hints(["soffice"], platform="freebsd14")
        self.assertEqual(len(generic), 1)
        self.assertIn("put soffice on PATH", generic[0])

    def test_platform_defaults_to_the_running_system(self):
        with patch.object(sys, "platform", "darwin"):
            hints = toolcheck.install_hints(["soffice"])
        self.assertTrue(hints[0].endswith("brew install --cask libreoffice"))

    def test_python_hint_installs_requirements_with_the_same_interpreter(self):
        hints = toolcheck.install_hints(
            ["python-pptx"],
            platform="linux",
            python="/venv/bin/python",
            requirements=Path("requirements.txt"),
        )
        self.assertEqual(len(hints), 2)
        self.assertTrue(
            hints[0].endswith("/venv/bin/python -m pip install -r requirements.txt"),
            hints[0],
        )
        self.assertIn("externally-managed-environment", hints[1])
        self.assertTrue(hints[1].endswith("python3 -m venv .venv"), hints[1])

    def test_python_hint_lists_only_missing_packages_without_requirements(self):
        hints = toolcheck.install_hints(
            ["Pillow (PIL)", "python-pptx"],
            platform="linux",
            python="/venv/bin/python",
        )
        self.assertTrue(
            hints[0].endswith("/venv/bin/python -m pip install python-pptx Pillow"),
            hints[0],
        )
        self.assertNotIn("PyMuPDF", hints[0])
        fitz_only = toolcheck.install_hints(["PyMuPDF (fitz)"], python="python3")
        self.assertTrue(fitz_only[0].endswith("python3 -m pip install PyMuPDF"))

    def test_python_hint_defaults_to_the_running_interpreter(self):
        hints = toolcheck.install_hints(["python-pptx"], platform="linux")
        self.assertIn(f"{shlex.quote(sys.executable)} -m pip install", hints[0])

    def test_hint_commands_quote_paths_with_spaces(self):
        requirements = Path("my dir") / "requirements.txt"
        posix = toolcheck.install_hints(
            ["python-pptx"],
            platform="darwin",
            python="/Users/Jane Doe/venv/bin/python",
            requirements=requirements,
        )
        self.assertTrue(
            posix[0].endswith(
                f"'/Users/Jane Doe/venv/bin/python' -m pip install -r '{requirements}'"
            ),
            posix[0],
        )
        windows = toolcheck.install_hints(
            ["python-pptx"],
            platform="win32",
            python=r"C:\Program Files\Python312\python.exe",
            requirements=requirements,
        )
        self.assertTrue(
            windows[0].endswith(
                r'"C:\Program Files\Python312\python.exe" -m pip install -r '
                f'"{requirements}"'
            ),
            windows[0],
        )
        plain = toolcheck.install_hints(
            ["python-pptx"], platform="win32", python=r"C:\Python312\python.exe"
        )
        self.assertTrue(
            plain[0].endswith(r"C:\Python312\python.exe -m pip install python-pptx")
        )

    def test_korean_font_hint_per_platform(self):
        for platform in ("darwin", "win32"):
            with self.subTest(platform=platform):
                hints = toolcheck.install_hints(["Korean font"], platform=platform)
                self.assertEqual(len(hints), 1)
                self.assertIn("font probe warnings", hints[0])
                self.assertNotIn("apt-get", hints[0])
        linux = toolcheck.install_hints(["Korean font"], platform="linux")
        self.assertEqual(len(linux), 1)
        self.assertTrue(linux[0].endswith("sudo apt-get install fonts-noto-cjk"))
        self.assertIn("--refresh", linux[0])
        other = toolcheck.install_hints(["Korean font"], platform="freebsd14")
        self.assertEqual(len(other), 1)
        self.assertIn("Noto Sans CJK KR", other[0])

    def test_every_missing_required_name_has_an_install_hint(self):
        names = toolcheck.missing_required({}, require_korean_font=True)
        hints = "\n".join(
            toolcheck.install_hints(names, platform="linux", python="python3")
        )
        for expected in (
            "libreoffice-impress",
            "python-pptx",
            "PyMuPDF",
            "Pillow",
            "fonts-noto-cjk",
        ):
            self.assertIn(expected, hints)

    def test_main_prints_hints_only_when_a_requirement_is_missing(self):
        requirements = self.work_dir / "requirements.txt"
        requirements.write_text("python-pptx\n", encoding="utf-8")
        with patch.object(toolcheck, "REQUIREMENTS_FILE", requirements):
            code, lines = self.run_main(self.tool_info(has_pptx=False), "--strict")
            self.assertEqual(code, 1)
            index = lines.index("  missing required: python-pptx")
            expected = [
                f"  hint: {hint}"
                for hint in toolcheck.install_hints(
                    ["python-pptx"], requirements=requirements
                )
            ]
            self.assertEqual(lines[index + 1 :], expected)
            self.assertIn("-m pip install -r", expected[0])
            self.assertIn(str(requirements), expected[0])

            code, lines = self.run_main(self.tool_info(), "--strict")
        self.assertEqual(code, 0)
        self.assertFalse(
            [line for line in lines if "hint:" in line or "missing required" in line]
        )

    def test_main_lists_missing_packages_when_requirements_file_is_absent(self):
        absent = self.work_dir / "absent-requirements.txt"
        with patch.object(toolcheck, "REQUIREMENTS_FILE", absent):
            code, lines = self.run_main(self.tool_info(has_fitz=False, has_PIL=False))
        self.assertEqual(code, 0)
        hint = next(line for line in lines if line.startswith("  hint: Python"))
        self.assertTrue(hint.endswith("-m pip install PyMuPDF Pillow"), hint)


if __name__ == "__main__":
    unittest.main()
