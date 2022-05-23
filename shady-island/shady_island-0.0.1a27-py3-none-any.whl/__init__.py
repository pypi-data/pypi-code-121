'''
# shady-island

[![Apache 2.0](https://img.shields.io/github/license/libreworks/shady-island)](https://github.com/libreworks/shady-island/blob/main/LICENSE)
[![npm](https://img.shields.io/npm/v/shady-island)](https://www.npmjs.com/package/shady-island)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/libreworks/shady-island/release/main?label=release)](https://github.com/libreworks/shady-island/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/libreworks/shady-island?sort=semver)](https://github.com/libreworks/shady-island/releases)
[![codecov](https://codecov.io/gh/libreworks/shady-island/branch/main/graph/badge.svg?token=OHTRGNTSPO)](https://codecov.io/gh/libreworks/shady-island)

Utilities and constructs for the AWS CDK.

## Features

* Create IPv6 CIDRs and routes for subnets in a VPC with the `CidrContext` construct.
* Set the `AssignIpv6AddressOnCreation` property of subnets in a VPC with the `AssignOnLaunch` construct.

## Documentation

* [TypeScript API Reference](https://libreworks.github.io/shady-island/api/API.html)
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

import aws_cdk
import aws_cdk.aws_ec2
import aws_cdk.aws_kms
import aws_cdk.aws_logs
import constructs


@jsii.data_type(
    jsii_type="shady-island.AssignOnLaunchProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc", "vpc_subnets": "vpcSubnets"},
)
class AssignOnLaunchProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) Properties for creating a new {@link AssignOnLaunch}.

        :param vpc: (experimental) The VPC whose subnets will be configured.
        :param vpc_subnets: (experimental) Which subnets to assign IPv6 addresses upon ENI creation.

        :stability: experimental
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC whose subnets will be configured.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) Which subnets to assign IPv6 addresses upon ENI creation.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssignOnLaunchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.CidrContextProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "address_pool": "addressPool",
        "assign_address_on_launch": "assignAddressOnLaunch",
        "cidr_block": "cidrBlock",
        "cidr_count": "cidrCount",
    },
)
class CidrContextProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        address_pool: typing.Optional[builtins.str] = None,
        assign_address_on_launch: typing.Optional[builtins.bool] = None,
        cidr_block: typing.Optional[builtins.str] = None,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for creating a new {@link CidrContext}.

        :param vpc: (experimental) The VPC whose subnets will be configured.
        :param address_pool: (experimental) The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block. If this parameter is not specified or is undefined, the CIDR block will be provided by AWS.
        :param assign_address_on_launch: (experimental) Whether this VPC should auto-assign an IPv6 address to launched ENIs. True by default.
        :param cidr_block: (experimental) An IPv6 CIDR block from the IPv6 address pool to use for this VPC. The {@link EnableIpv6Props#addressPool} attribute is required if this parameter is specified.
        :param cidr_count: (experimental) Split the CIDRs into this many groups (by default one for each subnet).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if address_pool is not None:
            self._values["address_pool"] = address_pool
        if assign_address_on_launch is not None:
            self._values["assign_address_on_launch"] = assign_address_on_launch
        if cidr_block is not None:
            self._values["cidr_block"] = cidr_block
        if cidr_count is not None:
            self._values["cidr_count"] = cidr_count

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC whose subnets will be configured.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def address_pool(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block.

        If this parameter is not specified or is undefined, the CIDR block will be
        provided by AWS.

        :stability: experimental
        '''
        result = self._values.get("address_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assign_address_on_launch(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether this VPC should auto-assign an IPv6 address to launched ENIs.

        True by default.

        :stability: experimental
        '''
        result = self._values.get("assign_address_on_launch")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cidr_block(self) -> typing.Optional[builtins.str]:
        '''(experimental) An IPv6 CIDR block from the IPv6 address pool to use for this VPC.

        The {@link EnableIpv6Props#addressPool} attribute is required if this
        parameter is specified.

        :stability: experimental
        '''
        result = self._values.get("cidr_block")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cidr_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Split the CIDRs into this many groups (by default one for each subnet).

        :stability: experimental
        '''
        result = self._values.get("cidr_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CidrContextProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.EncryptedLogGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "log_group_name": "logGroupName",
        "encryption_key": "encryptionKey",
        "removal_policy": "removalPolicy",
        "retention": "retention",
    },
)
class EncryptedLogGroupProps:
    def __init__(
        self,
        *,
        log_group_name: builtins.str,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
    ) -> None:
        '''(experimental) Constructor properties for EncryptedLogGroup.

        :param log_group_name: (experimental) Name of the log group. We need a log group name ahead of time because otherwise the key policy would create a cyclical dependency.
        :param encryption_key: (experimental) The KMS Key to encrypt the log group with. Default: A new KMS key will be created
        :param removal_policy: (experimental) Whether the key and group should be retained when they are removed from the Stack. Default: RemovalPolicy.RETAIN
        :param retention: (experimental) How long, in days, the log contents will be retained. Default: RetentionDays.TWO_YEARS

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if retention is not None:
            self._values["retention"] = retention

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''(experimental) Name of the log group.

        We need a log group name ahead of time because otherwise the key policy
        would create a cyclical dependency.

        :stability: experimental
        '''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) The KMS Key to encrypt the log group with.

        :default: A new KMS key will be created

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) Whether the key and group should be retained when they are removed from the Stack.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) How long, in days, the log contents will be retained.

        :default: RetentionDays.TWO_YEARS

        :stability: experimental
        '''
        result = self._values.get("retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptedLogGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="shady-island.IAssignOnLaunch")
class IAssignOnLaunch(typing_extensions.Protocol):
    '''(experimental) Interface for the AssignOnLaunch class.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> aws_cdk.aws_ec2.SelectedSubnets:
        '''(experimental) The chosen subnets for address assignment on ENI launch.

        :stability: experimental
        '''
        ...


class _IAssignOnLaunchProxy:
    '''(experimental) Interface for the AssignOnLaunch class.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IAssignOnLaunch"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> aws_cdk.aws_ec2.SelectedSubnets:
        '''(experimental) The chosen subnets for address assignment on ENI launch.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.SelectedSubnets, jsii.get(self, "vpcPlacement"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAssignOnLaunch).__jsii_proxy_class__ = lambda : _IAssignOnLaunchProxy


@jsii.interface(jsii_type="shady-island.ICidrContext")
class ICidrContext(typing_extensions.Protocol):
    '''(experimental) Interface for the CidrContext class.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        ...


class _ICidrContextProxy:
    '''(experimental) Interface for the CidrContext class.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "shady-island.ICidrContext"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICidrContext).__jsii_proxy_class__ = lambda : _ICidrContextProxy


@jsii.interface(jsii_type="shady-island.IEncryptedLogGroup")
class IEncryptedLogGroup(typing_extensions.Protocol):
    '''(experimental) A log group encrypted by a KMS customer managed key.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> aws_cdk.aws_kms.IKey:
        '''(experimental) The KMS encryption key.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        '''(experimental) The log group.

        :stability: experimental
        '''
        ...


class _IEncryptedLogGroupProxy:
    '''(experimental) A log group encrypted by a KMS customer managed key.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "shady-island.IEncryptedLogGroup"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> aws_cdk.aws_kms.IKey:
        '''(experimental) The KMS encryption key.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_kms.IKey, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        '''(experimental) The log group.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_logs.ILogGroup, jsii.get(self, "logGroup"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEncryptedLogGroup).__jsii_proxy_class__ = lambda : _IEncryptedLogGroupProxy


class Tier(metaclass=jsii.JSIIMeta, jsii_type="shady-island.Tier"):
    '''(experimental) A deployment environment with a specific purpose and audience.

    You can create any Tier you like, but we include those explained by DTAP.

    :see: https://en.wikipedia.org/wiki/Development,_testing,_acceptance_and_production
    :stability: experimental
    '''

    def __init__(self, id: builtins.str, label: builtins.str) -> None:
        '''(experimental) Creates a new Tier.

        :param id: - The machine-readable identifier for this tier (e.g. prod).
        :param label: - The human-readable label for this tier (e.g. Production).

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [id, label])

    @jsii.member(jsii_name="applyTags")
    def apply_tags(self, construct: constructs.IConstruct) -> None:
        '''(experimental) Adds the label of this tier as a tag to the provided construct.

        :param construct: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "applyTags", [construct]))

    @jsii.member(jsii_name="matches")
    def matches(self, other: "Tier") -> builtins.bool:
        '''(experimental) Compares this tier to the provided value and tests for equality.

        :param other: - The value to compare.

        :return: Whether the provided value is equal to this tier.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "matches", [other]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ACCEPTANCE")
    def ACCEPTANCE(cls) -> "Tier":
        '''(experimental) A tier that represents an acceptance environment.

        :stability: experimental
        '''
        return typing.cast("Tier", jsii.sget(cls, "ACCEPTANCE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DEVELOPMENT")
    def DEVELOPMENT(cls) -> "Tier":
        '''(experimental) A tier that represents a development environment.

        :stability: experimental
        '''
        return typing.cast("Tier", jsii.sget(cls, "DEVELOPMENT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PRODUCTION")
    def PRODUCTION(cls) -> "Tier":
        '''(experimental) A tier that represents a production environment.

        :stability: experimental
        '''
        return typing.cast("Tier", jsii.sget(cls, "PRODUCTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TESTING")
    def TESTING(cls) -> "Tier":
        '''(experimental) A tier that represents a testing environment.

        :stability: experimental
        '''
        return typing.cast("Tier", jsii.sget(cls, "TESTING"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''(experimental) The machine-readable identifier for this tier (e.g. prod).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) The human-readable label for this tier (e.g. Production).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))


@jsii.implements(IAssignOnLaunch)
class AssignOnLaunch(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.AssignOnLaunch",
):
    '''(experimental) Enables the "assignIpv6AddressOnCreation" attribute on selected subnets.

    :see: {@link https://github.com/aws/aws-cdk/issues/5927}
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) Creates a new BetterVpc.

        :param scope: - The construct scope.
        :param id: - The construct ID.
        :param vpc: (experimental) The VPC whose subnets will be configured.
        :param vpc_subnets: (experimental) Which subnets to assign IPv6 addresses upon ENI creation.

        :stability: experimental
        '''
        options = AssignOnLaunchProps(vpc=vpc, vpc_subnets=vpc_subnets)

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcPlacement")
    def vpc_placement(self) -> aws_cdk.aws_ec2.SelectedSubnets:
        '''(experimental) The chosen subnets for address assignment on ENI launch.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.SelectedSubnets, jsii.get(self, "vpcPlacement"))


@jsii.implements(ICidrContext)
class CidrContext(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.CidrContext",
):
    '''(experimental) Allocates IPv6 CIDRs and routes for subnets in a VPC.

    :see: {@link https://github.com/aws/aws-cdk/issues/5927}
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        address_pool: typing.Optional[builtins.str] = None,
        assign_address_on_launch: typing.Optional[builtins.bool] = None,
        cidr_block: typing.Optional[builtins.str] = None,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Creates a new BetterVpc.

        :param scope: - The construct scope.
        :param id: - The construct ID.
        :param vpc: (experimental) The VPC whose subnets will be configured.
        :param address_pool: (experimental) The ID of a BYOIP IPv6 address pool from which to allocate the CIDR block. If this parameter is not specified or is undefined, the CIDR block will be provided by AWS.
        :param assign_address_on_launch: (experimental) Whether this VPC should auto-assign an IPv6 address to launched ENIs. True by default.
        :param cidr_block: (experimental) An IPv6 CIDR block from the IPv6 address pool to use for this VPC. The {@link EnableIpv6Props#addressPool} attribute is required if this parameter is specified.
        :param cidr_count: (experimental) Split the CIDRs into this many groups (by default one for each subnet).

        :stability: experimental
        '''
        options = CidrContextProps(
            vpc=vpc,
            address_pool=address_pool,
            assign_address_on_launch=assign_address_on_launch,
            cidr_block=cidr_block,
            cidr_count=cidr_count,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @jsii.member(jsii_name="assignPrivateSubnetCidrs")
    def _assign_private_subnet_cidrs(
        self,
        vpc: aws_cdk.aws_ec2.IVpc,
        cidrs: typing.Sequence[builtins.str],
        cidr_block: aws_cdk.CfnResource,
    ) -> None:
        '''(experimental) Override the template;

        set the IPv6 CIDR for private subnets.

        :param vpc: - The VPC of the subnets.
        :param cidrs: - The possible IPv6 CIDRs to assign.
        :param cidr_block: - The CfnVPCCidrBlock the subnets depend on.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "assignPrivateSubnetCidrs", [vpc, cidrs, cidr_block]))

    @jsii.member(jsii_name="assignPublicSubnetCidrs")
    def _assign_public_subnet_cidrs(
        self,
        vpc: aws_cdk.aws_ec2.IVpc,
        cidrs: typing.Sequence[builtins.str],
        cidr_block: aws_cdk.CfnResource,
    ) -> None:
        '''(experimental) Override the template;

        set the IPv6 CIDR for isolated subnets.

        :param vpc: - The VPC of the subnets.
        :param cidrs: - The possible IPv6 CIDRs to assign.
        :param cidr_block: - The CfnVPCCidrBlock the subnets depend on.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "assignPublicSubnetCidrs", [vpc, cidrs, cidr_block]))

    @jsii.member(jsii_name="validateCidrCount")
    def _validate_cidr_count(
        self,
        vpc: aws_cdk.aws_ec2.IVpc,
        cidr_count: typing.Optional[jsii.Number] = None,
    ) -> jsii.Number:
        '''(experimental) Figure out the minimun required CIDR subnets and the number desired.

        :param vpc: - The VPC.
        :param cidr_count: - Optional. Divide the VPC CIDR into this many subsets.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.invoke(self, "validateCidrCount", [vpc, cidr_count]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The IPv6-enabled VPC.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.implements(IEncryptedLogGroup)
class EncryptedLogGroup(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.EncryptedLogGroup",
):
    '''(experimental) A log group encrypted by a KMS customer managed key.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        log_group_name: builtins.str,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
    ) -> None:
        '''(experimental) Creates a new EncryptedLogGroup.

        :param scope: -
        :param id: -
        :param log_group_name: (experimental) Name of the log group. We need a log group name ahead of time because otherwise the key policy would create a cyclical dependency.
        :param encryption_key: (experimental) The KMS Key to encrypt the log group with. Default: A new KMS key will be created
        :param removal_policy: (experimental) Whether the key and group should be retained when they are removed from the Stack. Default: RemovalPolicy.RETAIN
        :param retention: (experimental) How long, in days, the log contents will be retained. Default: RetentionDays.TWO_YEARS

        :stability: experimental
        '''
        props = EncryptedLogGroupProps(
            log_group_name=log_group_name,
            encryption_key=encryption_key,
            removal_policy=removal_policy,
            retention=retention,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> aws_cdk.aws_kms.IKey:
        '''(experimental) The KMS encryption key.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_kms.IKey, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> aws_cdk.aws_logs.ILogGroup:
        '''(experimental) The log group.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_logs.ILogGroup, jsii.get(self, "logGroup"))


__all__ = [
    "AssignOnLaunch",
    "AssignOnLaunchProps",
    "CidrContext",
    "CidrContextProps",
    "EncryptedLogGroup",
    "EncryptedLogGroupProps",
    "IAssignOnLaunch",
    "ICidrContext",
    "IEncryptedLogGroup",
    "Tier",
]

publication.publish()
