import pathlib

import boto3.session
import botocore.exceptions
from dict_tools.data import NamespaceDict

try:
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    session = boto3.session.Session()
    services = hub.OPT.pop_create.services or session.get_available_services()
    ctx.servers = [None]

    # We already have an acct plugin
    ctx.has_acct_plugin = False
    ctx.service_name = "aws_auto"

    # Initialize cloud spec
    ctx.cloud_spec = NamespaceDict(
        api_version="",
        project_name=ctx.project_name,
        service_name=ctx.service_name,
        request_format={
            "present": hub.pop_create.aws.template.PRESENT_REQUEST_FORMAT,
            "absent": hub.pop_create.aws.template.ABSENT_REQUEST_FORMAT,
            "describe": hub.pop_create.aws.template.DESCRIBE_REQUEST_FORMAT,
        },
        plugins={},
    )

    # This takes a while because we are making http calls to aws
    for service in tqdm.tqdm(services):
        try:
            plugins = hub.pop_create.aws.plugin.parse(session, service)
        except botocore.exceptions.UnknownServiceError as err:
            plugins = {}
            hub.log.error(f"{err.__class__.__name__}: {err}")

        ctx.cloud_spec.plugins = plugins

        # Generate the exec modules for this specific service
        hub.cloudspec.init.run(
            ctx,
            directory,
            create_plugins=["state_modules"],
        )

    ctx.cloud_spec.plugins = {}
    return ctx
