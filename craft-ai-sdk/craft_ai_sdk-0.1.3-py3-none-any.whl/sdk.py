import base64
import os
import json
import requests

from . import CRAFT_AI_ENVIRONMENT_URL
from .utils import handle_data_store_response, handle_http_request


class CraftAiSdk:
    def __init__(
        self,
        token,
        environment_url=CRAFT_AI_ENVIRONMENT_URL,
    ):
        """Main class to instantiate

        Args:
            token (str): token, access key
            environment_url (str, optional): URL to CraftAI environment.
                Defaults to `CRAFT_AI_ENVIRONMENT_URL` environment variable.

        Raises:
            ValueError: if the environment_url is not defined
                or when the corresponding environment variable is not set.
        """
        self._session = requests.Session()

        if not environment_url:
            raise ValueError("Parameter 'environment_url' should be set")
        self.base_environment_url = f"{environment_url}/api/v1"

        # Add authorization token
        self._session.headers["Authorization"] = f"Bearer {token}"

    # _____ REQUESTS METHODS _____

    @handle_http_request
    def _get(self, url, params=None, **kwargs):
        return self._session.get(url, params=params, **kwargs)

    @handle_http_request
    def _post(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.post(url, data=data, params=params, files=files, **kwargs)

    @handle_http_request
    def _delete(self, url, **kwargs):
        return self._session.delete(url, **kwargs)

    # _____ STEPS _____

    def create_steps(self, repo, private_key):
        """Create pipeline steps from a source code located on a remote repository.

        Args:
            repo (str): remote repository url
            private_key (str): private SSH key related to the repository
        """
        url = f"{self.base_environment_url}/steps"
        data = {
            "private_key": private_key,
            "repo": repo,
        }
        self._post(url, data=data)

    def delete_one_step(self, step_name, version):
        """Delete one step

        Args:
            step_name (str): name of the step to delete
                as defined in the configuration file
            version (str): version of the step to delete
        """
        url = os.path.join(f"{self.base_environment_url}/steps", step_name)
        data = {
            "version": version,
        }
        self._delete(url, data=data)

    # _____ PIPELINES _____

    def create_pipeline(self, pipeline_name, pipeline_version, template_path):
        """Create and execute a pipeline as defined by a YAML template.

        Args:
            pipeline_name (str): name of the pipeline
            pipeline_version (str): version of the pipeline
            template_path (str): path to a YAML template file that defines the structure
                of the pipeline as a DAG

        Returns:
            str: id of the created pipeline
        """
        url = f"{self.base_environment_url}/pipelines"
        files = {
            "template": open(template_path, "rb"),
        }
        params = {
            "pipeline_name": pipeline_name,
            "version": pipeline_version,
        }

        resp = self._post(url, files=files, params=params)
        return resp["id"]

    def delete_pipeline(
        self,
        pipeline_name,
        pipeline_version,
    ):
        """Delete a pipeline identified by its name and id

        Args:
            pipeline_name (str): name of the pipeline
            pipeline_version (str): version of the pipeline
        """
        url = f"{self.base_environment_url}/pipelines"
        params = {
            "pipeline_name": pipeline_name,
            "version": pipeline_version,
        }
        self._delete(url, params=params)

    def get_pipeline_status(self, pipeline_name, pipeline_version):
        """Get the status of a pipeline identified by its name and version

        Args:
            pipeline_name (str): name of the pipeline
            pipeline_version (str): version of the pipeline

        Returns:
            dict: _description_
        """
        url = f"{self.base_environment_url}/pipelines/status"
        params = {
            "pipeline_name": pipeline_name,
            "version": pipeline_version,
        }
        return self._get(url, params=params)

    # _____ ENDPOINTS _____

    def create_endpoint(
        self,
        pipeline_id,
        endpoint_name,
        endpoint_params=None,
        allow_unknown_params=None,
    ):
        """Create a custom endpoint associated to a given pipeline

        Args:
            pipeline_id (str): id of the pipeline
            endpoint_name (str): name of the endpoint
            endpoint_params (dict of str: dict, optional): structure of the endpoint
                parameters. Each item defines a parameter which name is given by the key
                and which constraints (type and requirement) are given by the value.
                An item has the form
                [str: parameter name] : {
                    "required": [bool],
                    "type": [str in ["string", "number", "object", "array"]],
                }
                Defaults to None.
            allow_unknown_params (bool, optional): if `True` the custom endpoint allows
                other parameters not specified in `endpoint_params`. Defaults to None.
        """
        url = f"{self.base_environment_url}/endpoints"

        endpoint_params = {} if endpoint_params is None else endpoint_params
        data = {
            "pipeline_id": pipeline_id,
            "name": endpoint_name,
            "allow_unknown_params": allow_unknown_params,
            "body_params": endpoint_params,
        }
        # filter optional parameters
        data = {k: v for k, v in data.items() if v is not None}

        return self._post(url, json=data)

    def delete_endpoint(self, endpoint_name):
        """Delete an endpoint

        :param endpoint_name: name of the endpoint to be deleted
        :type endpoint_name: str
        """
        url = os.path.join(f"{self.base_environment_url}/endpoints", endpoint_name)
        return self._delete(url)

    def list_endpoints(self):
        """Get the list of all endpoints

        Returns:
            list of dict: list of endpoints represented as dict
        """
        url = f"{self.base_environment_url}/endpoints"
        return self._get(url)

    def get_endpoint(self, endpoint_name):
        """Get information of an endpoint

        Args:
            endpoint_name (str): name of the endpoint

        Returns:
            dict: endpoint information
        """
        url = os.path.join(f"{self.base_environment_url}/endpoints", endpoint_name)
        return self._get(url)

    def trigger_endpoint(self, endpoint_name, params=None):
        """Trigger an endpoint

        Args:
            endpoint_name (str): name of the endpoint
            params (dict): parameters to be provided to the endpoint

        Returns:
            _type_: _description_
        """
        url = os.path.join(
            f"{self.base_environment_url}/endpoints", endpoint_name, "trigger"
        )
        return self._post(url, json=params)

    # _____ DATA STORE _____

    def data_store_list_objects(self):
        """Get the list of the objects stored in the data store

        Returns:
            list of dict: List of objects information
        """
        url = f"{self.base_environment_url}/data-store/list"
        response = self._get(url)

        return response["listed_elem"]["contents"]

    def _get_upload_presigned_url(self):
        url = f"{self.base_environment_url}/data-store/upload"
        resp = self._get(url)["urlObject"]
        presigned_url, data = resp["url"], resp["fields"]

        # Extract prefix condition from the presigned url
        policy = data["Policy"]
        policy_decode = json.loads(base64.b64decode(policy))
        prefix_condition = policy_decode["conditions"][0]
        prefix = prefix_condition[-1]
        return presigned_url, data, prefix

    def data_store_upload_object(self, filepath_or_buffer, object_path_in_datastore):
        """Upload a file as an object into the data store

        Args:
            filepath_or_buffer (str): String, path to the file to be uploaded ; or
                file-like object implenting a read() method (e.g. via buildin
                `open` function). The file object must be opened in binary mode,
                not text mode.
            object_path_in_datastore (str): destination of the uploaded file
        """
        if isinstance(filepath_or_buffer, str):
            # this is a filepath: call the method again with a buffer
            with open(filepath_or_buffer, "rb") as file_buffer:
                return self.data_store_upload_object(
                    file_buffer, object_path_in_datastore
                )

        if not hasattr(filepath_or_buffer, "read"):  # not a readable buffer
            raise ValueError(
                "'filepath_or_buffer' must be either a string (filepath) or an object "
                "with a read() method (file-like object)."
            )

        file_buffer = filepath_or_buffer
        files = {"file": file_buffer}
        presigned_url, data, prefix = self._get_upload_presigned_url()
        data["key"] = os.path.join(prefix, object_path_in_datastore)

        resp = requests.post(url=presigned_url, data=data, files=files)
        handle_data_store_response(resp)

    def _get_download_presigned_url(self, object_path_in_datastore):
        url = f"{self.base_environment_url}/data-store/download"
        data = {
            "path_to_object": object_path_in_datastore,
        }
        presigned_url = self._post(url, data=data)["signedUrl"]
        return presigned_url

    def data_store_download_object(self, object_path_in_datastore, filepath_or_buffer):
        """Download an object in the data store and save it into a file

        Args:
            object_path_in_datastore (str): location of the file to download
            filepath_or_buffer (str or file-like object):
                String, filepath to save the file to ; or a file-like object
                implementing a write() method, (e.g. via builtin `open` function).

        Returns:
            str: content of the file
        """
        presigned_url = self._get_download_presigned_url(object_path_in_datastore)
        resp = requests.get(presigned_url)
        object_content = handle_data_store_response(resp)

        if isinstance(filepath_or_buffer, str):  # filepath
            with open(filepath_or_buffer, "w") as f:
                f.write(object_content)
        elif hasattr(filepath_or_buffer, "write"):  # writable buffer
            filepath_or_buffer.write(object_content)
        else:
            raise ValueError(
                "'filepath_or_buffer' must be either a string (filepath) or an object "
                "with a write() method (file-like object)."
            )

    def data_store_delete_object(self, object_path_in_datastore):
        """Delete a file on the datastore

        Args:
            object_path_in_datastore (str): location of the file to delete on the store
        """
        url = f"{self.base_environment_url}/data-store/delete"
        data = {
            "path_to_object": object_path_in_datastore,
        }
        self._delete(url, data=data)
