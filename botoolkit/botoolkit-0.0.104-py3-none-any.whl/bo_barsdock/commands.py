from botoolkit.bo_barsdock.mixins import (
    BOBARSDockGeneralArgumentsMixin,
)
from botoolkit.bo_barsdock.settings import (
    TOOL_NAME as BOBARSDOCK_TOOL_NAME,
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


class ConfigureBOBARSDockCommand(
    BOBARSDockGeneralArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Конфигурирование инструмента bobarsdock
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

        self.description = 'Configure bobarsdock.'

    def get_tool_name(self):
        return BOBARSDOCK_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names

