from multiprocessing import Process, Queue
from typing import Dict, Any

from cosapp.systems.externalsystem import ExternalSystem


class ProcessSystem(ExternalSystem):

    __slots__ = ('_queue_in', '_queue_out', 'to_execute')

    def __init__(self, name: str, **kwargs):
        self._queue_in = Queue()
        self._queue_out = Queue()
        self.to_execute = Queue()

        super().__init__(name, **kwargs)

    def _initialize(self, **kwargs):
        self.add_inward(
            "working_folder",
            None,
            dtype=str,
            desc="Folder of execution for the process.",
        )
        return kwargs

    def call_setup_run(self):
        super().call_setup_run()
        self._process = Process(
            target=self.to_execute,
            args=(self._queue_in, self._queue_out, self.working_folder),
        )
        self._process.start()

    def call_clean_run(self):
        self._queue_in.put({})
        # self._queue_out.get()
        self._process.join()
        super().call_clean_run()

    def send_inputs(self):
        self._queue_in.put(self.serialize_data())

    def read_outputs(self, timeout: float = 1) -> Dict[str, Any]:
        return self._queue_out.get(True, timeout)
