# coding=utf-8

from flutter_gen.config.config_cmd import ConfigCommand
from flutter_gen.rename.rename_cmd import RenameCommand
from ..core.command import Command
from ..utils.utils import *

import os


class CreateCommand(Command):
    def __init__(self):
        super(CreateCommand, self).__init__()

    def create_app(self):
        (project_name, package_name,
         bundle_name) = ConfigCommand.getInstance().update_project_info()
        if project_name and package_name and bundle_name:
            git("clone", "https://github.com/tien-px/pt_flutter_clean_architecture_template", package_name)
            change_working_dir(package_name)
            RenameCommand(package_name).rename_app()
        else:
            print("Wrong input")
