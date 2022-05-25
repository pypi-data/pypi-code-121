from ..clients.service_foundry_client import ServiceFoundryServiceClient
from .input_hook import InputHook


class DummyInputHook(InputHook):
    def __init__(self, tfs_client: ServiceFoundryServiceClient, parameters):
        super().__init__(tfs_client)
        self.parameters = parameters

    def _get_param_from_id(self, param, options=None):
        if param.id in self.parameters:
            return self.parameters[param.id]
        raise RuntimeError(
            f"Parameter {param.id} is not provided."
            f" Suggested value is {param.default}."
            if param.default
            else "" + f" Valid choices are {options}"
            if options
            else ""
        )

    def ask_boolean(self, param):
        return self._get_param_from_id(param)

    def ask_string(self, param):
        return self._get_param_from_id(param)

    def ask_number(self, param):
        return self._get_param_from_id(param)

    def ask_file_path(self, param):
        return self._get_param_from_id(param)

    def ask_option(self, param):
        value = self._get_param_from_id(param, options=param.options)
        if value in param.options:
            return value
        raise RuntimeError(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{','.join(param.options.keys())}]"
        )

    def ask_workspace(self, param):
        workspace_choices = self.get_workspace_choices()
        workspaces = [workspace_choice[1] for workspace_choice in workspace_choices]
        value = self._get_param_from_id(param, options=workspaces)
        if value in workspaces:
            return value
        raise RuntimeError(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{' ,'.join(param.options.keys())}]"
        )
