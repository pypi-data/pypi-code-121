class ResourceNotFound(Exception):
    def __init__(self, message='Resource not found'):
        self.message = message
        super().__init__(self.message)


class JSONException(RuntimeError):
    def __init__(self, status, message, stacktrace, logs):
        self.status = status
        self.message = message
        self.stacktrace = stacktrace
        self.logs = logs

    def __str__(self):
        return (
            f'{self.status}: {self.message} \n\n '
            f'{self.stacktrace} \n Server Logs:\n {self.logs}'
        )


class FiddlerException(Exception):
    """An exception raised by client API in case of errors."""

    pass


class MalformedSchemaException(Exception):
    def __init__(self, message='Core Fiddler Object has Malformed Schema'):
        self.message = message
        super().__init__(self.message)


class CommandOptionsError(Exception):
    """Generic exception for insufficient args or configuration."""

    def __init__(self, *args, **kwargs):
        pass
