import re


def test_docker_file_with_docker(project_generator) -> None:
    with project_generator() as project_dir:
        assert (project_dir / "Dockerfile").exists()

        dockerfile_content = (project_dir / "Dockerfile").read_text()
        assert "FROM" in dockerfile_content


def test_docker_target_with_docker(project_generator) -> None:
    with project_generator() as project_dir:
        makefile = project_dir / "Makefile"
        makefile_content = makefile.read_text()

        # dockerimage target is present
        assert re.search(r"^dockerimage: build$", makefile_content, re.MULTILINE)

        # dockerimage target is included in .PHONY
        assert re.search(r"^.PHONY:.*dockerimage.*$", makefile_content, re.MULTILINE)


def test_readme_with_docker(project_generator) -> None:
    with project_generator() as project_dir:
        readme = project_dir / "README.md"
        readme_content = readme.read_text()
        assert "### Building a Docker image" in readme_content


def test_docker_file_without_docker(project_generator) -> None:
    with project_generator({"with_dockerfile": False}) as project_dir:
        assert not (project_dir / "Dockerfile").exists()


def test_docker_target_without_docker(project_generator) -> None:
    with project_generator({"with_dockerfile": False}) as project_dir:
        makefile = project_dir / "Makefile"
        makefile_content = makefile.read_text()

        # dockerimage target is not present
        assert not re.search(r"^dockerimage:$", makefile_content, re.MULTILINE)

        # dockerimage target is not included in .PHONY
        assert not re.search(
            r"^.PHONY:.*dockerimage.*$", makefile_content, re.MULTILINE
        )

        # Build target does not depend on dockerimage
        assert not re.search(r"^build:.*dockerimage.*$", makefile_content, re.MULTILINE)


def test_readme_without_docker(project_generator) -> None:
    with project_generator({"with_dockerfile": False}) as project_dir:
        readme = project_dir / "README.md"
        readme_content = readme.read_text()
        assert "### Building a Docker image" not in readme_content
        assert "make dockerimage" not in readme_content
