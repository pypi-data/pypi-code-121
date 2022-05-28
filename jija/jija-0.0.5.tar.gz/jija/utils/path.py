import os.path


class Path:
    def __init__(self, path):
        self.__path, self.__py_ending = self.split(path)

    @staticmethod
    def split(path):
        if isinstance(path, list):
            path = path.copy()
            if path[0] == '':
                path.pop(0)

        elif path.count('/'):
            path = path.split('/')

        elif path.count('\\'):
            path = path.split('\\')

        elif path.count('.'):
            path = path.split('.')
            if path[-1] == 'py':
                path[-2] += f'.{path[-1]}'
                del path[-1]

        else:
            path = [path]

        if not path:
            return path, False

        py_ending = path[-1].endswith('.py')
        if py_ending:
            path[-1] = path[-1][:-3]
        return path, py_ending

    @property
    def python(self):
        return '.'.join(self.__path)

    @property
    def system(self):
        return os.path.join(*self.__path) + ('.py' if self.__py_ending else '')

    def has_protected_nodes(self):
        for node in self.__path:
            if node.startswith('__'):
                return True

    def __add__(self, other):
        if isinstance(other, str) and not self.__py_ending:
            return Path(self.__path + [other])

        elif self.__py_ending:
            raise TypeError()

        else:
            raise NotImplementedError()
