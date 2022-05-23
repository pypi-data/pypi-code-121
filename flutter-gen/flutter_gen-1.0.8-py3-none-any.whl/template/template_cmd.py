# coding=utf-8

from subprocess import call

from flutter_gen.config.config_cmd import ConfigCommand
from flutter_gen.template.base_template import BaseTemplate
from ..utils.utils import *
from ..core.command import Command, CommandOption


class Template(object):

    class TemplateType:
        BASE = 'base'


class TemplateCommand(Command):
    def __init__(self, template_name, scene_name, options):
        super(TemplateCommand, self).__init__()
        self.template_name = template_name
        self.scene_name = scene_name
        self.options = CommandOption(options)

    def get_project_package_name(self):
        try:
            name = get_current_dart_package_name()
            print("Current package name: %s" % name)
            return name.strip()
        except (IOError, OSError) as e:
            logError("Please run this command in flutter folder.")
            exit(1)

    def create_files(self):
        if self.template_name == Template.TemplateType.BASE:
            template = BaseTemplate(
                self.options,
                self.scene_name,
                self.get_project_package_name()
            )
            output_path = template.create_files()
            # Reload disk
            logAndCommand("ide.action.synchronize")
        else:
            logError("Invalid template type.")
            exit(1)
