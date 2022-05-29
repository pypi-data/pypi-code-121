from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class JoyoussyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'joyoussync'
    label = 'joyoussync'
    verbose_name = _("Calendar sync for joyous")
