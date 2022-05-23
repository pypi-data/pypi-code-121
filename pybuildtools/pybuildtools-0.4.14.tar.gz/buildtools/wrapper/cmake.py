'''
cmake Wrapper

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
import os, subprocess

from buildtools.bt_logging import log
from buildtools.os_utils import cmd, ENV, BuildEnv

class CMake(object):
    @classmethod
    def GetVersion(cls):
        rev = subprocess.Popen(['cmake', '--version'], stdout=subprocess.PIPE).communicate()[0][:-1]
        if rev:
            return rev.decode('utf-8').split()[2]

    def __init__(self):
        self.flags = {}
        self.generator = None

    def setFlag(self, key, val):
        log.info('CMake: {} = {}'.format(key, val))
        self.flags[key] = val

    def build(self, CMAKE='cmake', dir='.', env=None, target=None, moreflags=None, env_dump=False):
        if moreflags is None:
            moreflags=[]
        if env is None:
            env = ENV.env
        flags = ['--build', dir]
        if target is not None:
            moreflags += ['--target', target]

        flags += moreflags

        with log.info('Running CMake --build:'):
            if env_dump: BuildEnv.dump(env)
            return cmd([CMAKE] + flags, env=env, critical=True, echo=True)

    def run(self, CMAKE='cmake', env=None, dir='.', moreflags=None, env_dump=False):
        if env is None:
            env = ENV.env
        if moreflags is None:
            moreflags=[]
        flags = []

        if self.generator is not None:
            flags += ['-G', self.generator]

        for key, value in self.flags.items():
            flags += ['-D{0}={1}'.format(key, value)]

        flags += moreflags

        with log.info('Running CMake:'):
            if env_dump: BuildEnv.dump(env)
            return cmd([CMAKE] + flags + [dir], env=env, critical=True, echo=True)
        return False
