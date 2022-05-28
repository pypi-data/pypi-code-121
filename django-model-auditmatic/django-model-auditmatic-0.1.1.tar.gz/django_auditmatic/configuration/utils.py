from typing import List, Optional, Tuple

from django.apps import apps
from django.conf import settings


def find_schemas() -> Optional[List[str]]:
    """
        find all schemas by querying the tenant's schema names.
    :return: List[str]
    """
    if not hasattr(settings, "TENANT_MODEL"):
        return None

    tenant_model_setting = settings.TENANT_MODEL
    split_tenant_model = tenant_model_setting.split(".")
    tenant_model_name = split_tenant_model[-1]
    tenant_model = None
    for model in apps.get_models():
        # print(dir(model))
        # print(model._meta.model_name, tenant_model_setting)
        if model._meta.model_name == tenant_model_name:
            tenant_model = model
    if not tenant_model:
        return None
    return tenant_model.objects.values_list("schema_name", flat=True)


def get_tenant_schemas_and_apps() -> Tuple[List, List]:
    """
        process tenant configuration if tenants are in use.
    :return:
    """
    tenant_schemas = find_schemas()
    schema_apps = []
    if tenant_schemas and len(tenant_schemas) > 0:
        if not hasattr(settings, "TENANT_APPS"):
            raise RuntimeError(
                "Detected tenant model but no apps configured for TENANT_APPS setting."
            )
        schema_apps = settings.TENANT_APPS
    return tenant_schemas, schema_apps
