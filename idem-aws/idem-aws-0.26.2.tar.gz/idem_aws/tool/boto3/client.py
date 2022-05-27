import asyncio
import re
from typing import Any
from typing import Dict
from typing import Generator

import boto3.session

ITERATION_FINISHED = object()

__func_alias__ = {"exec_": "exec"}


async def exec_(
    hub,
    ctx,
    service_name: str,
    operation: str,
    jmes_search_path: str = None,
    *op_args,
    **op_kwargs: Dict[str, Any],
) -> Any:
    """
    :param hub:
    :param ctx:
    :param service_name: The name of the service client to create
    :param operation: The operation to run from the service client
    :param jmes_search_path: The JMES path to use as a filter for paginated results
    :param op_args: arguments to pass to the operation call
    :param op_kwargs: keyword arguments to pass to the operation call

    :return: The result of the operation call
    """
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(
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
    kwargs = {k: v for k, v in op_kwargs.items() if v is not None}

    can_paginate = client.can_paginate(operation)

    if can_paginate:
        hub.log.debug(f"Paginating results for {service_name}.{operation}")
        paginator = client.get_paginator(operation)
        pages = paginator.paginate(*op_args, **kwargs)
        if jmes_search_path is None:
            return await hub.pop.loop.wrap(pages.build_full_result)
        else:
            iterator = await hub.pop.loop.wrap(pages.search, jmes_search_path)
            return [_ for _ in iterator]
    else:
        hub.log.debug(f"Getting raw results for {service_name}.{operation}")
        op = getattr(client, operation)
        return await hub.pop.loop.wrap(op, *op_args, **kwargs)


def get_client(hub, ctx, service_name: str):
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(
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
    return client


async def wait(
    hub,
    ctx,
    service_name: str,
    waiter_name: str,
    custom_waiter=None,
    delay: int = None,
    *wt_args,
    **wt_kwargs,
) -> None:
    """
    Asynchronously wait for the named resource to be available

    :param hub:
    :param ctx:
    :param service_name: The name of the service client to retrieve
    :param waiter_name: The name of the waiter to get from the service client
    :param custom_waiter: If an inbuilt waiter is not available , we can provide custom waiter for the service client
    :param delay: The delay in seconds before starting the waiter
    :param wt_args: Args to pass to the wait function
    :param wt_kwargs: kwargs to pass to the wait function
    """

    if custom_waiter is not None:
        waiter = custom_waiter

        if waiter is None:
            raise NameError(f"No custom waiter object defined for '{waiter_name}'. ")
    else:
        client = hub.tool.boto3.client.get_client(ctx, service_name)

        if waiter_name not in client.waiter_names:
            raise NameError(
                f"No waiter '{waiter_name}'. "
                f"Available waiters for '{service_name}' are: {' '.join(client.waiter_names)}"
            )

        waiter = client.get_waiter(waiter_name)

    if delay is not None:
        # There might be some delay for the resource to start updating/deleting after the api call
        hub.log.debug(f"Waiting '{delay}' seconds, before starting the waiter")
        await asyncio.sleep(delay)

    await hub.pop.loop.wrap(waiter.wait, *wt_args, **wt_kwargs)


def search(hub, ctx, service_name: str, collection: str, jmes_path: str = "*[]") -> str:
    """
    :param hub:
    :param ctx:
    :param service_name:
    :param collection:
    :param jmes_path:
    :return:
    """
    session: boto3.session.Session = hub.tool.boto3.session.get()
    client = session.client(
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

    # Find a paginator that can describe this collection
    for operation in client.meta.method_to_api_mapping:
        if client.can_paginate(operation) and re.match(
            f"[a-z]+_{collection.lower()}s?$", operation
        ):
            break
    else:
        raise AttributeError(
            f"Could not find a paginator for {service_name}.{collection}"
        )

    paginator = client.get_paginator(operation)
    pages = paginator.paginate()
    iterator: Generator = pages.search(jmes_path)
    try:
        return next(iterator, None)
    finally:
        iterator.close()
