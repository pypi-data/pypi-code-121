import pytest
from queenbee.job import Job as QbJob
from pollination_streamlit.api.client import ApiClient
from pollination_streamlit.api.jobs import JobsAPI
from pollination_streamlit.api.recipes import RecipesAPI
from pollination_streamlit.api.runs import RunsAPI


@pytest.fixture
def test_client():
    return ApiClient()


@pytest.fixture
def runs_api(test_client):
    return RunsAPI(test_client)


@pytest.fixture
def jobs_api(test_client):
    return JobsAPI(test_client)


@pytest.fixture
def recipes_api(test_client):
    return RecipesAPI(test_client)


def test_init_api_client(default_host, custom_host, api_token):
    client_no_auth = ApiClient()
    assert client_no_auth.host == default_host
    assert client_no_auth.headers == {}

    client_with_auth = ApiClient(host=custom_host, api_token=api_token)
    assert client_with_auth.host == custom_host
    assert client_with_auth.headers == {
        'x-pollination-token': api_token
    }

    client_host_string = ApiClient(host='https://some.host/')
    assert client_host_string.host == 'https://some.host'


def test_download_artifact(test_client: ApiClient, download_job_artifact, artifact_url: str):
    res = test_client.download_artifact(artifact_url)
    assert res.read() == b'Hello World!'


def test_get_job(jobs_api: JobsAPI, single_job, single_job_from_api, job_id):
    assert jobs_api.get_job('ladybug-tools', 'demo',
                            job_id) == single_job


def test_get_runs(runs_api: RunsAPI, job_results, job_id, run_results_dict):
    assert runs_api.get_runs('ladybug-tools', 'demo',
                             job_id) == run_results_dict


def test_get_run(runs_api: RunsAPI, single_run, single_run_from_api, run_id):
    assert runs_api.get_run('ladybug-tools', 'demo',
                            run_id) == single_run


def test_list_job_artifacts(jobs_api: JobsAPI, job_artifacts_list, job_id, artifact_path, artifact_list):
    assert jobs_api.list_job_artifacts(
        'ladybug-tools', 'demo', job_id, artifact_path) == artifact_list


def test_get_job_artifact(jobs_api: JobsAPI, download_job_artifact, job_id, artifact_path):
    assert jobs_api.get_job_artifact(
        'ladybug-tools', 'demo', job_id, artifact_path).read() == b'Hello World!'


def test_download_zipped_run_output(runs_api: RunsAPI, download_run_output_artifact, run_id, run_output):
    assert runs_api.download_zipped_run_output(
        'ladybug-tools', 'demo', run_id, run_output).read() == b'Hello World!'


def test_create_job(jobs_api: JobsAPI, create_job, job_id, job_spec: QbJob):
    assert jobs_api.create_job('ladybug-tools', 'demo', job_spec) \
        == job_id


def test_get_recipe(recipes_api: RecipesAPI, get_recipe, recipe):
    assert recipes_api.get_recipe(
        'ladybug-tools', 'annual-daylight', '0.8.2-viz') == recipe
