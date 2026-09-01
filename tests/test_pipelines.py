import re
from pathlib import Path

import pytest
import yaml

TEMPLATE_DIRECTORY = Path(__file__).parent.parent
REUSABLE_QA_WORKFLOW = TEMPLATE_DIRECTORY / ".github" / "workflows" / "reusable-qa.yml"
REMOTE_SCRIPT = Path("scripts") / "create_remote.py"


def test_github_pipeline_generates_pinned_qa_caller(project_generator) -> None:
    with project_generator({"git_provider": "GitHub"}) as project_dir:
        workflows = project_dir / ".github" / "workflows"
        assert {path.name for path in workflows.iterdir()} == {"qa.yml", "release.yml"}

        qa_content = (workflows / "qa.yml").read_text()
        assert re.search(
            r"uses: gvieralopez/cookie-pyrate/\.github/workflows/reusable-qa\.yml@(.+)", qa_content
        )

        release_content = (workflows / "release.yml").read_text()
        assert re.search(
            r"uses: gvieralopez/cookie-pyrate/\.github/workflows/reusable-release\.yml@(.+)",
            release_content,
        )
        assert 'workflows: ["QA"]' in release_content
        assert "release-ssh-key: ${{ secrets.RELEASE_SSH_KEY }}" in release_content


def test_required_qa_check_matches_the_name_github_will_report(project_generator) -> None:
    """The required check is "<caller job id> / <reusable job name>"; drift makes it unmergeable."""
    with project_generator({"git_provider": "GitHub"}) as project_dir:
        caller_jobs = yaml.safe_load((project_dir / ".github/workflows/qa.yml").read_text())["jobs"]
        reusable_jobs = yaml.safe_load(REUSABLE_QA_WORKFLOW.read_text())["jobs"]
        caller_job_id = next(iter(caller_jobs))
        reusable_job_name = next(iter(reusable_jobs.values()))["name"]

        script = (project_dir / REMOTE_SCRIPT).read_text()
        expected = f"{caller_job_id} / {reusable_job_name}"
        assert f'QA_STATUS_CHECK_NAME = "{expected}"' in script


def test_codeowners_names_the_github_user(project_generator) -> None:
    with project_generator({"codeowner_username": "octocat"}) as project_dir:
        assert (project_dir / "CODEOWNERS").read_text() == "* @octocat\n"


def test_blank_username_drops_codeowners(project_generator) -> None:
    with project_generator({"codeowner_username": ""}) as project_dir:
        assert not (project_dir / "CODEOWNERS").exists()


@pytest.mark.parametrize("answer", ["none", "None", " none "])
def test_none_username_drops_codeowners(project_generator, answer) -> None:
    with project_generator({"codeowner_username": answer}) as project_dir:
        assert not (project_dir / "CODEOWNERS").exists()


def test_github_directory_goes_when_nothing_needs_it(project_generator) -> None:
    with project_generator({"git_provider": "None", "codeowner_username": ""}) as project_dir:
        assert not (project_dir / ".github").exists()
