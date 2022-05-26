import os
import logging
import tempfile
from pathlib import Path
import re
from shutil import copytree
from typing import Optional

from toml import load, dump
from git import Repo
from git.exc import InvalidGitRepositoryError
import toml
from openapi_client.apis import DefaultApi

from leapcli.enums import ModelType
from leapcli.exceptions import CredentialsNotFound, AlreadyInitialized, InvalidProjectName, \
    ProjectNotFoundException, DatabaseAmbiguityException, DatasetNotFoundException


TENSORLEAP_DIR = '.tensorleap'
CONFIG_DIR = '~/.config/tensorleap'

VALID_PROJECT_REGEX = r'^[a-zA-Z0-9_\-. ]{3,}$'
VALID_PROJECT_EXPL = '''* At least 3 characters long.
* Allowed characters: alphanumeric, "_", "-", "."'''

VALID_ORG_REGEX = r'^[a-zA-Z0-9][a-zA-Z0-9\-]+[a-zA-Z0-9]$'
VALID_ORG_EXPL = '''* At least 3 characters long.
* Allowed characters: alphanumeric, "-"
* Does not start or end with a hyphen.
* No double hypens.'''

CONFIG_FILENAME = 'config.toml'

API_ENDPOINT = 'api/v2'

_log = logging.getLogger(__name__)


class Project:
    def __init__(self, directory: str = '.'):
        self.directory: Path = Path(directory)
        self.project: Optional[str] = None
        self.state = {}
        self.dataset: Optional[str] = None
        self.model_type: Optional[ModelType] = None

    def detect_project_dir(self) -> Path:
        try:
            repo = Repo(self.directory, search_parent_directories=True)
            return repo.working_tree_dir
        except InvalidGitRepositoryError:
            return os.getcwd()

    def detect_project(self) -> str:
        if self.is_initialized():
            return self.project_config()['projectName']
        raise CredentialsNotFound()

    def detect_dataset(self) -> str:
        if self.is_initialized():
            return self.project_config()['datasetName']
        raise CredentialsNotFound()

    def detect_model_type(self) -> ModelType:
        if self.is_initialized():
            return ModelType[self.project_config()['modelType']]
        raise CredentialsNotFound()

    @staticmethod
    def prompt_dataset() -> str:
        return input('Dataset name: ')

    @staticmethod
    def prompt_project() -> str:
        return input('Project name: ')

    # TODO: cache this result
    def project_id(self, api: DefaultApi, throw_on_not_found=True) -> Optional[str]:
        config_project_name = self.detect_project()
        matches = [proj.id for proj in api.get_projects().data if proj.name == config_project_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 0:
            if throw_on_not_found:
                raise ProjectNotFoundException(config_project_name)
            return None

        raise DatabaseAmbiguityException(f"Found more than two projects with the same name. "
                                         f"Project name: {config_project_name}")

    # TODO: cache this result
    def dataset_id(self, api: DefaultApi, throw_on_not_found=True) -> Optional[str]:
        config_dataset_name = self.detect_dataset()
        matches = [dataset.id for dataset in api.get_datasets().datasets if dataset.name == config_dataset_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 0:
            if throw_on_not_found:
                raise DatasetNotFoundException(config_dataset_name)
            return None

        raise DatabaseAmbiguityException(f"Found more than two datasets with the same name. "
                                         f"Dataset name: {config_dataset_name}")

    def cache_dir(self) -> Path:
        self.read_state()
        if 'cache_dir' in self.state:
            cache_dir = Path(self.state['cache_dir'])
            if cache_dir.exists():
                return Path(self.state['cache_dir'])

        cache_dir = tempfile.mkdtemp(prefix='tensorleap-cache')
        self.state['cache_dir'] = cache_dir
        self.save_state()
        return Path(cache_dir)

    @staticmethod
    def leapcli_state_file() -> Path:
        return Project.config_dir().joinpath('state.toml')

    def read_state(self) -> dict:
        if Project.leapcli_state_file().is_file():
            with open(Project.leapcli_state_file(), encoding='utf-8') as f:
                self.state = load(f)
        return self.state

    def save_state(self) -> None:
        with open(Project.leapcli_state_file(), 'w', encoding='utf-8') as f:
            dump(self.state, f)

    @staticmethod
    def leapcli_package_dir() -> Path:
        return Path(__file__).parent.parent

    @staticmethod
    def leapcli_package_info() -> dict:
        poetry_conf_file = Project.leapcli_package_dir(). \
            joinpath('pyproject.toml')
        with open(poetry_conf_file, encoding='utf-8') as f:
            return toml.load(f)

    @staticmethod
    def template_dir() -> Path:
        return Project.leapcli_package_dir().joinpath('templates')

    @staticmethod
    def config_dir() -> Path:
        ret = Path(CONFIG_DIR).expanduser()
        ret.mkdir(parents=True, exist_ok=True)
        return ret

    def tensorleap_dir(self) -> Path:
        return self.directory.joinpath(TENSORLEAP_DIR)

    @staticmethod
    def validate_project_name(name: str) -> None:
        if not name or re.match(VALID_PROJECT_REGEX, name) is None:
            raise InvalidProjectName()

    def is_initialized(self):
        return self.tensorleap_dir().is_dir()

    def init_project(self, project: str, dataset: str, model_type: ModelType):
        if self.is_initialized():
            raise AlreadyInitialized()
        self.project = project or self.prompt_project()
        Project.validate_project_name(self.project)
        self.dataset = dataset
        self.model_type = model_type
        self._generate_project_template()

    def config_file_path(self) -> Path:
        return self.tensorleap_dir().joinpath(CONFIG_FILENAME)

    def project_config(self) -> dict:
        with open(self.config_file_path(), 'r', encoding='utf-8') as config_file:
            _log.debug('reading stored config from %s', self.config_file_path())
            return toml.load(config_file)

    def _generate_project_template(self):
        assert self.project
        assert not self.tensorleap_dir().is_dir()

        tgt = self.tensorleap_dir()
        copytree(Project.template_dir().joinpath(TENSORLEAP_DIR), tgt)
        with open(self.config_file_path(), 'r', encoding='utf-8') as config_file:
            txt = config_file.read()
            txt = txt.replace('PROJ', self.project)
            txt = txt.replace('DATASET', self.dataset)
            txt = txt.replace('MODEL_TYPE', self.model_type.name)

        with open(self.config_file_path(), 'w', encoding='utf-8') as config_file:
            config_file.write(txt)

    def _integration_file_py_path(self, file_name: str) -> Path:
        file_py = self.project_config()['integration'][file_name]
        return self.tensorleap_dir().joinpath(file_py)

    def model_py_path(self) -> Path:
        return self._integration_file_py_path('model')

    def dataset_py_path(self) -> Path:
        return self._integration_file_py_path('dataset')

    def mapping_py_path(self) -> Path:
        return self._integration_file_py_path('mapping')
