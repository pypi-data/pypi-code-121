class Registry:
    def __init__(self):
        self.functions = {}

    def register(self, name: str):
        def wrapped(function):
            self.functions[name] = function
            return function
        return wrapped
