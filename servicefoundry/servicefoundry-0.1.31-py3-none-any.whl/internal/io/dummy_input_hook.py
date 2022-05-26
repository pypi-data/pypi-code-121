from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.exceptions import ConfigurationException
from servicefoundry.internal.io.input_hook import InputHook


class DummyInputHook(InputHook):
    def __init__(self, tfs_client: ServiceFoundryServiceClient, parameter_values):
        super().__init__(tfs_client)
        self.parameter_values = parameter_values

    def _get_param_from_id(self, param, options=None):
        if param.id in self.parameter_values:
            return self.parameter_values[param.id]
        default = param.default if param.default else param.suggest
        default = (
            f" Suggested value is {default}."
            if default is not None and default.strip() != ""
            else ""
        )
        options = f" Valid choices are {options}. " if options else ""

        raise ConfigurationException(
            f"Parameter {param.id} is not provided." + default + options
        )

    def confirm(self, param):
        return False

    def ask_string(self, param):
        return self._get_param_from_id(param)

    def ask_number(self, param):
        return self._get_param_from_id(param)

    def ask_file_path(self, param):
        return self._get_param_from_id(param)

    def ask_python_file(self, param):
        return self._get_param_from_id(param)

    def ask_option(self, param):
        value = self._get_param_from_id(param, options=param.options)
        if value in param.options:
            return value
        raise ConfigurationException(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{','.join(param.options.keys())}]"
        )

    def ask_workspace(self, param):
        workspace_choices = self.get_workspace_choices()
        workspaces = [workspace_choice[1] for workspace_choice in workspace_choices]
        value = self._get_param_from_id(param, options=workspaces)
        if value in workspaces:
            return value
        raise ConfigurationException(
            f"For parameter {param.id} provided value {value} "
            f"is not in [{' ,'.join(param.options.keys())}]"
        )
