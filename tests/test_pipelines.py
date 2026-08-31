import re


def test_github_pipeline_generates_pinned_qa_caller(project_generator) -> None:
    with project_generator({"git_provider": "GitHub"}) as project_dir:
        workflows = project_dir / ".github" / "workflows"
        assert {path.name for path in workflows.iterdir()} == {"qa.yml"}

        qa_content = (workflows / "qa.yml").read_text()
        assert re.search(r"uses: gvieralopez/cookie-pyrate/\.github/actions/run-qa@.+", qa_content)
        assert "actions/checkout@v4" in qa_content


def test_codeowners_names_the_github_user(project_generator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        assert (project_dir / "CODEOWNERS").read_text() == "* @octocat\n"


def test_blank_username_drops_codeowners(project_generator) -> None:
    with project_generator({"codeowner_username": ""}) as project_dir:
        assert not (project_dir / "CODEOWNERS").exists()


def test_github_directory_goes_when_nothing_needs_it(project_generator) -> None:
    with project_generator({"git_provider": "None", "codeowner_username": ""}) as project_dir:
        assert not (project_dir / ".github").exists()
