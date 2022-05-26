'''
# bastion

A set of constructs to create and access bastion hosts using SSO or IAM. By using session manager for shell access and GUI Connect for Windows RDP access, no ports need to be exposed to the internet and all access can be managed and audited through AWS services.

## Todo

* Allow choco installs
* fix aws cli not installing with winget
* Allow picking and choosing of services in the access policy
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_sso
import constructs


class BastionAccessPolicy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.BastionAccessPolicy",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        props = BastionAccessPolicyProps(security_tag=security_tag)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> aws_cdk.aws_iam.PolicyDocument:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.PolicyDocument, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: aws_cdk.aws_iam.PolicyDocument) -> None:
        jsii.set(self, "policy", value)


class BastionPermissionSet(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.BastionPermissionSet",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_arn: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        inline_policy: typing.Any = None,
        managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        relay_state_type: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_arn: The ARN of the SSO instance under which the operation will be executed. For more information about ARNs, see `Amazon Resource Names (ARNs) and AWS Service Namespaces <https://docs.aws.amazon.com//general/latest/gr/aws-arns-and-namespaces.html>`_ in the *AWS General Reference* .
        :param name: The name of the permission set.
        :param description: The description of the ``PermissionSet`` .
        :param inline_policy: The IAM inline policy that is attached to the permission set.
        :param managed_policies: A structure that stores the details of the IAM managed policy.
        :param relay_state_type: Used to redirect users within the application during the federation authentication process.
        :param session_duration: The length of time that the application user sessions are valid for in the ISO-8601 standard.
        :param tags: The tags to attach to the new ``PermissionSet`` .
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        props = BastionPermissionSetProps(
            instance_arn=instance_arn,
            name=name,
            description=description,
            inline_policy=inline_policy,
            managed_policies=managed_policies,
            relay_state_type=relay_state_type,
            session_duration=session_duration,
            tags=tags,
            security_tag=security_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="assign")
    def assign(
        self,
        account_id: builtins.str,
        principal_id: builtins.str,
        principal_type: builtins.str,
    ) -> None:
        '''
        :param account_id: -
        :param principal_id: -
        :param principal_type: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "assign", [account_id, principal_id, principal_type]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityTag")
    def security_tag(self) -> aws_cdk.Tag:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.Tag, jsii.get(self, "securityTag"))

    @security_tag.setter
    def security_tag(self, value: aws_cdk.Tag) -> None:
        jsii.set(self, "securityTag", value)


@jsii.implements(aws_cdk.aws_ec2.IInstance)
class LinuxBastion(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.LinuxBastion",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        package_manager: typing.Optional["LinuxPackageManager"] = None,
        packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param package_manager: (experimental) Package manager used for installing packages. Default: - dnf
        :param packages: (experimental) List of packages to be installed as part of the userdata using winget. Default: - []
        :param vpc: VPC to launch the instance in.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_type: Type of instance to launch. Default: - t3a.large
        :param machine_image: AMI to launch. Default: - latest windows server 2022 full base
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        props = LinuxBastionProps(
            package_manager=package_manager,
            packages=packages,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            block_devices=block_devices,
            instance_name=instance_name,
            instance_type=instance_type,
            machine_image=machine_image,
            private_ip_address=private_ip_address,
            role=role,
            security_group=security_group,
            user_data=user_data,
            security_tag=security_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> builtins.str:
        '''(experimental) The availability zone the instance was launched in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceAvailabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance's ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateDnsName")
    def instance_private_dns_name(self) -> builtins.str:
        '''(experimental) Private DNS name for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> builtins.str:
        '''(experimental) Private IP for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicDnsName")
    def instance_public_dns_name(self) -> builtins.str:
        '''(experimental) Publicly-routable DNS name for this instance.

        (May be an empty string if the instance does not have a public name).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicIp")
    def instance_public_ip(self) -> builtins.str:
        '''(experimental) Publicly-routable IP  address for this instance.

        (May be an empty string if the instance does not have a public IP).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "securityGroup"))


@jsii.enum(jsii_type="pwed-cdk.pwed_bastion.LinuxPackageManager")
class LinuxPackageManager(enum.Enum):
    '''
    :stability: experimental
    '''

    APT = "APT"
    '''
    :stability: experimental
    '''
    YUM = "YUM"
    '''
    :stability: experimental
    '''
    DNF = "DNF"
    '''
    :stability: experimental
    '''


class ScheduleShutdown(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.ScheduleShutdown",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        shutdown_schedule: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param shutdown_schedule: 
        :param timezone: 
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        props = ScheduleShutdownProps(
            shutdown_schedule=shutdown_schedule,
            timezone=timezone,
            security_tag=security_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.SecurityTagable",
    jsii_struct_bases=[],
    name_mapping={"security_tag": "securityTag"},
)
class SecurityTagable:
    def __init__(self, *, security_tag: typing.Optional[aws_cdk.Tag] = None) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_tag is not None:
            self._values["security_tag"] = security_tag

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityTagable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_ec2.IInstance)
class WindowsBastion(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="pwed-cdk.pwed_bastion.WindowsBastion",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        create_key_pair: typing.Optional[builtins.bool] = None,
        windows_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param create_key_pair: If a keypair should be created and saved into Secrets Manager. This can be used to get Administrator user access Default: - false
        :param windows_packages: (experimental) List of packages to be installed as part of the userdata using winget. Default: - no association
        :param vpc: VPC to launch the instance in.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_type: Type of instance to launch. Default: - t3a.large
        :param machine_image: AMI to launch. Default: - latest windows server 2022 full base
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        props = WindowsBastionProps(
            create_key_pair=create_key_pair,
            windows_packages=windows_packages,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            block_devices=block_devices,
            instance_name=instance_name,
            instance_type=instance_type,
            machine_image=machine_image,
            private_ip_address=private_ip_address,
            role=role,
            security_group=security_group,
            user_data=user_data,
            security_tag=security_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> builtins.str:
        '''(experimental) The availability zone the instance was launched in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceAvailabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''(experimental) The instance's ID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateDnsName")
    def instance_private_dns_name(self) -> builtins.str:
        '''(experimental) Private DNS name for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> builtins.str:
        '''(experimental) Private IP for this instance.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicDnsName")
    def instance_public_dns_name(self) -> builtins.str:
        '''(experimental) Publicly-routable DNS name for this instance.

        (May be an empty string if the instance does not have a public name).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePublicIp")
    def instance_public_ip(self) -> builtins.str:
        '''(experimental) Publicly-routable IP  address for this instance.

        (May be an empty string if the instance does not have a public IP).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "instancePublicIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "securityGroup"))


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.BastionAccessPolicyProps",
    jsii_struct_bases=[SecurityTagable],
    name_mapping={"security_tag": "securityTag"},
)
class BastionAccessPolicyProps(SecurityTagable):
    def __init__(self, *, security_tag: typing.Optional[aws_cdk.Tag] = None) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_tag is not None:
            self._values["security_tag"] = security_tag

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionAccessPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.BastionInstanceProps",
    jsii_struct_bases=[SecurityTagable],
    name_mapping={
        "security_tag": "securityTag",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "block_devices": "blockDevices",
        "instance_name": "instanceName",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "private_ip_address": "privateIpAddress",
        "role": "role",
        "security_group": "securityGroup",
        "user_data": "userData",
    },
)
class BastionInstanceProps(SecurityTagable):
    def __init__(
        self,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}
        :param vpc: VPC to launch the instance in.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_type: Type of instance to launch. Default: - t3a.large
        :param machine_image: AMI to launch. Default: - latest windows server 2022 full base
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
            "vpc_subnets": vpc_subnets,
        }
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''Where to place the instance within the VPC.

        :default: - Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''The name of the instance.

        :default: - CDK generated name
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Type of instance to launch.

        :default: - t3a.large
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''AMI to launch.

        :default: - latest windows server 2022 full base
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with an instance.

        Private IP should be available within the VPC that the instance is build within.

        :default: - no association
        '''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''An IAM role to associate with the instance profile assigned to this Auto Scaling Group.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:

        :default: - A role will automatically be created, it can be accessed via the ``role`` property

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''Security Group to assign to this instance.

        :default: - create new security group
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default:

        - A UserData object appropriate for the MachineImage's
        Operating System is created.
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.BastionPermissionSetProps",
    jsii_struct_bases=[
        aws_cdk.aws_sso.CfnPermissionSetProps, BastionAccessPolicyProps
    ],
    name_mapping={
        "instance_arn": "instanceArn",
        "name": "name",
        "description": "description",
        "inline_policy": "inlinePolicy",
        "managed_policies": "managedPolicies",
        "relay_state_type": "relayStateType",
        "session_duration": "sessionDuration",
        "tags": "tags",
        "security_tag": "securityTag",
    },
)
class BastionPermissionSetProps(
    aws_cdk.aws_sso.CfnPermissionSetProps,
    BastionAccessPolicyProps,
):
    def __init__(
        self,
        *,
        instance_arn: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        inline_policy: typing.Any = None,
        managed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        relay_state_type: typing.Optional[builtins.str] = None,
        session_duration: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.CfnTag]] = None,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
    ) -> None:
        '''
        :param instance_arn: The ARN of the SSO instance under which the operation will be executed. For more information about ARNs, see `Amazon Resource Names (ARNs) and AWS Service Namespaces <https://docs.aws.amazon.com//general/latest/gr/aws-arns-and-namespaces.html>`_ in the *AWS General Reference* .
        :param name: The name of the permission set.
        :param description: The description of the ``PermissionSet`` .
        :param inline_policy: The IAM inline policy that is attached to the permission set.
        :param managed_policies: A structure that stores the details of the IAM managed policy.
        :param relay_state_type: Used to redirect users within the application during the federation authentication process.
        :param session_duration: The length of time that the application user sessions are valid for in the ISO-8601 standard.
        :param tags: The tags to attach to the new ``PermissionSet`` .
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_arn": instance_arn,
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if inline_policy is not None:
            self._values["inline_policy"] = inline_policy
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if relay_state_type is not None:
            self._values["relay_state_type"] = relay_state_type
        if session_duration is not None:
            self._values["session_duration"] = session_duration
        if tags is not None:
            self._values["tags"] = tags
        if security_tag is not None:
            self._values["security_tag"] = security_tag

    @builtins.property
    def instance_arn(self) -> builtins.str:
        '''The ARN of the SSO instance under which the operation will be executed.

        For more information about ARNs, see `Amazon Resource Names (ARNs) and AWS Service Namespaces <https://docs.aws.amazon.com//general/latest/gr/aws-arns-and-namespaces.html>`_ in the *AWS General Reference* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-instancearn
        '''
        result = self._values.get("instance_arn")
        assert result is not None, "Required property 'instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the permission set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the ``PermissionSet`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inline_policy(self) -> typing.Any:
        '''The IAM inline policy that is attached to the permission set.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-inlinepolicy
        '''
        result = self._values.get("inline_policy")
        return typing.cast(typing.Any, result)

    @builtins.property
    def managed_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A structure that stores the details of the IAM managed policy.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-managedpolicies
        '''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def relay_state_type(self) -> typing.Optional[builtins.str]:
        '''Used to redirect users within the application during the federation authentication process.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-relaystatetype
        '''
        result = self._values.get("relay_state_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_duration(self) -> typing.Optional[builtins.str]:
        '''The length of time that the application user sessions are valid for in the ISO-8601 standard.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-sessionduration
        '''
        result = self._values.get("session_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''The tags to attach to the new ``PermissionSet`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sso-permissionset.html#cfn-sso-permissionset-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BastionPermissionSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.LinuxBastionProps",
    jsii_struct_bases=[BastionInstanceProps],
    name_mapping={
        "security_tag": "securityTag",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "block_devices": "blockDevices",
        "instance_name": "instanceName",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "private_ip_address": "privateIpAddress",
        "role": "role",
        "security_group": "securityGroup",
        "user_data": "userData",
        "package_manager": "packageManager",
        "packages": "packages",
    },
)
class LinuxBastionProps(BastionInstanceProps):
    def __init__(
        self,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        package_manager: typing.Optional[LinuxPackageManager] = None,
        packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}
        :param vpc: VPC to launch the instance in.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_type: Type of instance to launch. Default: - t3a.large
        :param machine_image: AMI to launch. Default: - latest windows server 2022 full base
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param package_manager: (experimental) Package manager used for installing packages. Default: - dnf
        :param packages: (experimental) List of packages to be installed as part of the userdata using winget. Default: - []

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
            "vpc_subnets": vpc_subnets,
        }
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if user_data is not None:
            self._values["user_data"] = user_data
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if packages is not None:
            self._values["packages"] = packages

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''Where to place the instance within the VPC.

        :default: - Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''The name of the instance.

        :default: - CDK generated name
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Type of instance to launch.

        :default: - t3a.large
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''AMI to launch.

        :default: - latest windows server 2022 full base
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with an instance.

        Private IP should be available within the VPC that the instance is build within.

        :default: - no association
        '''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''An IAM role to associate with the instance profile assigned to this Auto Scaling Group.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:

        :default: - A role will automatically be created, it can be accessed via the ``role`` property

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''Security Group to assign to this instance.

        :default: - create new security group
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default:

        - A UserData object appropriate for the MachineImage's
        Operating System is created.
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[LinuxPackageManager]:
        '''(experimental) Package manager used for installing packages.

        :default: - dnf

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[LinuxPackageManager], result)

    @builtins.property
    def packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of packages to be installed as part of the userdata using winget.

        :default: - []

        :stability: experimental
        '''
        result = self._values.get("packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinuxBastionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.ScheduleShutdownProps",
    jsii_struct_bases=[SecurityTagable],
    name_mapping={
        "security_tag": "securityTag",
        "shutdown_schedule": "shutdownSchedule",
        "timezone": "timezone",
    },
)
class ScheduleShutdownProps(SecurityTagable):
    def __init__(
        self,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        shutdown_schedule: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}
        :param shutdown_schedule: 
        :param timezone: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if shutdown_schedule is not None:
            self._values["shutdown_schedule"] = shutdown_schedule
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def shutdown_schedule(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("shutdown_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleShutdownProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="pwed-cdk.pwed_bastion.WindowsBastionProps",
    jsii_struct_bases=[BastionInstanceProps],
    name_mapping={
        "security_tag": "securityTag",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "block_devices": "blockDevices",
        "instance_name": "instanceName",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "private_ip_address": "privateIpAddress",
        "role": "role",
        "security_group": "securityGroup",
        "user_data": "userData",
        "create_key_pair": "createKeyPair",
        "windows_packages": "windowsPackages",
    },
)
class WindowsBastionProps(BastionInstanceProps):
    def __init__(
        self,
        *,
        security_tag: typing.Optional[aws_cdk.Tag] = None,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: aws_cdk.aws_ec2.SubnetSelection,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        create_key_pair: typing.Optional[builtins.bool] = None,
        windows_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param security_tag: Tag used by all bastion resources for managing access to resources. Default: - {Key: "security:bastion", value: "true"}
        :param vpc: VPC to launch the instance in.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param instance_type: Type of instance to launch. Default: - t3a.large
        :param machine_image: AMI to launch. Default: - latest windows server 2022 full base
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param create_key_pair: If a keypair should be created and saved into Secrets Manager. This can be used to get Administrator user access Default: - false
        :param windows_packages: (experimental) List of packages to be installed as part of the userdata using winget. Default: - no association

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
            "vpc_subnets": vpc_subnets,
        }
        if security_tag is not None:
            self._values["security_tag"] = security_tag
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if user_data is not None:
            self._values["user_data"] = user_data
        if create_key_pair is not None:
            self._values["create_key_pair"] = create_key_pair
        if windows_packages is not None:
            self._values["windows_packages"] = windows_packages

    @builtins.property
    def security_tag(self) -> typing.Optional[aws_cdk.Tag]:
        '''Tag used by all bastion resources for managing access to resources.

        :default: - {Key: "security:bastion", value: "true"}
        '''
        result = self._values.get("security_tag")
        return typing.cast(typing.Optional[aws_cdk.Tag], result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> aws_cdk.aws_ec2.SubnetSelection:
        '''Where to place the instance within the VPC.

        :default: - Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(aws_cdk.aws_ec2.SubnetSelection, result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''The name of the instance.

        :default: - CDK generated name
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Type of instance to launch.

        :default: - t3a.large
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''AMI to launch.

        :default: - latest windows server 2022 full base
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with an instance.

        Private IP should be available within the VPC that the instance is build within.

        :default: - no association
        '''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''An IAM role to associate with the instance profile assigned to this Auto Scaling Group.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:

        :default: - A role will automatically be created, it can be accessed via the ``role`` property

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''Security Group to assign to this instance.

        :default: - create new security group
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default:

        - A UserData object appropriate for the MachineImage's
        Operating System is created.
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    @builtins.property
    def create_key_pair(self) -> typing.Optional[builtins.bool]:
        '''If a keypair should be created and saved into Secrets Manager.

        This can be used to get Administrator user access

        :default: - false
        '''
        result = self._values.get("create_key_pair")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def windows_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of packages to be installed as part of the userdata using winget.

        :default: - no association

        :stability: experimental
        '''
        result = self._values.get("windows_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WindowsBastionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BastionAccessPolicy",
    "BastionAccessPolicyProps",
    "BastionInstanceProps",
    "BastionPermissionSet",
    "BastionPermissionSetProps",
    "LinuxBastion",
    "LinuxBastionProps",
    "LinuxPackageManager",
    "ScheduleShutdown",
    "ScheduleShutdownProps",
    "SecurityTagable",
    "WindowsBastion",
    "WindowsBastionProps",
]

publication.publish()
