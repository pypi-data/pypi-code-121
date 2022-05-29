import base64

from . import context
from agilicus.agilicus_api import (
    DesktopResource,
    DesktopResourceSpec,
    DesktopClientConfiguration,
    DesktopConnectionInfo,
    VNCConnectionInfo,
    VNCPasswordAuthentication,
)

from .input_helpers import build_updated_model
from .input_helpers import update_org_from_input_or_ctx
from .input_helpers import get_org_from_input_or_ctx
from .input_helpers import get_user_id_from_input_or_ctx
from .input_helpers import strip_none
from .output.table import (
    spec_column,
    format_table,
    metadata_column,
)


def list_desktop_resources(ctx, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    params = strip_none(kwargs)
    query_results = apiclient.app_services_api.list_desktop_resources(**params)
    return query_results.desktop_resources


def add_desktop_resource(ctx, read_write_password, read_only_password, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    spec = DesktopResourceSpec(**strip_none(kwargs))
    model = DesktopResource(spec=spec)
    _update_connection_info(
        model,
        read_write_password=read_write_password,
        read_only_password=read_only_password,
    )
    return apiclient.app_services_api.create_desktop_resource(model).to_dict()


def _update_connection_info(
    model: DesktopResource, read_write_password=None, read_only_password=None, **kwargs
):
    if (
        read_write_password is None and read_only_password is None
    ) or model.spec.desktop_type != "vnc":
        # nothing to do. Return the original
        return model.spec.connection_info

    conn_info = model.spec.connection_info or DesktopConnectionInfo()
    vnc_connection_info = conn_info.vnc_connection_info or VNCConnectionInfo()
    password_auth = (
        vnc_connection_info.password_authentication_info or VNCPasswordAuthentication()
    )

    if read_write_password is not None:
        password_auth.read_write_password = read_write_password

    if read_only_password is not None:
        password_auth.read_only_password = read_only_password

    vnc_connection_info.password_authentication_info = password_auth
    conn_info.vnc_connection_info = vnc_connection_info
    model.spec.connection_info = conn_info


def _get_desktop_resource(ctx, apiclient, resource_id, **kwargs):
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.get_desktop_resource(resource_id, **kwargs)


def show_desktop_resource(ctx, resource_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    return _get_desktop_resource(ctx, apiclient, resource_id, **kwargs).to_dict()


def delete_desktop_resource(ctx, resource_id, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    update_org_from_input_or_ctx(kwargs, ctx, **kwargs)
    return apiclient.app_services_api.delete_desktop_resource(resource_id, **kwargs)


def update_desktop_resource(
    ctx, resource_id, read_write_password, read_only_password, **kwargs
):
    apiclient = context.get_apiclient_from_ctx(ctx)
    get_args = {}
    update_org_from_input_or_ctx(get_args, ctx, **kwargs)
    mapping = _get_desktop_resource(ctx, apiclient, resource_id, **get_args)

    # This needs to run before the build_updated_model, because its check_type blows away
    # the types of nested objects, making them dicts.
    _update_connection_info(
        mapping,
        read_write_password=read_write_password,
        read_only_password=read_only_password,
    )

    # check_type=False works around nested types not deserializing correctly
    mapping.spec = build_updated_model(
        DesktopResourceSpec, mapping.spec, kwargs, check_type=False
    )
    return apiclient.app_services_api.replace_desktop_resource(
        resource_id, desktop_resource=mapping
    ).to_dict()


def create_desktop_client_config(ctx, desktop_resource_id, as_text, **kwargs):
    apiclient = context.get_apiclient_from_ctx(ctx)
    kwargs["org_id"] = get_org_from_input_or_ctx(ctx, **kwargs)
    kwargs["user_id"] = get_user_id_from_input_or_ctx(ctx, **kwargs)
    config = DesktopClientConfiguration(**strip_none(kwargs))
    result = apiclient.app_services_api.create_client_configuration(
        desktop_resource_id, desktop_client_configuration=config
    )

    cfg = result.generated_config.configuration_file
    if as_text:
        return base64.b64decode(cfg).decode()
    return cfg


def format_desktops_as_text(ctx, resources):
    columns = [
        metadata_column("id"),
        spec_column("org_id"),
        spec_column("name"),
        spec_column("address"),
        spec_column("desktop_type"),
        spec_column("session_type"),
        spec_column("connector_id"),
    ]

    return format_table(ctx, resources, columns)
