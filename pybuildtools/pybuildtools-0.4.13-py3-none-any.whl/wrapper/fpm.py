'''
FPM Wrapper

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
from buildtools.os_utils import cmd

class FPM(object):
    def __init__(self):
        self.name = ''
        self.version = ''
        self.input_type = ''
        self.output_type = ''
        self.workdir = ''
        self.iteration = 0

        self.dependencies = []
        self.conflicts = []
        self.replaces = []
        self.provides = []
        self.inputs = []

        self.filebinds = []
        self.configs = []

        self.afterInstall = None
        self.beforeInstall = None
        self.afterRemove = None
        self.beforeRemove = None

    def LoadControl(self, filename):
        '''
        Load Debian CONTROL file.
        '''
        with open(filename, 'r') as f:
            for line in f:
                directive, content = line.split(':', 1)
                func = getattr(self, '_handle_' + directive.lower())
                if func: func(content.strip(), line)

    def _file2list(self, filename):
        o = []
        with open(filename, 'r') as f:
            for line in f:
                o += [line.strip()]
        return o

    def LoadDebianDirectory(self, dir):
        '''Loads DEBIAN/ directory.'''
        file_conf = os.path.join(dir, 'conffiles')
        if os.path.isfile(file_conf):
            newconfigs = self._file2list(file_conf)
            if len(newconfigs) > 0:
                self.configs += newconfigs
                log.info('Added %r to configs', ', '.join(newconfigs))

        def setIfIsFile(prop, filename):
             if os.path.isfile(filename):
                 setattr(self, prop, filename)
                 log.info('Set %r to %r', prop, filename)

        setIfIsFile('afterInstall', os.path.join(dir, 'postinst'))
        setIfIsFile('beforeInstall', os.path.join(dir, 'preinst'))
        setIfIsFile('afterRemove', os.path.join(dir, 'postrm'))
        setIfIsFile('beforeRemove', os.path.join(dir, 'prerm'))

    def _handle_package(self, content, line):
        self.name = content

    def _handle_version(self, content, line):
        self.version = content

    def _handle_section(self, content, line):
        return  # web

    def _handle_priority(self, content, line):
        return  # optional

    def _handle_architecture(self, content, line):
        self.architecture = content

    def _handle_essential(self, content, line):
        return  # yes/no

    def _handle_depends(self, content, line):
        self.dependencies = [x.strip() for x in content.split(',')]

    def _handle_maintainer(self, content, line):
        self.maintainer = content

    def _handle_description(self, content, line):
        self.description = content

    def AddDepend(self, depend):
        self.dependencies += [depend]

    def _BuildIfNotNone(self, cmdline_opt, value):
        if value is not None:
            return [cmdline_opt, value]
        return []

    def Build(self, target_file, fpm='fpm'):
        cmdline = [fpm]

        cmdline += ['-s', self.input_type]
        cmdline += ['-t', self.output_type]
        cmdline += ['-C', self.workdir]
        cmdline += ['-p', target_file]
        cmdline += ['-n', self.name]
        cmdline += ['-v', self.version]
        cmdline += ['-a', self.architecture]

        if self.maintainer != '':
            cmdline += ['-m', self.maintainer]
        if self.description != '':
            cmdline += ['--description', self.description]
        if self.iteration > 0:
            cmdline += ['--iteration', self.iteration]

        for dep in self.dependencies:
            cmdline += ['-d', dep]

        for provided in self.provides:
            cmdline += ['--provides', provided]

        for conflict in self.conflicts:
            cmdline += ['--conflicts', conflict]

        for replacee in self.replaces:
            cmdline += ['--replaces', replacee]

        for config in self.configs:
            cmdline += ['--config-files', config]

        cmdline += self._BuildIfNotNone('--after-install', self.afterInstall)
        cmdline += self._BuildIfNotNone('--before-install', self.beforeInstall)
        cmdline += self._BuildIfNotNone('--after-remove', self.afterRemove)
        cmdline += self._BuildIfNotNone('--before-remove', self.beforeRemove)

        for inp in self.inputs:
            cmdline += [inp]

        #print(target_file, repr(cmdline))
        return cmd(cmdline, critical=True, echo=True)
