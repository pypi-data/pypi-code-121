"""
    install audit permission
"""
from django.apps import apps
from django.contrib.auth.models import Group

from django_auditmatic.configuration.data_classes import ConfiguredNames
from django_auditmatic.configuration.utils import get_tenant_schemas_and_apps
from django_auditmatic.permission import get_or_create_audit_permission
from django_auditmatic.util import get_model_names


def install_audit_permission() -> None:
    """
    install audit permission for configured models.
    :return: None
    """
    tenant_schemas, schema_apps = get_tenant_schemas_and_apps()
    group, _ = Group.objects.get_or_create(name="Any")
    configured_names = ConfiguredNames.from_settings()
    print("install audit permission")
    for model in apps.get_models():
        model_names = get_model_names(model, configured_names)
        if not model_names:
            continue

        if not len(schema_apps):  # pylint: disable=C1802
            print("install for model", model)
            perm = get_or_create_audit_permission(model)
            if configured_names.allow_any[model._meta.object_name.lower()]:
                group.permissions.add(perm)
