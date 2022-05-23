
'''
Twisted utilities

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
import sys
import threading
import time

# package Twisted
from twisted.internet import reactor
from twisted.internet.error import ProcessDone, ProcessTerminated
from twisted.internet.protocol import ProcessProtocol
from twisted.python.failure import Failure

import buildtools.os_utils as os_utils
from buildtools.bt_logging import log
from buildtools.utils import bytes2str


class _PipeReader(ProcessProtocol):

    def __init__(self, asc, process, stdout_callback, stderr_callback, exit_callback, linebreaks=None):
        self._asyncCommand = asc
        self._cb_stdout = stdout_callback
        self._cb_stderr = stderr_callback
        self._cb_exit = exit_callback
        self.process = process
        self.linebreaks = linebreaks or ('\r','\n','')

        self.buf = {
            'stdout': '',
            'stderr': ''
        }
        self.debug = False

    def _processData(self, bid: str, cb, data: bytes):
        if self.debug:
            log.info('%s %s: Received %d bytes', self._logPrefix(), bid, len(data))
        for b in bytes2str(data):
            if b not in self.linebreaks:
                self.buf[bid] += b
            else:
                self._dump_to_callback(bid, cb)

    def _dump_to_callback(self, bid, cb):
        buf = self.buf[bid].strip()
        if self.debug:
            log.info('%s buf = %r', self._logPrefix(), buf)
        if buf != '':
            cb(self._asyncCommand, buf)
        self.buf[bid] = ''

    def outReceived(self, data: bytes):
        self._processData('stdout', self._cb_stdout, data)

    def errReceived(self, data: bytes):
        self._processData('stderr', self._cb_stderr, data)

    def _logPrefix(self):
        return '[{}#{}]'.format(self._asyncCommand.refName, self.transport.pid)

    def inConnectionLost(self):
        log.warn('%s Lost connection to stdin.', self._logPrefix())

    def errConnectionLost(self):
        log.warn('%s Lost connection to stderr.', self._logPrefix())

    def processEnded(self, reason):
        self._dump_to_callback('stderr', self._cb_stderr)
        self._dump_to_callback('stdout', self._cb_stdout)
        self._asyncCommand.running=False
        self._asyncCommand.exit_code = reason.value.exitCode
        self._cb_exit(self._asyncCommand, self._asyncCommand.exit_code)


class ReactorManager:
    instance = None

    @classmethod
    def Start(cls):
        if cls.instance is None:
            cls.instance = threading.Thread(target=reactor.run, args=(False,))
            cls.instance.daemon = True
            cls.instance.start()
            log.info('Twisted Reactor started.')

    @classmethod
    def Stop(cls):
        reactor.stop()
        log.info('Twisted Reactor stopped.')


class AsyncCommand(object):

    def __init__(self, command, stdout=None, stderr=None, echo=False, env=None, PTY=False, refName=None, debug=False, globbify=True, linebreaks=None):
        self.running=False
        self.echo = echo
        self.command = command
        self.PTY = PTY
        self.stdout_callback = stdout if stdout is not None else self.default_stdout
        self.stderr_callback = stderr if stderr is not None else self.default_stderr
        self.linebreaks = linebreaks

        self.env = os_utils._cmd_handle_env(env)
        self.command = os_utils._cmd_handle_args(command,globbify=globbify)

        self.child = None
        self.refName = self.commandName = os.path.basename(self.command[0])
        if refName:
            self.refName = refName

        self.exit_code = None
        self.exit_code_handler = self.default_exit_handler

        self.log = log

        self.stdout_buffer = ''
        self.stderr_buffer = ''

        self.pipe_reader = None
        self.debug = debug

    def default_exit_handler(self, ascmd, code):
        if code != 0:
            if code < 0:
                strerr = '%s: Received signal %d' % (self.refName, 0-code)
                if code < -100:
                    strerr += ' (?!)'
                self.log.error(strerr)
            else:
                self.log.warning('%s exited with code %d', self.refName, code)
        else:
            self.log.info('%s has exited normally.', self.refName)

    def __addToBuffer(self, text, bufname, ascmd, logmethod):
        #print(bufname, repr(text))
        buf = getattr(self, bufname)

        for c in text:
            if c == '\r':
                continue # Fuck you, you don't exist.
            if c == '\n':
                logmethod('[%s] %s', ascmd.refName, buf+c)
                buf = ''
                continue
            buf += c
        setattr(self, bufname, buf)

    def default_stdout(self, ascmd, buf):
        self.__addToBuffer(buf, 'stdout_buffer', ascmd, ascmd.log.info)

    def default_stderr(self, ascmd, buf):
        self.__addToBuffer(buf, 'stderr_buffer', ascmd, ascmd.log.info)

    def Start(self):
        if self.echo:
            self.log.info('[ASYNC] $ "%s"', '" "'.join(self.command))
        pr = _PipeReader(self, self.child, self.stdout_callback, self.stderr_callback, self.exit_code_handler, self.linebreaks)
        pr.debug = self.debug
        self.running=True
        self.child = reactor.spawnProcess(pr, self.command[0], self.command[1:], env=self.env, usePTY=self.PTY)
        if self.child is None:
            self.log.error('Failed to start %r.', ' '.join(self.command))
            self.running=False
            return False
        ReactorManager.Start()
        return True

    def Stop(self):
        process = os_utils.find_process(self.child.pid)
        if process:
            process.terminate()

    def WaitUntilDone(self):
        while self.IsRunning():
            time.sleep(1)
        return self.exit_code

    def IsRunning(self):
        return self.running

def async_cmd(command, stdout=None, stderr=None, env=None):
    ascmd = AsyncCommand(command, stdout=stdout, stderr=stderr, env=env)
    ascmd.Start()
    return ascmd
