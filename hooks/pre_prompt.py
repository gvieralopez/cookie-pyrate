import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(  # noqa: S603
            command, check=False, capture_output=True, text=True, encoding="utf-8", timeout=timeout
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


def get_current_year() -> str:
    return str(datetime.now().year)


def get_latest_cookiepyrate_version(default: str = "main") -> str:
    """Return the latest GitHub release tag, falling back to the default ref."""
    request = urllib.request.Request(
        "https://api.github.com/repos/gvieralopez/cookiepyrate/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "cookie-pyrate"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
            release = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return default

    if not isinstance(release, dict):
        return default

    tag_name = release.get("tag_name")
    return tag_name if isinstance(tag_name, str) and tag_name else default


def update_cookiecutter_json(updates: dict[str, str]) -> None:
    config_path = Path("cookiecutter.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data.update(updates)
    config_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    updates = {
        "author_name": get_author_name_from_git(default="Gustavo Viera López"),
        "author_email": get_author_email_from_git(default="gvieralopez@gmail.com"),
        "year": get_current_year(),
        "__cookiepyrate_version": get_latest_cookiepyrate_version(),
    }
    update_cookiecutter_json(updates)
