from pathlib import Path

def remove_dockerfile_when_not_required():
    keep_dockerfile = "{{ cookiecutter.dockerfile_template }}".lower()
    if keep_dockerfile != "y":
        dockerfile = Path.cwd() / "Dockerfile"
        if dockerfile.exists():
            dockerfile.unlink()

if __name__ == "__main__":
    remove_dockerfile_when_not_required()
