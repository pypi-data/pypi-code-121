
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProductsAppConfig(AppConfig):

    name = 'products'
    verbose_name = _('Products')


default_app_config = 'products.ProductsAppConfig'
