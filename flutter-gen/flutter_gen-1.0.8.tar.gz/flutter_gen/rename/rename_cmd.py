# coding=utf-8

from ..config.config_cmd import ConfigCommand
from ..core.command import Command
from ..utils.utils import *
from ..utils.file_replace import replace
import os

class RenameCommand(Command):
    def __init__(self, target_name = None):
        super(RenameCommand, self).__init__()
        self.target_name = target_name

    def rename_app(self):
        # config = get_current_rename_config()
        # print("Current name: %s" % config.name)
        # print(config.application_name)
        # print(config.dart_package_name)
        # print(config.application_id)
        # print(config.bundle_id)
        # print(config.android_package_name)

        current_name = get_current_dart_package_name()
        config = ConfigCommand.getInstance()
        config_target_name = config.read_config("project.package_name")
        new_name = self.target_name if self.target_name is not None else config_target_name
        files_updated = replace(current_name,
                            new_name,
                            "./", 
                            recursive=True)
        print('Files updated:')
        for file in files_updated:
            print("%s MODIFIED" % file)
        



