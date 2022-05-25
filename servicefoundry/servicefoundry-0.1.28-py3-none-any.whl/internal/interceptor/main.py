import importlib
import inspect
import os
import sys
import traceback

from servicefoundry.internal.interceptor.communication import (
    Communication,
    Dependencies,
    Function,
    Invoke,
)
from servicefoundry.internal.interceptor.module_interceptor import ModuleInterceptor


def main(file_name, communication):
    sys.path.insert(1, os.getcwd())
    module_interceptor = ModuleInterceptor()
    module = importlib.import_module(file_name.split(".")[0])
    communication.write_ack()
    while True:
        process_command(module, module_interceptor, communication)


def process_command(module, module_interceptor, communication):
    command = communication.read_input_msg()
    if isinstance(command, Invoke):
        try:
            method_to_call = getattr(module, command.function)
            res = method_to_call(**command.payload)
            communication.write_response(res)
        except Exception as e:
            communication.write_exception(str(e), traceback.format_exc())
    elif isinstance(command, Dependencies):
        communication.write_response(module_interceptor.get_dependencies())
    elif isinstance(command, Function):
        functions = [
            member[0]
            for member in inspect.getmembers(module, predicate=inspect.isfunction)
        ]
        communication.write_response(functions)
    else:
        communication.write_exception(f"Can only handle command of type {[Invoke]}")


if __name__ == "__main__":
    infile = os.fdopen(int(sys.argv[2]))
    outfile = os.fdopen(int(sys.argv[3]), "w", buffering=1)
    communication = Communication(infile, outfile)
    try:
        main(sys.argv[1], communication)
    except Exception as e:
        print("Closing Interceptor.")
        traceback.format_exc()
        communication.write_exception(str(e), traceback.format_exc())
        communication.close()
