from django.http import HttpResponse, JsonResponse

from nwon_django_toolbox.exception_handler.get_error_response import (
    get_error_response as custom_get_response,
)


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response: HttpResponse = self.get_response(request)

        if response.status_code == 500:
            response_data = custom_get_response(
                details=response.__dict__,
                status_code=response.status_code,
            )

            return HttpResponse(response_data, status=response.status_code)

        if response.status_code == 404:
            response_data = custom_get_response(
                details=response.__dict__,
                status_code=response.status_code,
            )

            return HttpResponse(response_data, status=response.status_code)

        return response
