from cloudam_stream.core.actors import SourceActor
from cloudam_stream.core.ports.outputports import TextOutputPort

from cloudam_stream.core.parameters import FileInputParameter
from cloudam_stream.core.constants import config


class SmiFileSourceActor(SourceActor):
    title = "Smi File Source Actor"
    # 必填，用来定位ports
    name = "Source"
    success = TextOutputPort()
    input_file = FileInputParameter()

    def __iter__(self):
        source_file = config.INPUT_FILE_DIRECTORY + self.args.input_file
        print("------source file"+source_file)
        with open(source_file) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                yield line
