import os
import shutil
from pathlib import Path


def remove_dockerfile_when_not_required() -> None:
    keep_dockerfile = "{{ cookiecutter.dockerfile_template }}".lower()
    if keep_dockerfile != "y":
        dockerfile = Path.cwd() / "Dockerfile"
        if dockerfile.exists():
            dockerfile.unlink()


def add_license_file() -> None:
    license_choice = "{{ cookiecutter.license }}"

    if license_choice == "None":
        return
    
    # Cookiecutter sets this automatically
    template_dir = os.environ.get('COOKIECUTTER_TEMPLATE_DIR')
    license_src = Path(template_dir) / "licenses" / license_choice
    license_dst = Path.cwd() / "LICENSE"

    if license_src.exists():
        shutil.copyfile(license_src, license_dst)
    else:
        # Fallback for missing license template
        license_dst.write_text(
            f"License: {license_choice} not found in {license_src}\n\nPlease provide the license text."
        )

if __name__ == "__main__":
    remove_dockerfile_when_not_required()
    add_license_file()