import json
import logging
import time
from typing import Optional

import requests
import socketio

from ..const import REFRESH_ACCESS_TOKEN_IN_SEC, SERVICE_FOUNDRY_SERVER
from ..exceptions import ConfigurationException
from ..model.session import ServiceFoundrySession
from ..session_factory import get_session
from ..util import request_handling, upload_package_to_s3

logger = logging.getLogger(__name__)

VERSION_PREFIX = "v1"


def _get_or_throw(definition, key, error_message):
    if key not in definition:
        raise ConfigurationException(error_message)
    return definition[key]


class ServiceFoundryServiceClient:
    def __init__(
        self, session: Optional[ServiceFoundrySession], host=SERVICE_FOUNDRY_SERVER
    ):
        self.host = host
        self.session = session

    @classmethod
    def get_client(cls, auth_required=True):
        # Would be ok to prefer auth token from API instead of local session file
        if auth_required:
            session = get_session()
            if session:
                return cls(session=session)
            else:
                raise Exception("Please login before running this command.")
        else:
            # TODO (chiragjn): All usages should be made to handle session=None
            return cls(session=None)

    def check_and_refresh_session(self):
        decoded = self.session.decode()
        expiry_second = decoded["exp"]
        if expiry_second - time.time() < REFRESH_ACCESS_TOKEN_IN_SEC:
            logger.info(
                f"Going to refresh the access token {expiry_second - time.time()}."
            )
            self.session.refresh_access_token()

    def _get_header(self):
        return {"Authorization": f"Bearer {self.session.access_token}"}

    def list_workspace(self):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def create_workspace(self, cluster_id, name):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace"
        res = requests.post(
            url,
            data={"name": name, "clusterId": cluster_id},
            headers=self._get_header(),
        )
        return request_handling(res)

    def remove_workspace(self, workspace_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace/{workspace_id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def get_workspace_by_name(self, workspace_name, cluster_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace"
        res = requests.get(
            url,
            headers=self._get_header(),
            params={"name": workspace_name, "clusterId": cluster_id},
        )
        return request_handling(res)

    def get_workspace(self, workspace_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace/{workspace_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def list_service(self):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/service"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def list_service_by_workspace(self, workspace_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/workspace/{workspace_id}/services"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def remove_service(self, service_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/service/{service_id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def get_service(self, service_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/service/{service_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def list_deployment(self, service_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/service/{service_id}/deployments"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def get_deployment(self, deployment_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/deployment/{deployment_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def create_cluster(
        self, name, region, aws_account_id, cluster_name, ca_data, server_url
    ):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/cluster"
        res = requests.post(
            url,
            data={
                "id": name,
                "region": region,
                "authData": {
                    "awsAccountID": aws_account_id,
                    "clusterName": cluster_name,
                    "caData": ca_data,
                    "serverUrl": server_url,
                },
            },
            headers=self._get_header(),
        )
        return request_handling(res)

    def list_cluster(self):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/cluster"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def get_cluster(self, cluster_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/cluster/{cluster_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def remove_cluster(self, cluster_id):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/cluster/{cluster_id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def get_presigned_url(self, space_name, service_name, env):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/deployment/code-upload-url"
        res = requests.post(
            url,
            data={
                "workspaceFqn": space_name,
                "serviceName": service_name,
                "stage": env,
            },
            headers=self._get_header(),
        )
        return request_handling(res)

    # @TODO Get rid of env from backend and here
    def build_and_deploy(self, service_def, package_zip, env="default"):
        self.check_and_refresh_session()
        workspace = service_def["spec"]["workspace"]

        http_response = self.get_presigned_url(
            workspace, service_def["spec"]["name"], env
        )
        upload_package_to_s3(http_response, package_zip)

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/deployment"
        data = {
            "workspaceFqn": workspace,
            "componentDef": service_def,
            "s3Bucket": http_response["s3Bucket"],
            "s3Key": http_response["s3Key"],
        }
        deploy_response = requests.post(url, json=data, headers=self._get_header())
        return request_handling(deploy_response)

    def create_secret_group(self, name):
        self.check_and_refresh_session()
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret-group/"
        res = requests.post(url, headers=self._get_header(), json={"name": name})
        return request_handling(res)

    def delete_secret_group(self, id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret-group/{id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def get_secret_group(self, id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret-group/{id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def create_secret(self, secret_group_id, key, value):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret/"
        res = requests.post(
            url,
            headers=self._get_header(),
            json={"secretGroupId": secret_group_id, "key": key, "value": value},
        )
        return request_handling(res)

    def delete_secret(self, id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret/{id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def get_secret(self, id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret/{id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def get_secrets_in_group(self, secret_group_id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret/list-by-secret-group/{secret_group_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def get_secret_groups(self):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/secret-group/findAll"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def tail_logs(
        self, runId, callback=lambda log_line: print(log_line, end=""), wait=False
    ):
        self.check_and_refresh_session()
        sio = socketio.Client(request_timeout=60)
        callback("Waiting for the task to start...\n")

        @sio.event
        def logs(data):
            try:
                log_line = json.loads(data)["body"]["log"]
                callback(log_line)
            except Exception:
                pass

        # TODO: We are limiting the behavior to pure websocket since we were intermittently getting a 400
        # when the library was attempting to poll. Need to debug this further.
        sio.connect(SERVICE_FOUNDRY_SERVER, transports="websocket")
        sio.emit("logs", json.dumps({"runId": runId, "startTs": "0"}))
        if wait:
            sio.wait()

    def fetch_logs(self, runId):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/logs/runs/{runId}?startTs=0&endTs=5000000000&limit=1000&direction=asc"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def get_authorization_for_resource(self, resource_type, resource_id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/authorize/{resource_type}/{resource_id}"
        res = requests.get(url, headers=self._get_header())
        return request_handling(res)

    def create_authorization(self, resource_id, resource_type, user_id, role):
        # @TODO instead of user_id pass emailID. Need to be done once API is available on auth.
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/authorize"
        res = requests.post(
            url,
            headers=self._get_header(),
            json={
                "resourceId": resource_id,
                "resourceType": resource_type,
                "userName": user_id,
                "userType": "USER",
                "role": role,
            },
        )
        return request_handling(res)

    def delete_authorization(self, id):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/authorize/{id}"
        res = requests.delete(url, headers=self._get_header())
        return request_handling(res)

    def update_authorization(self, id, role):
        self.check_and_refresh_session()

        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/authorize"
        res = requests.patch(
            url, headers=self._get_header(), json={"id": id, "role": role}
        )
        return request_handling(res)

    def get_templates_list(self):
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/template"
        res = requests.get(url)
        return request_handling(res)

    def get_template_by_id(self, template_id):
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/template/{template_id}"
        res = requests.get(url)
        return request_handling(res)

    def get_base_by_id(self, base_id):
        url = f"{SERVICE_FOUNDRY_SERVER}/{VERSION_PREFIX}/template/base/{base_id}"
        res = requests.get(url)
        return request_handling(res)
