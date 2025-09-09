# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## 🚀 Prerequisites

Make sure you have the following tools installed before working with the project:

* [**uv**](https://docs.astral.sh/uv/) → Python project and environment management
* [**make**](https://www.gnu.org/software/make/) → run common project tasks via the `Makefile`
{% if cookiecutter.with_dockerfile %}* [**docker**](https://docs.docker.com/get-docker/) → build and run containerized deployments{% endif %}

## ⚡ Getting Started

Install dependencies into a local virtual environment:

```bash
uv sync --all-groups
```

This will create a `.venv` folder and install everything declared in `pyproject.toml`.

Then, you can activate the environment manually depending on your shell/OS:

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

## 🛠️ Usage

### Set up your environment variables  

Make a copy of the `.env.example` file and edit it with your settings:

```bash
cp .env.example .env
```

### Run the project

Start the main entry-point of your package with:

```bash
make run
```

That’s it! Your project should now be up and running with your configured environment.

## 📦 Tools for Developers

Common development tasks are wrapped in the `Makefile` for convenience.

### Linting, Formatting, and Type Checking

```bash
make qa
```

Runs **Ruff** for linting and formatting, and **Mypy** for type checking.

### Running Unit Tests

Before running tests, override any required environment variables in the `.env.test` file.

```bash
make test
```

Executes the test suite using **Pytest**.

### Building the Project

```bash
make build
```

Generates a distribution package inside the `dist/` directory.

### Cleaning Up

```bash
make clean
```

Removes build artifacts, caches, and temporary files to keep your project directory clean.

{% if cookiecutter.with_dockerfile %}### Building a Docker image

```bash
make dockerimage
```

Generates a docker image with the package inside the `dist/` directory already installed.{% endif %}
{% if cookiecutter.with_precommit %}
### Pre-Commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks before each commit.
The hooks wrap the same `make qa` tasks (Ruff + Mypy).

#### Setup

Next, we assume you already have a git repository created on this folder. If you haven't, just run:

```bash
git init
```

Then, install the hooks once:

```bash
pre-commit install
```

After that, checks will run automatically whenever you commit.

#### Manual Run

You can also trigger all hooks manually:

```bash
pre-commit run --all-files
```

which is equivalent to `make qa`.{% endif %}

## 🤝 Contributing

Contributions are welcome!
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
