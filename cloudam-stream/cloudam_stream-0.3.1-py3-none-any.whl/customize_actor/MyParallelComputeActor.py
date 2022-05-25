from cloudam_stream.core.actors import ParallelComputeActor
from cloudam_stream.core.ports.inputports import TextInputPort
from cloudam_stream.core.ports.outputports import TextOutputPort


class MyParallelComputeActor(ParallelComputeActor):
    title = "My Parallel Compute Actor"
    name = "Parallel"

    intake = TextInputPort()
    success = TextOutputPort()
    parameter_overrides = {
        "parallelism": 2,
    }

    ss = ""

    def begin(self):
        self.sss = ""

    def process(self, item, port):

        self.success.emit(item)
