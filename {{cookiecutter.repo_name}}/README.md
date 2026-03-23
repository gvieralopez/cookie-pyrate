# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Quick Start

### Prerequisites
- [uv](https://docs.astral.sh/uv/) - Python package manager

### Installation

```bash
uv sync --all-groups
```
{% if cookiecutter.cli_command %}
### Run

```bash
cp .env.example .env  # Configure as needed
uv run {{ cookiecutter.cli_command }}
```
{% endif %}
## Development

For setup, testing, building, and other development tasks, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Contributions are welcome!  
Please ensure all QA checks and tests pass before opening a pull request.

---

<sub>🚀 Project starter provided by [Cookie Pyrate](https://github.com/gvieralopez/cookie-pyrate)</sub>
