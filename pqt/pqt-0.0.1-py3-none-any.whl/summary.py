import duckdb


class Summary:

    def __init__(self, **kwargs):
        self.file = kwargs.get('file')
        self.lines = kwargs.get('lines')
        self.cursor = duckdb.connect().cursor()
        self.data = []

    def print(self):
        for entry in self.data:
            print(entry)
