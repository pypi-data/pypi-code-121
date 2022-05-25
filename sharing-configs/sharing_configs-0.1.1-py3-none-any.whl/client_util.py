from typing import Optional
from urllib.parse import urljoin

import requests

from sharing_configs.models import SharingConfigsConfig

from .exceptions import ApiException


class SharingConfigsClient:
    def __init__(self) -> None:
        self.config = SharingConfigsConfig.get_solo()
        self.label = self.config.label
        label_url = f"config/{str(self.label)}/folder/"
        self.base_url = urljoin(self.config.api_endpoint, label_url)
        self.headers = {
            "content-type": "application/json",
            "authorization": f"Token {self.config.api_key}",
        }

    def get_list_folders_url(self) -> str:
        """url to get available folders and subfolders"""
        return self.base_url

    def get_folder_files_url(self, folder) -> str:
        """url to get files in a given folder"""
        return urljoin(self.base_url, f"{folder}/files/")

    def get_import_url(self, folder, filename) -> str:
        """url to get a given file"""
        return urljoin(self.base_url, f"{folder}/files/{filename}")

    def get_export_url(self, folder) -> str:
        """url to upload a file"""
        return urljoin(self.base_url, f"{folder}/files/")

    def export(self, folder, data) -> dict:
        """
        expect path required param folder
        """
        resp = requests.post(
            url=self.get_export_url(folder), headers=self.headers, json=data
        )
        try:
            resp.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError) as e:
            raise ApiException("Error during export of object")
        return resp.json()

    def import_data(self, folder: str, filename: str) -> bytes:
        """expect required path params: label,folder,filename to get binary data from API"""
        resp = requests.get(
            url=self.get_import_url(folder, filename), headers=self.headers
        )
        try:
            resp.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError) as e:
            raise ApiException("Error during import of object")
        return resp.content

    def get_folders(self, permission: Optional[str]) -> dict:
        """
        return dict with attr "results" containing list of folders
        """
        if permission is not None:
            resp = requests.get(
                url=self.get_list_folders_url(), headers=self.headers, params=permission
            )

        else:

            resp = requests.get(url=self.get_list_folders_url(), headers=self.headers)

        try:
            resp.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError) as exc:
            raise ApiException({"error": "No folders"})

        return resp.json()

    def get_files(self, folder) -> dict:
        """
        expect required path param folder;
        return dict with attr "results" containing file names
        """
        resp = requests.get(self.get_folder_files_url(folder), headers=self.headers)
        try:
            resp.raise_for_status()
        except (requests.exceptions.HTTPError, requests.ConnectionError) as exc:
            raise ApiException("No files available")
        return resp.json()
