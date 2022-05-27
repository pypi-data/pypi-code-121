async def gather(hub, profiles):
    """
    load profiles from unencrypted AWS credential files

    Example:
    .. code-block:: yaml

        aws:
          profile_name:
            region_name: us-west-1
            endpoint_url: localhost:992
            aws_access_key_id: my_key_id
            aws_secret_access_key: my_key
            aws_session_token: my_token
    """
    sub_profiles = {}

    for profile, ctx in profiles.get("aws", {}).items():
        sub_profiles[profile] = ctx

    return sub_profiles
