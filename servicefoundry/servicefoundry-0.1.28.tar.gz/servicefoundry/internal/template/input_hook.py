from ..clients.service_foundry_client import ServiceFoundryServiceClient


class InputHook:
    def __init__(self, tfs_client: ServiceFoundryServiceClient):
        self.tfs_client = ServiceFoundryServiceClient.get_client()

    def get_workspace_choices(self):
        workspaces = self.tfs_client.list_workspace()
        workspaces_choices = [
            (workspace["name"], workspace["fqn"])
            for workspace in workspaces
            if workspace["status"] == "CREATE_SPACE_SUCCEEDED"
        ]
        return workspaces_choices

    def ask_boolean(self, prompt):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_boolean"
        )

    def ask_string(self, param):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_string"
        )

    def ask_number(self, param):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )
     
    def ask_file_path(self, param):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )

    def ask_option(self, param):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_option"
        )

    def ask_workspace(self, param):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_workspace"
        )
