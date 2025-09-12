import tomllib


def test_license(project_generator) -> None:
    licence_types = {
        "MIT": "MIT License",
        "Apache-2.0": "Apache License",
        "GPL-3.0-or-later": "GNU GENERAL PUBLIC LICENSE",
        "Proprietary": "Proprietary License",
    }
    for license, license_header in licence_types.items():
        with project_generator({"license": license}) as project_dir:
            pyproject = project_dir / "pyproject.toml"
            pyproject_content = tomllib.loads(pyproject.read_text())
            assert pyproject_content["project"]["license"]["text"] == license
            license_file = project_dir / "LICENSE"
            assert license_file.exists()
            license_content = license_file.read_text()
            assert license_header in license_content


def test_license_none(project_generator) -> None:
    with project_generator({"license": "None"}) as project_dir:
        pyproject = project_dir / "pyproject.toml"
        pyproject_content = tomllib.loads(pyproject.read_text())
        assert "license" not in pyproject_content["project"]
        license_file = project_dir / "LICENSE"
        assert not license_file.exists()
