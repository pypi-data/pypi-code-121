'''
Base BuildTarget

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
import hashlib
from inspect import trace
import os
from traceback import StackSummary
import traceback
import typing
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

yaml = YAML(typ='safe', pure=True)

from buildtools import os_utils, utils
from buildtools.bt_logging import IndentLogger, log
from buildtools.maestro.utils import callLambda

if typing.TYPE_CHECKING:
    from . import BuildMaestro

class BuildFailedError(Exception):
    pass

class BuildTarget(object):
    BT_TYPE: str = '-'
    BT_COLOR: str = 'cyan'
    BT_LABEL: str = 'FIXME'

    #                YYYYMMDDhhmm
    CACHE_VER: int = 202205141832

    CHECK_MTIMES: bool = True
    CHECK_HASHES: bool = True

    def __init__(self, targets: Union[List[str], str]=[], files: List[str]=[], dependencies: List[str]=[], provides: List[str]=[], name: str='') -> None:
        self.id: int = 0
        self.instantiated_at: StackSummary = traceback.extract_stack() # Instantiation
        self.added_at: Optional[StackSummary] = None
        self._all_provides: List[str] = targets if isinstance(targets, list) else [targets]+provides
        self.name: str = ''
        try:
            self.name = os.path.relpath(self._all_provides[0], os.getcwd()) if name == '' else name
        except ValueError:
            self.name = self._all_provides[0] if name == '' else name
        self.files: List[str] = files
        self.dependencies: List[str] = dependencies

        self.maestro: Optional['BuildMaestro'] = None

        #: Print executed commands to console.
        self.show_commands: bool = False

        #: This target was rebuilt. (Files changed)
        self.dirty: bool = False

        self._lambdas_called: bool=False

        # Cache stuff
        self.lastConfigHash: str = ''
        self.lastTargetHash: str = ''
        self.lastFileTimes: Dict[str, float]={}
        self.lastFileHashes: Dict[str, str]={}
        self.lastConfig: Dict[str, Any]={}

    def try_build(self) -> None:
        self.files = callLambda(self.files)
        self.readCache()
        if self.is_stale():
            with self.logStart():
                self.build()
                self.writeCache()

    def clean(self) -> None:
        with log.info('Cleaning %s...', self.name):
            for filename in self.provides():
                self.removeFile(filename)

    def removeFile(self, filename) -> None:
        if os.path.isfile(filename):
            log.info('<red>RM    </red> %s',filename)
            os.remove(filename)

    def _set_failed(self) -> None:
        self.built = False
        log.warn('Cleaning build artifacts due to failure...')
        self.clean()

    def failed(self, msg: str = 'Build failed') -> None:
        raise BuildFailedError(msg)

    def get_config(self) -> Dict[str, Any]:
        return {}

    def should_echo_commands(self) -> bool:
        return self.maestro.show_commands or self.show_commands

    def is_stale(self) -> bool:
        if self.lastTargetHash == '':
            self.readCache()
        if self.getTargetHash() != self.lastTargetHash:
            with log.debug('[is stale] Target hash changed'):
                log.debug('self.getTargetHash(): %r', self.getTargetHash())
                log.debug('self.lastTargetHash:  %r', self.lastTargetHash)
            return True
        if self.getConfigHash() != self.lastConfigHash:
            log.debug('[is stale] Config hash changed')
            return True
        if self.haveFilesChanged(): #self.checkMTimes(self.files+self.dependencies, self.provides(), config=self.get_config())
            return True
        return False

    def build(self) -> None:
        pass

    def provides(self) -> List[str]:
        return list(set(self._all_provides))

    def get_label(self) -> str:
        return self.BT_LABEL or self.BT_TYPE.upper() or type(self).__class__.__name__

    def get_displayed_name(self) -> str:
        return self.name

    def verboseLogEntry(self, color) -> str:
        if self.maestro.colors:
            return f'Running target <{color}>{self.name}</{color}>...'
        else:
            return f'Running target {self.name}...'

    def standardLogEntry(self, color) -> str:
        padded_label = self.get_label().ljust(self.maestro.get_max_label_length())
        if self.maestro.colors:
            return f'<{color}>{padded_label}</{color}> {self.get_displayed_name()}'
        else:
            return f'{padded_label} {self.get_displayed_name()}'

    def logStart(self) -> IndentLogger:
        color = self.BT_COLOR or 'cyan'
        pct = round((len(self.maestro.targetsCompleted)/len(self.maestro.targets))*100)
        msg = ''
        if self.maestro.verbose:
            msg = self.verboseLogEntry(color)
        else:
            msg = self.standardLogEntry(color)
        return log.info(f'[{str(pct).rjust(3)}%] {msg}')

    def serialize(self) -> Dict[str, Any]:
        return {
            'type': self.BT_TYPE,
            'name': self.name,
            'files': callLambda(self.files),
            'dependencies': self.dependencies,
            'provides': self.provides(),
            'show_commands': self.show_commands
        }

    def getFilesToCompare(self) -> List[str]:
        return [os.path.abspath(__file__)]+callLambda(self.files)+self.provides()+self.dependencies

    def serialize_file_times(self) -> Dict[str, float]:
        file_mtimes={}
        for filename in self.getFilesToCompare():
            if os.path.isfile(filename):
                file_mtimes[os.path.abspath(filename)]=os.path.getmtime(filename)
        return file_mtimes

    def serialize_file_hashes(self) -> Dict[str, str]:
        file_hashes={}
        for filename in self.getFilesToCompare():
            if os.path.isfile(filename):
                file_hashes[os.path.abspath(filename)]=utils.hashfile(filename, hashlib.md5())
        return file_hashes

    def genVirtualTarget(self, vid: Optional[str] = None) -> str:
        if vid is None:
            vid = self.getConfigHash()
        return os.path.join(self.maestro.builddir, 'tmp', 'virtual-targets', vid)

    def deserialize(self, data: Dict[str, Any]) -> None:
        self.target = data['target']
        self.files = data.get('files', [])
        self.dependencies = data.get('dependencies', [])
        self._all_provides = data.get('provides', [])

    def getCacheFile(self) -> str:
        filename = hashlib.md5(self.name.encode('utf-8')).hexdigest()+'.yml'
        return os.path.join(self.maestro.builddir, 'cache', filename)

    def getConfigHash(self) -> str:
        s = StringIO()
        yaml.dump(self.get_config(), s)
        return hashlib.md5(s.getvalue().encode('utf-8')).hexdigest()

    def getTargetHash(self) -> str:
        return hashlib.md5(';'.join(self.provides()).encode('utf-8')).hexdigest()

    def writeCache(self) -> None:
        configHash = self.getConfigHash()
        targetHash = self.getTargetHash()
        os_utils.ensureDirExists(os.path.dirname(self.getCacheFile()))
        with open(self.getCacheFile(), 'w') as f:
            yaml.dump_all([self.CACHE_VER, configHash, targetHash, self.serialize_file_times(), self.serialize_file_hashes(), self.get_config()], f)

    def readCache(self) -> None:
        self.lastConfigHash=''
        self.lastTargetHash=''
        self.lastFileTimes={}
        self.lastFileHashes={}
        self.lastConfig={}
        if os.path.isfile(self.getCacheFile()):
            try:
                with open(self.getCacheFile(), 'r') as f:
                    cachedata = list(yaml.load_all(f))
                    if len(cachedata)==6 and cachedata[0] == self.CACHE_VER:
                        _, _CH, _TH, _LFT, _LFH, _CFG = cachedata
                        self.lastConfigHash=_CH
                        self.lastTargetHash=_TH
                        self.lastFileTimes=_LFT
                        self.lastFileHashes=_LFH
                        self.lastConfig=_CFG
            except Exception as e:
                log.exception(e)
                pass

    def haveFilesChanged(self) -> bool:
        if self.lastTargetHash == '':
            self.readCache()
        curFileTimes = self.serialize_file_times()
        if self.CHECK_MTIMES:
            for filename, mtime in self.lastFileTimes.items():
                filename=os.path.abspath(filename)
                if filename not in curFileTimes.keys():
                    log.debug('File %s is currently missing.', filename)
                    return True
                if abs(curFileTimes[filename] - mtime) > 0.1:
                    log.debug('File %s has a changed mtime. abs(%d - %d) > 1', filename, curFileTimes[filename], mtime)
                    return True
        if self.CHECK_HASHES:
            curFileHashes = self.serialize_file_hashes()
            for filename, hashed in self.lastFileHashes.items():
                filename=os.path.abspath(filename)
                if filename not in curFileHashes.keys():
                    log.debug('File %s is currently missing.', filename)
                    return True
                if curFileHashes[filename] != hashed:
                    log.debug('File %s has a changed hash. (%s != %s)', filename, curFileHashes[filename], hashed)
                    return True
        for filename, mtime in curFileTimes.items():
            filename=os.path.abspath(filename)
            if filename in self.maestro.targetsDirty:
                log.debug('File %s was dirtied by another BuildTarget.', filename)
                return True

            if filename not in self.lastFileTimes.keys():
                log.debug('File %s is new.', filename)
                return True
        return False

    def getChangedFiles(self) -> Set[str]:
        '''
        Slower than haveFilesChanged.
        '''
        if self.lastTargetHash == '':
            self.readCache()
        o = set()
        if self.CHECK_MTIMES:
            curFileTimes = self.serialize_file_times()
            for filename, mtime in self.lastFileTimes.items():
                filename=os.path.abspath(filename)
                if filename not in curFileTimes.keys():
                    log.debug('File %s is currently missing.', filename)
                    o.add(filename)
                if curFileTimes[filename] != mtime:
                    log.debug('File %s has a changed mtime.', filename)
                    o.add(filename)
        if self.CHECK_HASHES:
            curFileHashes = self.serialize_file_hashes()
            for filename, hashed in self.lastFileHashes.items():
                filename=os.path.abspath(filename)
                if filename not in curFileHashes.keys():
                    log.debug('File %s is currently missing.', filename)
                    o.add(filename)
                if curFileHashes[filename] != hashed:
                    log.debug('File %s has a changed hash.', filename)
                    o.add(filename)
        for filename, mtime in curFileTimes.items():
            filename=os.path.abspath(filename)
            if filename not in self.lastFileTimes.keys():
                log.debug('File %s is new.', filename)
                o.add(filename)
        return o


    def checkMTimes(self, inputs: List[Union[str, Callable[[], str]]], targets: List[str], config: Optional[Dict[str, Any]]=None) -> bool:
        inputs=callLambda(inputs)
        for target in targets:
            if not os.path.isfile(target):
                log.debug('%s does not exist.', target)
                return True

        if config is not None:
            s = StringIO()
            yaml.dump(config, s)
            configHash = hashlib.md5(s.getvalue().encode('utf-8')).hexdigest()
            targetHash = hashlib.md5(';'.join(targets).encode('utf-8')).hexdigest()

            def writeHash():
                with open(configcachefile, 'w') as f:
                    f.write(configHash)
            os_utils.ensureDirExists('.build')
            configcachefile = os.path.join('.build', targetHash)
            if not os.path.isfile(configcachefile):
                writeHash()
                log.debug('%s: Target cache doesn\'t exist.', self.name)
                return True
            oldConfigHash = ''
            with open(configcachefile, 'r') as f:
                oldConfigHash = f.readline().strip()
            if(oldConfigHash != configHash):
                writeHash()
                log.debug('%s: Target config changed.', self.name)
                return True
        target_mtime = 0.  # must be higher
        newest_target = None
        inputs_mtime = 0.
        newest_input = None
        for infilename in targets:
            infilename = callLambda(infilename)
            if os.path.isfile(infilename):
                c_mtime = os.path.getmtime(infilename)
                # log.info("%d",input_mtime-target_mtime)
                if c_mtime > target_mtime:
                    target_mtime = c_mtime
                    newest_target = infilename
        for _i in inputs:
            infilename = callLambda(_i)
            if os.path.isfile(infilename):
                c_mtime = os.path.getmtime(infilename)
                # log.info("%d",input_mtime-target_mtime)
                if c_mtime > inputs_mtime:
                    inputs_mtime = c_mtime
                    newest_input = infilename
        if newest_input is None or target_mtime <= inputs_mtime:
            log.debug("%s is newer than %s by %ds!", newest_input, newest_target, inputs_mtime - target_mtime)
            return True
        else:
            log.debug("%s is older than %s by %ds!", newest_input, newest_target, target_mtime - inputs_mtime)

        return False

    def canBuild(self, maestro: 'BuildMaestro', keys: List[str]) -> bool:
        #self.files = list(callLambda(self.files))
        #for dep in list(set(self.dependencies + self.files)):
        if not self._lambdas_called:
            for reqfile in callLambda(self.files):
                if reqfile in keys and reqfile not in self.dependencies:
                    self.dependencies.append(reqfile)
        for dep in list(set(self.dependencies)):
            if dep not in maestro.targetsCompleted:
                log.debug('%s: Waiting on %s.',self.name,dep)
                return False
        log.debug('%s: CAN BUILD!',self.name)
        return True

    def touch(self, filename: str) -> None:
        p = Path(filename)
        p.parent.mkdir(exist_ok=True)
        p.touch(exist_ok=True)

    def _dumpStacks(self) -> None:
        with log.info('Created:'):
            [log.info(sl) for sl in traceback.format_list(self.instantiated_at)]
        if self.added_at:
            with log.info('Added:'):
                [log.info(sl) for sl in traceback.format_list(self.added_at)]


class SingleBuildTarget(BuildTarget):
    def __init__(self, target: str, files: List[str] = [], dependencies: List[str] = [], provides: List[str] = [], name: str = '') -> None:
        self.target=target
        super(SingleBuildTarget, self).__init__([target], files=files, dependencies=dependencies, provides=provides, name=name)
