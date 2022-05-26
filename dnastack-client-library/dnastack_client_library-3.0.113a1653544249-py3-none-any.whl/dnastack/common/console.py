import sys
from imagination.decorator import service
from threading import Lock


@service.registered()
class Console:
    """
    Virtual Console

    This class is a workaround to allow external processes capture the output through it.
    """
    def __init__(self):
        self.__output_lock = Lock()

    def print(self, content, end='\n'):
        with self.__output_lock:
            print(content, end=end)
            sys.stdout.flush()