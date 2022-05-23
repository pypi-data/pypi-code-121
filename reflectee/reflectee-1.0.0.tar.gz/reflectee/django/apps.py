import os
from django.apps import AppConfig

__all__ = ["DjangoAppConfig"]

class DjangoAppConfig(AppConfig):
    name = "reflectee"
    verbose_name = "Application"

    def ready(self):

        from django.conf import settings
        from ..handlers import loads
        
        api_path = getattr(settings, 'REFLECTEE_API_PATH', os.environ.get('REFLECTEE_API_PATH', 'api'))
        loads(api_path)

