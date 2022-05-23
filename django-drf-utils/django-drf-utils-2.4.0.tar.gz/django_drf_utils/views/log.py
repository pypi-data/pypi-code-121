import logging

from rest_framework import permissions, status, viewsets
from django_drf_utils.views.utils import DetailedResponse

logger = logging.getLogger(__name__)


class LogView(viewsets.ViewSet):
    """Send user logs"""

    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):  # pylint: disable=no-self-use
        forward_headers = ("User-Agent", "Accept-Language", "Origin", "Referer")
        headers = {name: request.headers.get(name) for name in forward_headers}
        payload = request.data.copy()
        level = payload.pop("level", "info").upper()
        message = payload.pop("message", "Frontend log msg")
        stack = payload.pop("stack", "frontend")
        logger.log(
            getattr(logging, level, logging.INFO),
            message,
            extra={
                **payload,
                "headers": headers,
                "stack": stack,
                "user": request.user.username
                if request.user.is_authenticated
                else None,
            },
        )
        return DetailedResponse("ok", status_code=status.HTTP_200_OK)
