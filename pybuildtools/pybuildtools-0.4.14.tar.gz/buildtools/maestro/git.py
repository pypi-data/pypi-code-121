'''
Git commands.  Mostly used for submodules.

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
import re
import shutil
import pygit2
from buildtools import log, os_utils, utils, error
from buildtools.maestro.base_target import SingleBuildTarget
from buildtools.repo.git import GitRepository
from buildtools.wrapper.git import Git

import toml

#from ruamel.yaml import YAML
#yaml = YAML(typ='safe', pure=True)

'''
[submodule "lib/js/jquery-ui"]
path = lib/js/jquery-ui
url = https://github.com/jquery/jquery-ui
[submodule "lib/js/tag-it"]
path = lib/js/tag-it
url = https://github.com/fagianijunior/tag-it.git
[submodule "lib/js/autobahn"]
path = lib/js/autobahn
url = https://github.com/crossbario/autobahn-js-built.git
[submodule "lib/js/libgif"]
path = lib/js/libgif
url = https://github.com/buzzfeed/libgif-js.git
[submodule "lib/js/jsrender"]
path = lib/js/jsrender
url = https://github.com/BorisMoore/jsrender.git
[submodule "lib/js/videoframe"]
path = lib/js/videoframe
url = https://github.com/allensarkisyan/VideoFrame.git
[submodule "lib/highlight.js"]
path = lib/js/highlight.js
url = https://github.com/isagalaev/highlight.js
'''

REG_SUBMODULE_SECTION = re.compile(r'\[submodule "([^"]+)"\]')


class GitSubmoduleCheckTarget(SingleBuildTarget):
    BT_TYPE = 'GitSubmodules'
    BT_LABEL = 'GIT SUBMODULES'

    def __init__(self, target=None, gitmodulesfile=None, gitconfigfile=None):
        self.gitconfigfile = gitconfigfile if gitconfigfile is not None else os.path.join('.git','config')
        self.gitmodulesfile = gitmodulesfile if gitmodulesfile is not None else '.gitmodules'
        super().__init__(target='.gitmodules-checked', files=[self.gitconfigfile,self.gitmodulesfile], dependencies=[], provides=[], name=self.gitmodulesfile)

    def is_stale(self):
        if super().is_stale():
            return True
        if os.path.isfile(self.target):
            state = Git.GetBranch()+Git.GetCommit()
            with open(self.target,'r') as f:
                if f.read().strip() == state:
                    return True
        return True

    def provides(self):
        return [self.target, self.gitmodulesfile+'.yml', '.gitconfig.yml']

    def build(self):
        gitmodules = {}
        with open(self.gitmodulesfile, 'r') as tomlf:
            smid = None
            for line in tomlf:
                line = line.strip()
                m = REG_SUBMODULE_SECTION.match(line)
                if m is not None:
                    smid = m.group(1).strip()
                    gitmodules[smid] = {}
                if '=' in line:
                    k, v = line.split('=', 2)
                    gitmodules[smid][k.strip()] = v.strip()
        gitconfig = {}
        with open(self.gitconfigfile, 'r') as tomlf:
            smid = None
            for line in tomlf:
                line = line.strip()
                #print(line)
                m = REG_SUBMODULE_SECTION.match(line)
                if m is not None:
                    smid = m.group(1).strip()
                    gitconfig[smid] = {}
                if smid is not None and '=' in line:
                    #print(line)
                    k, v = line.split('=', 2)
                    gitconfig[smid][k.strip()] = v.strip()
        '''
        with open(self.gitmodulesfile + '.yml', 'w') as f:
            yaml.dump(gitmodules, f, default_flow_style=False)
        with open('.gitconfig.yml', 'w') as f:
            yaml.dump(gitconfig, f, default_flow_style=False)
        '''
        for repoID, repoconf in gitconfig.items():
            if repoID not in gitmodules.keys():
                with log.warn('Submodule %s is present in .git/config but not .gitmodules!', repoID):
                    pathspec = repoconf.get('path', repoID)
                    path = os.path.abspath(pathspec)
                    tag = repoconf.get('tag', None)
                    branch = repoconf.get('branch', 'HEAD' if tag is None else None)
                    log.info('path = %s', pathspec)
        for repoID, repoconf in gitmodules.items():
            if repoID not in gitconfig.keys():
                with log.warn('Submodule %s is present in .gitmodules but not .git/config!', repoID):
                    pathspec = repoconf.get('path', repoID)
                    path = os.path.abspath(pathspec)
                    tag = repoconf.get('tag', None)
                    branch = repoconf.get('branch', 'HEAD' if tag is None else None)
                    opts = []
                    if branch != 'HEAD':
                        opts += ['-b', branch]
                    log.info('path = %s', pathspec)
                    if os.path.isdir(path):
                        log.warn('Removing existing %s directory.', path)
                        shutil.rmtree(path)
                    cmd = ['git', 'submodule', 'add']+opts+['-f', '--name', repoID, '--', repoconf.get('url'), pathspec]
                    os_utils.cmd(cmd, critical=True, echo=self.should_echo_commands(), show_output=True)
                    #log.error('Would exec: %s', ' '.join(cmd))

        for repoID, repoconf in gitmodules.items():
            with log.info('Checking %s...', repoID):
                pathspec = repoconf.get('path', repoID)
                path = os.path.abspath(pathspec)
                tag = repoconf.get('tag', None)
                branch = repoconf.get('branch', 'HEAD' if tag is None else None)
                if os.path.isdir(path):
                    desired_commit = ''
                    cmdline = ['git', 'ls-tree', Git.GetBranch(), pathspec]
                    stdout, stderr = os_utils.cmd_output(cmdline, echo=self.should_echo_commands(), critical=True)
                    skip_this = False
                    for line in (stdout+stderr).decode('utf-8').splitlines():
                        if line.startswith('error:') or line.startswith('fatal:'):
                            log.critical(line)
                            raise error.SubprocessThrewError(cmdline, line)
                        line,repoID = line.strip().split('\t')
                        _, _, desired_commit = line.split(' ')
                    if not skip_this:
                        with os_utils.Chdir(path, quiet=not self.should_echo_commands()):
                            cur_commit = Git.GetCommit(short=False, quiet=not self.should_echo_commands())
                            #log.info(desired_commit)
                            #log.info(cur_commit)
                            if cur_commit == desired_commit:
                                log.info('Commits are synced, skipping.')
                                continue

                repo = GitRepository(path, origin_uri=repoconf['url'], submodule=True)
                if repo.CheckForUpdates(branch=branch, quiet=False):
                    if os.path.isdir(path):
                        os_utils.cmd(['git', 'submodule', 'sync', '--', pathspec], critical=True, echo=self.should_echo_commands(), show_output=True)
                    os_utils.cmd(['git', 'submodule', 'update', '--init', '--recursive', pathspec], critical=True, echo=self.should_echo_commands(), show_output=True)
