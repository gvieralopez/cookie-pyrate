import re
from pathlib import Path

import pytest
import yaml

TEMPLATE_DIRECTORY = Path(__file__).parent.parent
REUSABLE_QA_WORKFLOW = TEMPLATE_DIRECTORY / ".github" / "workflows" / "reusable-qa.yml"
REUSABLE_RELEASE_WORKFLOW = TEMPLATE_DIRECTORY / ".github" / "workflows" / "reusable-release.yml"
RELEASE_CALLER = Path(".github") / "workflows" / "release.yml"
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


@pytest.mark.parametrize("with_dockerfile", [True, False])
def test_release_caller_offers_docker_publishing_only_with_a_dockerfile(
    project_generator, with_dockerfile
) -> None:
    conf = {"git_provider": "GitHub", "with_dockerfile": with_dockerfile}
    with project_generator(conf) as project_dir:
        options = _release_options(project_dir)
        assert ("publish-docker-image" in options) is with_dockerfile
        assert options.get("publish-docker-image", False) is False


@pytest.mark.parametrize("with_dockerfile", [True, False])
def test_release_caller_only_passes_declared_inputs(project_generator, with_dockerfile) -> None:
    conf = {"git_provider": "GitHub", "with_dockerfile": with_dockerfile}
    with project_generator(conf) as project_dir:
        reusable = yaml.safe_load(REUSABLE_RELEASE_WORKFLOW.read_text())
        # PyYAML reads the bare `on` key as the boolean True.
        declared = set(reusable[True]["workflow_call"]["inputs"])
        assert set(_release_options(project_dir)) <= declared


def test_docker_job_inherits_permissions_and_builds_the_released_commit() -> None:
    """Declaring `packages: write` on the job would stop the workflow for callers without it."""
    job = yaml.safe_load(REUSABLE_RELEASE_WORKFLOW.read_text())["jobs"]["publish-docker-image"]
    assert "permissions" not in job
    assert "release" in job["needs"]
    assert job["steps"][0]["with"]["ref"] == "${{ needs.release.outputs.sha }}"
    metadata = next(step for step in job["steps"] if step.get("id") == "meta")
    assert "revision=${{ needs.release.outputs.sha }}" in metadata["with"]["labels"]


def _release_options(project_dir: Path) -> dict[str, object]:
    caller = yaml.safe_load((project_dir / RELEASE_CALLER).read_text())
    options: dict[str, object] = caller["jobs"]["release"]["with"]
    return options
