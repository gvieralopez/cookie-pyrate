def test_repo_name(project_generator) -> None:
    project_names = {
        "my project": "my-project",
        "My pRoJeCT": "my-project",
        "my_project": "my-project",
    }

    for p_name, repo_name in project_names.items():
        with project_generator({"project_name": p_name}) as project_dir:
            assert project_dir.name == repo_name
