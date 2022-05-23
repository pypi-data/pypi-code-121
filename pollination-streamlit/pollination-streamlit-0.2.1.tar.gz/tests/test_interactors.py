from uuid import uuid4

import pytest
from pandas.util.testing import assert_frame_equal
from pollination_streamlit.dataframe import RunsDataFrame
from pollination_streamlit.interactors import (Artifact, Job, NewJob, Recipe,
                                               Run)


@pytest.fixture
def owner():
    return 'ladybug-tools'


@pytest.fixture
def project():
    return 'demo'


@pytest.fixture
def job_id():
    return str(uuid4())


@pytest.fixture
def test_client():
    pass


def test_artifact():
    key = '/some/test/key.txt'
    file_type = 'file'

    class JobStub:
        @staticmethod
        def download_artifact(path: str) -> bool:
            return path == key

    art = Artifact(key, file_type, JobStub)
    assert art.name == 'key.txt'
    assert art.is_file
    assert not art.is_folder
    assert art.download()

    art = Artifact(key, 'folder', JobStub)
    assert art.name == 'key.txt'
    assert not art.is_file
    assert art.is_folder
    with pytest.raises(ValueError):
        art.download()


def test_job(job_id, single_job_from_api, job_spec, job_status, recipe_interface):
    job = Job('ladybug-tools', 'demo', job_id)

    assert job.spec == job_spec
    assert job.status == job_status
    assert job.recipe_interface == recipe_interface
    assert job.recipe.owner == 'ladybug-tools'
    assert job.recipe.name == 'annual-daylight'
    assert job.recipe.tag == '0.8.2-viz'


def test_job_runs(job_id, job_results, run_results_dict):
    job = Job('ladybug-tools', 'demo', job_id)
    rdf = RunsDataFrame.from_run_results(run_results_dict)

    assert_frame_equal(job.runs_dataframe.dataframe, rdf.dataframe)

    run_id = job.runs_dataframe.dataframe.index[0]

    run = job.runs[0]
    assert run.owner == 'ladybug-tools'
    assert run.project == 'demo'
    assert run.job_id == job_id
    assert run.id == run_id


def test_run(job_id, run_id, single_run_from_api, run_status, recipe_interface):
    run = Run('ladybug-tools', 'demo', job_id, run_id)
    assert run.status == run_status
    assert run.recipe_interface == recipe_interface
    assert run.recipe.owner == 'ladybug-tools'
    assert run.recipe.name == 'annual-daylight'
    assert run.recipe.tag == '0.8.2-viz'

    assert run.full_artifact_path(
        '/some/path') == f'runs/{run_id}/workspace/some/path'
    assert run.full_artifact_path(
        'some/path') == f'runs/{run_id}/workspace/some/path'


def test_recipe(get_recipe, recipe):
    r = Recipe('ladybug-tools', 'annual-daylight', '0.8.2-viz')

    assert r.source_url == 'https://api.pollination.cloud/registries/ladybug-tools/recipe/annual-daylight/0.8.2-viz'
    assert r.api_object == recipe
    assert r.input_artifacts == ['model', 'schedule', 'wea']
    assert r.input_parameters == ['cpu-count', 'grid-filter',
                                  'min-sensor-count', 'north',
                                  'radiance-parameters', 'thresholds']
    assert r.inputs_required == ['model', 'wea']


def test_new_job_validation(get_recipe):
    r = Recipe('ladybug-tools', 'annual-daylight', '0.8.2-viz')

    new_job = NewJob('ladybug-tools', 'demo', r)

    with pytest.raises(ValueError):
        new_job.create()

    new_job.arguments = [
        {'model': 'path/to/model', 'wea': 'path/to/wea'},
        {'model': 'path/to/model'}
    ]

    with pytest.raises(ValueError):
        new_job.create()


def test_new_job(get_recipe_and_create_job, job_id):
    r = Recipe('ladybug-tools', 'annual-daylight', '0.8.2-viz')
    new_job = NewJob(
        owner='ladybug-tools',
        project='demo',
        recipe=r,
        name='Annual daylight with visualization',
        description='Show case the new visualization output',
        arguments=[
            {
                'cpu-count': '50',
                'grid-filter': '*',
                'min-sensor-count': '500',
                'north': '0',
                'radiance-parameters': '-ab 2 -ad 5000 -lw 2e-05',
                'thresholds': '-t 300 -lt 100 -ut 3000',
                'wea': 'USA_CA_Palo.Alto.AP.724937_CTZ2010.wea',
                'model': 'hsog4fmk.jjv.hbjson'
            },
            {
                'cpu-count': '50',
                'grid-filter': '*',
                'min-sensor-count': '500',
                'north': '0',
                'radiance-parameters': '-ab 2 -ad 5000 -lw 2e-05',
                'thresholds': '-t 300 -lt 100 -ut 3000',
                'wea': 'USA_CA_Palo.Alto.AP.724937_CTZ2010.wea',
                'model': 'hsog4fmk.jjv.hbjson'
            }
        ]
    )

    job = new_job.create()
    assert isinstance(job, Job)
    assert job.id == job_id
    assert job.owner == new_job.owner
    assert job.project == new_job.project
