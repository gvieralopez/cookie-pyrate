import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_git_config(key: str, default: str) -> str:
    return _run_command(["git", "config", "--global", key], default=default)


def get_latest_cookiepyrate_version(fallback_ref: str) -> str:
    tag = _run_command(["git", "describe", "--tags", "--match", "v*", "--abbrev=0"], default="")
    if not tag:
        sys.stderr.write(f"Warning: no release tag found; pinning workflows to '{fallback_ref}'.\n")
        return fallback_ref
    return tag


def get_codeowner_username(default: str) -> str:
    return _run_command(["gh", "api", "user", "--jq", ".login"], default=default)


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, encoding="utf-8", timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except (OSError, subprocess.SubprocessError):
        return default


if __name__ == "__main__":
    config_path = Path("cookiecutter.json")
    defaults = json.loads(config_path.read_text(encoding="utf-8"))
    updates = {
        "author_name": get_git_config("user.name", defaults["author_name"]),
        "author_email": get_git_config("user.email", defaults["author_email"]),
        "codeowner_username": get_codeowner_username(defaults["codeowner_username"]),
        "year": str(datetime.now().year),
        "__cookiepyrate_version": get_latest_cookiepyrate_version(
            defaults["__cookiepyrate_version"]
        ),
    }
    defaults.update(updates)
    config_path.write_text(json.dumps(defaults, indent=4, ensure_ascii=False), encoding="utf-8")
