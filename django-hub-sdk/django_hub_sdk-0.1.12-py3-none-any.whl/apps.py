from django.apps import AppConfig


class HubSdkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_hub_sdk"
    
    def ready(self):
        from . import settings as hub_settings
        from django.conf import settings
        for name in dir(hub_settings):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(hub_settings, name))
