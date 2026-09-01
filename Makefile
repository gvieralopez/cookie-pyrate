# Makefile for QA checks (lint, format, tests) on the template repository itself.
#
# `--config pyproject.toml` pins ruff to this file: without it ruff walks up from
# the shipped git-provider scripts and fails parsing the templated pyproject.toml.

.PHONY: qa lint format test

# Default target
qa: lint format test
	@printf "\033[92m[QA] All checks passed successfully.\033[0m\n"

lint:
	@printf "\n\033[1;34mRunning Ruff Linter\033[0m\n"
	uv run ruff check --config pyproject.toml --fix

format:
	@printf "\n\033[1;34mRunning Ruff Format\033[0m\n"
	uv run ruff format --config pyproject.toml

test:
	@printf "\n\033[1;34mRunning Pytest\033[0m\n"
	uv run pytest
