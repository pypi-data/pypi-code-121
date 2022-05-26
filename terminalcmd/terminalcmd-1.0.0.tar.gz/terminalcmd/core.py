from typing import Callable, Optional, List
from sys import exit

from .func_type import func_type
from .commands import Commands, get_command, _ask_handler, _help_command
from .exceptions import CommandExistError, ZeroCommandsError, MissingSDError

curr_arguments = []


def line_args() -> List[str]:
    return curr_arguments


def command(
    description: str = "NS",
    short_description: Optional[str] = None,
    name: Optional[str] = None,
    usage: Optional[str] = None
) -> Callable[[func_type], None]:
    def wrapper(function: func_type) -> None:
        nonlocal usage, description, short_description, name

        if not short_description:
            if function.__doc__:
                short_description = function.__doc__
            else:
                raise MissingSDError("You have not setted paramater 'short_description' to function "
                                     f"'{function.__name__}'. You can add this param in decorator '@new_command' "
                                     "or add \"\"\"Docstring\"\"\" to this function.")
        if not name:
            name = function.__name__
        if not usage:
            usage = f"<{name}>, <{name} ?>"

        if not get_command(name, True):
            Commands().set_new(function, name, short_description, description, usage)
        else:
            raise CommandExistError(f"Command with name '{name}' already exists.")

    return wrapper


def start_console(
    comandlet: str = "terminalcmd:/> ",
    stop_with_interrupt: bool = False,
    exist_error_message: str = "There is no such commands as '[command]'.",
    exit_message: str = "Goodbye!"
) -> None:
    if len(Commands().list) <= 2:
        raise ZeroCommandsError("You have not added any commands to core. "
                                "Use decorator '@new_command' to add commands.")
    while True:
        try:
            args = input("\n" + comandlet).split(" ")

            global curr_arguments
            curr_arguments = args
            command_name = args[0]

            if len(args) >= 2:
                if args[1] == "?":
                    _ask_handler(command_name)
                    continue
            if command_name == "help":
                _help_command()
                continue

            command = get_command(command_name, True)

            if command:
                command.function()
            else:
                print("\n" + exist_error_message.replace("[command]", command_name))
        except KeyboardInterrupt:
            if stop_with_interrupt:
                print("\n" + exit_message)
                exit(0)
            else:
                raise KeyboardInterrupt
