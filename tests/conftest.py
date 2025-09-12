from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from typing import Generator

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = Path(__file__).parent.parent


def clear_tmp_directory() -> None:
    tmp_dir = TEMPLATE_DIRECTORY / "tmp"
    if tmp_dir.exists():
        rmtree(tmp_dir)


@pytest.fixture
def project_generator():
    @contextmanager
    def project_generator(
        project_conf: dict | None = None,
    ) -> Generator[Path, None, None]:
        project_conf = {} if project_conf is None else project_conf
        """Generate a project using the provided configuration."""
        output_dir = TEMPLATE_DIRECTORY / "tmp"
        output_dir.mkdir(exist_ok=True)

        clear_tmp_directory()

        output = cookiecutter(
            str(TEMPLATE_DIRECTORY),
            output_dir=str(output_dir),
            no_input=True,
            extra_context=project_conf,
        )
        yield Path(output)

        clear_tmp_directory()

    return project_generator
