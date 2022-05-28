from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Dict
from logos_cdi.application import Module
from sys import argv


class AbstractCommand(ABC):

    __singleton__ = ['application']

    def __init__(self, argument_parser: ArgumentParser):
        self.argument_parser = argument_parser
        self._arguments = None

    def define_arguments(self, argument_parser: ArgumentParser):
        pass

    @property
    def arguments(self):
        if self._arguments is None:
            self.define_arguments(self.argument_parser)
            self._arguments = self.argument_parser.parse_known_args(getattr(self, 'argv', None))[0]
        return self._arguments

    @abstractmethod
    async def execute(self):
        raise NotImplementedError('please implement this method')


class CommandDelegator(AbstractCommand):

    def __init__(self, argument_parser: ArgumentParser, commands: Dict[str, AbstractCommand]):
        super().__init__(argument_parser)
        self.commands = commands

    def define_arguments(self, argument_parser: ArgumentParser):
        subparsers = argument_parser.add_subparsers(title='command', help='command to execute', required=True, dest='command')
        for command_name, command in self.commands.items():
            command_parser = subparsers.add_parser(command_name)
            command.define_arguments(command_parser)

    async def execute(self):
        command = self.commands[self.arguments.command]
        command.argv = argv[2::]
        await command.execute()


__container__ = Module()
__container__.container_builder()\
    .add_resource('commands', 'group', regex=r'^command:(?P<name>[\w+:]*)', resolve_resources=True)\
    .add_resource('argument_parser', 'service', factory='class::argparse:ArgumentParser')\
    .add_resource(
        name='command',
        type='service',
        factory='class::logos_cdi.command:CommandDelegator',
        parameters={"argument_parser": "%argument_parser%", "commands": "%commands%"}
    )
