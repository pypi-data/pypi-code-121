async def lookup(hub, ctx, name: str, service: str, resource: str, filter: str = "[]"):
    """
    A state to look up a resource that is not managed.
    It's data will be available to other states via the arg_bind requisite interface.

    :param hub:
    :param ctx:
    :param name: The name of the state
    :param service: The name of the service under the boto3 client to use
    :param resource: The name of the collection under the service to search
    :param filter: A JMESPath

    .. code-block:: sls

        my_unmanaged_resource:
            aws.data.lookup:
                service: ec2
                resource: vpc
                filter: *[]
    """
    ret = dict(comment="", old_state={}, new_state={}, name=name, result=True)
    resource = await hub.exec.aws.data.lookup(
        ctx, service=service, resource=resource, filter=filter
    )
    ret["comment"] = resource.comment
    ret["result"] = resource.result
    ret["old_state"] = resource.ret
    ret["new_state"] = resource.ret
    return ret
