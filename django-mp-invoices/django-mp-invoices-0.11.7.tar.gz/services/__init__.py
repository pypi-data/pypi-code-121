
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


def setup_settings(settings, is_prod, **kwargs):

    settings['MIDDLEWARE'] += ['services.middleware.ServicesMiddleware']


class ServicesConfig(AppConfig):
    name = 'services'
    verbose_name = _("Services")


default_app_config = 'services.ServicesConfig'
