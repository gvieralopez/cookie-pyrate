import tomllib


def test_package_name(project_generator) -> None:
    project_names = {
        "my project": "my_project",
        "My pRoJeCT": "my_project",
        "my_project": "my_project",
    }

    for p_name, package_name in project_names.items():
        with project_generator({"project_name": p_name}) as project_dir:
            pyproject = project_dir / "pyproject.toml"
            pyproject_content = tomllib.loads(pyproject.read_text())
            assert pyproject_content["project"]["name"] == package_name

            assert (project_dir / "src" / package_name).exists()
