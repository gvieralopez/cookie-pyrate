import json
import subprocess
from pathlib import Path


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except subprocess.SubprocessError:
        return default


def _get_git_config(key: str, default: str) -> str:
    return _run_command(["git", "config", "--global", key], default=default)


def get_author_name_from_git(default: str) -> str:
    return _get_git_config("user.name", default)


def get_author_email_from_git(default: str) -> str:
    return _get_git_config("user.email", default)


def update_cookiecutter_json(updates: dict[str, str]) -> None:
    config_path = Path("cookiecutter.json")
    data = json.loads(config_path.read_text())
    data.update(updates)
    config_path.write_text(json.dumps(data, indent=4))


if __name__ == "__main__":
    updates = {
        "author_name": get_author_name_from_git(default="Gustavo Viera López"),
        "author_email": get_author_email_from_git(default="gvieralopez@gmail.com"),
    }
    update_cookiecutter_json(updates)
