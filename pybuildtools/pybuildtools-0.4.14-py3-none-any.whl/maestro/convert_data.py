'''
BLURB GOES HERE.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import codecs
import os
import toml
import json
import enum

from ruamel.yaml import YAML
yaml = YAML(typ='safe', pure=True)

from buildtools import log, os_utils
from buildtools.maestro.base_target import SingleBuildTarget

class EDataType(enum.Enum):
    JSON = 'json'
    YAML = 'yaml'
    TOML = 'toml'

class ConvertDataBuildTarget(SingleBuildTarget):
    BT_TYPE = 'ConvertData'
    BT_LABEL = 'CONVERT'
    def __init__(self, target=None, filename='', dependencies=[], from_type=EDataType.JSON, to_type=EDataType.JSON, indent_chars=None, pretty_print=False):
        self.from_type=from_type
        self.to_type=to_type
        self.indent_chars=indent_chars
        self.pretty_print=pretty_print

        super().__init__(target, [filename, os.path.abspath(__file__)], dependencies)

    def get_label(self):
        return '{} {} -> {}'.format(self.BT_LABEL, self.from_type.name, self.to_type.name)

    def get_config(self):
        return {
            'from': self.from_type.value,
            'to': self.to_type.value,
            'indent_chars': self.indent_chars,
            'pretty_print': self.pretty_print,
        }

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        data = {}
        with open(self.files[0],'r', encoding='utf-8-sig') as inf:
            if self.from_type == EDataType.YAML:
                data=yaml.load(inf)
            if self.from_type == EDataType.JSON:
                data=json.load(inf)
            if self.from_type == EDataType.TOML:
                data=toml.load(inf)
        with open(self.target, 'w', encoding='utf-8') as outf:
            if self.to_type == EDataType.YAML:
                kwargs = {}
                kwargs['default_flow_style']=not self.pretty_print
                if self.indent_chars is not None and self.pretty_print:
                    kwargs['indent']=self.indent_chars
                yaml.dump(data, outf, **kwargs)
            if self.to_type == EDataType.JSON:
                json.dump(data, outf, indent=self.indent_chars if self.pretty_print and self.indent_chars is not None else None)
            if self.to_type == EDataType.TOML:
                toml.dump(data, outf)
