from servicefoundry.internal.exceptions import ConfigurationException
from servicefoundry.internal.io.input_hook import InputHook


# Not being used.
class DefaultInputHookDecorator(InputHook):
    def __init__(self, input_hook: InputHook, parameter_values):
        self.input_hook = input_hook
        self.parameter_values = parameter_values

    def _get_param_from_provided_value(self, param):
        if param.id in self.parameter_values:
            return self.parameter_values[param.id]

    def confirm(self, prompt, default=False):
        return self.input_hook.confirm(prompt, default=default)

    def ask_string(self, param):
        val = self._get_param_from_provided_value(param)
        if val:
            return val
        return self.input_hook.ask_string(param)

    def ask_number(self, param):
        val = self._get_param_from_provided_value(param)
        if val:
            return val
        return self._get_param_from_provided_value(param)

    def ask_file_path(self, param):
        val = self._get_param_from_provided_value(param)
        if val:
            return val
        return self._get_param_from_provided_value(param)

    def ask_python_file(self, param):
        val = self._get_param_from_provided_value(param)
        if val:
            return val
        return self._get_param_from_provided_value(param)

    def ask_option(self, param):
        val = self._get_param_from_provided_value(param)
        if val:
            return val
        return self._get_param_from_provided_value(param)

    def ask_workspace(self, param):
        value = self._get_param_from_provided_value(param)
        if value:
            workspace_choices = self.get_workspace_choices()
            workspaces = [workspace_choice[1] for workspace_choice in workspace_choices]
            if value in workspaces:
                return value
            else:
                raise ConfigurationException(
                    f"For parameter {param.id} provided value {value} "
                    f"is not in [{' ,'.join(param.options.keys())}]"
                )
        return self._get_param_from_provided_value(param)
