# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Quick Start

### Prerequisites
- [uv](https://docs.astral.sh/uv/) - Python package manager

### Installation

```bash
uv sync
```

The generated `uv.lock` is committed for reproducible installations. Use `uv add`
and `uv remove` to change dependencies, then run `uv lock`. The lockfile is the
deployment source of truth; a separate `requirements.txt` is not generated.
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
