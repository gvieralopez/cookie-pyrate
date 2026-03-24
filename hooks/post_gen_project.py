import shutil
from pathlib import Path


def remove_dockerfile_when_not_required() -> None:
    if not {{cookiecutter.with_dockerfile}}:
        _remove_file(Path.cwd() / "Dockerfile")


def remove_precommitconfig_when_not_required() -> None:
    if not {{cookiecutter.with_precommit}}:
        _remove_file(Path.cwd() / ".pre-commit-config.yaml")


def remove_docs_when_not_required() -> None:
    if not {{cookiecutter.with_docs}}:
        _remove_folder(Path.cwd() / "docs")


def add_license_file() -> None:
    license_choice = "{{ cookiecutter.license }}"
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


def _remove_folder(dir_path: Path) -> None:
    if dir_path.exists():
        shutil.rmtree(dir_path)


def _remove_file(file_path: Path) -> None:
    if file_path.exists():
        file_path.unlink()


if __name__ == "__main__":
    remove_dockerfile_when_not_required()
    remove_precommitconfig_when_not_required()
    remove_docs_when_not_required()
    add_license_file()
