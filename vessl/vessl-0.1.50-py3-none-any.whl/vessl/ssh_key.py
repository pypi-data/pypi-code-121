import os
from typing import List

from openapi_client.models import ResponseSSHKeyInfo
from openapi_client.models.ssh_key_create_api_input import SSHKeyCreateAPIInput
from vessl import vessl_api


def list_ssh_keys() -> List[ResponseSSHKeyInfo]:
    """List ssh public keys.

    Example:
        ```python
        vessl.list_ssh_keys()
        ```
    """
    return vessl_api.s_sh_key_list_api().ssh_keys


def create_ssh_key(
    key_path: str, key_name: str, ssh_public_key_value: str
) -> ResponseSSHKeyInfo:
    """Create a SSH public key.

    Args:
        key_path(str): SSH public key path.
        key_name(str): SSH public key name,
        ssh_public_key_value(str): SSH public key value.

    Example:
        ```python
        vessl.create_ssh_key(
            key_path="/Users/johndoe/.ssh/id_ed25519.pub",
            key_name="john@abcd.com",
            ssh_public_key_value="ssh-public-key-value",
        )
        ```
    """
    return vessl_api.s_sh_key_create_api(
        ssh_key_create_api_input=SSHKeyCreateAPIInput(
            filename=os.path.basename(key_path),
            name=key_name,
            public_key=ssh_public_key_value,
        )
    )


def delete_ssh_key(key_id: int) -> object:
    """Delete the ssh public key.

    Args:
        key_id(int): Key ID.

    Example:
        ```python
        vessl.delete_ssh_key(
            key_id=123456,
        )
        ```
    """
    return vessl_api.s_sh_key_delete_api(ssh_key_id=key_id)
