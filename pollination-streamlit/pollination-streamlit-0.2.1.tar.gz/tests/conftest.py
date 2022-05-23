import json
from pathlib import Path

import pytest
import requests_mock
from pydantic import BaseConfig
from queenbee.job import Job, JobStatus, RunStatus
from queenbee.recipe import RecipeInterface
from queenbee.recipe.recipe import Recipe
from requests import Request

BaseConfig.allow_population_by_field_name = True


@pytest.fixture
def curdir():
    return Path(__file__).parent


@pytest.fixture
def assets(curdir: Path):
    return curdir.joinpath('assets')


@pytest.fixture
def run_results_dict(assets: Path):
    with open(assets.joinpath('run-results.json')) as f:
        return json.load(f)


@pytest.fixture
def artifact_list(assets: Path):
    with open(assets.joinpath('artifact-list.json')) as f:
        return json.load(f)


@pytest.fixture
def single_job(assets: Path):
    return json.loads(assets.joinpath('job-pollination-api.json').read_bytes())


@pytest.fixture
def single_run(assets: Path):
    return json.loads(assets.joinpath('run-pollination-api.json').read_bytes())


@pytest.fixture
def recipe(assets: Path):
    return Recipe.from_file(assets.joinpath('recipe-pollination-api.json').as_posix())


@pytest.fixture
def default_host():
    return 'https://api.pollination.cloud'


@pytest.fixture
def custom_host():
    return 'https://api.staging.pollination.cloud'


@pytest.fixture
def api_token():
    return 'some-long-token-string'


@pytest.fixture
def job_id(single_job):
    return single_job['id']


@pytest.fixture
def run_id(single_run):
    return single_run['id']


@pytest.fixture
def job_spec(single_job):
    return Job.parse_obj(single_job['spec'])


@pytest.fixture
def job_status(single_job):
    return JobStatus.parse_obj(single_job['status'])


@pytest.fixture
def recipe_interface(single_job):
    return RecipeInterface.parse_obj(single_job['recipe'])


@pytest.fixture
def run_status(single_run):
    return RunStatus.parse_obj(single_run['status'])


@pytest.fixture
def job_create_response(job_id):
    return {
        "id": job_id,
        "message": "Use Location in headers to access the new object."
    }


@pytest.fixture
def run_output():
    return 'results'


@pytest.fixture
def artifact_path():
    return 'some-path'


@pytest.fixture
def artifact_url():
    return 'https://gcs.some.random.url/artifat-path'


@pytest.fixture
def job_results(default_host, job_id, run_results_dict):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/results?job_id={job_id}&page=1',
            json={'resources': run_results_dict}
        )
        yield


@pytest.fixture
def job_artifacts_list(default_host, job_id, artifact_path, artifact_list):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/jobs/{job_id}/artifacts?path={artifact_path}',
            json=artifact_list
        )
        yield


@pytest.fixture
def download_job_artifact(default_host, job_id, artifact_path, artifact_url):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/jobs/{job_id}/artifacts/download?path={artifact_path}',
            text=artifact_url,
        )
        m.get(artifact_url, content=b'Hello World!')
        yield


@pytest.fixture
def download_run_output_artifact(default_host, run_id, run_output, artifact_url):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/runs/{run_id}/outputs/{run_output}',
            text=artifact_url,
        )
        m.get(artifact_url, content=b'Hello World!')
        yield


@pytest.fixture
def single_run_from_api(default_host, run_id, single_run):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/runs/{run_id}',
            json=single_run,
        )
        yield


@pytest.fixture
def single_job_from_api(default_host, job_id, single_job):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/projects/ladybug-tools/demo/jobs/{job_id}',
            json=single_job,
        )
        yield


@pytest.fixture
def create_job(default_host, job_spec, job_create_response):
    def additional_matcher(request: Request):
        return json.loads(request.text) == job_spec.dict()

    with requests_mock.Mocker() as m:
        m.post(
            f'{default_host}/projects/ladybug-tools/demo/jobs',
            additional_matcher=additional_matcher,
            json=job_create_response
        )
        yield


@pytest.fixture
def get_recipe(default_host, recipe):
    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/registries/ladybug-tools/recipe/annual-daylight/0.8.2-viz/json',
            json=recipe.dict(),
        )
        yield


@pytest.fixture
def get_recipe_and_create_job(default_host, recipe, job_spec, job_create_response):
    def additional_matcher(request: Request):
        return json.loads(request.text) == job_spec.dict()

    with requests_mock.Mocker() as m:
        m.get(
            f'{default_host}/registries/ladybug-tools/recipe/annual-daylight/0.8.2-viz/json',
            json=recipe.dict(),
        )
        m.post(
            f'{default_host}/projects/ladybug-tools/demo/jobs',
            additional_matcher=additional_matcher,
            json=job_create_response
        )
        yield
