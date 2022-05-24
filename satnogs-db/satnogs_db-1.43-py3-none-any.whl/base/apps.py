"""SatNOGS DB Base app config"""
from django.apps import AppConfig


class BaseConfig(AppConfig):
    """Set configuration of the SatNOGS DB Base app"""
    name = 'db.base'
    verbose_name = "Base"

    def ready(self):
        from db.base import signals  # noqa: F401; pylint: disable=C0415,W0611
