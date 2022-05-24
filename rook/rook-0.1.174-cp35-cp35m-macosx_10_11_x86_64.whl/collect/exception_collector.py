import os
import sys
import traceback
from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.processor.namespaces.python_object_namespace import PythonObjectNamespace
from rook.processor.namespaces.collection_namespace import ListNamespace
from rook.services.exception_capturing_location_service import ExceptionCapturingLocationService
from rook.logger import logger
import uuid
from rook.singleton import singleton_obj

if sys.version.startswith('2'):
    import funcsigs
    signature_function = funcsigs.signature
else:
    import inspect
    signature_function = inspect.signature


class ExceptionCollector(object):

    class Traceback(object):
        def __init__(self, filename, line_number, function_name):
            self.filename = filename
            self.line = line_number
            self.function = function_name

    def __init__(self, output=None, exception_capturing_service=None):
        if output is None:
            output = singleton_obj._output

        self._output = output
        if exception_capturing_service is None:
            exception_capturing_service = singleton_obj.get_trigger_services().get_service(
                    ExceptionCapturingLocationService.NAME)

        self._exception_capturing_service = exception_capturing_service

    def collect(self, exc=None):
        try:
            if not self._exception_capturing_service.activation_status():
                return

            if exc is None:
                exc = sys.exc_info()[1]

            data_namespace = self._get_exception_data(exc)
            aug_ids = self._get_global_rule_ids()
            message_id = self._get_message_id()

            for aug_id in aug_ids:
                self._output.send_user_message(aug_id, message_id, data_namespace)
        except Exception as exc:
            logger.exception('Rook capture exception failed while collecting data')


    def _get_exception_data(self, exc):
        trace = self._get_exception_traceback(exc)
        local_variables = sys._getframe(4).f_locals
        return self._get_rookout_container_namespace(local_variables, trace, exc)

    def _get_exception_traceback(self, exc):
        if hasattr(exc, '__traceback__'):
            return self._get_exception_traceback_py3(exc)
        return self._get_exception_traceback_py2()

    def _get_exception_traceback_py3(self, exc):
        new_traceback = []
        trace = traceback.extract_tb(exc.__traceback__)

        for frame in trace:
            new_traceback.append(self.Traceback(frame.filename, frame.lineno, frame.name))

        return new_traceback

    def _get_exception_traceback_py2(self):
        new_traceback = []
        raw_traceback = sys.exc_info()[2]
        trace = traceback.extract_tb(raw_traceback)

        for frame in trace:
            new_traceback.append(self.Traceback(frame[0], frame[1], frame[2]))

        return new_traceback

    def _get_rookout_container_namespace(self, local_variables, traceback, exc):

        frame_container = self._get_frame_container(local_variables)
        traceback_container = self._wrap_traceback_in_namespace(traceback)
        exception_information_namespace = self._get_exception_information_namespace(exc, traceback)
        rookout_container = ContainerNamespace(
            {'frame': frame_container, 'traceback': traceback_container,
             'exception_information': exception_information_namespace})

        return ContainerNamespace({'rookout': rookout_container})

    def _get_frame_container(self, local_variables):
        locals_container = self._wrap_locals_in_container_namespace(local_variables)
        return ContainerNamespace({'locals': locals_container})

    def _wrap_locals_in_container_namespace(self, local_variables):
        """
        returns a ContainerNamespace with each variable given wrapped in PythonObjectNamespace
        """
        locals_container = ContainerNamespace({})

        for local_variable_name in local_variables:
            local_container_variable = PythonObjectNamespace(local_variables[local_variable_name])
            locals_container.write_attribute(local_variable_name, local_container_variable)

        return locals_container

    def _wrap_traceback_in_namespace(self, traceback_stack):
        traceback_attributes = []

        for stack_cell in traceback_stack:
            stack_cell_container = ContainerNamespace({})

            for attribute_name in [attr_name for attr_name in dir(stack_cell) if not attr_name.startswith('_')]:
                attribute_container = PythonObjectNamespace(stack_cell.__getattribute__(attribute_name))
                stack_cell_container.write_attribute(attribute_name, attribute_container)

            traceback_attributes.append(stack_cell_container)

        return ListNamespace(traceback_attributes)

    def _get_exception_information_namespace(self, exc, traceback_stack):
        exception_type = PythonObjectNamespace(type(exc).__name__)
        exception_frame = traceback_stack[-1]
        file_path = PythonObjectNamespace(exception_frame.filename)
        filename = PythonObjectNamespace(os.path.split(exception_frame.filename)[1])
        line_number = PythonObjectNamespace(exception_frame.line)
        try:
            exception_parameters = PythonObjectNamespace(dict(zip(
                [parameter for parameter in signature_function(exc.__init__).parameters],
                exc.args)))
        except ValueError:
            # init signature is not supported for this type of exception in Python2
            exception_parameters = PythonObjectNamespace({})

        return ContainerNamespace({
            'exception_type': exception_type,
            'file_path': file_path,
            'filename': filename,
            'line_number': line_number,
            'exception_parameters': exception_parameters})

    def _get_global_rule_ids(self):
        return self._exception_capturing_service.get_ids()

    def _get_message_id(self):
        return uuid.uuid4().hex


def collect(exc):
    ExceptionCollector().collect(exc)
