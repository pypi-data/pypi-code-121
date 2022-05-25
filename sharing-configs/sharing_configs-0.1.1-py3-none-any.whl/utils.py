import base64
from typing import Optional

import requests

from sharing_configs.client_util import SharingConfigsClient

from .exceptions import ApiException


def get_folders_from_api(permission: Optional[str]) -> dict:
    """
    make an API call to fetch data about folders with a given permission
    """
    obj = SharingConfigsClient()

    try:
        data = obj.get_folders(permission)

        return data
    except (requests.exceptions.HTTPError, requests.ConnectionError) as exc:
        raise ApiException({"error": "No folders"})


def get_imported_folders_choices(permission: Optional[str]) -> list:
    """
    create list of tuples (folders name) based on api response
    ex:[('folder_one', 'folder_one'), ('folder_two', 'folder_two')]
    """
    folders_choices = []
    api_dict = get_folders_from_api(permission)
    results_list = api_dict.get("results", "No results in your dict")
    if results_list is not None:
        lst = FolderList()
        all_folders = lst.folder_collector(results_list)
        for folder in all_folders:
            folders_choices.append((folder, folder))
    else:
        folders_choices = []
    # folders_choices [('example_folder', 'example_folder'), ('example_subfolder', 'example_subfolder')]
    return folders_choices


def get_files_in_folder_from_api(folder: str) -> dict:
    """
    return files for a given folder
    """
    obj = SharingConfigsClient()
    try:
        content = obj.get_files(folder)
        return content
    except (requests.exceptions.HTTPError, requests.ConnectionError) as exc:
        raise ApiException


def get_imported_files_choices(folder: str) -> list:
    """
    create list of filenames based on api response and to be passed to js

    """
    api_dict = get_files_in_folder_from_api(folder)
    results_list = api_dict.get("results", None)
    file_choices = []
    if results_list is not None:
        for item in results_list:
            file_choices.append(item.get("filename"))
    return file_choices


class FolderList:
    def __init__(self) -> None:
        self.folders_lst = []

    def folder_collector(self, lst) -> list:
        """
        Take a list and extract all (nested)folders from it.
        """

        for item in lst:
            self.folders_lst.append(item["name"])
            if len(item.get("children")) != 0:
                self.folder_collector(lst=item.get("children"))
        return self.folders_lst


def get_str_from_encoded64_object(content: bytes) -> str:
    """return string as a result of decoding (base64) byte object"""
    return base64.b64encode(content).decode("utf-8")
