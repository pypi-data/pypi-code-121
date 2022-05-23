'''
Maestro is my crappy, synchronous, yet extensible build system

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
import logging
import os
import re
import sys
import shutil
import argparse
import traceback

from buildtools import os_utils
from buildtools.bt_logging import log
from buildtools.maestro.base_target import BuildTarget
from buildtools.maestro.utils import (SerializableFileLambda,
                                      SerializableLambda)

from ruamel.yaml import YAML
from typing import Dict, List

yaml = YAML(typ='safe', pure=True)

yaml.register_class(SerializableLambda)
yaml.register_class(SerializableFileLambda)

class TarjanGraphVertex(object):
    def __init__(self, ID: int, refs: List[int]):
        self.id=ID
        self.refs = refs
        self.disc = -1
        self.low = -1
        self.stackMember = False


class TarjanGraph(object):
    def __init__(self):
        self.cur_id = 0 # Used for populating the graph.
        #self.graph = defaultdict(list)
        self.vertices = {}
        self.time = 0
        self.cycles=[]

    def add_edge(self, ID: int, refs: List[int]):
        self.vertices[ID] = TarjanGraphVertex(ID, refs)
        #for ref in refs:
        #    self.graph[ID].append(ref)

    def _sccutil(self, vertex, stack):
        vertex.disc = self.time
        vertex.low = self.time
        self.time+=1
        stack.append(vertex.id)
        vertex.stackMember=True

        for vID in vertex.refs:
            other_vertex = self.vertices[vID]
            if other_vertex.disc == -1:
                self._sccutil(other_vertex, stack)
                vertex.low=min(vertex.low,other_vertex.low)
            else:
                vertex.low=min(vertex.low,other_vertex.disc)
        w=-1
        if vertex.low == vertex.disc:
            cycle=[]
            while w!=vertex.id:
                w = stack.pop()
                cycle += [w]
                self.vertices[w].stackMember=False
            self.cycles += [cycle]

    def SCC(self):
        stack=[]
        for vertex in self.vertices.values():
            if vertex.disc == -1:
                self._sccutil(vertex, stack)

class BuildMaestro:
    ALL_TYPES = {}

    def __init__(self, hidden_build_dir='.build'):
        self.alltargets: List[BuildTarget] = []
        self.targets: List[str] = []
        self.targetsCompleted: List[str] = []
        self.targetsProvidedBy: Dict[str, BuildTarget] = {}

        self.verbose: bool = False
        self.colors: bool = False
        self.show_commands: bool = False

        self.builddir: str = hidden_build_dir
        self.all_targets_file: str = os.path.join(self.builddir, 'all_targets.yml')

        # This will get Maestro to delete the listed directories, if they are present during --clean.
        self.other_dirs_to_clean=[]

        self.args: argparse.Namespace = None

    def add(self, bt: BuildTarget) -> BuildTarget:
        bt.added_at = traceback.extract_stack()
        bt.id = len(self.alltargets)
        self.alltargets.append(bt)
        for t in bt.provides():
            if t in self.targets:
                log.warn(f'Target {t} already exists.')
                old = self.targetsProvidedBy[t]
                with log.warn('Old:'):
                    old._dumpStacks()
                with log.warn('New:'):
                    bt._dumpStacks()
            self.targetsProvidedBy[t] = bt
            self.targets.append(t)
        return bt

    def generateVirtualTarget(self, id: str) -> str:
        '''
        Usage:
        
        bm.add(CopyFilesTarget(target=bm.generateVirtualTarget('a'),...))
        '''
        return os.path.join(self.builddir, '.targets', id)

    def build_argparser(self):
        argp = argparse.ArgumentParser()
        argp.add_argument('--clean', action='store_true', default=False, help='Cleans everything.')
        argp.add_argument('--no-colors', action='store_true', default=False, help='Disables colors.')
        argp.add_argument('--rebuild', action='store_true', default=False, help='Clean rebuild of project.')
        argp.add_argument('--show-commands', action='store_true', default=False, help='Echoes the line used to execute commands. (echo=True in os_utils.cmd())')
        argp.add_argument('--verbose', action='store_true', default=False, help='Show hidden buildsteps.')
        return argp

    def parse_args(self, argp=None, args=None):
        if argp is None:
            argp = self.build_argparser()
        return argp.parse_args(args)

    def as_app(self, argp=None, args=None):
        self.args = self.parse_args(argp, args)
        if self.args.verbose:
            log.log.setLevel(logging.DEBUG)
            self.verbose = True

        self.show_commands = self.args.show_commands
        self.colors = not self.args.no_colors

        if self.colors:
            log.enableANSIColors()

        if self.args.rebuild or self.args.clean:
            self.clean()
        if self.args.clean:
            return
        self.run()

    def clean(self):
        older_files = set()
        if os.path.isfile(self.all_targets_file):
            with open(self.all_targets_file, 'r', encoding='utf-8') as f:
                try:
                    older_files = set(sorted(yaml.load(f)))
                except:
                    older_files = []
        for bt in self.alltargets:
            bt.maestro = self
            bt.clean()
        for xtradir in self.other_dirs_to_clean:
            if os.path.isdir(xtradir):
                if self.colors:
                    log.info('<red>RMTREE</red> %s <red>(other_dirs_to_clean)</red>', xtradir)
                else:
                    log.info('RMTREE %s (other_dirs_to_clean)', xtradir)
                shutil.rmtree(xtradir, ignore_errors=True)
        if os.path.isdir(self.builddir):
            if self.colors:
                log.info('<red>RMTREE</red> %s <red>(build system stuff)</red>', self.builddir)
            else:
                log.info('RMTREE %s (build system stuff)', self.builddir)
            shutil.rmtree(self.builddir, ignore_errors=True)
        with log.info('Cleaning up old unclaimed files...'):
            for targetfile in older_files:
                targetfile = os.path.normpath(targetfile)
                if os.path.isfile(targetfile):
                    if self.colors:
                        log.info('<red>RM</red> %s', targetfile)
                    else:
                        log.info('RM %s', targetfile)
                    os.remove(targetfile)

    @staticmethod
    def RecognizeType(cls):
        BuildMaestro.ALL_TYPES[cls.BT_TYPE] = cls

    def saveRules(self, filename):
        serialized = {}
        for rule in self.alltargets:
            serialized[rule.name] = rule.serialize()
        with codecs.open(filename + '.yml', 'w', encoding='utf-8') as f:
            yaml.indent()
            yaml.dump(serialized, f)
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            for tKey in sorted(serialized.keys()):
                target = dict(serialized[tKey])
                f.write(u'[{} {}]: {}\n'.format(target['type'], tKey, ', '.join(target.get('dependencies', []))))
                del target['dependencies']
                for provided in target.get('provides', []):
                    if provided != tKey:
                        f.write(u'< {}\n'.format(provided))
                for depend in target.get('files', []):
                    f.write(u'> {}\n'.format(depend))
                del target['files']
                del target['type']
                if len(target.keys()) > 0:
                    yaml.indent()
                    yaml.dump(target, f)
                f.write(u'\n')

    # def loadRules(self, filename):
    #     REGEX_RULEHEADER = re.compile('\[([A-Za-z0-9]+) ([^:]+)\]:(.*)$')
    #     self.targets = []
    #     self.alltargets = []
    #     with codecs.open(filename, 'r') as f:
    #         context = {}
    #         yamlbuf = ''
    #         ruleKey = ''
    #         for oline in f:
    #             s_line = oline.strip()
    #             if s_line.startswith('#') or s_line == '':
    #                 continue
    #             line = oline.rstrip()
    #             m = REGEX_RULEHEADER.match(line)
    #             if m is not None:
    #                 if len(context.keys()) > 0:
    #                     self.addFromRules(context, yamlbuf)
    #                     context = None
    #                     yamlbuf = ''
    #                     ruleKey = ''
    #                 typeID, ruleKey, depends = m.group(1, 2, 3)
    #                 context = {
    #                     'type': typeID,
    #                     'target': ruleKey,
    #                     'dependencies': [x.strip() for x in depends.split(',') if x != ''],
    #                     'files': [],
    #                     'provides': []
    #                 }
    #             elif line.startswith('>') and context is not None:
    #                 context['files'].append(line[1:].strip())
    #             elif line.startswith('<') and context is not None:
    #                 context['provides'].append(line[1:].strip())
    #             else:
    #                 yamlbuf += oline
    #         if context is not None:
    #             self.addFromRules(context, yamlbuf)
    #     log.info('Loaded %d rules from %s', len(self.alltargets), filename)

    # def addFromRules(self, context, yamlbuf):
    #     # print(repr(yamlbuf))
    #     if yamlbuf.strip() != '':
    #         yml = yaml.full_load(yamlbuf)
    #         for k, v in yml.items():
    #             context[k] = v
    #     cls = self.ALL_TYPES[context['type']]
    #     bt = cls()
    #     bt.deserialize(context)
    #     self.add(bt)

    def get_max_label_length(self) -> int:
        if len(self.alltargets):
            return max([len(bt.get_label()) for bt in self.alltargets])
        return 0

    def checkForCycles(self):
        with log.info('Checking for dependency cycles...'):
            # Using Tarjan's Strongly Connected Cycles algorithm
            tg = TarjanGraph()

            # First, I need to convert all BuildTargets to TarjanGraphVertexes.
            for bt in self.alltargets:
                refs = []
                for depend in bt.dependencies:
                    if not isinstance(depend, str):
                        log.critical('Build target %s has invalid dependency %s.',bt.name,depend)
                        sys.exit(1)
                    providers=[]
                    for obt in self.alltargets:
                        if depend in obt.provides():
                            #log.info('%s provides %s, which %s needs', obt.name, depend, bt.name)
                            providers += [obt]
                    if len(providers) > 1:
                        log.warning('Build target %s has %d providers for dependency %s: %r',bt.name,len(providers),depend,[x.name for x in providers])
                    elif len(providers) == 0:
                        log.critical('Build target %s has no providers for dependency %s: %r',bt.name,depend,[x.name for x in providers])
                        sys.exit(1)
                    refs.append(providers[-1].id)
                with log.debug('Dependency tree:'):
                    with log.debug('[%s] (%d,[%s])',bt.name,bt.id,', '.join([str(x) for x in refs])):
                        for refID in refs:
                            log.debug(self.alltargets[refID].name)
                tg.add_edge(bt.id, refs)

            # Run the algo
            tg.SCC()

            # Sort through the crap that falls out
            foundCycles=False
            for cycle in tg.cycles:
                if len(cycle) > 1:
                    log.critical('CYCLE FOUND: %r', ['#{} ({})'.format(self.alltargets[btid].id,self.alltargets[btid].name) for btid in cycle])
                    foundCycles=True
            return foundCycles

    def _write_targets(self):
        alltargets = set()
        for bt in self.alltargets:
            if bt.built:
                for targetfile in bt.provides():
                    alltargets.add(targetfile)
        os_utils.ensureDirExists(os.path.dirname(self.all_targets_file))
        with open(self.all_targets_file, 'w', encoding='utf-8') as f:
            yaml.dump(list(alltargets), f)

    def run(self, verbose=None):
        if verbose is not None:
            self.verbose = verbose

        new_targets=[]
        for t in self.targets:
            if t in new_targets:
                log.warn('Target %s added more than once.', t)
            else:
                new_targets.append(t)

        if self.checkForCycles():
            return
        keys = []
        alldeps=[]
        for target in self.alltargets:
            keys += target.provides()
            alldeps += target.dependencies
            target.built=False
        alldeps=list(set(alldeps))
        # Redundant
        #for target in self.alltargets:
        #    for reqfile in callLambda(target.files):
        #        if reqfile in keys and reqfile not in target.dependencies:
        #            target.dependencies.append(reqfile)
        loop = 0
        #progress = tqdm(total=len(self.targets), unit='target', desc='Building', leave=False)
        self.targetsCompleted = []
        self.targetsDirty = []
        while len(self.targets) > len(self.targetsCompleted) and loop < 100:
            loop += 1
            for bt in self.alltargets:
                bt.maestro = self
                if bt.canBuild(self, keys) and any([target not in self.targetsCompleted for target in bt.provides()]):
                    try:
                        bt.try_build()
                        # progress.update(1)
                        self.targetsCompleted += bt.provides()
                        if bt.dirty:
                            self.targetsDirty += bt.provides()
                    except Exception as e:
                        bt._set_failed()
                        self._write_targets()
                        log.critical('An exception occurred, build halted.')
                        log.exception(e)
                        return
                    except KeyboardInterrupt:
                        bt._set_failed()
                        self._write_targets()
                        log.critical('Cancelled via KeyboardInterrupt.')
                        return
                    bt.built=True
            log.debug('%d > %d, loop = %d',len(self.targets), len(self.targetsCompleted), loop)
        log.debug('%d > %d, loop = %d',len(self.targets), len(self.targetsCompleted), loop)
        # progress.close()
        self._write_targets()
        if loop >= 100:
            incompleteTargets=[t for t in self.targets if t not in self.targetsCompleted]
            if len(incompleteTargets)>0:
                with log.critical("Failed to resolve dependencies.  The following targets are left unresolved. Exiting."):
                    for t in incompleteTargets:
                        log.critical(t)
            orphanDeps=[t for t in alldeps if t not in self.targets]
            if len(orphanDeps)>0:
                with log.critical("Failed to resolve dependencies.  The following dependencies are orphaned. Exiting."):
                    for t in orphanDeps:
                        log.critical(t)
            #sys.exit(1)
        with log.info('Cleaning up...'):
            cachefiles = []
            for bt in self.alltargets:
                cachefiles.append(os.path.basename(bt.getCacheFile()))
            for filename in os.listdir(os.path.join(self.builddir, 'cache')):
                if filename not in cachefiles:
                    filename = os.path.join(self.builddir, 'cache', filename)
                    log.debug('<red>RM</red> %s', filename)
                    os.remove(filename)
