<div align="center">

<img src="assets/logo.svg" alt="" width="96">

# {{ cookiecutter.project_name }}

**{{ cookiecutter.project_description }}**

{% if cookiecutter.git_provider == "GitHub" -%}
[![QA](https://github.com/{{ cookiecutter.codeowner_username }}/{{ cookiecutter.repo_name }}/actions/workflows/qa.yml/badge.svg)](https://github.com/{{ cookiecutter.codeowner_username }}/{{ cookiecutter.repo_name }}/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/{{ cookiecutter.codeowner_username }}/{{ cookiecutter.repo_name }}?label=release)](https://github.com/{{ cookiecutter.codeowner_username }}/{{ cookiecutter.repo_name }}/releases/latest)
{% endif -%}
[![Python {{ cookiecutter.python_version }}+](https://img.shields.io/badge/python-{{ cookiecutter.python_version }}%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
{% if cookiecutter.license != "None" -%}
[![License: {{ cookiecutter.license }}](https://img.shields.io/badge/license-{{ cookiecutter.license | replace("-", "--") }}-green)](LICENSE)
{% endif -%}
<!-- Uncomment the badges that apply:
[![PyPI](https://img.shields.io/pypi/v/{{ cookiecutter.package_name }})](https://pypi.org/project/{{ cookiecutter.package_name }}/)
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/{{ cookiecutter.codeowner_username }}/{{ cookiecutter.repo_name }}/pkgs/container/{{ cookiecutter.repo_name }})
[![Docs](https://readthedocs.org/projects/{{ cookiecutter.repo_name }}/badge/?version=latest)](https://{{ cookiecutter.repo_name }}.readthedocs.io)
-->
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

[Quick start](#quick-start) · [Usage](#usage) · [Development](#development)

</div>

---

_What it does, for whom, and why it's different, in two or three sentences._

## Features

- _**Feature.** What it gives the user._

## Quick start

```bash
uv sync
```
{% if cookiecutter.cli_command %}
```bash
cp .env.example .env  # Configure as needed
uv run {{ cookiecutter.cli_command }}
```
{% endif %}
## Usage

_The smallest example that shows the main thing it does._

## Development

Setup, QA, docs and releases: [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.
{% if cookiecutter.license != "None" %}
## License

{{ cookiecutter.license }}: see [LICENSE](LICENSE).
{% endif %}
---

<sub>🚀 Project starter provided by [Cookie Pyrate {{ cookiecutter.__cookiepyrate_version }}](https://github.com/gvieralopez/cookie-pyrate/tree/{{ cookiecutter.__cookiepyrate_version }})</sub>
