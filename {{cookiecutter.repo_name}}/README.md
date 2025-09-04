# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

---

## 🚀 Prerequisites

Make sure you have the following tools installed:

- [uv](https://docs.astral.sh/uv/) (for Python project management)
- [make](https://www.gnu.org/software/make/) (for running project tasks)

---

## ⚡ Getting Started

Install dependencies into a local virtual environment:

```bash
uv sync --all-groups
```

This will create a `.venv` folder and install everything declared in `pyproject.toml`.

---

## 🛠️ Usage

### Set up your environment variables  

Make a copy of the `.env.example` file and edit it with your settings:

```bash
cp .env.example .env
```

### Run the project

Start the main entrypoint of your package with:

```bash
make run
```

That’s it! Your project should now be up and running with your configured environment.

---

## 📦 Tools for Developers

Common development tasks are wrapped in the `Makefile` for convenience:

### Linting & Formatting

```bash
make qa
```

Runs Ruff (lint + format) and Mypy type checks.

### Running Unit Tests

```bash
make test
```

Executes the test suite with Pytest.

### Building the Project

```bash
make build
```

Creates a distribution package inside `dist/`.

### Cleaning Up

```bash
make clean
```

Removes build artifacts, cache, and temporary files.

---

## 🤝 Contributing

Contributions are welcome!
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
