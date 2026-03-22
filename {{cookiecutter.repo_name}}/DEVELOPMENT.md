# Development Guide

## Prerequisites

Before developing this project, ensure you have the following installed:

### 1. [uv](https://docs.astral.sh/uv/)  
Python project and environment management.  
Install: [uv docs](https://docs.astral.sh/uv/getting-started/installation/)

### 2. [make](https://www.gnu.org/software/make/)  
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

{% if cookiecutter.with_dockerfile %}
### 3. [Docker](https://docs.docker.com/get-docker/)  
For building and running containerized deployments.
{% endif %}

## Installation in development mode

Install all dependencies including development tools:

```bash
uv sync --all-groups
```

This creates a `.venv` folder and installs everything from `pyproject.toml`.

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

### Updating Project Version

```bash
make version
```

Interactively prompts you to select the version update type (major, minor, patch, tag) 
and automatically updates the version accordingly.

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
pre-commit install
```

Checks will now run automatically on every commit.

### Manual Execution

Trigger all hooks manually:

```bash
pre-commit run --all-files
```

This is equivalent to running `make qa`.
{% endif %}
