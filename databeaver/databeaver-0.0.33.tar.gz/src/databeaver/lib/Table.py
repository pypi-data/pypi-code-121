from .Object import Object
import json

class Table(Object):
    """
    Abstract table class (not tied to a specific database engine)
    """
    def __init__(self, name, definition_file=None, columns=None):
        self.name = name
        self.columns = []
        super.__init__()
        logger = self.get_logger()
        if definition_file is None and columns is None:
            logger.error(f"{self.name} is invalid. No definition file or fields provided.")

        # Load the column information
        if definition_file:
            with open(definition_file) as f:
                self.columns = json.load(f)
        else:
            self.columns = columns

