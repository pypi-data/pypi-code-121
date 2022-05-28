class TXTMetadata:
    def __init__(self, path):
        self.path = path

    def readFile(self):
        with open(self.path, 'r') as file:
            lines = file.readlines()
        return lines

    @property
    def asDict(self):
        return {}

    @property
    def keys(self):
        return {}