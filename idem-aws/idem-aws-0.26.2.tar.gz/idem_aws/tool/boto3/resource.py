from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import boto3.resources.factory
import boto3.session

__func_alias__ = {"exec_": "exec", "dict_": "dict", "id_": "id"}


def create(
    hub,
    ctx,
    service_name: str,
    resource_class: str,
    *args,
    **resource_kwargs: Dict[str, Any],
) -> boto3.resources.factory.ServiceResource:
    """
    Create a boto3 resource class

    :param hub:
    :param ctx:
    :param service_name: The name of the service to get from boto3
    :param resource_class: The name of the resource class to get from the service
    :param resource_kwargs: kwargs to pass to the resource class creation

    :return:
    """
    session: boto3.session.Session = hub.tool.boto3.session.get(
        # Resources are not thread safe, use a brand new session
        botocore_session=None
    )
    resource: boto3.resources.factory.ResourceFactory = session.resource(
        service_name=service_name,
        region_name=ctx.acct.get("region_name"),
        api_version=ctx.acct.get("api_version"),
        use_ssl=ctx.acct.get("use_ssl", True),
        endpoint_url=ctx.acct.get("endpoint_url"),
        aws_access_key_id=ctx.acct.get("aws_access_key_id"),
        aws_secret_access_key=ctx.acct.get("aws_secret_access_key"),
        aws_session_token=ctx.acct.get("aws_session_token"),
        verify=ctx.acct.get("verify"),
    )

    # Don't pass kwargs that have a "None" value to the function call
    kwargs = {k: v for k, v in resource_kwargs.items() if v is not None}

    hub.log.debug(f"Getting resource {service_name}.{resource_class}")
    cls: boto3.resources.factory.ResourceHandler = getattr(resource, resource_class)
    if callable(cls):
        return cls(*args, **kwargs)
    else:
        return cls


class ResourceDict(dict):
    """
    Helper when outputting details of a resource class on the CLI
    """

    def __init__(self, resource: boto3.resources.factory.ServiceResource):
        super().__init__()
        self.resource = resource
        for i in self.resource.meta.identifiers:
            self[i] = getattr(self.resource, i)

    def __getattr__(self, item):
        return self.resource.__getattribute__(item)


def dict_(hub, resource: boto3.resources.factory.ServiceResource):
    # Helper on the hub for creating a resource dict
    return ResourceDict(resource)


async def exec_(
    hub,
    resource: boto3.resources.factory.ServiceResource,
    operation: str,
    *op_args,
    **op_kwargs: Dict[str, Any],
):
    """
    Call an operation on an existing resource

    :param hub:
    :param resource: The resource to call
    :param operation: The name of the operation to call on the resource
    :param op_args: Args to pass to the operation
    :param op_kwargs: Kwargs to pass to the operation
    :return:
    """
    # Don't pass kwargs that have a "None" value to the function call
    kwargs = {k: v for k, v in op_kwargs.items() if v is not None}

    hub.log.debug(f"Getting resource {resource}.{operation}")
    op = getattr(resource, operation)
    if callable(op):
        # It's a function, run it asynchronously
        return await hub.pop.loop.wrap(op, *op_args, **kwargs)
    else:
        # It's an attribute
        return op


async def describe(hub, resource: boto3.resources.factory.ServiceResource):
    """
    Describe a boto3 resource

    :param hub:
    :param resource: The resource to call

    :return:
    """
    try:
        await hub.pop.loop.wrap(resource.load)
    except hub.tool.boto3.exception.ClientError as e:
        hub.log.debug(f"{resource} does not exist")
        return {}

    return resource.meta.data


async def id_(hub, ctx, service_name: str, collection: str, **kwargs) -> str:
    """
    Find the ID of a resource that matches the given kwargs in a collection
    :param hub:
    :param ctx:
    :param service_name: The name of the service to get from boto3
    :param collection: The name of the collection to search under the resource
    :param kwargs: The kwargs to pass to the filter function
    :return:
    """
    session: boto3.session.Session = hub.tool.boto3.session.get(
        # Resources are not thread safe, use a brand new session
        botocore_session=None
    )

    resource: boto3.resources.factory.ResourceFactory = session.resource(
        service_name=service_name,
        region_name=ctx.acct.get("region_name"),
        api_version=ctx.acct.get("api_version"),
        use_ssl=ctx.acct.get("use_ssl", True),
        endpoint_url=ctx.acct.get("endpoint_url"),
        aws_access_key_id=ctx.acct.get("aws_access_key_id"),
        aws_secret_access_key=ctx.acct.get("aws_secret_access_key"),
        aws_session_token=ctx.acct.get("aws_session_token"),
        verify=ctx.acct.get("verify"),
    )

    assert any(
        collection == c.name for c in resource.meta.resource_model.collections
    ), f"Service {service_name} has no collection '{collection}: {','.join(resource.meta.resource_model.collections)}'"
    collected = getattr(resource, collection)

    iterator = await hub.pop.loop.wrap(
        collected.filter,
        MaxResults=5,
        DryRun=ctx.get("test", False),
        Filters=[
            {"Name": k, "Values": v if isinstance(v, (List, Tuple)) else [v]}
            for k, v in kwargs.items()
        ],
    )

    try:
        first = next(iter(iterator))
        return first.id
    except StopIteration:
        return ""
