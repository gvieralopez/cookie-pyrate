# Makefile for QA checks (lint, format, type-check, tests) and tasks (build, clean, run)

.PHONY: qa lint format typecheck test clean run build version versionupdate
.ONESHELL: version versionupdate

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

build: clean
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
	@TAGS="final rc beta alpha"
	@ACTIONS="major minor patch tag"
	@CURRENT_VERSION=`bumpver update --dry --patch 2>&1 | grep -oP "Old Version.*" | awk -F ': ' '{print $$2}'`
	@CURRENT_VERSION_TAG=`bumpver update --dry --patch 2>&1 | grep -oP "Old Version.*" | awk -F '-' '{print $$2}' | grep -oP "(rc|beta|alpha)"`
	@CURRENT_VERSION_HAS_TAG=`if [ -n "$$CURRENT_VERSION_TAG" ]; then echo "true"; else echo "false"; fi`
	@CURRENT_VERSION_TAG_PRIORITY=`if $$CURRENT_VERSION_HAS_TAG; then echo $$TAGS | sed 's/\s/\n/g' | grep -n $$CURRENT_VERSION_TAG | cut -d: -f1; else echo 5; fi`
	@AVAILABLE_VERSION_UPD_ACTIONS=`if $$CURRENT_VERSION_HAS_TAG; then echo 4; else echo 3; fi;`

	print_menu() {
		printf "$$1\n\n"
		for i in $$(seq 1 $$2); do
			ARGI="$$((i+3))"
			printf "$$i) $${!ARGI}\n"
		done
		echo
		read -p "Enter your choice [default $$3]: " choice;
		choice=$${choice:-$$3};
		if [ "$$choice" -ge 1 ] && [ "$$choice" -le "$$2" ]; then
			return "$$choice"
		else
			echo "Invalid choice. Please select a valid option." >&2
			exit 1
		fi
	}

	@printf "Current version: $$CURRENT_VERSION\n\n"

	print_menu "What type of version bump would you like to perform?" $$AVAILABLE_VERSION_UPD_ACTIONS 3 "Major" "Minor" "Patch" "Tag"
	action_index=$$?

	@DEFAULT_TAG_INDEX=`if [ "$$action_index" -eq "4" ]; then echo $$CURRENT_VERSION_TAG_PRIORITY; else echo 1; fi`
	@MAX_TAG_INDEX=`if [ "$$action_index" -eq "4" ]; then echo $$CURRENT_VERSION_TAG_PRIORITY; else echo 4; fi`
	print_menu "Select the tag type:" $$MAX_TAG_INDEX $$DEFAULT_TAG_INDEX "Stable (no tag)" "Release Candidate" "Beta" "Alpha"
	tag_index=$$?

	@VERSION_TAG=`echo $$TAGS | sed 's/\s/\n/g' | sed -n "$$tag_index"p`
	@VERSION_TYPE=`echo $$ACTIONS | sed 's/\s/\n/g' | sed -n "$$action_index"p`

	$(MAKE) --no-print-directory versionupdate VERSION_TYPE=$$VERSION_TYPE VERSION_TAG=$$VERSION_TAG

versionupdate:
	@CURRENT_VERSION_TAG=`bumpver update --dry --patch 2>&1 | grep -oP "Old Version.*" | awk -F '-' '{print $$2}' | grep -oP "(rc|beta|alpha)"`
	if [ "$$VERSION_TYPE" == "tag" ]; then \
		if [ "$$VERSION_TAG" == "$$CURRENT_VERSION_TAG" ]; then \
			bumpver update --tag-num -n; \
		else \
			bumpver update --tag $$VERSION_TAG; \
		fi; \
		exit 0; \
	fi;

	bumpver update --$$VERSION_TYPE --tag $$VERSION_TAG


