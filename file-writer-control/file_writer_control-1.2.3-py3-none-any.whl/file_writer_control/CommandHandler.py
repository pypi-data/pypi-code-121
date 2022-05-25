from file_writer_control.CommandChannel import CommandChannel
from file_writer_control.CommandStatus import CommandState
from datetime import timedelta


class CommandHandler:
    """
    A stand in for (more easily) checking the state of a command sent to a file-writer.
    """

    def __init__(self, command_channel: CommandChannel, command_id: str):
        """
        Constructor.
        :param command_channel: The instance of a CommandChannel that this class uses for getting the command status from.
        :param command_id: The (unique) command identifier.
        """
        self.command_id = command_id
        self.command_channel = command_channel

    def get_state(self) -> CommandState:
        """
        Get the command state.
        :return: The state of the command if possible. CommandState.UNKNOWN if the the state can not be determined.
        """
        command = self.command_channel.get_command(self.command_id)
        if command is None:
            return CommandState.UNKNOWN
        return command.state

    def is_done(self) -> bool:
        """
        :return: True if the command completed successfully. False otherwise.
        """
        current_state = self.command_channel.get_command(self.command_id).state
        if current_state == CommandState.ERROR:
            raise RuntimeError(
                f'Command failed with error message "{self.get_message()}".'
            )
        if current_state == CommandState.TIMEOUT_RESPONSE:
            raise RuntimeError("Timed out while trying to send command.")
        return current_state == CommandState.SUCCESS

    def get_message(self) -> str:
        """
        :return: If there was an error executing the command, this member function will return the error string as
        sent by the file-writer. Will return an empty string otherwise.
        """
        command = self.command_channel.get_command(self.command_id)
        if command is None:
            return ""
        return command.message

    def set_timeout(self, new_timeout: timedelta):
        self.command_channel.get_command(self.command_id).timeout = new_timeout

    def get_timeout(self):
        return self.command_channel.get_command(self.command_id).timeout
