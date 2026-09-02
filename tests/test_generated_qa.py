import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import ProjectGenerator

REMOTE_SCRIPT = Path("scripts") / "create_remote.py"
QA_STAGES = ("Running Ruff Linter", "Running Ruff Format", "Running Mypy")
NEEDS_MAKE = pytest.mark.skipif(shutil.which("make") is None, reason="make is missing")


@NEEDS_MAKE
def test_generated_project_passes_its_own_qa(default_project: Path) -> None:
    _assert_qa_passes(default_project)


@NEEDS_MAKE
def test_github_project_passes_its_own_qa(project_generator: ProjectGenerator) -> None:
    with project_generator({"git_provider": "GitHub"}) as project_dir:
        assert (project_dir / REMOTE_SCRIPT).is_file()

        _assert_qa_passes(project_dir)


def _assert_qa_passes(project_dir: Path) -> None:
    result = subprocess.run(
        [shutil.which("make") or "make", "qa"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    # A target dropped from `qa` would still exit 0, so check each one reports for itself.
    for stage in QA_STAGES:
        assert stage in output, output
