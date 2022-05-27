__contracts__ = ["soft_fail"]


async def lookup(hub, ctx, service: str, resource: str, filter: str = "*[]"):
    """
    Return the first match to the JMESPath filter on the named resource type.

    :param hub:
    :param ctx:
    :param service: The name of the service under the boto3 client to use
    :param resource: The name of the collection under the service to search
    :param filter: A JMESPath

    .. code-block:: bash

        $ idem exec aws.data.lookup service=ec2 resource=vpc filter="*[?CidrBlock==10.0.0.0/24]"
    """
    ret = dict(comment="", result=True, ret=None)
    resource = await hub.pop.loop.wrap(
        hub.tool.boto3.client.search,
        ctx,
        service_name=service,
        collection=resource,
        jmes_path=filter,
    )
    if not resource:
        ret["result"] = False
        ret["comment"] = f"Could not find '{service}.{resource}' with filter: {filter}"
    else:
        ret["comment"] = f"Found resource '{service}.{resource}'"
        ret["ret"] = resource
    return ret
