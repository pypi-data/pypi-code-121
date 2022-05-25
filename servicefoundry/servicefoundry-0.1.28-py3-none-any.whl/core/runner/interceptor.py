import inspect
import os
import subprocess
import sys
from pathlib import Path

from servicefoundry.internal.interceptor import main
from servicefoundry.internal.interceptor.communication import (
    Ack,
    CloseException,
    ErrorResponse,
    InvokeException,
)
from servicefoundry.internal.interceptor.main import Communication


class Interceptor:
    def __init__(self, predict_file):
        path = Path(predict_file)
        if not path.exists():
            raise RuntimeError(f"{predict_file} not exist.")
        self.predict_file = predict_file

        if predict_file.endswith(".py"):
            self.module_name = predict_file[0:-3].replace(os.sep, ".")
        else:
            raise RuntimeError(f"{predict_file} doesn't end with py")

        (self.read1, self.write1) = os.pipe()  # for parent -> child writes
        (self.read2, self.write2) = os.pipe()  # for child -> parent writes
        command = [
            sys.executable,
            inspect.getfile(main),
            predict_file,
            str(self.read1),
            str(self.write2),
        ]
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            pass_fds=(self.read1, self.write2),
        )
        infile = os.fdopen(self.read2)
        outfile = os.fdopen(self.write1, "w", buffering=1)
        self.communication = Communication(infile, outfile)
        msg = self.communication.read_input_msg()
        if isinstance(msg, Ack):
            return
        if isinstance(msg, ErrorResponse):
            raise RuntimeError(f"Failed to load predictor. Cause by: {msg.message}")

    def _read_response(self):
        try:
            return self.communication.read_response()
        except InvokeException as e:
            print(e.traceback)
            raise e
        except CloseException as e:
            self.close()
            print(e.traceback)
            raise e

    def invoke(self, function_name, **kwargs):
        self.communication.write_invoke(function_name, **kwargs)
        return self._read_response()

    def get_dependencies(self):
        self.communication.write_dependencies()
        return self._read_response()

    def get_functions(self):
        self.communication.write_function()
        return self._read_response()

    def close(self):
        self.process.terminate()
        for line in self.process.stdout.readlines():
            print(line)
        self.communication.close()

    @classmethod
    def create(cls, predict_file):
        return cls(predict_file)
