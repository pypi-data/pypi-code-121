import os
from pprint import pprint

import requests

from bodosdk.api.auth import AuthApi
from bodosdk.api.cluster import ClusterApi
from bodosdk.api.job import JobApi
from bodosdk.api.request_wrapper import RequestWrapper
from bodosdk.client.cluster import ClusterClient
from bodosdk.client.job import JobClient
from bodosdk.exc import APIKeysMissing
from bodosdk.models import APIKeys, WorkspaceKeys


class BodoClient:
    job: JobClient
    cluster: ClusterClient

    def __init__(self, auth_api: AuthApi, job_client: JobClient, cluster_client: ClusterClient):
        self._auth_api = auth_api
        self.job = job_client
        self.cluster = cluster_client

    def switch_workspace(self, auth: WorkspaceKeys):
        """
        You can provide WorkspaceKeys to other workspace. This way you don't need to recrete BodoClient if you will
        to use other workspace.

        :param auth: a set of client_id / seceret_key used for auth token generation
        :type auth: WorkspaceKeys
        :return: None
        :rtype: None
        :raises Unauthorized:

        workspaceA = WorkspaceKeys(client_id='x', secret_key='y')
        workspaceB = WorkspaceKeys(client_id='a', secret_key='b')

        bodo_client = get_bodo_client(auth)
        #list jobs in workspace A
        bodo_client.job.list()
        bodo_client.switch_workspace(workspaceB)
        #list jobs in workspace B
        bodo_client.job.list()
        """
        self._auth_api.switch_workspace(auth)


def get_bodo_client(auth: APIKeys=None, api_url="https://api.bodo.ai/api", auth_url='https://prod-auth.bodo.ai', print_logs=False):
    """


    :param auth: a set of client_id / seceret_key used for auth token generation
    :type auth: APIKeys
    :param api_url: api address of BodoPlatform
    :type api_url: str
    :param auth_url: api address of BodoAuthentication
    :type auth_url: str
    :param print_logs: set to True if you want to print all requests performed
    :type print_logs: boolean
    :return: BodoClient
    """
    if not auth:
        client_id = os.environ.get('BODO_CLIENT_ID')
        secret_key = os.environ.get('BODO_SECRET_KEY')
        if client_id and secret_key:
            auth = APIKeys(
                client_id=client_id,
                secret_key=secret_key
            )
        else:
            raise APIKeysMissing
    auth_api = AuthApi(auth, auth_url, RequestWrapper(print_logs))
    job_client = JobClient(JobApi(auth_api, api_url, RequestWrapper(print_logs)))
    cluster_client = ClusterClient(ClusterApi(auth_api, api_url, RequestWrapper(print_logs)))
    return BodoClient(auth_api, job_client, cluster_client)
