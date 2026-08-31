# Development Guide

## Prerequisites

Before developing this project, ensure you have the following installed:

### [uv](https://docs.astral.sh/uv/)  
Python project and environment management.  
Install: [uv docs](https://docs.astral.sh/uv/getting-started/installation/)

### [make](https://www.gnu.org/software/make/)  
Run common project tasks via the `Makefile`.

#### macOS  
```sh
xcode-select --install
```

#### Windows  
```powershell
choco install make
```

#### Linux
Usually pre-installed. If not:
```sh
sudo apt install build-essential   # Debian/Ubuntu
sudo dnf groupinstall "Development Tools"   # Fedora
```

### [git](https://git-scm.com/downloads)  
Version control, and what `make repo` uses to initialise the repository.
{% if cookiecutter.git_provider == "GitHub" %}
### [GitHub CLI](https://cli.github.com)  
Lets `make repo` create the GitHub remote and apply the branch policies.  
Authenticate once with `gh auth login`.
{% endif %}{% if cookiecutter.with_dockerfile %}
### [Docker](https://docs.docker.com/get-docker/)  
For building and running containerized deployments.
{% endif %}

## Installation in development mode

Install all dependencies including development tools:

```bash
uv sync
```

This creates a `.venv` folder and installs the project and default development
dependencies from `pyproject.toml` and the committed `uv.lock` file. After changing
dependencies, use `uv add`/`uv remove`, then run `uv lock` and commit the lockfile.

Activate the environment:

* **Linux / macOS (bash/zsh):**
  ```bash
  source .venv/bin/activate
  ```

* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

* **Windows (cmd.exe):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

## Development Tasks

All tasks are defined in the `Makefile` for convenience.

### Linting, Formatting, and Type Checking

```bash
make qa
```

Runs **Ruff** for linting and formatting, and **Mypy** for type checking.

### Running Unit Tests

Before running tests, configure environment variables in `.env.test` if needed.

```bash
make test
```

Executes the test suite using **Pytest**.

### Creating the Repository

Initialise the local repository and create its first commit on `main`:

```bash
make repo
```
{% if cookiecutter.git_provider == "GitHub" %}
The same command then creates the GitHub remote, pushes `main`, and applies the branch
policies. The remote is private by default; to make it public:

```bash
make repo REPO_ARGS=--public
```

`main` is protected: pull requests need one approval including the code owner, all
conversations resolved, the branch up to date with `main`, linear history, and the `qa`
check green. Force pushes and branch deletion are rejected.

The local steps need only git; the remote ones need the
[GitHub CLI](https://cli.github.com) authenticated with `gh auth login`. Without it the
local repository is still created and nothing is pushed.
{% else %}
No remote is configured: add one yourself with `git remote add origin <url>`.
{% endif %}
The command is safe to re-run: each step is skipped if it is already done, so an
interrupted run can be finished by running it again.

### Migrating to Git Worktrees

Migrate the repository to a shared bare-repository layout:

```bash
make worktree
```

This creates `.bare` for the shared Git history and a directory for the current
branch. If the current branch is not the remote default branch, a second directory
is created for that default branch. The converted repository root contains only
`.bare`, the `.git` pointer, and the worktree directories. Before converting, it
copies the complete original repository, including `.git`, to a sibling directory
named `<repo-name>-legacy-bak`, restores the original files to the current branch
worktree, and refuses to overwrite an existing backup or worktree layout. If the
migration fails, the original repository is restored and the temporary backup is
removed.

### Building the Project

```bash
make build
```

Generates a distribution package in the `dist/` directory.
{% if cookiecutter.git_provider == "GitHub" %}
### Releasing

Every push to `main` that passes QA cuts a release: the version is finalised, tagged,
published as a GitHub release, and `main` is bumped to the next prerelease. Nothing is
uploaded to PyPI unless you opt in.

#### Publishing to PyPI

Only relevant if you distribute this project as a package. Set up Trusted Publishing so
no API token has to be stored as a secret:

1. Go to <https://pypi.org/manage/account/publishing/>
2. Under "Add a new pending publisher," choose GitHub Actions
3. Fill in the workflow name `release.yml` and the environment name `pypi`
4. Save. PyPI will now trust publish requests coming from that workflow.

Then, in `.github/workflows/release.yml`, add `id-token: write` to `permissions`, flip
the two toggles, and point the deployment environment at the project:

```yaml
    permissions:
      contents: write
      id-token: write
    with:
      cookie-pyrate-ref: ...
      attach-distribution: true
      publish-to-pypi: true
      pypi-project-url: https://pypi.org/project/{{ cookiecutter.package_name }}/
```

Without `id-token: write` the whole workflow fails to start, so add it in the same edit.
`attach-distribution` also attaches the built artifacts to the GitHub release. A failed
upload leaves the GitHub release in place and only emits a warning.

The remaining toggles in that file are `create-github-release`, which cuts the GitHub
release, and `prepare-next-version`, which bumps `main` to the next prerelease once the
release is out. Both are on by default and can be turned off on their own.
{% endif %}
### Cleaning Up

```bash
make clean
```

Removes build artifacts, caches, and temporary files.

{% if cookiecutter.with_dockerfile %}
### Building a Docker Image

```bash
make dockerimage
```

Generates a Docker image with the package pre-installed and ready to use.
{% endif %}

{% if cookiecutter.with_docs %}
### Building Documentation

```bash
make docs
```

Generates project documentation in the `dist/docs` folder.

Documentation is also automatically included when running `make build`.
{% endif %}

{% if cookiecutter.with_precommit %}
## Pre-Commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks automatically before each commit.

### Setup

Install the hooks:

```bash
make repo  # if you haven't already
uv run pre-commit install
```

Checks will now run automatically on every commit.

### Manual Execution

Trigger all hooks manually:

```bash
uv run pre-commit run --all-files
```

This is equivalent to running `make qa`.
{% endif %}
