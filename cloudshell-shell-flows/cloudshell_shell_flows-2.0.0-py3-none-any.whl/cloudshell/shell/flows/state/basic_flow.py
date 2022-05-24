from cloudshell.logging.utils.decorators import command_logging

from cloudshell.shell.flows.command.basic_flow import RunCommandFlow
from cloudshell.shell.flows.interfaces import StateFlowInterface


class StateFlow(StateFlowInterface):
    def __init__(self, logger, resource_config, cli_configurator, api):
        self._logger = logger
        self._api = api
        self.resource_config = resource_config
        self._cli_configurator = cli_configurator

    @command_logging
    def health_check(self):
        """Verify that device is accessible over CLI by sending ENTER for cli."""
        api_response = "Online"

        result = f"Health check on resource {self.resource_config.name}"
        try:
            RunCommandFlow(self._logger, self._cli_configurator).run_custom_command("")
            result += " passed."
        except Exception as e:
            self._logger.exception(e)
            api_response = "Error"
            result += " failed."

        try:
            self._api.SetResourceLiveStatus(
                self.resource_config.name, api_response, result
            )
        except Exception:
            self._logger.error(
                "Cannot update {} resource status on portal".format(
                    self.resource_config.name
                )
            )

        return result

    def shutdown(self):
        """Shutdown device."""
        raise Exception(
            self.__class__.__name__,
            "Shutdown command isn't available for the current device",
        )
