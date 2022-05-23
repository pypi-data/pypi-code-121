import io
import json
import logging
import os
import mimetypes
from io import BytesIO
from time import sleep
from uuid import UUID

import requests
from typing import Dict, List, Optional, Callable, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from autoretouch.api_client.authenticator import Authenticator
from autoretouch.api_client.model import (
    ApiConfig,
    Organization,
    Page,
    Workflow,
    DeviceCodeResponse,
    WorkflowExecution,
    Credentials,
)

__all__ = [
    "AutoRetouchAPIClient",
    "DEFAULT_API_CONFIG"
]

logger = logging.getLogger("autoretouch-python-client")

DEFAULT_API_CONFIG = ApiConfig(
    BASE_API_URL="https://api.autoretouch.com",
    BASE_API_URL_CURRENT="https://api.autoretouch.com/v1",
    CLIENT_ID="V8EkfbxtBi93cAySTVWAecEum4d6pt4J",
    SCOPE="offline_access",
    AUDIENCE="https://api.autoretouch.com",
    AUTH_DOMAIN="https://auth.autoretouch.com",
)
CONFIG_ROOT = os.path.join(os.path.expanduser("~"), ".config")
AR_CREDENTIALS = os.environ.get(
    "AUTORETOUCH_CREDENTIALS_PATH",
    os.path.join(CONFIG_ROOT, "autoretouch-credentials.json")
)
AR_REFRESH_TOKEN = os.environ.get(
    "AUTORETOUCH_REFRESH_TOKEN", None
)
USER_CONFIG_PATH = os.path.join(CONFIG_ROOT, "autoretouch-config.json")
if os.path.isfile(USER_CONFIG_PATH):
    USER_CONFIG = json.load(open(USER_CONFIG_PATH, "r"))
else:
    USER_CONFIG = {
        "organization": {"id": None, "name": None},
        "workflow": {"name": None, "id": None}
    }
DEFAULT_ORG_ID = os.environ.get(
    "AUTORETOUCH_ORGANIZATION_ID",
    USER_CONFIG["organization"]["id"]
)
DEFAULT_WORKFLOW_ID = os.environ.get(
    "AUTORETOUCH_WORKFLOW_ID",
    USER_CONFIG["workflow"]["id"]
)
DEFAULT_USER_AGENT = "Autoretouch-Python-Api-Client-0.0.2"

T = TypeVar("T", bound=Callable)


class AutoRetouchAPIClient:
    """
    autoRetouch API client

    :param organization_id:
    :param api_config:
    :param credentials_path: optional path to a .json credential file
    :param refresh_token: optional refresh_token for requesting up-to-dates access_token
    :param user_agent:
    :param save_credentials: whether the credentials should be saved. Default: True
    """

    def __init__(
            self,
            organization_id: Optional[Union[str, UUID]] = DEFAULT_ORG_ID,
            workflow_id: Optional[Union[str, UUID]] = DEFAULT_WORKFLOW_ID,
            api_config: ApiConfig = DEFAULT_API_CONFIG,
            credentials_path: Optional[str] = AR_CREDENTIALS,
            refresh_token: Optional[str] = AR_REFRESH_TOKEN,
            user_agent: str = DEFAULT_USER_AGENT,
            save_credentials: bool = True,
    ):
        self.api_config = api_config
        self.user_agent = user_agent
        self.auth = Authenticator(
            self, credentials_path, refresh_token, save_credentials
        )
        self.organization_id = organization_id
        self.workflow_id = workflow_id

    @property
    def base_headers(self) -> dict:
        return {
            "User-Agent": self.user_agent,
            "Authorization": f"Bearer {self.auth.credentials.access_token}",
        }

    def get_api_status(self) -> int:
        return requests.get(f"{self.api_config.BASE_API_URL}/health").status_code

    # ****** AUTH ENDPOINTS ******

    def get_device_code(self) -> DeviceCodeResponse:
        logger.info("requesting new device code...")
        url = f"{self.api_config.AUTH_DOMAIN}/oauth/device/code"
        payload = f"client_id={self.api_config.CLIENT_ID}&scope={self.api_config.SCOPE}&audience={self.api_config.AUDIENCE}"
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url=url, headers=headers, data=payload)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        logger.info("new device code request was successful")
        return DeviceCodeResponse.from_dict(response.json())

    def get_credentials_from_device_code(self, device_code: str) -> Credentials:
        logger.info("requesting new credentials from device code...")
        url = f"{self.api_config.AUTH_DOMAIN}/oauth/token"
        payload = (
            f"grant_type=urn:ietf:params:oauth:grant-type:device_code"
            f"&device_code={device_code}"
            f"&client_id={self.api_config.CLIENT_ID}"
        )
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url=url, headers=headers, data=payload)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        logger.info("successfully obtained new credentials")
        return Credentials(**response.json())

    def get_credentials_from_refresh_token(self, refresh_token: str) -> Credentials:
        logger.info("requesting new credentials from refresh token...")
        url = f"{self.api_config.AUTH_DOMAIN}/oauth/token"
        payload = (
            f"grant_type=refresh_token"
            f"&refresh_token={refresh_token}"
            f"&client_id={self.api_config.CLIENT_ID}"
        )
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url=url, headers=headers, data=payload)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        logger.info("successfully obtained new credentials")
        return Credentials(refresh_token=refresh_token, **response.json())

    def revoke_refresh_token(self, refresh_token: str) -> int:
        logger.info("revoking refresh token...")
        url = f"{self.api_config.AUTH_DOMAIN}/oauth/revoke"
        payload = {"client_id": self.api_config.CLIENT_ID, "token": refresh_token}
        headers = {"User-Agent": self.user_agent, "Content-Type": "application/json"}
        response = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        logger.info("successfully revoked refresh token")
        return response.status_code

    def authenticated(self):
        auth = self.auth
        if auth.credentials is None:
            auth.authenticate()
        elif auth.token_expired:
            auth.refresh_credentials()

    def login(self):
        logger.info("logging in...")
        self.auth.authenticate()
        logger.info("logged in!")
        return self

    def logout(self):
        logger.info("logging out...")
        self.authenticated()
        self.auth.logout()
        logger.info("logged out!")
        return self

    def revoke_credentials(self):
        logger.info("revoking credentials...")
        self.authenticated()
        self.auth.revoke_refresh_token()
        logger.info("successfully revoked credentials")
        return self

    # ****** API ******

    def get_organizations(self) -> List[Organization]:
        logger.info("getting organizations...")
        self.authenticated()
        url = f"{self.api_config.BASE_API_URL_CURRENT}/organization?limit=50&offset=0"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        page = Page(**response.json())
        organizations = [Organization.from_dict(entry) for entry in page.entries]
        return organizations

    def get_organization(self, organization_id: Optional[UUID] = None) -> Organization:
        logger.info("getting organization...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/organization/{organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return Organization.from_dict(response.json())

    def get_workflows(self, organization_id: Optional[UUID] = None) -> List[Workflow]:
        logger.info("getting workflows...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow?limit=50&offset=0&organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        page = Page(**response.json())
        workflows = [Workflow.from_dict(entry) for entry in page.entries]
        return workflows

    def get_workflow(self, workflow_id: UUID, organization_id: Optional[UUID] = None, ) -> Workflow:
        logger.info("getting workflow...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/{workflow_id}?organization={organization_id}"
        response = requests.get(url, headers=self.base_headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return Workflow.from_dict(response.json())

    def get_workflow_executions(
            self, workflow_id: UUID, organization_id: Optional[UUID] = None
    ) -> Page:
        logger.info("getting workflow executions...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution?workflow={workflow_id}&limit=50&offset=0&organization={organization_id}"
        response = requests.get(url=url, headers=self.base_headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        page = Page(**response.json())
        page.entries = [WorkflowExecution.from_dict(entry) for entry in page.entries]
        return page

    def upload_image(
            self, image_path: str, organization_id: Optional[UUID] = None
    ) -> str:
        logger.info("uploading image...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/upload?organization={organization_id}"
        with open(image_path, "rb") as file:
            filename = os.path.basename(file.name)
            mimetype, _ = mimetypes.guess_type(file.name)
            files = [("file", (filename, file, mimetype))]
            response = requests.post(url=url, headers=self.base_headers, files=files)
            logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content.decode(response.encoding)

    def upload_image_from_stream(self, open_file: io.BufferedReader, organization_id: Optional[UUID] = None) -> str:
        logger.info("uploading image from stream...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/upload?organization={organization_id}"
        filename = os.path.basename(open_file.name) or "image"
        mimetype, _ = mimetypes.guess_type(open_file.name)
        files = [("file", (filename, open_file, mimetype))]
        response = requests.post(url=url, headers=self.base_headers, files=files)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content.decode(response.encoding)

    def upload_image_from_bytes(
            self,
            image_content: bytes,
            image_name: str,
            mimetype: Optional[str] = None,
            organization_id: Optional[UUID] = None,
    ) -> str:
        logger.info("uploading image from bytes...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/upload?organization={organization_id}"
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(image_name)
        with BytesIO(image_content) as file:
            files = [("file", (image_name, file, mimetype))]
            response = requests.post(url=url, headers=self.base_headers, files=files)
            logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content.decode(response.encoding)

    def create_workflow_execution_for_image_file(
            self,
            workflow_id: UUID,
            image_path: str,
            labels: Optional[Dict[str, str]] = None,
            workflow_version_id: Optional[UUID] = None,
            organization_id: Optional[UUID] = None,
    ) -> UUID:
        logger.info("creating workflow execution for image file...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        labels = labels or {}
        labels_encoded = "".join(
            [f"&label[{key}]={value}" for key, value in labels.items()]
        )
        version_str = f"&version={workflow_version_id}" if workflow_version_id else ""
        url = (
            f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/create"
            f"?workflow={workflow_id}"
            f"{version_str}"
            f"&organization={organization_id}"
            f"{labels_encoded}"
        )
        logger.info(f"Starting to process {image_path} with workflow {workflow_id}")
        with open(image_path, "rb") as file:
            filename = os.path.basename(file.name)
            mimetype, _ = mimetypes.guess_type(file.name)
            files = [("file", (filename, file, mimetype))]
            response = requests.post(url=url, headers=self.base_headers, files=files)
            logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return UUID(response.content.decode(response.encoding))

    def create_workflow_execution_for_image_reference(
            self,
            workflow_id: UUID,
            image_content_hash: str,
            image_name: str,
            labels: Optional[Dict[str, str]] = None,
            workflow_version_id: Optional[UUID] = None,
            organization_id: Optional[UUID] = None,
    ) -> UUID:
        logger.info("creating workflow execution for image reference...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        version_str = f"&version={workflow_version_id}" if workflow_version_id else ""
        url = (
            f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/create"
            f"?workflow={workflow_id}"
            f"{version_str}"
            f"&organization={organization_id}"
        )
        headers = {**self.base_headers, "Content-Type": "application/json"}
        mimetype, _ = mimetypes.guess_type(image_name)
        payload = {
            "image": {
                "name": image_name,
                "contentHash": image_content_hash,
                "contentType": mimetype,
            },
            **({"labels": labels} if labels else {}),
        }

        response = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return UUID(response.content.decode(response.encoding))

    def get_workflow_execution_details(
            self, workflow_execution_id: UUID, organization_id: Optional[UUID] = None
    ) -> WorkflowExecution:
        logger.info("getting workflow execution details...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/{workflow_execution_id}?organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return WorkflowExecution.from_dict(response.json())

    def get_workflow_execution_status_blocking(
            self, workflow_execution_id: UUID, organization_id: Optional[UUID] = None
    ) -> str:
        logger.info("getting workflow execution status...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/{workflow_execution_id}/status?organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "text/event-stream"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        # TODO: decode event stream format
        return response.content.decode(response.encoding)

    def download_image(
            self,
            image_content_hash: str,
            image_name: str,
            organization_id: Optional[UUID] = None,
    ) -> bytes:
        logger.info("downloading image...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/image/{image_content_hash}/{image_name}?organization={organization_id}"
        response = requests.get(url=url, headers=self.base_headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content

    def download_result_blocking(
            self, workflow_execution_id: UUID, organization_id: Optional[UUID] = None
    ) -> bytes:
        logger.info("downloading result (blocking)...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/{workflow_execution_id}/result/default?organization={organization_id}"
        response = requests.get(url=url, headers=self.base_headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content

    def download_result(
            self, result_path: str, organization_id: Optional[UUID] = None
    ) -> bytes:
        logger.info("downloading result...")
        self.authenticated()
        assert result_path.startswith("/image/")
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}{result_path}?organization={organization_id}"
        response = requests.get(url=url, headers=self.base_headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content

    def retry_workflow_execution(
            self, workflow_execution_id: UUID, organization_id: Optional[UUID] = None
    ) -> int:
        logger.info("retrying workflow execution...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/{workflow_execution_id}/retry?organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.post(url=url, headers=headers, data={})
        logger.debug(f"{url} answered with status {response.status_code}")
        return response.status_code

    def get_balance(self, organization_id: Optional[UUID] = None) -> int:
        logger.info("getting balance...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/organization/balance?organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        response = requests.get(url=url, headers=headers)
        logger.debug(f"{url} answered with status {response.status_code}")
        response.raise_for_status()
        return response.content

    # ****** HIGH-LEVEL METHODS ******

    def send_feedback(
            self,
            workflow_execution_id: UUID,
            thumbs_up: bool,
            expected_images_content_hashes: List[str] = [],
            organization_id: Optional[UUID] = None,
    ):
        logger.info("sending feedback...")
        self.authenticated()
        organization_id = self._get_organization_id(organization_id)
        url = f"{self.api_config.BASE_API_URL_CURRENT}/workflow/execution/{workflow_execution_id}/feedback?organization={organization_id}"
        headers = {**self.base_headers, "Content-Type": "application/json"}
        payload = {
            "thumbsUp": thumbs_up,
            "expectedImages": expected_images_content_hashes,
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

    def process_image(
            self,
            image_path: str,
            output_dir: str,
            workflow_id: Optional[UUID] = None,
            organization_id: Optional[UUID] = None
    ):
        """upload image, start workflow, download result to `output_dir`"""
        organization_id = self._get_organization_id(organization_id)
        workflow_id = self._get_workflow_id(workflow_id)
        execution_id = self.create_workflow_execution_for_image_file(
            workflow_id, image_path, organization_id=organization_id
        )
        while True:
            execution = self.get_workflow_execution_details(execution_id)
            if execution.status in ("COMPLETED", "FAILED"):
                break
            else:
                sleep(2.0)
        if execution.status == "FAILED":
            raise RuntimeWarning(f"execution failed on server")

        result = self.download_result(execution.resultPath)
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, os.path.split(image_path)[-1]), "wb") as f:
            f.write(result)

    @staticmethod
    def find_images(image_dir: str) -> List[str]:
        return [
            *filter(
                lambda f: os.path.splitext(f)[-1] in {".jpeg", ".jpg", ".png", ".tif", ".tiff"},
                os.listdir(image_dir),
            )
        ]

    def process_folder(
            self,
            image_dir: str,
            target_dir: str,
            workflow_id: Optional[UUID] = None,
            organization_id: Optional[UUID] = None
    ):
        """apply a workflow to a directory of images and download the results to `target_dir`"""
        organization_id = self._get_organization_id(organization_id)
        workflow_id = self._get_workflow_id(workflow_id)
        image_paths = self.find_images(image_dir)
        executor = ThreadPoolExecutor(max_workers=min(200, len(image_paths)))
        futures_to_images = {}
        for path in image_paths:
            path = os.path.join(image_dir, path)
            future = executor.submit(
                self.process_image, path, target_dir, workflow_id, organization_id
            )
            futures_to_images[future] = path
        for future in as_completed(futures_to_images):
            path = futures_to_images[future]
            try:
                future.result()
                logger.info(f"Processed {path} successfully")
            except Exception as e:
                logger.error(f"Execution failed for {path}: {e}")

    # ****** HELPERS ******

    def _get_organization_id(self, passed_in_value):
        value = self.organization_id or passed_in_value
        if value is None:
            raise ValueError(
                "Expected `organization_id` to not be None."
                " Either set the client instance attribute "
                "or passed it as kwarg when calling a client's method."
            )
        logger.info(f"using {'' if value == passed_in_value else 'default'} organization id: {value}")
        return value

    def _get_workflow_id(self, passed_in_value):
        value = self.workflow_id or passed_in_value
        if value is None:
            raise ValueError(
                "Expected `workflow_id` to not be None."
                " Either set the client instance attribute "
                "or passed it as kwarg when calling a client's method."
            )
        logger.info(f"using {'' if value == passed_in_value else 'default'} workflow id: {value}")
        return value
