from contextlib import contextmanager
from shutil import rmtree
from cookiecutter.main import cookiecutter
from pathlib import Path
from typing import Generator
import pytest

TEMPLATE_DIRECTORY = Path(__file__).parent.parent


def clear_tmp_directory() -> None:
    tmp_dir = TEMPLATE_DIRECTORY / "tmp"
    if tmp_dir.exists():
        rmtree(tmp_dir)


@pytest.fixture
def project_generator():
    @contextmanager
    def project_generator(project_conf: dict) -> Generator[Path, None, None]:
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
