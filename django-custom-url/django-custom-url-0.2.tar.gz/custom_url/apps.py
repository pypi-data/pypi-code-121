from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomUrlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_url'
    verbose_name = _('Custom URL')
