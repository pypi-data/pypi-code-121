import threading


class _TLockedIterator(object):
    def __init__(self, generator):
        self.__lock = threading.Lock()
        self.__generator = iter(generator)

    def __iter__(self):
        return self

    def __next__(self):
        with self.__lock:
            return next(self.__generator)


def gen_lock(gen):
    return _TLockedIterator(gen)
