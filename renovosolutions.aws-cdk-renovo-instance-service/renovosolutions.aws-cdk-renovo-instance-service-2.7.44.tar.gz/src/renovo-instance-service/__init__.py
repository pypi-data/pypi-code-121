'''
# cdk-renovo-instance-service

[![build](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-renovo-instance-service/actions/workflows/build.yml)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_route53
import constructs
import managed_instance_role


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.AmiLookup",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "owners": "owners", "windows": "windows"},
)
class AmiLookup:
    def __init__(
        self,
        *,
        name: builtins.str,
        owners: typing.Optional[typing.Sequence[builtins.str]] = None,
        windows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: The name string to use for AMI lookup.
        :param owners: The owners to use for AMI lookup.
        :param windows: Is this AMI expected to be windows?
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if owners is not None:
            self._values["owners"] = owners
        if windows is not None:
            self._values["windows"] = windows

    @builtins.property
    def name(self) -> builtins.str:
        '''The name string to use for AMI lookup.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def owners(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The owners to use for AMI lookup.'''
        result = self._values.get("owners")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def windows(self) -> typing.Optional[builtins.bool]:
        '''Is this AMI expected to be windows?'''
        result = self._values.get("windows")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmiLookup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InstanceService(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceService",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_type: aws_cdk.aws_ec2.InstanceType,
        machine_image: aws_cdk.aws_ec2.IMachineImage,
        name: builtins.str,
        parent_domain: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        instance_role: typing.Optional[managed_instance_role.ManagedInstanceRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_type: The type of instance to launch.
        :param machine_image: AMI to launch.
        :param name: The name of the service the instance is for.
        :param parent_domain: The parent domain of the service.
        :param vpc: The VPC to launch the instance in.
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default.
        :param availability_zones: Select subnets only in the given AZs.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param instance_role: The role to use for this instance. Default: - A new ManagedInstanceRole will be created for this instance
        :param key_name: Name of the SSH keypair to grant access to the instance.
        :param private_ip_address: Defines a private IP address to associate with the instance.
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: true
        :param security_group: The security group to use for this instance. Default: - A new SecurityGroup will be created for this instance
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE_WITH_NAT
        :param use_imdsv2_custom_aspect: Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS. Turned on by default otherwise we need to apply a feature flag to every project using an instance or apply a breaking change to instance construct ids. Default: true
        :param user_data: The user data to apply to the instance.
        '''
        props = InstanceServiceProps(
            instance_type=instance_type,
            machine_image=machine_image,
            name=name,
            parent_domain=parent_domain,
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            availability_zones=availability_zones,
            block_devices=block_devices,
            disable_inline_rules=disable_inline_rules,
            enable_cloudwatch_logs=enable_cloudwatch_logs,
            enabled_no_public_ingress_aspect=enabled_no_public_ingress_aspect,
            enable_no_db_ports_aspect=enable_no_db_ports_aspect,
            enable_no_remote_management_ports_aspect=enable_no_remote_management_ports_aspect,
            instance_role=instance_role,
            key_name=key_name,
            private_ip_address=private_ip_address,
            require_imdsv2=require_imdsv2,
            security_group=security_group,
            subnet_type=subnet_type,
            use_imdsv2_custom_aspect=use_imdsv2_custom_aspect,
            user_data=user_data,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instance")
    def instance(self) -> aws_cdk.aws_ec2.Instance:
        '''The underlying instance resource.'''
        return typing.cast(aws_cdk.aws_ec2.Instance, jsii.get(self, "instance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAvailabilityZone")
    def instance_availability_zone(self) -> builtins.str:
        '''The availability zone of the instance.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceAvailabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceCfn")
    def instance_cfn(self) -> aws_cdk.aws_ec2.CfnInstance:
        '''The underlying CfnInstance resource.'''
        return typing.cast(aws_cdk.aws_ec2.CfnInstance, jsii.get(self, "instanceCfn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceDnsName")
    def instance_dns_name(self) -> aws_cdk.aws_route53.ARecord:
        '''DNS record for this instance created in Route53.'''
        return typing.cast(aws_cdk.aws_route53.ARecord, jsii.get(self, "instanceDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEc2PrivateDnsName")
    def instance_ec2_private_dns_name(self) -> builtins.str:
        '''Private DNS name for this instance assigned by EC2.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceEc2PrivateDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceEc2PublicDnsName")
    def instance_ec2_public_dns_name(self) -> builtins.str:
        '''Public DNS name for this instance assigned by EC2.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceEc2PublicDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        '''The instance's ID.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instancePrivateIp")
    def instance_private_ip(self) -> builtins.str:
        '''Private IP for this instance.'''
        return typing.cast(builtins.str, jsii.get(self, "instancePrivateIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> aws_cdk.aws_iam.CfnInstanceProfile:
        '''The instance profile associated with this instance.'''
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> managed_instance_role.ManagedInstanceRole:
        '''The instance role associated with this instance.'''
        return typing.cast(managed_instance_role.ManagedInstanceRole, jsii.get(self, "instanceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="osType")
    def os_type(self) -> aws_cdk.aws_ec2.OperatingSystemType:
        '''The type of OS the instance is running.'''
        return typing.cast(aws_cdk.aws_ec2.OperatingSystemType, jsii.get(self, "osType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        '''The security group associated with this instance.'''
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, jsii.get(self, "securityGroup"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.InstanceServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "name": "name",
        "parent_domain": "parentDomain",
        "vpc": "vpc",
        "allow_all_outbound": "allowAllOutbound",
        "availability_zones": "availabilityZones",
        "block_devices": "blockDevices",
        "disable_inline_rules": "disableInlineRules",
        "enable_cloudwatch_logs": "enableCloudwatchLogs",
        "enabled_no_public_ingress_aspect": "enabledNoPublicIngressAspect",
        "enable_no_db_ports_aspect": "enableNoDBPortsAspect",
        "enable_no_remote_management_ports_aspect": "enableNoRemoteManagementPortsAspect",
        "instance_role": "instanceRole",
        "key_name": "keyName",
        "private_ip_address": "privateIpAddress",
        "require_imdsv2": "requireImdsv2",
        "security_group": "securityGroup",
        "subnet_type": "subnetType",
        "use_imdsv2_custom_aspect": "useImdsv2CustomAspect",
        "user_data": "userData",
    },
)
class InstanceServiceProps:
    def __init__(
        self,
        *,
        instance_type: aws_cdk.aws_ec2.InstanceType,
        machine_image: aws_cdk.aws_ec2.IMachineImage,
        name: builtins.str,
        parent_domain: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_devices: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.BlockDevice]] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        enable_cloudwatch_logs: typing.Optional[builtins.bool] = None,
        enabled_no_public_ingress_aspect: typing.Optional[builtins.bool] = None,
        enable_no_db_ports_aspect: typing.Optional[builtins.bool] = None,
        enable_no_remote_management_ports_aspect: typing.Optional[builtins.bool] = None,
        instance_role: typing.Optional[managed_instance_role.ManagedInstanceRole] = None,
        key_name: typing.Optional[builtins.str] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.SecurityGroup] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        use_imdsv2_custom_aspect: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
    ) -> None:
        '''
        :param instance_type: The type of instance to launch.
        :param machine_image: AMI to launch.
        :param name: The name of the service the instance is for.
        :param parent_domain: The parent domain of the service.
        :param vpc: The VPC to launch the instance in.
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default.
        :param availability_zones: Select subnets only in the given AZs.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization for the instances security group. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param enable_cloudwatch_logs: Whether or not to enable logging to Cloudwatch Logs. Default: true
        :param enabled_no_public_ingress_aspect: Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0. If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        :param enable_no_db_ports_aspect: Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param enable_no_remote_management_ports_aspect: Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs. If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail. Default: true
        :param instance_role: The role to use for this instance. Default: - A new ManagedInstanceRole will be created for this instance
        :param key_name: Name of the SSH keypair to grant access to the instance.
        :param private_ip_address: Defines a private IP address to associate with the instance.
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: true
        :param security_group: The security group to use for this instance. Default: - A new SecurityGroup will be created for this instance
        :param subnet_type: The subnet type to launch this service in. Default: ec2.SubnetType.PRIVATE_WITH_NAT
        :param use_imdsv2_custom_aspect: Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS. Turned on by default otherwise we need to apply a feature flag to every project using an instance or apply a breaking change to instance construct ids. Default: true
        :param user_data: The user data to apply to the instance.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
            "machine_image": machine_image,
            "name": name,
            "parent_domain": parent_domain,
            "vpc": vpc,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if disable_inline_rules is not None:
            self._values["disable_inline_rules"] = disable_inline_rules
        if enable_cloudwatch_logs is not None:
            self._values["enable_cloudwatch_logs"] = enable_cloudwatch_logs
        if enabled_no_public_ingress_aspect is not None:
            self._values["enabled_no_public_ingress_aspect"] = enabled_no_public_ingress_aspect
        if enable_no_db_ports_aspect is not None:
            self._values["enable_no_db_ports_aspect"] = enable_no_db_ports_aspect
        if enable_no_remote_management_ports_aspect is not None:
            self._values["enable_no_remote_management_ports_aspect"] = enable_no_remote_management_ports_aspect
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if key_name is not None:
            self._values["key_name"] = key_name
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if require_imdsv2 is not None:
            self._values["require_imdsv2"] = require_imdsv2
        if security_group is not None:
            self._values["security_group"] = security_group
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type
        if use_imdsv2_custom_aspect is not None:
            self._values["use_imdsv2_custom_aspect"] = use_imdsv2_custom_aspect
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        '''The type of instance to launch.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(aws_cdk.aws_ec2.InstanceType, result)

    @builtins.property
    def machine_image(self) -> aws_cdk.aws_ec2.IMachineImage:
        '''AMI to launch.'''
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the service the instance is for.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_domain(self) -> builtins.str:
        '''The parent domain of the service.'''
        result = self._values.get("parent_domain")
        assert result is not None, "Required property 'parent_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate connections to anywhere by default.'''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Select subnets only in the given AZs.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance.

        You can specify virtual devices and EBS volumes
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.BlockDevice]], result)

    @builtins.property
    def disable_inline_rules(self) -> typing.Optional[builtins.bool]:
        '''Whether to disable inline ingress and egress rule optimization for the instances security group.

        If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements.

        Inlining rules is an optimization for producing smaller stack templates.
        Sometimes this is not desirable, for example when security group access is managed via tags.

        The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'.

        :default: false
        '''
        result = self._values.get("disable_inline_rules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_cloudwatch_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable logging to Cloudwatch Logs.

        :default: true
        '''
        result = self._values.get("enable_cloudwatch_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enabled_no_public_ingress_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access from the public internet: Any rule with a source from 0.0.0.0/0 or ::/0.

        If these sources are used when this is enabled and error will be added to CDK metadata and deployment and synth will fail.
        '''
        result = self._values.get("enabled_no_public_ingress_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_db_ports_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to relational DB ports: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_db_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_no_remote_management_ports_aspect(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether or not to prevent security group from containing rules that allow access to remote management ports: SSH, RDP, WinRM, WinRM over HTTPs.

        If these ports are opened when this is enabled an error will be added to CDK metadata and deployment and synth will fail.

        :default: true
        '''
        result = self._values.get("enable_no_remote_management_ports_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_role(
        self,
    ) -> typing.Optional[managed_instance_role.ManagedInstanceRole]:
        '''The role to use for this instance.

        :default: - A new ManagedInstanceRole will be created for this instance
        '''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[managed_instance_role.ManagedInstanceRole], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''Name of the SSH keypair to grant access to the instance.'''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with the instance.'''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_imdsv2(self) -> typing.Optional[builtins.bool]:
        '''Whether IMDSv2 should be required on this instance.

        :default: true
        '''
        result = self._values.get("require_imdsv2")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.SecurityGroup]:
        '''The security group to use for this instance.

        :default: - A new SecurityGroup will be created for this instance
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SecurityGroup], result)

    @builtins.property
    def subnet_type(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetType]:
        '''The subnet type to launch this service in.

        :default: ec2.SubnetType.PRIVATE_WITH_NAT
        '''
        result = self._values.get("subnet_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetType], result)

    @builtins.property
    def use_imdsv2_custom_aspect(self) -> typing.Optional[builtins.bool]:
        '''Whether to use th IMDSv2 custom aspect provided by this library or the default one provided by AWS.

        Turned on by default otherwise we need to apply a feature flag to every project using an instance or
        apply a breaking change to instance construct ids.

        :default: true

        :see: https://github.com/jericht/aws-cdk/blob/56c01aedc4f745eec79409c99b749f516ffc39e1/packages/%40aws-cdk/aws-ec2/lib/aspects/require-imdsv2-aspect.ts#L95
        '''
        result = self._values.get("use_imdsv2_custom_aspect")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_data(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        '''The user data to apply to the instance.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedLoggingPolicy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicy",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        os: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param os: The OS of the instance this policy is for.
        '''
        props = ManagedLoggingPolicyProps(os=os)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> aws_cdk.aws_iam.ManagedPolicy:
        return typing.cast(aws_cdk.aws_iam.ManagedPolicy, jsii.get(self, "policy"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-instance-service.ManagedLoggingPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"os": "os"},
)
class ManagedLoggingPolicyProps:
    def __init__(self, *, os: builtins.str) -> None:
        '''
        :param os: The OS of the instance this policy is for.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "os": os,
        }

    @builtins.property
    def os(self) -> builtins.str:
        '''The OS of the instance this policy is for.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedLoggingPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AmiLookup",
    "InstanceService",
    "InstanceServiceProps",
    "ManagedLoggingPolicy",
    "ManagedLoggingPolicyProps",
]

publication.publish()
