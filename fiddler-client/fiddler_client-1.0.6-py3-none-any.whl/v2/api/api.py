from fiddler.libs.http_client import Client as PythonHttpClient
from fiddler.utils import logging

# @todo: This is v1 implementation needs to have a proper v2 approach
from fiddler.v2.api.dataset_mixin import DatasetMixin
from fiddler.v2.api.events_mixin import EventsMixin
from fiddler.v2.api.job_mixin import JobMixin
from fiddler.v2.api.model_mixin import ModelMixin
from fiddler.v2.api.project_mixin import ProjectMixin

logger = logging.getLogger(__name__)
URL_PREFIX = '/v2'


class Client(ModelMixin, DatasetMixin, ProjectMixin, EventsMixin, JobMixin):
    def __init__(
        self, url: str, organization_name: str, auth_token: str, timeout: int = None
    ) -> None:
        self.url = url.rstrip('/')
        self.auth_token = auth_token
        self.organization_name = organization_name
        self.request_headers = {'Authorization': f'Bearer {auth_token}'}
        self.timeout = timeout
        self.client = self._get_http_client()

    def _get_http_client(self, request_headers=None):
        request_headers = request_headers if request_headers else self.request_headers

        return PythonHttpClient(
            host=self.url + URL_PREFIX,
            request_headers=request_headers,
            timeout=self.timeout,
        )
