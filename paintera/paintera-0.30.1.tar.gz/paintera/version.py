class _Version(object):

    def __init__(
            self,
            major,
            minor,
            patch,
            tag):
        self._major    = major
        self._minor    = minor
        self._patch    = patch
        self._tag      = tag
        self._snapshot = '' if self._tag == '' else 'SNAPSHOT'
        self._python_version = f'{self._major}.{self._minor}.{self._patch}.{self._tag}'.strip('.')
        self._maven_version  = f'{self._major}.{self._minor}.{self._patch}-{self._snapshot}'.strip('-')

    def major(self):
        return self._major

    def minor(self):
        return self._minor

    def patch(self):
        return self._patch

    def tag(self):
        return self._tag

    def python_version(self):
        return self._python_version

    def maven_version(self):
        return self._maven_version

    def is_release(self):
        return self.tag() == ''

    def __str__(self):
        return self.python_version()

_paintera_version = _Version(0, 30, 1, '')
