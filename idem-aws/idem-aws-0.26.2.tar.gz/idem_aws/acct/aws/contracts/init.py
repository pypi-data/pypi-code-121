from typing import Any
from typing import Dict

import botocore.config
import dict_tools.data


def sig_gather(hub, profiles) -> Dict[str, Any]:
    ...


async def post_gather(hub, ctx) -> Dict[str, Any]:
    """
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
    """
    profiles = ctx.ret or {}

    hub.log.info(f"Read {len(profiles)} profiles from {ctx.ref}")

    for name, profile in profiles.items():
        new_profile = _sanitize_profile(profile)
        if "assume_role" in profile:
            # Get new access credentials for the assumed role
            sts_ctx = dict_tools.data.NamespaceDict(acct=new_profile)

            assume_role_obj = profile.pop("assume_role", None)
            credentials = await hub.exec.aws.sts.assume_role.credentials(
                sts_ctx, **assume_role_obj
            )
            if not credentials.result:
                raise ConnectionError(credentials.comment)
            # Overwrite the credentials for the profile with the ones from the assumed role
            new_profile["aws_access_key_id"] = credentials.ret["AccessKeyId"]
            new_profile["aws_secret_access_key"] = credentials.ret["SecretAccessKey"]
            new_profile["aws_session_token"] = credentials.ret["SessionToken"]
        if "esm" in profile:
            new_profile["esm"] = profile["esm"]
        profiles[name] = new_profile

    return profiles


def _sanitize_profile(profile: Dict[str, str]) -> Dict[str, str]:
    config = profile.get("config", {})
    if isinstance(config, Dict):
        config = botocore.config.Config(**config)
    return dict(
        region_name=_key_options(profile, "region_name", "region", "location"),
        verify=profile.get("verify", None),
        use_ssl=profile.get("use_ssl", True),
        endpoint_url=_key_options(profile, "endpoint_url", "endpoint"),
        aws_access_key_id=_key_options(profile, "aws_access_key_id", "key_id", "id"),
        aws_secret_access_key=_key_options(
            profile, "aws_secret_access_key", "secret_access_key", "access_key", "key"
        ),
        aws_session_token=_key_options(
            profile, "aws_session_token", "session_token", "token", "key"
        ),
        config=config,
    )


def _key_options(d: Dict[str, Any], *keys):
    for key in keys:
        if key in d:
            return d[key]
    else:
        return None
