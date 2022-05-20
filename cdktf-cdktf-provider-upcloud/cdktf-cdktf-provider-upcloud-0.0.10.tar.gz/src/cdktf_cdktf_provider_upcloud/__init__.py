'''
# Terraform CDK upcloud Provider ~> 2.4

This repo builds and publishes the Terraform upcloud Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-upcloud](https://www.npmjs.com/package/@cdktf/provider-upcloud).

`npm install @cdktf/provider-upcloud`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-upcloud](https://pypi.org/project/cdktf-cdktf-provider-upcloud).

`pipenv install cdktf-cdktf-provider-upcloud`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Upcloud](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Upcloud).

`dotnet add package HashiCorp.Cdktf.Providers.Upcloud`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-upcloud](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-upcloud).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-upcloud</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform upcloud Provider version 1:1. In fact, it always tracks `latest` of `~> 2.4` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform upcloud Provider](https://github.com/terraform-providers/terraform-provider-upcloud)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform upcloud Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
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

import cdktf
import constructs


class DataUpcloudHosts(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudHosts",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/hosts upcloud_hosts}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/hosts upcloud_hosts} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudHostsConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> "DataUpcloudHostsHostsList":
        return typing.cast("DataUpcloudHostsHostsList", jsii.get(self, "hosts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudHostsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataUpcloudHostsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudHostsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudHostsHosts",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudHostsHosts:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudHostsHosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudHostsHostsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudHostsHostsList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataUpcloudHostsHostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudHostsHostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudHostsHostsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudHostsHostsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostId")
    def host_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hostId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudHostsHosts]:
        return typing.cast(typing.Optional[DataUpcloudHostsHosts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataUpcloudHostsHosts]) -> None:
        jsii.set(self, "internalValue", value)


class DataUpcloudIpAddresses(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudIpAddresses",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/ip_addresses upcloud_ip_addresses}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/ip_addresses upcloud_ip_addresses} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudIpAddressesConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> "DataUpcloudIpAddressesAddressesList":
        return typing.cast("DataUpcloudIpAddressesAddressesList", jsii.get(self, "addresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudIpAddressesAddresses",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudIpAddressesAddresses:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudIpAddressesAddresses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudIpAddressesAddressesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudIpAddressesAddressesList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataUpcloudIpAddressesAddressesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudIpAddressesAddressesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudIpAddressesAddressesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudIpAddressesAddressesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="access")
    def access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "access"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="floating")
    def floating(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "floating"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mac")
    def mac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mac"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partOfPlan")
    def part_of_plan(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "partOfPlan"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ptrRecord")
    def ptr_record(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ptrRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="server")
    def server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "server"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudIpAddressesAddresses]:
        return typing.cast(typing.Optional[DataUpcloudIpAddressesAddresses], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataUpcloudIpAddressesAddresses],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudIpAddressesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataUpcloudIpAddressesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudIpAddressesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudNetworks(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworks",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/networks upcloud_networks}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filter_name: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/networks upcloud_networks} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter_name: If specified, results will be filtered to match name using a regular expression. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#filter_name DataUpcloudNetworks#filter_name}
        :param zone: If specified, this data source will return only networks from this zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#zone DataUpcloudNetworks#zone}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudNetworksConfig(
            filter_name=filter_name,
            zone=zone,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetFilterName")
    def reset_filter_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterName", []))

    @jsii.member(jsii_name="resetZone")
    def reset_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZone", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networks")
    def networks(self) -> "DataUpcloudNetworksNetworksList":
        return typing.cast("DataUpcloudNetworksNetworksList", jsii.get(self, "networks"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterNameInput")
    def filter_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterName")
    def filter_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterName"))

    @filter_name.setter
    def filter_name(self, value: builtins.str) -> None:
        jsii.set(self, "filterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter_name": "filterName",
        "zone": "zone",
    },
)
class DataUpcloudNetworksConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter_name: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter_name: If specified, results will be filtered to match name using a regular expression. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#filter_name DataUpcloudNetworks#filter_name}
        :param zone: If specified, this data source will return only networks from this zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#zone DataUpcloudNetworks#zone}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if filter_name is not None:
            self._values["filter_name"] = filter_name
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def filter_name(self) -> typing.Optional[builtins.str]:
        '''If specified, results will be filtered to match name using a regular expression.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#filter_name DataUpcloudNetworks#filter_name}
        '''
        result = self._values.get("filter_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''If specified, this data source will return only networks from this zone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/networks#zone DataUpcloudNetworks#zone}
        '''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudNetworksConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworks",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudNetworksNetworks:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudNetworksNetworks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksIpNetwork",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudNetworksNetworksIpNetwork:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudNetworksNetworksIpNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudNetworksNetworksIpNetworkList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksIpNetworkList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataUpcloudNetworksNetworksIpNetworkOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudNetworksNetworksIpNetworkOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudNetworksNetworksIpNetworkOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksIpNetworkOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "dhcp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDefaultRoute")
    def dhcp_default_route(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "dhcpDefaultRoute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDns")
    def dhcp_dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dhcpDns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudNetworksNetworksIpNetwork]:
        return typing.cast(typing.Optional[DataUpcloudNetworksNetworksIpNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataUpcloudNetworksNetworksIpNetwork],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataUpcloudNetworksNetworksList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataUpcloudNetworksNetworksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudNetworksNetworksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudNetworksNetworksOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipNetwork")
    def ip_network(self) -> DataUpcloudNetworksNetworksIpNetworkList:
        return typing.cast(DataUpcloudNetworksNetworksIpNetworkList, jsii.get(self, "ipNetwork"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servers")
    def servers(self) -> "DataUpcloudNetworksNetworksServersList":
        return typing.cast("DataUpcloudNetworksNetworksServersList", jsii.get(self, "servers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudNetworksNetworks]:
        return typing.cast(typing.Optional[DataUpcloudNetworksNetworks], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataUpcloudNetworksNetworks],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksServers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudNetworksNetworksServers:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudNetworksNetworksServers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudNetworksNetworksServersList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksServersList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataUpcloudNetworksNetworksServersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudNetworksNetworksServersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudNetworksNetworksServersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudNetworksNetworksServersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudNetworksNetworksServers]:
        return typing.cast(typing.Optional[DataUpcloudNetworksNetworksServers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataUpcloudNetworksNetworksServers],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataUpcloudStorage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudStorage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/storage upcloud_storage}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        type: builtins.str,
        access_type: typing.Optional[builtins.str] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        name_regex: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/storage upcloud_storage} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param type: Storage type (normal, backup, cdrom, template). Use 'favorite' as type to filter storages on the list of favorites. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#type DataUpcloudStorage#type}
        :param access_type: Storage access type (public, private). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#access_type DataUpcloudStorage#access_type}
        :param most_recent: If more than one result is returned, use the most recent storage. This is only useful with private storages. Public storages might give unpredictable results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#most_recent DataUpcloudStorage#most_recent}
        :param name: Exact name of the storage (same as title). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name DataUpcloudStorage#name}
        :param name_regex: Use regular expression to match storage name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name_regex DataUpcloudStorage#name_regex}
        :param zone: The zone in which the storage resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#zone DataUpcloudStorage#zone}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudStorageConfig(
            type=type,
            access_type=access_type,
            most_recent=most_recent,
            name=name,
            name_regex=name_regex,
            zone=zone,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccessType")
    def reset_access_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessType", []))

    @jsii.member(jsii_name="resetMostRecent")
    def reset_most_recent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMostRecent", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNameRegex")
    def reset_name_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameRegex", []))

    @jsii.member(jsii_name="resetZone")
    def reset_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZone", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tier")
    def tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessTypeInput")
    def access_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecentInput")
    def most_recent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mostRecentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegexInput")
    def name_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessType")
    def access_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessType"))

    @access_type.setter
    def access_type(self, value: builtins.str) -> None:
        jsii.set(self, "accessType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecent")
    def most_recent(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mostRecent"))

    @most_recent.setter
    def most_recent(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "mostRecent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegex")
    def name_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameRegex"))

    @name_regex.setter
    def name_regex(self, value: builtins.str) -> None:
        jsii.set(self, "nameRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudStorageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "type": "type",
        "access_type": "accessType",
        "most_recent": "mostRecent",
        "name": "name",
        "name_regex": "nameRegex",
        "zone": "zone",
    },
)
class DataUpcloudStorageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        type: builtins.str,
        access_type: typing.Optional[builtins.str] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        name_regex: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param type: Storage type (normal, backup, cdrom, template). Use 'favorite' as type to filter storages on the list of favorites. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#type DataUpcloudStorage#type}
        :param access_type: Storage access type (public, private). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#access_type DataUpcloudStorage#access_type}
        :param most_recent: If more than one result is returned, use the most recent storage. This is only useful with private storages. Public storages might give unpredictable results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#most_recent DataUpcloudStorage#most_recent}
        :param name: Exact name of the storage (same as title). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name DataUpcloudStorage#name}
        :param name_regex: Use regular expression to match storage name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name_regex DataUpcloudStorage#name_regex}
        :param zone: The zone in which the storage resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#zone DataUpcloudStorage#zone}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access_type is not None:
            self._values["access_type"] = access_type
        if most_recent is not None:
            self._values["most_recent"] = most_recent
        if name is not None:
            self._values["name"] = name
        if name_regex is not None:
            self._values["name_regex"] = name_regex
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Storage type (normal, backup, cdrom, template). Use 'favorite' as type to filter storages on the list of favorites.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#type DataUpcloudStorage#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_type(self) -> typing.Optional[builtins.str]:
        '''Storage access type (public, private).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#access_type DataUpcloudStorage#access_type}
        '''
        result = self._values.get("access_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def most_recent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If more than one result is returned, use the most recent storage.

        This is only useful with private storages. Public storages might give unpredictable results.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#most_recent DataUpcloudStorage#most_recent}
        '''
        result = self._values.get("most_recent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Exact name of the storage (same as title).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name DataUpcloudStorage#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_regex(self) -> typing.Optional[builtins.str]:
        '''Use regular expression to match storage name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#name_regex DataUpcloudStorage#name_regex}
        '''
        result = self._values.get("name_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''The zone in which the storage resides.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/storage#zone DataUpcloudStorage#zone}
        '''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudStorageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudTags(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudTags",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/tags upcloud_tags}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/tags upcloud_tags} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudTagsConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> "DataUpcloudTagsTagsList":
        return typing.cast("DataUpcloudTagsTagsList", jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudTagsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataUpcloudTagsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudTagsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudTagsTags",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataUpcloudTagsTags:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudTagsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudTagsTagsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudTagsTagsList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataUpcloudTagsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataUpcloudTagsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataUpcloudTagsTagsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudTagsTagsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servers")
    def servers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "servers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataUpcloudTagsTags]:
        return typing.cast(typing.Optional[DataUpcloudTagsTags], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DataUpcloudTagsTags]) -> None:
        jsii.set(self, "internalValue", value)


class DataUpcloudZone(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudZone",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/zone upcloud_zone}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/zone upcloud_zone} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Unique lablel for the zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zone#name DataUpcloudZone#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudZoneConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="public")
    def public(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "public"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudZoneConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataUpcloudZoneConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Unique lablel for the zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zone#name DataUpcloudZone#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Unique lablel for the zone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zone#name DataUpcloudZone#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudZoneConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataUpcloudZones(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.DataUpcloudZones",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/d/zones upcloud_zones}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filter_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/d/zones upcloud_zones} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zones#filter_type DataUpcloudZones#filter_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataUpcloudZonesConfig(
            filter_type=filter_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetFilterType")
    def reset_filter_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilterType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneIds")
    def zone_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "zoneIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterTypeInput")
    def filter_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterType")
    def filter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filterType"))

    @filter_type.setter
    def filter_type(self, value: builtins.str) -> None:
        jsii.set(self, "filterType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.DataUpcloudZonesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter_type": "filterType",
    },
)
class DataUpcloudZonesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zones#filter_type DataUpcloudZones#filter_type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if filter_type is not None:
            self._values["filter_type"] = filter_type

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def filter_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/d/zones#filter_type DataUpcloudZones#filter_type}.'''
        result = self._values.get("filter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataUpcloudZonesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirewallRules(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.FirewallRules",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules upcloud_firewall_rules}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firewall_rule: typing.Union[typing.Sequence["FirewallRulesFirewallRule"], cdktf.IResolvable],
        server_id: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules upcloud_firewall_rules} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param firewall_rule: firewall_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        :param server_id: The unique id of the server to be protected the firewall rules. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#server_id FirewallRules#server_id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FirewallRulesConfig(
            firewall_rule=firewall_rule,
            server_id=server_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleInput")
    def firewall_rule_input(
        self,
    ) -> typing.Optional[typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable]], jsii.get(self, "firewallRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdInput")
    def server_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRule")
    def firewall_rule(
        self,
    ) -> typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable]:
        return typing.cast(typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable], jsii.get(self, "firewallRule"))

    @firewall_rule.setter
    def firewall_rule(
        self,
        value: typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "firewallRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverId")
    def server_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverId"))

    @server_id.setter
    def server_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.FirewallRulesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "firewall_rule": "firewallRule",
        "server_id": "serverId",
    },
)
class FirewallRulesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        firewall_rule: typing.Union[typing.Sequence["FirewallRulesFirewallRule"], cdktf.IResolvable],
        server_id: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param firewall_rule: firewall_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        :param server_id: The unique id of the server to be protected the firewall rules. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#server_id FirewallRules#server_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "firewall_rule": firewall_rule,
            "server_id": server_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def firewall_rule(
        self,
    ) -> typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable]:
        '''firewall_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#firewall_rule FirewallRules#firewall_rule}
        '''
        result = self._values.get("firewall_rule")
        assert result is not None, "Required property 'firewall_rule' is missing"
        return typing.cast(typing.Union[typing.List["FirewallRulesFirewallRule"], cdktf.IResolvable], result)

    @builtins.property
    def server_id(self) -> builtins.str:
        '''The unique id of the server to be protected the firewall rules.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#server_id FirewallRules#server_id}
        '''
        result = self._values.get("server_id")
        assert result is not None, "Required property 'server_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRulesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.FirewallRulesFirewallRule",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "direction": "direction",
        "family": "family",
        "comment": "comment",
        "destination_address_end": "destinationAddressEnd",
        "destination_address_start": "destinationAddressStart",
        "destination_port_end": "destinationPortEnd",
        "destination_port_start": "destinationPortStart",
        "icmp_type": "icmpType",
        "protocol": "protocol",
        "source_address_end": "sourceAddressEnd",
        "source_address_start": "sourceAddressStart",
        "source_port_end": "sourcePortEnd",
        "source_port_start": "sourcePortStart",
    },
)
class FirewallRulesFirewallRule:
    def __init__(
        self,
        *,
        action: builtins.str,
        direction: builtins.str,
        family: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        destination_address_end: typing.Optional[builtins.str] = None,
        destination_address_start: typing.Optional[builtins.str] = None,
        destination_port_end: typing.Optional[builtins.str] = None,
        destination_port_start: typing.Optional[builtins.str] = None,
        icmp_type: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        source_address_end: typing.Optional[builtins.str] = None,
        source_address_start: typing.Optional[builtins.str] = None,
        source_port_end: typing.Optional[builtins.str] = None,
        source_port_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: Action to take if the rule conditions are met. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#action FirewallRules#action}
        :param direction: The direction of network traffic this rule will be applied to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#direction FirewallRules#direction}
        :param family: The address family of new firewall rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#family FirewallRules#family}
        :param comment: Freeform comment string for the rule. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#comment FirewallRules#comment}
        :param destination_address_end: The destination address range ends from this address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_address_end FirewallRules#destination_address_end}
        :param destination_address_start: The destination address range starts from this address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_address_start FirewallRules#destination_address_start}
        :param destination_port_end: The destination port range ends from this port number. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_port_end FirewallRules#destination_port_end}
        :param destination_port_start: The destination port range starts from this port number. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_port_start FirewallRules#destination_port_start}
        :param icmp_type: The ICMP type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#icmp_type FirewallRules#icmp_type}
        :param protocol: The protocol this rule will be applied to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#protocol FirewallRules#protocol}
        :param source_address_end: The source address range ends from this address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_address_end FirewallRules#source_address_end}
        :param source_address_start: The source address range starts from this address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_address_start FirewallRules#source_address_start}
        :param source_port_end: The source port range ends from this port number. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_port_end FirewallRules#source_port_end}
        :param source_port_start: The source port range starts from this port number. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_port_start FirewallRules#source_port_start}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "direction": direction,
            "family": family,
        }
        if comment is not None:
            self._values["comment"] = comment
        if destination_address_end is not None:
            self._values["destination_address_end"] = destination_address_end
        if destination_address_start is not None:
            self._values["destination_address_start"] = destination_address_start
        if destination_port_end is not None:
            self._values["destination_port_end"] = destination_port_end
        if destination_port_start is not None:
            self._values["destination_port_start"] = destination_port_start
        if icmp_type is not None:
            self._values["icmp_type"] = icmp_type
        if protocol is not None:
            self._values["protocol"] = protocol
        if source_address_end is not None:
            self._values["source_address_end"] = source_address_end
        if source_address_start is not None:
            self._values["source_address_start"] = source_address_start
        if source_port_end is not None:
            self._values["source_port_end"] = source_port_end
        if source_port_start is not None:
            self._values["source_port_start"] = source_port_start

    @builtins.property
    def action(self) -> builtins.str:
        '''Action to take if the rule conditions are met.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#action FirewallRules#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> builtins.str:
        '''The direction of network traffic this rule will be applied to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#direction FirewallRules#direction}
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def family(self) -> builtins.str:
        '''The address family of new firewall rule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#family FirewallRules#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Freeform comment string for the rule.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#comment FirewallRules#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_address_end(self) -> typing.Optional[builtins.str]:
        '''The destination address range ends from this address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_address_end FirewallRules#destination_address_end}
        '''
        result = self._values.get("destination_address_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_address_start(self) -> typing.Optional[builtins.str]:
        '''The destination address range starts from this address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_address_start FirewallRules#destination_address_start}
        '''
        result = self._values.get("destination_address_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_port_end(self) -> typing.Optional[builtins.str]:
        '''The destination port range ends from this port number.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_port_end FirewallRules#destination_port_end}
        '''
        result = self._values.get("destination_port_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_port_start(self) -> typing.Optional[builtins.str]:
        '''The destination port range starts from this port number.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#destination_port_start FirewallRules#destination_port_start}
        '''
        result = self._values.get("destination_port_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def icmp_type(self) -> typing.Optional[builtins.str]:
        '''The ICMP type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#icmp_type FirewallRules#icmp_type}
        '''
        result = self._values.get("icmp_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''The protocol this rule will be applied to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#protocol FirewallRules#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_address_end(self) -> typing.Optional[builtins.str]:
        '''The source address range ends from this address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_address_end FirewallRules#source_address_end}
        '''
        result = self._values.get("source_address_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_address_start(self) -> typing.Optional[builtins.str]:
        '''The source address range starts from this address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_address_start FirewallRules#source_address_start}
        '''
        result = self._values.get("source_address_start")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_port_end(self) -> typing.Optional[builtins.str]:
        '''The source port range ends from this port number.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_port_end FirewallRules#source_port_end}
        '''
        result = self._values.get("source_port_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_port_start(self) -> typing.Optional[builtins.str]:
        '''The source port range starts from this port number.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/firewall_rules#source_port_start FirewallRules#source_port_start}
        '''
        result = self._values.get("source_port_start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRulesFirewallRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FloatingIpAddress(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.FloatingIpAddress",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address upcloud_floating_ip_address}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access: typing.Optional[builtins.str] = None,
        family: typing.Optional[builtins.str] = None,
        mac_address: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address upcloud_floating_ip_address} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access: Is address for utility or public network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#access FloatingIpAddress#access}
        :param family: The address family of new IP address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#family FloatingIpAddress#family}
        :param mac_address: MAC address of server interface to assign address to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#mac_address FloatingIpAddress#mac_address}
        :param zone: Zone of address, required when assigning a detached floating IP address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#zone FloatingIpAddress#zone}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FloatingIpAddressConfig(
            access=access,
            family=family,
            mac_address=mac_address,
            zone=zone,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccess")
    def reset_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccess", []))

    @jsii.member(jsii_name="resetFamily")
    def reset_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFamily", []))

    @jsii.member(jsii_name="resetMacAddress")
    def reset_mac_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMacAddress", []))

    @jsii.member(jsii_name="resetZone")
    def reset_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZone", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessInput")
    def access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="macAddressInput")
    def mac_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "macAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="access")
    def access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "access"))

    @access.setter
    def access(self, value: builtins.str) -> None:
        jsii.set(self, "access", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="macAddress")
    def mac_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "macAddress"))

    @mac_address.setter
    def mac_address(self, value: builtins.str) -> None:
        jsii.set(self, "macAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.FloatingIpAddressConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access": "access",
        "family": "family",
        "mac_address": "macAddress",
        "zone": "zone",
    },
)
class FloatingIpAddressConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access: typing.Optional[builtins.str] = None,
        family: typing.Optional[builtins.str] = None,
        mac_address: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access: Is address for utility or public network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#access FloatingIpAddress#access}
        :param family: The address family of new IP address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#family FloatingIpAddress#family}
        :param mac_address: MAC address of server interface to assign address to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#mac_address FloatingIpAddress#mac_address}
        :param zone: Zone of address, required when assigning a detached floating IP address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#zone FloatingIpAddress#zone}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access is not None:
            self._values["access"] = access
        if family is not None:
            self._values["family"] = family
        if mac_address is not None:
            self._values["mac_address"] = mac_address
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def access(self) -> typing.Optional[builtins.str]:
        '''Is address for utility or public network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#access FloatingIpAddress#access}
        '''
        result = self._values.get("access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def family(self) -> typing.Optional[builtins.str]:
        '''The address family of new IP address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#family FloatingIpAddress#family}
        '''
        result = self._values.get("family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mac_address(self) -> typing.Optional[builtins.str]:
        '''MAC address of server interface to assign address to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#mac_address FloatingIpAddress#mac_address}
        '''
        result = self._values.get("mac_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''Zone of address, required when assigning a detached floating IP address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/floating_ip_address#zone FloatingIpAddress#zone}
        '''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FloatingIpAddressConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Loadbalancer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Loadbalancer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer upcloud_loadbalancer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        network: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        configured_status: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer upcloud_loadbalancer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the service must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#name Loadbalancer#name}
        :param network: Private network UUID where traffic will be routed. Must reside in load balancer zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#network Loadbalancer#network}
        :param plan: Plan which the service will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#plan Loadbalancer#plan}
        :param zone: Zone in which the service will be hosted, e.g. ``fi-hel1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#zone Loadbalancer#zone}
        :param configured_status: The service configured status indicates the service's current intended status. Managed by the customer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#configured_status Loadbalancer#configured_status}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerConfig(
            name=name,
            network=network,
            plan=plan,
            zone=zone,
            configured_status=configured_status,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetConfiguredStatus")
    def reset_configured_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguredStatus", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backends")
    def backends(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "backends"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frontends")
    def frontends(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "frontends"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationalState")
    def operational_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationalState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolvers")
    def resolvers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resolvers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuredStatusInput")
    def configured_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configuredStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuredStatus")
    def configured_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configuredStatus"))

    @configured_status.setter
    def configured_status(self, value: builtins.str) -> None:
        jsii.set(self, "configuredStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        jsii.set(self, "network", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        jsii.set(self, "plan", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


class LoadbalancerBackend(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerBackend",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend upcloud_loadbalancer_backend}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        loadbalancer: builtins.str,
        name: builtins.str,
        resolver_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend upcloud_loadbalancer_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param loadbalancer: ID of the load balancer to which the backend is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        :param name: The name of the backend must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#name LoadbalancerBackend#name}
        :param resolver_name: Domain Name Resolver used with dynamic type members. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerBackendConfig(
            loadbalancer=loadbalancer,
            name=name,
            resolver_name=resolver_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetResolverName")
    def reset_resolver_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResolverName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="members")
    def members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "members"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancerInput")
    def loadbalancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loadbalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolverNameInput")
    def resolver_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resolverNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(self, value: builtins.str) -> None:
        jsii.set(self, "loadbalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolverName")
    def resolver_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resolverName"))

    @resolver_name.setter
    def resolver_name(self, value: builtins.str) -> None:
        jsii.set(self, "resolverName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerBackendConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "loadbalancer": "loadbalancer",
        "name": "name",
        "resolver_name": "resolverName",
    },
)
class LoadbalancerBackendConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        loadbalancer: builtins.str,
        name: builtins.str,
        resolver_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param loadbalancer: ID of the load balancer to which the backend is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        :param name: The name of the backend must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#name LoadbalancerBackend#name}
        :param resolver_name: Domain Name Resolver used with dynamic type members. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "loadbalancer": loadbalancer,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if resolver_name is not None:
            self._values["resolver_name"] = resolver_name

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def loadbalancer(self) -> builtins.str:
        '''ID of the load balancer to which the backend is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#loadbalancer LoadbalancerBackend#loadbalancer}
        '''
        result = self._values.get("loadbalancer")
        assert result is not None, "Required property 'loadbalancer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the backend must be unique within the load balancer service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#name LoadbalancerBackend#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resolver_name(self) -> typing.Optional[builtins.str]:
        '''Domain Name Resolver used with dynamic type members.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_backend#resolver_name LoadbalancerBackend#resolver_name}
        '''
        result = self._values.get("resolver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "network": "network",
        "plan": "plan",
        "zone": "zone",
        "configured_status": "configuredStatus",
    },
)
class LoadbalancerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        network: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        configured_status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the service must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#name Loadbalancer#name}
        :param network: Private network UUID where traffic will be routed. Must reside in load balancer zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#network Loadbalancer#network}
        :param plan: Plan which the service will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#plan Loadbalancer#plan}
        :param zone: Zone in which the service will be hosted, e.g. ``fi-hel1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#zone Loadbalancer#zone}
        :param configured_status: The service configured status indicates the service's current intended status. Managed by the customer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#configured_status Loadbalancer#configured_status}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "network": network,
            "plan": plan,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if configured_status is not None:
            self._values["configured_status"] = configured_status

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the service must be unique within customer account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#name Loadbalancer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network(self) -> builtins.str:
        '''Private network UUID where traffic will be routed. Must reside in load balancer zone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#network Loadbalancer#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Plan which the service will have.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#plan Loadbalancer#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone in which the service will be hosted, e.g. ``fi-hel1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#zone Loadbalancer#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configured_status(self) -> typing.Optional[builtins.str]:
        '''The service configured status indicates the service's current intended status. Managed by the customer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer#configured_status Loadbalancer#configured_status}
        '''
        result = self._values.get("configured_status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerDynamicBackendMember(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerDynamicBackendMember",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member upcloud_loadbalancer_dynamic_backend_member}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backend: builtins.str,
        max_sessions: jsii.Number,
        name: builtins.str,
        weight: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ip: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member upcloud_loadbalancer_dynamic_backend_member} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: ID of the load balancer backend to which the member is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#backend LoadbalancerDynamicBackendMember#backend}
        :param max_sessions: Maximum number of sessions before queueing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#max_sessions LoadbalancerDynamicBackendMember#max_sessions}
        :param name: The name of the member must be unique within the load balancer backend service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#name LoadbalancerDynamicBackendMember#name}
        :param weight: Used to adjust the server's weight relative to other servers. All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load. A value of 0 means the server will not participate in load balancing but will still accept persistent connections. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#weight LoadbalancerDynamicBackendMember#weight}
        :param enabled: Indicates if the member is enabled. Disabled members are excluded from load balancing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#enabled LoadbalancerDynamicBackendMember#enabled}
        :param ip: Optional fallback IP address in case of failure on DNS resolving. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#ip LoadbalancerDynamicBackendMember#ip}
        :param port: Server port. Port is optional and can be specified in DNS SRV record. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#port LoadbalancerDynamicBackendMember#port}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerDynamicBackendMemberConfig(
            backend=backend,
            max_sessions=max_sessions,
            name=name,
            weight=weight,
            enabled=enabled,
            ip=ip,
            port=port,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessionsInput")
    def max_sessions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSessionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        jsii.set(self, "backend", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        jsii.set(self, "ip", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessions")
    def max_sessions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSessions"))

    @max_sessions.setter
    def max_sessions(self, value: jsii.Number) -> None:
        jsii.set(self, "maxSessions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        jsii.set(self, "weight", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerDynamicBackendMemberConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backend": "backend",
        "max_sessions": "maxSessions",
        "name": "name",
        "weight": "weight",
        "enabled": "enabled",
        "ip": "ip",
        "port": "port",
    },
)
class LoadbalancerDynamicBackendMemberConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backend: builtins.str,
        max_sessions: jsii.Number,
        name: builtins.str,
        weight: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ip: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backend: ID of the load balancer backend to which the member is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#backend LoadbalancerDynamicBackendMember#backend}
        :param max_sessions: Maximum number of sessions before queueing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#max_sessions LoadbalancerDynamicBackendMember#max_sessions}
        :param name: The name of the member must be unique within the load balancer backend service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#name LoadbalancerDynamicBackendMember#name}
        :param weight: Used to adjust the server's weight relative to other servers. All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load. A value of 0 means the server will not participate in load balancing but will still accept persistent connections. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#weight LoadbalancerDynamicBackendMember#weight}
        :param enabled: Indicates if the member is enabled. Disabled members are excluded from load balancing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#enabled LoadbalancerDynamicBackendMember#enabled}
        :param ip: Optional fallback IP address in case of failure on DNS resolving. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#ip LoadbalancerDynamicBackendMember#ip}
        :param port: Server port. Port is optional and can be specified in DNS SRV record. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#port LoadbalancerDynamicBackendMember#port}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "backend": backend,
            "max_sessions": max_sessions,
            "name": name,
            "weight": weight,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if ip is not None:
            self._values["ip"] = ip
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def backend(self) -> builtins.str:
        '''ID of the load balancer backend to which the member is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#backend LoadbalancerDynamicBackendMember#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_sessions(self) -> jsii.Number:
        '''Maximum number of sessions before queueing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#max_sessions LoadbalancerDynamicBackendMember#max_sessions}
        '''
        result = self._values.get("max_sessions")
        assert result is not None, "Required property 'max_sessions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the member must be unique within the load balancer backend service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#name LoadbalancerDynamicBackendMember#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def weight(self) -> jsii.Number:
        '''Used to adjust the server's weight relative to other servers.

        All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load.
        A value of 0 means the server will not participate in load balancing but will still accept persistent connections.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#weight LoadbalancerDynamicBackendMember#weight}
        '''
        result = self._values.get("weight")
        assert result is not None, "Required property 'weight' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Indicates if the member is enabled. Disabled members are excluded from load balancing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#enabled LoadbalancerDynamicBackendMember#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''Optional fallback IP address in case of failure on DNS resolving.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#ip LoadbalancerDynamicBackendMember#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Server port. Port is optional and can be specified in DNS SRV record.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_backend_member#port LoadbalancerDynamicBackendMember#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerDynamicBackendMemberConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerDynamicCertificateBundle(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerDynamicCertificateBundle",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle upcloud_loadbalancer_dynamic_certificate_bundle}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hostnames: typing.Sequence[builtins.str],
        key_type: builtins.str,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle upcloud_loadbalancer_dynamic_certificate_bundle} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param hostnames: Certificate hostnames. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#hostnames LoadbalancerDynamicCertificateBundle#hostnames}
        :param key_type: Private key type (``rsa`` / ``ecdsa``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#key_type LoadbalancerDynamicCertificateBundle#key_type}
        :param name: The name of the bundle must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#name LoadbalancerDynamicCertificateBundle#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerDynamicCertificateBundleConfig(
            hostnames=hostnames,
            key_type=key_type,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notBefore")
    def not_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBefore"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationalState")
    def operational_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationalState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnamesInput")
    def hostnames_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostnamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnames")
    def hostnames(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hostnames"))

    @hostnames.setter
    def hostnames(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "hostnames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        jsii.set(self, "keyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerDynamicCertificateBundleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "hostnames": "hostnames",
        "key_type": "keyType",
        "name": "name",
    },
)
class LoadbalancerDynamicCertificateBundleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        hostnames: typing.Sequence[builtins.str],
        key_type: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param hostnames: Certificate hostnames. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#hostnames LoadbalancerDynamicCertificateBundle#hostnames}
        :param key_type: Private key type (``rsa`` / ``ecdsa``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#key_type LoadbalancerDynamicCertificateBundle#key_type}
        :param name: The name of the bundle must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#name LoadbalancerDynamicCertificateBundle#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "hostnames": hostnames,
            "key_type": key_type,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def hostnames(self) -> typing.List[builtins.str]:
        '''Certificate hostnames.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#hostnames LoadbalancerDynamicCertificateBundle#hostnames}
        '''
        result = self._values.get("hostnames")
        assert result is not None, "Required property 'hostnames' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def key_type(self) -> builtins.str:
        '''Private key type (``rsa`` / ``ecdsa``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#key_type LoadbalancerDynamicCertificateBundle#key_type}
        '''
        result = self._values.get("key_type")
        assert result is not None, "Required property 'key_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the bundle must be unique within customer account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_dynamic_certificate_bundle#name LoadbalancerDynamicCertificateBundle#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerDynamicCertificateBundleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFrontend(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontend",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend upcloud_loadbalancer_frontend}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_backend_name: builtins.str,
        loadbalancer: builtins.str,
        mode: builtins.str,
        name: builtins.str,
        port: jsii.Number,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend upcloud_loadbalancer_frontend} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_backend_name: The name of the default backend where traffic will be routed. Note, default backend can be overwritten in frontend rules. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#default_backend_name LoadbalancerFrontend#default_backend_name}
        :param loadbalancer: ID of the load balancer to which the frontend is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#loadbalancer LoadbalancerFrontend#loadbalancer}
        :param mode: When load balancer operating in ``tcp`` mode it acts as a layer 4 proxy. In ``http`` mode it acts as a layer 7 proxy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#mode LoadbalancerFrontend#mode}
        :param name: The name of the frontend must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#name LoadbalancerFrontend#name}
        :param port: Port to listen incoming requests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#port LoadbalancerFrontend#port}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerFrontendConfig(
            default_backend_name=default_backend_name,
            loadbalancer=loadbalancer,
            mode=mode,
            name=name,
            port=port,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "rules"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsConfigs")
    def tls_configs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tlsConfigs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBackendNameInput")
    def default_backend_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultBackendNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancerInput")
    def loadbalancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loadbalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBackendName")
    def default_backend_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultBackendName"))

    @default_backend_name.setter
    def default_backend_name(self, value: builtins.str) -> None:
        jsii.set(self, "defaultBackendName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(self, value: builtins.str) -> None:
        jsii.set(self, "loadbalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "default_backend_name": "defaultBackendName",
        "loadbalancer": "loadbalancer",
        "mode": "mode",
        "name": "name",
        "port": "port",
    },
)
class LoadbalancerFrontendConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        default_backend_name: builtins.str,
        loadbalancer: builtins.str,
        mode: builtins.str,
        name: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param default_backend_name: The name of the default backend where traffic will be routed. Note, default backend can be overwritten in frontend rules. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#default_backend_name LoadbalancerFrontend#default_backend_name}
        :param loadbalancer: ID of the load balancer to which the frontend is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#loadbalancer LoadbalancerFrontend#loadbalancer}
        :param mode: When load balancer operating in ``tcp`` mode it acts as a layer 4 proxy. In ``http`` mode it acts as a layer 7 proxy. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#mode LoadbalancerFrontend#mode}
        :param name: The name of the frontend must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#name LoadbalancerFrontend#name}
        :param port: Port to listen incoming requests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#port LoadbalancerFrontend#port}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "default_backend_name": default_backend_name,
            "loadbalancer": loadbalancer,
            "mode": mode,
            "name": name,
            "port": port,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def default_backend_name(self) -> builtins.str:
        '''The name of the default backend where traffic will be routed.

        Note, default backend can be overwritten in frontend rules.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#default_backend_name LoadbalancerFrontend#default_backend_name}
        '''
        result = self._values.get("default_backend_name")
        assert result is not None, "Required property 'default_backend_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def loadbalancer(self) -> builtins.str:
        '''ID of the load balancer to which the frontend is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#loadbalancer LoadbalancerFrontend#loadbalancer}
        '''
        result = self._values.get("loadbalancer")
        assert result is not None, "Required property 'loadbalancer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mode(self) -> builtins.str:
        '''When load balancer operating in ``tcp`` mode it acts as a layer 4 proxy.

        In ``http`` mode it acts as a layer 7 proxy.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#mode LoadbalancerFrontend#mode}
        '''
        result = self._values.get("mode")
        assert result is not None, "Required property 'mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the frontend must be unique within the load balancer service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#name LoadbalancerFrontend#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Port to listen incoming requests.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend#port LoadbalancerFrontend#port}
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFrontendRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule upcloud_loadbalancer_frontend_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        frontend: builtins.str,
        name: builtins.str,
        priority: jsii.Number,
        actions: typing.Optional["LoadbalancerFrontendRuleActions"] = None,
        matchers: typing.Optional["LoadbalancerFrontendRuleMatchers"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule upcloud_loadbalancer_frontend_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param frontend: ID of the load balancer frontend to which the rule is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#frontend LoadbalancerFrontendRule#frontend}
        :param name: The name of the frontend rule must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        :param priority: Rule with the higher priority goes first. Rules with the same priority processed in alphabetical order. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#priority LoadbalancerFrontendRule#priority}
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#actions LoadbalancerFrontendRule#actions}
        :param matchers: matchers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#matchers LoadbalancerFrontendRule#matchers}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerFrontendRuleConfig(
            frontend=frontend,
            name=name,
            priority=priority,
            actions=actions,
            matchers=matchers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putActions")
    def put_actions(
        self,
        *,
        http_redirect: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsHttpRedirect"]]] = None,
        http_return: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsHttpReturn"]]] = None,
        tcp_reject: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsTcpReject"]]] = None,
        use_backend: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsUseBackend"]]] = None,
    ) -> None:
        '''
        :param http_redirect: http_redirect block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_redirect LoadbalancerFrontendRule#http_redirect}
        :param http_return: http_return block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_return LoadbalancerFrontendRule#http_return}
        :param tcp_reject: tcp_reject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#tcp_reject LoadbalancerFrontendRule#tcp_reject}
        :param use_backend: use_backend block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#use_backend LoadbalancerFrontendRule#use_backend}
        '''
        value = LoadbalancerFrontendRuleActions(
            http_redirect=http_redirect,
            http_return=http_return,
            tcp_reject=tcp_reject,
            use_backend=use_backend,
        )

        return typing.cast(None, jsii.invoke(self, "putActions", [value]))

    @jsii.member(jsii_name="putMatchers")
    def put_matchers(
        self,
        *,
        body_size: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersBodySize"]]] = None,
        body_size_range: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersBodySizeRange"]]] = None,
        cookie: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersCookie"]]] = None,
        header: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHeader"]]] = None,
        host: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHost"]]] = None,
        http_method: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHttpMethod"]]] = None,
        num_members_up: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersNumMembersUp"]]] = None,
        path: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersPath"]]] = None,
        src_ip: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcIp"]]] = None,
        src_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcPort"]]] = None,
        src_port_range: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcPortRange"]]] = None,
        url: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrl"]]] = None,
        url_param: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrlParam"]]] = None,
        url_query: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrlQuery"]]] = None,
    ) -> None:
        '''
        :param body_size: body_size block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size LoadbalancerFrontendRule#body_size}
        :param body_size_range: body_size_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size_range LoadbalancerFrontendRule#body_size_range}
        :param cookie: cookie block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#cookie LoadbalancerFrontendRule#cookie}
        :param header: header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#header LoadbalancerFrontendRule#header}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#host LoadbalancerFrontendRule#host}
        :param http_method: http_method block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_method LoadbalancerFrontendRule#http_method}
        :param num_members_up: num_members_up block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#num_members_up LoadbalancerFrontendRule#num_members_up}
        :param path: path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#path LoadbalancerFrontendRule#path}
        :param src_ip: src_ip block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_ip LoadbalancerFrontendRule#src_ip}
        :param src_port: src_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port LoadbalancerFrontendRule#src_port}
        :param src_port_range: src_port_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port_range LoadbalancerFrontendRule#src_port_range}
        :param url: url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url LoadbalancerFrontendRule#url}
        :param url_param: url_param block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_param LoadbalancerFrontendRule#url_param}
        :param url_query: url_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_query LoadbalancerFrontendRule#url_query}
        '''
        value = LoadbalancerFrontendRuleMatchers(
            body_size=body_size,
            body_size_range=body_size_range,
            cookie=cookie,
            header=header,
            host=host,
            http_method=http_method,
            num_members_up=num_members_up,
            path=path,
            src_ip=src_ip,
            src_port=src_port,
            src_port_range=src_port_range,
            url=url,
            url_param=url_param,
            url_query=url_query,
        )

        return typing.cast(None, jsii.invoke(self, "putMatchers", [value]))

    @jsii.member(jsii_name="resetActions")
    def reset_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActions", []))

    @jsii.member(jsii_name="resetMatchers")
    def reset_matchers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatchers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> "LoadbalancerFrontendRuleActionsOutputReference":
        return typing.cast("LoadbalancerFrontendRuleActionsOutputReference", jsii.get(self, "actions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchers")
    def matchers(self) -> "LoadbalancerFrontendRuleMatchersOutputReference":
        return typing.cast("LoadbalancerFrontendRuleMatchersOutputReference", jsii.get(self, "matchers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionsInput")
    def actions_input(self) -> typing.Optional["LoadbalancerFrontendRuleActions"]:
        return typing.cast(typing.Optional["LoadbalancerFrontendRuleActions"], jsii.get(self, "actionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frontendInput")
    def frontend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frontendInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchersInput")
    def matchers_input(self) -> typing.Optional["LoadbalancerFrontendRuleMatchers"]:
        return typing.cast(typing.Optional["LoadbalancerFrontendRuleMatchers"], jsii.get(self, "matchersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frontend")
    def frontend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frontend"))

    @frontend.setter
    def frontend(self, value: builtins.str) -> None:
        jsii.set(self, "frontend", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        jsii.set(self, "priority", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActions",
    jsii_struct_bases=[],
    name_mapping={
        "http_redirect": "httpRedirect",
        "http_return": "httpReturn",
        "tcp_reject": "tcpReject",
        "use_backend": "useBackend",
    },
)
class LoadbalancerFrontendRuleActions:
    def __init__(
        self,
        *,
        http_redirect: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsHttpRedirect"]]] = None,
        http_return: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsHttpReturn"]]] = None,
        tcp_reject: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsTcpReject"]]] = None,
        use_backend: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleActionsUseBackend"]]] = None,
    ) -> None:
        '''
        :param http_redirect: http_redirect block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_redirect LoadbalancerFrontendRule#http_redirect}
        :param http_return: http_return block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_return LoadbalancerFrontendRule#http_return}
        :param tcp_reject: tcp_reject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#tcp_reject LoadbalancerFrontendRule#tcp_reject}
        :param use_backend: use_backend block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#use_backend LoadbalancerFrontendRule#use_backend}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if http_redirect is not None:
            self._values["http_redirect"] = http_redirect
        if http_return is not None:
            self._values["http_return"] = http_return
        if tcp_reject is not None:
            self._values["tcp_reject"] = tcp_reject
        if use_backend is not None:
            self._values["use_backend"] = use_backend

    @builtins.property
    def http_redirect(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsHttpRedirect"]]]:
        '''http_redirect block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_redirect LoadbalancerFrontendRule#http_redirect}
        '''
        result = self._values.get("http_redirect")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsHttpRedirect"]]], result)

    @builtins.property
    def http_return(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsHttpReturn"]]]:
        '''http_return block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_return LoadbalancerFrontendRule#http_return}
        '''
        result = self._values.get("http_return")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsHttpReturn"]]], result)

    @builtins.property
    def tcp_reject(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]]]:
        '''tcp_reject block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#tcp_reject LoadbalancerFrontendRule#tcp_reject}
        '''
        result = self._values.get("tcp_reject")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]]], result)

    @builtins.property
    def use_backend(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]]]:
        '''use_backend block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#use_backend LoadbalancerFrontendRule#use_backend}
        '''
        result = self._values.get("use_backend")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActionsHttpRedirect",
    jsii_struct_bases=[],
    name_mapping={"location": "location"},
)
class LoadbalancerFrontendRuleActionsHttpRedirect:
    def __init__(self, *, location: builtins.str) -> None:
        '''
        :param location: Target location. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#location LoadbalancerFrontendRule#location}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "location": location,
        }

    @builtins.property
    def location(self) -> builtins.str:
        '''Target location.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#location LoadbalancerFrontendRule#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleActionsHttpRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActionsHttpReturn",
    jsii_struct_bases=[],
    name_mapping={
        "content_type": "contentType",
        "payload": "payload",
        "status": "status",
    },
)
class LoadbalancerFrontendRuleActionsHttpReturn:
    def __init__(
        self,
        *,
        content_type: builtins.str,
        payload: builtins.str,
        status: jsii.Number,
    ) -> None:
        '''
        :param content_type: Content type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#content_type LoadbalancerFrontendRule#content_type}
        :param payload: The payload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#payload LoadbalancerFrontendRule#payload}
        :param status: HTTP status code. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#status LoadbalancerFrontendRule#status}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content_type": content_type,
            "payload": payload,
            "status": status,
        }

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Content type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#content_type LoadbalancerFrontendRule#content_type}
        '''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def payload(self) -> builtins.str:
        '''The payload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#payload LoadbalancerFrontendRule#payload}
        '''
        result = self._values.get("payload")
        assert result is not None, "Required property 'payload' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> jsii.Number:
        '''HTTP status code.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#status LoadbalancerFrontendRule#status}
        '''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleActionsHttpReturn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFrontendRuleActionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHttpRedirect")
    def reset_http_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpRedirect", []))

    @jsii.member(jsii_name="resetHttpReturn")
    def reset_http_return(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpReturn", []))

    @jsii.member(jsii_name="resetTcpReject")
    def reset_tcp_reject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTcpReject", []))

    @jsii.member(jsii_name="resetUseBackend")
    def reset_use_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseBackend", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpRedirectInput")
    def http_redirect_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpRedirect]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpRedirect]]], jsii.get(self, "httpRedirectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpReturnInput")
    def http_return_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpReturn]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpReturn]]], jsii.get(self, "httpReturnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpRejectInput")
    def tcp_reject_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]]], jsii.get(self, "tcpRejectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBackendInput")
    def use_backend_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]]], jsii.get(self, "useBackendInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpRedirect")
    def http_redirect(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpRedirect]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpRedirect]], jsii.get(self, "httpRedirect"))

    @http_redirect.setter
    def http_redirect(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpRedirect]],
    ) -> None:
        jsii.set(self, "httpRedirect", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpReturn")
    def http_return(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpReturn]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpReturn]], jsii.get(self, "httpReturn"))

    @http_return.setter
    def http_return(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleActionsHttpReturn]],
    ) -> None:
        jsii.set(self, "httpReturn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tcpReject")
    def tcp_reject(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]], jsii.get(self, "tcpReject"))

    @tcp_reject.setter
    def tcp_reject(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsTcpReject"]],
    ) -> None:
        jsii.set(self, "tcpReject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBackend")
    def use_backend(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]], jsii.get(self, "useBackend"))

    @use_backend.setter
    def use_backend(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleActionsUseBackend"]],
    ) -> None:
        jsii.set(self, "useBackend", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerFrontendRuleActions]:
        return typing.cast(typing.Optional[LoadbalancerFrontendRuleActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LoadbalancerFrontendRuleActions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActionsTcpReject",
    jsii_struct_bases=[],
    name_mapping={"active": "active"},
)
class LoadbalancerFrontendRuleActionsTcpReject:
    def __init__(
        self,
        *,
        active: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#active LoadbalancerFrontendRule#active}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if active is not None:
            self._values["active"] = active

    @builtins.property
    def active(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#active LoadbalancerFrontendRule#active}.'''
        result = self._values.get("active")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleActionsTcpReject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleActionsUseBackend",
    jsii_struct_bases=[],
    name_mapping={"backend_name": "backendName"},
)
class LoadbalancerFrontendRuleActionsUseBackend:
    def __init__(self, *, backend_name: builtins.str) -> None:
        '''
        :param backend_name: The name of the backend where traffic will be routed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#backend_name LoadbalancerFrontendRule#backend_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "backend_name": backend_name,
        }

    @builtins.property
    def backend_name(self) -> builtins.str:
        '''The name of the backend where traffic will be routed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#backend_name LoadbalancerFrontendRule#backend_name}
        '''
        result = self._values.get("backend_name")
        assert result is not None, "Required property 'backend_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleActionsUseBackend(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "frontend": "frontend",
        "name": "name",
        "priority": "priority",
        "actions": "actions",
        "matchers": "matchers",
    },
)
class LoadbalancerFrontendRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        frontend: builtins.str,
        name: builtins.str,
        priority: jsii.Number,
        actions: typing.Optional[LoadbalancerFrontendRuleActions] = None,
        matchers: typing.Optional["LoadbalancerFrontendRuleMatchers"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param frontend: ID of the load balancer frontend to which the rule is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#frontend LoadbalancerFrontendRule#frontend}
        :param name: The name of the frontend rule must be unique within the load balancer service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        :param priority: Rule with the higher priority goes first. Rules with the same priority processed in alphabetical order. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#priority LoadbalancerFrontendRule#priority}
        :param actions: actions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#actions LoadbalancerFrontendRule#actions}
        :param matchers: matchers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#matchers LoadbalancerFrontendRule#matchers}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(actions, dict):
            actions = LoadbalancerFrontendRuleActions(**actions)
        if isinstance(matchers, dict):
            matchers = LoadbalancerFrontendRuleMatchers(**matchers)
        self._values: typing.Dict[str, typing.Any] = {
            "frontend": frontend,
            "name": name,
            "priority": priority,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if actions is not None:
            self._values["actions"] = actions
        if matchers is not None:
            self._values["matchers"] = matchers

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def frontend(self) -> builtins.str:
        '''ID of the load balancer frontend to which the rule is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#frontend LoadbalancerFrontendRule#frontend}
        '''
        result = self._values.get("frontend")
        assert result is not None, "Required property 'frontend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the frontend rule must be unique within the load balancer service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Rule with the higher priority goes first. Rules with the same priority processed in alphabetical order.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#priority LoadbalancerFrontendRule#priority}
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def actions(self) -> typing.Optional[LoadbalancerFrontendRuleActions]:
        '''actions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#actions LoadbalancerFrontendRule#actions}
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[LoadbalancerFrontendRuleActions], result)

    @builtins.property
    def matchers(self) -> typing.Optional["LoadbalancerFrontendRuleMatchers"]:
        '''matchers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#matchers LoadbalancerFrontendRule#matchers}
        '''
        result = self._values.get("matchers")
        return typing.cast(typing.Optional["LoadbalancerFrontendRuleMatchers"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchers",
    jsii_struct_bases=[],
    name_mapping={
        "body_size": "bodySize",
        "body_size_range": "bodySizeRange",
        "cookie": "cookie",
        "header": "header",
        "host": "host",
        "http_method": "httpMethod",
        "num_members_up": "numMembersUp",
        "path": "path",
        "src_ip": "srcIp",
        "src_port": "srcPort",
        "src_port_range": "srcPortRange",
        "url": "url",
        "url_param": "urlParam",
        "url_query": "urlQuery",
    },
)
class LoadbalancerFrontendRuleMatchers:
    def __init__(
        self,
        *,
        body_size: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersBodySize"]]] = None,
        body_size_range: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersBodySizeRange"]]] = None,
        cookie: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersCookie"]]] = None,
        header: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHeader"]]] = None,
        host: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHost"]]] = None,
        http_method: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersHttpMethod"]]] = None,
        num_members_up: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersNumMembersUp"]]] = None,
        path: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersPath"]]] = None,
        src_ip: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcIp"]]] = None,
        src_port: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcPort"]]] = None,
        src_port_range: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersSrcPortRange"]]] = None,
        url: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrl"]]] = None,
        url_param: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrlParam"]]] = None,
        url_query: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["LoadbalancerFrontendRuleMatchersUrlQuery"]]] = None,
    ) -> None:
        '''
        :param body_size: body_size block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size LoadbalancerFrontendRule#body_size}
        :param body_size_range: body_size_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size_range LoadbalancerFrontendRule#body_size_range}
        :param cookie: cookie block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#cookie LoadbalancerFrontendRule#cookie}
        :param header: header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#header LoadbalancerFrontendRule#header}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#host LoadbalancerFrontendRule#host}
        :param http_method: http_method block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_method LoadbalancerFrontendRule#http_method}
        :param num_members_up: num_members_up block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#num_members_up LoadbalancerFrontendRule#num_members_up}
        :param path: path block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#path LoadbalancerFrontendRule#path}
        :param src_ip: src_ip block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_ip LoadbalancerFrontendRule#src_ip}
        :param src_port: src_port block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port LoadbalancerFrontendRule#src_port}
        :param src_port_range: src_port_range block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port_range LoadbalancerFrontendRule#src_port_range}
        :param url: url block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url LoadbalancerFrontendRule#url}
        :param url_param: url_param block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_param LoadbalancerFrontendRule#url_param}
        :param url_query: url_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_query LoadbalancerFrontendRule#url_query}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if body_size is not None:
            self._values["body_size"] = body_size
        if body_size_range is not None:
            self._values["body_size_range"] = body_size_range
        if cookie is not None:
            self._values["cookie"] = cookie
        if header is not None:
            self._values["header"] = header
        if host is not None:
            self._values["host"] = host
        if http_method is not None:
            self._values["http_method"] = http_method
        if num_members_up is not None:
            self._values["num_members_up"] = num_members_up
        if path is not None:
            self._values["path"] = path
        if src_ip is not None:
            self._values["src_ip"] = src_ip
        if src_port is not None:
            self._values["src_port"] = src_port
        if src_port_range is not None:
            self._values["src_port_range"] = src_port_range
        if url is not None:
            self._values["url"] = url
        if url_param is not None:
            self._values["url_param"] = url_param
        if url_query is not None:
            self._values["url_query"] = url_query

    @builtins.property
    def body_size(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersBodySize"]]]:
        '''body_size block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size LoadbalancerFrontendRule#body_size}
        '''
        result = self._values.get("body_size")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersBodySize"]]], result)

    @builtins.property
    def body_size_range(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersBodySizeRange"]]]:
        '''body_size_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#body_size_range LoadbalancerFrontendRule#body_size_range}
        '''
        result = self._values.get("body_size_range")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersBodySizeRange"]]], result)

    @builtins.property
    def cookie(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersCookie"]]]:
        '''cookie block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#cookie LoadbalancerFrontendRule#cookie}
        '''
        result = self._values.get("cookie")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersCookie"]]], result)

    @builtins.property
    def header(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHeader"]]]:
        '''header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#header LoadbalancerFrontendRule#header}
        '''
        result = self._values.get("header")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHeader"]]], result)

    @builtins.property
    def host(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHost"]]]:
        '''host block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#host LoadbalancerFrontendRule#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHost"]]], result)

    @builtins.property
    def http_method(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHttpMethod"]]]:
        '''http_method block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#http_method LoadbalancerFrontendRule#http_method}
        '''
        result = self._values.get("http_method")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersHttpMethod"]]], result)

    @builtins.property
    def num_members_up(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersNumMembersUp"]]]:
        '''num_members_up block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#num_members_up LoadbalancerFrontendRule#num_members_up}
        '''
        result = self._values.get("num_members_up")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersNumMembersUp"]]], result)

    @builtins.property
    def path(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]]]:
        '''path block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#path LoadbalancerFrontendRule#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]]], result)

    @builtins.property
    def src_ip(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]]]:
        '''src_ip block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_ip LoadbalancerFrontendRule#src_ip}
        '''
        result = self._values.get("src_ip")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]]], result)

    @builtins.property
    def src_port(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]]]:
        '''src_port block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port LoadbalancerFrontendRule#src_port}
        '''
        result = self._values.get("src_port")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]]], result)

    @builtins.property
    def src_port_range(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]]]:
        '''src_port_range block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#src_port_range LoadbalancerFrontendRule#src_port_range}
        '''
        result = self._values.get("src_port_range")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]]], result)

    @builtins.property
    def url(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]]]:
        '''url block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url LoadbalancerFrontendRule#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]]], result)

    @builtins.property
    def url_param(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]]]:
        '''url_param block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_param LoadbalancerFrontendRule#url_param}
        '''
        result = self._values.get("url_param")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]]], result)

    @builtins.property
    def url_query(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]]]:
        '''url_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#url_query LoadbalancerFrontendRule#url_query}
        '''
        result = self._values.get("url_query")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersBodySize",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersBodySize:
    def __init__(self, *, method: builtins.str, value: jsii.Number) -> None:
        '''
        :param method: Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param value: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "value": value,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersBodySize(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersBodySizeRange",
    jsii_struct_bases=[],
    name_mapping={"range_end": "rangeEnd", "range_start": "rangeStart"},
)
class LoadbalancerFrontendRuleMatchersBodySizeRange:
    def __init__(self, *, range_end: jsii.Number, range_start: jsii.Number) -> None:
        '''
        :param range_end: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_end LoadbalancerFrontendRule#range_end}
        :param range_start: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_start LoadbalancerFrontendRule#range_start}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "range_end": range_end,
            "range_start": range_start,
        }

    @builtins.property
    def range_end(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_end LoadbalancerFrontendRule#range_end}
        '''
        result = self._values.get("range_end")
        assert result is not None, "Required property 'range_end' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def range_start(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_start LoadbalancerFrontendRule#range_start}
        '''
        result = self._values.get("range_start")
        assert result is not None, "Required property 'range_start' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersBodySizeRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersCookie",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "name": "name",
        "ignore_case": "ignoreCase",
        "value": "value",
    },
)
class LoadbalancerFrontendRuleMatchersCookie:
    def __init__(
        self,
        *,
        method: builtins.str,
        name: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param name: Name of the argument. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "name": name,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the argument.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersCookie(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersHeader",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "name": "name",
        "ignore_case": "ignoreCase",
        "value": "value",
    },
)
class LoadbalancerFrontendRuleMatchersHeader:
    def __init__(
        self,
        *,
        method: builtins.str,
        name: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param name: Name of the argument. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "name": name,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the argument.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersHost",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class LoadbalancerFrontendRuleMatchersHost:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersHost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersHttpMethod",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class LoadbalancerFrontendRuleMatchersHttpMethod:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: String value (``GET``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``CONNECT``, ``OPTIONS``, ``TRACE``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''String value (``GET``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``CONNECT``, ``OPTIONS``, ``TRACE``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersHttpMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersNumMembersUp",
    jsii_struct_bases=[],
    name_mapping={"backend_name": "backendName", "method": "method", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersNumMembersUp:
    def __init__(
        self,
        *,
        backend_name: builtins.str,
        method: builtins.str,
        value: jsii.Number,
    ) -> None:
        '''
        :param backend_name: The name of the ``backend`` which members will be monitored. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#backend_name LoadbalancerFrontendRule#backend_name}
        :param method: Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param value: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "backend_name": backend_name,
            "method": method,
            "value": value,
        }

    @builtins.property
    def backend_name(self) -> builtins.str:
        '''The name of the ``backend`` which members will be monitored.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#backend_name LoadbalancerFrontendRule#backend_name}
        '''
        result = self._values.get("backend_name")
        assert result is not None, "Required property 'backend_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersNumMembersUp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFrontendRuleMatchersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBodySize")
    def reset_body_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBodySize", []))

    @jsii.member(jsii_name="resetBodySizeRange")
    def reset_body_size_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBodySizeRange", []))

    @jsii.member(jsii_name="resetCookie")
    def reset_cookie(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookie", []))

    @jsii.member(jsii_name="resetHeader")
    def reset_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeader", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetHttpMethod")
    def reset_http_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMethod", []))

    @jsii.member(jsii_name="resetNumMembersUp")
    def reset_num_members_up(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumMembersUp", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetSrcIp")
    def reset_src_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSrcIp", []))

    @jsii.member(jsii_name="resetSrcPort")
    def reset_src_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSrcPort", []))

    @jsii.member(jsii_name="resetSrcPortRange")
    def reset_src_port_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSrcPortRange", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUrlParam")
    def reset_url_param(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlParam", []))

    @jsii.member(jsii_name="resetUrlQuery")
    def reset_url_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlQuery", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodySizeInput")
    def body_size_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySize]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySize]]], jsii.get(self, "bodySizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodySizeRangeInput")
    def body_size_range_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySizeRange]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySizeRange]]], jsii.get(self, "bodySizeRangeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieInput")
    def cookie_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersCookie]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersCookie]]], jsii.get(self, "cookieInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerInput")
    def header_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHeader]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHeader]]], jsii.get(self, "headerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHost]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHost]]], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethodInput")
    def http_method_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHttpMethod]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHttpMethod]]], jsii.get(self, "httpMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numMembersUpInput")
    def num_members_up_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersNumMembersUp]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersNumMembersUp]]], jsii.get(self, "numMembersUpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]]], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcIpInput")
    def src_ip_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]]], jsii.get(self, "srcIpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcPortInput")
    def src_port_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]]], jsii.get(self, "srcPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcPortRangeInput")
    def src_port_range_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]]], jsii.get(self, "srcPortRangeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]]], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlParamInput")
    def url_param_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]]], jsii.get(self, "urlParamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlQueryInput")
    def url_query_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]]], jsii.get(self, "urlQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodySize")
    def body_size(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySize]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySize]], jsii.get(self, "bodySize"))

    @body_size.setter
    def body_size(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySize]],
    ) -> None:
        jsii.set(self, "bodySize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bodySizeRange")
    def body_size_range(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySizeRange]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySizeRange]], jsii.get(self, "bodySizeRange"))

    @body_size_range.setter
    def body_size_range(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersBodySizeRange]],
    ) -> None:
        jsii.set(self, "bodySizeRange", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookie")
    def cookie(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersCookie]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersCookie]], jsii.get(self, "cookie"))

    @cookie.setter
    def cookie(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersCookie]],
    ) -> None:
        jsii.set(self, "cookie", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="header")
    def header(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHeader]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHeader]], jsii.get(self, "header"))

    @header.setter
    def header(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHeader]],
    ) -> None:
        jsii.set(self, "header", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHost]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHost]], jsii.get(self, "host"))

    @host.setter
    def host(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHost]],
    ) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def http_method(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHttpMethod]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHttpMethod]], jsii.get(self, "httpMethod"))

    @http_method.setter
    def http_method(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersHttpMethod]],
    ) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numMembersUp")
    def num_members_up(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersNumMembersUp]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersNumMembersUp]], jsii.get(self, "numMembersUp"))

    @num_members_up.setter
    def num_members_up(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List[LoadbalancerFrontendRuleMatchersNumMembersUp]],
    ) -> None:
        jsii.set(self, "numMembersUp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]], jsii.get(self, "path"))

    @path.setter
    def path(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersPath"]],
    ) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcIp")
    def src_ip(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]], jsii.get(self, "srcIp"))

    @src_ip.setter
    def src_ip(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcIp"]],
    ) -> None:
        jsii.set(self, "srcIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcPort")
    def src_port(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]], jsii.get(self, "srcPort"))

    @src_port.setter
    def src_port(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPort"]],
    ) -> None:
        jsii.set(self, "srcPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="srcPortRange")
    def src_port_range(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]], jsii.get(self, "srcPortRange"))

    @src_port_range.setter
    def src_port_range(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersSrcPortRange"]],
    ) -> None:
        jsii.set(self, "srcPortRange", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]], jsii.get(self, "url"))

    @url.setter
    def url(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrl"]],
    ) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlParam")
    def url_param(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]], jsii.get(self, "urlParam"))

    @url_param.setter
    def url_param(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlParam"]],
    ) -> None:
        jsii.set(self, "urlParam", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlQuery")
    def url_query(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]], jsii.get(self, "urlQuery"))

    @url_query.setter
    def url_query(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["LoadbalancerFrontendRuleMatchersUrlQuery"]],
    ) -> None:
        jsii.set(self, "urlQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerFrontendRuleMatchers]:
        return typing.cast(typing.Optional[LoadbalancerFrontendRuleMatchers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LoadbalancerFrontendRuleMatchers],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersPath",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "ignore_case": "ignoreCase", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersPath:
    def __init__(
        self,
        *,
        method: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersSrcIp",
    jsii_struct_bases=[],
    name_mapping={"value": "value"},
)
class LoadbalancerFrontendRuleMatchersSrcIp:
    def __init__(self, *, value: builtins.str) -> None:
        '''
        :param value: IP address. CIDR masks are supported, e.g. ``192.168.0.0/24``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "value": value,
        }

    @builtins.property
    def value(self) -> builtins.str:
        '''IP address. CIDR masks are supported, e.g. ``192.168.0.0/24``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersSrcIp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersSrcPort",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersSrcPort:
    def __init__(self, *, method: builtins.str, value: jsii.Number) -> None:
        '''
        :param method: Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param value: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "value": value,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``equal``, ``greater``, ``greater_or_equal``, ``less``, ``less_or_equal``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersSrcPort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersSrcPortRange",
    jsii_struct_bases=[],
    name_mapping={"range_end": "rangeEnd", "range_start": "rangeStart"},
)
class LoadbalancerFrontendRuleMatchersSrcPortRange:
    def __init__(self, *, range_end: jsii.Number, range_start: jsii.Number) -> None:
        '''
        :param range_end: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_end LoadbalancerFrontendRule#range_end}
        :param range_start: Integer value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_start LoadbalancerFrontendRule#range_start}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "range_end": range_end,
            "range_start": range_start,
        }

    @builtins.property
    def range_end(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_end LoadbalancerFrontendRule#range_end}
        '''
        result = self._values.get("range_end")
        assert result is not None, "Required property 'range_end' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def range_start(self) -> jsii.Number:
        '''Integer value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#range_start LoadbalancerFrontendRule#range_start}
        '''
        result = self._values.get("range_start")
        assert result is not None, "Required property 'range_start' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersSrcPortRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersUrl",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "ignore_case": "ignoreCase", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersUrl:
    def __init__(
        self,
        *,
        method: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersUrl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersUrlParam",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "name": "name",
        "ignore_case": "ignoreCase",
        "value": "value",
    },
)
class LoadbalancerFrontendRuleMatchersUrlParam:
    def __init__(
        self,
        *,
        method: builtins.str,
        name: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param name: Name of the argument. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "name": name,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the argument.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#name LoadbalancerFrontendRule#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersUrlParam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendRuleMatchersUrlQuery",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "ignore_case": "ignoreCase", "value": "value"},
)
class LoadbalancerFrontendRuleMatchersUrlQuery:
    def __init__(
        self,
        *,
        method: builtins.str,
        ignore_case: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``). Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        :param ignore_case: Ignore case, default ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        :param value: String value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
        }
        if ignore_case is not None:
            self._values["ignore_case"] = ignore_case
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def method(self) -> builtins.str:
        '''Match method (``exact``, ``substring``, ``regexp``, ``starts``, ``ends``, ``domain``, ``ip``, ``exists``).

        Matcher with ``exists`` and ``ip`` methods must be used without ``value`` and ``ignore_case`` fields.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#method LoadbalancerFrontendRule#method}
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ignore_case(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Ignore case, default ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#ignore_case LoadbalancerFrontendRule#ignore_case}
        '''
        result = self._values.get("ignore_case")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''String value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_rule#value LoadbalancerFrontendRule#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendRuleMatchersUrlQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFrontendTlsConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendTlsConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config upcloud_loadbalancer_frontend_tls_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate_bundle: builtins.str,
        frontend: builtins.str,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config upcloud_loadbalancer_frontend_tls_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate_bundle: Reference to certificate bundle ID. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#certificate_bundle LoadbalancerFrontendTlsConfig#certificate_bundle}
        :param frontend: ID of the load balancer frontend to which the TLS config is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#frontend LoadbalancerFrontendTlsConfig#frontend}
        :param name: The name of the TLS config must be unique within service frontend. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#name LoadbalancerFrontendTlsConfig#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerFrontendTlsConfigConfig(
            certificate_bundle=certificate_bundle,
            frontend=frontend,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateBundleInput")
    def certificate_bundle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateBundleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frontendInput")
    def frontend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frontendInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateBundle")
    def certificate_bundle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateBundle"))

    @certificate_bundle.setter
    def certificate_bundle(self, value: builtins.str) -> None:
        jsii.set(self, "certificateBundle", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frontend")
    def frontend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frontend"))

    @frontend.setter
    def frontend(self, value: builtins.str) -> None:
        jsii.set(self, "frontend", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerFrontendTlsConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "certificate_bundle": "certificateBundle",
        "frontend": "frontend",
        "name": "name",
    },
)
class LoadbalancerFrontendTlsConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        certificate_bundle: builtins.str,
        frontend: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param certificate_bundle: Reference to certificate bundle ID. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#certificate_bundle LoadbalancerFrontendTlsConfig#certificate_bundle}
        :param frontend: ID of the load balancer frontend to which the TLS config is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#frontend LoadbalancerFrontendTlsConfig#frontend}
        :param name: The name of the TLS config must be unique within service frontend. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#name LoadbalancerFrontendTlsConfig#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate_bundle": certificate_bundle,
            "frontend": frontend,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def certificate_bundle(self) -> builtins.str:
        '''Reference to certificate bundle ID.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#certificate_bundle LoadbalancerFrontendTlsConfig#certificate_bundle}
        '''
        result = self._values.get("certificate_bundle")
        assert result is not None, "Required property 'certificate_bundle' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def frontend(self) -> builtins.str:
        '''ID of the load balancer frontend to which the TLS config is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#frontend LoadbalancerFrontendTlsConfig#frontend}
        '''
        result = self._values.get("frontend")
        assert result is not None, "Required property 'frontend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the TLS config must be unique within service frontend.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_frontend_tls_config#name LoadbalancerFrontendTlsConfig#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFrontendTlsConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerManualCertificateBundle(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerManualCertificateBundle",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle upcloud_loadbalancer_manual_certificate_bundle}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate: builtins.str,
        name: builtins.str,
        private_key: builtins.str,
        intermediates: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle upcloud_loadbalancer_manual_certificate_bundle} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate: Certificate within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#certificate LoadbalancerManualCertificateBundle#certificate}
        :param name: The name of the bundle must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#name LoadbalancerManualCertificateBundle#name}
        :param private_key: Private key within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#private_key LoadbalancerManualCertificateBundle#private_key}
        :param intermediates: Intermediate certificates within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#intermediates LoadbalancerManualCertificateBundle#intermediates}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerManualCertificateBundleConfig(
            certificate=certificate,
            name=name,
            private_key=private_key,
            intermediates=intermediates,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIntermediates")
    def reset_intermediates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntermediates", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notBefore")
    def not_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBefore"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationalState")
    def operational_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operationalState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediatesInput")
    def intermediates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intermediatesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        jsii.set(self, "certificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediates")
    def intermediates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intermediates"))

    @intermediates.setter
    def intermediates(self, value: builtins.str) -> None:
        jsii.set(self, "intermediates", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        jsii.set(self, "privateKey", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerManualCertificateBundleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "certificate": "certificate",
        "name": "name",
        "private_key": "privateKey",
        "intermediates": "intermediates",
    },
)
class LoadbalancerManualCertificateBundleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        certificate: builtins.str,
        name: builtins.str,
        private_key: builtins.str,
        intermediates: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param certificate: Certificate within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#certificate LoadbalancerManualCertificateBundle#certificate}
        :param name: The name of the bundle must be unique within customer account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#name LoadbalancerManualCertificateBundle#name}
        :param private_key: Private key within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#private_key LoadbalancerManualCertificateBundle#private_key}
        :param intermediates: Intermediate certificates within base64 string must be in PEM format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#intermediates LoadbalancerManualCertificateBundle#intermediates}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
            "name": name,
            "private_key": private_key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if intermediates is not None:
            self._values["intermediates"] = intermediates

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def certificate(self) -> builtins.str:
        '''Certificate within base64 string must be in PEM format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#certificate LoadbalancerManualCertificateBundle#certificate}
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the bundle must be unique within customer account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#name LoadbalancerManualCertificateBundle#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Private key within base64 string must be in PEM format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#private_key LoadbalancerManualCertificateBundle#private_key}
        '''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def intermediates(self) -> typing.Optional[builtins.str]:
        '''Intermediate certificates within base64 string must be in PEM format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_manual_certificate_bundle#intermediates LoadbalancerManualCertificateBundle#intermediates}
        '''
        result = self._values.get("intermediates")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerManualCertificateBundleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerResolver(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerResolver",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver upcloud_loadbalancer_resolver}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cache_invalid: jsii.Number,
        cache_valid: jsii.Number,
        loadbalancer: builtins.str,
        name: builtins.str,
        nameservers: typing.Sequence[builtins.str],
        retries: jsii.Number,
        timeout: jsii.Number,
        timeout_retry: jsii.Number,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver upcloud_loadbalancer_resolver} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cache_invalid: Time in seconds to cache invalid results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_invalid LoadbalancerResolver#cache_invalid}
        :param cache_valid: Time in seconds to cache valid results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_valid LoadbalancerResolver#cache_valid}
        :param loadbalancer: ID of the load balancer to which the resolver is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#loadbalancer LoadbalancerResolver#loadbalancer}
        :param name: The name of the resolver must be unique within the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#name LoadbalancerResolver#name}
        :param nameservers: List of nameserver IP addresses. Nameserver can reside in public internet or in customer private network. Port is optional, if missing then default 53 will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#nameservers LoadbalancerResolver#nameservers}
        :param retries: Number of retries on failure. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#retries LoadbalancerResolver#retries}
        :param timeout: Timeout for the query in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout LoadbalancerResolver#timeout}
        :param timeout_retry: Timeout for the query retries in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout_retry LoadbalancerResolver#timeout_retry}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerResolverConfig(
            cache_invalid=cache_invalid,
            cache_valid=cache_valid,
            loadbalancer=loadbalancer,
            name=name,
            nameservers=nameservers,
            retries=retries,
            timeout=timeout,
            timeout_retry=timeout_retry,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheInvalidInput")
    def cache_invalid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheInvalidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheValidInput")
    def cache_valid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheValidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancerInput")
    def loadbalancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loadbalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameserversInput")
    def nameservers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "nameserversInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retriesInput")
    def retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutRetryInput")
    def timeout_retry_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutRetryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheInvalid")
    def cache_invalid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheInvalid"))

    @cache_invalid.setter
    def cache_invalid(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheInvalid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheValid")
    def cache_valid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheValid"))

    @cache_valid.setter
    def cache_valid(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheValid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(self, value: builtins.str) -> None:
        jsii.set(self, "loadbalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameservers")
    def nameservers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nameservers"))

    @nameservers.setter
    def nameservers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "nameservers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retries")
    def retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retries"))

    @retries.setter
    def retries(self, value: jsii.Number) -> None:
        jsii.set(self, "retries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutRetry")
    def timeout_retry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutRetry"))

    @timeout_retry.setter
    def timeout_retry(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutRetry", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerResolverConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cache_invalid": "cacheInvalid",
        "cache_valid": "cacheValid",
        "loadbalancer": "loadbalancer",
        "name": "name",
        "nameservers": "nameservers",
        "retries": "retries",
        "timeout": "timeout",
        "timeout_retry": "timeoutRetry",
    },
)
class LoadbalancerResolverConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cache_invalid: jsii.Number,
        cache_valid: jsii.Number,
        loadbalancer: builtins.str,
        name: builtins.str,
        nameservers: typing.Sequence[builtins.str],
        retries: jsii.Number,
        timeout: jsii.Number,
        timeout_retry: jsii.Number,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cache_invalid: Time in seconds to cache invalid results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_invalid LoadbalancerResolver#cache_invalid}
        :param cache_valid: Time in seconds to cache valid results. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_valid LoadbalancerResolver#cache_valid}
        :param loadbalancer: ID of the load balancer to which the resolver is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#loadbalancer LoadbalancerResolver#loadbalancer}
        :param name: The name of the resolver must be unique within the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#name LoadbalancerResolver#name}
        :param nameservers: List of nameserver IP addresses. Nameserver can reside in public internet or in customer private network. Port is optional, if missing then default 53 will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#nameservers LoadbalancerResolver#nameservers}
        :param retries: Number of retries on failure. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#retries LoadbalancerResolver#retries}
        :param timeout: Timeout for the query in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout LoadbalancerResolver#timeout}
        :param timeout_retry: Timeout for the query retries in seconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout_retry LoadbalancerResolver#timeout_retry}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cache_invalid": cache_invalid,
            "cache_valid": cache_valid,
            "loadbalancer": loadbalancer,
            "name": name,
            "nameservers": nameservers,
            "retries": retries,
            "timeout": timeout,
            "timeout_retry": timeout_retry,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def cache_invalid(self) -> jsii.Number:
        '''Time in seconds to cache invalid results.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_invalid LoadbalancerResolver#cache_invalid}
        '''
        result = self._values.get("cache_invalid")
        assert result is not None, "Required property 'cache_invalid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cache_valid(self) -> jsii.Number:
        '''Time in seconds to cache valid results.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#cache_valid LoadbalancerResolver#cache_valid}
        '''
        result = self._values.get("cache_valid")
        assert result is not None, "Required property 'cache_valid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def loadbalancer(self) -> builtins.str:
        '''ID of the load balancer to which the resolver is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#loadbalancer LoadbalancerResolver#loadbalancer}
        '''
        result = self._values.get("loadbalancer")
        assert result is not None, "Required property 'loadbalancer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the resolver must be unique within the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#name LoadbalancerResolver#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def nameservers(self) -> typing.List[builtins.str]:
        '''List of nameserver IP addresses.

        Nameserver can reside in public internet or in customer private network.
        Port is optional, if missing then default 53 will be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#nameservers LoadbalancerResolver#nameservers}
        '''
        result = self._values.get("nameservers")
        assert result is not None, "Required property 'nameservers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def retries(self) -> jsii.Number:
        '''Number of retries on failure.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#retries LoadbalancerResolver#retries}
        '''
        result = self._values.get("retries")
        assert result is not None, "Required property 'retries' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def timeout(self) -> jsii.Number:
        '''Timeout for the query in seconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout LoadbalancerResolver#timeout}
        '''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def timeout_retry(self) -> jsii.Number:
        '''Timeout for the query retries in seconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_resolver#timeout_retry LoadbalancerResolver#timeout_retry}
        '''
        result = self._values.get("timeout_retry")
        assert result is not None, "Required property 'timeout_retry' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerResolverConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerStaticBackendMember(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.LoadbalancerStaticBackendMember",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member upcloud_loadbalancer_static_backend_member}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backend: builtins.str,
        ip: builtins.str,
        max_sessions: jsii.Number,
        name: builtins.str,
        port: jsii.Number,
        weight: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member upcloud_loadbalancer_static_backend_member} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: ID of the load balancer backend to which the member is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#backend LoadbalancerStaticBackendMember#backend}
        :param ip: Server IP address in the customer private network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#ip LoadbalancerStaticBackendMember#ip}
        :param max_sessions: Maximum number of sessions before queueing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#max_sessions LoadbalancerStaticBackendMember#max_sessions}
        :param name: The name of the member must be unique within the load balancer backend service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#name LoadbalancerStaticBackendMember#name}
        :param port: Server port. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#port LoadbalancerStaticBackendMember#port}
        :param weight: Used to adjust the server's weight relative to other servers. All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load. A value of 0 means the server will not participate in load balancing but will still accept persistent connections. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#weight LoadbalancerStaticBackendMember#weight}
        :param enabled: Indicates if the member is enabled. Disabled members are excluded from load balancing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#enabled LoadbalancerStaticBackendMember#enabled}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LoadbalancerStaticBackendMemberConfig(
            backend=backend,
            ip=ip,
            max_sessions=max_sessions,
            name=name,
            port=port,
            weight=weight,
            enabled=enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessionsInput")
    def max_sessions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSessionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        jsii.set(self, "backend", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        jsii.set(self, "ip", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessions")
    def max_sessions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSessions"))

    @max_sessions.setter
    def max_sessions(self, value: jsii.Number) -> None:
        jsii.set(self, "maxSessions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        jsii.set(self, "weight", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.LoadbalancerStaticBackendMemberConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backend": "backend",
        "ip": "ip",
        "max_sessions": "maxSessions",
        "name": "name",
        "port": "port",
        "weight": "weight",
        "enabled": "enabled",
    },
)
class LoadbalancerStaticBackendMemberConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backend: builtins.str,
        ip: builtins.str,
        max_sessions: jsii.Number,
        name: builtins.str,
        port: jsii.Number,
        weight: jsii.Number,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backend: ID of the load balancer backend to which the member is connected. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#backend LoadbalancerStaticBackendMember#backend}
        :param ip: Server IP address in the customer private network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#ip LoadbalancerStaticBackendMember#ip}
        :param max_sessions: Maximum number of sessions before queueing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#max_sessions LoadbalancerStaticBackendMember#max_sessions}
        :param name: The name of the member must be unique within the load balancer backend service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#name LoadbalancerStaticBackendMember#name}
        :param port: Server port. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#port LoadbalancerStaticBackendMember#port}
        :param weight: Used to adjust the server's weight relative to other servers. All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load. A value of 0 means the server will not participate in load balancing but will still accept persistent connections. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#weight LoadbalancerStaticBackendMember#weight}
        :param enabled: Indicates if the member is enabled. Disabled members are excluded from load balancing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#enabled LoadbalancerStaticBackendMember#enabled}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "backend": backend,
            "ip": ip,
            "max_sessions": max_sessions,
            "name": name,
            "port": port,
            "weight": weight,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def backend(self) -> builtins.str:
        '''ID of the load balancer backend to which the member is connected.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#backend LoadbalancerStaticBackendMember#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip(self) -> builtins.str:
        '''Server IP address in the customer private network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#ip LoadbalancerStaticBackendMember#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_sessions(self) -> jsii.Number:
        '''Maximum number of sessions before queueing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#max_sessions LoadbalancerStaticBackendMember#max_sessions}
        '''
        result = self._values.get("max_sessions")
        assert result is not None, "Required property 'max_sessions' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the member must be unique within the load balancer backend service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#name LoadbalancerStaticBackendMember#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''Server port.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#port LoadbalancerStaticBackendMember#port}
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def weight(self) -> jsii.Number:
        '''Used to adjust the server's weight relative to other servers.

        All servers will receive a load proportional to their weight relative to the sum of all weights, so the higher the weight, the higher the load.
        A value of 0 means the server will not participate in load balancing but will still accept persistent connections.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#weight LoadbalancerStaticBackendMember#weight}
        '''
        result = self._values.get("weight")
        assert result is not None, "Required property 'weight' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Indicates if the member is enabled. Disabled members are excluded from load balancing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/loadbalancer_static_backend_member#enabled LoadbalancerStaticBackendMember#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerStaticBackendMemberConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseLogicalDatabase(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseLogicalDatabase",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database upcloud_managed_database_logical_database}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        service: builtins.str,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database upcloud_managed_database_logical_database} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the logical database. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#name ManagedDatabaseLogicalDatabase#name}
        :param service: Service's UUID for which this user belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#service ManagedDatabaseLogicalDatabase#service}
        :param character_set: Default character set for the database (LC_CTYPE). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#character_set ManagedDatabaseLogicalDatabase#character_set}
        :param collation: Default collation for the database (LC_COLLATE). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#collation ManagedDatabaseLogicalDatabase#collation}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ManagedDatabaseLogicalDatabaseConfig(
            name=name,
            service=service,
            character_set=character_set,
            collation=collation,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCharacterSet")
    def reset_character_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCharacterSet", []))

    @jsii.member(jsii_name="resetCollation")
    def reset_collation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollation", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="characterSetInput")
    def character_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "characterSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="collationInput")
    def collation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="characterSet")
    def character_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "characterSet"))

    @character_set.setter
    def character_set(self, value: builtins.str) -> None:
        jsii.set(self, "characterSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="collation")
    def collation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collation"))

    @collation.setter
    def collation(self, value: builtins.str) -> None:
        jsii.set(self, "collation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseLogicalDatabaseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "service": "service",
        "character_set": "characterSet",
        "collation": "collation",
    },
)
class ManagedDatabaseLogicalDatabaseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        service: builtins.str,
        character_set: typing.Optional[builtins.str] = None,
        collation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the logical database. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#name ManagedDatabaseLogicalDatabase#name}
        :param service: Service's UUID for which this user belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#service ManagedDatabaseLogicalDatabase#service}
        :param character_set: Default character set for the database (LC_CTYPE). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#character_set ManagedDatabaseLogicalDatabase#character_set}
        :param collation: Default collation for the database (LC_COLLATE). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#collation ManagedDatabaseLogicalDatabase#collation}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "service": service,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if character_set is not None:
            self._values["character_set"] = character_set
        if collation is not None:
            self._values["collation"] = collation

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the logical database.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#name ManagedDatabaseLogicalDatabase#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service(self) -> builtins.str:
        '''Service's UUID for which this user belongs to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#service ManagedDatabaseLogicalDatabase#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def character_set(self) -> typing.Optional[builtins.str]:
        '''Default character set for the database (LC_CTYPE).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#character_set ManagedDatabaseLogicalDatabase#character_set}
        '''
        result = self._values.get("character_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collation(self) -> typing.Optional[builtins.str]:
        '''Default collation for the database (LC_COLLATE).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_logical_database#collation ManagedDatabaseLogicalDatabase#collation}
        '''
        result = self._values.get("collation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseLogicalDatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysql(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysql",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql upcloud_managed_database_mysql}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        properties: typing.Optional["ManagedDatabaseMysqlProperties"] = None,
        title: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql upcloud_managed_database_mysql} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#name ManagedDatabaseMysql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        :param zone: Zone where the instance resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#title ManagedDatabaseMysql#title}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ManagedDatabaseMysqlConfig(
            name=name,
            plan=plan,
            zone=zone,
            maintenance_window_dow=maintenance_window_dow,
            maintenance_window_time=maintenance_window_time,
            powered=powered,
            properties=properties,
            title=title,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        migration: typing.Optional["ManagedDatabaseMysqlPropertiesMigration"] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        :param binlog_retention_period: The minimum amount of time in seconds to keep binlog entries before deletion. This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        :param connect_timeout: connect_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        :param default_time_zone: default_time_zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        :param group_concat_max_len: group_concat_max_len. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        :param information_schema_stats_expiry: information_schema_stats_expiry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        :param innodb_ft_min_token_size: innodb_ft_min_token_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        :param innodb_ft_server_stopword_table: innodb_ft_server_stopword_table. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        :param innodb_lock_wait_timeout: innodb_lock_wait_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        :param innodb_log_buffer_size: innodb_log_buffer_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        :param innodb_online_alter_log_max_size: innodb_online_alter_log_max_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        :param innodb_print_all_deadlocks: innodb_print_all_deadlocks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        :param innodb_rollback_on_timeout: innodb_rollback_on_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        :param interactive_timeout: interactive_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        :param internal_tmp_mem_storage_engine: internal_tmp_mem_storage_engine. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        :param long_query_time: long_query_time. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        :param max_allowed_packet: max_allowed_packet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        :param max_heap_table_size: max_heap_table_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        :param migration: migration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        :param net_read_timeout: net_read_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        :param net_write_timeout: net_write_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        :param public_access: Public Access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        :param slow_query_log: slow_query_log. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        :param sort_buffer_size: sort_buffer_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        :param sql_mode: sql_mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        :param sql_require_primary_key: sql_require_primary_key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        :param tmp_table_size: tmp_table_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        :param version: MySQL major version. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#version ManagedDatabaseMysql#version}
        :param wait_timeout: wait_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        value = ManagedDatabaseMysqlProperties(
            admin_password=admin_password,
            admin_username=admin_username,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            binlog_retention_period=binlog_retention_period,
            connect_timeout=connect_timeout,
            default_time_zone=default_time_zone,
            group_concat_max_len=group_concat_max_len,
            information_schema_stats_expiry=information_schema_stats_expiry,
            innodb_ft_min_token_size=innodb_ft_min_token_size,
            innodb_ft_server_stopword_table=innodb_ft_server_stopword_table,
            innodb_lock_wait_timeout=innodb_lock_wait_timeout,
            innodb_log_buffer_size=innodb_log_buffer_size,
            innodb_online_alter_log_max_size=innodb_online_alter_log_max_size,
            innodb_print_all_deadlocks=innodb_print_all_deadlocks,
            innodb_rollback_on_timeout=innodb_rollback_on_timeout,
            interactive_timeout=interactive_timeout,
            internal_tmp_mem_storage_engine=internal_tmp_mem_storage_engine,
            ip_filter=ip_filter,
            long_query_time=long_query_time,
            max_allowed_packet=max_allowed_packet,
            max_heap_table_size=max_heap_table_size,
            migration=migration,
            net_read_timeout=net_read_timeout,
            net_write_timeout=net_write_timeout,
            public_access=public_access,
            slow_query_log=slow_query_log,
            sort_buffer_size=sort_buffer_size,
            sql_mode=sql_mode,
            sql_require_primary_key=sql_require_primary_key,
            tmp_table_size=tmp_table_size,
            version=version,
            wait_timeout=wait_timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetMaintenanceWindowDow")
    def reset_maintenance_window_dow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowDow", []))

    @jsii.member(jsii_name="resetMaintenanceWindowTime")
    def reset_maintenance_window_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowTime", []))

    @jsii.member(jsii_name="resetPowered")
    def reset_powered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPowered", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="components")
    def components(self) -> "ManagedDatabaseMysqlComponentsList":
        return typing.cast("ManagedDatabaseMysqlComponentsList", jsii.get(self, "components"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabaseMysqlNodeStatesList":
        return typing.cast("ManagedDatabaseMysqlNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabaseMysqlPropertiesOutputReference":
        return typing.cast("ManagedDatabaseMysqlPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceHost")
    def service_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceHost"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servicePassword")
    def service_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePassword"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceUri")
    def service_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceUsername")
    def service_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUsername"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowDowInput")
    def maintenance_window_dow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowDowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowTimeInput")
    def maintenance_window_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="poweredInput")
    def powered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "poweredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional["ManagedDatabaseMysqlProperties"]:
        return typing.cast(typing.Optional["ManagedDatabaseMysqlProperties"], jsii.get(self, "propertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindowDow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindowTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        jsii.set(self, "plan", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="powered")
    def powered(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "powered"))

    @powered.setter
    def powered(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "powered", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseMysqlComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlComponentsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlComponentsList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseMysqlComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ManagedDatabaseMysqlComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseMysqlComponentsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlComponentsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usage")
    def usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlComponents]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlComponents],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "plan": "plan",
        "zone": "zone",
        "maintenance_window_dow": "maintenanceWindowDow",
        "maintenance_window_time": "maintenanceWindowTime",
        "powered": "powered",
        "properties": "properties",
        "title": "title",
    },
)
class ManagedDatabaseMysqlConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        properties: typing.Optional["ManagedDatabaseMysqlProperties"] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#name ManagedDatabaseMysql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        :param zone: Zone where the instance resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#title ManagedDatabaseMysql#title}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabaseMysqlProperties(**properties)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "plan": plan,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if maintenance_window_dow is not None:
            self._values["maintenance_window_dow"] = maintenance_window_dow
        if maintenance_window_time is not None:
            self._values["maintenance_window_time"] = maintenance_window_time
        if powered is not None:
            self._values["powered"] = powered
        if properties is not None:
            self._values["properties"] = properties
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the service.

        The name is used as a prefix for the logical hostname. Must be unique within an account

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#name ManagedDatabaseMysql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use. This determines how much resources the instance will have.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#plan ManagedDatabaseMysql#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#zone ManagedDatabaseMysql#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_dow ManagedDatabaseMysql#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#maintenance_window_time ManagedDatabaseMysql#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#powered ManagedDatabaseMysql#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabaseMysqlProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#properties ManagedDatabaseMysql#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabaseMysqlProperties"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#title ManagedDatabaseMysql#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabaseMysqlNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlNodeStatesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlNodeStatesList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabaseMysqlNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ManagedDatabaseMysqlNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class ManagedDatabaseMysqlNodeStatesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlNodeStatesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlNodeStates],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlProperties",
    jsii_struct_bases=[],
    name_mapping={
        "admin_password": "adminPassword",
        "admin_username": "adminUsername",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "binlog_retention_period": "binlogRetentionPeriod",
        "connect_timeout": "connectTimeout",
        "default_time_zone": "defaultTimeZone",
        "group_concat_max_len": "groupConcatMaxLen",
        "information_schema_stats_expiry": "informationSchemaStatsExpiry",
        "innodb_ft_min_token_size": "innodbFtMinTokenSize",
        "innodb_ft_server_stopword_table": "innodbFtServerStopwordTable",
        "innodb_lock_wait_timeout": "innodbLockWaitTimeout",
        "innodb_log_buffer_size": "innodbLogBufferSize",
        "innodb_online_alter_log_max_size": "innodbOnlineAlterLogMaxSize",
        "innodb_print_all_deadlocks": "innodbPrintAllDeadlocks",
        "innodb_rollback_on_timeout": "innodbRollbackOnTimeout",
        "interactive_timeout": "interactiveTimeout",
        "internal_tmp_mem_storage_engine": "internalTmpMemStorageEngine",
        "ip_filter": "ipFilter",
        "long_query_time": "longQueryTime",
        "max_allowed_packet": "maxAllowedPacket",
        "max_heap_table_size": "maxHeapTableSize",
        "migration": "migration",
        "net_read_timeout": "netReadTimeout",
        "net_write_timeout": "netWriteTimeout",
        "public_access": "publicAccess",
        "slow_query_log": "slowQueryLog",
        "sort_buffer_size": "sortBufferSize",
        "sql_mode": "sqlMode",
        "sql_require_primary_key": "sqlRequirePrimaryKey",
        "tmp_table_size": "tmpTableSize",
        "version": "version",
        "wait_timeout": "waitTimeout",
    },
)
class ManagedDatabaseMysqlProperties:
    def __init__(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        migration: typing.Optional["ManagedDatabaseMysqlPropertiesMigration"] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        :param binlog_retention_period: The minimum amount of time in seconds to keep binlog entries before deletion. This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        :param connect_timeout: connect_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        :param default_time_zone: default_time_zone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        :param group_concat_max_len: group_concat_max_len. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        :param information_schema_stats_expiry: information_schema_stats_expiry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        :param innodb_ft_min_token_size: innodb_ft_min_token_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        :param innodb_ft_server_stopword_table: innodb_ft_server_stopword_table. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        :param innodb_lock_wait_timeout: innodb_lock_wait_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        :param innodb_log_buffer_size: innodb_log_buffer_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        :param innodb_online_alter_log_max_size: innodb_online_alter_log_max_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        :param innodb_print_all_deadlocks: innodb_print_all_deadlocks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        :param innodb_rollback_on_timeout: innodb_rollback_on_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        :param interactive_timeout: interactive_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        :param internal_tmp_mem_storage_engine: internal_tmp_mem_storage_engine. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        :param long_query_time: long_query_time. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        :param max_allowed_packet: max_allowed_packet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        :param max_heap_table_size: max_heap_table_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        :param migration: migration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        :param net_read_timeout: net_read_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        :param net_write_timeout: net_write_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        :param public_access: Public Access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        :param slow_query_log: slow_query_log. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        :param sort_buffer_size: sort_buffer_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        :param sql_mode: sql_mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        :param sql_require_primary_key: sql_require_primary_key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        :param tmp_table_size: tmp_table_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        :param version: MySQL major version. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#version ManagedDatabaseMysql#version}
        :param wait_timeout: wait_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabaseMysqlPropertiesMigration(**migration)
        self._values: typing.Dict[str, typing.Any] = {}
        if admin_password is not None:
            self._values["admin_password"] = admin_password
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if binlog_retention_period is not None:
            self._values["binlog_retention_period"] = binlog_retention_period
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if default_time_zone is not None:
            self._values["default_time_zone"] = default_time_zone
        if group_concat_max_len is not None:
            self._values["group_concat_max_len"] = group_concat_max_len
        if information_schema_stats_expiry is not None:
            self._values["information_schema_stats_expiry"] = information_schema_stats_expiry
        if innodb_ft_min_token_size is not None:
            self._values["innodb_ft_min_token_size"] = innodb_ft_min_token_size
        if innodb_ft_server_stopword_table is not None:
            self._values["innodb_ft_server_stopword_table"] = innodb_ft_server_stopword_table
        if innodb_lock_wait_timeout is not None:
            self._values["innodb_lock_wait_timeout"] = innodb_lock_wait_timeout
        if innodb_log_buffer_size is not None:
            self._values["innodb_log_buffer_size"] = innodb_log_buffer_size
        if innodb_online_alter_log_max_size is not None:
            self._values["innodb_online_alter_log_max_size"] = innodb_online_alter_log_max_size
        if innodb_print_all_deadlocks is not None:
            self._values["innodb_print_all_deadlocks"] = innodb_print_all_deadlocks
        if innodb_rollback_on_timeout is not None:
            self._values["innodb_rollback_on_timeout"] = innodb_rollback_on_timeout
        if interactive_timeout is not None:
            self._values["interactive_timeout"] = interactive_timeout
        if internal_tmp_mem_storage_engine is not None:
            self._values["internal_tmp_mem_storage_engine"] = internal_tmp_mem_storage_engine
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if long_query_time is not None:
            self._values["long_query_time"] = long_query_time
        if max_allowed_packet is not None:
            self._values["max_allowed_packet"] = max_allowed_packet
        if max_heap_table_size is not None:
            self._values["max_heap_table_size"] = max_heap_table_size
        if migration is not None:
            self._values["migration"] = migration
        if net_read_timeout is not None:
            self._values["net_read_timeout"] = net_read_timeout
        if net_write_timeout is not None:
            self._values["net_write_timeout"] = net_write_timeout
        if public_access is not None:
            self._values["public_access"] = public_access
        if slow_query_log is not None:
            self._values["slow_query_log"] = slow_query_log
        if sort_buffer_size is not None:
            self._values["sort_buffer_size"] = sort_buffer_size
        if sql_mode is not None:
            self._values["sql_mode"] = sql_mode
        if sql_require_primary_key is not None:
            self._values["sql_require_primary_key"] = sql_require_primary_key
        if tmp_table_size is not None:
            self._values["tmp_table_size"] = tmp_table_size
        if version is not None:
            self._values["version"] = version
        if wait_timeout is not None:
            self._values["wait_timeout"] = wait_timeout

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''Custom password for admin user.

        Defaults to random string. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_password ManagedDatabaseMysql#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''Custom username for admin user. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#admin_username ManagedDatabaseMysql#admin_username}
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Automatic utility network IP Filter.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#automatic_utility_network_ip_filter ManagedDatabaseMysql#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour of day (in UTC) when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_hour ManagedDatabaseMysql#backup_hour}
        '''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''The minute of an hour when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#backup_minute ManagedDatabaseMysql#backup_minute}
        '''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def binlog_retention_period(self) -> typing.Optional[jsii.Number]:
        '''The minimum amount of time in seconds to keep binlog entries before deletion.

        This may be extended for services that require binlog entries for longer than the default for example if using the MySQL Debezium Kafka connector.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#binlog_retention_period ManagedDatabaseMysql#binlog_retention_period}
        '''
        result = self._values.get("binlog_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''connect_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#connect_timeout ManagedDatabaseMysql#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_time_zone(self) -> typing.Optional[builtins.str]:
        '''default_time_zone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#default_time_zone ManagedDatabaseMysql#default_time_zone}
        '''
        result = self._values.get("default_time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_concat_max_len(self) -> typing.Optional[jsii.Number]:
        '''group_concat_max_len.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#group_concat_max_len ManagedDatabaseMysql#group_concat_max_len}
        '''
        result = self._values.get("group_concat_max_len")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def information_schema_stats_expiry(self) -> typing.Optional[jsii.Number]:
        '''information_schema_stats_expiry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#information_schema_stats_expiry ManagedDatabaseMysql#information_schema_stats_expiry}
        '''
        result = self._values.get("information_schema_stats_expiry")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_min_token_size(self) -> typing.Optional[jsii.Number]:
        '''innodb_ft_min_token_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_min_token_size ManagedDatabaseMysql#innodb_ft_min_token_size}
        '''
        result = self._values.get("innodb_ft_min_token_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_server_stopword_table(self) -> typing.Optional[builtins.str]:
        '''innodb_ft_server_stopword_table.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_ft_server_stopword_table ManagedDatabaseMysql#innodb_ft_server_stopword_table}
        '''
        result = self._values.get("innodb_ft_server_stopword_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def innodb_lock_wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''innodb_lock_wait_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_lock_wait_timeout ManagedDatabaseMysql#innodb_lock_wait_timeout}
        '''
        result = self._values.get("innodb_lock_wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_log_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''innodb_log_buffer_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_log_buffer_size ManagedDatabaseMysql#innodb_log_buffer_size}
        '''
        result = self._values.get("innodb_log_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_online_alter_log_max_size(self) -> typing.Optional[jsii.Number]:
        '''innodb_online_alter_log_max_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_online_alter_log_max_size ManagedDatabaseMysql#innodb_online_alter_log_max_size}
        '''
        result = self._values.get("innodb_online_alter_log_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''innodb_print_all_deadlocks.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_print_all_deadlocks ManagedDatabaseMysql#innodb_print_all_deadlocks}
        '''
        result = self._values.get("innodb_print_all_deadlocks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''innodb_rollback_on_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#innodb_rollback_on_timeout ManagedDatabaseMysql#innodb_rollback_on_timeout}
        '''
        result = self._values.get("innodb_rollback_on_timeout")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def interactive_timeout(self) -> typing.Optional[jsii.Number]:
        '''interactive_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#interactive_timeout ManagedDatabaseMysql#interactive_timeout}
        '''
        result = self._values.get("interactive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def internal_tmp_mem_storage_engine(self) -> typing.Optional[builtins.str]:
        '''internal_tmp_mem_storage_engine.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#internal_tmp_mem_storage_engine ManagedDatabaseMysql#internal_tmp_mem_storage_engine}
        '''
        result = self._values.get("internal_tmp_mem_storage_engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ip_filter ManagedDatabaseMysql#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def long_query_time(self) -> typing.Optional[jsii.Number]:
        '''long_query_time.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#long_query_time ManagedDatabaseMysql#long_query_time}
        '''
        result = self._values.get("long_query_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_allowed_packet(self) -> typing.Optional[jsii.Number]:
        '''max_allowed_packet.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_allowed_packet ManagedDatabaseMysql#max_allowed_packet}
        '''
        result = self._values.get("max_allowed_packet")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_heap_table_size(self) -> typing.Optional[jsii.Number]:
        '''max_heap_table_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#max_heap_table_size ManagedDatabaseMysql#max_heap_table_size}
        '''
        result = self._values.get("max_heap_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def migration(self) -> typing.Optional["ManagedDatabaseMysqlPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#migration ManagedDatabaseMysql#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabaseMysqlPropertiesMigration"], result)

    @builtins.property
    def net_read_timeout(self) -> typing.Optional[jsii.Number]:
        '''net_read_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_read_timeout ManagedDatabaseMysql#net_read_timeout}
        '''
        result = self._values.get("net_read_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def net_write_timeout(self) -> typing.Optional[jsii.Number]:
        '''net_write_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#net_write_timeout ManagedDatabaseMysql#net_write_timeout}
        '''
        result = self._values.get("net_write_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Public Access.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#public_access ManagedDatabaseMysql#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def slow_query_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''slow_query_log.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#slow_query_log ManagedDatabaseMysql#slow_query_log}
        '''
        result = self._values.get("slow_query_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def sort_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''sort_buffer_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sort_buffer_size ManagedDatabaseMysql#sort_buffer_size}
        '''
        result = self._values.get("sort_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sql_mode(self) -> typing.Optional[builtins.str]:
        '''sql_mode.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_mode ManagedDatabaseMysql#sql_mode}
        '''
        result = self._values.get("sql_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_require_primary_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''sql_require_primary_key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#sql_require_primary_key ManagedDatabaseMysql#sql_require_primary_key}
        '''
        result = self._values.get("sql_require_primary_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tmp_table_size(self) -> typing.Optional[jsii.Number]:
        '''tmp_table_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#tmp_table_size ManagedDatabaseMysql#tmp_table_size}
        '''
        result = self._values.get("tmp_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''MySQL major version.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#version ManagedDatabaseMysql#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''wait_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#wait_timeout ManagedDatabaseMysql#wait_timeout}
        '''
        result = self._values.get("wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlPropertiesMigration",
    jsii_struct_bases=[],
    name_mapping={
        "dbname": "dbname",
        "host": "host",
        "ignore_dbs": "ignoreDbs",
        "password": "password",
        "port": "port",
        "ssl": "ssl",
        "username": "username",
    },
)
class ManagedDatabaseMysqlPropertiesMigration:
    def __init__(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#host ManagedDatabaseMysql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#password ManagedDatabaseMysql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#port ManagedDatabaseMysql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dbname is not None:
            self._values["dbname"] = dbname
        if host is not None:
            self._values["host"] = host
        if ignore_dbs is not None:
            self._values["ignore_dbs"] = ignore_dbs
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if ssl is not None:
            self._values["ssl"] = ssl
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def dbname(self) -> typing.Optional[builtins.str]:
        '''Database name for bootstrapping the initial connection.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#host ManagedDatabaseMysql#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#password ManagedDatabaseMysql#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#port ManagedDatabaseMysql#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseMysqlPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabaseMysqlPropertiesMigrationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlPropertiesMigrationOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDbname")
    def reset_dbname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbname", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetIgnoreDbs")
    def reset_ignore_dbs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreDbs", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbnameInput")
    def dbname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDbsInput")
    def ignore_dbs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ignoreDbsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbname")
    def dbname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbname"))

    @dbname.setter
    def dbname(self, value: builtins.str) -> None:
        jsii.set(self, "dbname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        jsii.set(self, "ignoreDbs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "ssl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlPropertiesMigration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ManagedDatabaseMysqlPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseMysqlPropertiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMigration")
    def put_migration(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#dbname ManagedDatabaseMysql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#host ManagedDatabaseMysql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ignore_dbs ManagedDatabaseMysql#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#password ManagedDatabaseMysql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#port ManagedDatabaseMysql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#ssl ManagedDatabaseMysql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_mysql#username ManagedDatabaseMysql#username}
        '''
        value = ManagedDatabaseMysqlPropertiesMigration(
            dbname=dbname,
            host=host,
            ignore_dbs=ignore_dbs,
            password=password,
            port=port,
            ssl=ssl,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putMigration", [value]))

    @jsii.member(jsii_name="resetAdminPassword")
    def reset_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPassword", []))

    @jsii.member(jsii_name="resetAdminUsername")
    def reset_admin_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminUsername", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBinlogRetentionPeriod")
    def reset_binlog_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinlogRetentionPeriod", []))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDefaultTimeZone")
    def reset_default_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTimeZone", []))

    @jsii.member(jsii_name="resetGroupConcatMaxLen")
    def reset_group_concat_max_len(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupConcatMaxLen", []))

    @jsii.member(jsii_name="resetInformationSchemaStatsExpiry")
    def reset_information_schema_stats_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInformationSchemaStatsExpiry", []))

    @jsii.member(jsii_name="resetInnodbFtMinTokenSize")
    def reset_innodb_ft_min_token_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtMinTokenSize", []))

    @jsii.member(jsii_name="resetInnodbFtServerStopwordTable")
    def reset_innodb_ft_server_stopword_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtServerStopwordTable", []))

    @jsii.member(jsii_name="resetInnodbLockWaitTimeout")
    def reset_innodb_lock_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLockWaitTimeout", []))

    @jsii.member(jsii_name="resetInnodbLogBufferSize")
    def reset_innodb_log_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLogBufferSize", []))

    @jsii.member(jsii_name="resetInnodbOnlineAlterLogMaxSize")
    def reset_innodb_online_alter_log_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbOnlineAlterLogMaxSize", []))

    @jsii.member(jsii_name="resetInnodbPrintAllDeadlocks")
    def reset_innodb_print_all_deadlocks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbPrintAllDeadlocks", []))

    @jsii.member(jsii_name="resetInnodbRollbackOnTimeout")
    def reset_innodb_rollback_on_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbRollbackOnTimeout", []))

    @jsii.member(jsii_name="resetInteractiveTimeout")
    def reset_interactive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInteractiveTimeout", []))

    @jsii.member(jsii_name="resetInternalTmpMemStorageEngine")
    def reset_internal_tmp_mem_storage_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalTmpMemStorageEngine", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetLongQueryTime")
    def reset_long_query_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongQueryTime", []))

    @jsii.member(jsii_name="resetMaxAllowedPacket")
    def reset_max_allowed_packet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAllowedPacket", []))

    @jsii.member(jsii_name="resetMaxHeapTableSize")
    def reset_max_heap_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxHeapTableSize", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetNetReadTimeout")
    def reset_net_read_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetReadTimeout", []))

    @jsii.member(jsii_name="resetNetWriteTimeout")
    def reset_net_write_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetWriteTimeout", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetSlowQueryLog")
    def reset_slow_query_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlowQueryLog", []))

    @jsii.member(jsii_name="resetSortBufferSize")
    def reset_sort_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortBufferSize", []))

    @jsii.member(jsii_name="resetSqlMode")
    def reset_sql_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlMode", []))

    @jsii.member(jsii_name="resetSqlRequirePrimaryKey")
    def reset_sql_require_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlRequirePrimaryKey", []))

    @jsii.member(jsii_name="resetTmpTableSize")
    def reset_tmp_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTmpTableSize", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetWaitTimeout")
    def reset_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabaseMysqlPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabaseMysqlPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminPasswordInput")
    def admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUsernameInput")
    def admin_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binlogRetentionPeriodInput")
    def binlog_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "binlogRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTimeZoneInput")
    def default_time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTimeZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupConcatMaxLenInput")
    def group_concat_max_len_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupConcatMaxLenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="informationSchemaStatsExpiryInput")
    def information_schema_stats_expiry_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "informationSchemaStatsExpiryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbFtMinTokenSizeInput")
    def innodb_ft_min_token_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbFtMinTokenSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbFtServerStopwordTableInput")
    def innodb_ft_server_stopword_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "innodbFtServerStopwordTableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbLockWaitTimeoutInput")
    def innodb_lock_wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLockWaitTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbLogBufferSizeInput")
    def innodb_log_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLogBufferSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSizeInput")
    def innodb_online_alter_log_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbOnlineAlterLogMaxSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbPrintAllDeadlocksInput")
    def innodb_print_all_deadlocks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "innodbPrintAllDeadlocksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbRollbackOnTimeoutInput")
    def innodb_rollback_on_timeout_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "innodbRollbackOnTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interactiveTimeoutInput")
    def interactive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "interactiveTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalTmpMemStorageEngineInput")
    def internal_tmp_mem_storage_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "internalTmpMemStorageEngineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="longQueryTimeInput")
    def long_query_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longQueryTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAllowedPacketInput")
    def max_allowed_packet_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAllowedPacketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxHeapTableSizeInput")
    def max_heap_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxHeapTableSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabaseMysqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netReadTimeoutInput")
    def net_read_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netReadTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netWriteTimeoutInput")
    def net_write_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netWriteTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slowQueryLogInput")
    def slow_query_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "slowQueryLogInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortBufferSizeInput")
    def sort_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sortBufferSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlModeInput")
    def sql_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlRequirePrimaryKeyInput")
    def sql_require_primary_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "sqlRequirePrimaryKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpTableSizeInput")
    def tmp_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tmpTableSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimeoutInput")
    def wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        jsii.set(self, "adminPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUsername")
    def admin_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminUsername"))

    @admin_username.setter
    def admin_username(self, value: builtins.str) -> None:
        jsii.set(self, "adminUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilter")
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "automaticUtilityNetworkIpFilter"))

    @automatic_utility_network_ip_filter.setter
    def automatic_utility_network_ip_filter(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "automaticUtilityNetworkIpFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        jsii.set(self, "backupHour", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        jsii.set(self, "backupMinute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binlogRetentionPeriod")
    def binlog_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "binlogRetentionPeriod"))

    @binlog_retention_period.setter
    def binlog_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "binlogRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "connectTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTimeZone")
    def default_time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultTimeZone"))

    @default_time_zone.setter
    def default_time_zone(self, value: builtins.str) -> None:
        jsii.set(self, "defaultTimeZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupConcatMaxLen")
    def group_concat_max_len(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupConcatMaxLen"))

    @group_concat_max_len.setter
    def group_concat_max_len(self, value: jsii.Number) -> None:
        jsii.set(self, "groupConcatMaxLen", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="informationSchemaStatsExpiry")
    def information_schema_stats_expiry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "informationSchemaStatsExpiry"))

    @information_schema_stats_expiry.setter
    def information_schema_stats_expiry(self, value: jsii.Number) -> None:
        jsii.set(self, "informationSchemaStatsExpiry", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbFtMinTokenSize")
    def innodb_ft_min_token_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbFtMinTokenSize"))

    @innodb_ft_min_token_size.setter
    def innodb_ft_min_token_size(self, value: jsii.Number) -> None:
        jsii.set(self, "innodbFtMinTokenSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbFtServerStopwordTable")
    def innodb_ft_server_stopword_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "innodbFtServerStopwordTable"))

    @innodb_ft_server_stopword_table.setter
    def innodb_ft_server_stopword_table(self, value: builtins.str) -> None:
        jsii.set(self, "innodbFtServerStopwordTable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbLockWaitTimeout")
    def innodb_lock_wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLockWaitTimeout"))

    @innodb_lock_wait_timeout.setter
    def innodb_lock_wait_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "innodbLockWaitTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbLogBufferSize")
    def innodb_log_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLogBufferSize"))

    @innodb_log_buffer_size.setter
    def innodb_log_buffer_size(self, value: jsii.Number) -> None:
        jsii.set(self, "innodbLogBufferSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSize")
    def innodb_online_alter_log_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbOnlineAlterLogMaxSize"))

    @innodb_online_alter_log_max_size.setter
    def innodb_online_alter_log_max_size(self, value: jsii.Number) -> None:
        jsii.set(self, "innodbOnlineAlterLogMaxSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbPrintAllDeadlocks")
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "innodbPrintAllDeadlocks"))

    @innodb_print_all_deadlocks.setter
    def innodb_print_all_deadlocks(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "innodbPrintAllDeadlocks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="innodbRollbackOnTimeout")
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "innodbRollbackOnTimeout"))

    @innodb_rollback_on_timeout.setter
    def innodb_rollback_on_timeout(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "innodbRollbackOnTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interactiveTimeout")
    def interactive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interactiveTimeout"))

    @interactive_timeout.setter
    def interactive_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "interactiveTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalTmpMemStorageEngine")
    def internal_tmp_mem_storage_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalTmpMemStorageEngine"))

    @internal_tmp_mem_storage_engine.setter
    def internal_tmp_mem_storage_engine(self, value: builtins.str) -> None:
        jsii.set(self, "internalTmpMemStorageEngine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="longQueryTime")
    def long_query_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longQueryTime"))

    @long_query_time.setter
    def long_query_time(self, value: jsii.Number) -> None:
        jsii.set(self, "longQueryTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAllowedPacket")
    def max_allowed_packet(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAllowedPacket"))

    @max_allowed_packet.setter
    def max_allowed_packet(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAllowedPacket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxHeapTableSize")
    def max_heap_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxHeapTableSize"))

    @max_heap_table_size.setter
    def max_heap_table_size(self, value: jsii.Number) -> None:
        jsii.set(self, "maxHeapTableSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netReadTimeout")
    def net_read_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netReadTimeout"))

    @net_read_timeout.setter
    def net_read_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "netReadTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netWriteTimeout")
    def net_write_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netWriteTimeout"))

    @net_write_timeout.setter
    def net_write_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "netWriteTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccess")
    def public_access(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publicAccess"))

    @public_access.setter
    def public_access(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publicAccess", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slowQueryLog")
    def slow_query_log(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "slowQueryLog"))

    @slow_query_log.setter
    def slow_query_log(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "slowQueryLog", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sortBufferSize")
    def sort_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sortBufferSize"))

    @sort_buffer_size.setter
    def sort_buffer_size(self, value: jsii.Number) -> None:
        jsii.set(self, "sortBufferSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlMode")
    def sql_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlMode"))

    @sql_mode.setter
    def sql_mode(self, value: builtins.str) -> None:
        jsii.set(self, "sqlMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlRequirePrimaryKey")
    def sql_require_primary_key(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "sqlRequirePrimaryKey"))

    @sql_require_primary_key.setter
    def sql_require_primary_key(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "sqlRequirePrimaryKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpTableSize")
    def tmp_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tmpTableSize"))

    @tmp_table_size.setter
    def tmp_table_size(self, value: jsii.Number) -> None:
        jsii.set(self, "tmpTableSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitTimeout")
    def wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitTimeout"))

    @wait_timeout.setter
    def wait_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "waitTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabaseMysqlProperties]:
        return typing.cast(typing.Optional[ManagedDatabaseMysqlProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabaseMysqlProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ManagedDatabasePostgresql(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresql",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql upcloud_managed_database_postgresql}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        properties: typing.Optional["ManagedDatabasePostgresqlProperties"] = None,
        title: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql upcloud_managed_database_postgresql} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        :param zone: Zone where the instance resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ManagedDatabasePostgresqlConfig(
            name=name,
            plan=plan,
            zone=zone,
            maintenance_window_dow=maintenance_window_dow,
            maintenance_window_time=maintenance_window_time,
            powered=powered,
            properties=properties,
            title=title,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        jit: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        migration: typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"] = None,
        pgbouncer: typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"] = None,
        pglookout: typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_read_replica: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pg_service_to_fork_from: typing.Optional[builtins.str] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        synchronous_replication: typing.Optional[builtins.str] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        variant: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        :param autovacuum_analyze_scale_factor: autovacuum_analyze_scale_factor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        :param autovacuum_analyze_threshold: autovacuum_analyze_threshold. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        :param autovacuum_freeze_max_age: autovacuum_freeze_max_age. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        :param autovacuum_max_workers: autovacuum_max_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        :param autovacuum_naptime: autovacuum_naptime. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        :param autovacuum_vacuum_cost_delay: autovacuum_vacuum_cost_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        :param autovacuum_vacuum_cost_limit: autovacuum_vacuum_cost_limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        :param autovacuum_vacuum_scale_factor: autovacuum_vacuum_scale_factor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        :param autovacuum_vacuum_threshold: autovacuum_vacuum_threshold. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        :param bgwriter_delay: bgwriter_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        :param bgwriter_flush_after: bgwriter_flush_after. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        :param bgwriter_lru_maxpages: bgwriter_lru_maxpages. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        :param bgwriter_lru_multiplier: bgwriter_lru_multiplier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        :param deadlock_timeout: deadlock_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        :param idle_in_transaction_session_timeout: idle_in_transaction_session_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        :param jit: jit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        :param log_autovacuum_min_duration: log_autovacuum_min_duration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        :param log_error_verbosity: log_error_verbosity. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        :param log_line_prefix: log_line_prefix. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        :param log_min_duration_statement: log_min_duration_statement. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        :param max_files_per_process: max_files_per_process. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        :param max_locks_per_transaction: max_locks_per_transaction. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        :param max_logical_replication_workers: max_logical_replication_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        :param max_parallel_workers: max_parallel_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        :param max_parallel_workers_per_gather: max_parallel_workers_per_gather. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        :param max_pred_locks_per_transaction: max_pred_locks_per_transaction. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        :param max_prepared_transactions: max_prepared_transactions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        :param max_replication_slots: max_replication_slots. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        :param max_stack_depth: max_stack_depth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        :param max_standby_archive_delay: max_standby_archive_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        :param max_standby_streaming_delay: max_standby_streaming_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        :param max_wal_senders: max_wal_senders. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        :param max_worker_processes: max_worker_processes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        :param migration: migration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        :param pglookout: pglookout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        :param pg_partman_bgw_interval: pg_partman_bgw.interval. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        :param pg_partman_bgw_role: pg_partman_bgw.role. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        :param pg_read_replica: Should the service which is being forked be a read replica. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_read_replica ManagedDatabasePostgresql#pg_read_replica}
        :param pg_service_to_fork_from: Name of the PG Service from which to fork (deprecated, use service_to_fork_from). This has effect only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_service_to_fork_from ManagedDatabasePostgresql#pg_service_to_fork_from}
        :param pg_stat_statements_track: pg_stat_statements.track. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        :param public_access: Public Access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        :param shared_buffers_percentage: shared_buffers_percentage. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        :param synchronous_replication: Synchronous replication type. Note that the service plan also needs to support synchronous replication. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        :param temp_file_limit: temp_file_limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        :param timezone: timezone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        :param track_activity_query_size: track_activity_query_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        :param track_commit_timestamp: track_commit_timestamp. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        :param track_functions: track_functions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        :param track_io_timing: track_io_timing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        :param variant: Variant of the PostgreSQL service, may affect the features that are exposed by default. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        :param version: PostgreSQL major version. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        :param wal_sender_timeout: wal_sender_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        :param wal_writer_delay: wal_writer_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        :param work_mem: work_mem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        value = ManagedDatabasePostgresqlProperties(
            admin_password=admin_password,
            admin_username=admin_username,
            automatic_utility_network_ip_filter=automatic_utility_network_ip_filter,
            autovacuum_analyze_scale_factor=autovacuum_analyze_scale_factor,
            autovacuum_analyze_threshold=autovacuum_analyze_threshold,
            autovacuum_freeze_max_age=autovacuum_freeze_max_age,
            autovacuum_max_workers=autovacuum_max_workers,
            autovacuum_naptime=autovacuum_naptime,
            autovacuum_vacuum_cost_delay=autovacuum_vacuum_cost_delay,
            autovacuum_vacuum_cost_limit=autovacuum_vacuum_cost_limit,
            autovacuum_vacuum_scale_factor=autovacuum_vacuum_scale_factor,
            autovacuum_vacuum_threshold=autovacuum_vacuum_threshold,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            bgwriter_delay=bgwriter_delay,
            bgwriter_flush_after=bgwriter_flush_after,
            bgwriter_lru_maxpages=bgwriter_lru_maxpages,
            bgwriter_lru_multiplier=bgwriter_lru_multiplier,
            deadlock_timeout=deadlock_timeout,
            idle_in_transaction_session_timeout=idle_in_transaction_session_timeout,
            ip_filter=ip_filter,
            jit=jit,
            log_autovacuum_min_duration=log_autovacuum_min_duration,
            log_error_verbosity=log_error_verbosity,
            log_line_prefix=log_line_prefix,
            log_min_duration_statement=log_min_duration_statement,
            max_files_per_process=max_files_per_process,
            max_locks_per_transaction=max_locks_per_transaction,
            max_logical_replication_workers=max_logical_replication_workers,
            max_parallel_workers=max_parallel_workers,
            max_parallel_workers_per_gather=max_parallel_workers_per_gather,
            max_pred_locks_per_transaction=max_pred_locks_per_transaction,
            max_prepared_transactions=max_prepared_transactions,
            max_replication_slots=max_replication_slots,
            max_stack_depth=max_stack_depth,
            max_standby_archive_delay=max_standby_archive_delay,
            max_standby_streaming_delay=max_standby_streaming_delay,
            max_wal_senders=max_wal_senders,
            max_worker_processes=max_worker_processes,
            migration=migration,
            pgbouncer=pgbouncer,
            pglookout=pglookout,
            pg_partman_bgw_interval=pg_partman_bgw_interval,
            pg_partman_bgw_role=pg_partman_bgw_role,
            pg_read_replica=pg_read_replica,
            pg_service_to_fork_from=pg_service_to_fork_from,
            pg_stat_statements_track=pg_stat_statements_track,
            public_access=public_access,
            shared_buffers_percentage=shared_buffers_percentage,
            synchronous_replication=synchronous_replication,
            temp_file_limit=temp_file_limit,
            timescaledb=timescaledb,
            timezone=timezone,
            track_activity_query_size=track_activity_query_size,
            track_commit_timestamp=track_commit_timestamp,
            track_functions=track_functions,
            track_io_timing=track_io_timing,
            variant=variant,
            version=version,
            wal_sender_timeout=wal_sender_timeout,
            wal_writer_delay=wal_writer_delay,
            work_mem=work_mem,
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetMaintenanceWindowDow")
    def reset_maintenance_window_dow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowDow", []))

    @jsii.member(jsii_name="resetMaintenanceWindowTime")
    def reset_maintenance_window_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindowTime", []))

    @jsii.member(jsii_name="resetPowered")
    def reset_powered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPowered", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="components")
    def components(self) -> "ManagedDatabasePostgresqlComponentsList":
        return typing.cast("ManagedDatabasePostgresqlComponentsList", jsii.get(self, "components"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeStates")
    def node_states(self) -> "ManagedDatabasePostgresqlNodeStatesList":
        return typing.cast("ManagedDatabasePostgresqlNodeStatesList", jsii.get(self, "nodeStates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryDatabase")
    def primary_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryDatabase"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="properties")
    def properties(self) -> "ManagedDatabasePostgresqlPropertiesOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceHost")
    def service_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceHost"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servicePassword")
    def service_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePassword"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceUri")
    def service_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceUsername")
    def service_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceUsername"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslmode")
    def sslmode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslmode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowDowInput")
    def maintenance_window_dow_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowDowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowTimeInput")
    def maintenance_window_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="poweredInput")
    def powered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "poweredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlProperties"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlProperties"], jsii.get(self, "propertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowDow")
    def maintenance_window_dow(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowDow"))

    @maintenance_window_dow.setter
    def maintenance_window_dow(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindowDow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowTime")
    def maintenance_window_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindowTime"))

    @maintenance_window_time.setter
    def maintenance_window_time(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindowTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        jsii.set(self, "plan", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="powered")
    def powered(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "powered"))

    @powered.setter
    def powered(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "powered", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlComponents",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabasePostgresqlComponents:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlComponents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlComponentsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlComponentsList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabasePostgresqlComponentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ManagedDatabasePostgresqlComponentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class ManagedDatabasePostgresqlComponentsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlComponentsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="route")
    def route(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "route"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usage")
    def usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlComponents]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlComponents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlComponents],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "plan": "plan",
        "zone": "zone",
        "maintenance_window_dow": "maintenanceWindowDow",
        "maintenance_window_time": "maintenanceWindowTime",
        "powered": "powered",
        "properties": "properties",
        "title": "title",
    },
)
class ManagedDatabasePostgresqlConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        plan: builtins.str,
        zone: builtins.str,
        maintenance_window_dow: typing.Optional[builtins.str] = None,
        maintenance_window_time: typing.Optional[builtins.str] = None,
        powered: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        properties: typing.Optional["ManagedDatabasePostgresqlProperties"] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the service. The name is used as a prefix for the logical hostname. Must be unique within an account Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        :param plan: Service plan to use. This determines how much resources the instance will have. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        :param zone: Zone where the instance resides. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        :param maintenance_window_dow: Maintenance window day of week. Lower case weekday name (monday, tuesday, ...). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        :param maintenance_window_time: Maintenance window UTC time in hh:mm:ss format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        :param powered: The administrative power state of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        :param title: Title of a managed database instance. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = ManagedDatabasePostgresqlProperties(**properties)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "plan": plan,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if maintenance_window_dow is not None:
            self._values["maintenance_window_dow"] = maintenance_window_dow
        if maintenance_window_time is not None:
            self._values["maintenance_window_time"] = maintenance_window_time
        if powered is not None:
            self._values["powered"] = powered
        if properties is not None:
            self._values["properties"] = properties
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the service.

        The name is used as a prefix for the logical hostname. Must be unique within an account

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#name ManagedDatabasePostgresql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plan(self) -> builtins.str:
        '''Service plan to use. This determines how much resources the instance will have.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#plan ManagedDatabasePostgresql#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''Zone where the instance resides.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#zone ManagedDatabasePostgresql#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def maintenance_window_dow(self) -> typing.Optional[builtins.str]:
        '''Maintenance window day of week. Lower case weekday name (monday, tuesday, ...).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_dow ManagedDatabasePostgresql#maintenance_window_dow}
        '''
        result = self._values.get("maintenance_window_dow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window_time(self) -> typing.Optional[builtins.str]:
        '''Maintenance window UTC time in hh:mm:ss format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#maintenance_window_time ManagedDatabasePostgresql#maintenance_window_time}
        '''
        result = self._values.get("maintenance_window_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def powered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''The administrative power state of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#powered ManagedDatabasePostgresql#powered}
        '''
        result = self._values.get("powered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def properties(self) -> typing.Optional["ManagedDatabasePostgresqlProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#properties ManagedDatabasePostgresql#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlProperties"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Title of a managed database instance.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#title ManagedDatabasePostgresql#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlNodeStates",
    jsii_struct_bases=[],
    name_mapping={},
)
class ManagedDatabasePostgresqlNodeStates:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlNodeStates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlNodeStatesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlNodeStatesList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedDatabasePostgresqlNodeStatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ManagedDatabasePostgresqlNodeStatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class ManagedDatabasePostgresqlNodeStatesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlNodeStatesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlNodeStates]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlNodeStates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlNodeStates],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlProperties",
    jsii_struct_bases=[],
    name_mapping={
        "admin_password": "adminPassword",
        "admin_username": "adminUsername",
        "automatic_utility_network_ip_filter": "automaticUtilityNetworkIpFilter",
        "autovacuum_analyze_scale_factor": "autovacuumAnalyzeScaleFactor",
        "autovacuum_analyze_threshold": "autovacuumAnalyzeThreshold",
        "autovacuum_freeze_max_age": "autovacuumFreezeMaxAge",
        "autovacuum_max_workers": "autovacuumMaxWorkers",
        "autovacuum_naptime": "autovacuumNaptime",
        "autovacuum_vacuum_cost_delay": "autovacuumVacuumCostDelay",
        "autovacuum_vacuum_cost_limit": "autovacuumVacuumCostLimit",
        "autovacuum_vacuum_scale_factor": "autovacuumVacuumScaleFactor",
        "autovacuum_vacuum_threshold": "autovacuumVacuumThreshold",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "bgwriter_delay": "bgwriterDelay",
        "bgwriter_flush_after": "bgwriterFlushAfter",
        "bgwriter_lru_maxpages": "bgwriterLruMaxpages",
        "bgwriter_lru_multiplier": "bgwriterLruMultiplier",
        "deadlock_timeout": "deadlockTimeout",
        "idle_in_transaction_session_timeout": "idleInTransactionSessionTimeout",
        "ip_filter": "ipFilter",
        "jit": "jit",
        "log_autovacuum_min_duration": "logAutovacuumMinDuration",
        "log_error_verbosity": "logErrorVerbosity",
        "log_line_prefix": "logLinePrefix",
        "log_min_duration_statement": "logMinDurationStatement",
        "max_files_per_process": "maxFilesPerProcess",
        "max_locks_per_transaction": "maxLocksPerTransaction",
        "max_logical_replication_workers": "maxLogicalReplicationWorkers",
        "max_parallel_workers": "maxParallelWorkers",
        "max_parallel_workers_per_gather": "maxParallelWorkersPerGather",
        "max_pred_locks_per_transaction": "maxPredLocksPerTransaction",
        "max_prepared_transactions": "maxPreparedTransactions",
        "max_replication_slots": "maxReplicationSlots",
        "max_stack_depth": "maxStackDepth",
        "max_standby_archive_delay": "maxStandbyArchiveDelay",
        "max_standby_streaming_delay": "maxStandbyStreamingDelay",
        "max_wal_senders": "maxWalSenders",
        "max_worker_processes": "maxWorkerProcesses",
        "migration": "migration",
        "pgbouncer": "pgbouncer",
        "pglookout": "pglookout",
        "pg_partman_bgw_interval": "pgPartmanBgwInterval",
        "pg_partman_bgw_role": "pgPartmanBgwRole",
        "pg_read_replica": "pgReadReplica",
        "pg_service_to_fork_from": "pgServiceToForkFrom",
        "pg_stat_statements_track": "pgStatStatementsTrack",
        "public_access": "publicAccess",
        "shared_buffers_percentage": "sharedBuffersPercentage",
        "synchronous_replication": "synchronousReplication",
        "temp_file_limit": "tempFileLimit",
        "timescaledb": "timescaledb",
        "timezone": "timezone",
        "track_activity_query_size": "trackActivityQuerySize",
        "track_commit_timestamp": "trackCommitTimestamp",
        "track_functions": "trackFunctions",
        "track_io_timing": "trackIoTiming",
        "variant": "variant",
        "version": "version",
        "wal_sender_timeout": "walSenderTimeout",
        "wal_writer_delay": "walWriterDelay",
        "work_mem": "workMem",
    },
)
class ManagedDatabasePostgresqlProperties:
    def __init__(
        self,
        *,
        admin_password: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        automatic_utility_network_ip_filter: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        ip_filter: typing.Optional[typing.Sequence[builtins.str]] = None,
        jit: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        migration: typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"] = None,
        pgbouncer: typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"] = None,
        pglookout: typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_read_replica: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pg_service_to_fork_from: typing.Optional[builtins.str] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        public_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        synchronous_replication: typing.Optional[builtins.str] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        variant: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param admin_password: Custom password for admin user. Defaults to random string. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        :param admin_username: Custom username for admin user. This must be set only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        :param automatic_utility_network_ip_filter: Automatic utility network IP Filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        :param autovacuum_analyze_scale_factor: autovacuum_analyze_scale_factor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        :param autovacuum_analyze_threshold: autovacuum_analyze_threshold. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        :param autovacuum_freeze_max_age: autovacuum_freeze_max_age. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        :param autovacuum_max_workers: autovacuum_max_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        :param autovacuum_naptime: autovacuum_naptime. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        :param autovacuum_vacuum_cost_delay: autovacuum_vacuum_cost_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        :param autovacuum_vacuum_cost_limit: autovacuum_vacuum_cost_limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        :param autovacuum_vacuum_scale_factor: autovacuum_vacuum_scale_factor. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        :param autovacuum_vacuum_threshold: autovacuum_vacuum_threshold. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        :param backup_hour: The hour of day (in UTC) when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        :param backup_minute: The minute of an hour when backup for the service is started. New backup is only started if previous backup has already completed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        :param bgwriter_delay: bgwriter_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        :param bgwriter_flush_after: bgwriter_flush_after. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        :param bgwriter_lru_maxpages: bgwriter_lru_maxpages. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        :param bgwriter_lru_multiplier: bgwriter_lru_multiplier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        :param deadlock_timeout: deadlock_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        :param idle_in_transaction_session_timeout: idle_in_transaction_session_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        :param ip_filter: IP filter. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        :param jit: jit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        :param log_autovacuum_min_duration: log_autovacuum_min_duration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        :param log_error_verbosity: log_error_verbosity. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        :param log_line_prefix: log_line_prefix. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        :param log_min_duration_statement: log_min_duration_statement. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        :param max_files_per_process: max_files_per_process. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        :param max_locks_per_transaction: max_locks_per_transaction. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        :param max_logical_replication_workers: max_logical_replication_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        :param max_parallel_workers: max_parallel_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        :param max_parallel_workers_per_gather: max_parallel_workers_per_gather. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        :param max_pred_locks_per_transaction: max_pred_locks_per_transaction. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        :param max_prepared_transactions: max_prepared_transactions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        :param max_replication_slots: max_replication_slots. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        :param max_stack_depth: max_stack_depth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        :param max_standby_archive_delay: max_standby_archive_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        :param max_standby_streaming_delay: max_standby_streaming_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        :param max_wal_senders: max_wal_senders. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        :param max_worker_processes: max_worker_processes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        :param migration: migration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        :param pglookout: pglookout block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        :param pg_partman_bgw_interval: pg_partman_bgw.interval. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        :param pg_partman_bgw_role: pg_partman_bgw.role. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        :param pg_read_replica: Should the service which is being forked be a read replica. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_read_replica ManagedDatabasePostgresql#pg_read_replica}
        :param pg_service_to_fork_from: Name of the PG Service from which to fork (deprecated, use service_to_fork_from). This has effect only when a new service is being created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_service_to_fork_from ManagedDatabasePostgresql#pg_service_to_fork_from}
        :param pg_stat_statements_track: pg_stat_statements.track. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        :param public_access: Public Access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        :param shared_buffers_percentage: shared_buffers_percentage. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        :param synchronous_replication: Synchronous replication type. Note that the service plan also needs to support synchronous replication. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        :param temp_file_limit: temp_file_limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        :param timezone: timezone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        :param track_activity_query_size: track_activity_query_size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        :param track_commit_timestamp: track_commit_timestamp. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        :param track_functions: track_functions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        :param track_io_timing: track_io_timing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        :param variant: Variant of the PostgreSQL service, may affect the features that are exposed by default. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        :param version: PostgreSQL major version. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        :param wal_sender_timeout: wal_sender_timeout. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        :param wal_writer_delay: wal_writer_delay. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        :param work_mem: work_mem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        if isinstance(migration, dict):
            migration = ManagedDatabasePostgresqlPropertiesMigration(**migration)
        if isinstance(pgbouncer, dict):
            pgbouncer = ManagedDatabasePostgresqlPropertiesPgbouncer(**pgbouncer)
        if isinstance(pglookout, dict):
            pglookout = ManagedDatabasePostgresqlPropertiesPglookout(**pglookout)
        if isinstance(timescaledb, dict):
            timescaledb = ManagedDatabasePostgresqlPropertiesTimescaledb(**timescaledb)
        self._values: typing.Dict[str, typing.Any] = {}
        if admin_password is not None:
            self._values["admin_password"] = admin_password
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if automatic_utility_network_ip_filter is not None:
            self._values["automatic_utility_network_ip_filter"] = automatic_utility_network_ip_filter
        if autovacuum_analyze_scale_factor is not None:
            self._values["autovacuum_analyze_scale_factor"] = autovacuum_analyze_scale_factor
        if autovacuum_analyze_threshold is not None:
            self._values["autovacuum_analyze_threshold"] = autovacuum_analyze_threshold
        if autovacuum_freeze_max_age is not None:
            self._values["autovacuum_freeze_max_age"] = autovacuum_freeze_max_age
        if autovacuum_max_workers is not None:
            self._values["autovacuum_max_workers"] = autovacuum_max_workers
        if autovacuum_naptime is not None:
            self._values["autovacuum_naptime"] = autovacuum_naptime
        if autovacuum_vacuum_cost_delay is not None:
            self._values["autovacuum_vacuum_cost_delay"] = autovacuum_vacuum_cost_delay
        if autovacuum_vacuum_cost_limit is not None:
            self._values["autovacuum_vacuum_cost_limit"] = autovacuum_vacuum_cost_limit
        if autovacuum_vacuum_scale_factor is not None:
            self._values["autovacuum_vacuum_scale_factor"] = autovacuum_vacuum_scale_factor
        if autovacuum_vacuum_threshold is not None:
            self._values["autovacuum_vacuum_threshold"] = autovacuum_vacuum_threshold
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if bgwriter_delay is not None:
            self._values["bgwriter_delay"] = bgwriter_delay
        if bgwriter_flush_after is not None:
            self._values["bgwriter_flush_after"] = bgwriter_flush_after
        if bgwriter_lru_maxpages is not None:
            self._values["bgwriter_lru_maxpages"] = bgwriter_lru_maxpages
        if bgwriter_lru_multiplier is not None:
            self._values["bgwriter_lru_multiplier"] = bgwriter_lru_multiplier
        if deadlock_timeout is not None:
            self._values["deadlock_timeout"] = deadlock_timeout
        if idle_in_transaction_session_timeout is not None:
            self._values["idle_in_transaction_session_timeout"] = idle_in_transaction_session_timeout
        if ip_filter is not None:
            self._values["ip_filter"] = ip_filter
        if jit is not None:
            self._values["jit"] = jit
        if log_autovacuum_min_duration is not None:
            self._values["log_autovacuum_min_duration"] = log_autovacuum_min_duration
        if log_error_verbosity is not None:
            self._values["log_error_verbosity"] = log_error_verbosity
        if log_line_prefix is not None:
            self._values["log_line_prefix"] = log_line_prefix
        if log_min_duration_statement is not None:
            self._values["log_min_duration_statement"] = log_min_duration_statement
        if max_files_per_process is not None:
            self._values["max_files_per_process"] = max_files_per_process
        if max_locks_per_transaction is not None:
            self._values["max_locks_per_transaction"] = max_locks_per_transaction
        if max_logical_replication_workers is not None:
            self._values["max_logical_replication_workers"] = max_logical_replication_workers
        if max_parallel_workers is not None:
            self._values["max_parallel_workers"] = max_parallel_workers
        if max_parallel_workers_per_gather is not None:
            self._values["max_parallel_workers_per_gather"] = max_parallel_workers_per_gather
        if max_pred_locks_per_transaction is not None:
            self._values["max_pred_locks_per_transaction"] = max_pred_locks_per_transaction
        if max_prepared_transactions is not None:
            self._values["max_prepared_transactions"] = max_prepared_transactions
        if max_replication_slots is not None:
            self._values["max_replication_slots"] = max_replication_slots
        if max_stack_depth is not None:
            self._values["max_stack_depth"] = max_stack_depth
        if max_standby_archive_delay is not None:
            self._values["max_standby_archive_delay"] = max_standby_archive_delay
        if max_standby_streaming_delay is not None:
            self._values["max_standby_streaming_delay"] = max_standby_streaming_delay
        if max_wal_senders is not None:
            self._values["max_wal_senders"] = max_wal_senders
        if max_worker_processes is not None:
            self._values["max_worker_processes"] = max_worker_processes
        if migration is not None:
            self._values["migration"] = migration
        if pgbouncer is not None:
            self._values["pgbouncer"] = pgbouncer
        if pglookout is not None:
            self._values["pglookout"] = pglookout
        if pg_partman_bgw_interval is not None:
            self._values["pg_partman_bgw_interval"] = pg_partman_bgw_interval
        if pg_partman_bgw_role is not None:
            self._values["pg_partman_bgw_role"] = pg_partman_bgw_role
        if pg_read_replica is not None:
            self._values["pg_read_replica"] = pg_read_replica
        if pg_service_to_fork_from is not None:
            self._values["pg_service_to_fork_from"] = pg_service_to_fork_from
        if pg_stat_statements_track is not None:
            self._values["pg_stat_statements_track"] = pg_stat_statements_track
        if public_access is not None:
            self._values["public_access"] = public_access
        if shared_buffers_percentage is not None:
            self._values["shared_buffers_percentage"] = shared_buffers_percentage
        if synchronous_replication is not None:
            self._values["synchronous_replication"] = synchronous_replication
        if temp_file_limit is not None:
            self._values["temp_file_limit"] = temp_file_limit
        if timescaledb is not None:
            self._values["timescaledb"] = timescaledb
        if timezone is not None:
            self._values["timezone"] = timezone
        if track_activity_query_size is not None:
            self._values["track_activity_query_size"] = track_activity_query_size
        if track_commit_timestamp is not None:
            self._values["track_commit_timestamp"] = track_commit_timestamp
        if track_functions is not None:
            self._values["track_functions"] = track_functions
        if track_io_timing is not None:
            self._values["track_io_timing"] = track_io_timing
        if variant is not None:
            self._values["variant"] = variant
        if version is not None:
            self._values["version"] = version
        if wal_sender_timeout is not None:
            self._values["wal_sender_timeout"] = wal_sender_timeout
        if wal_writer_delay is not None:
            self._values["wal_writer_delay"] = wal_writer_delay
        if work_mem is not None:
            self._values["work_mem"] = work_mem

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''Custom password for admin user.

        Defaults to random string. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_password ManagedDatabasePostgresql#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''Custom username for admin user. This must be set only when a new service is being created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#admin_username ManagedDatabasePostgresql#admin_username}
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Automatic utility network IP Filter.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#automatic_utility_network_ip_filter ManagedDatabasePostgresql#automatic_utility_network_ip_filter}
        '''
        result = self._values.get("automatic_utility_network_ip_filter")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def autovacuum_analyze_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_analyze_scale_factor.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_scale_factor ManagedDatabasePostgresql#autovacuum_analyze_scale_factor}
        '''
        result = self._values.get("autovacuum_analyze_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_analyze_threshold(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_analyze_threshold.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_analyze_threshold ManagedDatabasePostgresql#autovacuum_analyze_threshold}
        '''
        result = self._values.get("autovacuum_analyze_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_freeze_max_age(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_freeze_max_age.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_freeze_max_age ManagedDatabasePostgresql#autovacuum_freeze_max_age}
        '''
        result = self._values.get("autovacuum_freeze_max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_max_workers(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_max_workers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_max_workers ManagedDatabasePostgresql#autovacuum_max_workers}
        '''
        result = self._values.get("autovacuum_max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_naptime(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_naptime.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_naptime ManagedDatabasePostgresql#autovacuum_naptime}
        '''
        result = self._values.get("autovacuum_naptime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_delay(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_vacuum_cost_delay.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_delay ManagedDatabasePostgresql#autovacuum_vacuum_cost_delay}
        '''
        result = self._values.get("autovacuum_vacuum_cost_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_limit(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_vacuum_cost_limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_cost_limit ManagedDatabasePostgresql#autovacuum_vacuum_cost_limit}
        '''
        result = self._values.get("autovacuum_vacuum_cost_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_vacuum_scale_factor.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_scale_factor ManagedDatabasePostgresql#autovacuum_vacuum_scale_factor}
        '''
        result = self._values.get("autovacuum_vacuum_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_threshold(self) -> typing.Optional[jsii.Number]:
        '''autovacuum_vacuum_threshold.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autovacuum_vacuum_threshold ManagedDatabasePostgresql#autovacuum_vacuum_threshold}
        '''
        result = self._values.get("autovacuum_vacuum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour of day (in UTC) when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_hour ManagedDatabasePostgresql#backup_hour}
        '''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''The minute of an hour when backup for the service is started.

        New backup is only started if previous backup has already completed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#backup_minute ManagedDatabasePostgresql#backup_minute}
        '''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_delay(self) -> typing.Optional[jsii.Number]:
        '''bgwriter_delay.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_delay ManagedDatabasePostgresql#bgwriter_delay}
        '''
        result = self._values.get("bgwriter_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_flush_after(self) -> typing.Optional[jsii.Number]:
        '''bgwriter_flush_after.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_flush_after ManagedDatabasePostgresql#bgwriter_flush_after}
        '''
        result = self._values.get("bgwriter_flush_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_maxpages(self) -> typing.Optional[jsii.Number]:
        '''bgwriter_lru_maxpages.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_maxpages ManagedDatabasePostgresql#bgwriter_lru_maxpages}
        '''
        result = self._values.get("bgwriter_lru_maxpages")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_multiplier(self) -> typing.Optional[jsii.Number]:
        '''bgwriter_lru_multiplier.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#bgwriter_lru_multiplier ManagedDatabasePostgresql#bgwriter_lru_multiplier}
        '''
        result = self._values.get("bgwriter_lru_multiplier")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deadlock_timeout(self) -> typing.Optional[jsii.Number]:
        '''deadlock_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#deadlock_timeout ManagedDatabasePostgresql#deadlock_timeout}
        '''
        result = self._values.get("deadlock_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def idle_in_transaction_session_timeout(self) -> typing.Optional[jsii.Number]:
        '''idle_in_transaction_session_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#idle_in_transaction_session_timeout ManagedDatabasePostgresql#idle_in_transaction_session_timeout}
        '''
        result = self._values.get("idle_in_transaction_session_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_filter(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP filter.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ip_filter ManagedDatabasePostgresql#ip_filter}
        '''
        result = self._values.get("ip_filter")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jit(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''jit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#jit ManagedDatabasePostgresql#jit}
        '''
        result = self._values.get("jit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def log_autovacuum_min_duration(self) -> typing.Optional[jsii.Number]:
        '''log_autovacuum_min_duration.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_autovacuum_min_duration ManagedDatabasePostgresql#log_autovacuum_min_duration}
        '''
        result = self._values.get("log_autovacuum_min_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_error_verbosity(self) -> typing.Optional[builtins.str]:
        '''log_error_verbosity.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_error_verbosity ManagedDatabasePostgresql#log_error_verbosity}
        '''
        result = self._values.get("log_error_verbosity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_line_prefix(self) -> typing.Optional[builtins.str]:
        '''log_line_prefix.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_line_prefix ManagedDatabasePostgresql#log_line_prefix}
        '''
        result = self._values.get("log_line_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_min_duration_statement(self) -> typing.Optional[jsii.Number]:
        '''log_min_duration_statement.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#log_min_duration_statement ManagedDatabasePostgresql#log_min_duration_statement}
        '''
        result = self._values.get("log_min_duration_statement")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_files_per_process(self) -> typing.Optional[jsii.Number]:
        '''max_files_per_process.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_files_per_process ManagedDatabasePostgresql#max_files_per_process}
        '''
        result = self._values.get("max_files_per_process")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''max_locks_per_transaction.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_locks_per_transaction ManagedDatabasePostgresql#max_locks_per_transaction}
        '''
        result = self._values.get("max_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_logical_replication_workers(self) -> typing.Optional[jsii.Number]:
        '''max_logical_replication_workers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_logical_replication_workers ManagedDatabasePostgresql#max_logical_replication_workers}
        '''
        result = self._values.get("max_logical_replication_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers(self) -> typing.Optional[jsii.Number]:
        '''max_parallel_workers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers ManagedDatabasePostgresql#max_parallel_workers}
        '''
        result = self._values.get("max_parallel_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers_per_gather(self) -> typing.Optional[jsii.Number]:
        '''max_parallel_workers_per_gather.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_parallel_workers_per_gather ManagedDatabasePostgresql#max_parallel_workers_per_gather}
        '''
        result = self._values.get("max_parallel_workers_per_gather")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pred_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''max_pred_locks_per_transaction.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_pred_locks_per_transaction ManagedDatabasePostgresql#max_pred_locks_per_transaction}
        '''
        result = self._values.get("max_pred_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_prepared_transactions(self) -> typing.Optional[jsii.Number]:
        '''max_prepared_transactions.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_prepared_transactions ManagedDatabasePostgresql#max_prepared_transactions}
        '''
        result = self._values.get("max_prepared_transactions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_replication_slots(self) -> typing.Optional[jsii.Number]:
        '''max_replication_slots.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_replication_slots ManagedDatabasePostgresql#max_replication_slots}
        '''
        result = self._values.get("max_replication_slots")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_stack_depth(self) -> typing.Optional[jsii.Number]:
        '''max_stack_depth.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_stack_depth ManagedDatabasePostgresql#max_stack_depth}
        '''
        result = self._values.get("max_stack_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''max_standby_archive_delay.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_archive_delay ManagedDatabasePostgresql#max_standby_archive_delay}
        '''
        result = self._values.get("max_standby_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_streaming_delay(self) -> typing.Optional[jsii.Number]:
        '''max_standby_streaming_delay.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_standby_streaming_delay ManagedDatabasePostgresql#max_standby_streaming_delay}
        '''
        result = self._values.get("max_standby_streaming_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_wal_senders(self) -> typing.Optional[jsii.Number]:
        '''max_wal_senders.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_wal_senders ManagedDatabasePostgresql#max_wal_senders}
        '''
        result = self._values.get("max_wal_senders")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_worker_processes(self) -> typing.Optional[jsii.Number]:
        '''max_worker_processes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_worker_processes ManagedDatabasePostgresql#max_worker_processes}
        '''
        result = self._values.get("max_worker_processes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def migration(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"]:
        '''migration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#migration ManagedDatabasePostgresql#migration}
        '''
        result = self._values.get("migration")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesMigration"], result)

    @builtins.property
    def pgbouncer(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"]:
        '''pgbouncer block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pgbouncer ManagedDatabasePostgresql#pgbouncer}
        '''
        result = self._values.get("pgbouncer")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"], result)

    @builtins.property
    def pglookout(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"]:
        '''pglookout block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pglookout ManagedDatabasePostgresql#pglookout}
        '''
        result = self._values.get("pglookout")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"], result)

    @builtins.property
    def pg_partman_bgw_interval(self) -> typing.Optional[jsii.Number]:
        '''pg_partman_bgw.interval.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_interval ManagedDatabasePostgresql#pg_partman_bgw_interval}
        '''
        result = self._values.get("pg_partman_bgw_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pg_partman_bgw_role(self) -> typing.Optional[builtins.str]:
        '''pg_partman_bgw.role.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_partman_bgw_role ManagedDatabasePostgresql#pg_partman_bgw_role}
        '''
        result = self._values.get("pg_partman_bgw_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pg_read_replica(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Should the service which is being forked be a read replica.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_read_replica ManagedDatabasePostgresql#pg_read_replica}
        '''
        result = self._values.get("pg_read_replica")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def pg_service_to_fork_from(self) -> typing.Optional[builtins.str]:
        '''Name of the PG Service from which to fork (deprecated, use service_to_fork_from).

        This has effect only when a new service is being created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_service_to_fork_from ManagedDatabasePostgresql#pg_service_to_fork_from}
        '''
        result = self._values.get("pg_service_to_fork_from")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pg_stat_statements_track(self) -> typing.Optional[builtins.str]:
        '''pg_stat_statements.track.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#pg_stat_statements_track ManagedDatabasePostgresql#pg_stat_statements_track}
        '''
        result = self._values.get("pg_stat_statements_track")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Public Access.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#public_access ManagedDatabasePostgresql#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def shared_buffers_percentage(self) -> typing.Optional[jsii.Number]:
        '''shared_buffers_percentage.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#shared_buffers_percentage ManagedDatabasePostgresql#shared_buffers_percentage}
        '''
        result = self._values.get("shared_buffers_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def synchronous_replication(self) -> typing.Optional[builtins.str]:
        '''Synchronous replication type. Note that the service plan also needs to support synchronous replication.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#synchronous_replication ManagedDatabasePostgresql#synchronous_replication}
        '''
        result = self._values.get("synchronous_replication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def temp_file_limit(self) -> typing.Optional[jsii.Number]:
        '''temp_file_limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#temp_file_limit ManagedDatabasePostgresql#temp_file_limit}
        '''
        result = self._values.get("temp_file_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timescaledb(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"]:
        '''timescaledb block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timescaledb ManagedDatabasePostgresql#timescaledb}
        '''
        result = self._values.get("timescaledb")
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''timezone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#timezone ManagedDatabasePostgresql#timezone}
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_activity_query_size(self) -> typing.Optional[jsii.Number]:
        '''track_activity_query_size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_activity_query_size ManagedDatabasePostgresql#track_activity_query_size}
        '''
        result = self._values.get("track_activity_query_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def track_commit_timestamp(self) -> typing.Optional[builtins.str]:
        '''track_commit_timestamp.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_commit_timestamp ManagedDatabasePostgresql#track_commit_timestamp}
        '''
        result = self._values.get("track_commit_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_functions(self) -> typing.Optional[builtins.str]:
        '''track_functions.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_functions ManagedDatabasePostgresql#track_functions}
        '''
        result = self._values.get("track_functions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_io_timing(self) -> typing.Optional[builtins.str]:
        '''track_io_timing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#track_io_timing ManagedDatabasePostgresql#track_io_timing}
        '''
        result = self._values.get("track_io_timing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variant(self) -> typing.Optional[builtins.str]:
        '''Variant of the PostgreSQL service, may affect the features that are exposed by default.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#variant ManagedDatabasePostgresql#variant}
        '''
        result = self._values.get("variant")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL major version.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#version ManagedDatabasePostgresql#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wal_sender_timeout(self) -> typing.Optional[jsii.Number]:
        '''wal_sender_timeout.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_sender_timeout ManagedDatabasePostgresql#wal_sender_timeout}
        '''
        result = self._values.get("wal_sender_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def wal_writer_delay(self) -> typing.Optional[jsii.Number]:
        '''wal_writer_delay.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#wal_writer_delay ManagedDatabasePostgresql#wal_writer_delay}
        '''
        result = self._values.get("wal_writer_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def work_mem(self) -> typing.Optional[jsii.Number]:
        '''work_mem.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#work_mem ManagedDatabasePostgresql#work_mem}
        '''
        result = self._values.get("work_mem")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesMigration",
    jsii_struct_bases=[],
    name_mapping={
        "dbname": "dbname",
        "host": "host",
        "ignore_dbs": "ignoreDbs",
        "password": "password",
        "port": "port",
        "ssl": "ssl",
        "username": "username",
    },
)
class ManagedDatabasePostgresqlPropertiesMigration:
    def __init__(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dbname is not None:
            self._values["dbname"] = dbname
        if host is not None:
            self._values["host"] = host
        if ignore_dbs is not None:
            self._values["ignore_dbs"] = ignore_dbs
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if ssl is not None:
            self._values["ssl"] = ssl
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def dbname(self) -> typing.Optional[builtins.str]:
        '''Database name for bootstrapping the initial connection.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        '''
        result = self._values.get("dbname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Hostname or IP address of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_dbs(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        '''
        result = self._values.get("ignore_dbs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Port number of the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''The server where to migrate data from is secured with SSL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''User name for authentication with the server where to migrate data from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesMigration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesMigrationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesMigrationOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDbname")
    def reset_dbname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbname", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetIgnoreDbs")
    def reset_ignore_dbs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreDbs", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbnameInput")
    def dbname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDbsInput")
    def ignore_dbs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ignoreDbsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbname")
    def dbname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbname"))

    @dbname.setter
    def dbname(self, value: builtins.str) -> None:
        jsii.set(self, "dbname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreDbs")
    def ignore_dbs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ignoreDbs"))

    @ignore_dbs.setter
    def ignore_dbs(self, value: builtins.str) -> None:
        jsii.set(self, "ignoreDbs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "ssl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesMigration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesMigration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ManagedDatabasePostgresqlPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMigration")
    def put_migration(
        self,
        *,
        dbname: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_dbs: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dbname: Database name for bootstrapping the initial connection. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#dbname ManagedDatabasePostgresql#dbname}
        :param host: Hostname or IP address of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#host ManagedDatabasePostgresql#host}
        :param ignore_dbs: Comma-separated list of databases, which should be ignored during migration (supported by MySQL only at the moment). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_dbs ManagedDatabasePostgresql#ignore_dbs}
        :param password: Password for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#password ManagedDatabasePostgresql#password}
        :param port: Port number of the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#port ManagedDatabasePostgresql#port}
        :param ssl: The server where to migrate data from is secured with SSL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ssl ManagedDatabasePostgresql#ssl}
        :param username: User name for authentication with the server where to migrate data from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#username ManagedDatabasePostgresql#username}
        '''
        value = ManagedDatabasePostgresqlPropertiesMigration(
            dbname=dbname,
            host=host,
            ignore_dbs=ignore_dbs,
            password=password,
            port=port,
            ssl=ssl,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putMigration", [value]))

    @jsii.member(jsii_name="putPgbouncer")
    def put_pgbouncer(
        self,
        *,
        autodb_idle_timeout: typing.Optional[jsii.Number] = None,
        autodb_max_db_connections: typing.Optional[jsii.Number] = None,
        autodb_pool_mode: typing.Optional[builtins.str] = None,
        autodb_pool_size: typing.Optional[jsii.Number] = None,
        ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        min_pool_size: typing.Optional[jsii.Number] = None,
        server_idle_timeout: typing.Optional[jsii.Number] = None,
        server_lifetime: typing.Optional[jsii.Number] = None,
        server_reset_query_always: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param autodb_idle_timeout: If the automatically created database pools have been unused this many seconds, they are freed. If 0 then timeout is disabled. [seconds] Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        :param autodb_max_db_connections: Do not allow more than this many server connections per database (regardless of user). Setting it to 0 means unlimited. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        :param autodb_pool_mode: PGBouncer pool mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        :param autodb_pool_size: If non-zero then create automatically a pool of that size per user when a pool doesn't exist. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        :param ignore_startup_parameters: List of parameters to ignore when given in startup packet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        :param min_pool_size: Add more server connections to pool if below this number. Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        :param server_idle_timeout: If a server connection has been idle more than this many seconds it will be dropped. If 0 then timeout is disabled. [seconds] Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        :param server_lifetime: The pooler will close an unused server connection that has been connected longer than this. [seconds]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        :param server_reset_query_always: Run server_reset_query (DISCARD ALL) in all pooling modes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        value = ManagedDatabasePostgresqlPropertiesPgbouncer(
            autodb_idle_timeout=autodb_idle_timeout,
            autodb_max_db_connections=autodb_max_db_connections,
            autodb_pool_mode=autodb_pool_mode,
            autodb_pool_size=autodb_pool_size,
            ignore_startup_parameters=ignore_startup_parameters,
            min_pool_size=min_pool_size,
            server_idle_timeout=server_idle_timeout,
            server_lifetime=server_lifetime,
            server_reset_query_always=server_reset_query_always,
        )

        return typing.cast(None, jsii.invoke(self, "putPgbouncer", [value]))

    @jsii.member(jsii_name="putPglookout")
    def put_pglookout(
        self,
        *,
        max_failover_replication_time_lag: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_failover_replication_time_lag: max_failover_replication_time_lag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        value = ManagedDatabasePostgresqlPropertiesPglookout(
            max_failover_replication_time_lag=max_failover_replication_time_lag
        )

        return typing.cast(None, jsii.invoke(self, "putPglookout", [value]))

    @jsii.member(jsii_name="putTimescaledb")
    def put_timescaledb(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: timescaledb.max_background_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        value = ManagedDatabasePostgresqlPropertiesTimescaledb(
            max_background_workers=max_background_workers
        )

        return typing.cast(None, jsii.invoke(self, "putTimescaledb", [value]))

    @jsii.member(jsii_name="resetAdminPassword")
    def reset_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPassword", []))

    @jsii.member(jsii_name="resetAdminUsername")
    def reset_admin_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminUsername", []))

    @jsii.member(jsii_name="resetAutomaticUtilityNetworkIpFilter")
    def reset_automatic_utility_network_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticUtilityNetworkIpFilter", []))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeScaleFactor")
    def reset_autovacuum_analyze_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeThreshold")
    def reset_autovacuum_analyze_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeThreshold", []))

    @jsii.member(jsii_name="resetAutovacuumFreezeMaxAge")
    def reset_autovacuum_freeze_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumFreezeMaxAge", []))

    @jsii.member(jsii_name="resetAutovacuumMaxWorkers")
    def reset_autovacuum_max_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumMaxWorkers", []))

    @jsii.member(jsii_name="resetAutovacuumNaptime")
    def reset_autovacuum_naptime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumNaptime", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostDelay")
    def reset_autovacuum_vacuum_cost_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostDelay", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostLimit")
    def reset_autovacuum_vacuum_cost_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostLimit", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumScaleFactor")
    def reset_autovacuum_vacuum_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumThreshold")
    def reset_autovacuum_vacuum_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumThreshold", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBgwriterDelay")
    def reset_bgwriter_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterDelay", []))

    @jsii.member(jsii_name="resetBgwriterFlushAfter")
    def reset_bgwriter_flush_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterFlushAfter", []))

    @jsii.member(jsii_name="resetBgwriterLruMaxpages")
    def reset_bgwriter_lru_maxpages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMaxpages", []))

    @jsii.member(jsii_name="resetBgwriterLruMultiplier")
    def reset_bgwriter_lru_multiplier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMultiplier", []))

    @jsii.member(jsii_name="resetDeadlockTimeout")
    def reset_deadlock_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadlockTimeout", []))

    @jsii.member(jsii_name="resetIdleInTransactionSessionTimeout")
    def reset_idle_in_transaction_session_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleInTransactionSessionTimeout", []))

    @jsii.member(jsii_name="resetIpFilter")
    def reset_ip_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpFilter", []))

    @jsii.member(jsii_name="resetJit")
    def reset_jit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJit", []))

    @jsii.member(jsii_name="resetLogAutovacuumMinDuration")
    def reset_log_autovacuum_min_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAutovacuumMinDuration", []))

    @jsii.member(jsii_name="resetLogErrorVerbosity")
    def reset_log_error_verbosity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogErrorVerbosity", []))

    @jsii.member(jsii_name="resetLogLinePrefix")
    def reset_log_line_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLinePrefix", []))

    @jsii.member(jsii_name="resetLogMinDurationStatement")
    def reset_log_min_duration_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMinDurationStatement", []))

    @jsii.member(jsii_name="resetMaxFilesPerProcess")
    def reset_max_files_per_process(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFilesPerProcess", []))

    @jsii.member(jsii_name="resetMaxLocksPerTransaction")
    def reset_max_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxLogicalReplicationWorkers")
    def reset_max_logical_replication_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLogicalReplicationWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkers")
    def reset_max_parallel_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkersPerGather")
    def reset_max_parallel_workers_per_gather(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkersPerGather", []))

    @jsii.member(jsii_name="resetMaxPredLocksPerTransaction")
    def reset_max_pred_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPredLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxPreparedTransactions")
    def reset_max_prepared_transactions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPreparedTransactions", []))

    @jsii.member(jsii_name="resetMaxReplicationSlots")
    def reset_max_replication_slots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxReplicationSlots", []))

    @jsii.member(jsii_name="resetMaxStackDepth")
    def reset_max_stack_depth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStackDepth", []))

    @jsii.member(jsii_name="resetMaxStandbyArchiveDelay")
    def reset_max_standby_archive_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyArchiveDelay", []))

    @jsii.member(jsii_name="resetMaxStandbyStreamingDelay")
    def reset_max_standby_streaming_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyStreamingDelay", []))

    @jsii.member(jsii_name="resetMaxWalSenders")
    def reset_max_wal_senders(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWalSenders", []))

    @jsii.member(jsii_name="resetMaxWorkerProcesses")
    def reset_max_worker_processes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWorkerProcesses", []))

    @jsii.member(jsii_name="resetMigration")
    def reset_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigration", []))

    @jsii.member(jsii_name="resetPgbouncer")
    def reset_pgbouncer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgbouncer", []))

    @jsii.member(jsii_name="resetPglookout")
    def reset_pglookout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPglookout", []))

    @jsii.member(jsii_name="resetPgPartmanBgwInterval")
    def reset_pg_partman_bgw_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwInterval", []))

    @jsii.member(jsii_name="resetPgPartmanBgwRole")
    def reset_pg_partman_bgw_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwRole", []))

    @jsii.member(jsii_name="resetPgReadReplica")
    def reset_pg_read_replica(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgReadReplica", []))

    @jsii.member(jsii_name="resetPgServiceToForkFrom")
    def reset_pg_service_to_fork_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgServiceToForkFrom", []))

    @jsii.member(jsii_name="resetPgStatStatementsTrack")
    def reset_pg_stat_statements_track(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatStatementsTrack", []))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @jsii.member(jsii_name="resetSharedBuffersPercentage")
    def reset_shared_buffers_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSharedBuffersPercentage", []))

    @jsii.member(jsii_name="resetSynchronousReplication")
    def reset_synchronous_replication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSynchronousReplication", []))

    @jsii.member(jsii_name="resetTempFileLimit")
    def reset_temp_file_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTempFileLimit", []))

    @jsii.member(jsii_name="resetTimescaledb")
    def reset_timescaledb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimescaledb", []))

    @jsii.member(jsii_name="resetTimezone")
    def reset_timezone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezone", []))

    @jsii.member(jsii_name="resetTrackActivityQuerySize")
    def reset_track_activity_query_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackActivityQuerySize", []))

    @jsii.member(jsii_name="resetTrackCommitTimestamp")
    def reset_track_commit_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackCommitTimestamp", []))

    @jsii.member(jsii_name="resetTrackFunctions")
    def reset_track_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackFunctions", []))

    @jsii.member(jsii_name="resetTrackIoTiming")
    def reset_track_io_timing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackIoTiming", []))

    @jsii.member(jsii_name="resetVariant")
    def reset_variant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVariant", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetWalSenderTimeout")
    def reset_wal_sender_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalSenderTimeout", []))

    @jsii.member(jsii_name="resetWalWriterDelay")
    def reset_wal_writer_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalWriterDelay", []))

    @jsii.member(jsii_name="resetWorkMem")
    def reset_work_mem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkMem", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migration")
    def migration(self) -> ManagedDatabasePostgresqlPropertiesMigrationOutputReference:
        return typing.cast(ManagedDatabasePostgresqlPropertiesMigrationOutputReference, jsii.get(self, "migration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgbouncer")
    def pgbouncer(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference", jsii.get(self, "pgbouncer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pglookout")
    def pglookout(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesPglookoutOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesPglookoutOutputReference", jsii.get(self, "pglookout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timescaledb")
    def timescaledb(
        self,
    ) -> "ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference":
        return typing.cast("ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference", jsii.get(self, "timescaledb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminPasswordInput")
    def admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUsernameInput")
    def admin_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilterInput")
    def automatic_utility_network_ip_filter_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "automaticUtilityNetworkIpFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactorInput")
    def autovacuum_analyze_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeScaleFactorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumAnalyzeThresholdInput")
    def autovacuum_analyze_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumFreezeMaxAgeInput")
    def autovacuum_freeze_max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumFreezeMaxAgeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumMaxWorkersInput")
    def autovacuum_max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumMaxWorkersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumNaptimeInput")
    def autovacuum_naptime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumNaptimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumCostDelayInput")
    def autovacuum_vacuum_cost_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumCostLimitInput")
    def autovacuum_vacuum_cost_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumScaleFactorInput")
    def autovacuum_vacuum_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumScaleFactorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumThresholdInput")
    def autovacuum_vacuum_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterDelayInput")
    def bgwriter_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterFlushAfterInput")
    def bgwriter_flush_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterFlushAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterLruMaxpagesInput")
    def bgwriter_lru_maxpages_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMaxpagesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterLruMultiplierInput")
    def bgwriter_lru_multiplier_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMultiplierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadlockTimeoutInput")
    def deadlock_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deadlockTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleInTransactionSessionTimeoutInput")
    def idle_in_transaction_session_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleInTransactionSessionTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipFilterInput")
    def ip_filter_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jitInput")
    def jit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "jitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logAutovacuumMinDurationInput")
    def log_autovacuum_min_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logAutovacuumMinDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logErrorVerbosityInput")
    def log_error_verbosity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logErrorVerbosityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logLinePrefixInput")
    def log_line_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLinePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logMinDurationStatementInput")
    def log_min_duration_statement_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logMinDurationStatementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFilesPerProcessInput")
    def max_files_per_process_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFilesPerProcessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLocksPerTransactionInput")
    def max_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLocksPerTransactionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLogicalReplicationWorkersInput")
    def max_logical_replication_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLogicalReplicationWorkersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxParallelWorkersInput")
    def max_parallel_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxParallelWorkersPerGatherInput")
    def max_parallel_workers_per_gather_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersPerGatherInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPredLocksPerTransactionInput")
    def max_pred_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPredLocksPerTransactionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPreparedTransactionsInput")
    def max_prepared_transactions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPreparedTransactionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxReplicationSlotsInput")
    def max_replication_slots_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicationSlotsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStackDepthInput")
    def max_stack_depth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStackDepthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStandbyArchiveDelayInput")
    def max_standby_archive_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyArchiveDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStandbyStreamingDelayInput")
    def max_standby_streaming_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyStreamingDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWalSendersInput")
    def max_wal_senders_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWalSendersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWorkerProcessesInput")
    def max_worker_processes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkerProcessesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migrationInput")
    def migration_input(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesMigration]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesMigration], jsii.get(self, "migrationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgbouncerInput")
    def pgbouncer_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPgbouncer"], jsii.get(self, "pgbouncerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pglookoutInput")
    def pglookout_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesPglookout"], jsii.get(self, "pglookoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgPartmanBgwIntervalInput")
    def pg_partman_bgw_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pgPartmanBgwIntervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgPartmanBgwRoleInput")
    def pg_partman_bgw_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgPartmanBgwRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgReadReplicaInput")
    def pg_read_replica_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "pgReadReplicaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgServiceToForkFromInput")
    def pg_service_to_fork_from_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgServiceToForkFromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgStatStatementsTrackInput")
    def pg_stat_statements_track_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgStatStatementsTrackInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publicAccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sharedBuffersPercentageInput")
    def shared_buffers_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sharedBuffersPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="synchronousReplicationInput")
    def synchronous_replication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "synchronousReplicationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tempFileLimitInput")
    def temp_file_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tempFileLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timescaledbInput")
    def timescaledb_input(
        self,
    ) -> typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"]:
        return typing.cast(typing.Optional["ManagedDatabasePostgresqlPropertiesTimescaledb"], jsii.get(self, "timescaledbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezoneInput")
    def timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackActivityQuerySizeInput")
    def track_activity_query_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "trackActivityQuerySizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackCommitTimestampInput")
    def track_commit_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackCommitTimestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackFunctionsInput")
    def track_functions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackFunctionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackIoTimingInput")
    def track_io_timing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackIoTimingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variantInput")
    def variant_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "variantInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="walSenderTimeoutInput")
    def wal_sender_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walSenderTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="walWriterDelayInput")
    def wal_writer_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walWriterDelayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workMemInput")
    def work_mem_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workMemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        jsii.set(self, "adminPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUsername")
    def admin_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminUsername"))

    @admin_username.setter
    def admin_username(self, value: builtins.str) -> None:
        jsii.set(self, "adminUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticUtilityNetworkIpFilter")
    def automatic_utility_network_ip_filter(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "automaticUtilityNetworkIpFilter"))

    @automatic_utility_network_ip_filter.setter
    def automatic_utility_network_ip_filter(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "automaticUtilityNetworkIpFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactor")
    def autovacuum_analyze_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeScaleFactor"))

    @autovacuum_analyze_scale_factor.setter
    def autovacuum_analyze_scale_factor(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumAnalyzeScaleFactor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumAnalyzeThreshold")
    def autovacuum_analyze_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeThreshold"))

    @autovacuum_analyze_threshold.setter
    def autovacuum_analyze_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumAnalyzeThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumFreezeMaxAge")
    def autovacuum_freeze_max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumFreezeMaxAge"))

    @autovacuum_freeze_max_age.setter
    def autovacuum_freeze_max_age(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumFreezeMaxAge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumMaxWorkers")
    def autovacuum_max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumMaxWorkers"))

    @autovacuum_max_workers.setter
    def autovacuum_max_workers(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumMaxWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumNaptime")
    def autovacuum_naptime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumNaptime"))

    @autovacuum_naptime.setter
    def autovacuum_naptime(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumNaptime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumCostDelay")
    def autovacuum_vacuum_cost_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostDelay"))

    @autovacuum_vacuum_cost_delay.setter
    def autovacuum_vacuum_cost_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumVacuumCostDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumCostLimit")
    def autovacuum_vacuum_cost_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostLimit"))

    @autovacuum_vacuum_cost_limit.setter
    def autovacuum_vacuum_cost_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumVacuumCostLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumScaleFactor")
    def autovacuum_vacuum_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumScaleFactor"))

    @autovacuum_vacuum_scale_factor.setter
    def autovacuum_vacuum_scale_factor(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumVacuumScaleFactor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autovacuumVacuumThreshold")
    def autovacuum_vacuum_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumThreshold"))

    @autovacuum_vacuum_threshold.setter
    def autovacuum_vacuum_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "autovacuumVacuumThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        jsii.set(self, "backupHour", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        jsii.set(self, "backupMinute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterDelay")
    def bgwriter_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterDelay"))

    @bgwriter_delay.setter
    def bgwriter_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "bgwriterDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterFlushAfter")
    def bgwriter_flush_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterFlushAfter"))

    @bgwriter_flush_after.setter
    def bgwriter_flush_after(self, value: jsii.Number) -> None:
        jsii.set(self, "bgwriterFlushAfter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterLruMaxpages")
    def bgwriter_lru_maxpages(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMaxpages"))

    @bgwriter_lru_maxpages.setter
    def bgwriter_lru_maxpages(self, value: jsii.Number) -> None:
        jsii.set(self, "bgwriterLruMaxpages", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bgwriterLruMultiplier")
    def bgwriter_lru_multiplier(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMultiplier"))

    @bgwriter_lru_multiplier.setter
    def bgwriter_lru_multiplier(self, value: jsii.Number) -> None:
        jsii.set(self, "bgwriterLruMultiplier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadlockTimeout")
    def deadlock_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deadlockTimeout"))

    @deadlock_timeout.setter
    def deadlock_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "deadlockTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleInTransactionSessionTimeout")
    def idle_in_transaction_session_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleInTransactionSessionTimeout"))

    @idle_in_transaction_session_timeout.setter
    def idle_in_transaction_session_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "idleInTransactionSessionTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipFilter")
    def ip_filter(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipFilter"))

    @ip_filter.setter
    def ip_filter(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jit")
    def jit(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "jit"))

    @jit.setter
    def jit(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "jit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logAutovacuumMinDuration")
    def log_autovacuum_min_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logAutovacuumMinDuration"))

    @log_autovacuum_min_duration.setter
    def log_autovacuum_min_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "logAutovacuumMinDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logErrorVerbosity")
    def log_error_verbosity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logErrorVerbosity"))

    @log_error_verbosity.setter
    def log_error_verbosity(self, value: builtins.str) -> None:
        jsii.set(self, "logErrorVerbosity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logLinePrefix")
    def log_line_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLinePrefix"))

    @log_line_prefix.setter
    def log_line_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "logLinePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logMinDurationStatement")
    def log_min_duration_statement(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logMinDurationStatement"))

    @log_min_duration_statement.setter
    def log_min_duration_statement(self, value: jsii.Number) -> None:
        jsii.set(self, "logMinDurationStatement", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFilesPerProcess")
    def max_files_per_process(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFilesPerProcess"))

    @max_files_per_process.setter
    def max_files_per_process(self, value: jsii.Number) -> None:
        jsii.set(self, "maxFilesPerProcess", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLocksPerTransaction")
    def max_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLocksPerTransaction"))

    @max_locks_per_transaction.setter
    def max_locks_per_transaction(self, value: jsii.Number) -> None:
        jsii.set(self, "maxLocksPerTransaction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxLogicalReplicationWorkers")
    def max_logical_replication_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLogicalReplicationWorkers"))

    @max_logical_replication_workers.setter
    def max_logical_replication_workers(self, value: jsii.Number) -> None:
        jsii.set(self, "maxLogicalReplicationWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxParallelWorkers")
    def max_parallel_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkers"))

    @max_parallel_workers.setter
    def max_parallel_workers(self, value: jsii.Number) -> None:
        jsii.set(self, "maxParallelWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxParallelWorkersPerGather")
    def max_parallel_workers_per_gather(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkersPerGather"))

    @max_parallel_workers_per_gather.setter
    def max_parallel_workers_per_gather(self, value: jsii.Number) -> None:
        jsii.set(self, "maxParallelWorkersPerGather", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPredLocksPerTransaction")
    def max_pred_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPredLocksPerTransaction"))

    @max_pred_locks_per_transaction.setter
    def max_pred_locks_per_transaction(self, value: jsii.Number) -> None:
        jsii.set(self, "maxPredLocksPerTransaction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPreparedTransactions")
    def max_prepared_transactions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPreparedTransactions"))

    @max_prepared_transactions.setter
    def max_prepared_transactions(self, value: jsii.Number) -> None:
        jsii.set(self, "maxPreparedTransactions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxReplicationSlots")
    def max_replication_slots(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicationSlots"))

    @max_replication_slots.setter
    def max_replication_slots(self, value: jsii.Number) -> None:
        jsii.set(self, "maxReplicationSlots", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStackDepth")
    def max_stack_depth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStackDepth"))

    @max_stack_depth.setter
    def max_stack_depth(self, value: jsii.Number) -> None:
        jsii.set(self, "maxStackDepth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStandbyArchiveDelay")
    def max_standby_archive_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyArchiveDelay"))

    @max_standby_archive_delay.setter
    def max_standby_archive_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "maxStandbyArchiveDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxStandbyStreamingDelay")
    def max_standby_streaming_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyStreamingDelay"))

    @max_standby_streaming_delay.setter
    def max_standby_streaming_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "maxStandbyStreamingDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWalSenders")
    def max_wal_senders(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWalSenders"))

    @max_wal_senders.setter
    def max_wal_senders(self, value: jsii.Number) -> None:
        jsii.set(self, "maxWalSenders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWorkerProcesses")
    def max_worker_processes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkerProcesses"))

    @max_worker_processes.setter
    def max_worker_processes(self, value: jsii.Number) -> None:
        jsii.set(self, "maxWorkerProcesses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgPartmanBgwInterval")
    def pg_partman_bgw_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pgPartmanBgwInterval"))

    @pg_partman_bgw_interval.setter
    def pg_partman_bgw_interval(self, value: jsii.Number) -> None:
        jsii.set(self, "pgPartmanBgwInterval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgPartmanBgwRole")
    def pg_partman_bgw_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgPartmanBgwRole"))

    @pg_partman_bgw_role.setter
    def pg_partman_bgw_role(self, value: builtins.str) -> None:
        jsii.set(self, "pgPartmanBgwRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgReadReplica")
    def pg_read_replica(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "pgReadReplica"))

    @pg_read_replica.setter
    def pg_read_replica(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "pgReadReplica", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgServiceToForkFrom")
    def pg_service_to_fork_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgServiceToForkFrom"))

    @pg_service_to_fork_from.setter
    def pg_service_to_fork_from(self, value: builtins.str) -> None:
        jsii.set(self, "pgServiceToForkFrom", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgStatStatementsTrack")
    def pg_stat_statements_track(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgStatStatementsTrack"))

    @pg_stat_statements_track.setter
    def pg_stat_statements_track(self, value: builtins.str) -> None:
        jsii.set(self, "pgStatStatementsTrack", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccess")
    def public_access(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publicAccess"))

    @public_access.setter
    def public_access(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publicAccess", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sharedBuffersPercentage")
    def shared_buffers_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sharedBuffersPercentage"))

    @shared_buffers_percentage.setter
    def shared_buffers_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "sharedBuffersPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="synchronousReplication")
    def synchronous_replication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "synchronousReplication"))

    @synchronous_replication.setter
    def synchronous_replication(self, value: builtins.str) -> None:
        jsii.set(self, "synchronousReplication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tempFileLimit")
    def temp_file_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tempFileLimit"))

    @temp_file_limit.setter
    def temp_file_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "tempFileLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: builtins.str) -> None:
        jsii.set(self, "timezone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackActivityQuerySize")
    def track_activity_query_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trackActivityQuerySize"))

    @track_activity_query_size.setter
    def track_activity_query_size(self, value: jsii.Number) -> None:
        jsii.set(self, "trackActivityQuerySize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackCommitTimestamp")
    def track_commit_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackCommitTimestamp"))

    @track_commit_timestamp.setter
    def track_commit_timestamp(self, value: builtins.str) -> None:
        jsii.set(self, "trackCommitTimestamp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackFunctions")
    def track_functions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackFunctions"))

    @track_functions.setter
    def track_functions(self, value: builtins.str) -> None:
        jsii.set(self, "trackFunctions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackIoTiming")
    def track_io_timing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackIoTiming"))

    @track_io_timing.setter
    def track_io_timing(self, value: builtins.str) -> None:
        jsii.set(self, "trackIoTiming", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variant")
    def variant(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "variant"))

    @variant.setter
    def variant(self, value: builtins.str) -> None:
        jsii.set(self, "variant", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="walSenderTimeout")
    def wal_sender_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walSenderTimeout"))

    @wal_sender_timeout.setter
    def wal_sender_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "walSenderTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="walWriterDelay")
    def wal_writer_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walWriterDelay"))

    @wal_writer_delay.setter
    def wal_writer_delay(self, value: jsii.Number) -> None:
        jsii.set(self, "walWriterDelay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workMem")
    def work_mem(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workMem"))

    @work_mem.setter
    def work_mem(self, value: jsii.Number) -> None:
        jsii.set(self, "workMem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedDatabasePostgresqlProperties]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesPgbouncer",
    jsii_struct_bases=[],
    name_mapping={
        "autodb_idle_timeout": "autodbIdleTimeout",
        "autodb_max_db_connections": "autodbMaxDbConnections",
        "autodb_pool_mode": "autodbPoolMode",
        "autodb_pool_size": "autodbPoolSize",
        "ignore_startup_parameters": "ignoreStartupParameters",
        "min_pool_size": "minPoolSize",
        "server_idle_timeout": "serverIdleTimeout",
        "server_lifetime": "serverLifetime",
        "server_reset_query_always": "serverResetQueryAlways",
    },
)
class ManagedDatabasePostgresqlPropertiesPgbouncer:
    def __init__(
        self,
        *,
        autodb_idle_timeout: typing.Optional[jsii.Number] = None,
        autodb_max_db_connections: typing.Optional[jsii.Number] = None,
        autodb_pool_mode: typing.Optional[builtins.str] = None,
        autodb_pool_size: typing.Optional[jsii.Number] = None,
        ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        min_pool_size: typing.Optional[jsii.Number] = None,
        server_idle_timeout: typing.Optional[jsii.Number] = None,
        server_lifetime: typing.Optional[jsii.Number] = None,
        server_reset_query_always: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param autodb_idle_timeout: If the automatically created database pools have been unused this many seconds, they are freed. If 0 then timeout is disabled. [seconds] Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        :param autodb_max_db_connections: Do not allow more than this many server connections per database (regardless of user). Setting it to 0 means unlimited. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        :param autodb_pool_mode: PGBouncer pool mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        :param autodb_pool_size: If non-zero then create automatically a pool of that size per user when a pool doesn't exist. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        :param ignore_startup_parameters: List of parameters to ignore when given in startup packet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        :param min_pool_size: Add more server connections to pool if below this number. Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        :param server_idle_timeout: If a server connection has been idle more than this many seconds it will be dropped. If 0 then timeout is disabled. [seconds] Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        :param server_lifetime: The pooler will close an unused server connection that has been connected longer than this. [seconds]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        :param server_reset_query_always: Run server_reset_query (DISCARD ALL) in all pooling modes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if autodb_idle_timeout is not None:
            self._values["autodb_idle_timeout"] = autodb_idle_timeout
        if autodb_max_db_connections is not None:
            self._values["autodb_max_db_connections"] = autodb_max_db_connections
        if autodb_pool_mode is not None:
            self._values["autodb_pool_mode"] = autodb_pool_mode
        if autodb_pool_size is not None:
            self._values["autodb_pool_size"] = autodb_pool_size
        if ignore_startup_parameters is not None:
            self._values["ignore_startup_parameters"] = ignore_startup_parameters
        if min_pool_size is not None:
            self._values["min_pool_size"] = min_pool_size
        if server_idle_timeout is not None:
            self._values["server_idle_timeout"] = server_idle_timeout
        if server_lifetime is not None:
            self._values["server_lifetime"] = server_lifetime
        if server_reset_query_always is not None:
            self._values["server_reset_query_always"] = server_reset_query_always

    @builtins.property
    def autodb_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''If the automatically created database pools have been unused this many seconds, they are freed.

        If 0 then timeout is disabled. [seconds]

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_idle_timeout ManagedDatabasePostgresql#autodb_idle_timeout}
        '''
        result = self._values.get("autodb_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_max_db_connections(self) -> typing.Optional[jsii.Number]:
        '''Do not allow more than this many server connections per database (regardless of user).

        Setting it to 0 means unlimited.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_max_db_connections ManagedDatabasePostgresql#autodb_max_db_connections}
        '''
        result = self._values.get("autodb_max_db_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_pool_mode(self) -> typing.Optional[builtins.str]:
        '''PGBouncer pool mode.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_mode ManagedDatabasePostgresql#autodb_pool_mode}
        '''
        result = self._values.get("autodb_pool_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def autodb_pool_size(self) -> typing.Optional[jsii.Number]:
        '''If non-zero then create automatically a pool of that size per user when a pool doesn't exist.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#autodb_pool_size ManagedDatabasePostgresql#autodb_pool_size}
        '''
        result = self._values.get("autodb_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignore_startup_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of parameters to ignore when given in startup packet.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#ignore_startup_parameters ManagedDatabasePostgresql#ignore_startup_parameters}
        '''
        result = self._values.get("ignore_startup_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def min_pool_size(self) -> typing.Optional[jsii.Number]:
        '''Add more server connections to pool if below this number.

        Improves behavior when usual load comes suddenly back after period of total inactivity. The value is effectively capped at the pool size.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#min_pool_size ManagedDatabasePostgresql#min_pool_size}
        '''
        result = self._values.get("min_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''If a server connection has been idle more than this many seconds it will be dropped.

        If 0 then timeout is disabled. [seconds]

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_idle_timeout ManagedDatabasePostgresql#server_idle_timeout}
        '''
        result = self._values.get("server_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_lifetime(self) -> typing.Optional[jsii.Number]:
        '''The pooler will close an unused server connection that has been connected longer than this. [seconds].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_lifetime ManagedDatabasePostgresql#server_lifetime}
        '''
        result = self._values.get("server_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_reset_query_always(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Run server_reset_query (DISCARD ALL) in all pooling modes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#server_reset_query_always ManagedDatabasePostgresql#server_reset_query_always}
        '''
        result = self._values.get("server_reset_query_always")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesPgbouncer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAutodbIdleTimeout")
    def reset_autodb_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbIdleTimeout", []))

    @jsii.member(jsii_name="resetAutodbMaxDbConnections")
    def reset_autodb_max_db_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbMaxDbConnections", []))

    @jsii.member(jsii_name="resetAutodbPoolMode")
    def reset_autodb_pool_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolMode", []))

    @jsii.member(jsii_name="resetAutodbPoolSize")
    def reset_autodb_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolSize", []))

    @jsii.member(jsii_name="resetIgnoreStartupParameters")
    def reset_ignore_startup_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreStartupParameters", []))

    @jsii.member(jsii_name="resetMinPoolSize")
    def reset_min_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinPoolSize", []))

    @jsii.member(jsii_name="resetServerIdleTimeout")
    def reset_server_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerIdleTimeout", []))

    @jsii.member(jsii_name="resetServerLifetime")
    def reset_server_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerLifetime", []))

    @jsii.member(jsii_name="resetServerResetQueryAlways")
    def reset_server_reset_query_always(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerResetQueryAlways", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbIdleTimeoutInput")
    def autodb_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbIdleTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbMaxDbConnectionsInput")
    def autodb_max_db_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbMaxDbConnectionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbPoolModeInput")
    def autodb_pool_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autodbPoolModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbPoolSizeInput")
    def autodb_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbPoolSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreStartupParametersInput")
    def ignore_startup_parameters_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ignoreStartupParametersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minPoolSizeInput")
    def min_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minPoolSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdleTimeoutInput")
    def server_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverIdleTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverLifetimeInput")
    def server_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverLifetimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverResetQueryAlwaysInput")
    def server_reset_query_always_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "serverResetQueryAlwaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbIdleTimeout")
    def autodb_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbIdleTimeout"))

    @autodb_idle_timeout.setter
    def autodb_idle_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "autodbIdleTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbMaxDbConnections")
    def autodb_max_db_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbMaxDbConnections"))

    @autodb_max_db_connections.setter
    def autodb_max_db_connections(self, value: jsii.Number) -> None:
        jsii.set(self, "autodbMaxDbConnections", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbPoolMode")
    def autodb_pool_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autodbPoolMode"))

    @autodb_pool_mode.setter
    def autodb_pool_mode(self, value: builtins.str) -> None:
        jsii.set(self, "autodbPoolMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autodbPoolSize")
    def autodb_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbPoolSize"))

    @autodb_pool_size.setter
    def autodb_pool_size(self, value: jsii.Number) -> None:
        jsii.set(self, "autodbPoolSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreStartupParameters")
    def ignore_startup_parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ignoreStartupParameters"))

    @ignore_startup_parameters.setter
    def ignore_startup_parameters(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ignoreStartupParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minPoolSize")
    def min_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minPoolSize"))

    @min_pool_size.setter
    def min_pool_size(self, value: jsii.Number) -> None:
        jsii.set(self, "minPoolSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverIdleTimeout")
    def server_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverIdleTimeout"))

    @server_idle_timeout.setter
    def server_idle_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "serverIdleTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverLifetime")
    def server_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverLifetime"))

    @server_lifetime.setter
    def server_lifetime(self, value: jsii.Number) -> None:
        jsii.set(self, "serverLifetime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverResetQueryAlways")
    def server_reset_query_always(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "serverResetQueryAlways"))

    @server_reset_query_always.setter
    def server_reset_query_always(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "serverResetQueryAlways", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesPgbouncer],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesPglookout",
    jsii_struct_bases=[],
    name_mapping={
        "max_failover_replication_time_lag": "maxFailoverReplicationTimeLag",
    },
)
class ManagedDatabasePostgresqlPropertiesPglookout:
    def __init__(
        self,
        *,
        max_failover_replication_time_lag: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_failover_replication_time_lag: max_failover_replication_time_lag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_failover_replication_time_lag is not None:
            self._values["max_failover_replication_time_lag"] = max_failover_replication_time_lag

    @builtins.property
    def max_failover_replication_time_lag(self) -> typing.Optional[jsii.Number]:
        '''max_failover_replication_time_lag.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_failover_replication_time_lag ManagedDatabasePostgresql#max_failover_replication_time_lag}
        '''
        result = self._values.get("max_failover_replication_time_lag")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesPglookout(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesPglookoutOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesPglookoutOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxFailoverReplicationTimeLag")
    def reset_max_failover_replication_time_lag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailoverReplicationTimeLag", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailoverReplicationTimeLagInput")
    def max_failover_replication_time_lag_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFailoverReplicationTimeLagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailoverReplicationTimeLag")
    def max_failover_replication_time_lag(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFailoverReplicationTimeLag"))

    @max_failover_replication_time_lag.setter
    def max_failover_replication_time_lag(self, value: jsii.Number) -> None:
        jsii.set(self, "maxFailoverReplicationTimeLag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesPglookout],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesTimescaledb",
    jsii_struct_bases=[],
    name_mapping={"max_background_workers": "maxBackgroundWorkers"},
)
class ManagedDatabasePostgresqlPropertiesTimescaledb:
    def __init__(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: timescaledb.max_background_workers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max_background_workers is not None:
            self._values["max_background_workers"] = max_background_workers

    @builtins.property
    def max_background_workers(self) -> typing.Optional[jsii.Number]:
        '''timescaledb.max_background_workers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_postgresql#max_background_workers ManagedDatabasePostgresql#max_background_workers}
        '''
        result = self._values.get("max_background_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabasePostgresqlPropertiesTimescaledb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxBackgroundWorkers")
    def reset_max_background_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBackgroundWorkers", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxBackgroundWorkersInput")
    def max_background_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBackgroundWorkersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxBackgroundWorkers")
    def max_background_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBackgroundWorkers"))

    @max_background_workers.setter
    def max_background_workers(self, value: jsii.Number) -> None:
        jsii.set(self, "maxBackgroundWorkers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb]:
        return typing.cast(typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedDatabasePostgresqlPropertiesTimescaledb],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ManagedDatabaseUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user upcloud_managed_database_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service: builtins.str,
        username: builtins.str,
        password: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user upcloud_managed_database_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param service: Service's UUID for which this user belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#service ManagedDatabaseUser#service}
        :param username: Name of the database user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#username ManagedDatabaseUser#username}
        :param password: Password for the database user. Defaults to a random value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#password ManagedDatabaseUser#password}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ManagedDatabaseUserConfig(
            service=service,
            username=username,
            password=password,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ManagedDatabaseUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "service": "service",
        "username": "username",
        "password": "password",
    },
)
class ManagedDatabaseUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        service: builtins.str,
        username: builtins.str,
        password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param service: Service's UUID for which this user belongs to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#service ManagedDatabaseUser#service}
        :param username: Name of the database user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#username ManagedDatabaseUser#username}
        :param password: Password for the database user. Defaults to a random value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#password ManagedDatabaseUser#password}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if password is not None:
            self._values["password"] = password

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def service(self) -> builtins.str:
        '''Service's UUID for which this user belongs to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#service ManagedDatabaseUser#service}
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Name of the database user.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#username ManagedDatabaseUser#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for the database user. Defaults to a random value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/managed_database_user#password ManagedDatabaseUser#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedDatabaseUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Network",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/network upcloud_network}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ip_network: "NetworkIpNetwork",
        name: builtins.str,
        zone: builtins.str,
        router: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/network upcloud_network} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ip_network: ip_network block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#ip_network Network#ip_network}
        :param name: A valid name for the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#name Network#name}
        :param zone: The zone the network is in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#zone Network#zone}
        :param router: The UUID of a router. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#router Network#router}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkConfig(
            ip_network=ip_network,
            name=name,
            zone=zone,
            router=router,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putIpNetwork")
    def put_ip_network(
        self,
        *,
        address: builtins.str,
        dhcp: typing.Union[builtins.bool, cdktf.IResolvable],
        family: builtins.str,
        dhcp_default_route: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        dhcp_dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        gateway: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The CIDR range of the subnet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#address Network#address}
        :param dhcp: Is DHCP enabled? Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp Network#dhcp}
        :param family: IP address family. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#family Network#family}
        :param dhcp_default_route: Is the gateway the DHCP default route? Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_default_route Network#dhcp_default_route}
        :param dhcp_dns: The DNS servers given by DHCP. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_dns Network#dhcp_dns}
        :param gateway: Gateway address given by DHCP. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#gateway Network#gateway}
        '''
        value = NetworkIpNetwork(
            address=address,
            dhcp=dhcp,
            family=family,
            dhcp_default_route=dhcp_default_route,
            dhcp_dns=dhcp_dns,
            gateway=gateway,
        )

        return typing.cast(None, jsii.invoke(self, "putIpNetwork", [value]))

    @jsii.member(jsii_name="resetRouter")
    def reset_router(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouter", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipNetwork")
    def ip_network(self) -> "NetworkIpNetworkOutputReference":
        return typing.cast("NetworkIpNetworkOutputReference", jsii.get(self, "ipNetwork"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipNetworkInput")
    def ip_network_input(self) -> typing.Optional["NetworkIpNetwork"]:
        return typing.cast(typing.Optional["NetworkIpNetwork"], jsii.get(self, "ipNetworkInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerInput")
    def router_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="router")
    def router(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "router"))

    @router.setter
    def router(self, value: builtins.str) -> None:
        jsii.set(self, "router", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.NetworkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ip_network": "ipNetwork",
        "name": "name",
        "zone": "zone",
        "router": "router",
    },
)
class NetworkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ip_network: "NetworkIpNetwork",
        name: builtins.str,
        zone: builtins.str,
        router: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ip_network: ip_network block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#ip_network Network#ip_network}
        :param name: A valid name for the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#name Network#name}
        :param zone: The zone the network is in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#zone Network#zone}
        :param router: The UUID of a router. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#router Network#router}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ip_network, dict):
            ip_network = NetworkIpNetwork(**ip_network)
        self._values: typing.Dict[str, typing.Any] = {
            "ip_network": ip_network,
            "name": name,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if router is not None:
            self._values["router"] = router

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def ip_network(self) -> "NetworkIpNetwork":
        '''ip_network block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#ip_network Network#ip_network}
        '''
        result = self._values.get("ip_network")
        assert result is not None, "Required property 'ip_network' is missing"
        return typing.cast("NetworkIpNetwork", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''A valid name for the network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#name Network#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''The zone the network is in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#zone Network#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def router(self) -> typing.Optional[builtins.str]:
        '''The UUID of a router.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#router Network#router}
        '''
        result = self._values.get("router")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.NetworkIpNetwork",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "dhcp": "dhcp",
        "family": "family",
        "dhcp_default_route": "dhcpDefaultRoute",
        "dhcp_dns": "dhcpDns",
        "gateway": "gateway",
    },
)
class NetworkIpNetwork:
    def __init__(
        self,
        *,
        address: builtins.str,
        dhcp: typing.Union[builtins.bool, cdktf.IResolvable],
        family: builtins.str,
        dhcp_default_route: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        dhcp_dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        gateway: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: The CIDR range of the subnet. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#address Network#address}
        :param dhcp: Is DHCP enabled? Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp Network#dhcp}
        :param family: IP address family. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#family Network#family}
        :param dhcp_default_route: Is the gateway the DHCP default route? Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_default_route Network#dhcp_default_route}
        :param dhcp_dns: The DNS servers given by DHCP. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_dns Network#dhcp_dns}
        :param gateway: Gateway address given by DHCP. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#gateway Network#gateway}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address": address,
            "dhcp": dhcp,
            "family": family,
        }
        if dhcp_default_route is not None:
            self._values["dhcp_default_route"] = dhcp_default_route
        if dhcp_dns is not None:
            self._values["dhcp_dns"] = dhcp_dns
        if gateway is not None:
            self._values["gateway"] = gateway

    @builtins.property
    def address(self) -> builtins.str:
        '''The CIDR range of the subnet.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#address Network#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Is DHCP enabled?

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp Network#dhcp}
        '''
        result = self._values.get("dhcp")
        assert result is not None, "Required property 'dhcp' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def family(self) -> builtins.str:
        '''IP address family.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#family Network#family}
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp_default_route(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Is the gateway the DHCP default route?

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_default_route Network#dhcp_default_route}
        '''
        result = self._values.get("dhcp_default_route")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def dhcp_dns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The DNS servers given by DHCP.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#dhcp_dns Network#dhcp_dns}
        '''
        result = self._values.get("dhcp_dns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gateway(self) -> typing.Optional[builtins.str]:
        '''Gateway address given by DHCP.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/network#gateway Network#gateway}
        '''
        result = self._values.get("gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkIpNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkIpNetworkOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.NetworkIpNetworkOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDhcpDefaultRoute")
    def reset_dhcp_default_route(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpDefaultRoute", []))

    @jsii.member(jsii_name="resetDhcpDns")
    def reset_dhcp_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcpDns", []))

    @jsii.member(jsii_name="resetGateway")
    def reset_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGateway", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDefaultRouteInput")
    def dhcp_default_route_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "dhcpDefaultRouteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDnsInput")
    def dhcp_dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dhcpDnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayInput")
    def gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        jsii.set(self, "address", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "dhcp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDefaultRoute")
    def dhcp_default_route(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "dhcpDefaultRoute"))

    @dhcp_default_route.setter
    def dhcp_default_route(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "dhcpDefaultRoute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dhcpDns")
    def dhcp_dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dhcpDns"))

    @dhcp_dns.setter
    def dhcp_dns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dhcpDns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @gateway.setter
    def gateway(self, value: builtins.str) -> None:
        jsii.set(self, "gateway", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[NetworkIpNetwork]:
        return typing.cast(typing.Optional[NetworkIpNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[NetworkIpNetwork]) -> None:
        jsii.set(self, "internalValue", value)


class ObjectStorage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ObjectStorage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage upcloud_object_storage}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_key: builtins.str,
        name: builtins.str,
        secret_key: builtins.str,
        size: jsii.Number,
        zone: builtins.str,
        bucket: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ObjectStorageBucket"]]] = None,
        description: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage upcloud_object_storage} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_key: The access key used to identify user. Can be set to an empty string, which will tell the provider to get the access key from environment variable. The environment variable should be "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_{name}". {name} is the name given to object storage instance (so not the resource label), it should be all uppercased and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would use environment variable named "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_MY_FILES". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#access_key ObjectStorage#access_key}
        :param name: The name of the object storage instance to be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#name ObjectStorage#name}
        :param secret_key: The secret key used to authenticate user. Can be set to an empty string, which will tell the provider to get the secret key from environment variable. The environment variable should be "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_{name}". {name} is the name given to object storage instance (so not the resource label), it should be all uppercased and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would use environment variable named "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_MY_FILES". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#secret_key ObjectStorage#secret_key}
        :param size: The size of the object storage instance in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#size ObjectStorage#size}
        :param zone: The zone in which the object storage instance will be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#zone ObjectStorage#zone}
        :param bucket: bucket block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#bucket ObjectStorage#bucket}
        :param description: The description of the object storage instance to be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#description ObjectStorage#description}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ObjectStorageConfig(
            access_key=access_key,
            name=name,
            secret_key=secret_key,
            size=size,
            zone=zone,
            bucket=bucket,
            description=description,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usedSpace")
    def used_space(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "usedSpace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessKeyInput")
    def access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ObjectStorageBucket"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ObjectStorageBucket"]]], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKey"))

    @access_key.setter
    def access_key(self, value: builtins.str) -> None:
        jsii.set(self, "accessKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["ObjectStorageBucket"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["ObjectStorageBucket"]], jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["ObjectStorageBucket"]],
    ) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        jsii.set(self, "secretKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        jsii.set(self, "size", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ObjectStorageBucket",
    jsii_struct_bases=[],
    name_mapping={"name": "name"},
)
class ObjectStorageBucket:
    def __init__(self, *, name: builtins.str) -> None:
        '''
        :param name: The name of the bucket. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#name ObjectStorage#name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the bucket.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#name ObjectStorage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObjectStorageBucket(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ObjectStorageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_key": "accessKey",
        "name": "name",
        "secret_key": "secretKey",
        "size": "size",
        "zone": "zone",
        "bucket": "bucket",
        "description": "description",
    },
)
class ObjectStorageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_key: builtins.str,
        name: builtins.str,
        secret_key: builtins.str,
        size: jsii.Number,
        zone: builtins.str,
        bucket: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[ObjectStorageBucket]]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_key: The access key used to identify user. Can be set to an empty string, which will tell the provider to get the access key from environment variable. The environment variable should be "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_{name}". {name} is the name given to object storage instance (so not the resource label), it should be all uppercased and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would use environment variable named "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_MY_FILES". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#access_key ObjectStorage#access_key}
        :param name: The name of the object storage instance to be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#name ObjectStorage#name}
        :param secret_key: The secret key used to authenticate user. Can be set to an empty string, which will tell the provider to get the secret key from environment variable. The environment variable should be "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_{name}". {name} is the name given to object storage instance (so not the resource label), it should be all uppercased and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would use environment variable named "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_MY_FILES". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#secret_key ObjectStorage#secret_key}
        :param size: The size of the object storage instance in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#size ObjectStorage#size}
        :param zone: The zone in which the object storage instance will be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#zone ObjectStorage#zone}
        :param bucket: bucket block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#bucket ObjectStorage#bucket}
        :param description: The description of the object storage instance to be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#description ObjectStorage#description}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "access_key": access_key,
            "name": name,
            "secret_key": secret_key,
            "size": size,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if bucket is not None:
            self._values["bucket"] = bucket
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def access_key(self) -> builtins.str:
        '''The access key used to identify user.

        Can be set to an empty string, which will tell the provider to get the access key from environment variable.
        The environment variable should be "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_{name}".
        {name} is the name given to object storage instance (so not the resource label), it should be all uppercased
        and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would
        use environment variable named "UPCLOUD_OBJECT_STORAGE_ACCESS_KEY_MY_FILES".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#access_key ObjectStorage#access_key}
        '''
        result = self._values.get("access_key")
        assert result is not None, "Required property 'access_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the object storage instance to be created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#name ObjectStorage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_key(self) -> builtins.str:
        '''The secret key used to authenticate user.

        Can be set to an empty string, which will tell the provider to get the secret key from environment variable.
        The environment variable should be "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_{name}".
        {name} is the name given to object storage instance (so not the resource label), it should be all uppercased
        and all dashes (-) should be replaced with underscores (_). For example, object storage named "my-files" would
        use environment variable named "UPCLOUD_OBJECT_STORAGE_SECRET_KEY_MY_FILES".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#secret_key ObjectStorage#secret_key}
        '''
        result = self._values.get("secret_key")
        assert result is not None, "Required property 'secret_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''The size of the object storage instance in gigabytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#size ObjectStorage#size}
        '''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''The zone in which the object storage instance will be created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#zone ObjectStorage#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ObjectStorageBucket]]]:
        '''bucket block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#bucket ObjectStorage#bucket}
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ObjectStorageBucket]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the object storage instance to be created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/object_storage#description ObjectStorage#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObjectStorageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Router(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Router",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/router upcloud_router}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/router upcloud_router} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the router. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/router#name Router#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RouterConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachedNetworks")
    def attached_networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attachedNetworks"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.RouterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class RouterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the router. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/router#name Router#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the router.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/router#name Router#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RouterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Server(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Server",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/server upcloud_server}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hostname: builtins.str,
        network_interface: typing.Union[cdktf.IResolvable, typing.Sequence["ServerNetworkInterface"]],
        zone: builtins.str,
        cpu: typing.Optional[jsii.Number] = None,
        firewall: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        host: typing.Optional[jsii.Number] = None,
        login: typing.Optional["ServerLogin"] = None,
        mem: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        plan: typing.Optional[builtins.str] = None,
        simple_backup: typing.Optional["ServerSimpleBackup"] = None,
        storage_devices: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ServerStorageDevices"]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        template: typing.Optional["ServerTemplate"] = None,
        title: typing.Optional[builtins.str] = None,
        user_data: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/server upcloud_server} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param hostname: A valid domain name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#hostname Server#hostname}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#network_interface Server#network_interface}
        :param zone: The zone in which the server will be hosted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#zone Server#zone}
        :param cpu: The number of CPU for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#cpu Server#cpu}
        :param firewall: Are firewall rules active for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#firewall Server#firewall}
        :param host: Use this to start the VM on a specific host. Refers to value from host -attribute. Only available for private cloud hosts Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#host Server#host}
        :param login: login block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#login Server#login}
        :param mem: The size of memory for the server (in megabytes). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#mem Server#mem}
        :param metadata: Is the metadata service active for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#metadata Server#metadata}
        :param plan: The pricing plan used for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        :param simple_backup: simple_backup block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#simple_backup Server#simple_backup}
        :param storage_devices: storage_devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage_devices Server#storage_devices}
        :param tags: The server related tags. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#tags Server#tags}
        :param template: template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#template Server#template}
        :param title: A short, informational description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        :param user_data: Defines URL for a server setup script, or the script body itself. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user_data Server#user_data}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServerConfig(
            hostname=hostname,
            network_interface=network_interface,
            zone=zone,
            cpu=cpu,
            firewall=firewall,
            host=host,
            login=login,
            mem=mem,
            metadata=metadata,
            plan=plan,
            simple_backup=simple_backup,
            storage_devices=storage_devices,
            tags=tags,
            template=template,
            title=title,
            user_data=user_data,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLogin")
    def put_login(
        self,
        *,
        create_password: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        password_delivery: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_password: Indicates a password should be create to allow access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#create_password Server#create_password}
        :param keys: A list of ssh keys to access the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#keys Server#keys}
        :param password_delivery: The delivery method for the server’s root password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#password_delivery Server#password_delivery}
        :param user: Username to be create to access the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user Server#user}
        '''
        value = ServerLogin(
            create_password=create_password,
            keys=keys,
            password_delivery=password_delivery,
            user=user,
        )

        return typing.cast(None, jsii.invoke(self, "putLogin", [value]))

    @jsii.member(jsii_name="putSimpleBackup")
    def put_simple_backup(self, *, plan: builtins.str, time: builtins.str) -> None:
        '''
        :param plan: Simple backup plan. Accepted values: dailies, weeklies, monthlies. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        :param time: Time of the day at which backup will be taken. Should be provided in a hhmm format (e.g. 2230). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        value = ServerSimpleBackup(plan=plan, time=time)

        return typing.cast(None, jsii.invoke(self, "putSimpleBackup", [value]))

    @jsii.member(jsii_name="putTemplate")
    def put_template(
        self,
        *,
        storage: builtins.str,
        address: typing.Optional[builtins.str] = None,
        backup_rule: typing.Optional["ServerTemplateBackupRule"] = None,
        delete_autoresize_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filesystem_autoresize: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        size: typing.Optional[jsii.Number] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage: A valid storage UUID or template name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage Server#storage}
        :param address: The device address the storage will be attached to. Specify only the bus name (ide/scsi/virtio) to auto-select next available address from that bus. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#address Server#address}
        :param backup_rule: backup_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#backup_rule Server#backup_rule}
        :param delete_autoresize_backup: If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#delete_autoresize_backup Server#delete_autoresize_backup}
        :param filesystem_autoresize: If set to true, provider will attempt to resize partition and filesystem when the size of template storage changes. Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true). Taking and keeping backups incure costs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#filesystem_autoresize Server#filesystem_autoresize}
        :param size: The size of the storage in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#size Server#size}
        :param title: A short, informative description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        '''
        value = ServerTemplate(
            storage=storage,
            address=address,
            backup_rule=backup_rule,
            delete_autoresize_backup=delete_autoresize_backup,
            filesystem_autoresize=filesystem_autoresize,
            size=size,
            title=title,
        )

        return typing.cast(None, jsii.invoke(self, "putTemplate", [value]))

    @jsii.member(jsii_name="resetCpu")
    def reset_cpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpu", []))

    @jsii.member(jsii_name="resetFirewall")
    def reset_firewall(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewall", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetLogin")
    def reset_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogin", []))

    @jsii.member(jsii_name="resetMem")
    def reset_mem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMem", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetPlan")
    def reset_plan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlan", []))

    @jsii.member(jsii_name="resetSimpleBackup")
    def reset_simple_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSimpleBackup", []))

    @jsii.member(jsii_name="resetStorageDevices")
    def reset_storage_devices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageDevices", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTemplate")
    def reset_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplate", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="login")
    def login(self) -> "ServerLoginOutputReference":
        return typing.cast("ServerLoginOutputReference", jsii.get(self, "login"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="simpleBackup")
    def simple_backup(self) -> "ServerSimpleBackupOutputReference":
        return typing.cast("ServerSimpleBackupOutputReference", jsii.get(self, "simpleBackup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="template")
    def template(self) -> "ServerTemplateOutputReference":
        return typing.cast("ServerTemplateOutputReference", jsii.get(self, "template"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuInput")
    def cpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallInput")
    def firewall_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "firewallInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loginInput")
    def login_input(self) -> typing.Optional["ServerLogin"]:
        return typing.cast(typing.Optional["ServerLogin"], jsii.get(self, "loginInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memInput")
    def mem_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "metadataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="simpleBackupInput")
    def simple_backup_input(self) -> typing.Optional["ServerSimpleBackup"]:
        return typing.cast(typing.Optional["ServerSimpleBackup"], jsii.get(self, "simpleBackupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageDevicesInput")
    def storage_devices_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]]], jsii.get(self, "storageDevicesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateInput")
    def template_input(self) -> typing.Optional["ServerTemplate"]:
        return typing.cast(typing.Optional["ServerTemplate"], jsii.get(self, "templateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpu")
    def cpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpu"))

    @cpu.setter
    def cpu(self, value: jsii.Number) -> None:
        jsii.set(self, "cpu", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewall")
    def firewall(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "firewall"))

    @firewall.setter
    def firewall(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "firewall", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "host"))

    @host.setter
    def host(self, value: jsii.Number) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        jsii.set(self, "hostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mem")
    def mem(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mem"))

    @mem.setter
    def mem(self, value: jsii.Number) -> None:
        jsii.set(self, "mem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "metadata", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterface")
    def network_interface(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]], jsii.get(self, "networkInterface"))

    @network_interface.setter
    def network_interface(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]],
    ) -> None:
        jsii.set(self, "networkInterface", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        jsii.set(self, "plan", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageDevices")
    def storage_devices(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]], jsii.get(self, "storageDevices"))

    @storage_devices.setter
    def storage_devices(
        self,
        value: typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]],
    ) -> None:
        jsii.set(self, "storageDevices", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        jsii.set(self, "userData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "hostname": "hostname",
        "network_interface": "networkInterface",
        "zone": "zone",
        "cpu": "cpu",
        "firewall": "firewall",
        "host": "host",
        "login": "login",
        "mem": "mem",
        "metadata": "metadata",
        "plan": "plan",
        "simple_backup": "simpleBackup",
        "storage_devices": "storageDevices",
        "tags": "tags",
        "template": "template",
        "title": "title",
        "user_data": "userData",
    },
)
class ServerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        hostname: builtins.str,
        network_interface: typing.Union[cdktf.IResolvable, typing.Sequence["ServerNetworkInterface"]],
        zone: builtins.str,
        cpu: typing.Optional[jsii.Number] = None,
        firewall: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        host: typing.Optional[jsii.Number] = None,
        login: typing.Optional["ServerLogin"] = None,
        mem: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        plan: typing.Optional[builtins.str] = None,
        simple_backup: typing.Optional["ServerSimpleBackup"] = None,
        storage_devices: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ServerStorageDevices"]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        template: typing.Optional["ServerTemplate"] = None,
        title: typing.Optional[builtins.str] = None,
        user_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param hostname: A valid domain name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#hostname Server#hostname}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#network_interface Server#network_interface}
        :param zone: The zone in which the server will be hosted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#zone Server#zone}
        :param cpu: The number of CPU for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#cpu Server#cpu}
        :param firewall: Are firewall rules active for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#firewall Server#firewall}
        :param host: Use this to start the VM on a specific host. Refers to value from host -attribute. Only available for private cloud hosts Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#host Server#host}
        :param login: login block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#login Server#login}
        :param mem: The size of memory for the server (in megabytes). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#mem Server#mem}
        :param metadata: Is the metadata service active for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#metadata Server#metadata}
        :param plan: The pricing plan used for the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        :param simple_backup: simple_backup block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#simple_backup Server#simple_backup}
        :param storage_devices: storage_devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage_devices Server#storage_devices}
        :param tags: The server related tags. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#tags Server#tags}
        :param template: template block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#template Server#template}
        :param title: A short, informational description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        :param user_data: Defines URL for a server setup script, or the script body itself. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user_data Server#user_data}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(login, dict):
            login = ServerLogin(**login)
        if isinstance(simple_backup, dict):
            simple_backup = ServerSimpleBackup(**simple_backup)
        if isinstance(template, dict):
            template = ServerTemplate(**template)
        self._values: typing.Dict[str, typing.Any] = {
            "hostname": hostname,
            "network_interface": network_interface,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if cpu is not None:
            self._values["cpu"] = cpu
        if firewall is not None:
            self._values["firewall"] = firewall
        if host is not None:
            self._values["host"] = host
        if login is not None:
            self._values["login"] = login
        if mem is not None:
            self._values["mem"] = mem
        if metadata is not None:
            self._values["metadata"] = metadata
        if plan is not None:
            self._values["plan"] = plan
        if simple_backup is not None:
            self._values["simple_backup"] = simple_backup
        if storage_devices is not None:
            self._values["storage_devices"] = storage_devices
        if tags is not None:
            self._values["tags"] = tags
        if template is not None:
            self._values["template"] = template
        if title is not None:
            self._values["title"] = title
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''A valid domain name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#hostname Server#hostname}
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#network_interface Server#network_interface}
        '''
        result = self._values.get("network_interface")
        assert result is not None, "Required property 'network_interface' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["ServerNetworkInterface"]], result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''The zone in which the server will be hosted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#zone Server#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''The number of CPU for the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#cpu Server#cpu}
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def firewall(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Are firewall rules active for the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#firewall Server#firewall}
        '''
        result = self._values.get("firewall")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def host(self) -> typing.Optional[jsii.Number]:
        '''Use this to start the VM on a specific host.

        Refers to value from host -attribute. Only available for private cloud hosts

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#host Server#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def login(self) -> typing.Optional["ServerLogin"]:
        '''login block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#login Server#login}
        '''
        result = self._values.get("login")
        return typing.cast(typing.Optional["ServerLogin"], result)

    @builtins.property
    def mem(self) -> typing.Optional[jsii.Number]:
        '''The size of memory for the server (in megabytes).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#mem Server#mem}
        '''
        result = self._values.get("mem")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Is the metadata service active for the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#metadata Server#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def plan(self) -> typing.Optional[builtins.str]:
        '''The pricing plan used for the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        '''
        result = self._values.get("plan")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def simple_backup(self) -> typing.Optional["ServerSimpleBackup"]:
        '''simple_backup block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#simple_backup Server#simple_backup}
        '''
        result = self._values.get("simple_backup")
        return typing.cast(typing.Optional["ServerSimpleBackup"], result)

    @builtins.property
    def storage_devices(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]]]:
        '''storage_devices block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage_devices Server#storage_devices}
        '''
        result = self._values.get("storage_devices")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ServerStorageDevices"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The server related tags.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#tags Server#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def template(self) -> typing.Optional["ServerTemplate"]:
        '''template block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#template Server#template}
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional["ServerTemplate"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''A short, informational description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Defines URL for a server setup script, or the script body itself.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user_data Server#user_data}
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerLogin",
    jsii_struct_bases=[],
    name_mapping={
        "create_password": "createPassword",
        "keys": "keys",
        "password_delivery": "passwordDelivery",
        "user": "user",
    },
)
class ServerLogin:
    def __init__(
        self,
        *,
        create_password: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        password_delivery: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_password: Indicates a password should be create to allow access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#create_password Server#create_password}
        :param keys: A list of ssh keys to access the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#keys Server#keys}
        :param password_delivery: The delivery method for the server’s root password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#password_delivery Server#password_delivery}
        :param user: Username to be create to access the server. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user Server#user}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create_password is not None:
            self._values["create_password"] = create_password
        if keys is not None:
            self._values["keys"] = keys
        if password_delivery is not None:
            self._values["password_delivery"] = password_delivery
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def create_password(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Indicates a password should be create to allow access.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#create_password Server#create_password}
        '''
        result = self._values.get("create_password")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of ssh keys to access the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#keys Server#keys}
        '''
        result = self._values.get("keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def password_delivery(self) -> typing.Optional[builtins.str]:
        '''The delivery method for the server’s root password.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#password_delivery Server#password_delivery}
        '''
        result = self._values.get("password_delivery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''Username to be create to access the server.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#user Server#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerLoginOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ServerLoginOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreatePassword")
    def reset_create_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatePassword", []))

    @jsii.member(jsii_name="resetKeys")
    def reset_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeys", []))

    @jsii.member(jsii_name="resetPasswordDelivery")
    def reset_password_delivery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordDelivery", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createPasswordInput")
    def create_password_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "createPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keysInput")
    def keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "keysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordDeliveryInput")
    def password_delivery_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordDeliveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createPassword")
    def create_password(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "createPassword"))

    @create_password.setter
    def create_password(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "createPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keys")
    def keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keys"))

    @keys.setter
    def keys(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "keys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordDelivery")
    def password_delivery(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordDelivery"))

    @password_delivery.setter
    def password_delivery(self, value: builtins.str) -> None:
        jsii.set(self, "passwordDelivery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServerLogin]:
        return typing.cast(typing.Optional[ServerLogin], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServerLogin]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "bootable": "bootable",
        "ip_address": "ipAddress",
        "ip_address_family": "ipAddressFamily",
        "network": "network",
        "source_ip_filtering": "sourceIpFiltering",
    },
)
class ServerNetworkInterface:
    def __init__(
        self,
        *,
        type: builtins.str,
        bootable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ip_address: typing.Optional[builtins.str] = None,
        ip_address_family: typing.Optional[builtins.str] = None,
        network: typing.Optional[builtins.str] = None,
        source_ip_filtering: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param type: Network interface type. For private network interfaces, a network must be specified with an existing network id. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#type Server#type}
        :param bootable: ``true`` if this interface should be used for network booting. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#bootable Server#bootable}
        :param ip_address: The assigned IP address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#ip_address Server#ip_address}
        :param ip_address_family: The IP address type of this interface (one of ``IPv4`` or ``IPv6``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#ip_address_family Server#ip_address_family}
        :param network: The unique ID of a network to attach this network to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#network Server#network}
        :param source_ip_filtering: ``true`` if source IP should be filtered. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#source_ip_filtering Server#source_ip_filtering}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if bootable is not None:
            self._values["bootable"] = bootable
        if ip_address is not None:
            self._values["ip_address"] = ip_address
        if ip_address_family is not None:
            self._values["ip_address_family"] = ip_address_family
        if network is not None:
            self._values["network"] = network
        if source_ip_filtering is not None:
            self._values["source_ip_filtering"] = source_ip_filtering

    @builtins.property
    def type(self) -> builtins.str:
        '''Network interface type. For private network interfaces, a network must be specified with an existing network id.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#type Server#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bootable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''``true`` if this interface should be used for network booting.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#bootable Server#bootable}
        '''
        result = self._values.get("bootable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ip_address(self) -> typing.Optional[builtins.str]:
        '''The assigned IP address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#ip_address Server#ip_address}
        '''
        result = self._values.get("ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_address_family(self) -> typing.Optional[builtins.str]:
        '''The IP address type of this interface (one of ``IPv4`` or ``IPv6``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#ip_address_family Server#ip_address_family}
        '''
        result = self._values.get("ip_address_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(self) -> typing.Optional[builtins.str]:
        '''The unique ID of a network to attach this network to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#network Server#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_ip_filtering(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''``true`` if source IP should be filtered.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#source_ip_filtering Server#source_ip_filtering}
        '''
        result = self._values.get("source_ip_filtering")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerSimpleBackup",
    jsii_struct_bases=[],
    name_mapping={"plan": "plan", "time": "time"},
)
class ServerSimpleBackup:
    def __init__(self, *, plan: builtins.str, time: builtins.str) -> None:
        '''
        :param plan: Simple backup plan. Accepted values: dailies, weeklies, monthlies. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        :param time: Time of the day at which backup will be taken. Should be provided in a hhmm format (e.g. 2230). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "plan": plan,
            "time": time,
        }

    @builtins.property
    def plan(self) -> builtins.str:
        '''Simple backup plan. Accepted values: dailies, weeklies, monthlies.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#plan Server#plan}
        '''
        result = self._values.get("plan")
        assert result is not None, "Required property 'plan' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time(self) -> builtins.str:
        '''Time of the day at which backup will be taken. Should be provided in a hhmm format (e.g. 2230).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerSimpleBackup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerSimpleBackupOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ServerSimpleBackupOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="planInput")
    def plan_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "planInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeInput")
    def time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plan")
    def plan(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plan"))

    @plan.setter
    def plan(self, value: builtins.str) -> None:
        jsii.set(self, "plan", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="time")
    def time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "time"))

    @time.setter
    def time(self, value: builtins.str) -> None:
        jsii.set(self, "time", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServerSimpleBackup]:
        return typing.cast(typing.Optional[ServerSimpleBackup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServerSimpleBackup]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerStorageDevices",
    jsii_struct_bases=[],
    name_mapping={"storage": "storage", "address": "address", "type": "type"},
)
class ServerStorageDevices:
    def __init__(
        self,
        *,
        storage: builtins.str,
        address: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage: A valid storage UUID. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage Server#storage}
        :param address: The device address the storage will be attached to. Specify only the bus name (ide/scsi/virtio) to auto-select next available address from that bus. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#address Server#address}
        :param type: The device type the storage will be attached as. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#type Server#type}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "storage": storage,
        }
        if address is not None:
            self._values["address"] = address
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def storage(self) -> builtins.str:
        '''A valid storage UUID.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage Server#storage}
        '''
        result = self._values.get("storage")
        assert result is not None, "Required property 'storage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The device address the storage will be attached to.

        Specify only the bus name (ide/scsi/virtio) to auto-select next available address from that bus.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#address Server#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The device type the storage will be attached as.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#type Server#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerStorageDevices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "storage": "storage",
        "address": "address",
        "backup_rule": "backupRule",
        "delete_autoresize_backup": "deleteAutoresizeBackup",
        "filesystem_autoresize": "filesystemAutoresize",
        "size": "size",
        "title": "title",
    },
)
class ServerTemplate:
    def __init__(
        self,
        *,
        storage: builtins.str,
        address: typing.Optional[builtins.str] = None,
        backup_rule: typing.Optional["ServerTemplateBackupRule"] = None,
        delete_autoresize_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filesystem_autoresize: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        size: typing.Optional[jsii.Number] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage: A valid storage UUID or template name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage Server#storage}
        :param address: The device address the storage will be attached to. Specify only the bus name (ide/scsi/virtio) to auto-select next available address from that bus. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#address Server#address}
        :param backup_rule: backup_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#backup_rule Server#backup_rule}
        :param delete_autoresize_backup: If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#delete_autoresize_backup Server#delete_autoresize_backup}
        :param filesystem_autoresize: If set to true, provider will attempt to resize partition and filesystem when the size of template storage changes. Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true). Taking and keeping backups incure costs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#filesystem_autoresize Server#filesystem_autoresize}
        :param size: The size of the storage in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#size Server#size}
        :param title: A short, informative description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        '''
        if isinstance(backup_rule, dict):
            backup_rule = ServerTemplateBackupRule(**backup_rule)
        self._values: typing.Dict[str, typing.Any] = {
            "storage": storage,
        }
        if address is not None:
            self._values["address"] = address
        if backup_rule is not None:
            self._values["backup_rule"] = backup_rule
        if delete_autoresize_backup is not None:
            self._values["delete_autoresize_backup"] = delete_autoresize_backup
        if filesystem_autoresize is not None:
            self._values["filesystem_autoresize"] = filesystem_autoresize
        if size is not None:
            self._values["size"] = size
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def storage(self) -> builtins.str:
        '''A valid storage UUID or template name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#storage Server#storage}
        '''
        result = self._values.get("storage")
        assert result is not None, "Required property 'storage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''The device address the storage will be attached to.

        Specify only the bus name (ide/scsi/virtio) to auto-select next available address from that bus.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#address Server#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backup_rule(self) -> typing.Optional["ServerTemplateBackupRule"]:
        '''backup_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#backup_rule Server#backup_rule}
        '''
        result = self._values.get("backup_rule")
        return typing.cast(typing.Optional["ServerTemplateBackupRule"], result)

    @builtins.property
    def delete_autoresize_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#delete_autoresize_backup Server#delete_autoresize_backup}
        '''
        result = self._values.get("delete_autoresize_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def filesystem_autoresize(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If set to true, provider will attempt to resize partition and filesystem when the size of template storage changes.

        Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used
        to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true).
        Taking and keeping backups incure costs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#filesystem_autoresize Server#filesystem_autoresize}
        '''
        result = self._values.get("filesystem_autoresize")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def size(self) -> typing.Optional[jsii.Number]:
        '''The size of the storage in gigabytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#size Server#size}
        '''
        result = self._values.get("size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''A short, informative description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#title Server#title}
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.ServerTemplateBackupRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "retention": "retention", "time": "time"},
)
class ServerTemplateBackupRule:
    def __init__(
        self,
        *,
        interval: builtins.str,
        retention: jsii.Number,
        time: builtins.str,
    ) -> None:
        '''
        :param interval: The weekday when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#interval Server#interval}
        :param retention: The number of days before a backup is automatically deleted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#retention Server#retention}
        :param time: The time of day when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "retention": retention,
            "time": time,
        }

    @builtins.property
    def interval(self) -> builtins.str:
        '''The weekday when the backup is created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#interval Server#interval}
        '''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention(self) -> jsii.Number:
        '''The number of days before a backup is automatically deleted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#retention Server#retention}
        '''
        result = self._values.get("retention")
        assert result is not None, "Required property 'retention' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time(self) -> builtins.str:
        '''The time of day when the backup is created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerTemplateBackupRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerTemplateBackupRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ServerTemplateBackupRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionInput")
    def retention_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeInput")
    def time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retention")
    def retention(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retention"))

    @retention.setter
    def retention(self, value: jsii.Number) -> None:
        jsii.set(self, "retention", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="time")
    def time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "time"))

    @time.setter
    def time(self, value: builtins.str) -> None:
        jsii.set(self, "time", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServerTemplateBackupRule]:
        return typing.cast(typing.Optional[ServerTemplateBackupRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServerTemplateBackupRule]) -> None:
        jsii.set(self, "internalValue", value)


class ServerTemplateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.ServerTemplateOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBackupRule")
    def put_backup_rule(
        self,
        *,
        interval: builtins.str,
        retention: jsii.Number,
        time: builtins.str,
    ) -> None:
        '''
        :param interval: The weekday when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#interval Server#interval}
        :param retention: The number of days before a backup is automatically deleted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#retention Server#retention}
        :param time: The time of day when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/server#time Server#time}
        '''
        value = ServerTemplateBackupRule(
            interval=interval, retention=retention, time=time
        )

        return typing.cast(None, jsii.invoke(self, "putBackupRule", [value]))

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetBackupRule")
    def reset_backup_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupRule", []))

    @jsii.member(jsii_name="resetDeleteAutoresizeBackup")
    def reset_delete_autoresize_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAutoresizeBackup", []))

    @jsii.member(jsii_name="resetFilesystemAutoresize")
    def reset_filesystem_autoresize(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilesystemAutoresize", []))

    @jsii.member(jsii_name="resetSize")
    def reset_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSize", []))

    @jsii.member(jsii_name="resetTitle")
    def reset_title(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTitle", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRule")
    def backup_rule(self) -> ServerTemplateBackupRuleOutputReference:
        return typing.cast(ServerTemplateBackupRuleOutputReference, jsii.get(self, "backupRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tier")
    def tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRuleInput")
    def backup_rule_input(self) -> typing.Optional[ServerTemplateBackupRule]:
        return typing.cast(typing.Optional[ServerTemplateBackupRule], jsii.get(self, "backupRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutoresizeBackupInput")
    def delete_autoresize_backup_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteAutoresizeBackupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filesystemAutoresizeInput")
    def filesystem_autoresize_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "filesystemAutoresizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageInput")
    def storage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        jsii.set(self, "address", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutoresizeBackup")
    def delete_autoresize_backup(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteAutoresizeBackup"))

    @delete_autoresize_backup.setter
    def delete_autoresize_backup(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deleteAutoresizeBackup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filesystemAutoresize")
    def filesystem_autoresize(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "filesystemAutoresize"))

    @filesystem_autoresize.setter
    def filesystem_autoresize(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "filesystemAutoresize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        jsii.set(self, "size", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storage")
    def storage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storage"))

    @storage.setter
    def storage(self, value: builtins.str) -> None:
        jsii.set(self, "storage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServerTemplate]:
        return typing.cast(typing.Optional[ServerTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServerTemplate]) -> None:
        jsii.set(self, "internalValue", value)


class Storage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Storage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/storage upcloud_storage}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        size: jsii.Number,
        title: builtins.str,
        zone: builtins.str,
        backup_rule: typing.Optional["StorageBackupRule"] = None,
        clone: typing.Optional["StorageClone"] = None,
        delete_autoresize_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filesystem_autoresize: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        import_: typing.Optional["StorageImport"] = None,
        tier: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/storage upcloud_storage} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param size: The size of the storage in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#size Storage#size}
        :param title: A short, informative description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#title Storage#title}
        :param zone: The zone in which the storage will be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#zone Storage#zone}
        :param backup_rule: backup_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#backup_rule Storage#backup_rule}
        :param clone: clone block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#clone Storage#clone}
        :param delete_autoresize_backup: If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#delete_autoresize_backup Storage#delete_autoresize_backup}
        :param filesystem_autoresize: If set to true, provider will attempt to resize partition and filesystem when the size of the storage changes. Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true). Taking and keeping backups incure costs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#filesystem_autoresize Storage#filesystem_autoresize}
        :param import_: import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#import Storage#import}
        :param tier: The storage tier to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#tier Storage#tier}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StorageConfig(
            size=size,
            title=title,
            zone=zone,
            backup_rule=backup_rule,
            clone=clone,
            delete_autoresize_backup=delete_autoresize_backup,
            filesystem_autoresize=filesystem_autoresize,
            import_=import_,
            tier=tier,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putBackupRule")
    def put_backup_rule(
        self,
        *,
        interval: builtins.str,
        retention: jsii.Number,
        time: builtins.str,
    ) -> None:
        '''
        :param interval: The weekday when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#interval Storage#interval}
        :param retention: The number of days before a backup is automatically deleted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#retention Storage#retention}
        :param time: The time of day when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#time Storage#time}
        '''
        value = StorageBackupRule(interval=interval, retention=retention, time=time)

        return typing.cast(None, jsii.invoke(self, "putBackupRule", [value]))

    @jsii.member(jsii_name="putClone")
    def put_clone(self, *, id: builtins.str) -> None:
        '''
        :param id: The unique identifier of the storage/template to clone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#id Storage#id}
        '''
        value = StorageClone(id=id)

        return typing.cast(None, jsii.invoke(self, "putClone", [value]))

    @jsii.member(jsii_name="putImport")
    def put_import(
        self,
        *,
        source: builtins.str,
        source_location: builtins.str,
        source_hash: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source: The mode of the import task. One of ``http_import`` or ``direct_upload``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source Storage#source}
        :param source_location: The location of the file to import. For ``http_import`` an accessible URL for ``direct_upload`` a local file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_location Storage#source_location}
        :param source_hash: For ``direct_upload``; an optional hash of the file to upload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_hash Storage#source_hash}
        '''
        value = StorageImport(
            source=source, source_location=source_location, source_hash=source_hash
        )

        return typing.cast(None, jsii.invoke(self, "putImport", [value]))

    @jsii.member(jsii_name="resetBackupRule")
    def reset_backup_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupRule", []))

    @jsii.member(jsii_name="resetClone")
    def reset_clone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClone", []))

    @jsii.member(jsii_name="resetDeleteAutoresizeBackup")
    def reset_delete_autoresize_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAutoresizeBackup", []))

    @jsii.member(jsii_name="resetFilesystemAutoresize")
    def reset_filesystem_autoresize(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilesystemAutoresize", []))

    @jsii.member(jsii_name="resetImport")
    def reset_import(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImport", []))

    @jsii.member(jsii_name="resetTier")
    def reset_tier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTier", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRule")
    def backup_rule(self) -> "StorageBackupRuleOutputReference":
        return typing.cast("StorageBackupRuleOutputReference", jsii.get(self, "backupRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clone")
    def clone(self) -> "StorageCloneOutputReference":
        return typing.cast("StorageCloneOutputReference", jsii.get(self, "clone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="import")
    def import_(self) -> "StorageImportOutputReference":
        return typing.cast("StorageImportOutputReference", jsii.get(self, "import"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRuleInput")
    def backup_rule_input(self) -> typing.Optional["StorageBackupRule"]:
        return typing.cast(typing.Optional["StorageBackupRule"], jsii.get(self, "backupRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloneInput")
    def clone_input(self) -> typing.Optional["StorageClone"]:
        return typing.cast(typing.Optional["StorageClone"], jsii.get(self, "cloneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutoresizeBackupInput")
    def delete_autoresize_backup_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteAutoresizeBackupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filesystemAutoresizeInput")
    def filesystem_autoresize_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "filesystemAutoresizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importInput")
    def import_input(self) -> typing.Optional["StorageImport"]:
        return typing.cast(typing.Optional["StorageImport"], jsii.get(self, "importInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tierInput")
    def tier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutoresizeBackup")
    def delete_autoresize_backup(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteAutoresizeBackup"))

    @delete_autoresize_backup.setter
    def delete_autoresize_backup(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deleteAutoresizeBackup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filesystemAutoresize")
    def filesystem_autoresize(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "filesystemAutoresize"))

    @filesystem_autoresize.setter
    def filesystem_autoresize(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "filesystemAutoresize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        jsii.set(self, "size", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tier")
    def tier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tier"))

    @tier.setter
    def tier(self, value: builtins.str) -> None:
        jsii.set(self, "tier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        jsii.set(self, "zone", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.StorageBackupRule",
    jsii_struct_bases=[],
    name_mapping={"interval": "interval", "retention": "retention", "time": "time"},
)
class StorageBackupRule:
    def __init__(
        self,
        *,
        interval: builtins.str,
        retention: jsii.Number,
        time: builtins.str,
    ) -> None:
        '''
        :param interval: The weekday when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#interval Storage#interval}
        :param retention: The number of days before a backup is automatically deleted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#retention Storage#retention}
        :param time: The time of day when the backup is created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#time Storage#time}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "interval": interval,
            "retention": retention,
            "time": time,
        }

    @builtins.property
    def interval(self) -> builtins.str:
        '''The weekday when the backup is created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#interval Storage#interval}
        '''
        result = self._values.get("interval")
        assert result is not None, "Required property 'interval' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention(self) -> jsii.Number:
        '''The number of days before a backup is automatically deleted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#retention Storage#retention}
        '''
        result = self._values.get("retention")
        assert result is not None, "Required property 'retention' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def time(self) -> builtins.str:
        '''The time of day when the backup is created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#time Storage#time}
        '''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageBackupRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageBackupRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.StorageBackupRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionInput")
    def retention_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeInput")
    def time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retention")
    def retention(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retention"))

    @retention.setter
    def retention(self, value: jsii.Number) -> None:
        jsii.set(self, "retention", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="time")
    def time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "time"))

    @time.setter
    def time(self, value: builtins.str) -> None:
        jsii.set(self, "time", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageBackupRule]:
        return typing.cast(typing.Optional[StorageBackupRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StorageBackupRule]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.StorageClone",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class StorageClone:
    def __init__(self, *, id: builtins.str) -> None:
        '''
        :param id: The unique identifier of the storage/template to clone. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#id Storage#id}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''The unique identifier of the storage/template to clone.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#id Storage#id}
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageClone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageCloneOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.StorageCloneOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageClone]:
        return typing.cast(typing.Optional[StorageClone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StorageClone]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.StorageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "size": "size",
        "title": "title",
        "zone": "zone",
        "backup_rule": "backupRule",
        "clone": "clone",
        "delete_autoresize_backup": "deleteAutoresizeBackup",
        "filesystem_autoresize": "filesystemAutoresize",
        "import_": "import",
        "tier": "tier",
    },
)
class StorageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        size: jsii.Number,
        title: builtins.str,
        zone: builtins.str,
        backup_rule: typing.Optional[StorageBackupRule] = None,
        clone: typing.Optional[StorageClone] = None,
        delete_autoresize_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filesystem_autoresize: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        import_: typing.Optional["StorageImport"] = None,
        tier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param size: The size of the storage in gigabytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#size Storage#size}
        :param title: A short, informative description. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#title Storage#title}
        :param zone: The zone in which the storage will be created. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#zone Storage#zone}
        :param backup_rule: backup_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#backup_rule Storage#backup_rule}
        :param clone: clone block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#clone Storage#clone}
        :param delete_autoresize_backup: If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#delete_autoresize_backup Storage#delete_autoresize_backup}
        :param filesystem_autoresize: If set to true, provider will attempt to resize partition and filesystem when the size of the storage changes. Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true). Taking and keeping backups incure costs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#filesystem_autoresize Storage#filesystem_autoresize}
        :param import_: import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#import Storage#import}
        :param tier: The storage tier to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#tier Storage#tier}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(backup_rule, dict):
            backup_rule = StorageBackupRule(**backup_rule)
        if isinstance(clone, dict):
            clone = StorageClone(**clone)
        if isinstance(import_, dict):
            import_ = StorageImport(**import_)
        self._values: typing.Dict[str, typing.Any] = {
            "size": size,
            "title": title,
            "zone": zone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if backup_rule is not None:
            self._values["backup_rule"] = backup_rule
        if clone is not None:
            self._values["clone"] = clone
        if delete_autoresize_backup is not None:
            self._values["delete_autoresize_backup"] = delete_autoresize_backup
        if filesystem_autoresize is not None:
            self._values["filesystem_autoresize"] = filesystem_autoresize
        if import_ is not None:
            self._values["import_"] = import_
        if tier is not None:
            self._values["tier"] = tier

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''The size of the storage in gigabytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#size Storage#size}
        '''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''A short, informative description.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#title Storage#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> builtins.str:
        '''The zone in which the storage will be created.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#zone Storage#zone}
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backup_rule(self) -> typing.Optional[StorageBackupRule]:
        '''backup_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#backup_rule Storage#backup_rule}
        '''
        result = self._values.get("backup_rule")
        return typing.cast(typing.Optional[StorageBackupRule], result)

    @builtins.property
    def clone(self) -> typing.Optional[StorageClone]:
        '''clone block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#clone Storage#clone}
        '''
        result = self._values.get("clone")
        return typing.cast(typing.Optional[StorageClone], result)

    @builtins.property
    def delete_autoresize_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If set to true, the backup taken before the partition and filesystem resize attempt will be deleted immediately after success.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#delete_autoresize_backup Storage#delete_autoresize_backup}
        '''
        result = self._values.get("delete_autoresize_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def filesystem_autoresize(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If set to true, provider will attempt to resize partition and filesystem when the size of the storage changes.

        Please note that before the resize attempt is made, backup of the storage will be taken. If the resize attempt fails, the backup will be used
        to restore the storage and then deleted. If the resize attempt succeeds, backup will be kept (unless delete_autoresize_backup option is set to true).
        Taking and keeping backups incure costs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#filesystem_autoresize Storage#filesystem_autoresize}
        '''
        result = self._values.get("filesystem_autoresize")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def import_(self) -> typing.Optional["StorageImport"]:
        '''import block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#import Storage#import}
        '''
        result = self._values.get("import_")
        return typing.cast(typing.Optional["StorageImport"], result)

    @builtins.property
    def tier(self) -> typing.Optional[builtins.str]:
        '''The storage tier to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#tier Storage#tier}
        '''
        result = self._values.get("tier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.StorageImport",
    jsii_struct_bases=[],
    name_mapping={
        "source": "source",
        "source_location": "sourceLocation",
        "source_hash": "sourceHash",
    },
)
class StorageImport:
    def __init__(
        self,
        *,
        source: builtins.str,
        source_location: builtins.str,
        source_hash: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source: The mode of the import task. One of ``http_import`` or ``direct_upload``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source Storage#source}
        :param source_location: The location of the file to import. For ``http_import`` an accessible URL for ``direct_upload`` a local file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_location Storage#source_location}
        :param source_hash: For ``direct_upload``; an optional hash of the file to upload. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_hash Storage#source_hash}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
            "source_location": source_location,
        }
        if source_hash is not None:
            self._values["source_hash"] = source_hash

    @builtins.property
    def source(self) -> builtins.str:
        '''The mode of the import task. One of ``http_import`` or ``direct_upload``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source Storage#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_location(self) -> builtins.str:
        '''The location of the file to import. For ``http_import`` an accessible URL for ``direct_upload`` a local file.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_location Storage#source_location}
        '''
        result = self._values.get("source_location")
        assert result is not None, "Required property 'source_location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_hash(self) -> typing.Optional[builtins.str]:
        '''For ``direct_upload``; an optional hash of the file to upload.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/storage#source_hash Storage#source_hash}
        '''
        result = self._values.get("source_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageImport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StorageImportOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.StorageImportOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSourceHash")
    def reset_source_hash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceHash", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha256Sum")
    def sha256_sum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256Sum"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writtenBytes")
    def written_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "writtenBytes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHashInput")
    def source_hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceHashInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceLocationInput")
    def source_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceHash"))

    @source_hash.setter
    def source_hash(self, value: builtins.str) -> None:
        jsii.set(self, "sourceHash", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceLocation")
    def source_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceLocation"))

    @source_location.setter
    def source_location(self, value: builtins.str) -> None:
        jsii.set(self, "sourceLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StorageImport]:
        return typing.cast(typing.Optional[StorageImport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StorageImport]) -> None:
        jsii.set(self, "internalValue", value)


class Tag(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.Tag",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud/r/tag upcloud_tag}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud/r/tag upcloud_tag} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The value representing the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#name Tag#name}
        :param description: Free form text representing the meaning of the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#description Tag#description}
        :param servers: A collection of servers that have been assigned the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#servers Tag#servers}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TagConfig(
            name=name,
            description=description,
            servers=servers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetServers")
    def reset_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serversInput")
    def servers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serversInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="servers")
    def servers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "servers"))

    @servers.setter
    def servers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "servers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.TagConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "servers": "servers",
    },
)
class TagConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        servers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The value representing the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#name Tag#name}
        :param description: Free form text representing the meaning of the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#description Tag#description}
        :param servers: A collection of servers that have been assigned the tag. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#servers Tag#servers}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if servers is not None:
            self._values["servers"] = servers

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The value representing the tag.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#name Tag#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Free form text representing the meaning of the tag.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#description Tag#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def servers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A collection of servers that have been assigned the tag.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud/r/tag#servers Tag#servers}
        '''
        result = self._values.get("servers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UpcloudProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-upcloud.UpcloudProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/upcloud upcloud}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        password: builtins.str,
        username: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        retry_max: typing.Optional[jsii.Number] = None,
        retry_wait_max_sec: typing.Optional[jsii.Number] = None,
        retry_wait_min_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/upcloud upcloud} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param password: Password for UpCloud API user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#password UpcloudProvider#password}
        :param username: UpCloud username with API access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#username UpcloudProvider#username}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#alias UpcloudProvider#alias}
        :param retry_max: Maximum number of retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_max UpcloudProvider#retry_max}
        :param retry_wait_max_sec: Maximum time to wait between retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        :param retry_wait_min_sec: Minimum time to wait between retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        '''
        config = UpcloudProviderConfig(
            password=password,
            username=username,
            alias=alias,
            retry_max=retry_max,
            retry_wait_max_sec=retry_wait_max_sec,
            retry_wait_min_sec=retry_wait_min_sec,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetRetryMax")
    def reset_retry_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryMax", []))

    @jsii.member(jsii_name="resetRetryWaitMaxSec")
    def reset_retry_wait_max_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryWaitMaxSec", []))

    @jsii.member(jsii_name="resetRetryWaitMinSec")
    def reset_retry_wait_min_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetryWaitMinSec", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryMaxInput")
    def retry_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryMaxInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryWaitMaxSecInput")
    def retry_wait_max_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMaxSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryWaitMinSecInput")
    def retry_wait_min_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMinSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryMax")
    def retry_max(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryMax"))

    @retry_max.setter
    def retry_max(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "retryMax", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryWaitMaxSec")
    def retry_wait_max_sec(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMaxSec"))

    @retry_wait_max_sec.setter
    def retry_wait_max_sec(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "retryWaitMaxSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retryWaitMinSec")
    def retry_wait_min_sec(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retryWaitMinSec"))

    @retry_wait_min_sec.setter
    def retry_wait_min_sec(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "retryWaitMinSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-upcloud.UpcloudProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "password": "password",
        "username": "username",
        "alias": "alias",
        "retry_max": "retryMax",
        "retry_wait_max_sec": "retryWaitMaxSec",
        "retry_wait_min_sec": "retryWaitMinSec",
    },
)
class UpcloudProviderConfig:
    def __init__(
        self,
        *,
        password: builtins.str,
        username: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        retry_max: typing.Optional[jsii.Number] = None,
        retry_wait_max_sec: typing.Optional[jsii.Number] = None,
        retry_wait_min_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param password: Password for UpCloud API user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#password UpcloudProvider#password}
        :param username: UpCloud username with API access. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#username UpcloudProvider#username}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#alias UpcloudProvider#alias}
        :param retry_max: Maximum number of retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_max UpcloudProvider#retry_max}
        :param retry_wait_max_sec: Maximum time to wait between retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        :param retry_wait_min_sec: Minimum time to wait between retries. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "password": password,
            "username": username,
        }
        if alias is not None:
            self._values["alias"] = alias
        if retry_max is not None:
            self._values["retry_max"] = retry_max
        if retry_wait_max_sec is not None:
            self._values["retry_wait_max_sec"] = retry_wait_max_sec
        if retry_wait_min_sec is not None:
            self._values["retry_wait_min_sec"] = retry_wait_min_sec

    @builtins.property
    def password(self) -> builtins.str:
        '''Password for UpCloud API user.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#password UpcloudProvider#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''UpCloud username with API access.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#username UpcloudProvider#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#alias UpcloudProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retry_max(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of retries.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_max UpcloudProvider#retry_max}
        '''
        result = self._values.get("retry_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_wait_max_sec(self) -> typing.Optional[jsii.Number]:
        '''Maximum time to wait between retries.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_max_sec UpcloudProvider#retry_wait_max_sec}
        '''
        result = self._values.get("retry_wait_max_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retry_wait_min_sec(self) -> typing.Optional[jsii.Number]:
        '''Minimum time to wait between retries.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/upcloud#retry_wait_min_sec UpcloudProvider#retry_wait_min_sec}
        '''
        result = self._values.get("retry_wait_min_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UpcloudProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataUpcloudHosts",
    "DataUpcloudHostsConfig",
    "DataUpcloudHostsHosts",
    "DataUpcloudHostsHostsList",
    "DataUpcloudHostsHostsOutputReference",
    "DataUpcloudIpAddresses",
    "DataUpcloudIpAddressesAddresses",
    "DataUpcloudIpAddressesAddressesList",
    "DataUpcloudIpAddressesAddressesOutputReference",
    "DataUpcloudIpAddressesConfig",
    "DataUpcloudNetworks",
    "DataUpcloudNetworksConfig",
    "DataUpcloudNetworksNetworks",
    "DataUpcloudNetworksNetworksIpNetwork",
    "DataUpcloudNetworksNetworksIpNetworkList",
    "DataUpcloudNetworksNetworksIpNetworkOutputReference",
    "DataUpcloudNetworksNetworksList",
    "DataUpcloudNetworksNetworksOutputReference",
    "DataUpcloudNetworksNetworksServers",
    "DataUpcloudNetworksNetworksServersList",
    "DataUpcloudNetworksNetworksServersOutputReference",
    "DataUpcloudStorage",
    "DataUpcloudStorageConfig",
    "DataUpcloudTags",
    "DataUpcloudTagsConfig",
    "DataUpcloudTagsTags",
    "DataUpcloudTagsTagsList",
    "DataUpcloudTagsTagsOutputReference",
    "DataUpcloudZone",
    "DataUpcloudZoneConfig",
    "DataUpcloudZones",
    "DataUpcloudZonesConfig",
    "FirewallRules",
    "FirewallRulesConfig",
    "FirewallRulesFirewallRule",
    "FloatingIpAddress",
    "FloatingIpAddressConfig",
    "Loadbalancer",
    "LoadbalancerBackend",
    "LoadbalancerBackendConfig",
    "LoadbalancerConfig",
    "LoadbalancerDynamicBackendMember",
    "LoadbalancerDynamicBackendMemberConfig",
    "LoadbalancerDynamicCertificateBundle",
    "LoadbalancerDynamicCertificateBundleConfig",
    "LoadbalancerFrontend",
    "LoadbalancerFrontendConfig",
    "LoadbalancerFrontendRule",
    "LoadbalancerFrontendRuleActions",
    "LoadbalancerFrontendRuleActionsHttpRedirect",
    "LoadbalancerFrontendRuleActionsHttpReturn",
    "LoadbalancerFrontendRuleActionsOutputReference",
    "LoadbalancerFrontendRuleActionsTcpReject",
    "LoadbalancerFrontendRuleActionsUseBackend",
    "LoadbalancerFrontendRuleConfig",
    "LoadbalancerFrontendRuleMatchers",
    "LoadbalancerFrontendRuleMatchersBodySize",
    "LoadbalancerFrontendRuleMatchersBodySizeRange",
    "LoadbalancerFrontendRuleMatchersCookie",
    "LoadbalancerFrontendRuleMatchersHeader",
    "LoadbalancerFrontendRuleMatchersHost",
    "LoadbalancerFrontendRuleMatchersHttpMethod",
    "LoadbalancerFrontendRuleMatchersNumMembersUp",
    "LoadbalancerFrontendRuleMatchersOutputReference",
    "LoadbalancerFrontendRuleMatchersPath",
    "LoadbalancerFrontendRuleMatchersSrcIp",
    "LoadbalancerFrontendRuleMatchersSrcPort",
    "LoadbalancerFrontendRuleMatchersSrcPortRange",
    "LoadbalancerFrontendRuleMatchersUrl",
    "LoadbalancerFrontendRuleMatchersUrlParam",
    "LoadbalancerFrontendRuleMatchersUrlQuery",
    "LoadbalancerFrontendTlsConfig",
    "LoadbalancerFrontendTlsConfigConfig",
    "LoadbalancerManualCertificateBundle",
    "LoadbalancerManualCertificateBundleConfig",
    "LoadbalancerResolver",
    "LoadbalancerResolverConfig",
    "LoadbalancerStaticBackendMember",
    "LoadbalancerStaticBackendMemberConfig",
    "ManagedDatabaseLogicalDatabase",
    "ManagedDatabaseLogicalDatabaseConfig",
    "ManagedDatabaseMysql",
    "ManagedDatabaseMysqlComponents",
    "ManagedDatabaseMysqlComponentsList",
    "ManagedDatabaseMysqlComponentsOutputReference",
    "ManagedDatabaseMysqlConfig",
    "ManagedDatabaseMysqlNodeStates",
    "ManagedDatabaseMysqlNodeStatesList",
    "ManagedDatabaseMysqlNodeStatesOutputReference",
    "ManagedDatabaseMysqlProperties",
    "ManagedDatabaseMysqlPropertiesMigration",
    "ManagedDatabaseMysqlPropertiesMigrationOutputReference",
    "ManagedDatabaseMysqlPropertiesOutputReference",
    "ManagedDatabasePostgresql",
    "ManagedDatabasePostgresqlComponents",
    "ManagedDatabasePostgresqlComponentsList",
    "ManagedDatabasePostgresqlComponentsOutputReference",
    "ManagedDatabasePostgresqlConfig",
    "ManagedDatabasePostgresqlNodeStates",
    "ManagedDatabasePostgresqlNodeStatesList",
    "ManagedDatabasePostgresqlNodeStatesOutputReference",
    "ManagedDatabasePostgresqlProperties",
    "ManagedDatabasePostgresqlPropertiesMigration",
    "ManagedDatabasePostgresqlPropertiesMigrationOutputReference",
    "ManagedDatabasePostgresqlPropertiesOutputReference",
    "ManagedDatabasePostgresqlPropertiesPgbouncer",
    "ManagedDatabasePostgresqlPropertiesPgbouncerOutputReference",
    "ManagedDatabasePostgresqlPropertiesPglookout",
    "ManagedDatabasePostgresqlPropertiesPglookoutOutputReference",
    "ManagedDatabasePostgresqlPropertiesTimescaledb",
    "ManagedDatabasePostgresqlPropertiesTimescaledbOutputReference",
    "ManagedDatabaseUser",
    "ManagedDatabaseUserConfig",
    "Network",
    "NetworkConfig",
    "NetworkIpNetwork",
    "NetworkIpNetworkOutputReference",
    "ObjectStorage",
    "ObjectStorageBucket",
    "ObjectStorageConfig",
    "Router",
    "RouterConfig",
    "Server",
    "ServerConfig",
    "ServerLogin",
    "ServerLoginOutputReference",
    "ServerNetworkInterface",
    "ServerSimpleBackup",
    "ServerSimpleBackupOutputReference",
    "ServerStorageDevices",
    "ServerTemplate",
    "ServerTemplateBackupRule",
    "ServerTemplateBackupRuleOutputReference",
    "ServerTemplateOutputReference",
    "Storage",
    "StorageBackupRule",
    "StorageBackupRuleOutputReference",
    "StorageClone",
    "StorageCloneOutputReference",
    "StorageConfig",
    "StorageImport",
    "StorageImportOutputReference",
    "Tag",
    "TagConfig",
    "UpcloudProvider",
    "UpcloudProviderConfig",
]

publication.publish()
