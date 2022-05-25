'''
# cdk-library-managed-instance-role

[![build](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-managed-instance-role/workflows/build.yml)

This CDK Construct Library includes a construct (`ManagedInstanceRole`) which creates an AWS instance profile. By default this instance profile includes the basic policies required for instance management in SSM and the ability to Domain Join the instance.

The purpose of this CDK Construct Library is to ease the creation of instance roles by not needing to code the inclusion of baseline management roles for evey single different role implementation every time. Instance profiles only support a single role so its important the role includes all required access. This construct allows making additions to those baseline policies with ease.

The construct defines an interface (`IManagedInstanceRoleProps`) to configure the managed policies of the role as well as manage the inclusion of the default roles.

## Dev

### Pre-reqs:

You will need:

* npm installed on your machine
* AWS CDK installed on your machine
* python installed on your machine
* dotnet installed on your machine
* a github account

This project is managed with `projen`. Modify the `.projenrc.js` file and run `npx projen`. You can also modify this `README` file and the `src` code directory as needed. Github actions take care of publishing utilizing the automatically created workflows from `projen`.
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

import aws_cdk.aws_iam
import constructs


class ManagedInstanceRole(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRole",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        create_instance_profile: typing.Optional[builtins.bool] = None,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[aws_cdk.aws_iam.ManagedPolicy]] = None,
        retention_policy: typing.Optional[builtins.bool] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param create_instance_profile: Whether or not to associate the role with an instance profile. Default: true
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param retention_policy: The retention policy for this role.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        props = ManagedInstanceRoleProps(
            create_instance_profile=create_instance_profile,
            domain_join_enabled=domain_join_enabled,
            managed_policies=managed_policies,
            retention_policy=retention_policy,
            ssm_management_enabled=ssm_management_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''The role arn.'''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The role name.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> aws_cdk.aws_iam.Role:
        '''The role.'''
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile]:
        '''The CfnInstanceProfile automatically created for this role.'''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.CfnInstanceProfile], jsii.get(self, "instanceProfile"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-managed-instance-role.ManagedInstanceRoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_instance_profile": "createInstanceProfile",
        "domain_join_enabled": "domainJoinEnabled",
        "managed_policies": "managedPolicies",
        "retention_policy": "retentionPolicy",
        "ssm_management_enabled": "ssmManagementEnabled",
    },
)
class ManagedInstanceRoleProps:
    def __init__(
        self,
        *,
        create_instance_profile: typing.Optional[builtins.bool] = None,
        domain_join_enabled: typing.Optional[builtins.bool] = None,
        managed_policies: typing.Optional[typing.Sequence[aws_cdk.aws_iam.ManagedPolicy]] = None,
        retention_policy: typing.Optional[builtins.bool] = None,
        ssm_management_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param create_instance_profile: Whether or not to associate the role with an instance profile. Default: true
        :param domain_join_enabled: Should the role include directory service access with SSM.
        :param managed_policies: The managed policies to apply to the role in addition to the default policies.
        :param retention_policy: The retention policy for this role.
        :param ssm_management_enabled: Should the role include SSM management. By default if domainJoinEnabled is true then this role is always included.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create_instance_profile is not None:
            self._values["create_instance_profile"] = create_instance_profile
        if domain_join_enabled is not None:
            self._values["domain_join_enabled"] = domain_join_enabled
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if retention_policy is not None:
            self._values["retention_policy"] = retention_policy
        if ssm_management_enabled is not None:
            self._values["ssm_management_enabled"] = ssm_management_enabled

    @builtins.property
    def create_instance_profile(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to associate the role with an instance profile.

        :default: true
        '''
        result = self._values.get("create_instance_profile")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_join_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include directory service access with SSM.'''
        result = self._values.get("domain_join_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.ManagedPolicy]]:
        '''The managed policies to apply to the role in addition to the default policies.'''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.ManagedPolicy]], result)

    @builtins.property
    def retention_policy(self) -> typing.Optional[builtins.bool]:
        '''The retention policy for this role.'''
        result = self._values.get("retention_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ssm_management_enabled(self) -> typing.Optional[builtins.bool]:
        '''Should the role include SSM management.

        By default if domainJoinEnabled is true then this role is always included.
        '''
        result = self._values.get("ssm_management_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ManagedInstanceRole",
    "ManagedInstanceRoleProps",
]

publication.publish()
