import json
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

LATEST_PYRATE_RELEASE_URL = "https://api.github.com/repos/gvieralopez/cookiepyrate/releases/latest"
FALLBACK_PYRATE_VERSION_REF = "main"


def get_git_config(key: str, default: str) -> str:
    return _run_command(["git", "config", "--global", key], default=default)


def get_latest_cookiepyrate_version(release_url: str, fallaback_ref: str) -> str:
    try:
        with urllib.request.urlopen(release_url, timeout=5) as response:
            return str(json.load(response)["tag_name"])
    except Exception as error:
        sys.stderr.write(
            f"Warning: no release tag ({error}); pinning workflows to '{fallaback_ref}'.\n"
        )
        return fallaback_ref


def update_cookiecutter_json(updates: dict[str, str]) -> None:
    config_path = Path("cookiecutter.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data.update(updates)
    config_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, encoding="utf-8", timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except subprocess.SubprocessError:
        return default


if __name__ == "__main__":
    updates = {
        "author_name": get_git_config("user.name", "Gustavo Viera López"),
        "author_email": get_git_config("user.email", "gvieralopez@gmail.com"),
        "year": str(datetime.now().year),
        "__cookiepyrate_version": get_latest_cookiepyrate_version(
            LATEST_PYRATE_RELEASE_URL, FALLBACK_PYRATE_VERSION_REF
        ),
    }
    update_cookiecutter_json(updates)
