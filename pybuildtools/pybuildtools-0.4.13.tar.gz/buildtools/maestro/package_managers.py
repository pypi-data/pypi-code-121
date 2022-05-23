'''
Package management BuildTargets.

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
import json
import os, shutil
from buildtools import os_utils, utils
from buildtools.maestro.base_target import SingleBuildTarget


class _NPMLikeBuildTarget(SingleBuildTarget):
    def __init__(self, invocation, base_command=None, working_dir='.', opts=[], files=[], target=None, dependencies=[], exe_path=None, specfile=None, lockfile=None, modules_dir=None):
        self.specfile = specfile
        self.lockfile = lockfile

        self.working_dir = working_dir
        self.opts = opts
        self.exe_path = exe_path
        self.base_command = base_command
        self.invocation = invocation

        self.modules_dir = modules_dir

        if self.exe_path is None:
            self.exe_path = os_utils.which(invocation)
        super().__init__(target=target, files=files, dependencies=dependencies)

    def get_lockfile(self):
        return self.lockfile

    def get_specfile(self):
        return self.specfile

    def clean(self):
        super().clean()
        if self.modules_dir is not None and os.path.isdir(self.modules_dir):
            for filename in os_utils.get_file_list(self.modules_dir):
                self.removeFile(filename)
            shutil.rmtree(self.modules_dir)

    def get_config(self):
        return {
            'working_dir': self.working_dir,
            'opts': self.opts,
            'exe_path': self.exe_path,
            'base_command': self.base_command,
            'invocation': self.invocation,
            'specfile': {
                'filename': self.get_specfile(),
                'md5': utils.md5sum(self.get_specfile()) if self.get_specfile() is not None else None,
            },
            'lockfile': {
                'filename': self.get_lockfile(),
                'md5': utils.md5sum(self.get_lockfile()) if self.get_lockfile() is not None else None,
            }
        }

    def buildOpts(self):
        return [self.exe_path] + self.opts

    def build(self):
        opts = self.buildOpts()
        with os_utils.Chdir(self.working_dir):
            os_utils.cmd([self.exe_path] + self.opts, show_output=True, echo=self.should_echo_commands(), critical=True)
        if not os.path.isfile(self.target):
            self.touch(self.target)


class YarnBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Yarn'
    BT_LABEL = 'YARN'

    def __init__(self, base_command=None, working_dir='.', opts=[], modules_dir='node_modules', target=None, dependencies=[], yarn_path=None, lockfile=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.yarn-integrity')
        super().__init__('yarn', modules_dir=modules_dir, working_dir=working_dir, opts=opts, target=target, exe_path=yarn_path, files=[os.path.join(working_dir, 'package.json')], dependencies=[])


class NPMBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'NPM'
    BT_LABEL = 'NPM'

    def __init__(self, base_command=None, working_dir='.', opts=[], modules_dir='node_modules', target=None, dependencies=[], npm_path=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.npm.target')
        super().__init__('npm', working_dir=working_dir, modules_dir=modules_dir, opts=opts, target=target, exe_path=npm_path, files=[os.path.join(working_dir, 'package.json')], dependencies=[])


class BowerBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Bower'
    BT_LABEL = 'BOWER'

    def __init__(self, base_command=None, working_dir='.', opts=[], modules_dir='bower_components', target=None, dependencies=[], bower_path=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.bower.target')
        super().__init__('bower', working_dir=working_dir, modules_dir=modules_dir, opts=opts, target=target, exe_path=bower_path, files=[os.path.join(working_dir, 'bower.json')], dependencies=[])


class GruntBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Grunt'
    BT_LABEL = 'GRUNT'

    def __init__(self, base_command=None, working_dir='.', opts=[], target=None, dependencies=[], grunt_path=None):
        if target is None:
            target = os.path.join(working_dir, 'tmp', '.grunt.target')
        super().__init__('grunt', working_dir=working_dir, opts=opts, target=target, exe_path=grunt_path, files=[os.path.join(working_dir, 'Gruntfile.js')], dependencies=[])


class ComposerBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Composer'
    BT_LABEL = 'COMPOSER'

    def __init__(self, base_command='install', working_dir='.', opts=[], modules_dir='vendor', target=None, dependencies=[], composer_path=None, composer_json=None, composer_lock=None, composer_bin_dir=None):
        if composer_json is None:
            composer_json = os.path.abspath(os.path.join(working_dir, 'composer.json'))
        if composer_lock is None:
            composer_lock = os.path.abspath(os.path.join(working_dir, 'composer.lock'))
        if target is None:
            target = os.path.abspath(os.path.join(working_dir, modules_dir, '.composer.target'))
        self.composer_bin_dir = composer_bin_dir
        super().__init__('composer', base_command=base_command, modules_dir=modules_dir, working_dir=working_dir, opts=opts, target=target, exe_path=composer_path, files=[], dependencies=[], specfile=composer_json, lockfile=composer_lock)
        self.detectAutoloadedFiles()

    def processOpts(self):
        o = [self.exe_path, self.base_command] + self.opts
        o += ['-d', self.working_dir]
        return o

    def detectAutoloadedFiles(self):
        packagedata = {}
        if os.path.isfile(self.specfile):
            with open(self.specfile, 'r') as f:
                packagedata = json.load(f)

        for autoload_type, autoload_namespaces in packagedata.get('autoload', {}).items():
            if autoload_type == 'psr-4':
                for nspath in autoload_namespaces.values():
                    for filename in os_utils.get_file_list(nspath, '.'):
                        phpfn = os.path.abspath(filename)
                        self.files += [phpfn]

        self.files = list(set(self.files))

    def build(self):

        env = os_utils.ENV.clone()
        env.set('COMPOSER', self.specfile, noisy=self.should_echo_commands())
        if self.modules_dir is not None:
            env.set('COMPOSER_VENDOR_DIR', self.modules_dir, noisy=self.should_echo_commands())
        if self.composer_bin_dir is not None:
            env.set('COMPOSER_BIN_DIR', self.composer_bin_dir, noisy=self.should_echo_commands())
        cmdline = self.processOpts()
        os_utils.cmd(cmdline, show_output=True, echo=self.should_echo_commands(), critical=True, env=env)
        if os.path.isfile(self.target):
            self.touch(self.target)


class BrowserifyBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Browserify'
    BT_LABEL = 'BROWSERIFY'

    def __init__(self, base_command=None, working_dir='.', opts=[], target=None, files=[], dependencies=[], browserify_path=None):
        super().__init__('browserify', working_dir=working_dir, opts=opts, target=target, exe_path=browserify_path, files=files, dependencies=[])
