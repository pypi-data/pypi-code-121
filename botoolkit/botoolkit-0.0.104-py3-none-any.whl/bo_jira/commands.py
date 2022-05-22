from botoolkit.bo_jira.mixins import (
    JiraArgumentsMixin,
)
from botoolkit.bo_jira.settings import (
    TOOL_NAME as BOJIRA_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.core.commands import (
    BOConfiguredToolConfigureCommand,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)


class ConfigureBOJiraCommand(
    JiraArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Конфигурирование инструмента bojira
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Configure bojira for working with Jira instance.'
        )

    def get_tool_name(self):
        return BOJIRA_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names
