import os
import re
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
RUN_SETUP = ACTIONS / "run-setup" / "action.yml"
PUBLISH_TO_PYPI = ACTIONS / "publish-to-pypi" / "action.yml"
BASH = shutil.which("bash") or "bash"


@pytest.mark.parametrize(
    ("workflow", "names"),
    [(REUSABLE_QA, ("setup-command", "extra-checks")), (REUSABLE_RELEASE, ("setup-command",))],
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


@pytest.mark.parametrize("workflow", [REUSABLE_QA, REUSABLE_RELEASE])
def test_setup_secrets_are_declared_not_inherited(workflow: Path) -> None:
    """`secrets: inherit` doesn't cross owners, so callers map SETUP_ENV explicitly."""
    assert "SETUP_ENV" in _load(workflow)[True]["workflow_call"]["secrets"]
    assert "toJSON(secrets)" not in workflow.read_text()


@pytest.mark.parametrize("job", ["checks", "tests"])
def test_qa_jobs_hand_the_setup_secrets_to_run_qa(job: str) -> None:
    steps = _load(REUSABLE_QA)["jobs"][job]["steps"]
    run_qa = next(step for step in steps if step.get("uses", "").endswith("/run-qa"))

    assert run_qa["with"]["setup-command"] == "${{ inputs.setup-command }}"
    assert run_qa["with"]["setup-env"] == "${{ secrets.SETUP_ENV }}"


def test_run_qa_keeps_the_setup_secrets_to_the_setup_step() -> None:
    steps = _load(RUN_QA)["runs"]["steps"]
    setup = _run_qa_step("Run the setup command")

    assert setup["uses"].endswith("/run-setup")
    assert setup["with"] == {
        "command": "${{ inputs.setup-command }}",
        "setup-env": "${{ inputs.setup-env }}",
    }
    others = [step for step in steps if step.get("name") != "Run the setup command"]
    assert [step for step in others if "inputs.setup-env" in str(step)] == []


@pytest.mark.parametrize(
    ("job", "build_step"),
    [
        ("build-and-attach", "Install dependencies"),
        ("publish-docker-image", "Build and push the image"),
    ],
)
def test_release_runs_the_setup_before_building(job: str, build_step: str) -> None:
    steps = _load(REUSABLE_RELEASE)["jobs"][job]["steps"]
    names = [step.get("name") for step in steps]
    setup = steps[names.index("Run the setup command")]

    assert names.index("Run the setup command") < names.index(build_step)
    assert setup["uses"].endswith("/run-setup")
    assert setup["with"]["setup-env"] == "${{ secrets.SETUP_ENV }}"


def test_release_key_keeps_the_name_make_repo_gives_it(default_project: Path) -> None:
    """`make repo` stores the key and the generated release.yml passes it, so the names must match."""
    script = (default_project / "scripts" / "create_remote.py").read_text()
    stored = re.search(r'^RELEASE_KEY_SECRET_NAME = "(\w+)"', script, re.MULTILINE)
    workflow = _load(REUSABLE_RELEASE)
    caller = _load(default_project / ".github" / "workflows" / "release.yml")
    ssh_keys = {
        step["with"]["ssh-key"]
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if "ssh-key" in step.get("with", {})
    }

    assert stored
    expression = f"${{{{ secrets.{stored.group(1)} }}}}"
    assert set(workflow[True]["workflow_call"]["secrets"]) == {stored.group(1), "SETUP_ENV"}
    assert ssh_keys == {expression}
    assert caller["jobs"]["release"]["secrets"] == {stored.group(1): expression}


def test_commands_reach_bash_through_the_environment() -> None:
    """Interpolating ${{ inputs.* }} into `run` would let the expression engine rewrite them."""
    runs = [step["run"] for step in _all_steps() if "run" in step]
    assert [
        run
        for run in runs
        if any(f"inputs.{name}" in run for name in ("setup-command", "extra-checks", "command"))
    ] == []


def test_command_steps_stop_at_the_first_failure(tmp_path: Path) -> None:
    result = _setup(tmp_path, "touch first\nfalse\ntouch never")

    assert result.returncode != 0
    assert (tmp_path / "first").exists()
    assert not (tmp_path / "never").exists()


def test_setup_secrets_reach_the_command_and_nothing_else(tmp_path: Path) -> None:
    github_env = tmp_path / "github_env"
    github_env.touch()
    setup_env = "TOKEN=s3cret\r\n\n  \nURL=https://x.test/?a=b\n"
    command = 'printf "%s|%s|%s" "$TOKEN" "$URL" "${SETUP_ENV-unset}" > seen'

    result = _setup(tmp_path, command, setup_env, GITHUB_ENV=str(github_env))

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "seen").read_text() == "s3cret|https://x.test/?a=b|unset"
    assert "::add-mask::s3cret" in result.stdout
    assert github_env.read_text() == ""


def test_the_command_runs_without_setup_secrets(tmp_path: Path) -> None:
    result = _setup(tmp_path, "touch ran")

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "ran").exists()


def test_a_malformed_setup_line_fails_without_printing_it(tmp_path: Path) -> None:
    result = _setup(tmp_path, "touch never", "s3cret-without-a-name")

    assert result.returncode == 1
    assert "Every SETUP_ENV line must read NAME=value" in result.stdout
    assert "s3cret" not in result.stdout + result.stderr
    assert not (tmp_path / "never").exists()


def test_an_empty_setup_value_fails_and_names_the_variable(tmp_path: Path) -> None:
    result = _setup(tmp_path, "touch never", "TOKEN=")

    assert result.returncode == 1
    assert "TOKEN in SETUP_ENV is empty" in result.stdout
    assert "Dependabot" not in result.stdout
    assert not (tmp_path / "never").exists()


def test_an_empty_setup_value_on_a_dependabot_run_names_the_dependabot_store(
    tmp_path: Path,
) -> None:
    result = _setup(tmp_path, "true", "TOKEN=", GITHUB_ACTOR="dependabot[bot]")

    assert result.returncode == 1
    assert "Add its secret as a Dependabot secret too" in result.stdout


def test_the_development_guide_shows_the_setup_secrets(default_project: Path) -> None:
    development = (default_project / "DEVELOPMENT.md").read_text()
    section = development.split("### Extra CI steps", 1)[1]
    job = yaml.safe_load(section.split("```yaml", 1)[1].split("```", 1)[0])["jobs"]["qa"]

    assert job["secrets"] == {"SETUP_ENV": "WHEELS_TOKEN=${{ secrets.WHEELS_TOKEN }}\n"}
    assert "secret-env" not in section


@pytest.mark.parametrize(("git_provider", "documented"), [("GitHub", True), ("None", False)])
def test_development_guide_documents_the_extra_steps(
    project_generator: ProjectGenerator, git_provider: str, documented: bool
) -> None:
    with project_generator({"git_provider": git_provider}) as project_dir:
        development = (project_dir / "DEVELOPMENT.md").read_text()
        assert ("### Extra CI steps" in development) is documented


def test_docker_builds_leave_the_actions_checkout_out(default_project: Path) -> None:
    assert ".cookie-pyrate" in (default_project / ".dockerignore").read_text().split()


def _setup(
    cwd: Path, command: str, setup_env: str = "", **env: str
) -> subprocess.CompletedProcess[str]:
    script = _load(RUN_SETUP)["runs"]["steps"][0]["run"]
    return _bash(script, cwd, COMMAND=command, SETUP_ENV=setup_env, **env)


def test_the_reusable_release_never_uploads_to_pypi() -> None:
    """PyPI Trusted Publishing rejects uploads from a job defined in another repository's workflow."""
    workflow = _load(REUSABLE_RELEASE)
    runs = [step.get("run", "") for job in workflow["jobs"].values() for step in job["steps"]]

    assert [run for run in runs if "publish" in run and "uv" in run] == []
    assert "publish-to-pypi" not in workflow[True]["workflow_call"]["inputs"]


def test_the_pypi_action_builds_the_released_commit_after_the_setup() -> None:
    steps = _load(PUBLISH_TO_PYPI)["runs"]["steps"]
    names = [step.get("name") for step in steps]

    assert steps[0]["uses"].startswith("actions/checkout@")
    assert steps[0]["with"]["ref"] == "${{ inputs.sha }}"
    assert names.index("Run the setup command") < names.index("Build distribution")
    assert names.index("Build distribution") < names.index("Publish")


@pytest.mark.parametrize(
    ("index", "upload", "simple"),
    [
        ("pypi", "https://upload.pypi.org/legacy/", "https://pypi.org/simple/"),
        ("testpypi", "https://test.pypi.org/legacy/", "https://test.pypi.org/simple/"),
    ],
)
def test_the_pypi_action_uploads_with_trusted_publishing(
    tmp_path: Path, index: str, upload: str, simple: str
) -> None:
    calls = _fake_uv(tmp_path)

    result = _publish(tmp_path, index)

    assert result.returncode == 0, result.stdout + result.stderr
    assert calls.read_text().split() == [
        "publish",
        "--trusted-publishing",
        "always",
        "--publish-url",
        upload,
        "--check-url",
        simple,
    ]


def test_the_pypi_action_rejects_an_unknown_index(tmp_path: Path) -> None:
    calls = _fake_uv(tmp_path)

    result = _publish(tmp_path, "pypy")

    assert result.returncode == 1
    assert "index must be pypi or testpypi, not 'pypy'" in result.stdout
    assert not calls.exists()


def test_the_development_guide_shows_the_pypi_job(default_project: Path) -> None:
    development = (default_project / "DEVELOPMENT.md").read_text()
    release = yaml.safe_load(
        (default_project / ".github" / "workflows" / "release.yml").read_text()
    )
    pin = release["jobs"]["release"]["uses"].split("@", 1)[1]
    snippet = (
        development.split("#### Publishing to PyPI", 1)[1].split("```yaml", 1)[1].split("```", 1)[0]
    )
    job = yaml.safe_load(snippet)["pypi"]

    assert job["needs"] == "release"
    assert job["environment"]["name"] == "pypi"
    assert job["permissions"]["id-token"] == "write"
    assert (
        job["steps"][0]["uses"]
        == f"gvieralopez/cookie-pyrate/.github/actions/publish-to-pypi@{pin}"
    )
    assert job["steps"][0]["with"]["sha"] == "${{ needs.release.outputs.sha }}"
    assert "publish-to-pypi" not in release["jobs"]["release"]["with"]


def _fake_uv(folder: Path) -> Path:
    calls = folder / "uv-calls"
    fake = folder / "bin" / "uv"
    fake.parent.mkdir()
    fake.write_text(f'#!/bin/sh\necho "$@" > {calls}\n')
    fake.chmod(0o755)
    return calls


def _publish(folder: Path, index: str) -> subprocess.CompletedProcess[str]:
    steps = _load(PUBLISH_TO_PYPI)["runs"]["steps"]
    publish = next(step for step in steps if step.get("name") == "Publish")
    return subprocess.run(
        [BASH, "-c", publish["run"]],
        cwd=folder,
        env={"PATH": f"{folder / 'bin'}:{os.environ['PATH']}", "INDEX": index},
        capture_output=True,
        text=True,
        check=False,
    )


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
    for action in (RUN_QA, RUN_SETUP, PUBLISH_TO_PYPI):
        steps += _load(action)["runs"]["steps"]
    for workflow in (REUSABLE_QA, REUSABLE_RELEASE):
        for job in _load(workflow)["jobs"].values():
            steps += job.get("steps", [])
    return steps


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text())
