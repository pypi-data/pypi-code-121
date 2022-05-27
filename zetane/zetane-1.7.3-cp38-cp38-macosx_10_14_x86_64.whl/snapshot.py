

class Snapshot:
    """The snapshot class is responsible for serializing python API state to be loaded later in the engine.

    Returns:
        Snapshot: An object with handles for serializing core objects
    """
    def __init__(self, nsocket):
        pass


    def append(self, item):
        return self


    def capture(self, objects):
        """ Capture objects and serialize to file

        Args:
          objects (dict): keyed dictionary of id / object pairs to write to file
        """
        return self


    def serialize(self, filename=""):
        return self
