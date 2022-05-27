from typing import Any
from typing import Dict

import pop.contract


def client(hub, path: str, context):
    """
    Get an AWS service client based on the path and call an operation on it
    idem will automatically populate credentials from acct in the client.

    The calls mirror the namespacing of boto3.client and have the same parameters

    If a response can be paginated, the full result will be asynchronously collected and returned.

    path::

        boto3.client.[service_name].[operation] [kwargs="values"]

    Examples:
        In these examples will use the service_name of "ec2" and operation of "create_vpc"

        Call from the CLI
        .. code-block: bash

            $ idem exec boto3.client.ec2.create_vpc CidrBlock="10.0.0.0/24"

        Call from code
        .. code-block: python

            await hub.exec.boto3.client.ec2.create_vpc(ctx, CidrBlock="10.0.0.0/24")

    :param hub:
    :param path: client.[service_name].[function_name]
    :param context: None
    :return: The result of the call
    """
    c, service_name, operation = path.split(".", maxsplit=2)
    assert c == "client"

    async def _client_caller(ctx, *args, **kwargs) -> Dict[str, Any]:
        result = {"comment": (), "ret": None, "result": True}
        try:
            if operation.endswith(".search"):
                resource = operation.split(".")[0]
                ret = await hub.tool.boto3.client.search(
                    ctx, service_name, resource, *args, **kwargs
                )
                result["result"] = bool(ret)
                result["ret"] = ret
                result["comment"] = (f"Searched in {service_name}.{resource}",)
            else:
                ret: Dict[str, Any] = await hub.tool.boto3.client.exec(
                    ctx, service_name, operation, *args, **kwargs
                )
                if hasattr(ret, "keys"):
                    keys = sorted(ret.keys())
                else:
                    keys = []
                result["comment"] = tuple(keys)
                result["ret"] = ret
                result["result"] = bool(ret)
        except Exception as e:
            result["result"] = False
            result["comment"] = (f"{e.__class__.__name__}: {e}",)
        return result

    return pop.contract.ContractedAsync(
        hub,
        contracts=[],
        func=_client_caller,
        ref=path,
        name=operation,
        implicit_hub=False,
    )


def resource(hub, path: str, context):
    """
    Get an AWS service resource based on the path.
    If the path includes an operation then a resource is created with the args which runs the operation with the kwargs
    If the path does not include an operation then pass args and kwargs to the resource class and return details

    The calls mirror the namespacing of boto3.resource and have the same parameters

    Examples:
        Call from the CLI
        -----------------

        .. code-block: bash

            $ idem exec boto3.resource.ec2.Vpc.create_subnet vpc-71d00419 CidrBlock="10.0.0.0/24"

        Call from code
        --------------
        You can make the same call from within code:

        .. code-block: python

            # ret will do error catching and format the response as an ExecReturn
            ret = await hub.exec.boto3.ec2.Vpc.create_subnet("vpc-71d00419", CidrBlock="10.0.0.0/24")

        More control and better performance come from using the underlying tools directly, like so:

        .. code-block: python

            # resource will be reusable for more operation calls
            resource = hub.tool.boto3.resource.create(ctx, "Vpc", id="vpc-71d00419")

            # ret will contain the raw result of the operation call
            ret = await hub.tool.boto3.resource.exec(resource, "create_subnet", CidrBlock="10.0.0.0/24")

    :param hub:
    :param path: client.[service_name].[function_name]
    :param context: None
    :return: The data retrieved from the given resource path
    """
    r, service_name, resource_class = path.split(".", maxsplit=2)
    assert r == "resource"

    if "." in resource_class:
        resource_class, operation = resource_class.split(".")
    else:
        operation = None

    async def _resource_caller(ctx, *args, **kwargs):
        result = {"comment": (), "ret": None, "result": True}
        try:
            if operation == "id":
                # Return the first id that matches the given kwargs
                ret = await hub.tool.boto3.resource.id(
                    ctx,
                    service_name=service_name,
                    collection=f"{resource_class}s",
                    *args,
                    **kwargs,
                )
                result["comment"] = (
                    f"Searched for id in {service_name}.{resource_class}",
                )
                result["ret"] = ret
                result["result"] = bool(ret)
            elif operation:
                # There's a function call to make on this resource
                # Run the operation with the given parameters
                resource_ = hub.tool.boto3.resource.create(
                    ctx, service_name, resource_class, *args
                )
                result["ret"] = await hub.tool.boto3.resource.exec(
                    resource_, operation, **kwargs
                )
                result["comment"] = (f"{resource_.__class__.__name__}.{operation}",)
            else:
                # The path ends with the resource name describe it with the given parameters
                resource_ = hub.tool.boto3.resource.create(
                    ctx, service_name, resource_class, *args, **kwargs
                )
                # Return raw information about the object
                result["ret"] = hub.tool.boto3.resource.dict(resource_)
                result["comment"] = (resource_.__class__.__name__,)
        except Exception as e:
            result["result"] = False
            result["comment"] = (f"{e.__class__.__name__}: {e}",)

        return result

    return pop.contract.ContractedAsync(
        hub,
        contracts=[],
        func=_resource_caller,
        ref=path,
        name=resource_class,
        implicit_hub=False,
    )
