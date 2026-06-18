# Makefile for QA checks (lint, format, type-check, tests) and tasks (build, clean, run)

.PHONY: qa lint format typecheck test clean run build version {% if cookiecutter.with_docs %}docs{% endif %} {% if cookiecutter.with_dockerfile %}dockerimage{% endif %}
.ONESHELL: version

# Default target
qa: lint format typecheck
	@printf "\033[92m[QA] All checks passed successfully.\033[0m\n"

lint:
	@printf "\n\033[1;34mRunning Ruff Linter\033[0m\n"
	uvx ruff check --fix

format:
	@printf "\n\033[1;34mRunning Ruff Format\033[0m\n"
	uvx ruff format

typecheck:
	@printf "\n\033[1;34mRunning Mypy\033[0m\n"
	uv run mypy

test:
	@printf "\n\033[1;34mRunning Pytest\033[0m\n"
	uv run pytest

{% if cookiecutter.with_docs %}
docs:
	@printf "\n\033[1;34mBuilding the documentation\033[0m\n"
	uv sync --group docs
	uv run mkdocs build -f ./docs/src/mkdocs.yml -d ../../dist/docs
{% endif %}
	
build: clean {% if cookiecutter.with_docs %}docs{% endif %}
	uv sync --all-groups
	uv run python -m build
	uv export --no-emit-project --no-hashes --no-header --no-annotate --no-dev --format requirements-txt > "dist/requirements.txt"

{% if cookiecutter.with_dockerfile %}
dockerimage: build
	@printf "\n\033[1;34mBuilding the docker image\033[0m\n"
	docker build -f Dockerfile -t {{ cookiecutter.repo_name }}:latest . --platform="linux/amd64"
{% endif %}

clean:
	@printf "\n\033[1;34mCleaning build and cache artifacts\033[0m\n"
	rm -rf dist build .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name '__pycache__' -exec rm -rf {} +
{% if cookiecutter.cli_command %}
run:
	env $$(grep -v '^#' .env | xargs) uv run {{ cookiecutter.cli_command }}
{% endif %}
