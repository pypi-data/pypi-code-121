from typing import Any
from typing import Dict


async def is_resource_updated(
    hub,
    before: Dict[str, Any],
    role_arn: str,
    recording_group: Dict,
):
    if role_arn != before.get("role_arn"):
        return True

    if recording_group != before.get("recording_group"):
        return True

    return False
