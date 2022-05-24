'''
# Simple NAT

![Release](https://github.com/zxkane/snat/workflows/Release/badge.svg)
[![NPM version](http://img.shields.io/npm/v/cdk-construct-simple-nat.svg?style=flat-square)](https://www.npmjs.com/package/cdk-construct-simple-nat)
[![pypi version](http://img.shields.io/pypi/v/zxkane.cdk-construct-simple-nat.svg?style=flat-square)](https://pypi.org/project/zxkane.cdk-construct-simple-nat/)

It's a CDK construct to create NAT instances on AWS.

It supports adding specific IP CIDRs to route tables of VPC, the network traffic to those IP CIDRs will be forwarded to the NAT instances.

It supports routing to below services out of box,

* Github git servers
* Google
* Cloudflare

![Arch diagram](arch.png)

## Install

TypeScript/JavaScript:

```shell
yarn add cdk-construct-simple-nat
```

or

```shell
npm install cdk-construct-simple-nat
```

## Usage

```python
import { SimpleNAT } from 'cdk-construct-simple-nat';

new SimpleNAT(this, 'SimpleNAT', {
  vpc,
  natSubnetsSelection: {
    subnetType: SubnetType.PUBLIC,
    onePerAz: true,
  },
})
.withGithubRoute();
```

See the complete [example](example/) and [API doc](./API.md).

## FAQ

### What's the difference between [EC2 NAT instances](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-ec2-readme.html#using-nat-instances) and NAT instances created by this construct

There are below differences,

* EC2 NAT instance will route all Internet traffic to itself by default
* NAT instance uses depracated Amazon Linux AMI, this construct always uses latest Amazon Linux 2 AMI
* NAT instances created by this construct can work with NAT gateways together, you can have multiple NAT instances in one VPC
* This construct can help when only routing specific traffic(for example, github/gist) to NAT instances which acts as transit proxy

### What's the difference between [CDK built-in NAT instances](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-ec2-readme.html#using-nat-instances) and NAT instances created by this construct

* CDK built-in NAT instances has to be created with VPC stack, this construct can add NAT instances to any existing VPC
* You can use this construct multiple NAT instances for different purposes
* This construct allows you customize the instances how to route the traffic

### The deployment fails due to the routes in route table exceeds the limit

[The default routes in route table is 50](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-route-tables), the deployment will fail if adding routes more than the limit of your account.
You can increase the limit up to **1000** routes per route table via service quota.

### How to exclude IPv6 CIDR with built-in github/google/cloudflare routes

You can exclude IPv6 CIDR like below,

```python
new SimpleNAT(this, 'SimpleNAT', {
  vpc,
})
.withCloudflareRoute({
  excludeIPv6: true,
});
```
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
import aws_cdk.aws_iam
import constructs


@jsii.data_type(
    jsii_type="cdk-construct-simple-nat.RouteProps",
    jsii_struct_bases=[],
    name_mapping={"exclude_i_pv6": "excludeIPv6"},
)
class RouteProps:
    def __init__(self, *, exclude_i_pv6: typing.Optional[builtins.bool] = None) -> None:
        '''Properties for how adding IPs to route.

        :param exclude_i_pv6: If excluding IPv6 when creating route. Default: - false
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude_i_pv6 is not None:
            self._values["exclude_i_pv6"] = exclude_i_pv6

    @builtins.property
    def exclude_i_pv6(self) -> typing.Optional[builtins.bool]:
        '''If excluding IPv6 when creating route.

        :default: - false
        '''
        result = self._values.get("exclude_i_pv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RouteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SimpleNAT(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-construct-simple-nat.SimpleNAT",
):
    '''Simple NAT instaces construct.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        custom_scripts: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        key_name: typing.Optional[builtins.str] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        nat_subnets_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        private_subnets_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC the NAT instances will reside.
        :param custom_scripts: The custom script when provisioning the NAT instances. Default: - no custom script.
        :param instance_type: The instance type of NAT instances. Default: - t3.MICRO.
        :param key_name: The key name of ssh key of NAT instances. Default: - No SSH access will be possible.
        :param machine_image: The AMI of NAT instances. Default: - Amazon Linux 2 for x86_64.
        :param nat_subnets_selection: The subnet selection for NAT instances, one NAT instance will be placed in the selected subnets. NOTE: must select the public subnet Default: - subnetType is SubnetType.PUBLIC and onePerAZ is true.
        :param private_subnets_selection: The subnet selection for updating route tables for selected subnets. Default: - subnetType is SubnetType.PRIVATE_WITH_NAT.
        :param role: The IAM role attached to NAT instances. Default: - an IAM role is created.
        '''
        props = SimpleNATProps(
            vpc=vpc,
            custom_scripts=custom_scripts,
            instance_type=instance_type,
            key_name=key_name,
            machine_image=machine_image,
            nat_subnets_selection=nat_subnets_selection,
            private_subnets_selection=private_subnets_selection,
            role=role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addV4Route")
    def add_v4_route(self, v4_cidr: builtins.str) -> "SimpleNAT":
        '''
        :param v4_cidr: -
        '''
        return typing.cast("SimpleNAT", jsii.invoke(self, "addV4Route", [v4_cidr]))

    @jsii.member(jsii_name="addV6Route")
    def add_v6_route(self, v6_cidr: builtins.str) -> "SimpleNAT":
        '''
        :param v6_cidr: -
        '''
        return typing.cast("SimpleNAT", jsii.invoke(self, "addV6Route", [v6_cidr]))

    @jsii.member(jsii_name="withCloudflareRoute")
    def with_cloudflare_route(
        self,
        *,
        exclude_i_pv6: typing.Optional[builtins.bool] = None,
    ) -> "SimpleNAT":
        '''Add Cloudflare IPs to route table.

        See https://www.cloudflare.com/ips/ for details

        :param exclude_i_pv6: If excluding IPv6 when creating route. Default: - false
        '''
        props = RouteProps(exclude_i_pv6=exclude_i_pv6)

        return typing.cast("SimpleNAT", jsii.invoke(self, "withCloudflareRoute", [props]))

    @jsii.member(jsii_name="withGithubRoute")
    def with_github_route(
        self,
        *,
        exclude_i_pv6: typing.Optional[builtins.bool] = None,
    ) -> "SimpleNAT":
        '''Add Github IPs to route table.

        :param exclude_i_pv6: If excluding IPv6 when creating route. Default: - false
        '''
        props = RouteProps(exclude_i_pv6=exclude_i_pv6)

        return typing.cast("SimpleNAT", jsii.invoke(self, "withGithubRoute", [props]))

    @jsii.member(jsii_name="withGoogleRoute")
    def with_google_route(
        self,
        *,
        exclude_i_pv6: typing.Optional[builtins.bool] = None,
    ) -> "SimpleNAT":
        '''Add Google IPs to route table.

        :param exclude_i_pv6: If excluding IPv6 when creating route. Default: - false
        '''
        props = RouteProps(exclude_i_pv6=exclude_i_pv6)

        return typing.cast("SimpleNAT", jsii.invoke(self, "withGoogleRoute", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="Ipv6Regex")
    def IPV6_REGEX(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "Ipv6Regex"))


@jsii.data_type(
    jsii_type="cdk-construct-simple-nat.SimpleNATProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "custom_scripts": "customScripts",
        "instance_type": "instanceType",
        "key_name": "keyName",
        "machine_image": "machineImage",
        "nat_subnets_selection": "natSubnetsSelection",
        "private_subnets_selection": "privateSubnetsSelection",
        "role": "role",
    },
)
class SimpleNATProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        custom_scripts: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        key_name: typing.Optional[builtins.str] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        nat_subnets_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        private_subnets_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''Properties for NAT instances.

        :param vpc: The VPC the NAT instances will reside.
        :param custom_scripts: The custom script when provisioning the NAT instances. Default: - no custom script.
        :param instance_type: The instance type of NAT instances. Default: - t3.MICRO.
        :param key_name: The key name of ssh key of NAT instances. Default: - No SSH access will be possible.
        :param machine_image: The AMI of NAT instances. Default: - Amazon Linux 2 for x86_64.
        :param nat_subnets_selection: The subnet selection for NAT instances, one NAT instance will be placed in the selected subnets. NOTE: must select the public subnet Default: - subnetType is SubnetType.PUBLIC and onePerAZ is true.
        :param private_subnets_selection: The subnet selection for updating route tables for selected subnets. Default: - subnetType is SubnetType.PRIVATE_WITH_NAT.
        :param role: The IAM role attached to NAT instances. Default: - an IAM role is created.
        '''
        if isinstance(nat_subnets_selection, dict):
            nat_subnets_selection = aws_cdk.aws_ec2.SubnetSelection(**nat_subnets_selection)
        if isinstance(private_subnets_selection, dict):
            private_subnets_selection = aws_cdk.aws_ec2.SubnetSelection(**private_subnets_selection)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if custom_scripts is not None:
            self._values["custom_scripts"] = custom_scripts
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if key_name is not None:
            self._values["key_name"] = key_name
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if nat_subnets_selection is not None:
            self._values["nat_subnets_selection"] = nat_subnets_selection
        if private_subnets_selection is not None:
            self._values["private_subnets_selection"] = private_subnets_selection
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC the NAT instances will reside.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def custom_scripts(self) -> typing.Optional[builtins.str]:
        '''The custom script when provisioning the NAT instances.

        :default: - no custom script.
        '''
        result = self._values.get("custom_scripts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''The instance type of NAT instances.

        :default: - t3.MICRO.
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''The key name of ssh key of NAT instances.

        :default: - No SSH access will be possible.
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''The AMI of NAT instances.

        :default: - Amazon Linux 2 for x86_64.
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def nat_subnets_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnet selection for NAT instances, one NAT instance will be placed in the selected subnets.

        NOTE: must select the public subnet

        :default: - subnetType is SubnetType.PUBLIC and onePerAZ is true.
        '''
        result = self._values.get("nat_subnets_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def private_subnets_selection(
        self,
    ) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnet selection for updating route tables for selected subnets.

        :default: - subnetType is SubnetType.PRIVATE_WITH_NAT.
        '''
        result = self._values.get("private_subnets_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role attached to NAT instances.

        :default: - an IAM role is created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SimpleNATProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RouteProps",
    "SimpleNAT",
    "SimpleNATProps",
]

publication.publish()
