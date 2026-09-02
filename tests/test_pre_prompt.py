"""Cover the pre-prompt hook directly: generation leaves it out, so nothing else exercises it."""

import subprocess

import pytest

import pre_prompt


def test_git_config_answers_with_the_configured_value(monkeypatch: pytest.MonkeyPatch) -> None:
    commands = _patch_subprocess_run_output(monkeypatch, stdout="Grace Hopper\n")

    assert pre_prompt.get_git_config("user.name", "nobody") == "Grace Hopper"
    assert commands == [["git", "config", "--global", "user.name"]]


def test_git_config_falls_back_when_git_has_no_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_subprocess_run_output(monkeypatch, returncode=1)

    assert pre_prompt.get_git_config("user.email", "nobody@example.com") == "nobody@example.com"


def test_codeowner_username_answers_with_the_login(monkeypatch: pytest.MonkeyPatch) -> None:
    commands = _patch_subprocess_run_output(monkeypatch, stdout="octocat\n")

    assert pre_prompt.get_codeowner_username("") == "octocat"
    assert commands == [["gh", "api", "user", "--jq", ".login"]]


def test_codeowner_username_falls_back_when_gh_is_unauthenticated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unauthenticated gh must leave the default alone; CODEOWNERS then goes."""
    _patch_subprocess_run_output(monkeypatch, returncode=1)

    assert pre_prompt.get_codeowner_username("") == ""


def test_version_pins_to_the_latest_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_subprocess_run_output(monkeypatch, stdout="v1.2.3\n")

    assert pre_prompt.get_latest_cookiepyrate_version("main") == "v1.2.3"


def test_version_falls_back_to_the_ref_and_says_so(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _patch_subprocess_run_output(monkeypatch, stdout="")

    assert pre_prompt.get_latest_cookiepyrate_version("main") == "main"
    assert "no release tag found" in capsys.readouterr().err


@pytest.mark.parametrize(
    "error", [FileNotFoundError("gh"), subprocess.TimeoutExpired("gh", timeout=5)]
)
def test_a_missing_or_slow_command_falls_back(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def raise_error(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise error

    monkeypatch.setattr(subprocess, "run", raise_error)

    assert pre_prompt._run_command(["gh", "api", "user"], default="fallback") == "fallback"


def _patch_subprocess_run_output(
    monkeypatch: pytest.MonkeyPatch, stdout: str = "", returncode: int = 0
) -> list[list[str]]:
    commands: list[list[str]] = []

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    return commands
