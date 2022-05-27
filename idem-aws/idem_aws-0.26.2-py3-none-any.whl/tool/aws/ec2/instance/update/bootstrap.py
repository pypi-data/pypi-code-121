from typing import Dict
from typing import List
from typing import Tuple


async def apply(
    hub,
    ctx,
    resource,
    *,
    old_value: Tuple[Dict[str, str]],
    new_value: Tuple[Dict[str, str]],
    comments: List[str],
) -> bool:
    """
    Bootstrap an instance if hasn't been bootstrapped already with the methods in "new_value"

    Args:
        hub:
        ctx: The ctx from a state module call
        resource: An ec2 instance resource object
        old_value: The previous value from the attributes of an existing instance
        new_value: The desired value from the ec2 instance present state parameters
        comments: A running list of comments abound the update process
    """
    result = True

    # There is currently no way to "undo" bootstrapping with heist
    # We only need to check for bootstrapping that hasn't been completed according to ESM
    for bootstrap_options in new_value:
        heist_manager = bootstrap_options["heist_manager"]

        if heist_manager in old_value:
            comments += [f"Already bootstrapped aws.ec2.instance with {heist_manager}"]
            continue
        elif ctx.test:
            comments += [f"Would bootstrap aws.ec2.instance with {heist_manager}"]
            continue
        else:
            bootstrap_ret = await hub.exec.aws.ec2.instance.bootstrap(
                ctx, resource.id, **bootstrap_options
            )
            result &= bootstrap_ret["result"]

    return result
