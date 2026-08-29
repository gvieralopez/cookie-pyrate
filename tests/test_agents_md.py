import re
from pathlib import Path

from conftest import TEMPLATE_DIRECTORY, ProjectGenerator

TEMPLATED_RULES = ("src/", "Standard QA invocation")


def test_agents_md_has_no_frontmatter(default_project: Path) -> None:
    assert not (default_project / "AGENTS.md").read_text().startswith("---")


def test_agents_md_names_the_real_package(default_project: Path) -> None:
    content = (default_project / "AGENTS.md").read_text()
    assert "src/my_pirate_project/{models,errors,main}.py" in content
    assert "<snake_case_pkg>" not in content


def test_agents_md_sections_match_the_template_repo(default_project: Path) -> None:
    generated = (default_project / "AGENTS.md").read_text()
    root = (TEMPLATE_DIRECTORY / "AGENTS.md").read_text()
    assert re.findall(r"^## .+$", generated, re.MULTILINE) == re.findall(
        r"^## .+$", root, re.MULTILINE
    )


def test_agents_md_shares_the_untemplated_rules(default_project: Path) -> None:
    generated = (default_project / "AGENTS.md").read_text()
    root = (TEMPLATE_DIRECTORY / "AGENTS.md").read_text()
    shared = {r for r in _rules(root) if not any(t in r for t in TEMPLATED_RULES)}
    assert shared <= _rules(generated)


def test_agents_md_ci_rule_follows_the_pipeline(project_generator: ProjectGenerator) -> None:
    with project_generator({"ci_cd_pipeline": "None"}) as project_dir:
        assert "CI runs this same gate" not in (project_dir / "AGENTS.md").read_text()


def _rules(text: str) -> set[str]:
    return {line for line in text.splitlines() if re.match(r"^\d+\. ", line)}
