from django.apps import apps as django_apps
from django_tenants import app_settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection


def get_tenant():
    tenant = connection.tenant
    if tenant is None:
        raise Exception("No tenant configured in db connection, connection.tenant is none")
    # model = get_tenant_model()
    # return tenant if isinstance(tenant, model) else model(schema_name=tenant.schema_name)
    return tenant


def get_tenant_model():
    """
    Return the Tenant model that is active in this project.
    """
    try:
        return django_apps.get_model(app_settings.TENANT_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "TENANT_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "TENANT_MODEL refers to model '%s' that has not been installed"
            % app_settings.TENANT_MODEL
        )


def get_domain_model():
    """
    Return the Tenant model that is active in this project.
    """
    try:
        return django_apps.get_model(app_settings.DOMAIN_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "DOMAIN_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "DOMAIN_MODEL refers to model '%s' that has not been installed"
            % app_settings.DOMAIN_MODEL
        )
