# coding=utf-8

import glob
import re
from ..core.command import Command
from jinja2 import Environment, PackageLoader
from ..utils.file_helpers import *
from ..utils.utils import *
from flutter_gen.utils.print import *


class GenerateColorCommand(Command):
    def __init__(self):
        super(GenerateColorCommand, self).__init__()

    def run(self):
        try:
            pi = PrintInfo(name="generate color")
            pi.start()
            colors = []
            with open("./assets/color/colors.txt", 'r') as f:
                for line in f:
                    color = line.strip().replace('#', '').upper()
                    colors.append(color)
            env = Environment(
                loader=PackageLoader('flutter_gen_templates', 'gen'),
                trim_blocks=True,
                lstrip_blocks=True
            )
            template = env.get_template("colors.dart")
            content = template.render(
                colors=colors,
            )
            output_file = create_file(
                content, "colors", "g.dart", "lib/generated")
            pi.end()
        except Exception as e:
            print_error(e)
