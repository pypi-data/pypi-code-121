from importlib import import_module
from django.conf import settings

from django_tenants import app_settings
from django_tenants.backends.postgresql.schema import RLSDatabaseSchemaEditor

ORIGINAL_BACKEND = getattr(settings, 'ORIGINAL_BACKEND', 'django.db.backends.postgresql')

original_backend = import_module(ORIGINAL_BACKEND + '.base')


class DatabaseWrapper(original_backend.DatabaseWrapper):
    SchemaEditorClass = RLSDatabaseSchemaEditor

    def __init__(self, *args, **kwargs):
        self.tenant = None
        super().__init__(*args, **kwargs)

    def set_tenant(self, tenant):
        self.tenant = tenant

    def _cursor(self, name=None):
        cursor = super(DatabaseWrapper, self)._cursor(name=name)  # NOQA

        cursor.execute(f'SET picatron.administration_tenant = {app_settings.MAIN_TENANT_ID}')

        if self.tenant:
            cursor.execute(f'SET picatron.active_tenant = {self.tenant.pk}')
        else:
            cursor.execute(f'SET picatron.active_tenant = {app_settings.MAIN_TENANT_ID}')

        return cursor


class FakeTenant:
    """
    We can't import any db model in a backend (apparently?), so this class is used
    for wrapping schema names in a tenant-like structure.
    """
    def __init__(self):
        self.is_main = True
