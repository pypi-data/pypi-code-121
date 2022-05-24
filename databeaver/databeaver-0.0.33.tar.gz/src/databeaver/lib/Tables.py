from .Object import Object

class Tables(Object):
    def __init__(self, schema_dir=None, tables=None):
        """

        :param schema_dir: Directory containing json definitions for the tables needed in the system
        :param tables:
        """

