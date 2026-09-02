# Makefile for QA checks (lint, format, type-check, tests) on the template repository itself

.PHONY: qa lint format typecheck test

# Default target
qa: lint format typecheck test
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
