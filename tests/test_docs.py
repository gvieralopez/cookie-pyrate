import os
import re
import tomllib
from pathlib import Path

import yaml

from conftest import requirement_names


def test_pyproject_with_docs(default_project: Path) -> None:
    pyproject = default_project / "pyproject.toml"
    pyproject_content = tomllib.loads(pyproject.read_text())

    assert "docs" in pyproject_content["dependency-groups"]

    docs_deps = requirement_names(pyproject_content["dependency-groups"]["docs"])
    assert "zensical" in docs_deps
    assert "mkdocstrings[python]" in docs_deps


def test_docs_folder_with_docs(default_project: Path) -> None:
    assert (default_project / "docs").exists()
    assert (default_project / "zensical.toml").exists()
    assert not (default_project / "mkdocs.yml").exists()


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
    reference = (default_project / "dist" / "docs" / "reference" / "index.html").read_text()
    # Documented even without docstrings, so a new project's Reference page isn't empty.
    assert 'id="my_pirate_project.main.main"' in reference
    # ...but without loggers and private names.
    assert 'id="my_pirate_project.logger"' not in reference
    assert 'id="my_pirate_project.__version__"' not in reference


def test_docs_group_documents_the_api(default_project: Path) -> None:
    pyproject = tomllib.loads((default_project / "pyproject.toml").read_text())
    assert "mkdocstrings[python]" in requirement_names(pyproject["dependency-groups"]["docs"])


def test_zensical_is_set_up_for_a_hosted_site(default_project: Path) -> None:
    config = tomllib.loads((default_project / "zensical.toml").read_text())["project"]
    plugin_names = list(config["plugins"])

    assert "offline" not in plugin_names
    assert "mkdocstrings" in plugin_names
    assert {"📖 Reference": "reference.md"} in config["nav"]
    assert "/" not in [link for entry in config["nav"] for link in entry.values()]
    assert config["site_dir"] == "dist/docs"
    schemes = [palette["scheme"] for palette in config["theme"]["palette"]]
    assert schemes == ["default", "slate"]
    assert all("toggle" in palette for palette in config["theme"]["palette"])
    assert (default_project / "docs" / "reference.md").exists()


def test_read_the_docs_builds_the_locked_docs_group(default_project: Path) -> None:
    config = yaml.safe_load((default_project / ".readthedocs.yaml").read_text())

    assert config["version"] == 2
    assert " ".join(config["build"]["jobs"]["build"]["html"]).endswith("zensical build --clean")
    assert config["build"]["tools"]["python"] == "latest"
    install = " ".join(config["build"]["jobs"]["install"])
    assert "uv sync --frozen" in install
    assert "--group docs" in install


def test_pyproject_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        pyproject = project_dir / "pyproject.toml"
        pyproject_content = tomllib.loads(pyproject.read_text())
        assert "docs" not in pyproject_content.get("dependency-groups", {})


def test_docs_folder_without_docs(project_generator) -> None:
    with project_generator({"with_docs": False}) as project_dir:
        assert not (project_dir / "docs").exists()
        assert not (project_dir / "zensical.toml").exists()
        assert not (project_dir / ".readthedocs.yaml").exists()


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
