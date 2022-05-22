
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


def setup_settings(settings, **kwargs):

    settings['INSTALLED_APPS'] += [
        app for app in [
            'supplier_products',
            'ordered_model',
            'djckeditor'
        ] if app not in settings['INSTALLED_APPS']
    ]


class SuppliersAppConfig(AppConfig):

    name = 'suppliers'
    verbose_name = _('Suppliers')


default_app_config = 'suppliers.SuppliersAppConfig'
