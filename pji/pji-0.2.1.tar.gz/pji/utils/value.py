from multiprocessing import Lock


class ValueProxy:
    def __init__(self, init_value=None):
        self.__value = init_value
        self.__lock = Lock()

    @property
    def value(self):
        with self.__lock:
            return self.__value

    @value.setter
    def value(self, new_value):
        with self.__lock:
            self.__value = new_value
