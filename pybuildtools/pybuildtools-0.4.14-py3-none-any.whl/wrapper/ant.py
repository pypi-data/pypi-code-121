'''
Ant wrapper

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

from buildtools.os_utils import cmd

class Ant(object):
    def __init__(self):
        self.defines = {}
        self.propertyfiles=[]

    def AddDefine(self, k, v):
        self.defines[k]=v

    def AddPropertyFile(self, filename):
        self.propertyfiles += [filename]

    def Build(self, file, targets=['target'], ant='ant'):
        cmdline = [ant]

        cmdline += ['-file', target]

        for k, v in sorted(self.defines.items()):
            cmdline += ['-D{}={}'.format(k, v)]

        for filename in self.propertyfiles:
            cmdline += ['-propertyfile',filename]

        cmdline += targets

        return cmd(cmdline, critical=True, echo=True)
