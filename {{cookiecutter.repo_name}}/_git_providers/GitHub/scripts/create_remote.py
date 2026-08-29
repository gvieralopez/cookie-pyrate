import argparse
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

REPO_NAME = "{{ cookiecutter.repo_name }}"
PYPROJECT = Path("pyproject.toml")
QA_WORKFLOW = Path(".github/workflows/qa.yml")
CODEOWNERS = Path("CODEOWNERS")
QA_CHECK = "qa"
DEFAULT_BRANCH = "main"
INSTALL_URLS = {"gh": "https://cli.github.com", "git": "https://git-scm.com/downloads"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and configure this project's remote.")
    parser.add_argument("--public", action="store_true", help="make the remote repository public")
    args = parser.parse_args()
    create_remote("public" if args.public else "private")


def create_remote(visibility: str) -> None:
    check_github_access()
    create_remote_repository(visibility)
    push_branch()
    protect_branch()
    print(f"\nRepository ready on branch '{DEFAULT_BRANCH}'.")


def check_github_access() -> None:
    if not _succeeds("gh", "auth", "status"):
        raise SystemExit("error: the GitHub CLI is not authenticated; run `gh auth login`")


def create_remote_repository(visibility: str) -> None:
    if _succeeds("git", "remote", "get-url", "origin"):
        print("· remote 'origin' already configured")
        return

    if _succeeds("gh", "repo", "view", REPO_NAME):
        url = _existing_remote_url()
        _output("git", "remote", "add", "origin", url)
        print(f"· linked the existing remote {url}")
        return

    description = tomllib.loads(PYPROJECT.read_text())["project"]["description"]
    creation = ["repo", "create", REPO_NAME, f"--{visibility}", "--description", description]
    _output("gh", *creation, "--source", ".", "--remote", "origin")
    print(f"· created the {visibility} repository {REPO_NAME}")


def push_branch() -> None:
    if _succeeds("git", "rev-parse", "--abbrev-ref", DEFAULT_BRANCH + "@{upstream}"):
        print(f"· branch '{DEFAULT_BRANCH}' already tracks a remote")
        return
    _output("git", "push", "--set-upstream", "origin", DEFAULT_BRANCH)
    print(f"· pushed '{DEFAULT_BRANCH}' and set it as upstream")


def protect_branch() -> None:
    repository = _output("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    policy = _branch_policy(_required_status_checks())
    with TemporaryDirectory() as directory:
        policy_file = Path(directory) / "policy.json"
        policy_file.write_text(json.dumps(policy, indent=2))
        endpoint = f"repos/{repository}/branches/{DEFAULT_BRANCH}/protection"
        result = _run("gh", "api", "--method", "PUT", endpoint, "--input", str(policy_file))

    if result.returncode != 0:
        print(
            f"warning: could not protect '{DEFAULT_BRANCH}' ({_details(result)}).\n"
            "Branch protection may need a paid plan; the repository is otherwise ready.",
            file=sys.stderr,
        )
        return
    print(f"· protected '{DEFAULT_BRANCH}'")


def _required_status_checks() -> dict[str, Any] | None:
    if not QA_WORKFLOW.is_file():
        return None
    return {"strict": True, "contexts": [QA_CHECK]}


def _branch_policy(status_checks: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "required_status_checks": status_checks,
        "required_pull_request_reviews": {
            "required_approving_review_count": 0,
            "require_code_owner_reviews": CODEOWNERS.is_file(),
            "dismiss_stale_reviews": True,
        },
        "required_conversation_resolution": True,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "enforce_admins": False,
        "restrictions": None,
    }


def _existing_remote_url() -> str:
    if _output("gh", "config", "get", "git_protocol") == "ssh":
        return _output("gh", "repo", "view", REPO_NAME, "--json", "sshUrl", "--jq", ".sshUrl")
    return _output("gh", "repo", "view", REPO_NAME, "--json", "url", "--jq", ".url") + ".git"


def _executable(program: str) -> str:
    path = shutil.which(program)
    if path is None:
        raise SystemExit(f"error: {program} is required; install it from {INSTALL_URLS[program]}")
    return path


def _run(program: str, *args: str) -> subprocess.CompletedProcess[str]:
    command = [_executable(program), *args]
    return subprocess.run(command, check=False, capture_output=True, text=True)


def _succeeds(program: str, *args: str) -> bool:
    return _run(program, *args).returncode == 0


def _output(program: str, *args: str) -> str:
    result = _run(program, *args)
    if result.returncode != 0:
        raise SystemExit(f"error: `{program} {' '.join(args)}` failed: {_details(result)}")
    return result.stdout.strip()


def _details(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip()


if __name__ == "__main__":
    main()
