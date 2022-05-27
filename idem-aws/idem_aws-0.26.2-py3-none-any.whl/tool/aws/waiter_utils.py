from typing import Dict


def create_waiter_config(
    hub, default_delay: int, default_max_attempts: int, timeout_config: Dict or None
) -> Dict[str, int]:
    """
    Create a waiter configuration that can be used as input in boto3 waiter calls. The configuration is based on
    the default values and the customized value in timeout_config.

    Args:
        hub: The redistributed pop central hub.
        default_delay: The amount of time in seconds to wait between attempts.
        default_max_attempts: The maximum number of attempts to be made.
        timeout_config: Customized timeout configuration containing delay and max attempts.

    Returns:
        {"Delay": delay-time, "MaxAttempts": max-attempts}
    """
    result = {"Delay": default_delay, "MaxAttempts": default_max_attempts}
    if timeout_config:
        if "delay" in timeout_config:
            result["Delay"] = timeout_config["delay"]
        if "max_attempts" in timeout_config:
            result["MaxAttempts"] = timeout_config["max_attempts"]
    return result
