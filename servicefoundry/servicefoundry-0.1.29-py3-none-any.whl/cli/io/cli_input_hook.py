import os

import questionary
from questionary import Choice

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.console import console
from servicefoundry.internal.io.input_hook import InputHook
from servicefoundry.internal.lib import workspace as workspace_lib
from servicefoundry.internal.lib.util import (
    resolve_cluster_or_error,
    resolve_workspaces,
)

MSG_CREATE_NEW_SPACE = "Create a new workspace"


def python_file_filter(path: str):
    if path.endswith(".py"):
        return True
    return False


class CliInputHook(InputHook):
    def __init__(self, tfs_client: ServiceFoundryServiceClient):
        super().__init__(tfs_client)

    def _get_default(self, param):
        if param.default:
            return str(param.default)
        if param.suggest:
            return str(param.suggest)
        return ""

    def confirm(self, prompt, default=False):
        return questionary.confirm(prompt, default=default).ask()

    def ask_string(self, param):
        return questionary.text(param.prompt, default=self._get_default(param)).ask()

    def ask_number(self, param):
        while True:
            value = questionary.text(
                param.prompt, default=self._get_default(param)
            ).ask()
            if value.isdigit():
                return int(value)
            else:
                print(f"Not an integer Value {value}. Try again")

    def ask_file_path(self, param):
        return questionary.path(param.prompt, default=self._get_default(param)).ask()

    def ask_option(self, param):
        return questionary.select(param.prompt, choices=param.options).ask()

    def ask_python_file(self, param):
        while True:
            path = questionary.path(param.prompt, file_filter=python_file_filter).ask()
            if os.path.isfile(path):
                return path
            else:
                print(f"Incorrect path {path}. Try again.")

    def ask_workspace(self, param):
        # TODO: use get spaces
        workspaces = resolve_workspaces(
            client=self.tfs_client,
            name_or_id=None,
            cluster_name_or_id=None,
            ignore_context=False,
        )
        # TODO (chiragjn): should display fqn here for same workspace name across clusters in case
        #                  cluster is not set in context
        workspace_choices = [
            Choice(title=w.name, value=w.fqn)
            for w in workspaces
            if w.status == "CREATE_SPACE_SUCCEEDED"
        ]
        workspace_choices.append(
            Choice(title=MSG_CREATE_NEW_SPACE, value=MSG_CREATE_NEW_SPACE)
        )
        workspace = questionary.select(param.prompt, choices=workspace_choices).ask()

        if workspace == MSG_CREATE_NEW_SPACE:
            cluster = resolve_cluster_or_error(
                name_or_id=None,
                ignore_context=False,
                non_interactive=False,
                client=self.tfs_client,
            )
            new_space_name = questionary.text(
                "Please provide a name for your workspace"
            ).ask()
            workspace = workspace_lib.create_workspace(
                name=new_space_name,
                cluster_name_or_id=cluster.id,
                tail_logs=True,
                non_interactive=False,
                client=self.tfs_client,
            ).fqn
            console.print(f"Done, created new workspace with name {new_space_name!r}")

        return workspace
