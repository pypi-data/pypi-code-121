from click.shell_completion import CompletionItem
from click import ParamType

from dotpyle.services.file_handler import FileHandler, LocalFileHandler
from dotpyle.services.config_handler import ConfigHandler
import os
import sys
from dotpyle.decorators.pass_config_handler import pass_config_handler

# This is awful: should be done with inyection
from dotpyle.services.logger import Logger

logger = Logger(verbose=False)
config_handler = ConfigHandler(
    config=FileHandler(logger=logger).config, logger=logger
)


class DotfileNamesVarType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        names = config_handler.get_names()
        items = [(name, "") for name in names]
        for value, help in items:
            if incomplete in value or incomplete in help:
                yield (CompletionItem(value, help=help))


# TODO: get profiles given name (previous argument)
# TODO https://stackoverflow.com/a/58617108/10474917
class ProfileVarType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        profiles = config_handler.get_profiles()
        items = [(name, "") for name in profiles]
        for value, help in items:
            if incomplete in value or incomplete in help:
                yield (CompletionItem(value, help=help))


class ScriptVarType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        scripts = config_handler.get_scripts()
        items = [(name, "") for name in scripts]
        # For now, there will be no help
        for value, help in items:
            if incomplete in value or incomplete in help:
                yield (CompletionItem(value, help=help))


class EnvVarType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        return [
            CompletionItem(name)
            for name in os.environ
            if name.startswith(incomplete)
        ]


# No parece posible autocompletar con paths empezando en ~ o en / o en ../
# FIXME
# type=click.Path(exists=True, resolve_path=True, allow_dash=True)
class PathVarType(ParamType):
    def shell_complete(self, ctx, param, incomplete):
        import os

        return [CompletionItem(path) for path in os.listdir("/")]
