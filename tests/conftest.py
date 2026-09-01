import json
import os
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

ProjectGenerator = Callable[[dict[str, Any]], AbstractContextManager[Path]]

# Everything cookiecutter needs to render the template, and nothing else. A pre_prompt hook
# makes cookiecutter copy the whole template directory on *every* generation, so handing it
# the repository root would copy .venv, .git and every local cache each time.
TEMPLATE_CONTENTS = ("cookiecutter.json", "hooks", "{{cookiecutter.repo_name}}")

# Caches local tooling leaves behind. The post-gen hook strips these from generated projects
# too; keeping them out of the staged template means never paying to copy them in the first place.
BUILD_ARTEFACTS = ("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache")

# `gh api user` in the pre_prompt hook is a network round-trip whose answer decides whether
# CODEOWNERS survives, so an authenticated contributor and a bare CI runner would otherwise
# generate structurally different projects. Failing like an unauthenticated gh pins both to
# the CI behaviour. Only `gh` is stubbed: tests resolve `git` and `make` through PATH and
# need the real ones.
GH_STUB = "#!/bin/sh\nexit 1\n"

# `uv lock` also runs on every generation. Locking is covered once, by
# test_generation.py::test_generation_writes_a_lockfile, which drops this stub; everywhere
# else an empty lockfile is enough. Any other uv subcommand reaches the real binary, which
# `make docs` and `uv run` in the generated project depend on.
UV_STUB = """#!/bin/sh
if [ "$1" = lock ]; then
    : > uv.lock
    exit 0
fi
exec {uv} "$@"
"""


@pytest.fixture
def default_project(project_generator: ProjectGenerator) -> Generator[Path]:
    with project_generator({}) as project_dir:
        yield project_dir


@pytest.fixture
def project_generator(pristine_project: Callable[[dict[str, Any]], Path]) -> ProjectGenerator:
    """Hand each test its own copy, since many of them mutate the project they are given."""

    @contextmanager
    def generate(project_conf: dict[str, Any]) -> Generator[Path]:
        pristine = pristine_project(project_conf)
        with TemporaryDirectory() as output_dir:
            project_dir = Path(output_dir) / pristine.name
            shutil.copytree(pristine, project_dir, symlinks=True)
            yield project_dir

    return generate


@pytest.fixture(scope="session")
def pristine_project(
    staged_template: Path, _stubbed_path: None
) -> Iterator[Callable[[dict[str, Any]], Path]]:
    """Generate once per distinct configuration and reuse the result for the whole session."""
    generated: dict[str, Path] = {}

    with TemporaryDirectory(prefix="cookie-pyrate-projects-") as cache_dir:

        def build(project_conf: dict[str, Any]) -> Path:
            key = json.dumps(project_conf, sort_keys=True)
            if key not in generated:
                output_dir = Path(cache_dir) / str(len(generated))
                output_dir.mkdir()
                generated[key] = Path(
                    cookiecutter(
                        str(staged_template),
                        output_dir=str(output_dir),
                        no_input=True,
                        extra_context=project_conf,
                    )
                )
            return generated[key]

        yield build


@pytest.fixture(scope="session")
def staged_template() -> Iterator[Path]:
    """A copy of the template holding only what cookiecutter reads. See TEMPLATE_CONTENTS."""
    ignore = shutil.ignore_patterns(*BUILD_ARTEFACTS)

    with TemporaryDirectory(prefix="cookie-pyrate-template-") as staging_dir:
        staged = Path(staging_dir) / TEMPLATE_DIRECTORY.name
        staged.mkdir()
        for name in TEMPLATE_CONTENTS:
            source = TEMPLATE_DIRECTORY / name
            if source.is_dir():
                shutil.copytree(source, staged / name, ignore=ignore)
            else:
                shutil.copy2(source, staged / name)
        yield staged


@pytest.fixture
def unstubbed_path(stub_bin: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop the stubs again, for the few tests that need the real `gh` and `uv`."""
    entries = [e for e in os.environ["PATH"].split(os.pathsep) if e != str(stub_bin)]
    monkeypatch.setenv("PATH", os.pathsep.join(entries))


@pytest.fixture(scope="session")
def _stubbed_path(stub_bin: Path) -> Iterator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("PATH", f"{stub_bin}{os.pathsep}{os.environ['PATH']}")
        yield


@pytest.fixture(scope="session")
def stub_bin() -> Iterator[Path]:
    """Stubs for the commands the generation hooks shell out to. See GH_STUB and UV_STUB."""
    with TemporaryDirectory(prefix="cookie-pyrate-bin-") as bin_dir:
        stub_bin = Path(bin_dir)
        _write_stub(stub_bin / "gh", GH_STUB)
        _write_stub(stub_bin / "uv", UV_STUB.format(uv=shutil.which("uv") or "uv"))
        yield stub_bin


def _write_stub(path: Path, script: str) -> None:
    path.write_text(script)
    path.chmod(0o755)
