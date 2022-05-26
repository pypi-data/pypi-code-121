import json
from pydantic import BaseSettings
import requests

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder


class Grafana(BaseSettings):
    """
    Grafana API 

    :param grafana_url: base URL for Grafana
    :param grafana_token: Grafana API Token
    :param tls_verify: control TLS verification

    """
    grafana_url: str
    grafana_token: str
    tls_verify: bool = True

    class Config(BaseSettings.Config):
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'

    def _get(self, api: str):
        headers = {'Authorization': f"Bearer {self.grafana_token}",
                   'Content-Type': 'application/json'}

        r = requests.get(f"{self.grafana_url}/api{api}",
                         headers=headers, verify=self.tls_verify)
        if r.status_code != 200:
            print(f"{r.status_code} - {r.content}")

        return r

    def _post(self, api: str, data: str):
        headers = {'Authorization': f"Bearer {self.grafana_token}",
                   'Content-Type': 'application/json'}

        r = requests.post(f"{self.grafana_url}/api{api}",
                          data=data, headers=headers, verify=self.tls_verify)
        if r.status_code != 200:
            print(f"{r.status_code} - {r.content}")

        return r

    def _put(self, api: str, data: str):
        headers = {'Authorization': f"Bearer {self.grafana_token}",
                   'Content-Type': 'application/json'}

        r = requests.put(f"{self.grafana_url}/api{api}",
                         data=data, headers=headers, verify=self.tls_verify)
        if r.status_code != 200:
            print(f"{r.status_code} - {r.content}")

        return r

    def publish_dashboard(self, folder_uid: str, d: Dashboard, message: str = "", overwrite: bool = True):
        '''
        upload_to_grafana tries to upload dashboard to grafana and prints response

        :param d:           grafanalib dashboard
        :param overwrite:   overwrite switch
        :param message:     message
        '''

        data = json.dumps(
            {
                "dashboard": d.to_json_data(),
                "overwrite": overwrite,
                "message": message,
                "folderUid": folder_uid,
            }, sort_keys=True, indent=2, cls=DashboardEncoder)

        r = self._post('/dashboards/db', data)

    def publish_folder(self, uid: str, title: str, overwrite: bool = True):
        '''
        create grafana folder

        :param uid:         desired uid
        :param title:       desired title
        :param overwrite:   overwrite switch
        '''
        data = json.dumps(
            {
                "uid": uid,
                "title": title,
                "overwrite": overwrite
            }, sort_keys=True, indent=2)

        # Create if doesn't exist
        r = self._put(f"/folders/{uid}", data)
        if r.status_code == 404:
            r = self._post("/folders", data)
