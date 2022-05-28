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

import threading

import marcel.job
import marcel.object.error
import marcel.exception
import marcel.util

debug = marcel.job.debug
Job = marcel.job.Job
JobControl = marcel.job.JobControl


class JobThread(Job):

    def __init__(self, env, command):
        super().__init__(env, command)
        self.thread = None
        self.start_thread()

    def __repr__(self):
        return f'job({self.command.source})'

    def kill(self):
        assert False

    def signal(self, signal):
        assert False

    # ctrl-z
    def pause(self):
        assert False

    # bg
    def run_in_background(self):
        assert False

    # fg
    def run_in_foreground(self):
        assert False

    def check_alive(self):
        if self.thread is None or not self.thread.is_alive():
            self.state = Job.DEAD
            self.thread = None

    # For use by this class

    def start_thread(self):
        def run_command():
            self.command.execute()
        self.thread = threading.Thread(target=run_command)
        self.thread.start()
        while self.thread.is_alive():
            self.thread.join(timeout=Job.JOIN_DELAY_SEC)


class JobControlThread(JobControl):

    def __init__(self, env):
        super().__init__(env)

    def new_job(self, command):
        return JobThread(self.env, command)
