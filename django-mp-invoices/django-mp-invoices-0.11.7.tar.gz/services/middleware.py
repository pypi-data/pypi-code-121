
from django.utils.functional import SimpleLazyObject
from services.service import ServicesService


class ServicesMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.services = SimpleLazyObject(
            lambda: ServicesService(request.user))
        return self.get_response(request)
