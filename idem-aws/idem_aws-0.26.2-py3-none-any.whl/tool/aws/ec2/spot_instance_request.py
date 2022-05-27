"""
Contains functions that are useful for describing instances in a consistent manner
"""
from typing import Any
from typing import Dict


async def convert_to_present(
    hub, describe_spot_instance_requests: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert instances from ec2.describe_spot_instance_requests() to aws.ec2.spot_instance_requests.present states

    This is the preferred "meta" function for collecting information about multiple instances
    """
    result = {}
    for spot_instance_request in describe_spot_instance_requests[
        "SpotInstanceRequests"
    ]:
        resource_id = spot_instance_request["SpotInstanceRequestId"]
        result[resource_id] = dict(
            name=resource_id,
            resource_id=resource_id,
            launch_specification=spot_instance_request.get("LaunchSpecification"),
            spot_price=spot_instance_request.get("SpotPrice"),
            type=spot_instance_request.get("Type"),
            tags=spot_instance_request.get("Tags"),
            availability_zone_group=spot_instance_request.get(
                "LaunchedAvailabilityZone"
            ),
            valid_until=spot_instance_request.get("ValidUntil"),
            instance_interruption_behavior=spot_instance_request.get(
                "InstanceInterruptionBehavior"
            ),
            # These don't appear in describe spot_instance_requests; can only be specified on creation
            instance_count=None,
            launch_group=None,
            valid_from=None,
        )
    return result


async def get(hub, ctx, *, resource_id: str) -> Dict[str, Any]:
    """
    Get the state of a single spot_instance_request from the conversion to present

    This is the preferred "meta" function for collecting information about a single instance
    """
    ret = await hub.exec.boto3.client.ec2.describe_spot_instance_requests(
        ctx, SpotInstanceRequestIds=[resource_id]
    )

    if not ret:
        return {}

    present_states = await hub.tool.aws.ec2.spot_instance_request.convert_to_present(
        ret.ret
    )
    if not present_states:
        return {}

    # There will only be one result from "convert_to_present", return it as a plain dictionary
    state = next(iter((present_states).values()))
    return state


def test(hub, **kwargs) -> Dict[str, Any]:
    """
    Compute the state based on the parameters passed to an instance.present function for ctx.test
    """
    result = {}
    for k, v in kwargs.items():
        # Ignore kwargs that were None
        if v is None:
            continue
        result[k] = v
    return result
