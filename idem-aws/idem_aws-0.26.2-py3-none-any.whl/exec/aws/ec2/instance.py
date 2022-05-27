import pathlib

from Cryptodome.PublicKey import RSA


async def bootstrap(
    hub,
    ctx,
    instance_id,
    username: str = None,
    host: str = None,
    ssh_public_key: str = None,
    ssh_private_key: str = None,
    availability_zone: str = None,
    *,
    heist_manager: str,
    artifact_version: str = None,
    **kwargs,
):
    """
    Connect to the instance with an ssh keypair and call heist to bootstrap it.
    If an ssh keypair is not provided one will be created.

    Args:
        hub:
        ctx:
        instance_id: An AWS EC2 Instance ID
        username(Text, Optional): The instance OS username to use in the connection, Defaults to ec2-user
        host(Text, Optional): The public ip address or dns name of the instance.  Defaults to autodetect
        ssh_public_key(Text, Optional): A public ssh key or path to send to the instance
        ssh_private_key(Text, Optional): A private ssh key or path to send to the instance
        availability_zone(Text, Optional): The Availability Zone in which the EC2 instance was launched
        heist_manager(Text, Required): The heist manager to use to bootstrap the instance (I.E. salt.minion)
        artifact_version(Text, Optional): The version of the heist_manager's artifact to upload to the instance, Defaults to latest

    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": Dict}

    Examples:

        .. code-block:: bash

            idem exec aws.ec2.instance.bootstrap <instance_id> heist_manager="salt.minion"

    """
    result = dict(comment=(), result=True, ret=None)

    if bool(ssh_public_key) is not bool(ssh_private_key):
        result["comment"] += (
            "Both a private ssh key and a public ssh key must be specified",
        )
        result["result"] = False
        return result

    if not (ssh_public_key and ssh_private_key):
        result["comment"] += (
            f"Created a keypair to bootstrap instance with {heist_manager}",
        )
        key_pair = RSA.generate(2048)
        ssh_public_key = key_pair.publickey().export_key("OpenSSH")
        ssh_private_key = key_pair.export_key("PEM")

    # Create an instance resource object to use for defaults
    instance = hub.tool.boto3.resource.create(ctx, "ec2", "Instance", instance_id)

    # Verify the public key
    public_key_path = pathlib.Path(ssh_public_key)
    # If the ssh_public_key was a path, then read the contents of that path into a variable
    if public_key_path.exists():
        ssh_public_key = public_key_path.read_text()

    # Verify the private key
    private_key_path = pathlib.Path(ssh_private_key)
    if private_key_path.exists():
        ssh_private_key = private_key_path.read_bytes()
    else:
        ssh_private_key = ssh_private_key.encode()

    # Verify the host address
    if host is None:

        # Default to the public ip address and fall back to the public dns name
        host = instance.public_ip_address or instance.public_dns_name

    # Verify the username
    if username is None:
        # This is a safe bet for most official AMIs except Windows, Debian, Ubuntu, and Bitnami
        username = "ec2-user"
        # TODO, can we do more intelligent username guessing based on the AMI?
        #     https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html
        #     It can probably come from UserData on the instance...

    # Verify the availability zone
    if availability_zone is None:
        availability_zone = instance.placement["AvailabilityZone"]

    # Connect to the ec2 instance with the public key, connection will be available for 60 seconds
    connection_ret = (
        await hub.exec.boto3.client.ec2_instance_connect.send_ssh_public_key(
            ctx,
            InstanceId=instance_id,
            InstanceOSUser=username,
            SSHPublicKey=ssh_public_key,
            AvailabilityZone=availability_zone,
        )
    )

    result["result"] &= connection_ret.result & connection_ret.ret["Success"]
    if not result["result"]:
        result["comment"] += (
            f"Failed to connect to instance {instance_id}",
            f"InstanceConnect RequestId: {connection_ret.ret['RequestId']}",
            connection_ret.comment,
        )
        return result

    remotes = {
        instance_id: dict(
            host=host,
            username=username,
            client_keys=[ssh_private_key],
            **kwargs,
        ),
        "bootstrap": True,
    }

    await hub.heist[heist_manager].run(
        remotes=remotes, artifact_version=artifact_version
    )

    result["comment"] += (
        f"Successfully bootstrapped instance '{instance_id}' with '{heist_manager}'",
    )

    return result
