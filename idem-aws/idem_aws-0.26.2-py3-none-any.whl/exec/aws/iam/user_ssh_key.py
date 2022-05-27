from typing import Any
from typing import Dict


async def get_ssh_key_if_attached_to_user(
    hub, ctx, user_name: str, ssh_public_key_id: str
) -> Dict[str, Any]:
    """
    Check if ssh_public_key_id is already associated to this user. If already associated
    return the metadata of ssh public key. If not associated return {} in ret.

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        user_name: The name (friendly name, not ARN) of the IAM user
        ssh_public_key_id(Text): The SSH public key ID

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}
    """
    result = dict(comment=(), result=True, ret=None)
    user_ssh_public_keys_list = await hub.exec.boto3.client.iam.list_ssh_public_keys(
        ctx, UserName=user_name
    )
    if user_ssh_public_keys_list.get("result"):
        attached_user_ssh_public_keys_list = user_ssh_public_keys_list["ret"].get(
            "SSHPublicKeys"
        )
        if attached_user_ssh_public_keys_list:
            for ssh_public_key in attached_user_ssh_public_keys_list:
                if ssh_public_key.get("SSHPublicKeyId") == ssh_public_key_id:
                    result["ret"] = ssh_public_key
                    break
    else:
        result["comment"] = user_ssh_public_keys_list["comment"]
        result["result"] = False
    return result
