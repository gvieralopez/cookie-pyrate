import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml
from markdown_it import MarkdownIt

from conftest import TEMPLATE_DIRECTORY, ProjectConfig, ProjectGenerator

QA_BADGE = "https://github.com/octocat/my-pirate-project/actions/workflows/qa.yml/badge.svg"
RELEASE_BADGE = "https://img.shields.io/github/v/release/octocat/my-pirate-project"
LINK_TARGET = re.compile(r"\]\(([^)#:]+)\)|src=\"([^\"]+)\"")


def test_badges_link_to_the_owner_and_repository(project_generator: ProjectGenerator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        readme = _visible(project_dir)
        assert QA_BADGE in readme
        assert RELEASE_BADGE in readme
        assert "python-3.15%2B" in readme


def test_every_badge_renders_as_an_image(project_generator: ProjectGenerator) -> None:
    """A line starting with HTML can turn the next lines into raw text; CommonMark shows it."""
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        html = MarkdownIt("commonmark").render((project_dir / "README.md").read_text())
        images = re.findall(r'<img src="([^"]+)"', html)

        assert "[![" not in _without_comments(html)
        assert len(images) == 8
        assert any("astral-sh/uv" in image for image in images)
        assert any("mypy_badge" in image for image in images)


def test_github_badges_need_github(project_generator: ProjectGenerator) -> None:
    with project_generator({"git_provider": "None"}) as project_dir:
        readme = (project_dir / "README.md").read_text()
        assert "actions/workflows/qa.yml" not in readme
        assert "github/v/release" not in readme


def test_readme_branches_only_where_it_must() -> None:
    """Conditions in the README template bite; only these three reasons justify one."""
    template = (TEMPLATE_DIRECTORY / "{{cookiecutter.repo_name}}" / "README.md").read_text()
    conditions = set(re.findall(r"\{%-?\s*if (.+?)\s*-?%\}", template))
    assert conditions == {
        'cookiecutter.git_provider == "GitHub"',
        'cookiecutter.license != "None"',
        "cookiecutter.cli_command",
    }
    assert "{% set" not in template


@pytest.mark.parametrize(
    ("license_choice", "badge"),
    [("MIT", "license-MIT-"), ("GPL-3.0-or-later", "license-GPL--3.0--or--later-"), ("None", None)],
)
def test_license_badge_and_section_follow_the_choice(
    project_generator: ProjectGenerator, license_choice: str, badge: str | None
) -> None:
    with project_generator({"license": license_choice}) as project_dir:
        readme = _visible(project_dir)
        assert ("## License" in readme) is (badge is not None)
        assert badge is None or badge in readme


def test_optional_badges_ship_hidden(project_generator: ProjectGenerator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        readme = (project_dir / "README.md").read_text()
        hidden = "".join(re.findall(r"<!--(.*?)-->", readme, re.DOTALL))
        assert "pypi/v/my_pirate_project" in hidden
        assert "pkgs/container/my-pirate-project" in hidden
        assert "readthedocs.org/projects/my-pirate-project" in hidden
        assert "pypi/v/" not in _visible(project_dir)


@pytest.mark.parametrize(
    ("with_docs", "logos"),
    [
        (True, {Path("assets/logo.svg"), Path("docs/images/logo.svg")}),
        (False, {Path("assets/logo.svg")}),
    ],
)
def test_logo_with_the_project_initial(
    project_generator: ProjectGenerator, with_docs: bool, logos: set[Path]
) -> None:
    with project_generator({"with_docs": with_docs, "project_name": "Treasure Map"}) as project_dir:
        logo = (project_dir / "assets" / "logo.svg").read_text()
        svgs = {path.relative_to(project_dir) for path in project_dir.rglob("logo.svg")}
        assert svgs == logos
        assert {(project_dir / path).read_text() for path in logos} == {logo}
        assert ">T</text>" in logo
        assert 'src="assets/logo.svg"' in (project_dir / "README.md").read_text()


def test_docs_use_the_same_logo(default_project: Path) -> None:
    theme = yaml.safe_load((default_project / "mkdocs.yml").read_text())["theme"]
    assert theme["logo"] == theme["favicon"] == "images/logo.svg"
    assert not list((default_project / "docs").rglob("*.png"))


@pytest.mark.parametrize(
    ("version", "link"),
    [("v1.2.3", "cookie-pyrate/tree/v1.2.3"), ("main", "cookie-pyrate/tree/main")],
)
def test_footer_names_the_template_version(
    project_generator: ProjectGenerator, version: str, link: str
) -> None:
    with project_generator({"__cookiepyrate_version": version}) as project_dir:
        footer = (project_dir / "README.md").read_text().strip().splitlines()[-1]
        assert f"Cookie Pyrate {version}]" in footer
        assert link in footer


@pytest.mark.parametrize(
    "conf",
    [{}, {"with_docs": False, "license": "None", "git_provider": "None", "cli_command": "x"}],
)
def test_readme_renders_completely(
    project_generator: ProjectGenerator, conf: ProjectConfig
) -> None:
    with project_generator(conf) as project_dir:
        readme = (project_dir / "README.md").read_text()
        assert "{{" not in readme
        assert "{%" not in readme
        for target in _relative_targets(readme):
            assert (project_dir / target).exists(), target


def test_project_links_start_empty(default_project: Path) -> None:
    pyproject = tomllib.loads((default_project / "pyproject.toml").read_text())
    assert pyproject["project"]["urls"] == {}


def test_project_with_empty_links_still_builds(default_project: Path) -> None:
    result = subprocess.run(
        [shutil.which("uv") or "uv", "build", "--wheel", "--out-dir", "dist"],
        cwd=default_project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert list((default_project / "dist").glob("*.whl"))


def _visible(project_dir: Path) -> str:
    return _without_comments((project_dir / "README.md").read_text())


def _relative_targets(readme: str) -> list[str]:
    targets = [link or src for link, src in LINK_TARGET.findall(_without_comments(readme))]
    return [target for target in targets if not target.startswith("http")]


def _without_comments(markdown: str) -> str:
    return re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
