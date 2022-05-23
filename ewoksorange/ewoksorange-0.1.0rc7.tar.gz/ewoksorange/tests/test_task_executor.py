from AnyQt.QtCore import QObject

from ewoksorange.bindings.taskexecutor import TaskExecutor
from ewoksorange.bindings.taskexecutor import ThreadedTaskExecutor
from ewoksorange.bindings.taskexecutor_queue import TaskExecutorQueue
from ewoksorange.bindings.qtapp import QtEvent
from ewokscore.tests.examples.tasks.sumtask import SumTask


def test_task_executor():
    executor = TaskExecutor(SumTask)
    assert not executor.is_ready_to_execute
    assert not executor.succeeded

    executor.create_task(inputs={"a": 1, "b": 2})
    assert executor.is_ready_to_execute
    assert not executor.succeeded

    executor.execute_task()
    assert executor.succeeded
    results = {k: v.value for k, v in executor.output_variables.items()}
    assert results == {"result": 3}


def test_threaded_task_executor(qtapp):
    finished = QtEvent()

    def finished_callback():
        finished.set()

    executor = ThreadedTaskExecutor(ewokstaskclass=SumTask)

    executor.finished.connect(finished_callback)
    assert not executor.is_ready_to_execute
    assert not executor.succeeded

    executor.create_task(inputs={"a": 1, "b": 2})
    assert executor.is_ready_to_execute
    assert not executor.succeeded

    executor.start()
    assert finished.wait(timeout=3)
    assert executor.succeeded
    results = {k: v.value for k, v in executor.output_variables.items()}
    assert results == {"result": 3}

    executor.finished.disconnect(finished_callback)


def test_threaded_task_executor_queue(qtapp):
    class MyObject(QObject):
        def __init__(self):
            self.results = None
            self.finished = QtEvent()

        def finished_callback(self):
            # taskExecutor = self.sender()  # Doesn't work for unknown reasons
            taskExecutor = executor._taskExecutor
            self.results = {
                k: v.value for k, v in taskExecutor.output_variables.items()
            }
            self.finished.set()

    obj = MyObject()
    executor = TaskExecutorQueue(ewokstaskclass=SumTask)
    executor.add(inputs={"a": 1, "b": 2}, _callbacks=(obj.finished_callback,))
    assert obj.finished.wait(timeout=3)
    assert obj.results == {"result": 3}
