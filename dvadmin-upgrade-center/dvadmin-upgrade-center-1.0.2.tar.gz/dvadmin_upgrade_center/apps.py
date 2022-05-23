from django.apps import AppConfig


class UpgradeCenterBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dvadmin_upgrade_center'
    url_prefix = "upgrade_center_backend"
