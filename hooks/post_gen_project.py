from pathlib import Path
import shutil


def remove_dockerfile_when_not_required() -> None:
    keep_dockerfile = "{{ cookiecutter.dockerfile_template }}".lower()
    if keep_dockerfile != "y":
        dockerfile = Path.cwd() / "Dockerfile"
        if dockerfile.exists():
            dockerfile.unlink()


def add_license_file() -> None:
    license_choice = "{{ cookiecutter.license }}"
    license_src = Path(__file__).parent / ".." / "licenses" / license_choice
    license_dst = Path.cwd() / "LICENSE"

    if license_src.exists():
        shutil.copyfile(license_src, license_dst)

if __name__ == "__main__":
    remove_dockerfile_when_not_required()
    add_license_file()
