from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent
sys.path.insert(0, str(TESTS_DIR))

from test_deck_spec import BASE, LEDGER  # noqa: E402


LAZY_IMPORT_PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
import deck_spec
web_search = str(deck_spec.WEB_SEARCH_SCRIPTS)
before = ["validate_fact_ledger" in sys.modules, web_search in sys.path]
validator = deck_spec.fact_ledger_validator
after = ["validate_fact_ledger" in sys.modules, sys.path.count(web_search)]
print(json.dumps([before, after, validator is deck_spec.fact_ledger_validator]))
"""


def run_python(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-B", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


class StandaloneSkillTests(unittest.TestCase):
    """The skill folder must work when it is installed without web-search."""

    @classmethod
    def setUpClass(cls):
        root = TESTS_DIR / ".test-work"
        root.mkdir(exist_ok=True)
        work = tempfile.TemporaryDirectory(dir=root)
        cls.addClassCleanup(work.cleanup)
        cls.work_dir = Path(work.name)
        cls.skill = cls.work_dir / SKILL_ROOT.name
        shutil.copytree(
            SKILL_ROOT,
            cls.skill,
            ignore=shutil.ignore_patterns("tests", "__pycache__"),
        )

    def setUp(self):
        self.case_dir = self.work_dir / self._testMethodName
        self.case_dir.mkdir()

    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return run_python([str(self.skill / "scripts" / script), *args], self.skill)

    def write_json(self, name: str, value: dict) -> Path:
        path = self.case_dir / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_help_runs_without_the_web_search_skill(self):
        self.assertFalse((self.work_dir / "web-search").exists())
        for script in ("deck_spec.py", "verify_deck.py"):
            with self.subTest(script=script):
                result = self.run_script(script, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_spec_without_fact_ledger_validates_without_the_web_search_skill(self):
        spec = copy.deepcopy(BASE)
        spec["factLedger"] = None
        spec["slides"][1]["claimIds"] = []
        result = self.run_script("deck_spec.py", str(self.write_json("spec.json", spec)))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Deck spec PASS", result.stdout)

    def test_fact_ledger_spec_asks_to_install_the_web_search_skill(self):
        self.write_json("fact-ledger.json", LEDGER)
        spec = self.write_json("spec.json", copy.deepcopy(BASE))
        result = self.run_script("deck_spec.py", str(spec))
        self.assertEqual(result.returncode, 2)
        self.assertIn("`web-search` 스킬", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_verify_deck_reports_the_missing_web_search_skill_without_a_traceback(self):
        self.write_json("fact-ledger.json", LEDGER)
        spec = self.write_json("spec.json", copy.deepcopy(BASE))
        result = self.run_script(
            "verify_deck.py",
            str(self.case_dir / "deck.pptx"),
            "--out", str(self.case_dir / "qa"),
            "--deck-spec", str(spec),
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("`web-search` 스킬", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class LazySiblingImportTests(unittest.TestCase):
    def test_importing_deck_spec_leaves_validator_and_sys_path_untouched(self):
        result = run_python(
            ["-c", LAZY_IMPORT_PROBE, str(SKILL_ROOT / "scripts")],
            SKILL_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [[False, False], [True, 1], True])


if __name__ == "__main__":
    unittest.main()
