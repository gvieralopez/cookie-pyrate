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

### Building the Project

```bash
make build
```

Generates a distribution package in the `dist/` directory.

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
git init  # if you haven't already
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
