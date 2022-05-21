#cheese

class HTTPError(Exception):
    def __init__(self, description, name, code):
        self.description = description
        self.name = name
        self.code = code