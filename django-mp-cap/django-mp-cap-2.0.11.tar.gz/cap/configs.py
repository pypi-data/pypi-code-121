
from suit.apps import DjangoSuitConfig

from django.conf import settings


class SuitConfig(DjangoSuitConfig):

    menu = getattr(settings, 'ADMIN_MENU', [])

    layout = getattr(settings, 'ADMIN_LAYOUT', 'vertical')

    menu_show_home = getattr(settings, 'ADMIN_MENU_SHOW_HOME', True)

    form_submit_on_right = False
