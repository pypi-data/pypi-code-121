import threading

from pynextflow.entities.workflow import Workflow

_thread_data = None


class Executor(object):

    def __enter__(self):
        global _thread_data
        _thread_data = threading.local()
        _thread_data.executor = self
        _thread_data.body = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _thread_data
        _thread_data = None

    def run(self, work: Workflow, returns=False):
        pass


def _get_executor() -> Executor:
    global _thread_data
    return None if _thread_data is None else _thread_data.executor


def _executor_start():
    global _thread_data
    if _thread_data:
        _thread_data.body = True


def _executor_end():
    global _thread_data
    if _thread_data:
        _thread_data.body = False


def _executor_started() -> bool:
    global _thread_data
    if _thread_data:
        return _thread_data.body == True
    return False
