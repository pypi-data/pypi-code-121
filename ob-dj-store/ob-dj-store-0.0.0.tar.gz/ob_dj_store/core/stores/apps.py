from django.apps import AppConfig
from django.core.checks import register
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores import settings_validation


class StoresConfig(AppConfig):
    name = "ob_dj_store.core.stores"
    verbose_name = _("Stores")

    def ready(self):
        import ob_dj_store.core.stores.receivers  # noqa F401

        register(settings_validation.required_installed_apps)
