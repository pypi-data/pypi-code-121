import time

import grpc
import pkg_resources
import requests
from google.protobuf.empty_pb2 import Empty
from grpc import ChannelConnectivity
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import featurestore
import featurestore.core.CoreService_pb2 as pb
from featurestore.core import CoreService_pb2_grpc, interactive_console
from featurestore.core.auth import AuthWrapper
from featurestore.core.client_config import ClientConfig
from featurestore.core.collections.jobs import Jobs
from featurestore.core.collections.projects import Projects
from featurestore.core.config import ConfigUtils
from featurestore.core.credentials import CredentialsHelper
from featurestore.core.data_source_wrappers import SparkDataFrame, get_raw_data_location
from featurestore.core.entities.extract_schema_job import ExtractSchemaJob
from featurestore.core.interceptors import (
    AuthClientInterceptor,
    ExponentialBackoff,
    RetryOnRpcErrorClientInterceptor,
)
from featurestore.core.schema import Schema


class Client:
    def __init__(
        self,
        url: str,
        secure: bool = False,
        root_certificates: str = None,
        config: ClientConfig = ClientConfig(),
    ):
        self._client_config = config
        options = [
            ("grpc.primary_user_agent", "feature-store-py-cli/SUBST_FS_VERSION"),
        ]
        if secure:
            default_root_certs = pkg_resources.resource_filename(
                "featurestore", "_credentials/roots.pem"
            )
            credentials = self._get_channel_credentials(
                root_certificates if root_certificates else default_root_certs
            )
            channel = grpc.secure_channel(url, credentials, options)
        else:
            channel = grpc.insecure_channel(url, options)

        interceptors = [
            RetryOnRpcErrorClientInterceptor(
                max_attempts=5,
                sleeping_policy=ExponentialBackoff(
                    init_backoff_ms=1000, max_backoff_ms=30000, multiplier=4
                ),
                status_for_retry=(
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                ),
            ),
            AuthClientInterceptor(self),
        ]
        self._channel = grpc.intercept_channel(channel, *interceptors)
        self._connection_state = None
        self._config = ConfigUtils.collect_properties()

        def on_connectivity_change(value):
            self._connection_state = value
            return

        self._channel.subscribe(on_connectivity_change, try_to_connect=True)
        if config.wait_for_backend:
            while self._connection_state != ChannelConnectivity.READY:
                print("Connecting to the server {} ...".format(url))
                time.sleep(2)
        else:
            print("Connected to server {}".format(url))

        self._stub = CoreService_pb2_grpc.CoreServiceStub(self._channel)
        self.auth = AuthWrapper(self._stub)
        self.projects = Projects(self._stub)
        self.jobs = Jobs(self._stub)
        if (
            self.get_version() != featurestore.__version__
            and featurestore.__version__ != "dev"
        ):
            raise Exception(
                f"Feature Store Client v{featurestore.__version__} is not compatible with Server v{self.get_version()}"
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()
        return False

    def close(self):
        self._channel.close()

    def get_version(self) -> str:
        request = Empty()
        response = self._stub.GetVersion(request)
        return response.version

    def extract_schema_from_source_async(
        self, raw_data_location, credentials=None
    ) -> ExtractSchemaJob:
        request = pb.StartExtractSchemaJobRequest()
        if isinstance(raw_data_location, SparkDataFrame):
            raw_data_location._write_to_cache(self._stub)
            data_source = raw_data_location._get_cache_location()
        else:
            data_source = get_raw_data_location(raw_data_location)
        request.raw_data_location.CopyFrom(data_source)
        CredentialsHelper.set_credentials(request, data_source, credentials)
        job_id = self._stub.StartExtractSchemaJob(request)
        return ExtractSchemaJob(self._stub, job_id)

    @interactive_console.record_stats
    def extract_schema_from_source(self, raw_data_location, credentials=None) -> Schema:
        job = self.extract_schema_from_source_async(raw_data_location, credentials)
        while not job.is_done():
            job.show_progress()
            time.sleep(2)
        job.show_progress()  # there is possibility that some progress was pushed before finishing job
        return job.get_result()

    def _has_online_retrieve_permissions(self, project_name, feature_set_name):
        request = pb.HasPermissionToRetrieveRequest()
        request.project_name = project_name
        request.feature_set_name = feature_set_name
        response = self._stub.HasPermissionToRetrieve(request)
        return response.has_retrieve_permission

    def online_retrieve(
        self,
        project_name,
        feature_set_name,
        primary_key,
        secondary_key=None,
        verify=False,
    ):
        # this method will be eventually removed, H2O's online is using method onlineRetrieve on feature set entity
        if not self._has_online_retrieve_permissions(project_name, feature_set_name):
            raise Exception(
                "User does not have enough permissions to execute online retrieve call"
            )
        resp = self._stub.GetOnlineRetrieveMeta(Empty())
        if not resp.is_enabled:
            raise Exception(
                "Online feature store integration is not enabled on the backend"
            )
        url = (
            resp.base_online_url
            + requests.utils.quote(project_name)
            + "/"
            + requests.utils.quote(feature_set_name)
            + "/"
            + requests.utils.quote(primary_key)
        )
        if secondary_key:
            params = dict(secondaryKey=requests.utils.quote(secondary_key))
        else:
            params = dict(secondaryKey="")
        session = requests.Session()
        session.auth = (resp.username, resp.password)
        session.headers.update({"user-id": self.auth.get_active_user().id})
        if not verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = session.get(url, params=params, verify=verify).json()
        return response

    def show_progress(self, interactive):
        ConfigUtils.set_property(
            self._config, ConfigUtils.INTERACTIVE_LOGGING, str(interactive)
        )

    @staticmethod
    def _get_channel_credentials(cert_location: str) -> grpc.ChannelCredentials:
        if cert_location is not None:
            with open(cert_location, "rb") as cert_file:
                return grpc.ssl_channel_credentials(cert_file.read())
        return grpc.ssl_channel_credentials(None)
