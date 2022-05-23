# coding=utf-8

from flutter_gen.utils.dart_helpers import write_content_to_file
from flutter_gen.config.config_cmd import ConfigCommand
from flutter_gen.rename.rename_cmd import RenameCommand
from ..core.command import Command
from ..utils.utils import *
import json


class CreateI18NCommand(Command):
    def __init__(self, key: str, text: str):
        super(CreateI18NCommand, self).__init__()
        self.key = key
        self.text = text

    def update(self, obj, path, value):
        *path, last = path.split(".")
        for bit in path:
            obj = obj.setdefault(bit, {})
        obj[last] = value

    def create(self):
        default_file = "en-US.json"
        with open('assets/i18n/%s' % (default_file), 'r+', encoding='utf8') as json_file:
            data = json.load(json_file)
            self.update(data, self.key, self.text)
            json_object = json.dumps(data, indent=4)
            # Write to file
            write_content_to_file(json_file, json_object)
        new_key = self.key.replace('.', '_')
        logResult("i18n.%s" % (new_key))
