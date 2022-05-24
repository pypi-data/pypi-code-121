from django.conf import settings
from dnoticias_services.base_service import BaseService


class BaseSubscriptionRequest(BaseService):
    API_KEY = getattr(settings, "SUBSCRIPTION_SERVICE_ACCOUNT_API_KEY", None)
    TIMEOUT = getattr(settings, "SUBSCRIPTION_SERVICE_REQUEST_TIMEOUT", 5)
