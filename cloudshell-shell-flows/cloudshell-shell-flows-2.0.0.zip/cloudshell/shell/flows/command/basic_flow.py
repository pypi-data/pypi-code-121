from cloudshell.logging.utils.decorators import command_logging

from cloudshell.shell.flows.interfaces import RunCommandFlowInterface


class RunCommandFlow(RunCommandFlowInterface):
    def __init__(self, logger, cli_configurator):
        """Create RunCommandOperations.

        :param logger: QsLogger object
        :param cloudshell.cli.configurator.AbstractModeConfigurator cli_configurator:
        """
        self._logger = logger
        self._cli_configurator = cli_configurator

    def _run_command_flow(self, custom_command, is_config=False):
        """Execute flow which run custom command on device.

        :param custom_command: the command to execute on device
        :type custom_command: str
        :param is_config: if True then run command in configuration mode
        :return: command execution output
        """
        commands = self.parse_custom_commands(custom_command)

        if is_config:
            service_manager = self._cli_configurator.config_mode_service()
        else:
            service_manager = self._cli_configurator.enable_mode_service()

        responses = []
        with service_manager as session:
            for cmd in commands:
                responses.append(session.send_command(command=cmd))
        return "\n".join(responses)

    @command_logging
    def run_custom_command(self, custom_command):
        """Execute custom command on device.

        :param custom_command: command
        :type custom_command: str

        :return: result of command execution
        """
        return self._run_command_flow(custom_command=custom_command)

    @command_logging
    def run_custom_config_command(self, custom_command):
        """Execute custom command in configuration mode on device.

        :param custom_command: command
        :type custom_command: str

        :return: result of command execution
        """
        return self._run_command_flow(custom_command=custom_command, is_config=True)

    def parse_custom_commands(self, command, separator=";"):
        """Parse run custom command string into the commands list.

        :param str command: run custom [config] command(s)
        :param str separator: commands separator in the string
        :rtype: list[str]
        """
        if isinstance(command, str):
            return command.strip(separator).split(separator)
        return command
