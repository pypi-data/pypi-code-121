def is_pending(hub, ret: dict, state: str = None) -> bool:
    """
    This method enables state specific implementation of is_pending logic,
    based on resource specific attribute(s).
    Usage 'idem state <sls-file> --reconciler=basic --pending=aws'

    :param hub: The hub
    :param ret: The returned dictionary of the last run
    :param state: The name of the state
    :return: True | False
    """

    if (
        state is not None
        and hub.states[state] is not None
        and callable(getattr(hub.states[state], "is_pending", None))
    ):
        return hub.states[state].is_pending(ret=ret)
    else:
        # Default is_pending
        return not ret["result"] is True or bool(ret["changes"])
