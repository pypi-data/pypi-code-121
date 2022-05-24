
class DaprServer:
    def __init__(self, app, port, **options):
        self.app = app
        self.port = port
        self.options = options

    def run(self):
        print("service run in {}".format(self.port))
        self.app.run(self.port, **self.options)


def create_dapr_server(app, port, **options):
    return DaprServer(app, port, **options)
