from pathlib import Path

from conftest import CACHE_FOLDERS, _render_template, copy_template_contents

PLANTED_CACHES = (
    Path("scripts") / ".mypy_cache",
    Path("_git_providers") / "GitHub" / "scripts" / ".mypy_cache",
    Path("src") / "__pycache__",
)


def test_local_caches_do_not_ship(tmp_path: Path) -> None:
    template = copy_template_contents(tmp_path / "template")
    for cache in PLANTED_CACHES:
        planted = template / "{{cookiecutter.repo_name}}" / cache
        planted.mkdir(parents=True, exist_ok=True)
        (planted / "stale.json").write_text("{}")

    project_dir = _render_template(template, tmp_path / "output", {})

    strays = [
        str(p.relative_to(project_dir)) for p in project_dir.rglob("*") if p.name in CACHE_FOLDERS
    ]
    assert strays == []


def test_generation_writes_a_lockfile(default_project: Path) -> None:
    lockfile = (default_project / "uv.lock").read_text()
    assert 'requires-python = ">=3.13"' in lockfile
    assert "[[package]]" in lockfile
