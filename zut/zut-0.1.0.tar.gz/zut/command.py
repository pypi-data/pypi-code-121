import argparse
from collections import namedtuple
from types import FunctionType
from importlib import import_module

Command = namedtuple("Command", ["name", "func"])

class CommandManager:
    def __init__(self, pkg:str=None, prog:str=None, description:str=None):
        self.pkg = pkg
        self.parser = argparse.ArgumentParser(prog=prog if prog else pkg, description=description)
        self.subparsers = self.parser.add_subparsers()
        
        self.commands = []
        self.default_command = None


    def add_command(self, name:str, func=None, configure_func=None, help:str=None, package:str=None):
        cmd_parser = self.subparsers.add_parser(name, help=help)

        if not func or not configure_func:
            module = import_module("." + name, self.pkg)

        if not func:
            if hasattr(module, "main"):
                if not isinstance(module.main, FunctionType):
                    raise ValueError("%s.main is %s, expected function" % type(module.main).__name__)
                func = module.main
            else:
                raise ValueError("module %s has no main function" % (module.__name__))

        cmd_parser.set_defaults(func=func)
        self.commands.append(Command(name, func))

        if not configure_func:
            if hasattr(module, "configure"):
                if not isinstance(module.configure, FunctionType):
                    raise ValueError("%s.configure is %s, expected function" % type(module.configure).__name__)
                configure_func = module.configure

        if configure_func:
            configure_func(cmd_parser)

        if help and not cmd_parser.description:
            cmd_parser.description = help

        return cmd_parser


    def run(self):
        # Parse command-line
        args = vars(self.parser.parse_args())

        # Run command
        func = args.pop("func", self.default_command)
        if not func:
            print("No command to run")
            return 1

        returncode = func(**args)
        return returncode
