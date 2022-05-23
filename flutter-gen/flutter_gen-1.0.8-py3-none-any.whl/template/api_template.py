# coding=utf-8

import os
from datetime import datetime
from jinja2 import Environment, PackageLoader

from flutter_gen.utils.dart_helpers import format_dart_file_code

from flutter_gen.utils.utils import *
from flutter_gen.utils.str_helpers import upper_first_letter, lower_first_letter
from flutter_gen.utils.file_helpers import create_file
import re


class APITemplate(object):
    def __init__(self, name):
        self.name = name
        self.file_name = self.camel_to_snake(name)

    def run(self):
        log('Successfully create file:')
        env = Environment(
            loader=PackageLoader('flutter_gen_templates', 'api'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template("api.dart")
        content = template.render(
            name=self.name,
            file_name=self.file_name,
        )
        output_file = create_file(
            content, "api_" + self.file_name, "dart", "lib/data/api/data_source")
        log('    {}'.format(output_file))

    def is_camel_case(self, s):
        return s != s.lower() and s != s.upper() and "_" not in s

    def camel_to_snake(self, name):
        if self.is_camel_case(name):
            upper_case_letters = re.findall('[A-Z][^A-Z]*', name)
            return '_'.join(upper_case_letters).lower()
        else:
            logError(
                'Invalid filename. Filename need to be camel string.\nFor example: MyCamelCase')
            exit(1)
