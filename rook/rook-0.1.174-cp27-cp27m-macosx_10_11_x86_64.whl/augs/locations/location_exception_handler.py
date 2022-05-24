from .location import Location

from rook.services.exception_capturing_location_service import ExceptionCapturingLocationService


class LocationExceptionHandler(Location):

    NAME = 'exception_handler'

    def __init__(self, output, aug, arguments, processor_factory):
        super(LocationExceptionHandler, self).__init__(output, aug)

    def _add_aug_internal(self, trigger_services):
        trigger_services.get_service(ExceptionCapturingLocationService.NAME).add_exception_capturing_aug(self)
