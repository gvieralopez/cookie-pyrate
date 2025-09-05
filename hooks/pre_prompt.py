import json
import subprocess
from pathlib import Path


def get_git_config(key, default=""):
    try:
        result = subprocess.run(
            ["git", "config", "--global", key],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except subprocess.SubprocessError:
        return default


if __name__ == "__main__":
    author_name = get_git_config("user.name", "Gustavo Viera López")
    email = get_git_config("user.email", "gvieralopez@gmail.com")

    config = Path("cookiecutter.json")

    data = json.loads(config.read_text())
    data["author_name"] = author_name
    data["email"] = email

    config.write_text(json.dumps(data, indent=4))
