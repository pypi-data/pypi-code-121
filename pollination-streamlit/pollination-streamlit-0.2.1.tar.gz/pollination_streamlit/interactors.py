import pathlib
import typing as t
from io import BytesIO

from queenbee.io.inputs.job import JobArgument, JobPathArgument
from queenbee.job import Job as QbJob
from queenbee.job import JobArguments, JobStatus, RunStatus
from queenbee.recipe import Recipe as QbRecipe
from queenbee.recipe import RecipeInterface

from .api.client import ApiClient
from .api.jobs import JobsAPI
from .api.recipes import RecipesAPI
from .api.runs import RunsAPI
from .dataframe import RunsDataFrame


class Recipe:

    def __init__(self, owner: str, name: str, tag: str = 'latest', client: ApiClient = ApiClient()):
        self.owner = owner
        self.name = name
        self.tag = tag

        self.recipe_api = RecipesAPI(client)
        self._client = client

        self._api_object = None

    @classmethod
    def from_source_url(cls, url: str, client: ApiClient = ApiClient()):
        source_split = url.split('/')
        return cls(
            owner=source_split[-4],
            name=source_split[-2],
            tag=source_split[-1],
            client=client,
        )

    def _fetch_recipe(self):
        self._api_object = self.recipe_api.get_recipe(
            self.owner, self.name, self.tag)

    @property
    def source_url(self) -> str:
        return f'{self._client.host}/registries/{self.owner}/recipe/{self.name}/{self.tag}'

    @property
    def api_object(self) -> QbRecipe:
        if self._api_object is None:
            self._fetch_recipe()
        return self._api_object

    @property
    def input_artifacts(self) -> t.List[str]:
        return [i.name for i in self.api_object.inputs if i.is_artifact]

    @property
    def input_parameters(self) -> t.List[str]:
        return [i.name for i in self.api_object.inputs if i.is_parameter]

    @property
    def inputs_required(self) -> t.List[str]:
        return [i.name for i in self.api_object.inputs if i.required]


class Job:

    def __init__(self, owner: str, project: str, id: str, client: ApiClient = ApiClient()):
        self.owner = owner
        self.project = project
        self.id = id
        self.job_api = JobsAPI(client)
        self.run_api = RunsAPI(client)

        self._client = client

        self._runs = None
        self._api_object = None

    def __str__(self) -> str:
        return f'<Job {self.owner}/{self.project}/{self.id}>'

    def _fetch_runs(self):
        self._runs = self.run_api.get_runs(self.owner, self.project, self.id)

    def _fetch_job(self):
        self._api_object = self.job_api.get_job(
            self.owner, self.project, self.id)

    def refresh(self):
        self._fetch_runs()
        self._fetch_job()

    @property
    def api_object(self) -> t.Dict[str, t.Any]:
        if self._api_object is None:
            self._fetch_job()
        return self._api_object

    @property
    def spec(self) -> QbJob:
        return QbJob.parse_obj(self.api_object['spec'])

    @property
    def status(self) -> JobStatus:
        return JobStatus.parse_obj(self.api_object['status'])

    @property
    def recipe_interface(self) -> RecipeInterface:
        return RecipeInterface.parse_obj(self.api_object['recipe'])

    @property
    def recipe(self) -> Recipe:
        return Recipe.from_source_url(self.recipe_interface.source, self._client)

    @property
    def runs_dataframe(self) -> RunsDataFrame:
        if self._runs is None:
            self._fetch_runs()
        return RunsDataFrame.from_run_results(self._runs)

    @property
    def runs(self) -> t.List['Run']:
        df = self.runs_dataframe
        runs = []
        for run_id in df.dataframe.index:
            run = Run(
                self.owner, self.project, self.id, run_id, self._client
            )
            runs.append(run)

        return runs

    def list_artifacts(self, path: str = None) -> t.List['Artifact']:
        response = self.job_api.list_job_artifacts(
            self.owner, self.project, self.id, path
        )
        return [Artifact(job=self, **artifact) for artifact in response]

    def download_artifact(self, path: str) -> BytesIO:
        return self.job_api.get_job_artifact(self.owner, self.project, self.id, path)


class NewJob:

    def __init__(self, owner: str, project: str, recipe: Recipe,
                 arguments: t.List[t.Dict[str, t.Any]] = [],
                 name: str = None, description: str = None,
                 client: ApiClient = ApiClient()):
        self.owner = owner
        self.project = project
        self.recipe = recipe
        self.arguments = arguments
        self.name = name
        self.description = description

        self._client = client
        self.job_api = JobsAPI(client)

    def create(self) -> Job:
        qb_job = self.generate_qb_job()
        job_id = self.job_api.create_job(self.owner, self.project, qb_job)
        return Job(self.owner, self.project, job_id, self._client)

    def upload_artifact(self, fp: pathlib.Path, target_folder: str = '') -> str:
        artifact_path = pathlib.Path(target_folder).joinpath(fp.name)
        return self.job_api.upload_artifact(self.owner, self.project, fp, artifact_path)

    def generate_qb_job(self) -> QbJob:
        arguments = self._generate_qb_job_arguments()
        return QbJob(
            source=self.recipe.source_url,
            arguments=arguments,
            name=self.name,
            description=self.description,
        )

    def _check_arguments(self):
        if self.arguments == []:
            raise ValueError('No job arguments specified')
        for i, run_args in enumerate(self.arguments):
            for ri in self.recipe.inputs_required:
                if ri not in run_args.keys():
                    raise ValueError(
                        f'Missing required input {ri} in arguments[{i}]')

    def _generate_qb_job_arguments(self) -> t.List[t.List[JobArguments]]:
        self._check_arguments()

        job_arguments = []

        for args in self.arguments:
            run_args = []
            for k, v in args.items():
                if k in self.recipe.input_artifacts:
                    run_args.append(JobPathArgument.parse_obj({
                        'name': k,
                        'source': {
                            'type': 'ProjectFolder',
                            'path': v
                        }
                    }))
                else:
                    run_args.append(JobArgument(
                        name=k,
                        value=v
                    ))

            job_arguments.append(run_args)

        return job_arguments


class Run:

    def __init__(self, owner: str, project: str, job_id: str, id: str, client: ApiClient = ApiClient()) -> None:
        self.owner = owner
        self.project = project
        self.job_id = job_id
        self.id = id

        self.run_api = RunsAPI(client)
        self.job = Job(owner, project, job_id, client)

        self._client = client

        self._api_object = None

    @property
    def _base_artifact_path(self) -> str:
        return f'runs/{self.id}/workspace/'

    def _fetch_run(self):
        self._api_object = self.run_api.get_run(
            self.owner, self.project, self.id)

    def refresh(self):
        self._fetch_run()

    @property
    def api_object(self) -> t.Dict[str, t.Any]:
        if self._api_object is None:
            self._fetch_run()
        return self._api_object

    @property
    def status(self) -> RunStatus:
        return RunStatus.parse_obj(self.api_object['status'])

    @property
    def recipe_interface(self) -> RecipeInterface:
        return RecipeInterface.parse_obj(self.api_object['recipe'])

    @property
    def recipe(self) -> Recipe:
        return Recipe.from_source_url(self.recipe_interface.source, self._client)

    def full_artifact_path(self, path: str) -> str:
        if path.startswith(self._base_artifact_path):
            return path
        if path.startswith('/'):
            path = path[1:]
        return self._base_artifact_path + path

    def download_zipped_output(self, output_name: str) -> BytesIO:
        return self.run_api.download_zipped_run_output(
            self.owner, self.project, self.id, output_name
        )

    def list_artifacts(self, path: str) -> t.List['Artifact']:
        return self.job.list_artifacts(self.full_artifact_path(path))

    def download_artifact(self, path: str) -> BytesIO:
        return self.job.download_artifact(self.full_artifact_path(path))


class Artifact:

    def __init__(self, key: str, file_type: str, job: Job, **kwargs):
        self.key = key
        self.file_type = file_type
        self.job = job

    def __str__(self) -> str:
        return f'<Artifact: {self.file_type} - {self.key}>'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def name(self) -> str:
        return self.key.split('/')[-1]

    @property
    def is_file(self) -> bool:
        return self.file_type == 'file'

    @property
    def is_folder(self) -> bool:
        return self.file_type == 'folder'

    def download(self) -> BytesIO:
        if self.is_file:
            return self.job.download_artifact(self.key)
        raise ValueError(f'Cannot download artifact of type {self.file_type}')

    def list_children(self) -> t.List['Artifact']:
        return self.job.list_artifacts(self.key)
