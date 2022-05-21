# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: October 25th 2021 09:14:48 am
'''

import os
import sys
import argparse
from typing import Callable

from . import Module_Path, Version
from .util import get_class, join_path, join_to_abs_path
from .project.constants import (
    Unittest_Module_Folder, Project_Config_File, Project_Pack_File, Project_Requirement_File,
    Component_Module_Folder, Controller_Module_Folder)


class CommandProcessor:
    Command_Test_Project = 'test'
    Command_Create_Project = 'create'
    Command_Show_Version = 'version'
    Command_Pack_Project = 'pack'

    def __init__(self):
        self.project_dir = None
        self.__create_command_parser()

    @property
    def args_key_project_directory(self) -> str:
        return 'project_directory'

    @property
    def project_component_dir(self) -> str:
        return join_path(self.project_dir, Component_Module_Folder)

    @property
    def project_controller_dir(self) -> str:
        return join_path(self.project_dir, Controller_Module_Folder)

    @property
    def project_unitetest_dir(self) -> str:
        return join_path(self.project_dir, Unittest_Module_Folder)

    @property
    def project_config_file(self) -> str:
        return join_path(self.project_dir, Project_Config_File)

    @property
    def project_pack_file(self) -> str:
        return join_path(self.project_dir, Project_Pack_File)

    @property
    def project_requirement_file(self) -> str:
        return join_path(self.project_dir, Project_Requirement_File)

    def process_command(self):
        self.__parse_command()

        if hasattr(self.args, 'command'):
            if hasattr(self, self.args.command):
                func = getattr(self, self.args.command)
                if callable(func):
                    func()
                else:
                    self.parser.print_help()
        else:
            self.parser.print_help()

    def test(self):
        import unittest
        from .unit_test import get_test_suite
        runner = unittest.TextTestRunner()
        runner.run(get_test_suite())

    def pack(self) -> None:
        from .project.pack import HyssopPack
        if self.project_dir:
            HyssopPack().pack(self.project_dir, self.args.o,
                              prepare_wheels=self.args.add_wheels,
                              compile_py=not self.args.decompile_pyc)

    def version(self):
        print('hyssop {}'.format(Version))

    def create(self):
        self.project_dir = self.project_dir if self.project_dir else 'hello_world'

        if not os.path.isdir(self.project_dir):
            os.makedirs(self.project_dir)

        self._create_project_component_files()
        self._create_project_controller_files()
        self._create_project_config_files()
        self._create_project_test_files()
        self._create_project_pack_files()
        self._create_project_requirement_files()

        print('project created at', os.path.abspath(self.project_dir))

    def _create_project_component_files(self):
        if not os.path.isdir(self.project_component_dir):
            os.makedirs(self.project_component_dir)

        with open(join_path(self.project_component_dir, '__init__.py'), 'w') as f:
            f.write('''\
from hyssop.project.component import ComponentTypes, ConfigComponentValidator

from hyssop.project.config_validator import ConfigContainerMeta, ConfigElementMeta

# add hello validator to component config validator
ConfigComponentValidator.set_cls_parameters(
    ConfigContainerMeta('hello', False,
        ConfigElementMeta('p1', str, True) # validate HelloComponent's 'p1' argument is required and string type
    )
)

class HelloComponentTypes(ComponentTypes):
    Hello = ('hello', 'hello', 'HelloComponent')
''')

        with open(join_path(self.project_component_dir, 'hello.py'), 'w') as f:
            f.write('''\
from hyssop.project.component import Component
from . import HelloComponentTypes

class HelloComponent(Component):
    def init(self, component_manager, p1, *arugs, **kwargs) -> None:
        print('init Hello component load from', __package__, 'and the parameters p1:', p1)

    def hello(self):
        return 'Hello World, This is hyssop generate hello component'
''')

    def _create_project_controller_files(self):
        pass

    def _create_project_test_files(self):
        if not os.path.isdir(self.project_unitetest_dir):
            os.makedirs(self.project_unitetest_dir)

        with open(join_path(self.project_unitetest_dir, '__init__.py'), 'w') as f:
            f.write('''\
from hyssop.unit_test import UnitTestTypes

class UTTypes(UnitTestTypes):
    UT1 = ('ut1', 'ut1', 'UT1TestCase')
''')

        with open(join_path(self.project_unitetest_dir, 'ut1.py'), 'w') as f:
            f.write('''\
from hyssop.unit_test import UnitTestCase

class UT1TestCase(UnitTestCase):
    def test(self):
        # implement unit test here...
        import os
        from component import HelloComponentTypes
        from hyssop.project.mixin import ProjectMixin

        project = ProjectMixin()
        project.load_project(os.path.dirname(os.path.dirname(__file__)))
        comp = project.component_manager.get_component(
            HelloComponentTypes.Hello)
        print(comp.hello())
''')

    def _create_project_config_files(self):
        with open(self.project_config_file, 'w') as f:
            f.write('''\
name: hyssop Project
debug: False
component:
  hello: 
    p1: 'This is p1'
''')

    def _create_project_pack_files(self):
        with open(self.project_pack_file, 'w') as f:
            f.write('''
# This is packing list indicated what are the files should be pack
# If this file does not exist under the project folder, all of the files under the folder will be packed

include:
# List absolute or relative path of additional file or directory to be packed
# - example.txt
# - example_dir

exclude:
# List absolute or relative path of file, directory, or file extension to be ignored.
- '.log'
''')

    def _create_project_requirement_files(self):
        # requirement
        from . import __name__, Version
        with open(self.project_requirement_file, 'w') as f:
            f.write('{}>={}'.format(__name__, Version))

    def __create_command_parser(self):
        self.parser = argparse.ArgumentParser(prog='hyssop')
        self.command_parsers = self.parser.add_subparsers(title='command')

        test_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Test_Project, help='test hyssop library or specfied project directory path')
        test_parser.add_argument(self.args_key_project_directory, nargs='?',
                                 help='project directory path')
        test_parser.set_defaults(command=CommandProcessor.Command_Test_Project)

        make_serv_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Create_Project, help='create a project template with specfied project directory path')
        make_serv_parser.add_argument(self.args_key_project_directory,
                                      help='project directory path')
        make_serv_parser.set_defaults(
            command=CommandProcessor.Command_Create_Project)

        pack_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Pack_Project, help='pack project with specfied project directory path')
        pack_parser.add_argument(self.args_key_project_directory,
                                 help='project directory path')
        pack_parser.add_argument(
            '-o', help='specify output compressed file path', default=None)
        pack_parser.add_argument('-w', '--add_wheels', action='store_true',
                                 help='add dependency wheel files')
        pack_parser.add_argument('-d', '--decompile_pyc', action='store_true',
                                 help='disable compile .py to .pyc')
        pack_parser.set_defaults(command=CommandProcessor.Command_Pack_Project)

        version_serv_parser = self.command_parsers.add_parser(
            CommandProcessor.Command_Show_Version, help='print version number to console')
        version_serv_parser.set_defaults(
            command=CommandProcessor.Command_Show_Version)

    def __parse_command(self):
        sys.path.insert(0, os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        self.args = self.parser.parse_args()

        if hasattr(self.args, self.args_key_project_directory):
            if self.args.project_directory:
                self.project_dir = join_to_abs_path(
                    self.args.project_directory)
                sys.path.insert(0, os.path.abspath(self.project_dir))
                sys.path.insert(0, os.path.dirname(
                    os.path.abspath(self.project_dir)))
