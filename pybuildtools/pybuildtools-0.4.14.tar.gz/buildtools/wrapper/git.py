'''
Git Wrapper

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
import os, sys, glob, subprocess

from buildtools.bt_logging import log
from buildtools.os_utils import cmd_output, Chdir, cmd, _args2str
from logging import critical

class Git(object):
    @classmethod
    def GetCommit(cls, ref='HEAD', short=True, quiet=True):
        try:
            addtl_flags = []
            if short: addtl_flags.append('--short')
            stdout, stderr = cmd_output(['git', 'rev-parse'] + addtl_flags + [ref], echo=not quiet, critical=True)
            return (stdout + stderr).decode('utf-8').strip()
            # rev = subprocess.Popen(['git', 'rev-parse'] + addtl_flags + [ref], stdout=subprocess.PIPE).communicate()[0][:-1]
            # if rev:
            #    return rev.decode('utf-8')
        except Exception as e:
            print(e)
            pass
        return '[UNKNOWN]'
    @classmethod
    def LSRemote(cls, remote=None, ref=None, quiet=True):
        args = []
        if remote:
            args.append(remote)
        if ref:
            args.append(ref)
        try:
            ret = cmd_output(['git', 'ls-remote'] + args, echo=not quiet, critical=True)
            if not ret:
                return None
            #print(repr(ret))
            stderr, stdout = ret
            o = {}
            for line in (stdout + stderr).decode('utf-8').split('\n'):
                line = line.strip()
                if not quiet:
                    print(line)
                if line == '':
                    continue
                line_chunks = line.split()
                if len(line_chunks) == 2:
                    hashid, ref = line_chunks
                    o[ref] = hashid
            return o
        except Exception as e:
            print(e)
            pass
        return None

    @classmethod
    def OutputIsFatal(cls, output):
        for line in output.splitlines():
            if line.startswith('fatal:'):
                log.critical(output)
                return True
        return False

    @classmethod
    def GetBranch(cls, quiet=True):
        try:
            cmd = ["git", "symbolic-ref", "--short", 'HEAD']
            #stderr, stdout = cmd_output(["git", "rev-parse", "--abbrev-ref", 'HEAD', '--'], echo=not quiet, critical=True)
            stderr, stdout = cmd_output(cmd, echo=not quiet, critical=True)
            o = (stderr + stdout).decode('utf-8').strip()
            if cls.OutputIsFatal(o):
                log.error(_args2str(cmd))
                return None
            return o.strip()
        except Exception as e:
            print(e)
            pass
        return None

    @classmethod
    def IsDirty(cls, quiet=True):
        try:
            # branch = subprocess.Popen(['git', 'ls-files', '-m', '-o', '-d', '--exclude-standard'], stdout=subprocess.PIPE).communicate()[0][:-1]
            # if branch:
            stderr, stdout = cmd_output(['git', 'ls-files', '-m', '-o', '-d', '--exclude-standard'], echo=not quiet, critical=True)
            for line in (stderr + stdout).decode('utf-8').split('\n'):
                line = line.strip()
                if line != '': return True
            return False
        except Exception as e:
            print(e)
            pass
        return None
