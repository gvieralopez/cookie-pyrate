import os
import re
import tomllib
from pathlib import Path


def check_version_in_all_locations(project_dir: Path, version: str):
    pyproject = project_dir / "pyproject.toml"
    pyproject_content = tomllib.loads(pyproject.read_text())

    assert "tool" in pyproject_content
    assert "ebump" in pyproject_content["tool"]

    patterns = pyproject_content["tool"]["ebump"]["patterns"]

    for file, file_patterns in patterns.items():
        file_path = project_dir / file
        assert file_path.exists(), f"File {file} does not exist"

        for pattern in file_patterns:
            file_content = file_path.read_text()
            replaced_pattern = pattern.replace("{version}", version)
            assert re.search(replaced_pattern, file_content, re.MULTILINE), (
                f"Pattern {replaced_pattern} not found in {file}"
            )


def run_version_target(
    project_dir: Path, version_type: str, version_tag: str, should_fail: bool = False
) -> None:
    exit_status = os.system(f"cd {project_dir} && uvx ebump {version_type} {version_tag}")  # noqa: S605
    assert not should_fail or exit_status != 0, "Command was expected to fail but succeeded"
    assert should_fail or exit_status == 0, f"Command failed with exit status {exit_status}"


def test_version(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")


def test_patch_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "patch", "final")
    check_version_in_all_locations(default_project, "0.1.1")


def test_minor_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "minor", "final")
    check_version_in_all_locations(default_project, "0.2.0")


def test_major_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "major", "final")
    check_version_in_all_locations(default_project, "1.0.0")


def test_minor_beta_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "minor", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta0")


def test_tag_beta_num_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "minor", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta0")
    run_version_target(default_project, "tag", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta1")


def test_new_tag_bump(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "minor", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta0")
    run_version_target(default_project, "tag", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta1")
    run_version_target(default_project, "tag", "rc")
    check_version_in_all_locations(default_project, "0.2.0-rc0")


def test_bump_tag_from_stable_mode(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "tag", "beta")
    check_version_in_all_locations(default_project, "0.1.0-beta1")


def test_bump_stable_in_tag_mode(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "minor", "beta")
    check_version_in_all_locations(default_project, "0.2.0-beta0")
    run_version_target(default_project, "tag", "final")
    check_version_in_all_locations(default_project, "0.2.0")


def test_bump_with_invalid_tag(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "patch", "beta")
    check_version_in_all_locations(default_project, "0.1.1-beta0")
    run_version_target(default_project, "tag", "alpha", should_fail=True)
    check_version_in_all_locations(default_project, "0.1.1-beta0")


def test_invalid_version_type(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "invalid_type", "final", should_fail=True)
    check_version_in_all_locations(default_project, "0.1.0")


def test_invalid_version_tag(default_project: Path) -> None:
    check_version_in_all_locations(default_project, "0.1.0")
    run_version_target(default_project, "patch", "invalid_tag", should_fail=True)
    check_version_in_all_locations(default_project, "0.1.0")
