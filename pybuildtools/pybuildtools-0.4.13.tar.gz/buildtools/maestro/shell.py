'''
Buildtarget for executing arbitrary shell commands.

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
import subprocess

from buildtools import os_utils
from buildtools.maestro.base_target import BuildTarget

class CommandBuildTarget(BuildTarget):
    BT_LABEL = 'SHELL'
    #BT_COLOR = 'red'

    def __init__(self, targets, files, cmd, show_output=False, echo=None, dependencies=[], provides=[], name=None, globbify=False, cwd='.'):
        self.cmd = cmd
        self.cwd = cwd
        self.show_output = show_output
        self.echo = echo
        self.globbify = globbify
        newt = []
        for x in targets:
            if x.startswith('@'):
                x = self.genVirtualTarget(x[1:])
            newt.append(x)
        super().__init__(newt, files, dependencies, provides, name or subprocess.list2cmdline(cmd))

    def get_config(self):
        return {
            'cmd': self.cmd,
            'cwd': self.cwd,
            'show_output': self.show_output,
            'echo': self.echo
        }

    def build(self):
        with os_utils.Chdir(self.cwd):
            os_utils.cmd(self.cmd, show_output=self.show_output, echo=self.should_echo_commands() if self.echo is None else self.echo, critical=True, globbify=self.globbify)
        for t in self.provides():
            self.touch(t)
