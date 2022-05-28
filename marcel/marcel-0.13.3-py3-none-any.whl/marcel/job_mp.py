# This file is part of Marcel.
# 
# Marcel is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your
# option) any later version.
# 
# Marcel is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Marcel.  If not, see <https://www.gnu.org/licenses/>.

import os
import multiprocessing as mp
import multiprocessing.connection as mpc
import signal
import sys
import threading

import marcel.job
import marcel.object.error
import marcel.exception
import marcel.util

debug = marcel.job.debug
Job = marcel.job.Job
JobControl = marcel.job.JobControl

# The code for processing child input from multiple processes is adapted from here:
# https://docs.python.org/3/library/multiprocessing.html#multiprocessing.connection.wait
# w.close() in the parent process is extremely subtle (to me).
# Multiprocessing and signal handling is discussed here:
# See https://www.titonbarua.com/posts/2014-10-29-safe-use-of-unix-signals-with-multiprocessing-modules-in-python
#
# Signal handling:
# When a process receives a signal, that signal is propagated to its children, (created by mp.Process().start())
# The main (console-handling) process can issue additional signals, aimed at specific children, but otherwise,
# signal processing is all-or-none. I.e., the handling of a signal is the same across all of the children.
#
# - Ctrl-C: When typed on the console, this generates SIGINT. We want to kill the foreground process, only, if there
#   is one. We don't want the signal reaching all children, as they will all die. And if they all ignore the signal,
#   then they are unkillable, by SIGINT anyway. So do the following:
#   - Main process handles SIGINT.
#   - Child processes ignore it.
#   - Main process SIGINT handler sends SIGTERM to the child implementing the foreground process.
#
# - Ctrl-Z: When typed on the console, this generates SIGTSTP. We want to move the foreground process, if there is
#   one, to the background and pause it. This can be done as follows:
#   - Main process handles SIGTSTP.
#   - Child processes do the default (suspend).
#   - Main process SIGTSTP handler reawakens children that are supposed to be running by sending SIGCONT.


class JobMP(Job):

    def __init__(self, env, command):
        super().__init__(env, command)
        self.process = None
        self.start_process()

    def __repr__(self):
        return (f'job({self.process.pid}({self.state_symbol()}): {self.command.source})'
                if self.process else
                f'job(-----({self.state_symbol()}): {self.command.source})')

    def kill(self):
        if self.state != Job.DEAD:
            debug(f'kill {self}')
            self.state = Job.DEAD
            try:
                os.kill(self.process.pid, signal.SIGTERM)
                self.process.join(Job.JOIN_DELAY_SEC)
                if self.process.is_alive():
                    os.kill(self.process.pid, signal.SIGKILL)
                    self.process.join(Job.JOIN_DELAY_SEC)
                    if self.process.is_alive():
                        print(f'Unable to kill {self}', file=sys.stderr)
                    else:
                        self.process = None
            except ProcessLookupError:
                pass

    def signal(self, signal):
        debug(f'signal {self} {signal}')
        try:
            os.kill(self.process.pid, signal)
        except ProcessLookupError:
            pass

    # ctrl-z
    def pause(self):
        debug(f'pause {self}')
        if self.state not in (Job.RUNNING_PAUSED, Job.DEAD):
            debug(f'sending SIGTSTP to {self.process.pid}')
            self.state = Job.RUNNING_PAUSED
            os.kill(self.process.pid, signal.SIGTSTP)

    # bg
    def run_in_background(self):
        debug(f'run_in_background {self}')
        if self.state != Job.DEAD:
            self.state = Job.RUNNING_BACKGROUND
            os.kill(self.process.pid, signal.SIGCONT)

    # fg
    def run_in_foreground(self):
        debug(f'run_in_foreground {self}')
        if self.state == Job.RUNNING_FOREGROUND:
            pass
        elif self.state == Job.RUNNING_BACKGROUND:
            self.state = Job.RUNNING_FOREGROUND
        elif self.state == Job.RUNNING_PAUSED:
            self.state = Job.RUNNING_FOREGROUND
            os.kill(self.process.pid, signal.SIGCONT)
        elif self.state == Job.DEAD:
            raise marcel.exception.KillCommandException('Cannot foreground killed job')

    def check_alive(self):
        if self.process is None or not self.process.is_alive():
            self.state = Job.DEAD
            self.process = None

    # For use by this class

    def start_process(self):
        def run_command_in_child(command, writer):
            debug(f'running: {command.source}')
            try:
                debug(f'About to execute {command.pipeline}')
                debug(f'Env {type(self.env.impl)}')
                command.execute()
                debug(f'Command complete, env keys: {self.env.allvars().keys()}')
            except marcel.exception.KillCommandException as e:
                marcel.util.print_to_stderr(e, self.env)
            except marcel.exception.KillAndResumeException as e:
                # Error handler printed the error
                pass
            writer.close()

        # duplex=False: child writes to parent when function completes execution. No need to communicate in the
        # other direction
        debug(f'About to spawn process for {self.command.source}')
        reader, writer = mp.Pipe(duplex=False)
        self.process = mp.Process(target=run_command_in_child, args=(self.command, writer))
        self.process.daemon = True
        try:
            # Set up process handling as it should exist in the child process. Ignore ctrl-c (since that
            # should only kill the foreground process), and default handling for ctrl-z (pause).
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGTSTP, signal.SIG_DFL)
            self.process.start()
            writer.close()  # See topmost comment
        finally:
            # Restore process handling needed by the console process.
            signal.signal(signal.SIGINT, JobControl.only.ctrl_c_handler)
            signal.signal(signal.SIGTSTP, JobControl.only.ctrl_z_handler)
        debug(f'Started process {self.process.pid}')


class ChildListener(threading.Thread):

    def __init__(self, child_completion_handler):
        super().__init__()
        self.daemon = True
        self.child_completion_handler = child_completion_handler
        self.waiter = threading.Condition()
        self.listeners = []

    def add_listener(self, listener):
        self.waiter.acquire()
        self.listeners.append(listener)
        self.waiter.notify()
        self.waiter.release()

    def run(self):
        to_remove = []
        while True:
            self.waiter.acquire()
            # Remove any listeners that threw EOFError in a previous iteration
            for listener in to_remove:
                self.listeners.remove(listener)
            to_remove.clear()
            # Wait until a listener has something
            while len(self.listeners) == 0:
                self.waiter.wait(1)
            listeners = list(self.listeners)
            self.waiter.release()
            # Process the listeners that are ready
            for listener in mpc.wait(listeners, 0.1):
                try:
                    self.child_completion_handler(listener.recv())
                except EOFError:
                    to_remove.append(listener)


class JobControlMP(JobControl):

    def __init__(self, env):
        super().__init__(env)
        signal.signal(signal.SIGINT, self.ctrl_c_handler)
        signal.signal(signal.SIGTSTP, self.ctrl_z_handler)

    def ctrl_c_handler(self, signum, frame):
        debug(f'ctrl c handler')
        assert signum == signal.SIGINT
        assert os.getpid() == JobControl.pid  # Parent process
        foreground = self.foreground()
        if foreground:
            foreground.kill()

    def ctrl_z_handler(self, signum, frame):
        debug(f'ctrl z handler')
        assert signum == signal.SIGTSTP
        assert os.getpid() == JobControl.pid  # Parent process
        foreground = self.foreground()
        if foreground:
            foreground.pause()
            print()
        # Ctrl-Z propagates to children, suspending them. If they should be running in the background, restart them.
        for job in self._jobs:
            if job.state == Job.RUNNING_BACKGROUND:
                job.run_in_background()

    def new_job(self, command):
        return JobMP(self.env, command)
