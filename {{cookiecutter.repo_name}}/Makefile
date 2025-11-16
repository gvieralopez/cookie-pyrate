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
	uv run mypy .

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

run:
	env $$(grep -v '^#' .env | xargs) uv run {{ cookiecutter.cli_command }}

version:
	# Usage:
	#
	# make version [VERSION_TYPE=<major|minor|patch|tag> VERSION_TAG=<final|rc|beta|alpha> DRY=<0|1|false|true>]
	#
	# Examples:
	#
	# make version											# Run interactively
	# make version DRY=1									# Run interactively in dry mode (no changes)
	#
	# make version VERSION_TYPE=minor VERSION_TAG=beta		# Directly bump minor version and set tag to beta
	# make version VERSION_TYPE=patch VERSION_TAG=final		# Directly bump patch version with no tag
	# make version VERSION_TYPE=tag VERSION_TAG=beta		# Directly bump tag version to beta or increasing tag number if already on beta
	#
	# Errors when:
	# - VERSION_TYPE is not one of: major, minor, patch, tag
	# - VERSION_TAG is not one of: final, rc, beta, alpha
	# - VERSION_TYPE=tag but current version is already stable or VERSION_TAG is lower than current tag (e.g. trying to set beta tag when current version is rc)

	@TAGS="final rc beta alpha"
	@ACTIONS="major minor patch tag"
	@CURRENT_VERSION=`uv run bumpver update --dry --patch 2>&1 | grep -oE "Old Version.*" | awk -F ': ' '{print $$2}'`
	@CURRENT_VERSION_TAG=`echo "$$CURRENT_VERSION" | grep -oE "(rc|beta|alpha)"`
	@CURRENT_VERSION_HAS_TAG=`if [ -n "$$CURRENT_VERSION_TAG" ]; then echo "true"; else echo "false"; fi`
	@CURRENT_VERSION_TAG_LEVEL=`if $$CURRENT_VERSION_HAS_TAG; then echo $$TAGS | sed 's/\s/\n/g' | grep -n $$CURRENT_VERSION_TAG | cut -d: -f1; else echo 5; fi`
	@AVAILABLE_VERSION_UPD_ACTIONS=`if $$CURRENT_VERSION_HAS_TAG; then echo 4; else echo 3; fi;`
	@DRY_RUN=`if [ "$${DRY:-false}" == "true" ] || [ "$$DRY" == "1" ]; then echo "true"; else echo "false"; fi;`
	@DRY_FLAG=`if $$DRY_RUN; then echo "--dry"; else echo ""; fi`

	print_menu() {
		printf "$$1\n\n"																		# Print the prompt
		for i in $$(seq 1 $$2); do ARGI="$$((i+3))"; printf "$$i) $${!ARGI}\n"; done			# Print the options
		echo; read -p "Enter your choice [default $$3]: " choice; echo;	choice=$${choice:-$$3}; # Read user input with default
		if [ "$$choice" -ge 1 ] && [ "$$choice" -le "$$2" ]; then return "$$choice"; fi			# Return the selected option index
		echo "Invalid choice. Please select a valid option." >&2 && exit 1						# Exit on invalid input
	}

	if $$DRY_RUN; then printf "\033[93m[DRY RUN] No changes will be made.\033[0m\n\n"; fi
	if [ -z "$$VERSION_TYPE" ] || [ -z "$$VERSION_TAG" ]; then printf "Current version: $$CURRENT_VERSION\n\n"; fi

	@VALID_ACTIONS=`echo $$ACTIONS | cut -d' ' -f1-"$$AVAILABLE_VERSION_UPD_ACTIONS"`
	if [ -z "$$VERSION_TYPE" ]; then
		print_menu "What type of version bump would you like to perform?" $$AVAILABLE_VERSION_UPD_ACTIONS 3 "Major" "Minor" "Patch" "Tag"
		action_index=$$?
		@VERSION_TYPE=`echo $$VALID_ACTIONS | sed 's/\s/\n/g' | sed -n "$$action_index"p`
	else
		if ! echo "$$VALID_ACTIONS" | grep -qw "$$VERSION_TYPE"; then echo "Invalid VERSION_TYPE '$$VERSION_TYPE'. Must be one of: $$VALID_ACTIONS" >&2; exit 1; fi
	fi

	MAX_TAG_INDEX=`if [ "$$VERSION_TYPE" == "tag" ]; then echo $$CURRENT_VERSION_TAG_LEVEL; else echo 4; fi`
	@VALID_TAGS=`echo $$TAGS | cut -d' ' -f1-"$$MAX_TAG_INDEX"`
	if [ -z "$$VERSION_TAG" ]; then
		DEFAULT_TAG_INDEX=`if [ "$$VERSION_TYPE" == "tag" ]; then echo $$CURRENT_VERSION_TAG_LEVEL; else echo 1; fi`
		print_menu "Select the tag type:" $$MAX_TAG_INDEX $$DEFAULT_TAG_INDEX "Stable (no tag)" "Release Candidate" "Beta" "Alpha"
		tag_index=$$?
		@VERSION_TAG=`echo $$VALID_TAGS | sed 's/\s/\n/g' | sed -n "$$tag_index"p`
	else
		if ! echo "$$VALID_TAGS" | grep -qw "$$VERSION_TAG"; then echo "Invalid VERSION_TAG '$$VERSION_TAG'. Must be one of: $$VALID_TAGS" >&2; exit 1; fi
	fi

	if [ "$$VERSION_TYPE" == "tag" ]; then \
		if [ "$$VERSION_TAG" == "$$CURRENT_VERSION_TAG" ]; then \
			uv run bumpver update $$DRY_FLAG --tag-num -n; \
		else \
			uv run bumpver update $$DRY_FLAG --tag $$VERSION_TAG; \
		fi; \
		exit 0; \
	fi;

	uv run bumpver update $$DRY_FLAG --$$VERSION_TYPE --tag $$VERSION_TAG
