import json
import shutil
from collections.abc import Callable, Generator, Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = Path(__file__).parent.parent

# Keep in sync with the `ebump-version` default in .github/actions/bump-version/action.yml
EBUMP_VERSION = "0.2.1"

ProjectConfig = dict[str, Any]
TemplateRenderer = Callable[[ProjectConfig], Path]
ProjectGenerator = Callable[[ProjectConfig], AbstractContextManager[Path]]

TEMPLATE_CONTENTS = (
    Path("cookiecutter.json"),
    Path("hooks") / "post_gen_project.py",
    Path("{{cookiecutter.repo_name}}"),
)

CACHE_FOLDERS = ("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache")


def copy_template_contents(destination: Path) -> Path:
    ignore = shutil.ignore_patterns(*CACHE_FOLDERS)
    for name in TEMPLATE_CONTENTS:
        source, target = TEMPLATE_DIRECTORY / name, destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=ignore)
        else:
            shutil.copy2(source, target)
    return destination


@pytest.fixture(scope="session")
def render_template() -> Iterator[TemplateRenderer]:
    cache: dict[int, Path] = {}

    with TemporaryDirectory(prefix="cookie-pyrate-") as workspace:
        template = copy_template_contents(Path(workspace) / "template")

        def render_template_with_cache(project_conf: ProjectConfig) -> Path:
            key = hash(json.dumps(project_conf, sort_keys=True))
            if key not in cache:
                output_dir = Path(workspace) / "projects" / str(key)
                cache[key] = _render_template(template, output_dir, project_conf)
            return cache[key]

        yield render_template_with_cache


@pytest.fixture
def project_generator(render_template: TemplateRenderer) -> ProjectGenerator:
    @contextmanager
    def generate(project_conf: ProjectConfig) -> Generator[Path]:
        project = render_template(project_conf)
        with TemporaryDirectory() as destination:
            project_dir = Path(destination) / project.name
            shutil.copytree(project, project_dir, symlinks=True)
            yield project_dir

    return generate


@pytest.fixture
def default_project(project_generator: ProjectGenerator) -> Generator[Path]:
    with project_generator({}) as project_dir:
        yield project_dir


def _render_template(template: Path, output_dir: Path, project_conf: ProjectConfig) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        cookiecutter(
            str(template), output_dir=str(output_dir), no_input=True, extra_context=project_conf
        )
    )
