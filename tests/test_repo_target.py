import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ProjectGenerator

REMOTE_SCRIPT = Path("scripts") / "create_remote.py"
PROVIDERS_DIR = Path("_git_providers")
NEEDS_MAKE = pytest.mark.skipif(shutil.which("make") is None, reason="make is missing")
_GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def test_makefile_exposes_the_repo_target(default_project: Path) -> None:
    makefile = (default_project / "Makefile").read_text()
    assert re.search(r"^repo:$", makefile, re.MULTILINE)
    assert re.search(r"^\.PHONY:.*\brepo\b", makefile, re.MULTILINE)
    assert "git init -q -b main" in makefile
    assert str(REMOTE_SCRIPT) in makefile


def test_remote_script_renders_to_valid_python(default_project: Path) -> None:
    source = (default_project / REMOTE_SCRIPT).read_text()
    compile(source, str(REMOTE_SCRIPT), "exec")
    assert 'REPO_NAME = "my-pirate-project"' in source


def test_remote_script_does_not_leak_generation_paths(default_project: Path) -> None:
    source = (default_project / REMOTE_SCRIPT).read_text()
    assert "_output_dir" not in source
    assert "_repo_dir" not in source


def test_missing_gh_creates_no_remote(default_project: Path, tmp_path: Path) -> None:
    result = _run_script(default_project, REMOTE_SCRIPT, path=_git_only_bin(tmp_path))

    assert result.returncode == 1
    assert "cli.github.com" in result.stderr
    assert not (default_project / ".git").exists()


def test_provider_sources_do_not_ship(default_project: Path) -> None:
    assert (default_project / REMOTE_SCRIPT).is_file()
    assert not (default_project / PROVIDERS_DIR).exists()


def test_no_provider_ships_a_purely_local_repo_target(project_generator: ProjectGenerator) -> None:
    with project_generator({"git_provider": "None"}) as project_dir:
        assert not (project_dir / REMOTE_SCRIPT).exists()
        assert not (project_dir / PROVIDERS_DIR).exists()
        assert str(REMOTE_SCRIPT) not in (project_dir / "Makefile").read_text()
        for script in (project_dir / "scripts").iterdir():
            assert '"gh"' not in script.read_text()


def test_policy_enforces_review_rules(project_generator: ProjectGenerator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        policy = _policy(project_dir)
        reviews = policy["required_pull_request_reviews"]
        assert reviews == {
            "required_approving_review_count": 0,
            "require_code_owner_reviews": True,
            "dismiss_stale_reviews": True,
        }
        assert policy["required_conversation_resolution"] is True
        assert policy["required_linear_history"] is True
        assert policy["allow_force_pushes"] is False
        assert policy["allow_deletions"] is False


def test_policy_requires_the_qa_check_when_a_workflow_exists(default_project: Path) -> None:
    assert _policy(default_project)["required_status_checks"] == {
        "strict": True,
        "contexts": ["qa"],
    }


def test_policy_drops_the_qa_check_without_a_workflow(project_generator: ProjectGenerator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        (project_dir / ".github" / "workflows" / "qa.yml").unlink()

        policy = _policy(project_dir)
        assert policy["required_status_checks"] is None
        assert policy["required_pull_request_reviews"]["require_code_owner_reviews"] is True  # type: ignore[index]


def test_policy_drops_code_owner_reviews_without_codeowners(
    project_generator: ProjectGenerator,
) -> None:
    with project_generator({"codeowner_username": ""}) as project_dir:
        assert not (project_dir / "CODEOWNERS").exists()
        reviews = _policy(project_dir)["required_pull_request_reviews"]
        assert reviews["require_code_owner_reviews"] is False  # type: ignore[index]


@NEEDS_MAKE
def test_make_repo_initialises_main_and_is_idempotent(
    project_generator: ProjectGenerator, tmp_path: Path
) -> None:
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text("[init]\n\tdefaultBranch = master\n")

    with project_generator({"git_provider": "None"}) as project_dir:
        first = _make_repo(project_dir, gitconfig=str(gitconfig))
        second = _make_repo(project_dir, gitconfig=str(gitconfig))

        assert first.returncode == 0, first.stderr
        assert "initialised the local repository" in first.stdout
        assert "created the initial commit" in first.stdout
        assert (project_dir / ".git" / "HEAD").read_text().strip() == "ref: refs/heads/main"

        assert second.returncode == 0, second.stderr
        assert "already initialised" in second.stdout
        assert "initial commit already present" in second.stdout


@NEEDS_MAKE
def test_make_repo_without_git_names_the_fix(
    project_generator: ProjectGenerator, tmp_path: Path
) -> None:
    make_only = tmp_path / "bin"
    make_only.mkdir()
    (make_only / "make").symlink_to(shutil.which("make") or "")

    with project_generator({"git_provider": "None"}) as project_dir:
        result = _make_repo(project_dir, path=make_only)

        assert result.returncode != 0
        assert "git-scm.com/downloads" in result.stderr
        assert not (project_dir / ".git").exists()


@pytest.mark.parametrize(
    ("protocol", "expected"),
    [("ssh", "git@github.com:me/repo.git"), ("https", "https://github.com/me/repo.git")],
)
def test_existing_remote_honours_the_configured_protocol(
    default_project: Path, tmp_path: Path, protocol: str, expected: str
) -> None:
    fake_bin = _git_only_bin(tmp_path)
    gh = fake_bin / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        f'  "config get git_protocol") echo {protocol} ;;\n'
        '  *"--json sshUrl"*) echo git@github.com:me/repo.git ;;\n'
        '  *"--json url"*) echo https://github.com/me/repo ;;\n'
        "  *) exit 0 ;;\n"
        "esac\n"
    )
    gh.chmod(0o755)

    _git_init(default_project)
    result = _run_module(
        default_project, REMOTE_SCRIPT, "module.create_remote_repository('private')", path=fake_bin
    )

    assert result.returncode == 0, result.stderr
    origin = subprocess.run(
        [shutil.which("git") or "git", "remote", "get-url", "origin"],
        cwd=default_project,
        capture_output=True,
        text=True,
        check=True,
    )
    assert origin.stdout.strip() == expected


def _git_init(project_dir: Path) -> None:
    subprocess.run(
        [shutil.which("git") or "git", "init", "-q", "-b", "main"],
        cwd=project_dir,
        capture_output=True,
        check=True,
    )


def _make_repo(
    project_dir: Path, path: Path | None = None, gitconfig: str | None = None
) -> subprocess.CompletedProcess[str]:
    extra = {"GIT_CONFIG_GLOBAL": gitconfig} if gitconfig else {}
    return subprocess.run(
        [shutil.which("make") or "make", "repo"],
        cwd=project_dir,
        env=_environment(project_dir, path, **extra),
        capture_output=True,
        text=True,
        check=False,
    )


def _git_only_bin(tmp_path: Path) -> Path:
    only_git = tmp_path / "bin"
    only_git.mkdir(exist_ok=True)
    (only_git / "git").symlink_to(shutil.which("git") or "")
    return only_git


def _environment(project_dir: Path, path: Path | None, **extra: str) -> dict[str, str]:
    return {
        "PATH": str(path) if path else os.environ["PATH"],
        **_GIT_IDENTITY,
        "HOME": str(project_dir),
        **extra,
    }


def _run_script(
    project_dir: Path, script: Path, path: Path | None = None, **extra: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=project_dir,
        env=_environment(project_dir, path, **extra),
        capture_output=True,
        text=True,
        check=False,
    )


def _run_module(
    project_dir: Path, script: Path, body: str, path: Path | None = None, **extra: str
) -> subprocess.CompletedProcess[str]:
    program = (
        "import importlib.util;"
        f"spec = importlib.util.spec_from_file_location('m', {str(script)!r});"
        "module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module);"
        f"{body}"
    )
    return subprocess.run(
        [sys.executable, "-c", program],
        cwd=project_dir,
        env=_environment(project_dir, path, **extra),
        capture_output=True,
        text=True,
        check=False,
    )


def _policy(project_dir: Path) -> dict[str, object]:
    result = _run_module(
        project_dir,
        REMOTE_SCRIPT,
        "import json; print(json.dumps(module._branch_policy(module._required_status_checks())))",
    )
    assert result.returncode == 0, result.stderr
    loaded: dict[str, object] = json.loads(result.stdout)
    return loaded
