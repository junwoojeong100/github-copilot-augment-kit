from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
BASE = SKILL_ROOT / "examples" / "precision-manufacturing.example.json"


def run_lint(spec_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "lint_spec.py"), str(spec_path)],
        capture_output=True,
        text=True,
    )


def write_temp(spec: dict, directory: str) -> Path:
    path = Path(directory) / "spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class LintSpecTests(unittest.TestCase):
    def test_base_example_passes(self):
        result = run_lint(BASE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_qa_invariant_violations_are_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["operations"]["action"]["durationMs"] = 3000
        spec["agents"]["orchestration"]["summary"] = "자율 대응을 완료했습니다."
        spec["governance"]["cards"][0]["value"] = str(spec["governance"]["evaluation"]["finalScore"])
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("durationMs", result.stdout)
        self.assertIn("의사결정 패키지", result.stdout)
        self.assertIn("finalScore", result.stdout)

    def test_structural_error_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["navigation"] = spec["navigation"][:7]  # break the fixed 8-route contract
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("STRUCTURE", result.stdout)


if __name__ == "__main__":
    unittest.main()
