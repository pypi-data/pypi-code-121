from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = 'ssi_views'
    verbose_name = _('SSI Views')
