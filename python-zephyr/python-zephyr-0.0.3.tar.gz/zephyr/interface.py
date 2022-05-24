"""
General interface for Zephyr API.
"""
import time
from json import dumps
from json import loads
from typing import Literal
import random
import requests

import zephyr.exceptions as exceptions


def rm_none_from_dict(data: dict):
    """
    Remove None values from a dictionary

    :param data:
        dictionary to remove None values from
    :return:
        dictionary without None values
    """
    if data is None:
        return None
    else:
        return {
            k: v for k, v in data.items() if v is not None and v != "" and (len(v) > 0 if isinstance(v, list) else True)
        }


def add_query_params(url: str, params: dict):
    """
    Add query parameters to a url
    :param url: url to add query parameters to
    :param params: dictionary of query parameters
    :return: url with query parameters
    """
    if params:
        url += "?"
        for key in params:
            url += key + "=" + str(params[key]) + "&"
        url = url[:-1]
    return url


def retry_with_backoff(retries: int = 5, backoff_in_seconds: float = 1.0):
    """
    Retry with backoff (decorator function)
    :param retries: number of retry count
    :param backoff_in_seconds: retry backoff time
    :return: callback function
    """
    def rwb(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    if x == retries:
                        raise
                    else:
                        sleep = (backoff_in_seconds * 2 ** x +
                                 random.uniform(0, 1))
                        time.sleep(sleep)
                        x += 1
        return wrapper
    return rwb


def match_str_in_datadict(data: dict, text: str, identifier: str):
    """
    Match a string in a dictionary of data

    :param identifier:
        name of the key containing the string to match
    :param data:
        data to search
    :param text:
        string to search for
    :return:
        object where text matches
    """
    matches = [folder for folder in data["values"] if text in folder[identifier]]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        return [x for x in matches if text == x][0]
    else:
        return None


class ZephyrInterface:
    """
    Handles the communication with Zephyr

    See https://support.smartbear.com/zephyr-scale-cloud/api-docs/ for API reference

    :param bearer_token:
            token to be used for auth, without the "Bearer " prefix.
            Can be generated in your Zephyr account settings.
    """

    def __init__(self, bearer_token: str):
        """
        Initializes the ZephyrInterface

        :param bearer_token:
            token to be used for auth, without the "Bearer " prefix.
            Can be generated in your Zephyr account settings.
        """
        self.header = {"Authorization": "Bearer " + bearer_token, "Content-Type": "application/json"}
        self.base_url = "https://api.zephyrscale.smartbear.com/v2"

    @retry_with_backoff(retries=5)
    def get_request(self, url: str, params: dict = None):
        """
        Get request at given url with pre-set up header.

        :param params:
            dictionary of query parameters
        :param url:
            url to get
        :return:
            parsed data from the request
        """
        params = rm_none_from_dict(params)
        url = add_query_params(url, params)
        response = requests.get(url, headers=self.header)
        if response.status_code == 200:
            return loads(str(response.text))
        else:
            raise exceptions.BadResponseError(f"Bad response from Zephyr. Code: {response.status_code}")

    @retry_with_backoff(retries=5)
    def post_request(self, url: str, payload: dict):
        """
        Post request at given url with pre-set up header.

        :param payload:
            payload to send
        :param url:
            url to post to
        :return:
            parsed data from the request
        """
        response = requests.post(url, headers=self.header, data=dumps(payload))
        if response.status_code == 201:
            return loads(str(response.text))
        else:
            raise exceptions.BadResponseError(f"Bad response from Zephyr. Code: {response.status_code}")

    @retry_with_backoff(retries=5)
    def put_request(self, url: str, payload: dict):
        """
        Put request at given url with pre-set up header.

        :param payload:
            payload to send
        :param url:
            url to put to
        :return:
            parsed data from the request
        """
        response = requests.put(url, headers=self.header, data=dumps(payload))
        if response.status_code == 200:
            return loads(str(response.text)) if response.text else None
        else:
            raise exceptions.BadResponseError(f"Bad response from Zephyr. Code: {response.status_code}")

    def get_project_id(self, project_key):
        """
        Gets the project id for a given project key

        :param project_key:
            key of the project to search for (e.g. "BMC")
        :return:
            id of the project
        """
        url = self.base_url + "/projects"
        data = self.get_request(url)

        if data is not None:
            matched_dict = match_str_in_datadict(data, project_key, "key")
            if matched_dict is not None:
                return matched_dict["id"]
            else:
                raise exceptions.FolderNotFoundError(f"Folder {project_key} not found")
        else:
            return None

    def get_folder_id(
        self,
        project_key: str = None,
        folder_name: str = None,
        parent_id: int = None,
        folder_type: Literal["TEST_CASE", "TEST_PLAN", "TEST_CYCLE"] = "TEST_CASE",
        timeout_s: float = 1.0,
    ):
        """
        Gets the testcase folder id for a given folder name and parent folder id
        :param project_key:
            key of the project to search in (e.g. "BMC")
        :param folder_name:
            name of the folder to search for (e.g. "2.6.5_ESS State Machine")
        :param parent_id:
            id of the parent folder to search in
        :param folder_type:
            type of the folder to look for
        :param timeout_s:
            wait time between individual requests to Zephyr API
        :return:
            id of the folder
        """
        url = self.base_url + "/folders"
        payload = dict(
            projectKey=project_key,
            folderType=folder_type,
            maxResults=1,
        )
        data = self.get_request(url, payload)
        total_folders = data["total"]

        payload = dict(
            projectKey=project_key,
            folderType=folder_type,
            maxResults=total_folders,
        )
        data = self.get_request(url, payload)
        folder_found = False
        if data is not None:
            folders = data["values"]
            # check if all folders are returned, get rest otherwise
            if data["maxResults"] != total_folders:
                while data["next"] is not None:
                    data = self.get_request(data["next"])
                    folders.extend(data["values"])
                    time.sleep(timeout_s)
            found_folders = [folder for folder in folders if folder_name == folder["name"]]
            if parent_id is not None:
                found_folders = [folder for folder in found_folders if parent_id == folder["parentId"]]
            if found_folders is not None:
                if len(found_folders) == 1:
                    return found_folders[0]["id"]
                elif len(found_folders) > 1:
                    return [folder["id"] for folder in found_folders]
        if not folder_found:
            raise exceptions.FolderNotFoundError(f"Folder {folder_name} not found")

    def get_children_folder_ids(
        self,
        parent_id: int = None,
        folder_type: Literal["TEST_CASE", "TEST_PLAN", "TEST_CYCLE"] = "TEST_CASE",
        timeout_s: float = 1.0,
    ):
        """
        Gets all children folder ids for a given parent folder id
        :param parent_id:
            id of the parent folder to search in
        :param folder_type:
            type of the folder to look for
        :param timeout_s:
            wait time between individual requests to Zephyr API
        :return:
            ids of the children folders
        """
        url = self.base_url + "/folders"
        payload = dict(
            folderType=folder_type,
            maxResults=1,
        )
        data = self.get_request(url, payload)
        total_folders = data["total"]
        payload = dict(
            folderType=folder_type,
            maxResults=total_folders,
        )
        data = self.get_request(url, payload)
        if data is not None:
            folders = data["values"]
            # check if all folders are returned, get rest otherwise
            if data["maxResults"] != total_folders:
                while data["next"] is not None:
                    data = self.get_request(data["next"])
                    folders.extend(data["values"])
                    time.sleep(timeout_s)
            found_ids = [folder["id"] for folder in folders if parent_id == folder["parentId"]]
            return found_ids
        else:
            return None

    def get_environments(self, project_key: str = None, timeout_s: float = 1.0):
        """
        Gets all available test environments for a given project_key
        :param project_key:
            key of the project to search in (e.g. "BMC")
        :param timeout_s:
            wait time between individual requests to Zephyr API
        :return:
            environments as a data dictionary
        """
        url = self.base_url + "/environments"
        payload = dict(
            projectKey=project_key,
            maxResults=1,
        )
        data = self.get_request(url, payload)
        total_environments = data["total"]
        payload = dict(
            projectKey=project_key,
            maxResults=total_environments,
        )
        data = self.get_request(url, payload)
        if data is not None:
            environments = data["values"]
            # check if all folders are returned, get rest otherwise
            if data["maxResults"] != total_environments:
                while data["next"] is not None:
                    data = self.get_request(data["next"])
                    environments.extend(data["values"])
                    time.sleep(timeout_s)
            return environments
        else:
            return None

    def get_statuses(
        self,
        project_key: str = None,
        status_type: Literal["TEST_CASE", "TEST_PLAN", "TEST_CYCLE", "TEST_EXECUTION"] = "TEST_EXECUTION",
        timeout_s: float = 1.0,
    ):
        """
        Gets all available test statuses for a given project and type
        :param project_key:
            key of the project to search in (e.g. "BMC")
        :param status_type:
            type of status to look for. Valid values: "TEST_CASE", "TEST_PLAN", "TEST_CYCLE", "TEST_EXECUTION"
        :param timeout_s:
            wait time between individual requests to Zephyr API
        :return:
            statuses as a data dictionary
        """
        url = self.base_url + "/statuses"
        payload = dict(
            projectKey=project_key,
            statusType=status_type,
            maxResults=1,
        )
        data = self.get_request(url, payload)
        total_statuses = data["total"]
        payload = dict(
            projectKey=project_key,
            statusType=status_type,
            maxResults=total_statuses,
        )
        data = self.get_request(url, payload)
        if data is not None:
            statuses = data["values"]
            # check if all folders are returned, get rest otherwise
            if data["maxResults"] != total_statuses:
                while data["next"] is not None:
                    data = self.get_request(data["next"])
                    statuses.extend(data["values"])
                    time.sleep(timeout_s)
            return statuses
        else:
            return None


if __name__ == "__main__":
    with open("mytoken.txt", "r") as f:
        token = f.read()

    zi = ZephyrInterface(token)
    myFolderId = zi.get_folder_id(project_key="BMC", folder_name="2.6.5_ESS State Machine")
    print("2.6.5_ESS State Machine folder Id: " + str(myFolderId))
    myFolderId = zi.get_folder_id(project_key="BMC", folder_name="bolognasc")
    print("All bolognasc folder Ids: " + str(myFolderId))
    myFolderId = zi.get_folder_id(project_key="BMC", folder_name="Gtest")
    print("GtestFolderId: " + str(myFolderId))
    myFolderId = zi.get_folder_id(project_key="BMC", folder_name="bolognasc", parent_id=myFolderId)
    print("bolognasc Folder Id within Gtest: " + str(myFolderId))
    myChildrenIds = zi.get_children_folder_ids(folder_type="TEST_CASE", parent_id=myFolderId)
    print("All children folder Ids of bolognasc Folder Id within Gtest: " + str(myChildrenIds))
    print(zi.get_project_id("BMC"))
    myStatuses = zi.get_statuses(project_key="BMC", status_type="TEST_EXECUTION")
    print(myStatuses[0]["id"])
