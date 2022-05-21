from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class A2faConfig(AppConfig):
    name = "j2fa"
    verbose_name = _("2-Factor Authentication")
    default_auto_field = "django.db.models.AutoField"
