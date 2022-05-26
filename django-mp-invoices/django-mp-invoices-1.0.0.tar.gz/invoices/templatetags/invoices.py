
from django.apps import apps
from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.simple_tag
def get_sale_types():

    sale_model = apps.get_model('invoices', 'Sale')
    app_config = apps.get_app_config('invoices')

    sale_types = [
        {
            'code': sale_model.TYPE_CASH_REGISTER,
            'name': _('Cash register'),
            'color': 'success',
            'icon': 'money'
        },
        {
            'code': sale_model.TYPE_WRITE_OFF,
            'name': _('Write off'),
            'color': 'danger',
            'icon': 'remove'
        },
        {
            'code': sale_model.TYPE_IN_PROCESS,
            'name': _('In process'),
            'color': 'secondary',
            'icon': 'tasks'
        },
        {
            'code': sale_model.TYPE_DEBT,
            'name': _('Debt'),
            'color': 'info',
            'icon': 'download'
        }
    ]

    if app_config.is_online_sale_enabled:
        sale_types.append({
            'code': sale_model.TYPE_ONLINE,
            'name': _('Online'),
            'color': 'primary',
            'icon': 'wifi'
        })

    sale_types.append({
        'code': sale_model.TYPE_CUSTOM,
        'name': _('Custom'),
        'color': 'warning',
        'icon': 'list'
    })

    return sale_types


@register.simple_tag
def get_arrival_types():
    arrival_model = apps.get_model('invoices', 'Arrival')
    return [
        {
            'code': arrival_model.TYPE_INCOME,
            'name': _('Income'),
            'color': 'success',
            'icon': 'download'
        },
        {
            'code': arrival_model.TYPE_RETURN,
            'name': _('Return'),
            'color': 'danger',
            'icon': 'remove'
        },
        {
            'code': arrival_model.TYPE_CUSTOM,
            'name': _('Custom'),
            'color': 'warning',
            'icon': 'list'
        }
    ]
