# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

Style, conventions and tooling for this project.

## Layout

1. `src/{{ cookiecutter.package_name }}/{models,errors,main}.py`; sub-domains as sub-packages (e.g. `validation/`).
2. Data structures live in `models.py`, error types in `errors.py`.
3. Order functions top-down — callers before callees, private helpers (`_name`) last — so the most important read first.
4. Do not write docstrings or descriptive comments unless the asks for them or they provide context that cannot be inferred by reading the code.

## Design

1. Data structures are immutable dataclasses: `@dataclass(frozen=True)` (add `slots=True` when it fits).
2. Avoid default arguments in functions.
3. If a function takes a bool that drives an `if`, prefer splitting into two functions (one delegating to the other, or factoring out shared logic when it saves ≥2 LoC).

## Hygiene

1. No commented-out code.
2. Every `# noqa` must specify a rule code, e.g. `# noqa: E501` and should be avoided unless the user asks for it.
3. Serialise JSON with `indent=2`.
4. Wrap any disk I/O in `TemporaryDirectory()` and operate via `Path` objects.

## Python

1. Always use f-strings, `pathlib`, and idiomatic constructs.
2. Avoid `open()` for reading or writing — use `Path.read_text()` / `Path.write_text()` / `Path.read_bytes()` / `Path.write_bytes()` (ruff `PTH`).
3. Never use `print` outside `scripts/`. Use `logger = logging.getLogger(__name__)` at module level (ruff `T20`).
4. Annotate everything; mypy runs with `disallow_untyped_defs = true`. Use modern typing (`list[...]`, `dict[...]`, `X | None`, `collections.abc.MutableMapping`, etc.).

## Tests

1. Function-based pytest with `@pytest.mark.parametrize`. No test classes.
2. Shared fixtures, env dicts and fixture-path constants live in `tests/conftest.py`. Test data under `tests/data/` or `tests/fixtures/`.
3. Mock environment with `monkeypatch.setattr(<module>, "environ", env_vars)` — do not mutate the real `os.environ`.
4. Don't lower the `--cov-fail-under` threshold configured in `pyproject.toml`; add tests instead.

## Tooling

1. Use **ruff + mypy + pytest** with **uv**.
2. Standard QA invocation: `make qa && make test` — `make qa` covers lint, format and type checks only, tests are a separate target.
3. Never call `python3` directly in agent scripts; use `uv run` so inline script metadata can declare dependencies.
