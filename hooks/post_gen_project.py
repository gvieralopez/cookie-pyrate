import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTEXT: dict[str, Any] = json.loads(r"""{{ cookiecutter | jsonify }}""")


def remove_dockerfile_when_not_required() -> None:
    if not CONTEXT["with_dockerfile"]:
        _remove_file(Path.cwd() / "Dockerfile")


def remove_precommitconfig_when_not_required() -> None:
    if not CONTEXT["with_precommit"]:
        _remove_file(Path.cwd() / ".pre-commit-config.yaml")


def remove_docs_when_not_required() -> None:
    if not CONTEXT["with_docs"]:
        _remove_folder(Path.cwd() / "docs")


def remove_ci_cd_pipeline_when_not_required() -> None:
    if CONTEXT["ci_cd_pipeline"] == "None":
        _remove_folder(Path.cwd() / ".github")


def add_license_file() -> None:
    license_choice = str(CONTEXT["license"])
    licenses_dir = Path.cwd() / "_licenses"

    if license_choice.lower() == "none":
        _remove_folder(licenses_dir)
        return

    license_src = licenses_dir / license_choice
    license_dst = Path.cwd() / "LICENSE"

    if license_src.exists():
        shutil.copyfile(license_src, license_dst)
    else:
        license_404 = f"License: {license_choice} not found.\n\nPlease update this file"
        license_dst.write_text(license_404)

    _remove_folder(licenses_dir)


def create_uv_lockfile() -> None:
    # Cookiecutter deletes the generated project when a hook exits nonzero, so a
    # missing lockfile must never propagate out of here.
    try:
        _write_uv_lockfile()
    except RuntimeError as error:
        logger.warning("%s.\nRun `uv lock` in the generated project.", error)


def _remove_folder(dir_path: Path) -> None:
    if dir_path.exists():
        shutil.rmtree(dir_path)


def _remove_file(file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink()


def _write_uv_lockfile() -> None:
    if (uv := shutil.which("uv")) is None:
        raise RuntimeError("uv was not found")
    try:
        result = subprocess.run(
            [uv, "lock"], check=False, capture_output=True, text=True, timeout=120
        )
    except subprocess.SubprocessError as error:
        raise RuntimeError(f"`uv lock` did not finish ({error})") from error
    if result.returncode != 0 or not (Path.cwd() / "uv.lock").exists():
        raise RuntimeError(f"`uv lock` failed:\n{(result.stderr or result.stdout).strip()}")


if __name__ == "__main__":
    remove_dockerfile_when_not_required()
    remove_precommitconfig_when_not_required()
    remove_docs_when_not_required()
    remove_ci_cd_pipeline_when_not_required()
    add_license_file()
    create_uv_lockfile()
