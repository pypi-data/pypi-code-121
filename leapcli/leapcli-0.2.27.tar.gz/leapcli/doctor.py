import logging
import sys
import traceback
from functools import lru_cache
from typing import Optional
from urllib3.exceptions import MaxRetryError

import luddite
import pkg_resources
from openapi_client.api.default_api import DefaultApi
from openapi_client.exceptions import NotFoundException, UnauthorizedException
from semver import VersionInfo

from leapcli.project import Project
from leapcli.login import Authenticator
from leapcli.exceptions import LoginFailed, DoctorCheckFailed
import leapcli.exceptions
from leapcli.push import Push

_log = logging.getLogger(__name__)

BANNER = '''
*******************************************************************
*                       Tensorleap CLI                            *
*                       --------------                            *
*                        health check                             *
*******************************************************************
'''

SCREEN_WIDTH = len(BANNER.split('\n')[1])


def format_kv(key: str, val: str) -> str:
    padding = SCREEN_WIDTH - len(key) - len(val) - 1
    assert padding > 0
    return f'{key}:{" " * padding}{val}'


# Prints key aligned to left and value to right.
def print_kv(key: str, val: str):
    print(format_kv(key, val))


def yesnobool(value: bool) -> str:
    return 'yes' if value else 'no'


class Doctor:
    def __init__(self, project: Project):
        self.project = project
        self._api: Optional[DefaultApi] = None

    def _get_api(self) -> DefaultApi:
        if self._api is None:
            self._api = Authenticator.authenticated_api()
        return self._api

    @staticmethod
    @lru_cache(1)
    def latest_cli_version() -> VersionInfo:
        return VersionInfo.parse(luddite.get_version_pypi("leapcli"))

    @staticmethod
    @lru_cache(1)
    def current_cli_version() -> VersionInfo:
        return VersionInfo.parse(pkg_resources.get_distribution("leapcli").version)

    @lru_cache(1)
    def update_available(self):
        return VersionInfo.compare(self.current_cli_version(),
                                   self.latest_cli_version()) < 0

    def check_cli(self):
        print_kv('Tensorleap CLI version', str(self.current_cli_version()))
        update = 'no'
        if self.update_available():
            update = f'yes ({str(self.latest_cli_version())})'
        print_kv('CLI update available', update)

    def check_project(self):
        Authenticator.initialize()
        print('\n* Inspecting project settings...\n')
        initialized = self.project.is_initialized()
        init = yesnobool(initialized)
        print_kv('Project initialized', init)
        if not initialized:
            print("\nRun `leap init` in your project's root directory.")
            raise DoctorCheckFailed()
        print_kv('API URL', Authenticator.detect_backend_url())
        print_kv('Project name', self.project.detect_project())
        print_kv('Dataset name', self.project.detect_dataset())

    def check_model(self) -> bool:
        path, _ = Push(self.project).serialize_model()
        return path.is_file()

    def check_dataset(self):
        Push(self.project).parse_dataset()
        print_kv('Dataset parse', 'ok')

    def check_codebase(self, should_check_model=True, should_check_dataset=True):
        print('\n* Inspecting model...\n')
        try:
            if should_check_model:
                if self.check_model():
                    print_kv('Model serialization', 'ok')
            if should_check_dataset:
                self.check_dataset()
            return
        except leapcli.exceptions.ModelNotFound:
            print_kv('Model serialization', 'error')
            expected_model_path = self.project.model_py_path()
            print(f'\nFailed to load model configuration.\n'
                  f'Path: {expected_model_path}')
        except leapcli.exceptions.ModelEntryPointNotFound:
            print_kv('Model serialization', 'error')
            expected_model_path = self.project.model_py_path()
            print(f'\nleap_save_model(path) function not found in model\n'
                  f'configuration file.\n'
                  f'\n'
                  f'Path: {expected_model_path}')
        except leapcli.exceptions.ModelNotSaved:
            print_kv('Model serialization', 'error')
            print('\nleap_save_model(path) did not save the model\n'
                  'to the given path.')
        except leapcli.exceptions.ModelSaveFailure as error:
            print_kv('Model serialization', 'error')
            print('\nleap_save_model(path) raised an exception.\n')
            print(type(error.inner_exception))
            traceback.print_exception(error.exc_type,
                                      error.inner_exception,
                                      error.traceback,
                                      file=sys.stdout)
        except leapcli.exceptions.ParseDatasetFailed:
            print_kv('Parse dataset', 'error')
            print('\ndataset raised an exception.\n')
        except Exception:  # pylint: disable=broad-except
            print_kv('Model serialization', 'error')
            print('Unknown error trying to save the model')
            traceback.print_exc()

        raise DoctorCheckFailed()

    @staticmethod
    def check_creds():
        print('\n* Inspecting credentials...')
        if not Authenticator.has_credentials():
            # TODO: use the real URL once this screen is implemented
            # in the web UI
            print('\n'
                  'Credentials not found.\n'
                  '\n'
                  'You can generate an API key on your Tensorleap environment\n')
            raise DoctorCheckFailed()
        try:
            Authenticator.initialize()

            print()
            print_kv('Logged in as', Authenticator.user.local.email)
            return True
        except (UnauthorizedException, NotFoundException, LoginFailed):
            print('\n'
                  'Login failed with the configured credentials.\n'
                  '\n'
                  'Try running `leap login` again.\n')
            raise DoctorCheckFailed()

    def check_project_exist(self):
        print('\n* Finding project...\n')
        project_id = self.project.project_id(self._get_api(), throw_on_not_found=False)
        if project_id is None:
            print(f"Did not find project named {self.project.detect_project()}.")
        else:
            print_kv("Project found. ID", project_id)

    def check_dataset_exist(self):
        print('\n* Finding dataset...\n')
        dataset_id = self.project.dataset_id(self._get_api(), throw_on_not_found=False)
        if dataset_id is None:
            print(f"Did not find dataset named {self.project.detect_dataset()}.")
        else:
            print_kv("Dataset found. ID", dataset_id)

    def run(self, should_check_model=True, should_check_dataset=True):
        print(BANNER)
        try:
            self.check_cli()
            self.check_project()
            self.check_creds()
            self.check_project_exist()
            if should_check_dataset:
                self.check_dataset_exist()
            self.check_codebase(should_check_model, should_check_dataset)
        except MaxRetryError:
            print('Failed to access the server. Please check your apiEndpoint in .tensorleap/config.toml')
            print('Check failed.')
        except DoctorCheckFailed:
            print('Check failed.')
