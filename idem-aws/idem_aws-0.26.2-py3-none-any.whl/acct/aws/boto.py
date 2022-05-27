from typing import Any
from typing import Dict


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    Get profile names from encrypted AWS credential files.
    Standardize the profile keys to what a boto3 Client requires

    Example:
    .. code-block:: yaml

        aws.boto:
          profile_name:
            id: XXXXXXXXXXXXXXXXX
            key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            region: us-east-1
    """
    sub_profiles = {}
    for profile, ctx in profiles.get("aws.boto", {}).items():
        # Add a boto session to the ctx for exec and state modules
        # Strip any args that were used for authentication
        # Boto uses the default account if none was specified
        sub_profiles[profile] = ctx
    return sub_profiles
