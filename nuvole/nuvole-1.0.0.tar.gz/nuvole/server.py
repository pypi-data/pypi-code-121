from .logger import log
import tornado.ioloop
import tornado.web


class Server:

    def __init__(self, services, context=None):
        """
        Class Server
        :param services: list of Service's subclasses
        :param context: useful data object (optional)
        """
        self.app = tornado.web.Application(handlers=[
            (service.PATH, service, dict(context=context)) for service in services
        ])

    def run(self, host, port):
        """
        Run httpServer
        :param host: serving host
        :param port: serving port
        """
        self.app.listen(port, address=host)
        log.info(f'Start listening on {host}:{port}')
        tornado.ioloop.IOLoop.instance().start()
