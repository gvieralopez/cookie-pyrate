{%- set owner = cookiecutter.codeowner_username | trim -%}
{%- set has_owner = cookiecutter.git_provider == "GitHub" and owner and owner | lower != "none" -%}
{%- set repo = cookiecutter.repo_name -%}
{%- set version = cookiecutter.__cookiepyrate_version -%}
<div align="center">

<img src="{% if cookiecutter.with_docs %}docs/src/docs/images/logo.svg{% else %}assets/logo.svg{% endif %}" alt="" width="96">

# {{ cookiecutter.project_name }}

**{{ cookiecutter.project_description }}**

{% if has_owner -%}
[![QA](https://github.com/{{ owner }}/{{ repo }}/actions/workflows/qa.yml/badge.svg)](https://github.com/{{ owner }}/{{ repo }}/actions/workflows/qa.yml)
[![Release](https://img.shields.io/github/v/release/{{ owner }}/{{ repo }}?label=release)](https://github.com/{{ owner }}/{{ repo }}/releases/latest)
{% endif -%}
[![Python {{ cookiecutter.python_version }}+](https://img.shields.io/badge/python-{{ cookiecutter.python_version }}%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
{% if cookiecutter.license != "None" -%}
[![License: {{ cookiecutter.license }}](https://img.shields.io/badge/license-{{ cookiecutter.license | replace("-", "--") }}-green)](LICENSE)
{% endif -%}
<!-- Uncomment the badges that apply:
[![PyPI](https://img.shields.io/pypi/v/{{ cookiecutter.package_name }})](https://pypi.org/project/{{ cookiecutter.package_name }}/)
{% if has_owner and cookiecutter.with_dockerfile -%}
[![Docker image](https://img.shields.io/badge/docker-ghcr.io-2496ED?logo=docker&logoColor=white)](https://github.com/{{ owner }}/{{ repo }}/pkgs/container/{{ repo }})
{% endif -%}
{% if cookiecutter.with_docs -%}
[![Docs](https://readthedocs.org/projects/{{ repo }}/badge/?version=latest)](https://{{ repo }}.readthedocs.io)
{% endif -%}
-->
<br>
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

[Quick start](#quick-start) · [Usage](#usage) · {% if cookiecutter.with_docs %}[Documentation](#documentation) · {% endif %}[Development](#development)

</div>

---

_What it does, for whom, and why it's different, in two or three sentences._

## Features

- _**Feature.** What it gives the user._

## Quick start

```bash
{% if has_owner %}git clone https://github.com/{{ owner }}/{{ repo }}.git
cd {{ repo }}
{% endif %}uv sync
{%- if cookiecutter.cli_command %}
cp .env.example .env  # Configure as needed
uv run {{ cookiecutter.cli_command }}
{%- endif %}
```

<!-- Once published, the shortest way in:
pip install {{ cookiecutter.package_name }}
{%- if has_owner and cookiecutter.with_dockerfile %}
docker run ghcr.io/{{ owner }}/{{ repo }}
{%- endif %}
-->

## Usage

_The smallest example that shows the main thing it does._
{% if cookiecutter.with_docs %}
## Documentation

`make docs` builds the site into `dist/docs`. Once the repository is imported on Read the Docs, every push
publishes it there (see [DEVELOPMENT.md](DEVELOPMENT.md)).
{% endif %}
## Development

Setup, QA and releases: [DEVELOPMENT.md](DEVELOPMENT.md).

## Contributing

Issues and pull requests are welcome; `make qa` must pass.
{% if cookiecutter.license != "None" %}
## License

{{ cookiecutter.license }}: see [LICENSE](LICENSE).
{% endif %}
---

<sub>🚀 Project starter provided by [Cookie Pyrate {{ version }}](https://github.com/gvieralopez/cookie-pyrate/{% if version.startswith("v") %}releases/tag/{% else %}tree/{% endif %}{{ version }})</sub>
