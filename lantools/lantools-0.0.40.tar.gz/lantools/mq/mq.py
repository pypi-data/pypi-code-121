class Reader:
    def __init__(self, options):
        self.options = options

    def get_option(self, name, default=None):
        if name in self.options:
            return self.options.get(name)
        else:
            return default

    def run(self, callback):
        pass

class Writer:
    def write(self, message, *, callback=None):
        pass
