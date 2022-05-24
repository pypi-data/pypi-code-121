'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-vpc?style=flat-square)](https://github.com/pepperize/cdk-vpc/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-vpc?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-vpc)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-vpc?style=flat-square)](https://pypi.org/project/pepperize.cdk-vpc/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.Vpc?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.Vpc/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-vpc/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-vpc/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-vpc?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-vpc/releases)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod&style=flat-square)](https://gitpod.io/#https://github.com/pepperize/cdk-vpc)

# CDK Vpc

Utility constructs for tagging subnets or creating a cheaper vpc.

* [Cheaper Vpc](#create-a-cheaper-vpc)
* [Tagging subnets](#tag-your-imported-subnets)

## Install

### TypeScript

```shell
npm install @pepperize/cdk-vpc
```

or

```shell
yarn add @pepperize/cdk-vpc
```

### Python

```shell
pip install pepperize.cdk-vpc
```

### C# / .Net

```shell
dotnet add package Pepperize.CDK.Vpc
```

## Getting Started

1. Create a new CDK TypeScript App project with [projen](https://github.com/projen/projen)

   ```shell
   mkdir my-project
   cd my-project
   git init -b main
   npx projen new awscdk-app-ts
   ```
2. Add `@pepperize/cdk-vpc` to your dependencies in `.projenrc.js`

   ```python
   const project = new awscdk.AwsCdkTypeScriptApp({
     //...
     deps: ["@pepperize/cdk-vpc"],
   });
   ```
3. Install the dependency

   ```shell
   npx projen
   ```

# Usage

## Create a cheaper Vpc

Use this as a cheaper drop-in replacement to create a vpc with 2 AvailabilityZones and a `t3.nano` NatInstance.

```python
import { App, Stack } from "aws-cdk-lib";
import { CheapVpc } from "@pepperize/cdk-vpc";

const app = new App();
const stack = new Stack(app, "MyCheapVpcStack");

new CheapVpc(stack, "MyCheapVpc");
```

## Tag your imported subnets

Subnets imported by `Vpc.fromLookup` wouldn't be tagged by `Tags.of` automatically. To tag them (or any other imported vpc resource) use:

```python
import { CheapVpc } from "@pepperize/cdk-vpc";
import * as ec2 from "aws-cdk-lib/aws-ec2";

const app = new App();
const stack = new Stack(app, "VpcStack");
const vpc = ec2.Vpc.fromLookup(stack, "VpcLookup", {
  vpcId: "vpc-1234567890",
  region: env.region,
});

new CreateTags(vpcStack, "TagPrivateSubnets", {
  resourceIds: vpc.privateSubnets.map((subnet) => {
    return subnet.subnetId;
  }),
  tags: [
    {
      key: "kubernetes.io/role/internal-elb",
      value: "1",
    },
  ],
});
```

# Contributing

Contributions of all kinds are welcome :rocket: Check out our [contributor's guide](https://github.com/pepperize/cdk-vpc/blob/main/CONTRIBUTING.md).

For a quick start, check out a development environment:

```shell
git clone git@github.com:pepperize/cdk-vpc
cd cdk-vpc
 # install dependencies
yarn
# build with projen
yarn build
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
import constructs


class CheapVpc(
    aws_cdk.aws_ec2.Vpc,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-vpc.CheapVpc",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cidr: typing.Optional[builtins.str] = None,
        default_instance_tenancy: typing.Optional[aws_cdk.aws_ec2.DefaultInstanceTenancy] = None,
        enable_dns_hostnames: typing.Optional[builtins.bool] = None,
        enable_dns_support: typing.Optional[builtins.bool] = None,
        flow_logs: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.FlowLogOptions]] = None,
        gateway_endpoints: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.GatewayVpcEndpointOptions]] = None,
        max_azs: typing.Optional[jsii.Number] = None,
        nat_gateway_provider: typing.Optional[aws_cdk.aws_ec2.NatProvider] = None,
        nat_gateways: typing.Optional[jsii.Number] = None,
        nat_gateway_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        subnet_configuration: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SubnetConfiguration]] = None,
        vpn_connections: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ec2.VpnConnectionOptions]] = None,
        vpn_gateway: typing.Optional[builtins.bool] = None,
        vpn_gateway_asn: typing.Optional[jsii.Number] = None,
        vpn_route_propagation: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SubnetSelection]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cidr: The CIDR range to use for the VPC, e.g. '10.0.0.0/16'. Should be a minimum of /28 and maximum size of /16. The range will be split across all subnets per Availability Zone. Default: Vpc.DEFAULT_CIDR_RANGE
        :param default_instance_tenancy: The default tenancy of instances launched into the VPC. By setting this to dedicated tenancy, instances will be launched on hardware dedicated to a single AWS customer, unless specifically specified at instance launch time. Please note, not all instance types are usable with Dedicated tenancy. Default: DefaultInstanceTenancy.Default (shared) tenancy
        :param enable_dns_hostnames: Indicates whether the instances launched in the VPC get public DNS hostnames. If this attribute is true, instances in the VPC get public DNS hostnames, but only if the enableDnsSupport attribute is also set to true. Default: true
        :param enable_dns_support: Indicates whether the DNS resolution is supported for the VPC. If this attribute is false, the Amazon-provided DNS server in the VPC that resolves public DNS hostnames to IP addresses is not enabled. If this attribute is true, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC IPv4 network range plus two will succeed. Default: true
        :param flow_logs: Flow logs to add to this VPC. Default: - No flow logs.
        :param gateway_endpoints: Gateway endpoints to add to this VPC. Default: - None.
        :param max_azs: Define the maximum number of AZs to use in this region. If the region has more AZs than you want to use (for example, because of EIP limits), pick a lower number here. The AZs will be sorted and picked from the start of the list. If you pick a higher number than the number of AZs in the region, all AZs in the region will be selected. To use "all AZs" available to your account, use a high number (such as 99). Be aware that environment-agnostic stacks will be created with access to only 2 AZs, so to use more than 2 AZs, be sure to specify the account and region on your stack. Default: 3
        :param nat_gateway_provider: What type of NAT provider to use. Select between NAT gateways or NAT instances. NAT gateways may not be available in all AWS regions. Default: NatProvider.gateway()
        :param nat_gateways: The number of NAT Gateways/Instances to create. The type of NAT gateway or instance will be determined by the ``natGatewayProvider`` parameter. You can set this number lower than the number of Availability Zones in your VPC in order to save on NAT cost. Be aware you may be charged for cross-AZ data traffic instead. Default: - One NAT gateway/instance per Availability Zone
        :param nat_gateway_subnets: Configures the subnets which will have NAT Gateways/Instances. You can pick a specific group of subnets by specifying the group name; the picked subnets must be public subnets. Only necessary if you have more than one public subnet group. Default: - All public subnets.
        :param subnet_configuration: Configure the subnets to build for each AZ. Each entry in this list configures a Subnet Group; each group will contain a subnet for each Availability Zone. For example, if you want 1 public subnet, 1 private subnet, and 1 isolated subnet in each AZ provide the following:: new ec2.Vpc(this, 'VPC', { subnetConfiguration: [ { cidrMask: 24, name: 'ingress', subnetType: ec2.SubnetType.PUBLIC, }, { cidrMask: 24, name: 'application', subnetType: ec2.SubnetType.PRIVATE_WITH_NAT, }, { cidrMask: 28, name: 'rds', subnetType: ec2.SubnetType.PRIVATE_ISOLATED, } ] }); Default: - The VPC CIDR will be evenly divided between 1 public and 1 private subnet per AZ.
        :param vpn_connections: VPN connections to this VPC. Default: - No connections.
        :param vpn_gateway: Indicates whether a VPN gateway should be created and attached to this VPC. Default: - true when vpnGatewayAsn or vpnConnections is specified
        :param vpn_gateway_asn: The private Autonomous System Number (ASN) for the VPN gateway. Default: - Amazon default ASN.
        :param vpn_route_propagation: Where to propagate VPN routes. Default: - On the route tables associated with private subnets. If no private subnets exists, isolated subnets are used. If no isolated subnets exists, public subnets are used.
        '''
        props = aws_cdk.aws_ec2.VpcProps(
            cidr=cidr,
            default_instance_tenancy=default_instance_tenancy,
            enable_dns_hostnames=enable_dns_hostnames,
            enable_dns_support=enable_dns_support,
            flow_logs=flow_logs,
            gateway_endpoints=gateway_endpoints,
            max_azs=max_azs,
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=nat_gateways,
            nat_gateway_subnets=nat_gateway_subnets,
            subnet_configuration=subnet_configuration,
            vpn_connections=vpn_connections,
            vpn_gateway=vpn_gateway,
            vpn_gateway_asn=vpn_gateway_asn,
            vpn_route_propagation=vpn_route_propagation,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class CreateTags(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-vpc.CreateTags",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        resource_ids: typing.Sequence[builtins.str],
        tags: typing.Sequence["Tag"],
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param resource_ids: (experimental) The IDs of the ec2 resources, separated by spaces. Constraints: Up to 1000 resource IDs. We recommend breaking up this request into smaller batches.
        :param tags: (experimental) The tags. The value parameter is required, but if you don't want the tag to have a value, specify the parameter with no value, and we set the value to an empty string.
        :param removal_policy: 
        '''
        props = CreateTagsProps(
            resource_ids=resource_ids, tags=tags, removal_policy=removal_policy
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-vpc.CreateTagsProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource_ids": "resourceIds",
        "tags": "tags",
        "removal_policy": "removalPolicy",
    },
)
class CreateTagsProps:
    def __init__(
        self,
        *,
        resource_ids: typing.Sequence[builtins.str],
        tags: typing.Sequence["Tag"],
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''(experimental) Adds or overwrites only the specified tags for the specified Amazon EC2 resource or resources.

        When you specify an existing tag key, the value is overwritten with the new value. Each resource can have a maximum of 50 tags. Each tag consists of a key and optional value. Tag keys must be unique per resource.

        :param resource_ids: (experimental) The IDs of the ec2 resources, separated by spaces. Constraints: Up to 1000 resource IDs. We recommend breaking up this request into smaller batches.
        :param tags: (experimental) The tags. The value parameter is required, but if you don't want the tag to have a value, specify the parameter with no value, and we set the value to an empty string.
        :param removal_policy: 

        :see: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateTags.html
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_ids": resource_ids,
            "tags": tags,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def resource_ids(self) -> typing.List[builtins.str]:
        '''(experimental) The IDs of the ec2 resources, separated by spaces.

        Constraints: Up to 1000 resource IDs. We recommend breaking up this request into smaller batches.

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html#tag-resources
        :stability: experimental
        '''
        result = self._values.get("resource_ids")
        assert result is not None, "Required property 'resource_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.List["Tag"]:
        '''(experimental) The tags.

        The value parameter is required, but if you don't want the tag to have a value, specify the parameter with no value, and we set the value to an empty string.

        :stability: experimental
        '''
        result = self._values.get("tags")
        assert result is not None, "Required property 'tags' is missing"
        return typing.cast(typing.List["Tag"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''
        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateTagsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-vpc.Tag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class Tag:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: The key of the tag. Constraints: Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws:.
        :param value: The value of the tag. Constraints: Tag values are case-sensitive and accept a maximum of 256 Unicode characters.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''The key of the tag.

        Constraints: Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws:.
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The value of the tag.

        Constraints: Tag values are case-sensitive and accept a maximum of 256 Unicode characters.
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Tag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CheapVpc",
    "CreateTags",
    "CreateTagsProps",
    "Tag",
]

publication.publish()
