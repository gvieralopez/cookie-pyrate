import json
import shutil
from collections.abc import Callable, Generator, Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory, mkdtemp
from typing import Any

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIRECTORY = Path(__file__).parent.parent

# Keep in sync with the `ebump-version` default in .github/actions/bump-version/action.yml
EBUMP_VERSION = "0.2.1"

ProjectGenerator = Callable[[dict[str, Any]], AbstractContextManager[Path]]

TEMPLATE_CONTENTS = (
    Path("cookiecutter.json"),
    Path("hooks") / "post_gen_project.py",
    Path("{{cookiecutter.repo_name}}"),
)

CACHE_FOLDERS = ("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache")


def copy_template_contents(destination: Path) -> Path:
    """Copy TEMPLATE_CONTENTS into `destination`, leaving local caches behind."""
    ignore = shutil.ignore_patterns(*CACHE_FOLDERS)
    for name in TEMPLATE_CONTENTS:
        source, target = TEMPLATE_DIRECTORY / name, destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=ignore)
        else:
            shutil.copy2(source, target)
    return destination


def render_template(template: Path, output_dir: Path, project_conf: dict[str, Any]) -> Path:
    """Render `template` into `output_dir`, the one place the tests call cookiecutter."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        cookiecutter(
            str(template), output_dir=str(output_dir), no_input=True, extra_context=project_conf
        )
    )


@pytest.fixture
def default_project(project_generator: ProjectGenerator) -> Generator[Path]:
    with project_generator({}) as project_dir:
        yield project_dir


@pytest.fixture
def project_generator(cached_project: Callable[[dict[str, Any]], Path]) -> ProjectGenerator:
    """Hand each test its own copy, since many of them mutate the project they are given."""

    @contextmanager
    def generate(project_conf: dict[str, Any]) -> Generator[Path]:
        source = cached_project(project_conf)
        with TemporaryDirectory() as output_dir:
            project_dir = Path(output_dir) / source.name
            shutil.copytree(source, project_dir, symlinks=True)
            yield project_dir

    return generate


@pytest.fixture(scope="session")
def cached_project(
    generate_project: Callable[[dict[str, Any]], Path],
) -> Callable[[dict[str, Any]], Path]:
    """`generate_project`, but generating only once per distinct configuration."""
    return _make_caching_generator(generate_project)


@pytest.fixture(scope="session")
def generate_project(template_copy: Path) -> Iterator[Callable[[dict[str, Any]], Path]]:
    """Render the template copy, each configuration into a directory of its own."""
    with TemporaryDirectory(prefix="cookie-pyrate-projects-") as output_root:

        def generate(project_conf: dict[str, Any]) -> Path:
            return render_template(template_copy, Path(mkdtemp(dir=output_root)), project_conf)

        yield generate


@pytest.fixture(scope="session")
def template_copy() -> Iterator[Path]:
    """The copy the tests render from, made once and kept for the whole session."""
    with TemporaryDirectory(prefix="cookie-pyrate-template-") as temporary_dir:
        yield copy_template_contents(Path(temporary_dir) / TEMPLATE_DIRECTORY.name)


def _make_caching_generator(
    generate: Callable[[dict[str, Any]], Path],
) -> Callable[[dict[str, Any]], Path]:
    """Return `generate` wrapped so each distinct configuration is only generated once."""
    results: dict[str, Path] = {}

    def generate_or_reuse(project_conf: dict[str, Any]) -> Path:
        key = json.dumps(project_conf, sort_keys=True)
        if key not in results:
            results[key] = generate(project_conf)
        return results[key]

    return generate_or_reuse
