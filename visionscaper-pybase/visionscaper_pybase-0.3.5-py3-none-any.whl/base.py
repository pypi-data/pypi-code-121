from basics.logging import get_logger


class Base:

    def __init__(self, *args, pybase_logger_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        if pybase_logger_name is None:
            pybase_logger_name = self.__class__.__name__

        self._pybase_logger_name = pybase_logger_name

        self._valid = True
        self._log = self._get_logger(self._pybase_get_logger_name())

    def instance_valid(self):
        return self._valid

    def _pybase_get_logger_name(self):
        return self._pybase_logger_name

    def _get_logger(self, name):
        return get_logger(name)

    def __str__(self):
        return self._pybase_get_logger_name()
