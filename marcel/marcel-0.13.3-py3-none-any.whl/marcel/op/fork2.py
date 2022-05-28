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

import multiprocessing as mp
import multiprocessing.connection as mpc
import os
import threading
import time

import dill

import marcel.argsparser
import marcel.core
import marcel.opmodule
import marcel.op.labelthread


def fork2(env, host, pipelineable):
    assert isinstance(pipelineable, marcel.core.Pipelineable)
    pipelineable = pipelineable.create_pipeline()
    return Fork2(env), [host, pipelineable]


class Fork2ArgsParser(marcel.argsparser.ArgsParser):

    def __init__(self, env):
        super().__init__('fork', env)
        self.add_anon('cluster', convert=self.fork_spec, target='cluster_name')
        self.add_anon('pipeline', convert=self.check_pipeline)
        self.validate()


class Fork2(marcel.core.Op):

    def __init__(self, env):
        super().__init__(env)
        self.cluster_name = None
        self.cluster = None
        self.pipeline = None
        self.remote_pipeline = None
        self.workers = None

    def __repr__(self):
        return f'@{self.cluster_name} {self.pipeline}'

    # AbstractOp

    def setup_1(self):
        self.cluster = self.env().cluster(self.cluster_name)
        self.workers = []
        for host in self.cluster.hosts:
            self.workers.append(ForkWorker(host, self))

    # Op

    def receive(self, _):
        for worker in self.workers:
            worker.start_process()
        for worker in self.workers:
            worker.wait()

    def must_be_first_in_pipeline(self):
        return True

    # Fork

    @staticmethod
    def return_remote_output(writer):
        def f(x):
            writer.send(dill.dumps(x))
        return f


class ForkWorker:

    def __init__(self, host, op):
        self.host = host
        self.op = op
        self.process = None
        # duplex=False: child writes to parent when function completes execution. No need to communicate in the
        # other direction
        self.reader, self.writer = mp.Pipe(duplex=False)
        CHILD_LISTENER.add_listener(self)
        self.pipeline = marcel.core.Pipeline()
        remote = marcel.opmodule.create_op(op.env(), 'remote', op.pipeline)
        remote.set_host(host)
        label_thread = marcel.op.labelthread.LabelThread(op.env())
        label_thread.set_label(host)
        map = marcel.opmodule.create_op(op.env(),
                                        'map',
                                        lambda *x: self.writer.send(dill.dumps(x))
                                        )
        self.pipeline.append(remote)
        self.pipeline.append(label_thread)
        self.pipeline.append(map)
        label_thread.receiver = op.receiver

    # Modeled after Job.start_process
    def start_process(self):
        def run_pipeline_in_child():
            try:
                self.pipeline.set_error_handler(self.op.owner.error_handler)
                self.pipeline.setup_1()
                self.pipeline.set_env(self.op.env())
                self.pipeline.receive(None)
                self.pipeline.receive_complete()
            except BaseException as e:
                self.writer.send(dill.dumps(e))
            self.writer.close()
        self.process = mp.Process(target=run_pipeline_in_child, args=tuple())
        self.process.daemon = False
        self.process.start()
        self.writer.close()

    def wait(self):
        while self.process.is_alive():
            self.process.join(0.1)


# Adapted from job.ChildListener
class ChildListener(threading.Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.waiter = threading.Condition()
        self.workers = []

    def add_listener(self, worker):
        self.waiter.acquire()
        self.workers.append(worker)
        self.waiter.notify()
        self.waiter.release()

    def run(self):
        to_remove = []
        while True:
            self.waiter.acquire()
            # Remove any listeners that threw EOFError in a previous iteration
            for worker in to_remove:
                self.workers.remove(worker)
            to_remove.clear()
            # Wait until a listener has something
            while len(self.workers) == 0:
                self.waiter.wait(1)
            readers = []
            workers = {}
            for worker in self.workers:
                readers.append(worker.reader)
                workers[worker.reader.fileno()] = worker
            self.waiter.release()
            # Process the workers that are ready
            for reader in mpc.wait(readers, 0.1):
                worker = workers[reader.fileno()]
                try:
                    input = reader.recv()
                    if input is not None:
                        x = dill.loads(input)
                        worker.op.send(x)
                except EOFError:
                    to_remove.append(worker)


CHILD_LISTENER = ChildListener()
CHILD_LISTENER.start()