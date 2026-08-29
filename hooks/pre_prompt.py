import json
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

LATEST_PYRATE_RELEASE_URL = "https://api.github.com/repos/gvieralopez/cookie-pyrate/releases/latest"
CONFIG_PATH = Path("cookiecutter.json")


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


def get_codeowner_username(default: str) -> str:
    return _run_command(["gh", "api", "user", "--jq", ".login"], default=default)


def read_cookiecutter_json() -> dict[str, Any]:
    config: dict[str, Any] = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return config


def write_cookiecutter_json(config: dict[str, Any], updates: dict[str, str]) -> None:
    config.update(updates)
    CONFIG_PATH.write_text(json.dumps(config, indent=4, ensure_ascii=False), encoding="utf-8")


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, encoding="utf-8", timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except (OSError, subprocess.SubprocessError):
        return default


if __name__ == "__main__":
    defaults = read_cookiecutter_json()
    updates = {
        "author_name": get_git_config("user.name", defaults["author_name"]),
        "author_email": get_git_config("user.email", defaults["author_email"]),
        "codeowner_username": get_codeowner_username(defaults["codeowner_username"]),
        "year": str(datetime.now().year),
        "__cookiepyrate_version": get_latest_cookiepyrate_version(
            LATEST_PYRATE_RELEASE_URL, defaults["__cookiepyrate_version"]
        ),
    }
    write_cookiecutter_json(defaults, updates)
