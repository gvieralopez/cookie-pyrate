import re


def test_github_pipeline_generates_pinned_qa_caller(project_generator) -> None:
    with project_generator({"ci_cd_pipeline": "GitHub"}) as project_dir:
        workflows = project_dir / ".github" / "workflows"
        assert {path.name for path in workflows.iterdir()} == {"qa.yml"}

        qa_content = (workflows / "qa.yml").read_text()
        assert re.search(r"uses: gvieralopez/cookie-pyrate/github-actions/run-qa@.+", qa_content)
        assert "actions/checkout@v4" in qa_content


def test_none_pipeline_removes_github_workflows(project_generator) -> None:
    with project_generator({"ci_cd_pipeline": "None"}) as project_dir:
        assert not (project_dir / ".github").exists()
