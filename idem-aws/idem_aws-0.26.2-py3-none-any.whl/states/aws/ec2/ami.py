import copy
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    kernel_id: str = None,
    image_location: str = None,
    architecture: str = None,
    block_device_mappings: List = None,
    description: str = None,
    ena_support: bool = None,
    billing_products: List = None,
    ramdisk_id: str = None,
    root_device_name: str = None,
    sriov_net_support: str = None,
    virtualization_type: str = None,
    boot_mode: str = None,
    tags: List = None,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""

    Register an AWS AMI.

    Args:
        name(Text):
            A region-unique name for the AMI.
            Constraints: 3-128 alphanumeric characters, parentheses (()), square brackets ([]), spaces ( ), periods (.),
            slashes (/), dashes (-), single quotes ('), at-signs (@), or underscores(_)

        resource_id(Text, optional):
            AWS AMI image_id

        image_location(Text, optional):
            The full path to your AMI manifest in Amazon S3 storage.
            The specified bucket must have the aws-exec-read canned access control list (ACL) to ensure that it can be accessed by Amazon EC2.
            For more information, see Canned ACLs in the Amazon S3 Service Developer Guide .

        architecture(Text, optional):
            The architecture of the AMI. Default: For Amazon EBS-backed AMIs, i386.
            For instance store-backed AMIs, the architecture specified in the manifest file.

        block_device_mappings(List, optional):
            The block device mapping entries.
            If you specify an Amazon EBS volume using the ID of an Amazon EBS snapshot, you can't specify the encryption state of the volume.
            If you create an AMI on an Outpost, then all backing snapshots must be on the same Outpost or in the Region of that Outpost.
            AMIs on an Outpost that include local snapshots can be used to launch instances on the same Outpost only.
            For more information, Amazon EBS local snapshots on Outposts in the Amazon Elastic Compute Cloud User Guide.

            Below are the attributes available for block device mapping entries:
            Type: object dict(Describes a block device mapping, which defines the EBS volumes and instance store volumes to attach to an instance at launch.)

            DeviceName (Text):
            The device name (for example, /dev/sdh or xvdh ).

            VirtualName (Text, Optional):
            The virtual device name (ephemeral N). Instance store volumes are numbered starting from 0.
            An instance type with 2 available instance store volumes can specify mappings for ephemeral0 and ephemeral1 .
            The number of available instance store volumes depends on the instance type. After you connect to the instance, you must mount the volume.
            NVMe instance store volumes are automatically enumerated and assigned a device name. Including them in your block device mapping has no effect.
            Constraints: For M3 instances, you must specify instance store volumes in the block device mapping for the instance.
            When you launch an M3 instance, we ignore any instance store volumes specified in the block device mapping for the AMI.

            Ebs (Dict):
            Parameters used to automatically set up EBS volumes when the instance is launched.

            DeleteOnTermination (bool, Optional):
            Indicates whether the EBS volume is deleted on instance termination. For more information,
            see Preserving Amazon EBS volumes on instance termination in the Amazon EC2 User Guide .

            Iops (Integer, Optional):
            The number of I/O operations per second (IOPS). For gp3 , io1 , and io2 volumes,
            this represents the number of IOPS that are provisioned for the volume. For gp2 volumes,
            this represents the baseline performance of the volume and the rate at which the volume accumulates I/O credits for bursting.

            The following are the supported values for each volume type:

            gp3 : 3,000-16,000 IOPS
            io1 : 100-64,000 IOPS
            io2 : 100-64,000 IOPS
            For io1 and io2 volumes, we guarantee 64,000 IOPS only for Instances built on the Nitro System.
            Other instance families guarantee performance up to 32,000 IOPS.

            This parameter is required for io1 and io2 volumes. The default for gp3 volumes is 3,000 IOPS.
            This parameter is not supported for gp2 , st1 , sc1 , or standard volumes.

            SnapshotId (Text):
            The ID of the snapshot.

            VolumeSize (Integer):
            The size of the volume, in GiBs. You must specify either a snapshot ID or a volume size.
            If you specify a snapshot, the default is the snapshot size.
            You can specify a volume size that is equal to or larger than the snapshot size.

            The following are the supported volumes sizes for each volume type:

            gp2 and gp3 :1-16,384
            io1 and io2 : 4-16,384
            st1 and sc1 : 125-16,384
            standard : 1-1,024

            VolumeType (Text):
            The volume type. For more information, see Amazon EBS volume types in the Amazon EC2 User Guide .
            If the volume type is io1 or io2 , you must specify the IOPS that the volume supports.

            KmsKeyId (Text, Optional):
            Identifier (key ID, key alias, ID ARN, or alias ARN) for a customer managed CMK under which the EBS volume is encrypted.
            This parameter is only supported on BlockDeviceMapping objects called by RunInstances, RequestSpotFleet, and RequestSpotInstances .

            Throughput (Integer, Optional):
            The throughput that the volume supports, in MiB/s.
            This parameter is valid only for gp3 volumes.
            Valid Range: Minimum value of 125. Maximum value of 1000.

            OutpostArn (Text, Optional):
            The ARN of the Outpost on which the snapshot is stored.

            Encrypted (bool, Optional):
            Indicates whether the encryption state of an EBS volume is changed while being restored from a backing snapshot.
            The effect of setting the encryption state to true depends on the volume origin (new or from a snapshot),
            starting encryption state, ownership, and whether encryption by default is enabled. For more information,
            see Amazon EBS encryption in the Amazon EC2 User Guide .
            In no case can you remove encryption from an encrypted volume.
            Encrypted volumes can only be attached to instances that support Amazon EBS encryption.
            For more information, see Supported instance types .
            This parameter is not returned by DescribeImageAttribute .

            NoDevice (Text, Optional):
            To omit the device from the block device mapping, specify an empty string.
            When this property is specified, the device is removed from the block device mapping regardless of the assigned value.

        description(Text, optional):
            A description for your AMI.

        ena_support(Boolean, optional):
            Set to true to enable enhanced networking with ENA for the AMI and any instances that you launch from the AMI.
            This option is supported only for HVM AMIs.
            Specifying this option with a PV AMI can make instances launched from the AMI unreachable.

        kernel_id (Text, optional):
            The ID of the kernel.

        billing_products (List, optional):
            The billing product codes. Your account must be authorized to specify billing product codes.
            Otherwise, you can use the Amazon Web Services Marketplace to bill for the use of an AMI.

        ramdisk_id (Text, optional):
            The ID of the RAM disk.

        root_device_name (Text, optional):
            The device name of the root device volume (for example, /dev/sda1 ).

        sriov_net_support (Text, optional):
            Set to simple to enable enhanced networking with the Intel 82599 Virtual Function interface for the AMI and any instances that you launch from the AMI.
            There is no way to disable sriovNetSupport at this time.
            This option is supported only for HVM AMIs. Specifying this option with a PV AMI can make instances launched from the AMI unreachable.

        virtualization_type (Text, optional):
            The type of virtualization (hvm | paravirtual).
            Default: paravirtual

        boot_mode (Text, optional):
            The boot mode of the AMI. For more information, see Boot modes in the Amazon Elastic Compute Cloud User Guide.

        tags(List, optional):
            The tags to assign to the AMI. Defaults to None.
                * Key (Text) -- The key of the tag. Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws: .
                * Value (Text) -- The value of the tag. Tag values are case-sensitive and accept a maximum of 255 Unicode characters.

    Request Syntax:
       [ami-resource-id]:
         aws.ec2.ami.present:
            - name: 'string'
            - image_location: 'string'
            - architecture: 'i386'|'x86_64'|'arm64'|'x86_64_mac'
            - block_device_mappings:
            - DeviceName: 'string'
                VirtualName: 'string'
                    Ebs:
                      DeleteOnTermination: True|False
                      Iops: 123
                      SnapshotId: 'string'
                      VolumeSize: integer
                      VolumeType': 'standard'|'io1'|'io2'|'gp2'|'sc1'|'st1'|'gp3'
                      KmsKeyId: 'string'
                      Throughput: integer
                      OutpostArn: 'string'
                      Encrypted: True|False
                NoDevice: 'string'
            - description: 'string'
            - ena_support: True|False
            - kernel_id: 'string'
            - billing_products
                - 'string'
                - 'string'
            - ramdisk_id: 'string'
            - root_device_name: 'string'
            - sriov_net_support: 'string'
            - virtualization_type: 'string'
            - boot_mode: 'legacy-bios'|'uefi'
            - tags:
                - Key: 'string'
                  Value: 'string'
            - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            idem-test-ami:
              aws.ec2.ami.present:
              - name: amzn-ami-vpc-nat-2018.03.0.20210721.0-x86_64-ebs
              - resource_id: ami-00a36856283d67c39
              - image_location: amazon/amzn-ami-vpc-nat-2018.03.0.20210721.0-x86_64-ebs
              - architecture: x86_64
              - kernel_id: None
              - block_device_mappings:
                - DeviceName: /dev/xvda
                  Ebs:
                    DeleteOnTermination: false
                    SnapshotId: snap-1833745e
                    VolumeSize: 15
                    VolumeType: standard
              - description: Amazon Linux AMI 2018.03.0.20210721.0 x86_64 VPC HVM ebs
              - ramdisk_id: ari-1a2b3c4d
              - root_device_name: /dev/xvda
              - virtualization_type: hvm
              - tags:
                - Key: Name
                  Value: ami-name
                - Key: ami-tag-key-2
                  Value: ami-tag-value-2
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False

    desired_state = {
        "name": name,
        "image_location": image_location,
        "architecture": architecture,
        "kernel_id": kernel_id,
        "block_device_mappings": block_device_mappings,
        "description": description,
        "ena_support": ena_support,
        "billing_products": billing_products,
        "ramdisk_id": ramdisk_id,
        "root_device_name": root_device_name,
        "sriov_net_support": sriov_net_support,
        "virtualization_type": virtualization_type,
        "boot_mode": boot_mode,
        "tags": tags,
    }

    ami_args = {
        "Name": name,
        "ImageLocation": image_location,
        "Architecture": architecture,
        "KernelId": kernel_id,
        "BlockDeviceMappings": block_device_mappings,
        "Description": description,
        "EnaSupport": ena_support,
        "BillingProducts": billing_products,
        "RamdiskId": ramdisk_id,
        "RootDeviceName": root_device_name,
        "SriovNetSupport": sriov_net_support,
        "VirtualizationType": virtualization_type,
        "BootMode": boot_mode,
    }

    if resource_id:
        response = await hub.exec.boto3.client.ec2.describe_images(
            ctx, ImageIds=[resource_id]
        )
        if not response["result"]:
            result["comment"] = response["comment"]
            result["result"] = response["result"]
            return result
        if response["ret"].get("Images"):
            before = response["ret"].get("Images")[0]

    if before:

        result[
            "old_state"
        ] = hub.tool.aws.ec2.conversion_utils.convert_raw_ami_to_present(
            raw_resource=before
        )
        plan_state = copy.deepcopy(result["old_state"])

        # update (we can only update tags and description)
        if tags is not None:
            # Update tags
            update_ret = await hub.exec.aws.ec2.tag.update_tags(
                ctx=ctx,
                resource_id=resource_id,
                old_tags=result["old_state"].get("tags"),
                new_tags=tags,
            )
            result["result"] = update_ret["result"]
            result["comment"] = update_ret["comment"]

            # If tag updates fails, it wont update description
            if not result["result"]:
                return result
            resource_updated = bool(update_ret["ret"])
            if ctx.get("test", False) and update_ret["ret"]:
                plan_state["tags"] = update_ret["ret"].get("tags")

        if (
            description is not None
            and result["old_state"].get("description") != description
        ):
            if ctx.get("test", False):
                plan_state["description"] = description
                resource_updated = True
            else:
                # update with actual aws
                update_ret = await hub.exec.boto3.client.ec2.modify_image_attribute(
                    ctx, Description={"Value": description}, ImageId=resource_id
                )
                result["result"] = result["result"] and update_ret["result"]
                result["comment"] = result["comment"] + (
                    (f"Update description: {description}",)
                    if result["result"]
                    else update_ret["comment"]
                )

                # If description update fails
                if not result["result"]:
                    return result

                resource_updated = resource_updated or bool(update_ret["ret"])

        if resource_updated:
            if ctx.get("test", False):
                result["comment"] = (f"Would update aws.ec2.ami '{name}'",) + result[
                    "comment"
                ]
            else:
                result["comment"] = (f"Updated aws.ec2.ami '{name}'",) + result[
                    "comment"
                ]
    else:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state=desired_state,
            )

            result["comment"] = (f"Would create aws.ec2.ami '{name}'",)
            return result

        # response for register_image is {'ImageId': 'string'}
        ret = await hub.exec.boto3.client.ec2.register_image(ctx, **ami_args)
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result
        resource_id = ret["ret"]["ImageId"]
        result["comment"] = (f"Created aws.ec2.ami '{name}'",)

        if tags is not None:
            ret = await hub.exec.boto3.client.ec2.create_tags(
                ctx, Resources=[resource_id], Tags=tags
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + ret["comment"]
    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            response = await hub.exec.boto3.client.ec2.describe_images(
                ctx, ImageIds=[resource_id]
            )
            after = response["ret"].get("Images")[0]
            result[
                "new_state"
            ] = hub.tool.aws.ec2.conversion_utils.convert_raw_ami_to_present(
                raw_resource=after
            )
        else:
            result["comment"] = (f"aws.ec2.ami '{name}' already exists",)
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False

    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    r"""

    Deregisters the specified AMI. After you deregister an AMI, it can't be used to launch new instances.

    If you deregister an AMI that matches a Recycle Bin retention rule,
    the AMI is retained in the Recycle Bin for the specified retention period.
    For more information, see Recycle Bin in the Amazon Elastic Compute Cloud User Guide.

    When you deregister an AMI, it doesn't affect any instances that you've already launched from the AMI.
    You'll continue to incur usage costs for those instances until you terminate them.

    When you deregister an Amazon EBS-backed AMI,
    it doesn't affect the snapshot that was created for the root volume of the instance during the AMI creation process.
    When you deregister an instance store-backed AMI,
    it doesn't affect the files that you uploaded to Amazon S3 when you created the AMI.

    Args:
        name(Text): The Idem name of the AMI.
        resource_id(Text, optional): The AWS image_id.

    Request Syntax:
       [ami-resource-id]:
              aws.ec2.ami.absent:
              - name: 'string'
              - resource_id: 'string'

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            idem-test-ami:
              aws.ec2.ami.absent:
                - name: idem-test-ami
                - resource_id:ami-000c540e28953ace2
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = (f"aws.ec2.ami '{name}' already absent",)
        return result

    before = await hub.exec.boto3.client.ec2.describe_images(
        ctx, ImageIds=[resource_id]
    )

    if not before["result"]:
        result["comment"] = before["comment"]
        result["result"] = False
        return result

    if not before["ret"].get("Images"):
        result["comment"] = (f"aws.ec2.ami '{name}' already absent",)
    else:
        result[
            "old_state"
        ] = hub.tool.aws.ec2.conversion_utils.convert_raw_ami_to_present(
            raw_resource=before["ret"].get("Images")[0]
        )

        if ctx.get("test", False):
            result["comment"] = (f"Would delete aws.ec2.ami '{name}'",)
            return result

        ret = await hub.exec.boto3.client.ec2.deregister_image(ctx, ImageId=resource_id)
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
        else:
            result["comment"] = (f"Deleted aws.ec2.ami '{name}'",)

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Describe the resource in a way that can be recreated/managed with the corresponding "present" function

    Gets information about the AWS AMI

    Returns:
        Dict[str, Dict[str, Any]]

    Examples:

        .. code-block:: bash

            $ idem describe aws.ec2.ami

    """
    result = {}
    ret = await hub.exec.boto3.client.ec2.describe_images(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe AMI {ret['comment']}")
        return {}

    for image in ret["ret"].get("Images"):
        resource_id = image.get("ImageId")
        resource_translated = (
            hub.tool.aws.ec2.conversion_utils.convert_raw_ami_to_present(
                raw_resource=image
            )
        )
        result[resource_id] = {
            "aws.ec2.ami.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource_translated.items()
            ]
        }

    return result


async def search(
    hub,
    ctx,
    name,
    filters: List = None,
    resource_id: str = None,
    executable_users: List = None,
    owners: List = None,
    include_deprecated: bool = False,
    most_recent: bool = True,
):
    """
    Use an un-managed AMI as a data-source. Supply one of the inputs as the filter.

    Args:
        name(Text):
            The name of the Idem state.

        resource_id(Text, optional):
            AWS image id to identify the resource.

        executable_users(list, optional):
            Scopes the images by users with explicit launch permissions.
            Specify an Amazon Web Services account ID, self (the sender of the request), or all (public AMIs).

        owners(list, optional):
            Scopes the results to images with the specified owners.
            You can specify a combination of Amazon Web Services account IDs, self , amazon , and aws-marketplace.
            If you omit this parameter, the results include all images for which you have launch permissions, regardless of ownership.

        include_deprecated(bool, optional):
            If true , all deprecated AMIs are included in the response.
            If false , no deprecated AMIs are included in the response. If no value is specified, the default value is false .

        most_recent(bool, optional):
            If more than one result is returned, use the most recent AMI.

        filters(list, optional):
            One or more filters: for example, tag :<key>, tag-key. A complete list of filters can be found at
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_images


    Request Syntax:
        [Idem-state-name]:
          aws.ec2.ami.search:
          - resource_id: 'string'
          - executable_users
            - user1
          - owners
            - amazon
          - include_deprecated: True|False
          - most_recent: True|False
          - filters:
            - name: 'string'
              values: 'list'
            - name: 'string'
              values: 'list'

        Examples:

            my-unmanaged-ami:
              aws.ec2.ami.search:
                - resource_id: value
                - most_recent: False
                - filters:
                    - name: 'name'
                      values: ["amzn-ami-minimal-hvm-2018.03.0.20181129-x86_64-ebs_2"]
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    syntax_validation = hub.tool.aws.search_utils.search_filter_syntax_validation(
        filters=filters
    )
    if not syntax_validation["result"]:
        result["comment"] = syntax_validation["comment"]
        return result
    boto3_filter = hub.tool.aws.search_utils.convert_search_filter_to_boto3(
        filters=filters
    )

    ami_args = {}
    if boto3_filter:
        ami_args["Filters"] = boto3_filter
    if resource_id:
        ami_args["ImageIds"] = [resource_id]
    if executable_users:
        ami_args["ExecutableUsers"] = executable_users
    if owners:
        ami_args["Owners"] = owners
    if include_deprecated:
        ami_args["IncludeDeprecated"] = include_deprecated

    ret = await hub.exec.boto3.client.ec2.describe_images(ctx, **ami_args)

    if not ret["result"]:
        result["result"] = False
        result["comment"] = ret["comment"]
        return result

    if not ret["ret"]["Images"]:
        result["result"] = False
        result["comment"] = (f"Unable to find aws.ec2.ami '{name}'",)
        return result

    resource = ret["ret"]["Images"][0]
    if len(ret["ret"]["Images"]) > 1:
        if most_recent:
            ret["ret"]["Images"].sort(
                key=lambda x: datetime.strptime(
                    x.get("CreationDate"), "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                reverse=True,
            )
            resource = ret["ret"]["Images"][0]
        else:
            result["comment"] = (
                f'More than one aws.ec2.ami resource was found. Use resource {resource.get("ImageId")}',
            )

    result["old_state"] = hub.tool.aws.ec2.conversion_utils.convert_raw_ami_to_present(
        raw_resource=resource
    )
    # Populate both "old_state" and "new_state" with the same data
    result["new_state"] = copy.deepcopy(result["old_state"])
    return result
