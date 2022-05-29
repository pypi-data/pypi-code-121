from .location import Location

from rook.services.http_server_services.http_server_services import HttpServerService


class HttpServerHandler(Location):

    NAME = 'http_server'

    def __init__(self, output, aug, arguments, processor_factory):
        super(HttpServerHandler, self).__init__(output, aug)

    def _add_aug_internal(self, trigger_services):
        trigger_services.get_service(HttpServerService.NAME).add_logging_aug(self)
