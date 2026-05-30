"""Generate expected_output.txt golden files for test fixtures (cross-platform)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
MAIN = PROJECT_ROOT / "main.py"


def _run_aicc(args: list[str]) -> None:
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    env.setdefault("TERM", "dumb")
    result = subprocess.run(
        [sys.executable, str(MAIN), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"main.py failed (exit {result.returncode}):\n{result.stderr}"
        )


def _write_golden_from_output(output_path: Path, golden_path: Path) -> None:
    lines = output_path.read_text(encoding="utf-8").splitlines()
    tree_idx = next(
        i for i, line in enumerate(lines) if line.strip().startswith("Project tree:")
    )
    legend_idx = tree_idx - 1 if tree_idx > 0 else tree_idx
    body: list[str] = [
        "This file is a concatenation of several source files from a project.",
        "",
    ]
    for line in lines[legend_idx:]:
        if line.strip().startswith("Project tree:"):
            body.append("Project tree: [NORMALIZED_PATH]")
        else:
            body.append(line)
    golden_path.write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")


def generate_basic_project_golden() -> Path:
    project_dir = TESTS_DIR / "test_projects" / "basic_project"
    temp_output = TESTS_DIR / ".golden_basic_output.txt"
    golden_path = project_dir / "expected_output.txt"
    _run_aicc(
        [
            "--project",
            str(project_dir),
            "--output",
            str(temp_output),
            "--no-timestamp",
            "--config",
            str(project_dir / "config.yaml"),
            "--format",
            "text",
            "--no-clipboard",
        ]
    )
    _write_golden_from_output(temp_output, golden_path)
    temp_output.unlink(missing_ok=True)
    return golden_path


def generate_strip_comments_golden() -> Path:
    project_dir = TESTS_DIR / "test_projects" / "strip_comments_project"
    temp_output = TESTS_DIR / ".golden_strip_output.txt"
    golden_path = project_dir / "expected_output.txt"
    _run_aicc(
        [
            "--project",
            str(project_dir),
            "--output",
            str(temp_output),
            "--no-timestamp",
            "--strip-comments",
            "--format",
            "text",
            "--no-clipboard",
        ]
    )
    _write_golden_from_output(temp_output, golden_path)
    temp_output.unlink(missing_ok=True)
    return golden_path


def main() -> int:
    basic = generate_basic_project_golden()
    strip = generate_strip_comments_golden()
    print(f"Generated: {basic}")
    print(f"Generated: {strip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
