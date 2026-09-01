import shutil
from pathlib import Path

from cookiecutter.main import cookiecutter

from conftest import BUILD_ARTEFACTS, TEMPLATE_CONTENTS, TEMPLATE_DIRECTORY

PLANTED_CACHES = (
    Path("scripts") / ".mypy_cache",
    Path("_git_providers") / "GitHub" / "scripts" / ".mypy_cache",
    Path("src") / "__pycache__",
)


def test_local_caches_do_not_ship(tmp_path: Path, _stubbed_path: None) -> None:
    """Whatever mypy or pytest left inside the template stays out of the generated project."""
    template = _stage_template(tmp_path / "template")
    for cache in PLANTED_CACHES:
        planted = template / "{{cookiecutter.repo_name}}" / cache
        planted.mkdir(parents=True, exist_ok=True)
        (planted / "stale.json").write_text("{}")

    project_dir = _generate(template, tmp_path / "output")

    strays = sorted(str(p.relative_to(project_dir)) for p in project_dir.rglob("*") if _cache(p))
    assert strays == []


def test_generation_writes_a_lockfile(tmp_path: Path, unstubbed_path: None) -> None:
    """Every other test runs against a stubbed `uv lock`; this one runs the real thing."""
    project_dir = _generate(_stage_template(tmp_path / "template"), tmp_path / "output")

    lockfile = (project_dir / "uv.lock").read_text()
    assert 'requires-python = ">=3.13"' in lockfile
    assert "[[package]]" in lockfile


def _stage_template(template: Path) -> Path:
    template.mkdir(parents=True)
    ignore = shutil.ignore_patterns(*BUILD_ARTEFACTS)
    for name in TEMPLATE_CONTENTS:
        source = TEMPLATE_DIRECTORY / name
        if source.is_dir():
            shutil.copytree(source, template / name, ignore=ignore)
        else:
            shutil.copy2(source, template / name)
    return template


def _generate(template: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        cookiecutter(str(template), output_dir=str(output_dir), no_input=True, extra_context={})
    )


def _cache(path: Path) -> bool:
    return path.name in BUILD_ARTEFACTS
