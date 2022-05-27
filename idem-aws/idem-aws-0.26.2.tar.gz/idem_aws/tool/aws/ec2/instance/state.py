"""
Contains functions that are useful for describing instances in a consistent manner
"""
import asyncio
from typing import Any
from typing import Dict
from typing import Tuple


async def convert_to_present(
    hub, ctx, describe_instances: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert instances from ec2.describe_instances() to aws.ec2.instance.present states

    This is the preferred "meta" function for collecting information about multiple instances
    """
    result = {}
    coros = []
    for reservation in describe_instances.get("Reservations", []):
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            result[instance_id] = dict(
                name=instance_id,
                resource_id=instance_id,
                image_id=instance.get("ImageId"),
                instance_type=instance.get("InstanceType"),
                block_device_mappings=instance.get("BlockDeviceMappings"),
                ebs_optimized=instance.get("EbsOptimized"),
                kernel_id=instance.get("KernelId"),
                placement=instance.get("Placement"),
                subnet_id=instance.get("SubnetId"),
                network_interfaces=instance.get("NetworkInterfaces"),
                private_ip_address=instance.get("PrivateIpAddress"),
                monitoring_enabled=instance.get("Monitoring", {}).get("State")
                == "enabled",
                root_device_name=instance.get("RootDeviceName"),
                product_codes=instance.get("ProductCodes"),
                source_dest_check=instance.get("SourceDestCheck"),
                running=instance.get("State", {}).get("Name") == "running",
                reservation_id=reservation.get("ReservationId"),
                owner_id=reservation.get("OwnerId"),
                bootstrap=[],
            )

            coros.append(
                # launch_template config get most parameters for an instance
                hub.tool.aws.ec2.instance.state.config(ctx, instance_id=instance_id)
            )

    # This can be a heavy process if there are many instances, use coroutines to collect them all at simultaneously
    for ret in asyncio.as_completed(coros):
        instance_id, config = await ret
        result[instance_id].update(config)

    return hub.tool.aws.ec2.instance.data.sanitize_dict(result)


async def config(hub, ctx, *, instance_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Retrieves the configuration data of the specified instance.

    This action calls on other describe actions to get instance information.
    Depending on your instance configuration, you may need to allow the following actions in your IAM policy:
        - DescribeSpotInstanceRequests
        - DescribeInstanceCreditSpecifications
        - DescribeVolumes
        - DescribeInstanceAttribute
        - DescribeElasticGpus.
    Or, you can allow describe* depending on your instance requirements.
    """
    config = {}
    response = await hub.exec.boto3.client.ec2.get_launch_template_data(
        ctx, InstanceId=instance_id
    )
    if response:
        hub.log.trace(
            f"Collecting instance '{instance_id}' config from launch template data"
        )
        # This is ideal and concise
        config.update(
            hub.tool.aws.ec2.instance.state.parse_launch_template_data(
                **response.ret["LaunchTemplateData"]
            )
        )
    else:
        # Maybe we lack permissions, or we are using localstack and get_launch_template_data is not implemented yet
        # Get that same information elsewhere
        hub.log.trace(f"Collecting instance '{instance_id}' config manually")
        config.update(
            await hub.tool.aws.ec2.instance.state.attributes(
                ctx, instance_id=instance_id
            )
        )

    # The following attributes are not part of the launch template data
    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="sriovNetSupport", InstanceId=instance_id
    )
    if ret:
        config["sriov_net_support"] = ret.ret["SriovNetSupport"].get("Value")

    # describing "enaSupport" is not supported by AWS yet
    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="enaSupport", InstanceId=instance_id
    )
    if ret:
        config["ena_support"] = ret.ret["EnaSupport"].get("Value")

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="ebsOptimized", InstanceId=instance_id
    )
    if ret:
        config["ebs_optimized"] = ret.ret["EbsOptimized"].get("Value")

    return instance_id, config


def parse_launch_template_data(hub, **launch_config) -> Dict[str, Any]:
    """
    Parse LaunchTemplateData to collect information about a single instance
    """
    return dict(
        image_id=launch_config.get("ImageId"),
        instance_type=launch_config.get("InstanceType"),
        user_data=launch_config.get("UserData"),
        disable_api_termination=launch_config.get("DisableApiTermination"),
        instance_initiated_shutdown_behavior=launch_config.get(
            "InstanceInitiatedShutdownBehavior"
        ),
        block_device_mappings=launch_config.get("BlockDeviceMappings"),
        ebs_optimized=launch_config.get("EbsOptimized"),
        enclave_options_enabled=launch_config.get("EnclaveOptions", {}).get("Enabled"),
        kernel_id=launch_config.get("KernelId"),
        ram_disk_id=launch_config.get("RamDiskId"),
        monitoring_enbaled=launch_config.get("Monitoring", {}).get("Enabled"),
        network_interfaces=launch_config.get("NetworkInterfaces"),
        tags={
            tag["Key"]: tag.get("Value")
            for tag in launch_config.get("TagSpecifications", {}).get("Tags", [])
        },
        placement=launch_config.get("Placement"),
        elastic_gpu_specifications=launch_config.get("ElasticGpuSpecifications"),
        elastic_inference_accelerators=launch_config.get(
            "ElasticInferenceAccelerators"
        ),
        security_group_ids=launch_config.get("SecurityGroupIds"),
        instance_market_options=launch_config.get("InstanceMarketOptions"),
        credit_specification=launch_config.get("CreditSpecification"),
        cpu_options=launch_config.get("CpuOptions"),
        capacity_reservation_specification=launch_config.get(
            "CapacityReservationSpecification"
        ),
        license_specifications=launch_config.get("LicenseSpecifications"),
        hibernation_options=launch_config.get("HibernationOptions"),
        metadata_options=launch_config.get("MetadataOptions"),
        instance_requirements=launch_config.get("InstanceRequirements"),
        private_dns_name_options=launch_config.get("PrivateDnsNameOptions"),
        maintentance_options=launch_config.get("MaintenanceOptions"),
    )


async def attributes(hub, ctx, *, instance_id: str) -> Dict[str, Any]:
    """
    Manually collect information about a single instance
    """
    instance = {}

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="userData", InstanceId=instance_id
    )
    if ret:
        instance["user_data"] = ret.ret["UserData"]

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="disableApiTermination", InstanceId=instance_id
    )
    if ret:
        instance["disable_api_termination"] = ret.ret["DisableApiTermination"].get(
            "Value"
        )

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="instanceInitiatedShutdownBehavior", InstanceId=instance_id
    )
    if ret:
        instance["instance_initiated_shutdown_behavior"] = ret.ret[
            "InstanceInitiatedShutdownBehavior"
        ].get("Value")

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="enclaveOptions", InstanceId=instance_id
    )
    if ret:
        # This is not supported by AWS yet
        instance["enclave_options"] = ret.ret["EnclaveOptions"]["Enabled"]

    ret = await hub.exec.boto3.client.ec2.describe_instance_attribute(
        ctx, Attribute="ramdisk", InstanceId=instance_id
    )
    if ret:
        instance["ram_disk_id"] = ret.ret["RamdiskId"]

    ret = await hub.exec.boto3.client.ec2.describe_tags(
        ctx,
        Filters=[
            {"Name": "resource-id", "Values": [instance_id]},
        ],
    )
    if ret:
        instance["tags"] = {tag["Key"]: tag.get("Value") for tag in ret.ret["Tags"]}

    # TODO these are available in launch_config and need to be collected manually too
    #    security_group_ids = launch_config["SecurityGroupIds"]
    #    instance_market_options = launch_config["InstanceMarketOptions"]
    #    credit_specification = launch_config["CreditSpecification"]
    #    cpu_options = launch_config["CpuOptions"]
    #    capacity_reservation_specification = launch_config["CapacityReservationSpecification"]
    #    license_specifications = launch_config["LicenseSpecifications"]
    #    hibernation_options = launch_config["HibernationOptions"]
    #    metadata_options = launch_config["MetadataOptions"]
    #    instance_requirements = launch_config["InstanceRequirements"]
    #    private_dns_name_options = launch_config["PrivateDnsNameOptions"]
    #    maintentance_options = launch_config["MaintenanceOptions"]
    return instance


async def get(
    hub, ctx, *, instance_id: str = None, client_token: str = None
) -> Dict[str, Any]:
    """
    Get the state of a single instance from the conversion to present

    This is the preferred "meta" function for collecting information about a single instance
    """
    if instance_id:
        ret = await hub.exec.boto3.client.ec2.describe_instances(
            ctx, InstanceIds=[instance_id]
        )
    elif client_token:
        ret = await hub.exec.boto3.client.ec2.describe_instances(
            ctx, Filters=[dict(Name="client-token", Values=[client_token])]
        )
    else:
        raise ValueError("Must specify either 'instance_id' or 'client_token'")

    if not ret.result:
        return {}

    present_states = await hub.tool.aws.ec2.instance.state.convert_to_present(
        ctx, ret.ret
    )
    if not present_states:
        return {}

    # There will only be one result from "convert_to_present", return it as a plain dictionary
    state = next(iter((present_states).values()))

    if "old_state" in ctx:
        # Check for completed bootstrap calls, this can change when heist can detect existing services
        # Unlike all the other attributes of a state, this can only come from ctx for now
        state["bootstrap"] = (ctx.old_state or {}).get("bootstrap", [])
    else:
        state["bootstrap"] = []

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
