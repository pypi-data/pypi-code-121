from typing import List, Dict

from prettytable import PLAIN_COLUMNS
from prettytable import PrettyTable

from leapcli.enums import ResourceEnum
from leapcli.login import Authenticator
from leapcli.project import Project


class Get:
    def __init__(self, project: Project):
        self.project = project

        Authenticator.initialize(self.project)
        self._api = Authenticator.authenticated_api()

    def run(self, resource: ResourceEnum) -> None:
        resource_json_list: List[Dict[str, str]] = []
        if resource == ResourceEnum.secret:
            resource_json_list = self.get_secrets()

        self._print_json_table(resource_json_list)

    def get_secrets(self) -> List[Dict[str, str]]:
        return_secrets_json_list: List[Dict[str, str]] = []
        get_secret_manager_list_response = self._api.get_secret_manager_list()
        get_secret_manager_list_results = get_secret_manager_list_response["results"]
        selected_keys = ["name", "created_at"]
        for secret_json in get_secret_manager_list_results:
            truncated_json = {key: secret_json[key] for key in selected_keys}
            return_secrets_json_list.append(truncated_json)

        return return_secrets_json_list

    @staticmethod
    def _print_json_table(resource_json_list: List[Dict[str, str]]) -> None:
        if len(resource_json_list) == 0:
            print("No entries")
            return

        table = PrettyTable()
        field_names = [str.upper(field) for field in list(resource_json_list[0].keys())]

        table.field_names = field_names
        for resource_json in resource_json_list:
            table.add_row(list(resource_json.values()))

        table.set_style(PLAIN_COLUMNS)
        print(table)
