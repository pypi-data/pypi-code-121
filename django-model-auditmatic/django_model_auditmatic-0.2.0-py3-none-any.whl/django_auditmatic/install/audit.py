"""
    install audit command
"""
from django.apps import apps

from django_auditmatic.configuration.data_classes import ConfiguredNames
from django_auditmatic.configuration.utils import get_tenant_schemas_and_apps
from django_auditmatic.util import process_model_for_all_schemas


def install_audit():
    """
        installs the auditing triggers and such for the configured models.
    :return:
    """

    # debug = settings.AUDITMATIC.get("debug", False)
    tenant_schemas, schema_apps = get_tenant_schemas_and_apps()

    configured_names = ConfiguredNames.from_settings()

    for model in apps.get_models():
        process_model_for_all_schemas(
            model,
            configured_names,
            schema_apps,
            tenant_schemas,
        )
