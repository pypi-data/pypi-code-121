# coding=utf-8

import glob
import re
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.file_helpers import *
from ..utils.utils import *
from flutter_gen.utils.print import *


class FontData(object):
    def __init__(self, name, family_name):
        self.name = name
        self.family_name = family_name


class GenerateFontCommand(Command):
    def __init__(self):
        super(GenerateFontCommand, self).__init__()

    def run(self):
        try:
            pi = PrintInfo(name="generate font")
            pi.start()
            fonts = []
            pubspec_text = read("pubspec.yaml")
            pubspec_data = yaml.safe_load(pubspec_text)
            flutter = pubspec_data["flutter"]
            if "fonts" in flutter:
                for font in flutter["fonts"]:
                    family_name = font["family"]
                    name = family_name[0].lower() + family_name[1:]
                    fonts.append(FontData(name, family_name))
            else:
                print_error("No fonts available")
            env = Environment(
                loader=PackageLoader('flutter_gen_templates', 'gen'),
                trim_blocks=True,
                lstrip_blocks=True
            )
            template = env.get_template("fonts.dart")
            content = template.render(
                fonts=fonts,
            )
            output_file = create_file(
                content, "fonts", "g.dart", "lib/generated")
            pi.end()
        except Exception as e:
            print_error(e)
