import hashlib
import importlib.util
import logging
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

import requests
from openapi_client.model.add_version_params import AddVersionParams
from openapi_client.model.dataset_parse_request_params import DatasetParseRequestParams
from openapi_client.model.external_import_model_storage import ExternalImportModelStorage
from openapi_client.model.new_dataset_params import NewDatasetParams
from openapi_client.model.save_dataset_version_params import SaveDatasetVersionParams
from openapi_client.model.add_project_params import AddProjectParams
from openapi_client.models import GetUploadSignedUrlParams, ImportNewModelParams, ImportModelType, \
    ExternalImportModelStorageResponse, GetCurrentProjectVersionParams
from openapi_client.model.dataset_version import DatasetVersion
from openapi_client.model.model_graph import ModelGraph
from openapi_client.model.dataset import Dataset

from leap_model_parser.contract.importmodelresponse import ImportModelTypeEnum
from leap_model_parser.model_parser import ModelParser

from code_loader import LeapLoader
from code_loader.contract.responsedataclasses import DatasetIntegParseResult

from leapcli.exceptions import ModelNotFound, ModelEntryPointNotFound, ModelSaveFailure, \
    ModelNotSaved, DatabaseAmbiguityException, SecretNotFoundException, MappingNotFound, ParseDatasetFailed
from leapcli.login import Authenticator
from leapcli.project import Project
from leapcli.mapping.leap_graph_editor import LeapGraphEditor
from leapcli.enums import ModelType

_log = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Push:
    def __init__(self, project: Project):
        self.project = project

        Authenticator.initialize()
        self._api = Authenticator.authenticated_api()

    @staticmethod
    def file_sha(path: Path) -> str:
        file_hash = hashlib.sha256()
        block_size = 2 ** 16
        with open(path, 'rb') as f:
            chunk = f.read(block_size)
            while len(chunk) > 0:
                file_hash.update(chunk)
                chunk = f.read(block_size)  # Read the next block from the file
            return file_hash.hexdigest()

    def get_import_url(self, filename: str) -> Tuple[str, str]:
        params = GetUploadSignedUrlParams(filename)
        import_url_response: ExternalImportModelStorage = self._api.get_upload_signed_url(params)
        return import_url_response.url, import_url_response.file_name

    @staticmethod
    def upload_file(url: str, path: Path) -> None:
        with open(path, 'rb') as f:
            requests.put(url, f, headers={"content-type": "application/octet-stream"})

    def current_project_version(self) -> str:
        proj_id = self.project.project_id(self._api)
        return self._api.get_current_project_version(GetCurrentProjectVersionParams(proj_id)).version_id

    def _create_import_new_model_params(
            self, filename: str, branch_name: Optional[str] = None,
            version: Optional[str] = None, model_name: Optional[str] = None) -> ImportNewModelParams:
        proj_id = self.project.project_id(self._api)
        if not version:
            version = self.current_project_version()
        if not model_name:
            model_name = f'CLI_{datetime.utcnow().strftime("%m/%d/%Y_%H:%M:%S")}'

        additional_arguments = {}
        if branch_name:
            additional_arguments['branch_name'] = branch_name

        model_type = self.project.detect_model_type()
        import_model_type = ImportModelType(model_type.value)

        if model_type == ModelType.onnx:
            additional_arguments['transform_inputs'] = True

        return ImportNewModelParams(
            proj_id, filename, model_name, version, import_model_type, **additional_arguments)

    def start_import_job(self, filename: str, branch_name: Optional[str] = None,
                         version: Optional[str] = None, model_name: Optional[str] = None) -> str:
        params = self._create_import_new_model_params(filename, branch_name, version, model_name)

        response: ExternalImportModelStorageResponse = self._api.import_model(params)
        return response.import_model_job_id

    def import_model(self, content_hash: str, path: Path, branch_name: Optional[str] = None,
                     version: Optional[str] = None, model_name: Optional[str] = None) -> str:
        url, file_name = self.get_import_url(content_hash)
        Push.upload_file(url, path)
        return self.start_import_job(file_name, branch_name, version, model_name)

    def _parse_dataset(self, dataset_py_as_string: str):
        dataset_id = self.project.dataset_id(self._api)
        params = DatasetParseRequestParams(dataset_id, script=dataset_py_as_string)
        self._api.parse_dataset(params)

    def _save_dataset(self, dataset_py_as_string: str, secret_name: Optional[str] = None) -> DatasetVersion:
        dataset_id = self.project.dataset_id(self._api)

        params = SaveDatasetVersionParams(dataset_id, script=dataset_py_as_string,
                                          save_as_new=False, is_valid=False)
        if secret_name is not None:
            secret_id = self.find_secret_id(secret_name)
            params.secret_manager_id = secret_id

        dataset_response: Dataset = self._api.save_dataset_version(params).dataset

        return dataset_response.latest_version

    def save_and_parse_dataset(self, secret_name: Optional[str] = None) -> DatasetVersion:
        dataset_py_path = self.project.dataset_py_path()
        with open(str(dataset_py_path), "r") as f:
            dataset_py_as_string = f.read()
        return self._save_dataset(dataset_py_as_string, secret_name)

    @staticmethod
    def load_model_config_module(model_py_path: Path):
        if not model_py_path.is_file():
            raise ModelNotFound()

        spec = importlib.util.spec_from_file_location('tensorleap.model', model_py_path)
        model_module = importlib.util.module_from_spec(spec)

        sys.modules['tensorleap.model'] = model_module
        spec.loader.exec_module(model_module)
        return model_module

    @staticmethod
    def load_mapping_config_module(mapping_py_path: Path):
        if not mapping_py_path.is_file():
            raise MappingNotFound()

        spec = importlib.util.spec_from_file_location('tensorleap.mapping', mapping_py_path)
        model_module = importlib.util.module_from_spec(spec)

        sys.modules['tensorleap.mapping'] = model_module
        spec.loader.exec_module(model_module)
        return model_module

    def _push_dataset(self, secret_name: Optional[str]) -> DatasetVersion:
        dataset_id = self.project.dataset_id(self._api, throw_on_not_found=False)
        if dataset_id is None:
            print(f"New dataset detected. Dataset name: {self.project.detect_dataset()}")
            self.create_dataset()
        return self.save_and_parse_dataset(secret_name)

    def _push_model(self, branch_name: Optional[str], version: Optional[str], model_name: Optional[str]):
        serialized_model_path, content_hash = self.serialize_model()
        self.import_model(content_hash, serialized_model_path, branch_name, version, model_name)

    def parse_dataset(self) -> DatasetIntegParseResult:
        dataset_py_path = self.project.dataset_py_path()
        with open(str(dataset_py_path), "r") as f:
            dataset_py_as_string = f.read()
        leap_loader = LeapLoader(dataset_py_as_string)
        dataset_parse_result = leap_loader.check_dataset()
        if not dataset_parse_result.is_valid:
            print('\nFailed to parse dataset script.\n')
            error_message = dataset_parse_result.general_error
            if error_message is None:
                error_message = str([payload.display for payload in dataset_parse_result.payloads
                                     if not payload.is_passed])
            print(error_message)
            raise ParseDatasetFailed()

        return dataset_parse_result

    def _create_graph_with_mapping(self, dataset_version: DatasetVersion) -> LeapGraphEditor:
        serialized_model_path, _ = self.serialize_model()
        import_model_type = ImportModelTypeEnum(self.project.detect_model_type().value)
        model_graph = ModelParser().generate_model_graph(serialized_model_path, import_model_type)
        graph_editor = LeapGraphEditor(model_graph)

        mapping_py_path = self.project.mapping_py_path()
        mapping_module = Push.load_mapping_config_module(mapping_py_path)
        node_connections = mapping_module.NODE_CONNECTIONS

        graph_editor.add_connections_to_graph(node_connections)

        dataset_parse_result = self.parse_dataset()
        dataset_name = self.project.detect_dataset()

        graph_editor.add_dataset(dataset_name, dataset_version, dataset_parse_result)

        return graph_editor

    def _push_mapping(self, dataset_version: DatasetVersion, branch_name: Optional[str], model_name: Optional[str]):
        graph_editor = self._create_graph_with_mapping(dataset_version)
        project_id = self.project.project_id(self._api)
        model_graph = ModelGraph('version_cli@0.1.0', graph_editor.model_graph_dict())
        if branch_name is None:
            branch_name = "master"
        if model_name is None:
            model_name = time.strftime('%H:%M%p %Z on %b %d, %Y')
        add_version_params = AddVersionParams(
            project_id=project_id,
            model_graph=model_graph,
            branch_name=branch_name,
            description=model_name
        )
        self._api.add_version(add_version_params)

    # Returns path to serialized model in cache dir and content content_hash of the file
    def serialize_model(self) -> Tuple[Path, str]:
        model_py_path = self.project.model_py_path()
        _log.debug('Looking for model integration file', extra=dict(path=model_py_path))

        if not model_py_path.is_file():
            raise ModelNotFound()

        _log.info('Loading user model configuration', extra=dict(path=model_py_path))
        model_module = Push.load_model_config_module(model_py_path)

        if not hasattr(model_module, 'leap_save_model'):
            raise ModelEntryPointNotFound()

        suffix = f'.{self.project.detect_model_type().name}'
        _, tmp_model_file = tempfile.mkstemp(suffix=suffix)
        tmp_model_file = Path(tmp_model_file)

        _log.info('Invoking user leap_save_model', extra=dict(tgt_path=tmp_model_file))
        try:
            model_module.leap_save_model(tmp_model_file)
        except Exception as error:
            raise ModelSaveFailure() from error

        # Don't accumulate temp files with identical content
        # TODO: future enhancement: don't uploads to server if already uploaded before

        # File could exist but have 0 bytes because of mktemp
        if not tmp_model_file.exists() or tmp_model_file.stat().st_size == 0:
            raise ModelNotSaved()
        content_hash = Push.file_sha(tmp_model_file)
        cache_path = self.project.cache_dir().joinpath(content_hash + suffix)
        tmp_model_file.rename(cache_path)

        return cache_path, content_hash

    def _push_all(self, branch_name: Optional[str], version: Optional[str],
                  model_name: Optional[str], secret_name: Optional[str]):
        dataset_version = self._push_dataset(secret_name)
        if self.project.mapping_py_path().exists():
            self._push_mapping(dataset_version, branch_name, model_name)
        else:
            self._push_model(branch_name, version, model_name)

    def _create_project_if_not_exist(self):
        project_id = self.project.project_id(self._api, throw_on_not_found=False)
        if project_id is None:
            print(f"New project detected. Project name: {self.project.detect_project()}")
            self.create_project()

    def run(self, should_push_model_only, should_push_dataset_only,
            branch_name: Optional[str] = None, version: Optional[str] = None, model_name: Optional[str] = None,
            secret_name: Optional[str] = None):
        if should_push_dataset_only:
            self._push_dataset(secret_name)
        else:
            self._create_project_if_not_exist()
            if should_push_model_only:
                self._push_model(branch_name, version, model_name)
            else:
                self._push_all(branch_name, version, model_name, secret_name)

        print('Push command successfully completed')

    def create_project(self):
        project_name = self.project.detect_project()
        add_project_params = AddProjectParams(name=project_name, description="created by LeapCLI")
        self._api.add_project(add_project_params)

    def create_dataset(self):
        dataset_name = self.project.detect_dataset()
        add_dataset_params = NewDatasetParams(name=dataset_name)
        self._api.add_dataset(add_dataset_params)

    def find_secret_id(self, secret_name: str, throw_on_not_found=True) -> Optional[str]:
        matches = [secret.id for secret in self._api.get_secret_manager_list().results if secret.name == secret_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 0:
            if throw_on_not_found:
                raise SecretNotFoundException(secret_name)
            return None

        raise DatabaseAmbiguityException(f"Found more than two secrets with the same name. "
                                         f"Secret name: {secret_name}")
