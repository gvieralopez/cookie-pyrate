import tomllib


def test_pyproject_with_precommit(project_generator) -> None:
    with project_generator() as project_dir:
        pyproject = project_dir / "pyproject.toml"
        pyproject_content = tomllib.loads(pyproject.read_text())

        assert "pre-commit" in pyproject_content["dependency-groups"]["dev"]


def test_precommit_config_with_precommit(project_generator) -> None:
    with project_generator() as project_dir:
        assert (project_dir / ".pre-commit-config.yaml").exists()


def test_precommit_config_without_precommit(project_generator) -> None:
    with project_generator({"with_precommit": False}) as project_dir:
        assert not (project_dir / ".pre-commit-config.yaml").exists()


def test_readme_with_precommit(project_generator) -> None:
    with project_generator() as project_dir:
        readme = project_dir / "README.md"
        readme_content = readme.read_text()
        assert "### Pre-Commit Hooks" in readme_content


def test_readme_without_docs(project_generator) -> None:
    with project_generator({"with_precommit": False}) as project_dir:
        readme = project_dir / "README.md"
        readme_content = readme.read_text()
        assert "### Pre-Commit Hooks" not in readme_content
