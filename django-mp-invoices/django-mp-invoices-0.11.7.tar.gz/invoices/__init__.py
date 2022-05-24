
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


def setup_settings(settings, is_prod, **kwargs):

    settings['CSS_COMPONENTS'] = {
        'invoices': [
            'invoices/invoices.css'
        ],
        **settings.get('CSS_COMPONENTS', {})
    }

    settings['JS_COMPONENTS'] = {
        'invoices': [
            'deleteaction.js',
            'cellinput.js',
            'list.js',
            'modal.js',
            'invoices/jquery.scannerdetection.js',
            'invoices/SelectProductList.js',
            'invoices/InvoiceList.js',
            'invoices/InvoiceTotal.js',
            'invoices/CategoryTree.js',
            'invoices/ContactChoiceField.js',
            'invoices/SelectServiceItemList.js',
        ],
        **settings.get('JS_COMPONENTS', {})
    }

    settings['MIDDLEWARE'] += ['invoices.middleware.InvoicesMiddleware']

    settings['INSTALLED_APPS'] += [
        app for app in [
            'notify',
            'managers',
            'invoice_products'
        ] if app not in settings['INSTALLED_APPS']
    ]


class InvoicesConfig(AppConfig):

    name = 'invoices'
    verbose_name = _("Invoices")

    is_online_sale_enabled = False


default_app_config = 'invoices.InvoicesConfig'
