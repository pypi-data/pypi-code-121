from .namespace import Namespace


class ErrorNamespace(Namespace):

    def __init__(self, message, parameters, exception_namespace, traceback_namespace):
        super(ErrorNamespace, self).__init__()
        self.message = message
        self.parameters = parameters
        self.exc = exception_namespace
        self.traceback = traceback_namespace
