from . import config
from .sql_loader import SqlLoader
from .transform import Transform


class SQLTransform(Transform):
    """
    SQL transform runs in the destination, it needs a local source (same db as destination)
    """

    def __init__(self, mode, source, destination, directory=None, filename=None):
        super().__init__(mode, source, destination)
        assert source.local == True

        if directory:
            self.scripts = SqlLoader.from_directory(
                directory, mode, source, destination
            )
        elif filename:
            self.scripts = [SqlLoader(filename, mode, source, destination)]
        else:
            raise config.ConfigError(
                "SQL transform must be given directory or file attribute"
            )

    def get_scripts(self):
        return self.scripts
