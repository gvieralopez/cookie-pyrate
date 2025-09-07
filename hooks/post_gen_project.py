import os
import shutil
from pathlib import Path


def remove_dockerfile_when_not_required() -> None:
    keep_dockerfile = "{{ cookiecutter.dockerfile_template }}".lower()
    if keep_dockerfile != "y":
        dockerfile = Path.cwd() / "Dockerfile"
        if dockerfile.exists():
            dockerfile.unlink()

def remove_licenses_folder(licenses_dir: Path) -> None:
    if licenses_dir.exists():
        shutil.rmtree(licenses_dir)

def add_license_file() -> None:
    license_choice = "{{ cookiecutter.license }}"
    licenses_dir = Path.cwd() / "_licenses"

    if license_choice == "None":
        remove_licenses_folder(licenses_dir)
        return
    
    license_src = licenses_dir / license_choice
    license_dst = Path.cwd() / "LICENSE"
    
    if license_src.exists():
        shutil.copyfile(license_src, license_dst)
    else:
        # Fallback for missing license template
        license_dst.write_text(
            f"License: {license_choice} not found.\n\nPlease provide the license text."
        )
    
    remove_licenses_folder(licenses_dir)


if __name__ == "__main__":
    remove_dockerfile_when_not_required()
    add_license_file()