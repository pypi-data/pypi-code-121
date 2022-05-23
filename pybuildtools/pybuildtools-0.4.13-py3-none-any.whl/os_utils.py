'''
OS Utilities.

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
import filecmp
import glob
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
import tqdm
import typing
import zipfile

from buildtools.bt_logging import log
from functools import reduce
from subprocess import CalledProcessError

from typing import List, Any, Union, Tuple
import psutil

buildtools_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
scripts_dir = os.path.join(buildtools_dir, 'scripts')

REG_EXCESSIVE_WHITESPACE = re.compile(r'\s{2,}')
PLATFORM = platform.system()
PATH_7ZA: typing.Optional[os.PathLike] = None

def clock():
    if sys.platform == 'win32':
        return time.clock()
    else:
        return time.time()


def getElapsed(start):
    return '%d:%02d:%02d.%03d' % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [((clock() - start) * 1000,), 1000, 60, 60])


def secondsToStr(t: int) -> str:
    '''
    Take integer seconds, return formatted string.
    '''
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class BuildEnv(object):

    def __init__(self, initial=None):
        if initial is not None:
            self.env = initial
        else:
            self.env = os.environ
        self.keycapmap = {k.upper(): k for k in self.env}
        self.noisy = True

    def getKey(self, key):
        okey = key
        key = key.upper()
        if key not in self.keycapmap:
            self.keycapmap[key] = okey
        return self.keycapmap[key]

    def set(self, key, val, noisy=None):
        if noisy is None:
            noisy = self.noisy
        key = self.getKey(key)
        if noisy:
            log.info('Environment: {} = {}'.format(key, val))
        self.env[key] = val

    def get(self, key, default=None):
        key = self.getKey(key)
        if key not in self.env:
            return default
        return self.env[key]

    def merge(self, newvars):
        self.env = dict(self.env, **newvars)

    def prependTo(self, key, value, delim=None, noisy=None):
        if delim is None:
            delim = os.pathsep
        if noisy is None:
            noisy = self.noisy
        key = self.getKey(key)
        if noisy:
            log.info('Environment: {1} prepended to {0}'.format(key, value))
        self.env[key] = delim.join([value] + self.env.get(key, '').split(delim))

    def appendTo(self, key, value, delim=';', noisy=None):
        if noisy is None:
            noisy = self.noisy
        key = self.getKey(key)
        if noisy:
            log.info('Environment: {1} appended to {0}'.format(key, value))
        self.env[key] = delim.join(self.env.get(key, '').split(delim) + [value])

    def clone(self):
        return BuildEnv(self.env.copy())

    def dumpToLog(self, keys=None):
        if keys is None:
            keys = self.env.keys()
        self.dump(self.env, keys)

    def which(self, program, skip_paths=[]):
        fpath, _ = os.path.split(program)
        if fpath:
            if is_executable(program):
                return program
        else:
            for path in self.get("PATH").split(os.pathsep):
                path = path.strip('"')
                is_skipped_path = False
                for badpath in skip_paths:
                    if badpath.lower() in path.lower():
                        is_skipped_path = True
                        break
                if is_skipped_path:
                    continue
                exe_file = os.path.join(path, program)
                if sys.platform == 'win32':
                    for ext in self.get("PATHEXT").split(os.pathsep):
                        proposed_file = exe_file + ""
                        if not proposed_file.endswith(ext):
                            proposed_file += ext
                            if os.path.isfile(proposed_file):
                                exe_file = proposed_file
                                #print('{}: {}'.format(exe_file,ext))
                                break
                if is_executable(exe_file):
                    return exe_file
        return None

    def assertWhich(self, program, fail_raise=False, skip_paths=[]):
        fullpath = self.which(program, skip_paths)
        with log.info('Checking if %s exists...', program):
            if fullpath is None:
                errmsg = '{executable} is not in PATH!'.format(executable=program)
                raise RuntimeError(errmsg)
            else:
                log.info('Found: %s', fullpath)
        return fullpath

    def removeDuplicatedEntries(self, key, noisy=None, delim=os.pathsep):
        if noisy is None:
            noisy = self.noisy
        newlist = []
        key = self.getKey(key)
        for entry in self.env[key].split(delim):
            entry = entry.strip('"')
            if entry in newlist:
                if noisy:
                    log.info('Build env: Removing %r from %s: duplicated entry.', entry, key)
                continue
            newlist += [entry]
        self.env[key] = delim.join(newlist)

    @classmethod
    def dump(cls, env, keys=None):
        for key, value in sorted(env.items()):
            if keys is not None and key not in keys:
                continue
            log.info('+{0}="{1}"'.format(key, value))


def ensureDirExists(path, mode=0o777, noisy=False):
    if path != '' and not os.path.isdir(path):
        os.makedirs(path, mode)
        if noisy:
            log.info('Created %s.', path)


class DeferredLogEntry(object):

    def __init__(self, label):
        self.label = label

    def toStr(self, entryVars):
        return self.label.format(**entryVars)


class TimeExecution(object):

    def __init__(self, label):
        self.start_time = None
        self.vars = {}
        if isinstance(label, str):
            self.label = DeferredLogEntry('Completed in {elapsed}s - {label}')
            self.vars['label'] = label
        elif isinstance(label, DeferredLogEntry):
            self.label = label

    def __enter__(self):
        self.start_time = clock()
        return self

    def __exit__(self, typeName, value, traceback):
        self.vars['elapsed'] = secondsToStr(clock() - self.start_time)
        with log:
            log.info(self.label.toStr(self.vars))
        return False


class Chdir(object):

    def __init__(self, newdir, quiet=False):
        self.pwd = os.path.abspath(os.getcwd())
        self.chdir = newdir
        self.quiet = quiet

    def __enter__(self):
        try:
            if os.getcwd() != self.chdir:
                os.chdir(self.chdir)
                if not self.quiet:
                    log.info('cd ' + self.chdir)
        except Exception as e:
            log.critical('Failed to chdir to {}.'.format(self.chdir))
            log.exception(e)
            sys.exit(1)
        return self

    def __exit__(self, typeName, value, traceback):
        try:
            if os.getcwd() != self.pwd:
                os.chdir(self.pwd)
                if not self.quiet:
                    log.info('cd ' + self.pwd)
        except Exception as e:
            log.critical('Failed to chdir to {}.'.format(self.chdir))
            log.exception(e)
            sys.exit(1)
        return False


def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    return ENV.which(program)


def assertWhich(program, fail_raise=False):
    return ENV.assertWhich(program, fail_raise)


def _cmd_handle_env(env):
    if env is None:
        env = ENV.env
    if isinstance(env, BuildEnv):
        env = env.env
    # Fix a bug where env vars get some weird types.
    new_env = {}
    for k, v in env.items():
        k = str(k)
        v = str(v)
        new_env[k] = v
    return new_env


def _cmd_handle_args(command, globbify):
    # Shell-style globbin'.
    new_args = []  # command[0]]
    for arg in command:  # 1:
        arg = str(arg)
        if globbify:
            if '~' in arg:
                arg = os.path.expanduser(arg)
            if '*' in arg or '?' in arg:
                new_args += glob.glob(arg)
                continue

        new_args += [arg]
    return new_args


def find_process(pid):
    for proc in psutil.process_iter():
        try:
            if proc.pid == pid:
                if proc.status() == psutil.STATUS_ZOMBIE:
                    log.warn('Detected zombie process #%s, skipping.', proc.pid)
                    continue
                return proc
        except psutil.AccessDenied:
            continue
    return None


def check_output(*popenargs, timeout=None, acceptable_exit_codes=[0], **kwargs):
    '''
    Python 3.6 subprocess.check_output(), modded to accept more exit codes.
    '''
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')

    if 'input' in kwargs and kwargs['input'] is None:
        # Explicitly passing input=None was previously equivalent to passing an
        # empty string. That is maintained here for backwards compatibility.
        kwargs['input'] = '' if kwargs.get('universal_newlines', False) else b''
    return run(*popenargs, stdout=subprocess.PIPE, timeout=timeout, check=True, acceptable_exit_codes=acceptable_exit_codes, **kwargs).stdout


def check_call(*popenargs, acceptable_exit_codes=[0], **kwargs):
    """
    Python 3.6 subprocess.check_call(), modded to accept more exit codes.
    """
    retcode = subprocess.call(*popenargs, **kwargs)
    if retcode not in acceptable_exit_codes:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return 0


def run(*popenargs, input=None, timeout=None, check=False, acceptable_exit_codes=[0], **kwargs):
    '''
    Python 3.6 subprocess.run(), modded to accept more exit codes.
    '''
    with subprocess.Popen(*popenargs, **kwargs) as process:
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(process.args, timeout, output=stdout,  # pylint: disable=E1101
                                            stderr=stderr)
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
        if check and retcode not in acceptable_exit_codes:
            raise CalledProcessError(retcode, process.args,  # pylint: disable=E1101
                                     output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(process.args, retcode, stdout, stderr)  # pylint: disable=E1101


def cmd(command, echo=False, env=None, show_output=True, critical=False, globbify=True, acceptable_exit_codes=[0]):
    new_env = _cmd_handle_env(env)
    command = _cmd_handle_args(command, globbify)
    if echo:
        log.info('$ ' + _args2str(command))

    output = ''
    try:
        if show_output:
            code = subprocess.call(command, env=new_env, shell=False)
            #print(repr(code))
            success = code in acceptable_exit_codes
            if critical and not success:
                raise CalledProcessError(code, command)
            return success
        else:
            # Using our own customized check_output for acceptable_exit_codes.
            output = check_output(command, env=new_env, stderr=subprocess.STDOUT, acceptable_exit_codes=acceptable_exit_codes)
            return True
    except CalledProcessError as cpe:
        log.error(cpe.output)
        if critical:
            raise cpe
        log.error(cpe)
        return False
    except Exception as e:
        log.error(e)
        log.error(output)
        if critical:
            raise e
        log.error(e)
        return False

def cmd_output(command, echo=False, env=None, critical=False, globbify=True) -> Tuple[bytes, bytes]:
    '''
    :returns List[2]: (stdout,stderr)
    '''
    new_env = _cmd_handle_env(env)
    command = _cmd_handle_args(command, globbify)
    if echo:
        log.info('$ ' + _args2str(command))

    try:
        return subprocess.Popen(command, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    except Exception as e:
        log.error(repr(command))
        if critical:
            raise e
        log.error(e)
    return False

def cmd_out(command: Union[List[str], str], echo=False, env=None, critical=False, globbify=True, encoding: str='utf-8') -> str:
    '''
    :returns str: stderr and stdout, piped into one string and decoded as UTF-8.
    '''
    new_env = _cmd_handle_env(env)
    command = _cmd_handle_args(command, globbify)
    if echo:
        log.info('$ ' + _args2str(command))

    try:
        p = subprocess.Popen(command, env=new_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        return p.stdout.read().decode('utf-8')
    except Exception as e:
        log.error(repr(command))
        if critical:
            raise e
        log.error(e)
    return None


def cmd_daemonize(command, echo=False, env=None, critical=False, globbify=True):
    new_env = _cmd_handle_env(env)
    command = _cmd_handle_args(command, globbify)
    if echo:
        log.info('& ' + _args2str(command))

    try:
        if platform.system() == 'Windows':
            # HACK
            batch = os.tmpnam() + '.bat'
            with open(batch, 'w') as b:
                b.write(' '.join(command))
            os.startfile(batch)
        else:
            subprocess.Popen(command, env=new_env)
        return True
    except Exception as e:
        log.error(repr(command))
        if critical:
            raise e
        log.error(e)
        return False


def old_copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.path.getmtime(src) - os.path.getmtime(dst) > 1:
                shutil.copy2(s, d)


def canCopy(src, dest, **op_args):
    '''
    :param ignore_mtime bool:
        Ignore file modification timestamps.
    :param ignore_filecmp bool:
        Disable byte-to-byte comparison AND os.stat checks.
    :param ignore_bytecmp bool:
        Do not check each file byte-for-byte, perform shallow os.stat checks.
    '''
    if not os.path.isfile(dest):
        return True
    if not op_args.get('ignore_mtime', False):
        if os.path.getmtime(src) - os.path.getmtime(dest) > 1.0:
            return True
    if not op_args.get('ignore_filecmp', False):
        if not filecmp.cmp(src, dest, op_args.get('ignore_bytecmp', False)):
            return True
    return False


def single_copy(fromfile: str, newroot: str, **op_args):
    '''
    :param as_file bool:
        Copy to new name rather than to new directory. False by default.
    :param verbose bool:
        Log copying action.
    :param ignore_mtime bool:
        Ignore file modification timestamps.
    :param ignore_filecmp bool:
        Disable byte-to-byte comparison AND os.stat checks.
    :param ignore_bytecmp bool:
        Do not check each file byte-for-byte, perform shallow os.stat checks.
    '''
    newfile = os.path.join(newroot, os.path.basename(fromfile))
    if op_args.get('as_file', False) or '.' in newroot:
        newfile = newroot
    if canCopy(fromfile, newfile, **op_args):
        if op_args.get('verbose', False):
            log.info('Copying {} -> {}'.format(fromfile, newfile))
        shutil.copy2(fromfile, newfile)


def copytree(fromdir, todir, ignore=None, verbose=False, ignore_mtime=False, progress=False):
    if progress:
        count={'a':0}
        def incrementCount(a,b,**c):
            count['a']+=1
        optree(fromdir, todir, incrementCount, ignore,
               verbose=False, ignore_mtime=ignore_mtime)
        optree(fromdir, todir, single_copy, ignore,
               verbose=verbose, ignore_mtime=ignore_mtime, tqdm_total=count['a'],
               tqdm_desc='Copying...', progress=True)
    else:
        optree(fromdir, todir, single_copy, ignore,
                verbose=verbose, ignore_mtime=ignore_mtime)


def optree(fromdir, todir, op, ignore=None, **op_args):
    if ignore is None:
        ignore = []
    gen = []
    # print('ignore=' + repr(ignore))
    for root, _, files in os.walk(fromdir):
        path = root.split(os.sep)
        start = len(fromdir)
        if root[start:].startswith(os.sep):
            start += 1
        substructure = root[start:]
        assert not substructure.startswith(os.sep)
        newroot = os.path.join(todir, substructure)
        if any([(x + '/' in ignore) for x in path]):
            if op_args.get('verbose', False):
                log.info(u'Skipping {}'.format(substructure))
            continue
        #if not os.path.isdir(newroot):
        #    if op_args.get('verbose', False):
        #        log.info(u'mkdir {}'.format(newroot))
        #    os.makedirs(newroot)
        for filename in files:
            fromfile = os.path.join(root, filename)
            _, ext = os.path.splitext(os.path.basename(fromfile))
            if ext in ignore:
                if op_args.get('verbose', False):
                    log.info(u'Skipping {} ({})'.format(fromfile, ext))
                continue
            gen += [(fromfile, newroot)]
    #print(len(gen))
    prog=None
    if op_args.get('progress', False):
        prog = tqdm.tqdm(gen,
            desc=op_args.get('tqdm_desc', 'Operating...'),
            total=op_args.get('tqdm_total', 0),
            leave=True,
            ascii=sys.platform.startswith('win'), # *shakes fist*
            unit='file')

    for fromfile, newroot in gen:
        if not os.path.isdir(newroot):
            if op_args.get('verbose', False):
                log.info(u'mkdir {}'.format(newroot))
            os.makedirs(newroot)
        op(fromfile, newroot, **op_args)
        if prog:
            prog.update(1)
    if prog:
        prog.close()


def safe_rmtree(dirpath):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def RemoveExcessiveWhitespace(text):
    return REG_EXCESSIVE_WHITESPACE.sub('', text)


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def standardize_path(path):
    pathchunks = path.split('/')
    path = pathchunks[0]
    for chunk in pathchunks[1:]:
        path = os.path.join(path, chunk)
    return path


REG_DRIVELETTER = re.compile(r'^([A-Z]):\\')


def cygpath(inpath):
    chunks = inpath.split('\\')
    chunks[0] = chunks[0].lower()[:-1]
    return '/cygdrive/' + '/'.join(chunks)

'''
def _autoescape(string):
    if ' ' in string:
        return '"' + string + '"'
    else:
        return string
'''

def _args2str(cmdlist):
    #return ' '.join([_autoescape(x) for x in cmdlist])
    return ' '.join([shlex.quote(x) for x in cmdlist])

def decompressFile(archive: os.PathLike, to: os.PathLike='.', env=None, path7za: os.PathLike = '7za'):
    '''
    Decompresses the file to the current working directory.

    Uses 7za for .7z and .rar files. (p7zip)
    '''
    
    archive = str(archive)
    to = str(to)
    path7za = str(path7za)

    if env is None:
        env = ENV
    #print('Trying to decompress ' + archive)
    lc = archive.lower()
    if lc.endswith('.tar.gz') or lc.endswith('.tgz'):
        with tarfile.open(archive, mode='r:gz') as arch:
            arch.extractall(to)
        return True
    elif lc.endswith('.bz2') or lc.endswith('.tbz'):
        with tarfile.open(archive, mode='r:bz2') as arch:
            arch.extractall(to)
        return True
    elif lc.endswith('.tar.xz'):
        with tarfile.open(archive, mode='r:xz') as arch:
            arch.extractall(to)
        return True
    elif lc.endswith('.tar.7z'):
        cmd([path7za, 'x', '-aoa', '-o'+to, '--', archive], echo=True, show_output=False, critical=True)
        with tarfile.open(archive[:-3], mode='r') as arch:
            arch.extractall(to)
        os.remove(archive[:-3])
        return True
    elif lc.endswith('.gz'):
        with tarfile.open(archive, mode='r:gz') as arch:
            arch.extractall(to)
    elif lc.endswith('.7z'):
        if PLATFORM == 'Windows':
            archive = cygpath(archive)
        cmd([path7za, 'x', '-aoa', '-o'+to, '--', archive], echo=True, show_output=False, critical=True)
    elif lc.endswith('.zip'):
        with zipfile.ZipFile(archive) as arch:
            arch.extractall(to)
        return True
    elif lc.endswith('.rar'):
        cmd([path7za, 'x', '-aoa', '-o'+to, '--', archive], echo=True, show_output=False, critical=True)
    else:
        log.critical('decompressFile(): Unknown file extension: %s', archive)
    return False


def del_empty_dirs(src_dir: str, quiet=False) -> int:
    '''
    Removes empty directories.

    :param src_dir:
        Root of directory tree to search for empty directories.
    :param quiet:
        Squelches log messages about removing empty directories.
    :returns:
        Count of removed directories.
    '''
    ndeleted = -1
    totalDel = 0
    while ndeleted != 0:
        ndeleted = 0
        # Listing the files
        for dirpath, dirnames, filenames in os.walk(src_dir, topdown=False):
            #print(dirpath, src_dir)
            if dirpath == src_dir:
                continue
            #print(dirpath, len(dirnames), len(filenames))
            if len(filenames) == 0 and len(dirnames) == 0:
                if not quiet:
                    log.info('Removing %s (empty)...', dirpath)
                os.rmdir(dirpath)
                ndeleted += 1
                totalDel += 1
    return totalDel


def get_file_list(root_dir: str, start: str = None, prefix: str='') -> list:
    '''
    Gets all files in a directory, including in subdirectories.
    :param root_dir:
        Root of directory tree to search for files.
    :param start:
        start parameter for `os.path.relpath()`.
    :param prefix:
        Prefix to append to each returned file path.
    :returns:
        List of files.
    '''
    output = []
    if start is None:
        start = root_dir
    for root, _, files in os.walk(root_dir):
        for filename in files:
            rpath = os.path.relpath(os.path.abspath(os.path.join(root, filename)), start)
            if prefix is not None:
                rpath = os.path.join(prefix, rpath)
            output += [rpath]
    return output

def detect_encoding(filename: str) -> typing.List:
    '''
    Attempts to detect encoding of filename using chardet.
    '''
    import chardet
    toread = min(32, os.path.getsize(filename))
    raw = b''
    with open(filename, 'rb') as f:
        raw = f.read(toread)
    encoding = 'utf-8-sig'
    bom = False
    if raw.startswith(codecs.BOM_UTF8):
        bom=True
        encoding = 'utf-8-sig'
    else:
        result = chardet.detect(raw)
        encoding = result['encoding']
        if encoding in ('utf-8', 'ascii'):
            encoding = 'utf-8-sig'
        if encoding in ('cp1252', 'Windows-1252'):
            encoding = 'cp1252'
    return encoding

def fix_encoding(filename, encoding='utf-8-sig'):
    #log.info('chardet guesses: {}'.format(encoding))
    if encoding in ('utf-8-sig', 'cp1252'):
        with codecs.open(filename, 'r', encoding=encoding) as inf:
            with codecs.open(filename + '.utf8', 'w', encoding='utf-8-sig') as outf:
                for line in ftfy.fix_file(inf, fix_entities=False, fix_latin_ligatures=False, fix_character_width=False, uncurl_quotes=False):
                    outf.write(line)
        # This is here because Windows 10 was locking files randomly.
        attempt=0
        while attempt<5:
            attempt += 1
            try:
                if os.path.isfile(filename):
                    os.remove(filename)
                break
            except PermissionError:
                log.error("[%d/%d] Failed to delete %s, trying again in 1s.", attempt,5,filename)
                time.sleep(0.5)
        shutil.move(filename + '.utf8', filename)
    return encoding

def is_windows():
    return platform.system() == 'Windows'

def is_linux():
    return platform.system() == 'Linux'

#def is_osx():
# Ha Ha fuck macs.

ENV = BuildEnv()

# Platform-specific extensions
if platform.system() == 'Windows':
    import buildtools._os_utils_win32
    buildtools._os_utils_win32.cmd_output = cmd_output
    buildtools._os_utils_win32.ENV = ENV
    from buildtools._os_utils_win32 import WindowsEnv, getVSVars
else:
    import buildtools._os_utils_linux
    buildtools._os_utils_linux.cmd_output = cmd_output
    buildtools._os_utils_linux.ENV = ENV
    from buildtools._os_utils_linux import GetDpkgShlibs, InstallDpkgPackages, DpkgSearchFiles
