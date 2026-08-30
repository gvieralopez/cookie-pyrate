# Makefile for QA checks (lint, format, type-check, tests) and tasks (build, clean, run)

.PHONY: qa lint format typecheck test clean run build version repo worktree {% if cookiecutter.with_docs %}docs{% endif %} {% if cookiecutter.with_dockerfile %}dockerimage{% endif %}
.ONESHELL: version

WORKTREE_SCRIPT_URL := https://raw.githubusercontent.com/gvieralopez/cookie-pyrate/main/scripts/worktree.sh

# Default target
qa: lint format typecheck
	@printf "\033[92m[QA] All checks passed successfully.\033[0m\n"

lint:
	@printf "\n\033[1;34mRunning Ruff Linter\033[0m\n"
	uv run ruff check --fix

format:
	@printf "\n\033[1;34mRunning Ruff Format\033[0m\n"
	uv run ruff format

typecheck:
	@printf "\n\033[1;34mRunning Mypy\033[0m\n"
	uv run mypy

test:
	@printf "\n\033[1;34mRunning Pytest\033[0m\n"
	uv run pytest

repo:
	@printf "\n\033[1;34mCreating the git repository\033[0m\n"
	@command -v git >/dev/null || { printf "error: git is required; install it from https://git-scm.com/downloads\n" >&2; exit 1; }
	@if [ -e .git ]; then echo "· local repository already initialised"; \
	else git init -q -b main && echo "· initialised the local repository"; fi
	@if git rev-parse --verify -q HEAD >/dev/null; then echo "· initial commit already present"; \
	else git add --all && git commit -q -m "Initial commit" && echo "· created the initial commit"; fi
{% if cookiecutter.git_provider != "None" %}	uv run python scripts/create_remote.py $(REPO_ARGS)
{% endif %}

worktree:
	@if ! command -v curl >/dev/null || ! command -v bash >/dev/null; then printf "error: curl and bash are required\n" >&2; exit 1; fi
	@bash -o pipefail -c 'curl --fail --silent --show-error --location "$(WORKTREE_SCRIPT_URL)" | bash'
{% if cookiecutter.with_docs %}
docs:
	@printf "\n\033[1;34mBuilding the documentation\033[0m\n"
	uv run --group docs mkdocs build -f ./docs/src/mkdocs.yml -d ../../dist/docs
{% endif %}
	
build: clean {% if cookiecutter.with_docs %}docs{% endif %}
	uv build

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
