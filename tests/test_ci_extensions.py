import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from conftest import TEMPLATE_DIRECTORY, ProjectGenerator

WORKFLOWS = TEMPLATE_DIRECTORY / ".github" / "workflows"
ACTIONS = TEMPLATE_DIRECTORY / ".github" / "actions"
REUSABLE_QA = WORKFLOWS / "reusable-qa.yml"
REUSABLE_RELEASE = WORKFLOWS / "reusable-release.yml"
RUN_QA = ACTIONS / "run-qa" / "action.yml"
EXPORT_SECRETS = ACTIONS / "export-secrets" / "action.yml"
BASH = shutil.which("bash") or "bash"
NEEDS_JQ = pytest.mark.skipif(shutil.which("jq") is None, reason="jq is missing")


@pytest.mark.parametrize(
    ("workflow", "names"),
    [
        (REUSABLE_QA, ("setup-command", "extra-checks", "secret-env")),
        (REUSABLE_RELEASE, ("setup-command", "secret-env")),
    ],
)
def test_extension_inputs_change_nothing_by_default(workflow: Path, names: tuple[str, ...]) -> None:
    inputs = _load(workflow)[True]["workflow_call"]["inputs"]
    assert {name: inputs[name]["default"] for name in names} == dict.fromkeys(names, "")


def test_setup_runs_before_the_install_and_extra_checks_after_the_tests() -> None:
    steps = _load(RUN_QA)["runs"]["steps"]
    names = [step.get("name") for step in steps]

    assert names.index("Run the setup command") < names.index("Install dependencies")
    assert names.index("Run the extra checks") > names.index("Run tests")
    assert "inputs.checks == 'true'" in steps[names.index("Run the extra checks")]["if"]


@pytest.mark.parametrize("job", ["checks", "tests"])
def test_qa_jobs_export_secrets_before_running_qa(job: str) -> None:
    steps = _load(REUSABLE_QA)["jobs"][job]["steps"]
    uses = [step.get("uses", "") for step in steps]
    export = next(i for i, used in enumerate(uses) if used.endswith("/export-secrets"))
    run_qa = next(i for i, used in enumerate(uses) if used.endswith("/run-qa"))

    assert export < run_qa
    assert steps[run_qa]["with"]["setup-command"] == "${{ inputs.setup-command }}"


@pytest.mark.parametrize(
    ("job", "build_step"),
    [
        ("build-and-publish", "Install dependencies"),
        ("publish-docker-image", "Build and push the image"),
    ],
)
def test_release_runs_the_setup_before_building(job: str, build_step: str) -> None:
    steps = _load(REUSABLE_RELEASE)["jobs"][job]["steps"]
    names = [step.get("name") for step in steps]
    uses = [step.get("uses", "") for step in steps]
    export = next(i for i, used in enumerate(uses) if used.endswith("/export-secrets"))

    assert export < names.index("Run the setup command") < names.index(build_step)


def test_inherited_secrets_still_reach_the_release_key() -> None:
    workflow = _load(REUSABLE_RELEASE)
    declared = set(workflow[True]["workflow_call"]["secrets"])
    ssh_keys = [
        step["with"]["ssh-key"]
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if "ssh-key" in step.get("with", {})
    ]

    assert {"release-ssh-key", "RELEASE_SSH_KEY"} <= declared
    assert ssh_keys
    assert set(ssh_keys) == {"${{ secrets.release-ssh-key || secrets.RELEASE_SSH_KEY }}"}


def test_commands_reach_bash_through_the_environment() -> None:
    """Interpolating ${{ inputs.* }} into `run` would let the expression engine rewrite them."""
    runs = [step["run"] for step in _all_steps() if "run" in step]
    assert [
        run for run in runs if "inputs.setup-command" in run or "inputs.extra-checks" in run
    ] == []


def test_command_steps_stop_at_the_first_failure(tmp_path: Path) -> None:
    step = _run_qa_step("Run the setup command")
    result = _bash(step["run"], tmp_path, COMMAND="touch first\nfalse\ntouch never")

    assert result.returncode != 0
    assert (tmp_path / "first").exists()
    assert not (tmp_path / "never").exists()


@NEEDS_JQ
def test_exported_secrets_reach_the_job_environment(tmp_path: Path) -> None:
    secrets = {"TOKEN": "s3cret", "MULTI": "one\ntwo", "OTHER": "unrequested"}
    github_env = tmp_path / "github_env"

    result = _export(tmp_path, "TOKEN MULTI", secrets, github_env)

    assert result.returncode == 0, result.stdout + result.stderr
    exported = github_env.read_text()
    assert _heredoc_value(exported, "TOKEN") == "s3cret"
    assert _heredoc_value(exported, "MULTI") == "one\ntwo"
    assert "OTHER" not in exported
    assert "::add-mask::s3cret" in result.stdout


@NEEDS_JQ
def test_a_missing_secret_fails_and_names_the_fix(tmp_path: Path) -> None:
    result = _export(tmp_path, "MISSING", {}, tmp_path / "github_env")

    assert result.returncode == 1
    assert "Secret MISSING isn't available" in result.stdout
    assert "secrets: inherit" in result.stdout


@pytest.mark.parametrize(("git_provider", "documented"), [("GitHub", True), ("None", False)])
def test_development_guide_documents_the_extra_steps(
    project_generator: ProjectGenerator, git_provider: str, documented: bool
) -> None:
    with project_generator({"git_provider": git_provider}) as project_dir:
        development = (project_dir / "DEVELOPMENT.md").read_text()
        assert ("### Extra CI steps" in development) is documented


def test_docker_builds_leave_the_actions_checkout_out(default_project: Path) -> None:
    assert ".cookie-pyrate" in (default_project / ".dockerignore").read_text().split()


def _export(
    cwd: Path, names: str, secrets: dict[str, str], github_env: Path
) -> subprocess.CompletedProcess[str]:
    script = _load(EXPORT_SECRETS)["runs"]["steps"][0]["run"]
    github_env.touch()
    return _bash(script, cwd, NAMES=names, SECRETS=json.dumps(secrets), GITHUB_ENV=str(github_env))


def _heredoc_value(github_env: str, name: str) -> str:
    lines = github_env.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"{name}<<"))
    delimiter = lines[start].split("<<", 1)[1]
    end = lines.index(delimiter, start + 1)
    return "\n".join(lines[start + 1 : end])


def _bash(script: str, cwd: Path, **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [BASH, "-c", script],
        cwd=cwd,
        env={"PATH": os.environ["PATH"], **env},
        capture_output=True,
        text=True,
        check=False,
    )


def _run_qa_step(name: str) -> dict[str, Any]:
    steps: list[dict[str, Any]] = _load(RUN_QA)["runs"]["steps"]
    return next(step for step in steps if step.get("name") == name)


def _all_steps() -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for action in (RUN_QA, EXPORT_SECRETS):
        steps += _load(action)["runs"]["steps"]
    for workflow in (REUSABLE_QA, REUSABLE_RELEASE):
        for job in _load(workflow)["jobs"].values():
            steps += job.get("steps", [])
    return steps


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text())
