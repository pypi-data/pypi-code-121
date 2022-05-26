
from suit.apps import DjangoSuitConfig

from django.conf import settings


class SuitConfig(DjangoSuitConfig):

    menu = getattr(settings, 'ADMIN_MENU', [])

    layout = getattr(settings, 'ADMIN_LAYOUT', 'vertical')

    form_submit_on_right = False
