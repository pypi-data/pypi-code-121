from django.apps import AppConfig
from . import __version__


class IndyDashConfig(AppConfig):
    name = 'indydash'
    label = 'indydash'

    verbose_name = f"Industry Structures Dashboard v{__version__}"
