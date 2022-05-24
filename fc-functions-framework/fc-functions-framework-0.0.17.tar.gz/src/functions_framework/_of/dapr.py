

class DaprApplication:
    def __init__(self, app, port, **options):
        self.app = app

        self.port = port

        self.options = options

    def run(self):
        self.app.run(self.port, **self.options)
