from django.apps import AppConfig
from . import __version__


class BlacklistConfig(AppConfig):
    name = "blacklist"
    label = "blacklist"
    verbose_name = f"Blacklist v{__version__}"

    def ready(self):
        import blacklist.signals
