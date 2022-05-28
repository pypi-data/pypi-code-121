from sys import path, argv
from os.path import abspath
from argparse import ArgumentParser
from importlib import import_module
from logos_cdi import Module
from logos_cdi.abstract import AbstractContainer
from logos_cdi.application import Application
from logos_cdi.command import AbstractCommand

path.append(abspath('.'))

try:
    app = getattr(import_module('main'), 'app')
except:
    app = None


class ManagerCommand(AbstractCommand):

    def __init__(self, argument_parser: ArgumentParser, context: AbstractContainer):
        super().__init__(argument_parser)
        self.context = context

    def define_arguments(self, argument_parser: ArgumentParser):
        argument_parser.add_argument('--application', required=app is None)

    async def execute(self):
        global app
        print(app)
        if not app:
            module_path, app_var = self.arguments.application.split(':')
            try:
                app = getattr(import_module(module_path), app_var, None)
            except:
                raise ValueError(f'"{self.arguments.application}" is invalid application url')
        if not isinstance(app, Application):
            raise ValueError(f'"{self.arguments.application or "main:app"}" not is Application instance')
        command = app.get('command')
        await command.execute()


__container__ = Module()
__container__.container_builder()\
    .add_resource(
        name='command',
        type='service',
        factory='class::logos_cdi.manager:ManagerCommand',
        parameters={"argument_parser": ArgumentParser(add_help=False), "context": '%context%'}
    )
