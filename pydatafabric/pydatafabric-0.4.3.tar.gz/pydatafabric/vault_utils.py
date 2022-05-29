import hvac


def get_secrets(mount_point, path, parse_data=True):
    vault_client = hvac.Client()
    data = vault_client.secrets.kv.v2.read_secret_version(
        mount_point=mount_point, path=path
    )
    if parse_data:
        data = data["data"]["data"]
    return data
