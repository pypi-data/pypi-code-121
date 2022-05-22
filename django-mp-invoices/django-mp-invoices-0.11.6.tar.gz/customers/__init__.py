
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CustomersAppConfig(AppConfig):

    name = 'customers'
    verbose_name = _('Customers')


default_app_config = 'customers.CustomersAppConfig'
