from django.apps import AppConfig
from django.db.models.signals import post_migrate

from django_tenants.management import create_default_tenant


class DjangoTenantsConfig(AppConfig):
    name = 'django_tenants'
    verbose_name = "Django tenants"

    def ready(self):
        post_migrate.connect(create_default_tenant, sender=self)
