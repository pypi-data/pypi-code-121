import six
import os
import inspect

from rook.exceptions import RookHashFailedException, RookHashCalculationFailed, \
    RookSourceFileNotFound

from rook.processor.error import Error

from rook.logger import logger


class FileUtils(object):
    def __init__(self):
        # This is to allow tests to reliably hook the file open function
        self.open_file = open

    def get_safe_file_contents(self, module):
        filepath = inspect.getsourcefile(module)
        try:
            return self.get_file_contents(None, module, filepath)
        except Exception:
            logger.exception("Error while reading file")
            return None

    def get_file_contents(self, location, module, filepath):
        if not filepath:
            if module.__file__.endswith('.pyc'):
                if location:
                    location.send_warning(Error(exc=RookSourceFileNotFound(module.__file__)))
                return None
            raise RookHashFailedException(module.__name__)

        try:
            with self.open_file(filepath, 'rb') as f:
                string = f.read()
        except IOError as exc:
            # if reading the file has failed, it might be because it's a zipimport.
            # try loading the file contents using the module's loader.
            if not os.path.exists(filepath) and ".zip/" in filepath:
                relative_path = filepath.split(".zip/", 2)[1]
                string = module.__loader__.get_data(relative_path)
            else:
                if not os.path.isfile(filepath):
                    if location:
                        location.send_warning(Error(exc=RookSourceFileNotFound(module.__file__)))
                    return None
                raise RookHashCalculationFailed(filepath, module.__name__, exc)

        return self._normalize_file_contents(string)

    @staticmethod
    def _normalize_file_contents(data):
        if six.PY2:
            string = data.replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00').replace('\r', '\n')
        else:
            string = data.decode().replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00'). \
                replace('\r', '\n').encode('UTF8')
        return string
