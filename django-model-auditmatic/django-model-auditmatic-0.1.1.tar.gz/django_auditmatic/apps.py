"""
    app config
"""
from django.apps import AppConfig
from django.conf import settings


class DjangoAuditmaticConfig(AppConfig):
    """
    config
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_auditmatic"


if not hasattr(settings, "AUDITMATIC"):
    raise RuntimeError("AUDITMATIC Config not detected.")
