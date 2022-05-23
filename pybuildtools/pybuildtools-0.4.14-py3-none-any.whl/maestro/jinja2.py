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
import os
from typing import List
from .base_target import SingleBuildTarget
from .. import os_utils
import jinja2

def j_cmd(cmdline: List[str], echo=False, lang='', comment=None, env=None, critical=True, globbify=False):
    o = ''
    if env is None:
        env = os_utils.ENV.clone()
    if echo:
        if comment is not None:
            comment = f'# {comment}\n'
        else:
            comment = ''
        o += f'```shell\n{comment}$ {os_utils._args2str(cmdline)}\n```\n'
    o += f'```{lang}\n'
    o += os_utils.cmd_out(cmdline, True, env, critical, globbify)
    o += '```\n'
    return o

class Jinja2BuildTarget(SingleBuildTarget):
    BT_LABEL = 'JINJA2'
    def __init__(self, source_filename, dest_filename, jenv: jinja2.Environment, jinja_vars={}, dependencies=[]):
        self.source_filename = source_filename
        self.jenv = jenv
        self.jinja_vars = jinja_vars
        super().__init__(target=dest_filename, files=[source_filename], dependencies=dependencies)

    def build(self):
        os_utils.ensureDirExists(os.path.dirname(self.target))
        with open(self.target, 'w') as f:
            f.write(self.jenv.get_template(self.source_filename).render(self.jinja_vars))
