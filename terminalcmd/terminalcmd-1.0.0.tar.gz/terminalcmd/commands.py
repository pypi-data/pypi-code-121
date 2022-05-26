from dataclasses import dataclass
from typing import Any, Optional, List, Tuple
from sys import exit

from .func_type import func_type
from .exceptions import CommandExistError


@dataclass
class Command:
    function: Any
    name: str
    short_description: str
    description: str
    usage: str

    def __repr__(self) -> str:
        return f"Command with function: {self.function} and name: {self.name}"


def __allocate_description(description: str) -> str:
    if description != "NS":
        return f"  Description:\n    '{description}'\n"
    return str()


def _ask_handler(command_name: str) -> None:
    command = get_command(command_name)
    ask_text = (
        f"Command '{command.name}':\n"
        f"  Short description:\n    '{command.short_description}'\n"
        f"{__allocate_description(command.description)}"
        f"  Usage:\n    '{command.usage}'"
    )
    print("\n" + ask_text)


def __spaces_len() -> int:
    length_spaces = [command_obj.name for command_obj in Commands().list]
    length_spaces.sort(reverse=True, key=len)
    return len(length_spaces[0])


def _help_command() -> None:
    help_text = str()

    for command_obj in Commands().list:
        help_text += (f"\n{command_obj.name}{' ' * (__spaces_len() - len(command_obj.name))} | "
                      f"{command_obj.short_description}")

    print(help_text)


class Commands:
    __list: List[Command] = [
        Command(_help_command, "help", "Show help message.",
                "Show information about every commands in list.", "<help>, <help ?>"),
        Command(exit, "exit", "Exit from running app.",
                "Exit from current running app wirth exiut code 0.", "<exit>, <exit ?>"),
    ]

    def __init__(self, name: Optional[str] = None) -> None:
        if name:
            self.name = name

    @property  # This actually nowhere used...
    def list(self) -> Tuple[Command]:  
        return tuple(self.__list)

    def set_new(self, function: func_type, name: str,
                short_description: str, description: str, usage: str) -> None:
        self.__list.append(Command(function, name, short_description, description, usage))


def get_command(name: str, allow_none_return: bool = False) -> Optional[Command]:
    for command_obj in Commands().list:
        if command_obj.name == name:
            return command_obj
    if not allow_none_return:
        raise CommandExistError(f"Cannot find any command with name '{name}'.")


def transform_command() -> str:
    """This function do nothing YET."""
    return transform_command.__doc__
