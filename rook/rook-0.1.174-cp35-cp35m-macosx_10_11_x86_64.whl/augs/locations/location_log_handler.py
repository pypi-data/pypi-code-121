from rook.services.logging_location_service import LoggingLocationService

from .location import Location


class LocationLogHandler(Location):

    NAME = 'log_handler'

    def __init__(self, output, aug, arguments, processor_factory):
        super(LocationLogHandler, self).__init__(output, aug)

    def _add_aug_internal(self, trigger_services):
        trigger_services.get_service(LoggingLocationService.NAME).add_logging_aug(self)
