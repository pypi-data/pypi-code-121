from typing import Callable, Union

import requests

from pymbse.commons import text_file
from pymbse.pymbse.model_api.executor.notebook_script_executor import ScriptExecutor, NotebookExecutor
from pymbse.pymbse.model_api.executor.notebook_converter import create_script_if_missing_or_outdated

from pymbse.pymbse.model_api.executor.notebook_converter import convert_ipynb_to_html
from pymbse.pymbse.model_api.model_api import ModelAPI
from pymbse.pymbse.model_api.snapshot.model_snapshot import ModelSnapshot, HashedModelSnapshot

API_ENDPOINT = "api/model_snapshots"


def post_model_snapshot_to_cache_decorator(execute_notebook: Callable) -> Callable:
    """Decorator posting a model snapshot to model_api with notebook execution. The notebook itself is not uploaded
    due to its, potentially, excessive size and MongoDb message limit of 16 Mb.

    :param execute_notebook: a function executing a notebook and returning model snapshot
    :return: a cached execute_script function that either stores the model snapshot or not
    """
    def wrapper(model_api: ModelAPI) -> None:
        """Wrapper function executing a notebook

        :param model_api: ModelAPI instance
        """
        cached_model_snapshot = get_cached_model_snapshot(model_api.ip_with_port, model_api.root_model_metadata_hash)
        if cached_model_snapshot is None:
            executed_model_snapshot = execute_notebook(model_api)
            post_model_snapshot_to_cache(model_api.ip_with_port, executed_model_snapshot, model_api.root_model_metadata_hash)
        else:
            execute_notebook(model_api)

    return wrapper


def get_model_snapshot_from_cache_decorator(execute_script: Callable) -> Callable:
    """Decorator acting on a ModelAPI method and providing a caching mechanism. If a model snapshot model_api is present in a
    database, then its snapshot is returned, otherwise the script is executed and the snapshot stored in the database.

    :param execute_script: an execute_script function
    :return: a cached execute_script function that either executes the function or returns a cached model snapshot
    """
    def wrapper(model_api: ModelAPI) -> ModelSnapshot:
        """ Function wrapping the model_api functionality

        :param model_api: ModelAPI instance
        :return: a ModelSnapshot instance either obtained from the model_api or from script execution
        """

        cached_model = get_cached_model_snapshot(model_api.ip_with_port, model_api.root_model_metadata_hash)
        if cached_model is None:
            print('Executing %s as its model snapshot is not yet cached.' %
                  model_api.root_model_config.model_abs_path)
            cached_model = execute_script(model_api)
            post_model_snapshot_to_cache(model_api.ip_with_port, cached_model, model_api.root_model_metadata_hash)

        return cached_model

    return wrapper


def get_cached_model_snapshot(ip_with_port: str, model_snapshot_hash: str) -> Union[None, ModelSnapshot]:
    """Function getting a cached model from a database

    :param ip_with_port: a path to the database with an ip and port, e.g., localhost:8000
    :param model_snapshot_hash: a model_api of the model snapshot, it is the primary key for the model_api mechanism
    :return: None if a model_api is not present in the database, otherwise a ModelSnapshot instance
    """
    url = "%s/%s/%s" % (ip_with_port, API_ENDPOINT, model_snapshot_hash)
    response = requests.request("GET", url)
    if response.json() is None or response.status_code != 200:
        return None
    else:
        return HashedModelSnapshot(**response.json()).downcast_to_model_snapshot()


def post_model_snapshot_to_cache(ip_with_port: str, model_snapshot: ModelSnapshot, model_snapshot_hash: str) -> None:
    """Function posting a model snapshot with model_api to the model_api database

    :param ip_with_port: a path to the database with an ip and port, e.g., localhost:8000
    :param model_snapshot: a model snapshot to be cached
    :param model_snapshot_hash: a model_api of the model snapshot, it is the primary key for the model_api mechanism
    """
    url = "%s/%s/" % (ip_with_port, API_ENDPOINT)
    json_payload = model_snapshot.upcast_to_hashed_model_snapshot(model_snapshot_hash).dict()
    response = requests.request("POST", url, json=json_payload)
    if response.status_code != 201:
        raise ConnectionError('Could not post model snapshot to url: %s' % url)


class NotebookModelAPI(ModelAPI):
    def get_html_report(self) -> str:
        """Method returning an HTML report content. It executes a notebook with papermill and returns an HTML file
        content.

        :return: a string containing the HTML report content
        """
        self.execute_without_cache()
        convert_ipynb_to_html(ipynb_abs_path=self.root_model_config.get_ipynb_out_abs_path(),
                              html_abs_path=self.root_model_config.get_html_out_abs_path())
        return text_file.read(self.root_model_config.get_html_out_abs_path())

    def get_ipynb_report(self) -> str:
        """Method returning an ipynb report content. It executes a notebook with papermill and returns an ipynb file
        content.

        :return: a string containing the ipynb report content
        """
        self.execute_without_cache()
        return text_file.read(self.root_model_config.get_ipynb_out_abs_path())

    @post_model_snapshot_to_cache_decorator
    def execute_without_cache(self) -> ModelSnapshot:
        return NotebookExecutor(model_dependency_config=self.root_model_config,
                                input_parameters=self.input_parameters).execute_with_snapshot()

    @get_model_snapshot_from_cache_decorator
    def execute(self) -> ModelSnapshot:
        return NotebookExecutor(model_dependency_config=self.root_model_config,
                                input_parameters=self.input_parameters).execute_with_snapshot()


class ScriptModelAPI(ModelAPI):

    @get_model_snapshot_from_cache_decorator
    def execute(self) -> ModelSnapshot:
        return ScriptExecutor(model_dependency_config=self.root_model_config,
                              input_parameters=self.input_parameters
                              ).execute_with_snapshot()


def create_script_if_missing_or_outdated_decorator(script_dependent_function: Callable) -> Callable:
    """

    :param script_dependent_function: a function executing
    :return: a script_dependent_function with ensured script presence
    """
    def wrapper(self: ModelAPI, *args, **kwargs) -> Callable:
        """Wrapper function executing the script_dependent_function

        :param self: PyMBSE instance
        :param args: a list of arguments
        :param kwargs: a dictionary with keyword arguments
        :return: script_dependent_function call
        """
        notebook_abs_path = self.root_model_config.model_abs_path
        script_abs_path = self.root_model_config.get_script_abs_path()
        model_name_without_ext = self.root_model_config.get_model_name_without_ext()
        create_script_if_missing_or_outdated(notebook_abs_path=notebook_abs_path,
                                             script_abs_path=script_abs_path,
                                             model_name_without_ext=model_name_without_ext)
        return script_dependent_function(self, *args, **kwargs)
    return wrapper


class NotebookScriptModelAPI(ScriptModelAPI):

    @create_script_if_missing_or_outdated_decorator
    def get_figures_of_merit(self) -> dict:
        return super().get_figures_of_merit()

    @create_script_if_missing_or_outdated_decorator
    def get_artefacts(self) -> dict:
        return super().get_artefacts()

    @create_script_if_missing_or_outdated_decorator
    def get_artefact(self, artefact_name: str) -> str:
        return super().get_artefact(artefact_name)
