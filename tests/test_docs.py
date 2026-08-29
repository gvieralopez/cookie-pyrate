import os
import re
import tomllib
from pathlib import Path


def test_pyproject_with_docs(default_project: Path) -> None:
    pyproject = default_project / "pyproject.toml"
    pyproject_content = tomllib.loads(pyproject.read_text())

    assert "docs" in pyproject_content["dependency-groups"]

    docs_deps = pyproject_content["dependency-groups"]["docs"]
    assert "mkdocs" in docs_deps
    assert "mkdocs-material" in docs_deps
    assert "pygments" in docs_deps


def test_docs_folder_with_docs(default_project: Path) -> None:
    assert (default_project / "docs").exists()
    assert (default_project / "docs" / "src" / "mkdocs.yml").exists()


def test_docs_target_with_docs(default_project: Path) -> None:
    makefile = default_project / "Makefile"
    makefile_content = makefile.read_text()

    # Docs target is present
    assert re.search(r"^docs:$", makefile_content, re.MULTILINE)

    # Docs target is included in .PHONY
    assert re.search(r"^.PHONY:.*docs.*$", makefile_content, re.MULTILINE)

    # Build target depends on docs
    assert re.search(r"^build:.*docs.*$", makefile_content, re.MULTILINE)


def test_readme_with_docs(default_project: Path) -> None:
    development = default_project / "DEVELOPMENT.md"
    development_content = development.read_text()
    assert "### Building Documentation" in development_content


def test_docs_build_target(default_project: Path) -> None:
    os.system(f"cd {default_project} && make docs")  # noqa: S605
    assert (default_project / "dist" / "docs").exists()


def test_pyproject_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        pyproject = project_dir / "pyproject.toml"
        pyproject_content = tomllib.loads(pyproject.read_text())
        assert "docs" not in pyproject_content.get("dependency-groups", {})


def test_docs_folder_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        assert not (project_dir / "docs").exists()


def test_docs_target_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        makefile = project_dir / "Makefile"
        makefile_content = makefile.read_text()

        # Docs target is not present
        assert not re.search(r"^docs:$", makefile_content, re.MULTILINE)

        # Docs target is not included in .PHONY
        assert not re.search(r"^.PHONY:.*docs.*$", makefile_content, re.MULTILINE)

        # Build target does not depend on docs
        assert not re.search(r"^build:.*docs.*$", makefile_content, re.MULTILINE)


def test_readme_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        development = project_dir / "DEVELOPMENT.md"
        development_content = development.read_text()
        assert "### Building Documentation" not in development_content
        assert "make docs" not in development_content
