# coding=utf-8

from os import read
from flutter_gen.config.config_cmd import ConfigCommand
from flutter_gen.utils.utils import *
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.str_helpers import snake_to_camel, plural_to_singular
from ..utils.file_helpers import create_file, read_json
from ..utils.json_helpers import get_keys
from flutter_gen.utils.print import *
import os


class LocaleItem(object):
    def __init__(self, name, key):
        self.name = name
        self.key = key


class GenerateLocalizationCommand(Command):
    def __init__(self):
        super(GenerateLocalizationCommand, self).__init__()

    def run(self):
        pi = PrintInfo(name="generate localization")
        pi.start()
        items = []
        # config = ConfigCommand.getInstance()
        # translations_path = config.read_config("localization.input_path")
        # output_dir = config.read_config("localization.output_path")
        # output_file_name = config.read_config("localization.file_name")
        translations_path = "assets/i18n"
        try:
            for file in os.listdir(translations_path):
                if file.endswith(".json"):
                    name = os.path.basename(file)
                    if name == "en-US.json":
                        json = read_json("%s/en-US.json" % translations_path)
                        break
                    else:
                        json = read_json("%s/%s" % (translations_path, file))
        except FileNotFoundError:
            print_error("i18n file not found")
            return
        val_names = []
        key_paths = []
        get_keys(json, val_names, separator="_")
        get_keys(json, key_paths, separator=".")
        for i in range(len(val_names)):
            items.append(LocaleItem(val_names[i], key_paths[i]))
        env = Environment(
            loader=PackageLoader("flutter_gen_templates", "gen"),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("i18n.dart")
        content = template.render(items=items)
        file_path = create_file(
            content, "i18n", "g.dart", "lib/generated")
        pi.end()
