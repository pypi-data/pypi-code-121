from typing import List

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


def get_messages_data(request) -> "List[dict]":
    """
        Get list of dictionary for text and type
    """
    messages_data = []
    for message in messages.get_messages(request):
        messages_data.append({
            "type": message.level_tag,
            "text": str(message)
        })
    return messages_data


class RequestException(APIException):
    """
        Custom exception
    """
    status_code = status.HTTP_417_EXPECTATION_FAILED
    default_detail = _('Could not satisfy the request Accept header.')
    default_code = 'not_acceptable'

    def __init__(self, request, code=None):
        if code is not None:
            self.status_code = code
        detail = {"_messages": get_messages_data(request)}
        super().__init__(detail, self.default_code)
