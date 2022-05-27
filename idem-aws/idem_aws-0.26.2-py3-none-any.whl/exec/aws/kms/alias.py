async def get_alias_by_name(hub, ctx, alias_name):
    """
    This function will take alias name as input
    and returns the metadata like target kms key, target arn about the alias name
    by searching in aliases.

    Args:
        hub:
        ctx:
        alias_name: alias name of the KMS key

    Returns:
        Dict[str, str]
    """
    ret = {}
    result = dict(comment="", result=True, ret=None)
    try:
        before = await hub.exec.boto3.client.kms.list_aliases(ctx)
        result["result"] = before["result"]
        result["comment"] = before["comment"]
        if before["result"] and before["ret"].get("Aliases"):
            for alias in before["ret"]["Aliases"]:
                if alias_name == alias.get("AliasName"):
                    ret = alias
                    break
        result["ret"] = ret
    except hub.tool.boto3.exception.ClientError as e:
        result["comment"] = f"{e.__class__.__name__}: {e}"
        result["result"] = False

    return result
