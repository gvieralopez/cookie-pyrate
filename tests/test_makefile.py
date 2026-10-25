import re

import pytest

from conftest import ProjectConfig, ProjectGenerator

CONFIGURATIONS = [
    {},
    {"cli_command": "pirate"},
    {"with_docs": False, "with_dockerfile": False},
    {"git_provider": "None"},
]


@pytest.mark.parametrize("conf", CONFIGURATIONS)
def test_every_phony_target_has_a_rule(
    project_generator: ProjectGenerator, conf: ProjectConfig
) -> None:
    with project_generator(conf) as project_dir:
        makefile = (project_dir / "Makefile").read_text()
        phony = re.search(r"^\.PHONY:(.*)$", makefile, re.MULTILINE)
        assert phony
        rules = set(re.findall(r"^([\w-]+):", makefile, re.MULTILINE))
        assert set(phony.group(1).split()) - rules == set()
