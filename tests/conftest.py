from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = Path(__file__).parent.parent

# Keep in sync with the `ebump-version` default in .github/actions/bump-version/action.yml
EBUMP_VERSION = "0.2.1"

ProjectGenerator = Callable[[dict[str, Any]], AbstractContextManager[Path]]


@pytest.fixture
def default_project(project_generator: ProjectGenerator) -> Generator[Path]:
    with project_generator({}) as project_dir:
        yield project_dir


@pytest.fixture
def project_generator() -> ProjectGenerator:
    @contextmanager
    def generate(project_conf: dict[str, Any]) -> Generator[Path]:
        with TemporaryDirectory() as output_dir:
            output = cookiecutter(
                str(TEMPLATE_DIRECTORY),
                output_dir=output_dir,
                no_input=True,
                extra_context=project_conf,
            )
            yield Path(output)

    return generate
