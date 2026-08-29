import tomllib
from pathlib import Path


def test_pyproject_with_precommit(default_project: Path) -> None:
    pyproject = default_project / "pyproject.toml"
    pyproject_content = tomllib.loads(pyproject.read_text())

    assert "pre-commit" in pyproject_content["dependency-groups"]["dev"]


def test_precommit_config_with_precommit(default_project: Path) -> None:
    assert (default_project / ".pre-commit-config.yaml").exists()


def test_precommit_config_without_precommit(project_generator) -> None:
    with project_generator({"with_precommit": False}) as project_dir:
        assert not (project_dir / ".pre-commit-config.yaml").exists()


def test_readme_with_precommit(default_project: Path) -> None:
    development = default_project / "DEVELOPMENT.md"
    development_content = development.read_text()
    assert "## Pre-Commit Hooks" in development_content


def test_development_without_precommit(project_generator) -> None:
    with project_generator({"with_precommit": False}) as project_dir:
        development = project_dir / "DEVELOPMENT.md"
        development_content = development.read_text()
        assert "## Pre-Commit Hooks" not in development_content
