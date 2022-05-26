import json
from mlplatform_lib.api_client import ApiClient
from mlplatform_lib.hyperdata.hyperdata_http_client import HyperdataHttpClient
import requests
from mlplatform_lib.utils.print_utils import print_header


class HyperdataLocalChecker:
    def __init__(self, api_client: ApiClient):
        self.hyperdata_addr = api_client.hyperdata_addr
        self.proauth_addr = api_client.proauth_addr
        self.user_id = api_client.user_id
        self.user_password = api_client.user_password
        self.project_name = api_client.project_name
        self.hyperdata_client = HyperdataHttpClient(hd_addr=self.hyperdata_addr, api_client=api_client)

        # generated
        self.hyperdata_client = None
        self.access_token = None
        self.refresh_token = None
        self.hyperdata_token_header = None
        self.project_id = None

    def _check_hyperdata_proauth_server_connect(self):
        print_header(f'check proauth server "{self.proauth_addr}" connection.')
        res = requests.post(
            url=self.proauth_addr + "/proauth/oauth/authenticate",
            headers={"Content-Type": "application/json;charset=UTF-8"},
            data=json.dumps({"user_id": self.user_id, "password": self.user_password}),
        )
        if res.status_code != 200:
            print(
                "cannot connect to %s. proauth server returns status code %d"
                % (self.proauth_addr, res.status_code)
            )
            raise Exception(res)

        response = json.loads(res.text)
        if response["result"] == "false":
            raise Exception(response["error"])
        self.access_token = response["token"]
        self.refresh_token = response["refresh_token"]
        self.hyperdata_token_header = {"Authorization": self.access_token}
        print("check proauth server connection end.\n")

    def _check_hyperdata_project(self):
        print_header(f'check is hyperdata project "{self.project_name}" exist.')

        project_get_url = self.hyperdata_addr + "/hyperdata/web-service/projects"
        res = requests.get(project_get_url, headers=self.hyperdata_token_header)
        if res.status_code != 200:
            print(
                "cannot connect to %s. hyperdata server returns status code %d"
                % (self.hyperdata_addr, res.status_code)
            )
            raise Exception(res)

        project_infos = json.loads(res.text)["dto"]["project"]
        project_id = None
        for project_info in project_infos:
            if project_info["name"] == self.project_name:
                project_id = project_info["id"]
                break
        if project_id is None:
            print(f"Cannot found project {self.project_name}. Please check hyperdata.")
            raise Exception("_check_hyperdata_project failed.")
        else:
            self.project_id = project_id

        print("check hyperdata server connection end.\n")

    def run(self):
        self._check_hyperdata_proauth_server_connect()
        self._check_hyperdata_project()
