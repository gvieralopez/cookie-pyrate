import os
import re
from pathlib import Path

import tomllib


def check_version_in_all_locations(project_dir: Path, version: str):
    pyproject = project_dir / "pyproject.toml"
    pyproject_content = tomllib.loads(pyproject.read_text())

    assert "tool" in pyproject_content
    assert "bumpver" in pyproject_content["tool"]
    assert "file_patterns" in pyproject_content["tool"]["bumpver"]

    file_patterns = pyproject_content["tool"]["bumpver"]["file_patterns"]

    for file, patterns in file_patterns.items():
        file_path = project_dir / file
        assert file_path.exists(), f"File {file} does not exist"

        for pattern in patterns:
            file_content = file_path.read_text()
            pattern = pattern.replace("{version}", version)
            assert re.search(pattern, file_content, re.MULTILINE), (
                f"Pattern {pattern} not found in {file}"
            )


def run_version_target(
    project_dir: Path, version_type: str, version_tag: str, should_fail: bool = False
) -> None:
    exit_status = os.system(
        f"cd {project_dir} && make version VERSION_TYPE={version_type} VERSION_TAG={version_tag}"
    )
    assert not should_fail or exit_status != 0, (
        "Command was expected to fail but succeeded"
    )
    assert should_fail or exit_status == 0, (
        f"Command failed with exit status {exit_status}"
    )


def test_version(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")


def test_patch_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "patch", "final")
        check_version_in_all_locations(project_dir, "0.1.1")


def test_minor_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "minor", "final")
        check_version_in_all_locations(project_dir, "0.2.0")


def test_major_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "major", "final")
        check_version_in_all_locations(project_dir, "1.0.0")


def test_minor_beta_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "minor", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta0")


def test_tag_beta_num_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "minor", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta0")
        run_version_target(project_dir, "tag", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta1")


def test_new_tag_bump(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "minor", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta0")
        run_version_target(project_dir, "tag", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta1")
        run_version_target(project_dir, "tag", "rc")
        check_version_in_all_locations(project_dir, "0.2.0-rc0")


def test_bump_tag_in_stable_mode(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "tag", "beta", should_fail=True)
        check_version_in_all_locations(project_dir, "0.1.0")


def test_bump_stable_in_tag_mode(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "minor", "beta")
        check_version_in_all_locations(project_dir, "0.2.0-beta0")
        run_version_target(project_dir, "tag", "final")
        check_version_in_all_locations(project_dir, "0.2.0")


def test_bump_with_invalid_tag(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "patch", "beta")
        check_version_in_all_locations(project_dir, "0.1.1-beta0")
        run_version_target(project_dir, "tag", "alpha", should_fail=True)
        check_version_in_all_locations(project_dir, "0.1.1-beta0")


def test_invalid_version_type(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "invalid_type", "final", should_fail=True)
        check_version_in_all_locations(project_dir, "0.1.0")


def test_invalid_version_tag(project_generator) -> None:
    with project_generator() as project_dir:
        check_version_in_all_locations(project_dir, "0.1.0")
        run_version_target(project_dir, "patch", "invalid_tag", should_fail=True)
        check_version_in_all_locations(project_dir, "0.1.0")
