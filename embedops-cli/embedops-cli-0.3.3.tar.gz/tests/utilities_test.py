"""
`api_interface_test`
=======================================================================
Unit tests for code to upload XML files to the API
* Author(s): Bryan Siepert
"""
import pytest
from dynaconf import Dynaconf

DEFAULT_JOB_URL = "https://gitlab.com/luminostics/corefw/-/jobs/1890073938"


@pytest.fixture(scope="function", autouse=True)
def set_env_like_ci(monkeypatch):
    """Makes the environment look like it does in a CI system"""
    monkeypatch.setenv("CI_JOB_URL", DEFAULT_JOB_URL)
    monkeypatch.setenv("CI_COMMIT_SHA", "d34db33f")
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "main")


def set_test_settings():
    """A fixture to setup Dynaconf to use the testing environment"""
    return Dynaconf(
        FORCE_ENV_FOR_DYNACONF="loader",
        loaders=["embedops_cli.ci_config_loader"],
        envvar_prefix="EMBEDOPS",
        environments=True,
        settings_files=["settings.toml", ".secrets.toml"],
    )


def test_bb_get_job_url(monkeypatch):
    """Test that the job url for bitbucket is returned correctly"""
    monkeypatch.setenv("BITBUCKET_COMMIT", "c48aa")
    monkeypatch.setenv("BITBUCKET_BRANCH", "main")
    monkeypatch.setenv(
        "BITBUCKET_GIT_HTTP_ORIGIN", "https://bitbucket.org/baileysteinfadt/ti-testbed"
    )
    monkeypatch.setenv("BITBUCKET_STEP_UUID", "{4b85eb71-8130-4234-b57e-b7afe874eafc}")
    monkeypatch.setenv("BITBUCKET_BUILD_NUMBER", "76")

    settings = set_test_settings()

    assert settings.job_url == (
        f"https://bitbucket.org/baileysteinfadt/ti-testbed/addon/"
        f"pipelines/home#!/results/76/steps/{{4b85eb71-8130-4234-b57e-b7afe874eafc}}"
    )

    monkeypatch.setenv(
        "BITBUCKET_GIT_HTTP_ORIGIN", "https://bitbucket.org/baileysteinfadt/ti-testbed"
    )
    monkeypatch.setenv("BITBUCKET_STEP_UUID", "{not-a-real-uuid}")
    monkeypatch.setenv("BITBUCKET_BUILD_NUMBER", "2112")

    settings2 = set_test_settings()
    assert settings2.job_url == (
        f"https://bitbucket.org/baileysteinfadt/ti-testbed/addon/"
        f"pipelines/home#!/results/2112/steps/{{not-a-real-uuid}}"
    )


def test_gl_get_job_url(monkeypatch):
    """Test that the job url for gitlab is returned correctly"""
    settings = set_test_settings()

    assert settings.job_url == DEFAULT_JOB_URL


def test_no_ci_url_env(monkeypatch):
    """Test that the job url is not set it is not returned"""
    monkeypatch.delenv("CI_COMMIT_SHA")
    monkeypatch.delenv("CI_COMMIT_REF_NAME")
    monkeypatch.delenv("CI_JOB_URL")

    settings = set_test_settings()

    assert settings.get("job_url", None) is None
