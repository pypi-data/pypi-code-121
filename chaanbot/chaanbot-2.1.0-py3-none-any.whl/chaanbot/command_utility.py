""" Help methods for commands to the bot """

import logging

logger = logging.getLogger("command_utility")


def matches(command_dict_or_operation, message) -> bool:
    if not message or not command_dict_or_operation:
        return False

    if "commands" in command_dict_or_operation:  # If operation was passed in then dict should have "commands" key
        operation = command_dict_or_operation
        return _operation_matches_message(operation, message)
    else:
        for operation, value in command_dict_or_operation.items():
            if _operation_matches_message(value, message):
                return True
    return False


def _operation_matches_message(operation, message) -> bool:
    for command in operation["commands"]:
        if command and command.lower() == get_command(message).lower():
            has_argument_regex = "argument_regex" in operation
            if not has_argument_regex and not get_argument(message):
                return True
            if operation["argument_regex"].search(get_argument(message)):
                logger.debug("Message matches command dict and argument regex")
                return True
    return False


def get_command(message) -> str:
    return get_command_and_argument(message)[0]


def get_argument(message) -> str:
    """Get the argument to a message. A message looks like: [command] [argument].
    E.g. the argument to "!hl test" would be "test"."""
    try:
        return get_command_and_argument(message)[1]
    except IndexError:
        return ""


def get_command_and_argument(message) -> (str, str):
    return message.split(None, 1)
