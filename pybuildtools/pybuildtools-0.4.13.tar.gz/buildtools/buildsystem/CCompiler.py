'''
Generic C Compiler wrapper

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
from buildtools.bt_logging import log
from buildtools import os_utils


class CCompiler(object):

    def __init__(self, output, template=None):
        self.files = []
        self.output = output
        self.cflags = None

        self.compiler = ''
        self.linker = ''

    def compile(self):
        return


class WindowsCCompiler(CCompiler):

    def __init__(self, output, template=None):
        super(WindowsCCompiler, self).__init__(output, template)
        if template is not None:
            self.cflags = template.cflags
        if self.cflags is None:
            self.cflags = ["-nologo", "-O2", "-MD"]

        self.compiler = 'cl'
        self.linker = 'link'

    def compile(self):
        ofiles = []
        for filename in self.files:
            of = "{}.obj".format(os.path.splitext(filename)[0])
            if os_utils.canCopy(filename, of):  # Checks mtime.
                os_utils.cmd([self.compiler, '-c'] + self.cflags + ['-Fo:', of, filename], critical=True, show_output=True, echo=True)
            ofiles.append(of)
        os_utils.cmd([self.linker, '/lib', '/nologo', '/out:' + self.output] + ofiles, critical=True, show_output=True, echo=True)
