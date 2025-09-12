def test_valid_repo_name(project_generator) -> None:
    project_names = {
        "My project": "my-project",
    }

    for p_name, repo_name in project_names.items():
        with project_generator({"project_name": p_name}) as project_dir:
            assert project_dir.name == repo_name
