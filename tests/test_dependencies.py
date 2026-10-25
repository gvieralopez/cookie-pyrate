import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from conftest import ProjectGenerator

ENV_TEST_PROBE = """import os


def test_env_test_is_loaded() -> None:
    assert os.environ["COOKIE_PYRATE_VERSION"] == "1.2.3"
"""


@pytest.mark.parametrize("group", ["dev", "docs"])
def test_every_tool_has_a_version_floor(default_project: Path, group: str) -> None:
    pyproject = tomllib.loads((default_project / "pyproject.toml").read_text())
    requirements = pyproject["dependency-groups"][group]
    assert requirements
    assert [requirement for requirement in requirements if ">=" not in requirement] == []


def test_env_test_overrides_the_shell(project_generator: ProjectGenerator) -> None:
    with project_generator({}) as project_dir:
        (project_dir / "tests" / "test_env_probe.py").write_text(ENV_TEST_PROBE)
        result = subprocess.run(
            [shutil.which("uv") or "uv", "run", "pytest", "tests/test_env_probe.py", "--no-cov"],
            cwd=project_dir,
            env={**os.environ, "COOKIE_PYRATE_VERSION": "from-the-shell"},
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
