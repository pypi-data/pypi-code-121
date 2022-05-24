from . import config
from .transform import Transform
from .py_loader import PyLoader


class PyTransform(Transform):
    """"""

    def __init__(self, mode, source, destination, directory=None, filename=None):
        super().__init__(mode, source, destination)

        if directory:
            self.scripts = PyLoader.from_directory(directory, mode, source, destination)
        elif filename:
            self.scripts = [PyLoader(filename, mode, source, destination)]
        else:
            raise config.ConfigError(
                "SQL transform must be given directory or file attribute"
            )

    def get_scripts(self):
        return self.scripts
