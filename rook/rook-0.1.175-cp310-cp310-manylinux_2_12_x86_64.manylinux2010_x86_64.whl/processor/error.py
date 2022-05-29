import sys
import traceback

from rook.exceptions import ToolException
from rook.processor.namespace_serializer import NamespaceSerializer  # lgtm[py/cyclic-import]
from .namespaces.python_object_namespace import PythonObjectNamespace
import rook.protobuf.variant_pb2


class Error(object):
    def __init__(self, exc=None, type=None, message=None, parameters=None, traceback=None):
        self.exc = exc

        if isinstance(exc, ToolException):
            self.type = exc.get_type()
            self.message = exc.get_message()
            self.parameters = exc.get_parameters()
        else:
            self.type = type or "Unknown"
            self.message = message
            self.parameters = parameters

        # Extract traceback if was not supplied
        self.traceback = traceback
        if self.traceback is None and sys.exc_info()[2]:
            self.traceback = sys.exc_info()[2]

    def dump(self, error, serializer=None):
        if serializer is None:
            serializer = NamespaceSerializer()

        try:
            if self.message:
                error.message = NamespaceSerializer.normalize_string(self.message)
            else:
                error.message = ''
        except Exception: # We are already deep in error handling code - just ignore
            pass

        try:
            error.type = NamespaceSerializer.normalize_string(self.type)
        except Exception: # We are already deep in error handling code - just ignore
            pass

        try:
            serializer.dump(PythonObjectNamespace(self.parameters), error.parameters, False)
        except Exception: # We are already deep in error handling code - just ignore
            pass

        try:
            serializer.dump(PythonObjectNamespace(self.exc), error.exc, False)
        except Exception: # We are already deep in error handling code - just ignore
            pass

        try:
            if self.traceback:
                traceback_string = '\n'.join(traceback.format_tb(self.traceback))
                serializer.dump(PythonObjectNamespace(traceback_string,
                                                      PythonObjectNamespace.ObjectDumpConfig.tailor_limits(traceback_string)),
                                error.traceback, False)
        except Exception: # We are already deep in error handling code - just ignore
            pass

    def dumps(self):
        error = rook.protobuf.variant_pb2.Error()
        self.dump(error)
        return error
