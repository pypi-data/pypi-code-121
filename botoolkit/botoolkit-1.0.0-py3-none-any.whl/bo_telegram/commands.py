from botoolkit.bo_telegram.mixins import (
    TelegramArgumentMixin,
)
from botoolkit.bo_telegram.settings import (
    TOOL_NAME as BOTELEGRAM_TOOL_NAME,
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


class BOTelegramConfigureCommand(
    TelegramArgumentMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда конфигурирования инструмента botoolkit
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
            'Configure botelegram for working with Telegram.'
        )

    def get_tool_name(self):
        return BOTELEGRAM_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names
