import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class DataAwsImagebuilderComponent(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component aws_imagebuilder_component}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component aws_imagebuilder_component} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#arn DataAwsImagebuilderComponent#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#id DataAwsImagebuilderComponent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#tags DataAwsImagebuilderComponent#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderComponentConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeDescription")
    def change_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "changeDescription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedOsVersions")
    def supported_os_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedOsVersions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderComponentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#arn DataAwsImagebuilderComponent#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#id DataAwsImagebuilderComponent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#tags DataAwsImagebuilderComponent#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#arn DataAwsImagebuilderComponent#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#id DataAwsImagebuilderComponent#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_component#tags DataAwsImagebuilderComponent#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderComponentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderComponents(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponents",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components aws_imagebuilder_components}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderComponentsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components aws_imagebuilder_components} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#filter DataAwsImagebuilderComponents#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#id DataAwsImagebuilderComponents#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#owner DataAwsImagebuilderComponents#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderComponentsConfig(
            filter=filter,
            id=id,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderComponentsFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderComponentsFilterList":
        return typing.cast("DataAwsImagebuilderComponentsFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderComponentsFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderComponentsFilter"]]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponentsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
        "owner": "owner",
    },
)
class DataAwsImagebuilderComponentsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderComponentsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#filter DataAwsImagebuilderComponents#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#id DataAwsImagebuilderComponents#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#owner DataAwsImagebuilderComponents#owner}.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if owner is not None:
            self._values["owner"] = owner

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderComponentsFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#filter DataAwsImagebuilderComponents#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderComponentsFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#id DataAwsImagebuilderComponents#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#owner DataAwsImagebuilderComponents#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderComponentsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponentsFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderComponentsFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#name DataAwsImagebuilderComponents#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#values DataAwsImagebuilderComponents#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#name DataAwsImagebuilderComponents#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_components#values DataAwsImagebuilderComponents#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderComponentsFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderComponentsFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponentsFilterList",
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
    ) -> "DataAwsImagebuilderComponentsFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderComponentsFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderComponentsFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderComponentsFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderComponentsFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderComponentsFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderComponentsFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderComponentsFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderComponentsFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderComponentsFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderContainerRecipe(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipe",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe aws_imagebuilder_container_recipe}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe aws_imagebuilder_container_recipe} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#arn DataAwsImagebuilderContainerRecipe#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#id DataAwsImagebuilderContainerRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#tags DataAwsImagebuilderContainerRecipe#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderContainerRecipeConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> "DataAwsImagebuilderContainerRecipeComponentList":
        return typing.cast("DataAwsImagebuilderContainerRecipeComponentList", jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerType")
    def container_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileTemplateData")
    def dockerfile_template_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfileTemplateData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceConfiguration")
    def instance_configuration(
        self,
    ) -> "DataAwsImagebuilderContainerRecipeInstanceConfigurationList":
        return typing.cast("DataAwsImagebuilderContainerRecipeInstanceConfigurationList", jsii.get(self, "instanceConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImage")
    def parent_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentImage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepository")
    def target_repository(
        self,
    ) -> "DataAwsImagebuilderContainerRecipeTargetRepositoryList":
        return typing.cast("DataAwsImagebuilderContainerRecipeTargetRepositoryList", jsii.get(self, "targetRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDirectory"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponent",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeComponent:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeComponent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderContainerRecipeComponentList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponentList",
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
    ) -> "DataAwsImagebuilderContainerRecipeComponentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeComponentOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeComponentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponentOutputReference",
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
    @jsii.member(jsii_name="componentArn")
    def component_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "componentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "DataAwsImagebuilderContainerRecipeComponentParameterList":
        return typing.cast("DataAwsImagebuilderContainerRecipeComponentParameterList", jsii.get(self, "parameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeComponent]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeComponent], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeComponent],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponentParameter",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeComponentParameter:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeComponentParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderContainerRecipeComponentParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponentParameterList",
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
    ) -> "DataAwsImagebuilderContainerRecipeComponentParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeComponentParameterOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeComponentParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeComponentParameterOutputReference",
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
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeComponentParameter]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeComponentParameter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeComponentParameter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderContainerRecipeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#arn DataAwsImagebuilderContainerRecipe#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#id DataAwsImagebuilderContainerRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#tags DataAwsImagebuilderContainerRecipe#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#arn DataAwsImagebuilderContainerRecipe#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#id DataAwsImagebuilderContainerRecipe#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipe#tags DataAwsImagebuilderContainerRecipe#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeInstanceConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeInstanceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsList",
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
    ) -> "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference",
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
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "deleteOnTermination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList",
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
    ) -> "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference",
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
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebs")
    def ebs(
        self,
    ) -> DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsList:
        return typing.cast(DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsList, jsii.get(self, "ebs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDevice")
    def no_device(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "noDevice"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualName")
    def virtual_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderContainerRecipeInstanceConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationList",
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
    ) -> "DataAwsImagebuilderContainerRecipeInstanceConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeInstanceConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeInstanceConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeInstanceConfigurationOutputReference",
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
    @jsii.member(jsii_name="blockDeviceMapping")
    def block_device_mapping(
        self,
    ) -> DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList:
        return typing.cast(DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList, jsii.get(self, "blockDeviceMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeInstanceConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeTargetRepository",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderContainerRecipeTargetRepository:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipeTargetRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderContainerRecipeTargetRepositoryList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeTargetRepositoryList",
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
    ) -> "DataAwsImagebuilderContainerRecipeTargetRepositoryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipeTargetRepositoryOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderContainerRecipeTargetRepositoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipeTargetRepositoryOutputReference",
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
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderContainerRecipeTargetRepository]:
        return typing.cast(typing.Optional[DataAwsImagebuilderContainerRecipeTargetRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderContainerRecipeTargetRepository],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderContainerRecipes(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipes",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes aws_imagebuilder_container_recipes}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderContainerRecipesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes aws_imagebuilder_container_recipes} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#filter DataAwsImagebuilderContainerRecipes#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#id DataAwsImagebuilderContainerRecipes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#owner DataAwsImagebuilderContainerRecipes#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderContainerRecipesConfig(
            filter=filter,
            id=id,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderContainerRecipesFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderContainerRecipesFilterList":
        return typing.cast("DataAwsImagebuilderContainerRecipesFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderContainerRecipesFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderContainerRecipesFilter"]]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
        "owner": "owner",
    },
)
class DataAwsImagebuilderContainerRecipesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderContainerRecipesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#filter DataAwsImagebuilderContainerRecipes#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#id DataAwsImagebuilderContainerRecipes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#owner DataAwsImagebuilderContainerRecipes#owner}.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if owner is not None:
            self._values["owner"] = owner

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderContainerRecipesFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#filter DataAwsImagebuilderContainerRecipes#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderContainerRecipesFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#id DataAwsImagebuilderContainerRecipes#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#owner DataAwsImagebuilderContainerRecipes#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipesFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderContainerRecipesFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#name DataAwsImagebuilderContainerRecipes#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#values DataAwsImagebuilderContainerRecipes#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#name DataAwsImagebuilderContainerRecipes#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_container_recipes#values DataAwsImagebuilderContainerRecipes#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderContainerRecipesFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderContainerRecipesFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipesFilterList",
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
    ) -> "DataAwsImagebuilderContainerRecipesFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderContainerRecipesFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderContainerRecipesFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderContainerRecipesFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderContainerRecipesFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderContainerRecipesFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderContainerRecipesFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderContainerRecipesFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderContainerRecipesFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderContainerRecipesFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderDistributionConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration aws_imagebuilder_distribution_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration aws_imagebuilder_distribution_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#arn DataAwsImagebuilderDistributionConfiguration#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#id DataAwsImagebuilderDistributionConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#tags DataAwsImagebuilderDistributionConfiguration#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderDistributionConfigurationConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(
        self,
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionList":
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionList", jsii.get(self, "distribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderDistributionConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#arn DataAwsImagebuilderDistributionConfiguration#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#id DataAwsImagebuilderDistributionConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#tags DataAwsImagebuilderDistributionConfiguration#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#arn DataAwsImagebuilderDistributionConfiguration#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#id DataAwsImagebuilderDistributionConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configuration#tags DataAwsImagebuilderDistributionConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistribution",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistribution:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference",
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
    @jsii.member(jsii_name="organizationalUnitArns")
    def organizational_unit_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organizationalUnitArns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArns")
    def organization_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organizationArns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userGroups")
    def user_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIds")
    def user_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference",
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
    @jsii.member(jsii_name="amiTags")
    def ami_tags(self) -> cdktf.StringMap:
        return typing.cast(cdktf.StringMap, jsii.get(self, "amiTags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchPermission")
    def launch_permission(
        self,
    ) -> DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionList:
        return typing.cast(DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionList, jsii.get(self, "launchPermission"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccountIds")
    def target_account_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetAccountIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference",
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
    @jsii.member(jsii_name="containerTags")
    def container_tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "containerTags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepository")
    def target_repository(
        self,
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryList":
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryList", jsii.get(self, "targetRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference",
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
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference",
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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="default")
    def default(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "default"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateId")
    def launch_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderDistributionConfigurationDistributionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationDistributionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationDistributionOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderDistributionConfigurationDistributionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationDistributionOutputReference",
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
    @jsii.member(jsii_name="amiDistributionConfiguration")
    def ami_distribution_configuration(
        self,
    ) -> DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationList:
        return typing.cast(DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationList, jsii.get(self, "amiDistributionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerDistributionConfiguration")
    def container_distribution_configuration(
        self,
    ) -> DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationList:
        return typing.cast(DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationList, jsii.get(self, "containerDistributionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateConfiguration")
    def launch_template_configuration(
        self,
    ) -> DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList:
        return typing.cast(DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList, jsii.get(self, "launchTemplateConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseConfigurationArns")
    def license_configuration_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "licenseConfigurationArns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderDistributionConfigurationDistribution]:
        return typing.cast(typing.Optional[DataAwsImagebuilderDistributionConfigurationDistribution], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderDistributionConfigurationDistribution],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderDistributionConfigurations(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurations",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations aws_imagebuilder_distribution_configurations}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderDistributionConfigurationsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations aws_imagebuilder_distribution_configurations} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#filter DataAwsImagebuilderDistributionConfigurations#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#id DataAwsImagebuilderDistributionConfigurations#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderDistributionConfigurationsConfig(
            filter=filter,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderDistributionConfigurationsFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderDistributionConfigurationsFilterList":
        return typing.cast("DataAwsImagebuilderDistributionConfigurationsFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderDistributionConfigurationsFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderDistributionConfigurationsFilter"]]], jsii.get(self, "filterInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
    },
)
class DataAwsImagebuilderDistributionConfigurationsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderDistributionConfigurationsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#filter DataAwsImagebuilderDistributionConfigurations#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#id DataAwsImagebuilderDistributionConfigurations#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderDistributionConfigurationsFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#filter DataAwsImagebuilderDistributionConfigurations#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderDistributionConfigurationsFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#id DataAwsImagebuilderDistributionConfigurations#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationsFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderDistributionConfigurationsFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#name DataAwsImagebuilderDistributionConfigurations#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#values DataAwsImagebuilderDistributionConfigurations#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#name DataAwsImagebuilderDistributionConfigurations#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_distribution_configurations#values DataAwsImagebuilderDistributionConfigurations#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderDistributionConfigurationsFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderDistributionConfigurationsFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationsFilterList",
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
    ) -> "DataAwsImagebuilderDistributionConfigurationsFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderDistributionConfigurationsFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderDistributionConfigurationsFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderDistributionConfigurationsFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderDistributionConfigurationsFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderDistributionConfigurationsFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderDistributionConfigurationsFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderDistributionConfigurationsFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderDistributionConfigurationsFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderDistributionConfigurationsFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image aws_imagebuilder_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image aws_imagebuilder_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#arn DataAwsImagebuilderImage#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#id DataAwsImagebuilderImage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#tags DataAwsImagebuilderImage#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderImageConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildVersionArn")
    def build_version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArn")
    def container_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerRecipeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArn")
    def distribution_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributionConfigurationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabled")
    def enhanced_image_metadata_enabled(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "enhancedImageMetadataEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArn")
    def image_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageRecipeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfiguration")
    def image_tests_configuration(
        self,
    ) -> "DataAwsImagebuilderImageImageTestsConfigurationList":
        return typing.cast("DataAwsImagebuilderImageImageTestsConfigurationList", jsii.get(self, "imageTestsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="osVersion")
    def os_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputResources")
    def output_resources(self) -> "DataAwsImagebuilderImageOutputResourcesList":
        return typing.cast("DataAwsImagebuilderImageOutputResourcesList", jsii.get(self, "outputResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#arn DataAwsImagebuilderImage#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#id DataAwsImagebuilderImage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#tags DataAwsImagebuilderImage#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#arn DataAwsImagebuilderImage#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#id DataAwsImagebuilderImage#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image#tags DataAwsImagebuilderImage#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageImageTestsConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageImageTestsConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageImageTestsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageImageTestsConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageImageTestsConfigurationList",
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
    ) -> "DataAwsImagebuilderImageImageTestsConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageImageTestsConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageImageTestsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageImageTestsConfigurationOutputReference",
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
    @jsii.member(jsii_name="imageTestsEnabled")
    def image_tests_enabled(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "imageTestsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutes")
    def timeout_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutMinutes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageImageTestsConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageImageTestsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageImageTestsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResources",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageOutputResources:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageOutputResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResourcesAmis",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageOutputResourcesAmis:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageOutputResourcesAmis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageOutputResourcesAmisList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResourcesAmisList",
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
    ) -> "DataAwsImagebuilderImageOutputResourcesAmisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageOutputResourcesAmisOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageOutputResourcesAmisOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResourcesAmisOutputReference",
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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageOutputResourcesAmis]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageOutputResourcesAmis], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageOutputResourcesAmis],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImageOutputResourcesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResourcesList",
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
    ) -> "DataAwsImagebuilderImageOutputResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageOutputResourcesOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageOutputResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageOutputResourcesOutputReference",
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
    @jsii.member(jsii_name="amis")
    def amis(self) -> DataAwsImagebuilderImageOutputResourcesAmisList:
        return typing.cast(DataAwsImagebuilderImageOutputResourcesAmisList, jsii.get(self, "amis"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageOutputResources]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageOutputResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageOutputResources],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImagePipeline(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipeline",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline aws_imagebuilder_image_pipeline}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline aws_imagebuilder_image_pipeline} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#arn DataAwsImagebuilderImagePipeline#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#id DataAwsImagebuilderImagePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#tags DataAwsImagebuilderImagePipeline#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderImagePipelineConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArn")
    def container_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerRecipeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateLastRun")
    def date_last_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateLastRun"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateNextRun")
    def date_next_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateNextRun"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArn")
    def distribution_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributionConfigurationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabled")
    def enhanced_image_metadata_enabled(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "enhancedImageMetadataEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArn")
    def image_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageRecipeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfiguration")
    def image_tests_configuration(
        self,
    ) -> "DataAwsImagebuilderImagePipelineImageTestsConfigurationList":
        return typing.cast("DataAwsImagebuilderImagePipelineImageTestsConfigurationList", jsii.get(self, "imageTestsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "DataAwsImagebuilderImagePipelineScheduleList":
        return typing.cast("DataAwsImagebuilderImagePipelineScheduleList", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderImagePipelineConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#arn DataAwsImagebuilderImagePipeline#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#id DataAwsImagebuilderImagePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#tags DataAwsImagebuilderImagePipeline#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#arn DataAwsImagebuilderImagePipeline#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#id DataAwsImagebuilderImagePipeline#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipeline#tags DataAwsImagebuilderImagePipeline#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImagePipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineImageTestsConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImagePipelineImageTestsConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImagePipelineImageTestsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImagePipelineImageTestsConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineImageTestsConfigurationList",
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
    ) -> "DataAwsImagebuilderImagePipelineImageTestsConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImagePipelineImageTestsConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImagePipelineImageTestsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineImageTestsConfigurationOutputReference",
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
    @jsii.member(jsii_name="imageTestsEnabled")
    def image_tests_enabled(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "imageTestsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutes")
    def timeout_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutMinutes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImagePipelineImageTestsConfiguration]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImagePipelineImageTestsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImagePipelineImageTestsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineSchedule",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImagePipelineSchedule:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImagePipelineSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImagePipelineScheduleList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineScheduleList",
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
    ) -> "DataAwsImagebuilderImagePipelineScheduleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImagePipelineScheduleOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImagePipelineScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelineScheduleOutputReference",
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
    @jsii.member(jsii_name="pipelineExecutionStartCondition")
    def pipeline_execution_start_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineExecutionStartCondition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleExpression")
    def schedule_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheduleExpression"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImagePipelineSchedule]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImagePipelineSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImagePipelineSchedule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImagePipelines(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelines",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines aws_imagebuilder_image_pipelines}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImagePipelinesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines aws_imagebuilder_image_pipelines} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#filter DataAwsImagebuilderImagePipelines#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#id DataAwsImagebuilderImagePipelines#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderImagePipelinesConfig(
            filter=filter,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImagePipelinesFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderImagePipelinesFilterList":
        return typing.cast("DataAwsImagebuilderImagePipelinesFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImagePipelinesFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImagePipelinesFilter"]]], jsii.get(self, "filterInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelinesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
    },
)
class DataAwsImagebuilderImagePipelinesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImagePipelinesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#filter DataAwsImagebuilderImagePipelines#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#id DataAwsImagebuilderImagePipelines#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImagePipelinesFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#filter DataAwsImagebuilderImagePipelines#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImagePipelinesFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#id DataAwsImagebuilderImagePipelines#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImagePipelinesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelinesFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderImagePipelinesFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#name DataAwsImagebuilderImagePipelines#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#values DataAwsImagebuilderImagePipelines#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#name DataAwsImagebuilderImagePipelines#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_pipelines#values DataAwsImagebuilderImagePipelines#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImagePipelinesFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImagePipelinesFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelinesFilterList",
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
    ) -> "DataAwsImagebuilderImagePipelinesFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImagePipelinesFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImagePipelinesFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImagePipelinesFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImagePipelinesFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImagePipelinesFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImagePipelinesFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderImagePipelinesFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderImagePipelinesFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderImagePipelinesFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImageRecipe(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipe",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe aws_imagebuilder_image_recipe}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe aws_imagebuilder_image_recipe} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#arn DataAwsImagebuilderImageRecipe#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#id DataAwsImagebuilderImageRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#tags DataAwsImagebuilderImageRecipe#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderImageRecipeConfig(
            arn=arn,
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockDeviceMapping")
    def block_device_mapping(
        self,
    ) -> "DataAwsImagebuilderImageRecipeBlockDeviceMappingList":
        return typing.cast("DataAwsImagebuilderImageRecipeBlockDeviceMappingList", jsii.get(self, "blockDeviceMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> "DataAwsImagebuilderImageRecipeComponentList":
        return typing.cast("DataAwsImagebuilderImageRecipeComponentList", jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImage")
    def parent_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentImage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataBase64")
    def user_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDataBase64"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDirectory"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMapping",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageRecipeBlockDeviceMapping:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipeBlockDeviceMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsList",
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
    ) -> "DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference",
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
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "deleteOnTermination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImageRecipeBlockDeviceMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMappingList",
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
    ) -> "DataAwsImagebuilderImageRecipeBlockDeviceMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageRecipeBlockDeviceMappingOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageRecipeBlockDeviceMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeBlockDeviceMappingOutputReference",
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
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebs")
    def ebs(self) -> DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsList:
        return typing.cast(DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsList, jsii.get(self, "ebs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDevice")
    def no_device(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "noDevice"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualName")
    def virtual_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMapping]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMapping], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageRecipeBlockDeviceMapping],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponent",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageRecipeComponent:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipeComponent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageRecipeComponentList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponentList",
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
    ) -> "DataAwsImagebuilderImageRecipeComponentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageRecipeComponentOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageRecipeComponentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponentOutputReference",
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
    @jsii.member(jsii_name="componentArn")
    def component_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "componentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "DataAwsImagebuilderImageRecipeComponentParameterList":
        return typing.cast("DataAwsImagebuilderImageRecipeComponentParameterList", jsii.get(self, "parameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageRecipeComponent]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageRecipeComponent], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageRecipeComponent],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponentParameter",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderImageRecipeComponentParameter:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipeComponentParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageRecipeComponentParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponentParameterList",
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
    ) -> "DataAwsImagebuilderImageRecipeComponentParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageRecipeComponentParameterOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderImageRecipeComponentParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeComponentParameterOutputReference",
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
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderImageRecipeComponentParameter]:
        return typing.cast(typing.Optional[DataAwsImagebuilderImageRecipeComponentParameter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderImageRecipeComponentParameter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsImagebuilderImageRecipeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#arn DataAwsImagebuilderImageRecipe#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#id DataAwsImagebuilderImageRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#tags DataAwsImagebuilderImageRecipe#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#arn DataAwsImagebuilderImageRecipe#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#id DataAwsImagebuilderImageRecipe#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipe#tags DataAwsImagebuilderImageRecipe#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageRecipes(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipes",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes aws_imagebuilder_image_recipes}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImageRecipesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes aws_imagebuilder_image_recipes} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#filter DataAwsImagebuilderImageRecipes#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#id DataAwsImagebuilderImageRecipes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#owner DataAwsImagebuilderImageRecipes#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderImageRecipesConfig(
            filter=filter,
            id=id,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImageRecipesFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderImageRecipesFilterList":
        return typing.cast("DataAwsImagebuilderImageRecipesFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImageRecipesFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImageRecipesFilter"]]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
        "owner": "owner",
    },
)
class DataAwsImagebuilderImageRecipesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderImageRecipesFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#filter DataAwsImagebuilderImageRecipes#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#id DataAwsImagebuilderImageRecipes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#owner DataAwsImagebuilderImageRecipes#owner}.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if owner is not None:
            self._values["owner"] = owner

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImageRecipesFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#filter DataAwsImagebuilderImageRecipes#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderImageRecipesFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#id DataAwsImagebuilderImageRecipes#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#owner DataAwsImagebuilderImageRecipes#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipesFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderImageRecipesFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#name DataAwsImagebuilderImageRecipes#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#values DataAwsImagebuilderImageRecipes#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#name DataAwsImagebuilderImageRecipes#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_image_recipes#values DataAwsImagebuilderImageRecipes#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderImageRecipesFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderImageRecipesFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipesFilterList",
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
    ) -> "DataAwsImagebuilderImageRecipesFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderImageRecipesFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImageRecipesFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImageRecipesFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderImageRecipesFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderImageRecipesFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderImageRecipesFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderImageRecipesFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderImageRecipesFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderImageRecipesFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderInfrastructureConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration aws_imagebuilder_infrastructure_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration aws_imagebuilder_infrastructure_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#arn DataAwsImagebuilderInfrastructureConfiguration#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#id DataAwsImagebuilderInfrastructureConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#resource_tags DataAwsImagebuilderInfrastructureConfiguration#resource_tags}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#tags DataAwsImagebuilderInfrastructureConfiguration#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderInfrastructureConfigurationConfig(
            arn=arn,
            id=id,
            resource_tags=resource_tags,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetResourceTags")
    def reset_resource_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTags", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceMetadataOptions")
    def instance_metadata_options(
        self,
    ) -> "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsList":
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsList", jsii.get(self, "instanceMetadataOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileName")
    def instance_profile_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPair")
    def key_pair(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyPair"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logging")
    def logging(self) -> "DataAwsImagebuilderInfrastructureConfigurationLoggingList":
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationLoggingList", jsii.get(self, "logging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminateInstanceOnFailure")
    def terminate_instance_on_failure(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "terminateInstanceOnFailure"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTagsInput")
    def resource_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "resourceTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTags")
    def resource_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "resourceTags"))

    @resource_tags.setter
    def resource_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "resourceTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
        "id": "id",
        "resource_tags": "resourceTags",
        "tags": "tags",
    },
)
class DataAwsImagebuilderInfrastructureConfigurationConfig(
    cdktf.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#arn DataAwsImagebuilderInfrastructureConfiguration#arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#id DataAwsImagebuilderInfrastructureConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#resource_tags DataAwsImagebuilderInfrastructureConfiguration#resource_tags}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#tags DataAwsImagebuilderInfrastructureConfiguration#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if tags is not None:
            self._values["tags"] = tags

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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#arn DataAwsImagebuilderInfrastructureConfiguration#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#id DataAwsImagebuilderInfrastructureConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#resource_tags DataAwsImagebuilderInfrastructureConfiguration#resource_tags}.'''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configuration#tags DataAwsImagebuilderInfrastructureConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsList",
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
    ) -> "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference",
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
    @jsii.member(jsii_name="httpPutResponseHopLimit")
    def http_put_response_hop_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpPutResponseHopLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpTokens")
    def http_tokens(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpTokens"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions]:
        return typing.cast(typing.Optional[DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLogging",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderInfrastructureConfigurationLogging:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderInfrastructureConfigurationLoggingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLoggingList",
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
    ) -> "DataAwsImagebuilderInfrastructureConfigurationLoggingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationLoggingOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderInfrastructureConfigurationLoggingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLoggingOutputReference",
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
    @jsii.member(jsii_name="s3Logs")
    def s3_logs(
        self,
    ) -> "DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsList":
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsList", jsii.get(self, "s3Logs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLogging]:
        return typing.cast(typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLogging], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLogging],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsList",
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
    ) -> "DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference",
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
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3BucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs]:
        return typing.cast(typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderInfrastructureConfigurations(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurations",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations aws_imagebuilder_infrastructure_configurations}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations aws_imagebuilder_infrastructure_configurations} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#filter DataAwsImagebuilderInfrastructureConfigurations#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#id DataAwsImagebuilderInfrastructureConfigurations#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsImagebuilderInfrastructureConfigurationsConfig(
            filter=filter,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderInfrastructureConfigurationsFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "DataAwsImagebuilderInfrastructureConfigurationsFilterList":
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationsFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]], jsii.get(self, "filterInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "id": "id",
    },
)
class DataAwsImagebuilderInfrastructureConfigurationsConfig(
    cdktf.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#filter DataAwsImagebuilderInfrastructureConfigurations#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#id DataAwsImagebuilderInfrastructureConfigurations#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id

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
    def filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#filter DataAwsImagebuilderInfrastructureConfigurations#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsImagebuilderInfrastructureConfigurationsFilter"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#id DataAwsImagebuilderInfrastructureConfigurations#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationsFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class DataAwsImagebuilderInfrastructureConfigurationsFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#name DataAwsImagebuilderInfrastructureConfigurations#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#values DataAwsImagebuilderInfrastructureConfigurations#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#name DataAwsImagebuilderInfrastructureConfigurations#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/imagebuilder_infrastructure_configurations#values DataAwsImagebuilderInfrastructureConfigurations#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsImagebuilderInfrastructureConfigurationsFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsImagebuilderInfrastructureConfigurationsFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationsFilterList",
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
    ) -> "DataAwsImagebuilderInfrastructureConfigurationsFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsImagebuilderInfrastructureConfigurationsFilterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderInfrastructureConfigurationsFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderInfrastructureConfigurationsFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsImagebuilderInfrastructureConfigurationsFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsImagebuilderInfrastructureConfigurationsFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.DataAwsImagebuilderInfrastructureConfigurationsFilterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "values", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsImagebuilderInfrastructureConfigurationsFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsImagebuilderInfrastructureConfigurationsFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsImagebuilderInfrastructureConfigurationsFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderComponent(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderComponent",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component aws_imagebuilder_component}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        platform: builtins.str,
        version: builtins.str,
        change_description: typing.Optional[builtins.str] = None,
        data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        supported_os_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        uri: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component aws_imagebuilder_component} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#name ImagebuilderComponent#name}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#platform ImagebuilderComponent#platform}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#version ImagebuilderComponent#version}.
        :param change_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#change_description ImagebuilderComponent#change_description}.
        :param data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#data ImagebuilderComponent#data}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#description ImagebuilderComponent#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#id ImagebuilderComponent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#kms_key_id ImagebuilderComponent#kms_key_id}.
        :param supported_os_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#supported_os_versions ImagebuilderComponent#supported_os_versions}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags ImagebuilderComponent#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags_all ImagebuilderComponent#tags_all}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#uri ImagebuilderComponent#uri}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderComponentConfig(
            name=name,
            platform=platform,
            version=version,
            change_description=change_description,
            data=data,
            description=description,
            id=id,
            kms_key_id=kms_key_id,
            supported_os_versions=supported_os_versions,
            tags=tags,
            tags_all=tags_all,
            uri=uri,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetChangeDescription")
    def reset_change_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChangeDescription", []))

    @jsii.member(jsii_name="resetData")
    def reset_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetData", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetSupportedOsVersions")
    def reset_supported_os_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportedOsVersions", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUri")
    def reset_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUri", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeDescriptionInput")
    def change_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "changeDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedOsVersionsInput")
    def supported_os_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "supportedOsVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uriInput")
    def uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeDescription")
    def change_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "changeDescription"))

    @change_description.setter
    def change_description(self, value: builtins.str) -> None:
        jsii.set(self, "changeDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        jsii.set(self, "platform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedOsVersions")
    def supported_os_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedOsVersions"))

    @supported_os_versions.setter
    def supported_os_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "supportedOsVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @uri.setter
    def uri(self, value: builtins.str) -> None:
        jsii.set(self, "uri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderComponentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "platform": "platform",
        "version": "version",
        "change_description": "changeDescription",
        "data": "data",
        "description": "description",
        "id": "id",
        "kms_key_id": "kmsKeyId",
        "supported_os_versions": "supportedOsVersions",
        "tags": "tags",
        "tags_all": "tagsAll",
        "uri": "uri",
    },
)
class ImagebuilderComponentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        platform: builtins.str,
        version: builtins.str,
        change_description: typing.Optional[builtins.str] = None,
        data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        supported_os_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#name ImagebuilderComponent#name}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#platform ImagebuilderComponent#platform}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#version ImagebuilderComponent#version}.
        :param change_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#change_description ImagebuilderComponent#change_description}.
        :param data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#data ImagebuilderComponent#data}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#description ImagebuilderComponent#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#id ImagebuilderComponent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#kms_key_id ImagebuilderComponent#kms_key_id}.
        :param supported_os_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#supported_os_versions ImagebuilderComponent#supported_os_versions}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags ImagebuilderComponent#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags_all ImagebuilderComponent#tags_all}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#uri ImagebuilderComponent#uri}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "platform": platform,
            "version": version,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if change_description is not None:
            self._values["change_description"] = change_description
        if data is not None:
            self._values["data"] = data
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if supported_os_versions is not None:
            self._values["supported_os_versions"] = supported_os_versions
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if uri is not None:
            self._values["uri"] = uri

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#name ImagebuilderComponent#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def platform(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#platform ImagebuilderComponent#platform}.'''
        result = self._values.get("platform")
        assert result is not None, "Required property 'platform' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#version ImagebuilderComponent#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def change_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#change_description ImagebuilderComponent#change_description}.'''
        result = self._values.get("change_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#data ImagebuilderComponent#data}.'''
        result = self._values.get("data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#description ImagebuilderComponent#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#id ImagebuilderComponent#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#kms_key_id ImagebuilderComponent#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def supported_os_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#supported_os_versions ImagebuilderComponent#supported_os_versions}.'''
        result = self._values.get("supported_os_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags ImagebuilderComponent#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#tags_all ImagebuilderComponent#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_component#uri ImagebuilderComponent#uri}.'''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderComponentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderContainerRecipe(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipe",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe aws_imagebuilder_container_recipe}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        component: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeComponent"]],
        container_type: builtins.str,
        name: builtins.str,
        parent_image: builtins.str,
        target_repository: "ImagebuilderContainerRecipeTargetRepository",
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dockerfile_template_data: typing.Optional[builtins.str] = None,
        dockerfile_template_uri: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_configuration: typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        working_directory: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe aws_imagebuilder_container_recipe} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param component: component block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#component ImagebuilderContainerRecipe#component}
        :param container_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#container_type ImagebuilderContainerRecipe#container_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#name ImagebuilderContainerRecipe#name}.
        :param parent_image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#parent_image ImagebuilderContainerRecipe#parent_image}.
        :param target_repository: target_repository block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#target_repository ImagebuilderContainerRecipe#target_repository}
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#version ImagebuilderContainerRecipe#version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#description ImagebuilderContainerRecipe#description}.
        :param dockerfile_template_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_data ImagebuilderContainerRecipe#dockerfile_template_data}.
        :param dockerfile_template_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_uri ImagebuilderContainerRecipe#dockerfile_template_uri}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#id ImagebuilderContainerRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_configuration: instance_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#instance_configuration ImagebuilderContainerRecipe#instance_configuration}
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags ImagebuilderContainerRecipe#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags_all ImagebuilderContainerRecipe#tags_all}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#working_directory ImagebuilderContainerRecipe#working_directory}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderContainerRecipeConfig(
            component=component,
            container_type=container_type,
            name=name,
            parent_image=parent_image,
            target_repository=target_repository,
            version=version,
            description=description,
            dockerfile_template_data=dockerfile_template_data,
            dockerfile_template_uri=dockerfile_template_uri,
            id=id,
            instance_configuration=instance_configuration,
            kms_key_id=kms_key_id,
            tags=tags,
            tags_all=tags_all,
            working_directory=working_directory,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putComponent")
    def put_component(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeComponent"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putComponent", [value]))

    @jsii.member(jsii_name="putInstanceConfiguration")
    def put_instance_configuration(
        self,
        *,
        block_device_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping"]]] = None,
        image: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param block_device_mapping: block_device_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#block_device_mapping ImagebuilderContainerRecipe#block_device_mapping}
        :param image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#image ImagebuilderContainerRecipe#image}.
        '''
        value = ImagebuilderContainerRecipeInstanceConfiguration(
            block_device_mapping=block_device_mapping, image=image
        )

        return typing.cast(None, jsii.invoke(self, "putInstanceConfiguration", [value]))

    @jsii.member(jsii_name="putTargetRepository")
    def put_target_repository(
        self,
        *,
        repository_name: builtins.str,
        service: builtins.str,
    ) -> None:
        '''
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#repository_name ImagebuilderContainerRecipe#repository_name}.
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#service ImagebuilderContainerRecipe#service}.
        '''
        value = ImagebuilderContainerRecipeTargetRepository(
            repository_name=repository_name, service=service
        )

        return typing.cast(None, jsii.invoke(self, "putTargetRepository", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDockerfileTemplateData")
    def reset_dockerfile_template_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerfileTemplateData", []))

    @jsii.member(jsii_name="resetDockerfileTemplateUri")
    def reset_dockerfile_template_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerfileTemplateUri", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceConfiguration")
    def reset_instance_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceConfiguration", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetWorkingDirectory")
    def reset_working_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDirectory", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> "ImagebuilderContainerRecipeComponentList":
        return typing.cast("ImagebuilderContainerRecipeComponentList", jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceConfiguration")
    def instance_configuration(
        self,
    ) -> "ImagebuilderContainerRecipeInstanceConfigurationOutputReference":
        return typing.cast("ImagebuilderContainerRecipeInstanceConfigurationOutputReference", jsii.get(self, "instanceConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepository")
    def target_repository(
        self,
    ) -> "ImagebuilderContainerRecipeTargetRepositoryOutputReference":
        return typing.cast("ImagebuilderContainerRecipeTargetRepositoryOutputReference", jsii.get(self, "targetRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentInput")
    def component_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponent"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponent"]]], jsii.get(self, "componentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerTypeInput")
    def container_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileTemplateDataInput")
    def dockerfile_template_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dockerfileTemplateDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileTemplateUriInput")
    def dockerfile_template_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dockerfileTemplateUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceConfigurationInput")
    def instance_configuration_input(
        self,
    ) -> typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"]:
        return typing.cast(typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"], jsii.get(self, "instanceConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImageInput")
    def parent_image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentImageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepositoryInput")
    def target_repository_input(
        self,
    ) -> typing.Optional["ImagebuilderContainerRecipeTargetRepository"]:
        return typing.cast(typing.Optional["ImagebuilderContainerRecipeTargetRepository"], jsii.get(self, "targetRepositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectoryInput")
    def working_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerType")
    def container_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerType"))

    @container_type.setter
    def container_type(self, value: builtins.str) -> None:
        jsii.set(self, "containerType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileTemplateData")
    def dockerfile_template_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfileTemplateData"))

    @dockerfile_template_data.setter
    def dockerfile_template_data(self, value: builtins.str) -> None:
        jsii.set(self, "dockerfileTemplateData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileTemplateUri")
    def dockerfile_template_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfileTemplateUri"))

    @dockerfile_template_uri.setter
    def dockerfile_template_uri(self, value: builtins.str) -> None:
        jsii.set(self, "dockerfileTemplateUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImage")
    def parent_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentImage"))

    @parent_image.setter
    def parent_image(self, value: builtins.str) -> None:
        jsii.set(self, "parentImage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDirectory"))

    @working_directory.setter
    def working_directory(self, value: builtins.str) -> None:
        jsii.set(self, "workingDirectory", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponent",
    jsii_struct_bases=[],
    name_mapping={"component_arn": "componentArn", "parameter": "parameter"},
)
class ImagebuilderContainerRecipeComponent:
    def __init__(
        self,
        *,
        component_arn: builtins.str,
        parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeComponentParameter"]]] = None,
    ) -> None:
        '''
        :param component_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#component_arn ImagebuilderContainerRecipe#component_arn}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#parameter ImagebuilderContainerRecipe#parameter}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "component_arn": component_arn,
        }
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def component_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#component_arn ImagebuilderContainerRecipe#component_arn}.'''
        result = self._values.get("component_arn")
        assert result is not None, "Required property 'component_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponentParameter"]]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#parameter ImagebuilderContainerRecipe#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponentParameter"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeComponent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderContainerRecipeComponentList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponentList",
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
    ) -> "ImagebuilderContainerRecipeComponentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderContainerRecipeComponentOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponent]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponent]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponent]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderContainerRecipeComponentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponentOutputReference",
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

    @jsii.member(jsii_name="putParameter")
    def put_parameter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeComponentParameter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putParameter", [value]))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "ImagebuilderContainerRecipeComponentParameterList":
        return typing.cast("ImagebuilderContainerRecipeComponentParameterList", jsii.get(self, "parameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentArnInput")
    def component_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "componentArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponentParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeComponentParameter"]]], jsii.get(self, "parameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentArn")
    def component_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "componentArn"))

    @component_arn.setter
    def component_arn(self, value: builtins.str) -> None:
        jsii.set(self, "componentArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderContainerRecipeComponent, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderContainerRecipeComponent, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderContainerRecipeComponent, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponentParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ImagebuilderContainerRecipeComponentParameter:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#name ImagebuilderContainerRecipe#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#value ImagebuilderContainerRecipe#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#name ImagebuilderContainerRecipe#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#value ImagebuilderContainerRecipe#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeComponentParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderContainerRecipeComponentParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponentParameterList",
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
    ) -> "ImagebuilderContainerRecipeComponentParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderContainerRecipeComponentParameterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponentParameter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponentParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponentParameter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderContainerRecipeComponentParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeComponentParameterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderContainerRecipeComponentParameter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderContainerRecipeComponentParameter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderContainerRecipeComponentParameter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "component": "component",
        "container_type": "containerType",
        "name": "name",
        "parent_image": "parentImage",
        "target_repository": "targetRepository",
        "version": "version",
        "description": "description",
        "dockerfile_template_data": "dockerfileTemplateData",
        "dockerfile_template_uri": "dockerfileTemplateUri",
        "id": "id",
        "instance_configuration": "instanceConfiguration",
        "kms_key_id": "kmsKeyId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "working_directory": "workingDirectory",
    },
)
class ImagebuilderContainerRecipeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        component: typing.Union[cdktf.IResolvable, typing.Sequence[ImagebuilderContainerRecipeComponent]],
        container_type: builtins.str,
        name: builtins.str,
        parent_image: builtins.str,
        target_repository: "ImagebuilderContainerRecipeTargetRepository",
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dockerfile_template_data: typing.Optional[builtins.str] = None,
        dockerfile_template_uri: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_configuration: typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param component: component block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#component ImagebuilderContainerRecipe#component}
        :param container_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#container_type ImagebuilderContainerRecipe#container_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#name ImagebuilderContainerRecipe#name}.
        :param parent_image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#parent_image ImagebuilderContainerRecipe#parent_image}.
        :param target_repository: target_repository block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#target_repository ImagebuilderContainerRecipe#target_repository}
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#version ImagebuilderContainerRecipe#version}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#description ImagebuilderContainerRecipe#description}.
        :param dockerfile_template_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_data ImagebuilderContainerRecipe#dockerfile_template_data}.
        :param dockerfile_template_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_uri ImagebuilderContainerRecipe#dockerfile_template_uri}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#id ImagebuilderContainerRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_configuration: instance_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#instance_configuration ImagebuilderContainerRecipe#instance_configuration}
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags ImagebuilderContainerRecipe#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags_all ImagebuilderContainerRecipe#tags_all}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#working_directory ImagebuilderContainerRecipe#working_directory}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(target_repository, dict):
            target_repository = ImagebuilderContainerRecipeTargetRepository(**target_repository)
        if isinstance(instance_configuration, dict):
            instance_configuration = ImagebuilderContainerRecipeInstanceConfiguration(**instance_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "component": component,
            "container_type": container_type,
            "name": name,
            "parent_image": parent_image,
            "target_repository": target_repository,
            "version": version,
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
        if dockerfile_template_data is not None:
            self._values["dockerfile_template_data"] = dockerfile_template_data
        if dockerfile_template_uri is not None:
            self._values["dockerfile_template_uri"] = dockerfile_template_uri
        if id is not None:
            self._values["id"] = id
        if instance_configuration is not None:
            self._values["instance_configuration"] = instance_configuration
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if working_directory is not None:
            self._values["working_directory"] = working_directory

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
    def component(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponent]]:
        '''component block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#component ImagebuilderContainerRecipe#component}
        '''
        result = self._values.get("component")
        assert result is not None, "Required property 'component' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeComponent]], result)

    @builtins.property
    def container_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#container_type ImagebuilderContainerRecipe#container_type}.'''
        result = self._values.get("container_type")
        assert result is not None, "Required property 'container_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#name ImagebuilderContainerRecipe#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_image(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#parent_image ImagebuilderContainerRecipe#parent_image}.'''
        result = self._values.get("parent_image")
        assert result is not None, "Required property 'parent_image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_repository(self) -> "ImagebuilderContainerRecipeTargetRepository":
        '''target_repository block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#target_repository ImagebuilderContainerRecipe#target_repository}
        '''
        result = self._values.get("target_repository")
        assert result is not None, "Required property 'target_repository' is missing"
        return typing.cast("ImagebuilderContainerRecipeTargetRepository", result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#version ImagebuilderContainerRecipe#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#description ImagebuilderContainerRecipe#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dockerfile_template_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_data ImagebuilderContainerRecipe#dockerfile_template_data}.'''
        result = self._values.get("dockerfile_template_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dockerfile_template_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#dockerfile_template_uri ImagebuilderContainerRecipe#dockerfile_template_uri}.'''
        result = self._values.get("dockerfile_template_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#id ImagebuilderContainerRecipe#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_configuration(
        self,
    ) -> typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"]:
        '''instance_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#instance_configuration ImagebuilderContainerRecipe#instance_configuration}
        '''
        result = self._values.get("instance_configuration")
        return typing.cast(typing.Optional["ImagebuilderContainerRecipeInstanceConfiguration"], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags ImagebuilderContainerRecipe#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#tags_all ImagebuilderContainerRecipe#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#working_directory ImagebuilderContainerRecipe#working_directory}.'''
        result = self._values.get("working_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfiguration",
    jsii_struct_bases=[],
    name_mapping={"block_device_mapping": "blockDeviceMapping", "image": "image"},
)
class ImagebuilderContainerRecipeInstanceConfiguration:
    def __init__(
        self,
        *,
        block_device_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping"]]] = None,
        image: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param block_device_mapping: block_device_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#block_device_mapping ImagebuilderContainerRecipe#block_device_mapping}
        :param image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#image ImagebuilderContainerRecipe#image}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if block_device_mapping is not None:
            self._values["block_device_mapping"] = block_device_mapping
        if image is not None:
            self._values["image"] = image

    @builtins.property
    def block_device_mapping(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping"]]]:
        '''block_device_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#block_device_mapping ImagebuilderContainerRecipe#block_device_mapping}
        '''
        result = self._values.get("block_device_mapping")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping"]]], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#image ImagebuilderContainerRecipe#image}.'''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeInstanceConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping",
    jsii_struct_bases=[],
    name_mapping={
        "device_name": "deviceName",
        "ebs": "ebs",
        "no_device": "noDevice",
        "virtual_name": "virtualName",
    },
)
class ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping:
    def __init__(
        self,
        *,
        device_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs"] = None,
        no_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        virtual_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#device_name ImagebuilderContainerRecipe#device_name}.
        :param ebs: ebs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#ebs ImagebuilderContainerRecipe#ebs}
        :param no_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#no_device ImagebuilderContainerRecipe#no_device}.
        :param virtual_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#virtual_name ImagebuilderContainerRecipe#virtual_name}.
        '''
        if isinstance(ebs, dict):
            ebs = ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs(**ebs)
        self._values: typing.Dict[str, typing.Any] = {}
        if device_name is not None:
            self._values["device_name"] = device_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if no_device is not None:
            self._values["no_device"] = no_device
        if virtual_name is not None:
            self._values["virtual_name"] = virtual_name

    @builtins.property
    def device_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#device_name ImagebuilderContainerRecipe#device_name}.'''
        result = self._values.get("device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(
        self,
    ) -> typing.Optional["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs"]:
        '''ebs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#ebs ImagebuilderContainerRecipe#ebs}
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional["ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs"], result)

    @builtins.property
    def no_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#no_device ImagebuilderContainerRecipe#no_device}.'''
        result = self._values.get("no_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def virtual_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#virtual_name ImagebuilderContainerRecipe#virtual_name}.'''
        result = self._values.get("virtual_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "encrypted": "encrypted",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "snapshot_id": "snapshotId",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#delete_on_termination ImagebuilderContainerRecipe#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#encrypted ImagebuilderContainerRecipe#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#iops ImagebuilderContainerRecipe#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#snapshot_id ImagebuilderContainerRecipe#snapshot_id}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_size ImagebuilderContainerRecipe#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_type ImagebuilderContainerRecipe#volume_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def delete_on_termination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#delete_on_termination ImagebuilderContainerRecipe#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#encrypted ImagebuilderContainerRecipe#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#iops ImagebuilderContainerRecipe#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#snapshot_id ImagebuilderContainerRecipe#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_size ImagebuilderContainerRecipe#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_type ImagebuilderContainerRecipe#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference",
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

    @jsii.member(jsii_name="resetDeleteOnTermination")
    def reset_delete_on_termination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteOnTermination", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

    @jsii.member(jsii_name="resetVolumeSize")
    def reset_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeSize", []))

    @jsii.member(jsii_name="resetVolumeType")
    def reset_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteOnTerminationInput")
    def delete_on_termination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteOnTerminationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInput")
    def volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteOnTermination"))

    @delete_on_termination.setter
    def delete_on_termination(self, value: builtins.str) -> None:
        jsii.set(self, "deleteOnTermination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: builtins.str) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        jsii.set(self, "iops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @volume_size.setter
    def volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "volumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        jsii.set(self, "volumeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList",
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
    ) -> "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference",
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

    @jsii.member(jsii_name="putEbs")
    def put_ebs(
        self,
        *,
        delete_on_termination: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#delete_on_termination ImagebuilderContainerRecipe#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#encrypted ImagebuilderContainerRecipe#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#iops ImagebuilderContainerRecipe#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#kms_key_id ImagebuilderContainerRecipe#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#snapshot_id ImagebuilderContainerRecipe#snapshot_id}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_size ImagebuilderContainerRecipe#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#volume_type ImagebuilderContainerRecipe#volume_type}.
        '''
        value = ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs(
            delete_on_termination=delete_on_termination,
            encrypted=encrypted,
            iops=iops,
            kms_key_id=kms_key_id,
            snapshot_id=snapshot_id,
            volume_size=volume_size,
            volume_type=volume_type,
        )

        return typing.cast(None, jsii.invoke(self, "putEbs", [value]))

    @jsii.member(jsii_name="resetDeviceName")
    def reset_device_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceName", []))

    @jsii.member(jsii_name="resetEbs")
    def reset_ebs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbs", []))

    @jsii.member(jsii_name="resetNoDevice")
    def reset_no_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoDevice", []))

    @jsii.member(jsii_name="resetVirtualName")
    def reset_virtual_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebs")
    def ebs(
        self,
    ) -> ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference:
        return typing.cast(ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference, jsii.get(self, "ebs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceNameInput")
    def device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsInput")
    def ebs_input(
        self,
    ) -> typing.Optional[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs], jsii.get(self, "ebsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDeviceInput")
    def no_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualNameInput")
    def virtual_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @device_name.setter
    def device_name(self, value: builtins.str) -> None:
        jsii.set(self, "deviceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDevice")
    def no_device(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noDevice"))

    @no_device.setter
    def no_device(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualName")
    def virtual_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualName"))

    @virtual_name.setter
    def virtual_name(self, value: builtins.str) -> None:
        jsii.set(self, "virtualName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderContainerRecipeInstanceConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeInstanceConfigurationOutputReference",
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

    @jsii.member(jsii_name="putBlockDeviceMapping")
    def put_block_device_mapping(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putBlockDeviceMapping", [value]))

    @jsii.member(jsii_name="resetBlockDeviceMapping")
    def reset_block_device_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockDeviceMapping", []))

    @jsii.member(jsii_name="resetImage")
    def reset_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockDeviceMapping")
    def block_device_mapping(
        self,
    ) -> ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList:
        return typing.cast(ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList, jsii.get(self, "blockDeviceMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockDeviceMappingInput")
    def block_device_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping]]], jsii.get(self, "blockDeviceMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        jsii.set(self, "image", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderContainerRecipeInstanceConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderContainerRecipeInstanceConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderContainerRecipeInstanceConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeTargetRepository",
    jsii_struct_bases=[],
    name_mapping={"repository_name": "repositoryName", "service": "service"},
)
class ImagebuilderContainerRecipeTargetRepository:
    def __init__(self, *, repository_name: builtins.str, service: builtins.str) -> None:
        '''
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#repository_name ImagebuilderContainerRecipe#repository_name}.
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#service ImagebuilderContainerRecipe#service}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
            "service": service,
        }

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#repository_name ImagebuilderContainerRecipe#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_container_recipe#service ImagebuilderContainerRecipe#service}.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderContainerRecipeTargetRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderContainerRecipeTargetRepositoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderContainerRecipeTargetRepositoryOutputReference",
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
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderContainerRecipeTargetRepository]:
        return typing.cast(typing.Optional[ImagebuilderContainerRecipeTargetRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderContainerRecipeTargetRepository],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderDistributionConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration aws_imagebuilder_distribution_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        distribution: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderDistributionConfigurationDistribution"]],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration aws_imagebuilder_distribution_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param distribution: distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#distribution ImagebuilderDistributionConfiguration#distribution}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#id ImagebuilderDistributionConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags ImagebuilderDistributionConfiguration#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags_all ImagebuilderDistributionConfiguration#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderDistributionConfigurationConfig(
            distribution=distribution,
            name=name,
            description=description,
            id=id,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putDistribution")
    def put_distribution(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderDistributionConfigurationDistribution"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putDistribution", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> "ImagebuilderDistributionConfigurationDistributionList":
        return typing.cast("ImagebuilderDistributionConfigurationDistributionList", jsii.get(self, "distribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionInput")
    def distribution_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistribution"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistribution"]]], jsii.get(self, "distributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "distribution": "distribution",
        "name": "name",
        "description": "description",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ImagebuilderDistributionConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        distribution: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderDistributionConfigurationDistribution"]],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param distribution: distribution block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#distribution ImagebuilderDistributionConfiguration#distribution}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#id ImagebuilderDistributionConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags ImagebuilderDistributionConfiguration#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags_all ImagebuilderDistributionConfiguration#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "distribution": distribution,
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
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def distribution(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistribution"]]:
        '''distribution block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#distribution ImagebuilderDistributionConfiguration#distribution}
        '''
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistribution"]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#id ImagebuilderDistributionConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags ImagebuilderDistributionConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#tags_all ImagebuilderDistributionConfiguration#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistribution",
    jsii_struct_bases=[],
    name_mapping={
        "region": "region",
        "ami_distribution_configuration": "amiDistributionConfiguration",
        "container_distribution_configuration": "containerDistributionConfiguration",
        "launch_template_configuration": "launchTemplateConfiguration",
        "license_configuration_arns": "licenseConfigurationArns",
    },
)
class ImagebuilderDistributionConfigurationDistribution:
    def __init__(
        self,
        *,
        region: builtins.str,
        ami_distribution_configuration: typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration"] = None,
        container_distribution_configuration: typing.Optional["ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration"] = None,
        launch_template_configuration: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration"]]] = None,
        license_configuration_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#region ImagebuilderDistributionConfiguration#region}.
        :param ami_distribution_configuration: ami_distribution_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#ami_distribution_configuration ImagebuilderDistributionConfiguration#ami_distribution_configuration}
        :param container_distribution_configuration: container_distribution_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#container_distribution_configuration ImagebuilderDistributionConfiguration#container_distribution_configuration}
        :param launch_template_configuration: launch_template_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_template_configuration ImagebuilderDistributionConfiguration#launch_template_configuration}
        :param license_configuration_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#license_configuration_arns ImagebuilderDistributionConfiguration#license_configuration_arns}.
        '''
        if isinstance(ami_distribution_configuration, dict):
            ami_distribution_configuration = ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration(**ami_distribution_configuration)
        if isinstance(container_distribution_configuration, dict):
            container_distribution_configuration = ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration(**container_distribution_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "region": region,
        }
        if ami_distribution_configuration is not None:
            self._values["ami_distribution_configuration"] = ami_distribution_configuration
        if container_distribution_configuration is not None:
            self._values["container_distribution_configuration"] = container_distribution_configuration
        if launch_template_configuration is not None:
            self._values["launch_template_configuration"] = launch_template_configuration
        if license_configuration_arns is not None:
            self._values["license_configuration_arns"] = license_configuration_arns

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#region ImagebuilderDistributionConfiguration#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ami_distribution_configuration(
        self,
    ) -> typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration"]:
        '''ami_distribution_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#ami_distribution_configuration ImagebuilderDistributionConfiguration#ami_distribution_configuration}
        '''
        result = self._values.get("ami_distribution_configuration")
        return typing.cast(typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration"], result)

    @builtins.property
    def container_distribution_configuration(
        self,
    ) -> typing.Optional["ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration"]:
        '''container_distribution_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#container_distribution_configuration ImagebuilderDistributionConfiguration#container_distribution_configuration}
        '''
        result = self._values.get("container_distribution_configuration")
        return typing.cast(typing.Optional["ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration"], result)

    @builtins.property
    def launch_template_configuration(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration"]]]:
        '''launch_template_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_template_configuration ImagebuilderDistributionConfiguration#launch_template_configuration}
        '''
        result = self._values.get("launch_template_configuration")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration"]]], result)

    @builtins.property
    def license_configuration_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#license_configuration_arns ImagebuilderDistributionConfiguration#license_configuration_arns}.'''
        result = self._values.get("license_configuration_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistribution(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "ami_tags": "amiTags",
        "description": "description",
        "kms_key_id": "kmsKeyId",
        "launch_permission": "launchPermission",
        "name": "name",
        "target_account_ids": "targetAccountIds",
    },
)
class ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration:
    def __init__(
        self,
        *,
        ami_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        launch_permission: typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission"] = None,
        name: typing.Optional[builtins.str] = None,
        target_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param ami_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#ami_tags ImagebuilderDistributionConfiguration#ami_tags}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#kms_key_id ImagebuilderDistributionConfiguration#kms_key_id}.
        :param launch_permission: launch_permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_permission ImagebuilderDistributionConfiguration#launch_permission}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.
        :param target_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_account_ids ImagebuilderDistributionConfiguration#target_account_ids}.
        '''
        if isinstance(launch_permission, dict):
            launch_permission = ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission(**launch_permission)
        self._values: typing.Dict[str, typing.Any] = {}
        if ami_tags is not None:
            self._values["ami_tags"] = ami_tags
        if description is not None:
            self._values["description"] = description
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if launch_permission is not None:
            self._values["launch_permission"] = launch_permission
        if name is not None:
            self._values["name"] = name
        if target_account_ids is not None:
            self._values["target_account_ids"] = target_account_ids

    @builtins.property
    def ami_tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#ami_tags ImagebuilderDistributionConfiguration#ami_tags}.'''
        result = self._values.get("ami_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#kms_key_id ImagebuilderDistributionConfiguration#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def launch_permission(
        self,
    ) -> typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission"]:
        '''launch_permission block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_permission ImagebuilderDistributionConfiguration#launch_permission}
        '''
        result = self._values.get("launch_permission")
        return typing.cast(typing.Optional["ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_account_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_account_ids ImagebuilderDistributionConfiguration#target_account_ids}.'''
        result = self._values.get("target_account_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission",
    jsii_struct_bases=[],
    name_mapping={
        "organizational_unit_arns": "organizationalUnitArns",
        "organization_arns": "organizationArns",
        "user_groups": "userGroups",
        "user_ids": "userIds",
    },
)
class ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission:
    def __init__(
        self,
        *,
        organizational_unit_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organizational_unit_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organizational_unit_arns ImagebuilderDistributionConfiguration#organizational_unit_arns}.
        :param organization_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organization_arns ImagebuilderDistributionConfiguration#organization_arns}.
        :param user_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_groups ImagebuilderDistributionConfiguration#user_groups}.
        :param user_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_ids ImagebuilderDistributionConfiguration#user_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if organizational_unit_arns is not None:
            self._values["organizational_unit_arns"] = organizational_unit_arns
        if organization_arns is not None:
            self._values["organization_arns"] = organization_arns
        if user_groups is not None:
            self._values["user_groups"] = user_groups
        if user_ids is not None:
            self._values["user_ids"] = user_ids

    @builtins.property
    def organizational_unit_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organizational_unit_arns ImagebuilderDistributionConfiguration#organizational_unit_arns}.'''
        result = self._values.get("organizational_unit_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def organization_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organization_arns ImagebuilderDistributionConfiguration#organization_arns}.'''
        result = self._values.get("organization_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_groups ImagebuilderDistributionConfiguration#user_groups}.'''
        result = self._values.get("user_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_ids ImagebuilderDistributionConfiguration#user_ids}.'''
        result = self._values.get("user_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference",
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

    @jsii.member(jsii_name="resetOrganizationalUnitArns")
    def reset_organizational_unit_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnitArns", []))

    @jsii.member(jsii_name="resetOrganizationArns")
    def reset_organization_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationArns", []))

    @jsii.member(jsii_name="resetUserGroups")
    def reset_user_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserGroups", []))

    @jsii.member(jsii_name="resetUserIds")
    def reset_user_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArnsInput")
    def organizational_unit_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationalUnitArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArnsInput")
    def organization_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userGroupsInput")
    def user_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdsInput")
    def user_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArns")
    def organizational_unit_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organizationalUnitArns"))

    @organizational_unit_arns.setter
    def organizational_unit_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "organizationalUnitArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArns")
    def organization_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organizationArns"))

    @organization_arns.setter
    def organization_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "organizationArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userGroups")
    def user_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userGroups"))

    @user_groups.setter
    def user_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "userGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIds")
    def user_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userIds"))

    @user_ids.setter
    def user_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "userIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference",
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

    @jsii.member(jsii_name="putLaunchPermission")
    def put_launch_permission(
        self,
        *,
        organizational_unit_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param organizational_unit_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organizational_unit_arns ImagebuilderDistributionConfiguration#organizational_unit_arns}.
        :param organization_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#organization_arns ImagebuilderDistributionConfiguration#organization_arns}.
        :param user_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_groups ImagebuilderDistributionConfiguration#user_groups}.
        :param user_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#user_ids ImagebuilderDistributionConfiguration#user_ids}.
        '''
        value = ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission(
            organizational_unit_arns=organizational_unit_arns,
            organization_arns=organization_arns,
            user_groups=user_groups,
            user_ids=user_ids,
        )

        return typing.cast(None, jsii.invoke(self, "putLaunchPermission", [value]))

    @jsii.member(jsii_name="resetAmiTags")
    def reset_ami_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmiTags", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetLaunchPermission")
    def reset_launch_permission(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchPermission", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTargetAccountIds")
    def reset_target_account_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetAccountIds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchPermission")
    def launch_permission(
        self,
    ) -> ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference:
        return typing.cast(ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference, jsii.get(self, "launchPermission"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiTagsInput")
    def ami_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "amiTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchPermissionInput")
    def launch_permission_input(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission], jsii.get(self, "launchPermissionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccountIdsInput")
    def target_account_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetAccountIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiTags")
    def ami_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "amiTags"))

    @ami_tags.setter
    def ami_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "amiTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAccountIds")
    def target_account_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetAccountIds"))

    @target_account_ids.setter
    def target_account_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetAccountIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "target_repository": "targetRepository",
        "container_tags": "containerTags",
        "description": "description",
    },
)
class ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration:
    def __init__(
        self,
        *,
        target_repository: "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository",
        container_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_repository: target_repository block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_repository ImagebuilderDistributionConfiguration#target_repository}
        :param container_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#container_tags ImagebuilderDistributionConfiguration#container_tags}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        '''
        if isinstance(target_repository, dict):
            target_repository = ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository(**target_repository)
        self._values: typing.Dict[str, typing.Any] = {
            "target_repository": target_repository,
        }
        if container_tags is not None:
            self._values["container_tags"] = container_tags
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def target_repository(
        self,
    ) -> "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository":
        '''target_repository block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_repository ImagebuilderDistributionConfiguration#target_repository}
        '''
        result = self._values.get("target_repository")
        assert result is not None, "Required property 'target_repository' is missing"
        return typing.cast("ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository", result)

    @builtins.property
    def container_tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#container_tags ImagebuilderDistributionConfiguration#container_tags}.'''
        result = self._values.get("container_tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference",
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

    @jsii.member(jsii_name="putTargetRepository")
    def put_target_repository(
        self,
        *,
        repository_name: builtins.str,
        service: builtins.str,
    ) -> None:
        '''
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#repository_name ImagebuilderDistributionConfiguration#repository_name}.
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#service ImagebuilderDistributionConfiguration#service}.
        '''
        value = ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository(
            repository_name=repository_name, service=service
        )

        return typing.cast(None, jsii.invoke(self, "putTargetRepository", [value]))

    @jsii.member(jsii_name="resetContainerTags")
    def reset_container_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerTags", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepository")
    def target_repository(
        self,
    ) -> "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference":
        return typing.cast("ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference", jsii.get(self, "targetRepository"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerTagsInput")
    def container_tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "containerTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetRepositoryInput")
    def target_repository_input(
        self,
    ) -> typing.Optional["ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository"]:
        return typing.cast(typing.Optional["ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository"], jsii.get(self, "targetRepositoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerTags")
    def container_tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "containerTags"))

    @container_tags.setter
    def container_tags(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "containerTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository",
    jsii_struct_bases=[],
    name_mapping={"repository_name": "repositoryName", "service": "service"},
)
class ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository:
    def __init__(self, *, repository_name: builtins.str, service: builtins.str) -> None:
        '''
        :param repository_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#repository_name ImagebuilderDistributionConfiguration#repository_name}.
        :param service: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#service ImagebuilderDistributionConfiguration#service}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
            "service": service,
        }

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#repository_name ImagebuilderDistributionConfiguration#repository_name}.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#service ImagebuilderDistributionConfiguration#service}.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference",
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
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceInput")
    def service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        jsii.set(self, "repositoryName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @service.setter
    def service(self, value: builtins.str) -> None:
        jsii.set(self, "service", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "launch_template_id": "launchTemplateId",
        "account_id": "accountId",
        "default": "default",
    },
)
class ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration:
    def __init__(
        self,
        *,
        launch_template_id: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        default: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param launch_template_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_template_id ImagebuilderDistributionConfiguration#launch_template_id}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#account_id ImagebuilderDistributionConfiguration#account_id}.
        :param default: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#default ImagebuilderDistributionConfiguration#default}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "launch_template_id": launch_template_id,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if default is not None:
            self._values["default"] = default

    @builtins.property
    def launch_template_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_template_id ImagebuilderDistributionConfiguration#launch_template_id}.'''
        result = self._values.get("launch_template_id")
        assert result is not None, "Required property 'launch_template_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#account_id ImagebuilderDistributionConfiguration#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#default ImagebuilderDistributionConfiguration#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList",
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
    ) -> "ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetDefault")
    def reset_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefault", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInput")
    def default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "defaultInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateIdInput")
    def launch_template_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "launchTemplateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="default")
    def default(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "default"))

    @default.setter
    def default(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "default", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateId")
    def launch_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "launchTemplateId"))

    @launch_template_id.setter
    def launch_template_id(self, value: builtins.str) -> None:
        jsii.set(self, "launchTemplateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderDistributionConfigurationDistributionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionList",
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
    ) -> "ImagebuilderDistributionConfigurationDistributionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderDistributionConfigurationDistributionOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistribution]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistribution]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistribution]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderDistributionConfigurationDistributionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderDistributionConfigurationDistributionOutputReference",
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

    @jsii.member(jsii_name="putAmiDistributionConfiguration")
    def put_ami_distribution_configuration(
        self,
        *,
        ami_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        launch_permission: typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission] = None,
        name: typing.Optional[builtins.str] = None,
        target_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param ami_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#ami_tags ImagebuilderDistributionConfiguration#ami_tags}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#kms_key_id ImagebuilderDistributionConfiguration#kms_key_id}.
        :param launch_permission: launch_permission block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#launch_permission ImagebuilderDistributionConfiguration#launch_permission}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#name ImagebuilderDistributionConfiguration#name}.
        :param target_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_account_ids ImagebuilderDistributionConfiguration#target_account_ids}.
        '''
        value = ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration(
            ami_tags=ami_tags,
            description=description,
            kms_key_id=kms_key_id,
            launch_permission=launch_permission,
            name=name,
            target_account_ids=target_account_ids,
        )

        return typing.cast(None, jsii.invoke(self, "putAmiDistributionConfiguration", [value]))

    @jsii.member(jsii_name="putContainerDistributionConfiguration")
    def put_container_distribution_configuration(
        self,
        *,
        target_repository: ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository,
        container_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_repository: target_repository block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#target_repository ImagebuilderDistributionConfiguration#target_repository}
        :param container_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#container_tags ImagebuilderDistributionConfiguration#container_tags}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_distribution_configuration#description ImagebuilderDistributionConfiguration#description}.
        '''
        value = ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration(
            target_repository=target_repository,
            container_tags=container_tags,
            description=description,
        )

        return typing.cast(None, jsii.invoke(self, "putContainerDistributionConfiguration", [value]))

    @jsii.member(jsii_name="putLaunchTemplateConfiguration")
    def put_launch_template_configuration(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putLaunchTemplateConfiguration", [value]))

    @jsii.member(jsii_name="resetAmiDistributionConfiguration")
    def reset_ami_distribution_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmiDistributionConfiguration", []))

    @jsii.member(jsii_name="resetContainerDistributionConfiguration")
    def reset_container_distribution_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerDistributionConfiguration", []))

    @jsii.member(jsii_name="resetLaunchTemplateConfiguration")
    def reset_launch_template_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchTemplateConfiguration", []))

    @jsii.member(jsii_name="resetLicenseConfigurationArns")
    def reset_license_configuration_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseConfigurationArns", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiDistributionConfiguration")
    def ami_distribution_configuration(
        self,
    ) -> ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference:
        return typing.cast(ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference, jsii.get(self, "amiDistributionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerDistributionConfiguration")
    def container_distribution_configuration(
        self,
    ) -> ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference:
        return typing.cast(ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference, jsii.get(self, "containerDistributionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateConfiguration")
    def launch_template_configuration(
        self,
    ) -> ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList:
        return typing.cast(ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList, jsii.get(self, "launchTemplateConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiDistributionConfigurationInput")
    def ami_distribution_configuration_input(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration], jsii.get(self, "amiDistributionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerDistributionConfigurationInput")
    def container_distribution_configuration_input(
        self,
    ) -> typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration], jsii.get(self, "containerDistributionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="launchTemplateConfigurationInput")
    def launch_template_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration]]], jsii.get(self, "launchTemplateConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseConfigurationArnsInput")
    def license_configuration_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "licenseConfigurationArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseConfigurationArns")
    def license_configuration_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "licenseConfigurationArns"))

    @license_configuration_arns.setter
    def license_configuration_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "licenseConfigurationArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistribution, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistribution, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderDistributionConfigurationDistribution, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image aws_imagebuilder_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        infrastructure_configuration_arn: builtins.str,
        container_recipe_arn: typing.Optional[builtins.str] = None,
        distribution_configuration_arn: typing.Optional[builtins.str] = None,
        enhanced_image_metadata_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        image_recipe_arn: typing.Optional[builtins.str] = None,
        image_tests_configuration: typing.Optional["ImagebuilderImageImageTestsConfiguration"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["ImagebuilderImageTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image aws_imagebuilder_image} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param infrastructure_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#infrastructure_configuration_arn ImagebuilderImage#infrastructure_configuration_arn}.
        :param container_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#container_recipe_arn ImagebuilderImage#container_recipe_arn}.
        :param distribution_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#distribution_configuration_arn ImagebuilderImage#distribution_configuration_arn}.
        :param enhanced_image_metadata_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#enhanced_image_metadata_enabled ImagebuilderImage#enhanced_image_metadata_enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#id ImagebuilderImage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_recipe_arn ImagebuilderImage#image_recipe_arn}.
        :param image_tests_configuration: image_tests_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_configuration ImagebuilderImage#image_tests_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags ImagebuilderImage#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags_all ImagebuilderImage#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeouts ImagebuilderImage#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderImageConfig(
            infrastructure_configuration_arn=infrastructure_configuration_arn,
            container_recipe_arn=container_recipe_arn,
            distribution_configuration_arn=distribution_configuration_arn,
            enhanced_image_metadata_enabled=enhanced_image_metadata_enabled,
            id=id,
            image_recipe_arn=image_recipe_arn,
            image_tests_configuration=image_tests_configuration,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putImageTestsConfiguration")
    def put_image_tests_configuration(
        self,
        *,
        image_tests_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param image_tests_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_enabled ImagebuilderImage#image_tests_enabled}.
        :param timeout_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeout_minutes ImagebuilderImage#timeout_minutes}.
        '''
        value = ImagebuilderImageImageTestsConfiguration(
            image_tests_enabled=image_tests_enabled, timeout_minutes=timeout_minutes
        )

        return typing.cast(None, jsii.invoke(self, "putImageTestsConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#create ImagebuilderImage#create}.
        '''
        value = ImagebuilderImageTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetContainerRecipeArn")
    def reset_container_recipe_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerRecipeArn", []))

    @jsii.member(jsii_name="resetDistributionConfigurationArn")
    def reset_distribution_configuration_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDistributionConfigurationArn", []))

    @jsii.member(jsii_name="resetEnhancedImageMetadataEnabled")
    def reset_enhanced_image_metadata_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnhancedImageMetadataEnabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImageRecipeArn")
    def reset_image_recipe_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageRecipeArn", []))

    @jsii.member(jsii_name="resetImageTestsConfiguration")
    def reset_image_tests_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageTestsConfiguration", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfiguration")
    def image_tests_configuration(
        self,
    ) -> "ImagebuilderImageImageTestsConfigurationOutputReference":
        return typing.cast("ImagebuilderImageImageTestsConfigurationOutputReference", jsii.get(self, "imageTestsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="osVersion")
    def os_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputResources")
    def output_resources(self) -> "ImagebuilderImageOutputResourcesList":
        return typing.cast("ImagebuilderImageOutputResourcesList", jsii.get(self, "outputResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ImagebuilderImageTimeoutsOutputReference":
        return typing.cast("ImagebuilderImageTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArnInput")
    def container_recipe_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerRecipeArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArnInput")
    def distribution_configuration_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributionConfigurationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabledInput")
    def enhanced_image_metadata_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enhancedImageMetadataEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArnInput")
    def image_recipe_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageRecipeArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfigurationInput")
    def image_tests_configuration_input(
        self,
    ) -> typing.Optional["ImagebuilderImageImageTestsConfiguration"]:
        return typing.cast(typing.Optional["ImagebuilderImageImageTestsConfiguration"], jsii.get(self, "imageTestsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArnInput")
    def infrastructure_configuration_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infrastructureConfigurationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["ImagebuilderImageTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["ImagebuilderImageTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArn")
    def container_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerRecipeArn"))

    @container_recipe_arn.setter
    def container_recipe_arn(self, value: builtins.str) -> None:
        jsii.set(self, "containerRecipeArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArn")
    def distribution_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributionConfigurationArn"))

    @distribution_configuration_arn.setter
    def distribution_configuration_arn(self, value: builtins.str) -> None:
        jsii.set(self, "distributionConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabled")
    def enhanced_image_metadata_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enhancedImageMetadataEnabled"))

    @enhanced_image_metadata_enabled.setter
    def enhanced_image_metadata_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enhancedImageMetadataEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArn")
    def image_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageRecipeArn"))

    @image_recipe_arn.setter
    def image_recipe_arn(self, value: builtins.str) -> None:
        jsii.set(self, "imageRecipeArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @infrastructure_configuration_arn.setter
    def infrastructure_configuration_arn(self, value: builtins.str) -> None:
        jsii.set(self, "infrastructureConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "infrastructure_configuration_arn": "infrastructureConfigurationArn",
        "container_recipe_arn": "containerRecipeArn",
        "distribution_configuration_arn": "distributionConfigurationArn",
        "enhanced_image_metadata_enabled": "enhancedImageMetadataEnabled",
        "id": "id",
        "image_recipe_arn": "imageRecipeArn",
        "image_tests_configuration": "imageTestsConfiguration",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class ImagebuilderImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        infrastructure_configuration_arn: builtins.str,
        container_recipe_arn: typing.Optional[builtins.str] = None,
        distribution_configuration_arn: typing.Optional[builtins.str] = None,
        enhanced_image_metadata_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        image_recipe_arn: typing.Optional[builtins.str] = None,
        image_tests_configuration: typing.Optional["ImagebuilderImageImageTestsConfiguration"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["ImagebuilderImageTimeouts"] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param infrastructure_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#infrastructure_configuration_arn ImagebuilderImage#infrastructure_configuration_arn}.
        :param container_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#container_recipe_arn ImagebuilderImage#container_recipe_arn}.
        :param distribution_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#distribution_configuration_arn ImagebuilderImage#distribution_configuration_arn}.
        :param enhanced_image_metadata_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#enhanced_image_metadata_enabled ImagebuilderImage#enhanced_image_metadata_enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#id ImagebuilderImage#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_recipe_arn ImagebuilderImage#image_recipe_arn}.
        :param image_tests_configuration: image_tests_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_configuration ImagebuilderImage#image_tests_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags ImagebuilderImage#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags_all ImagebuilderImage#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeouts ImagebuilderImage#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(image_tests_configuration, dict):
            image_tests_configuration = ImagebuilderImageImageTestsConfiguration(**image_tests_configuration)
        if isinstance(timeouts, dict):
            timeouts = ImagebuilderImageTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "infrastructure_configuration_arn": infrastructure_configuration_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if container_recipe_arn is not None:
            self._values["container_recipe_arn"] = container_recipe_arn
        if distribution_configuration_arn is not None:
            self._values["distribution_configuration_arn"] = distribution_configuration_arn
        if enhanced_image_metadata_enabled is not None:
            self._values["enhanced_image_metadata_enabled"] = enhanced_image_metadata_enabled
        if id is not None:
            self._values["id"] = id
        if image_recipe_arn is not None:
            self._values["image_recipe_arn"] = image_recipe_arn
        if image_tests_configuration is not None:
            self._values["image_tests_configuration"] = image_tests_configuration
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def infrastructure_configuration_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#infrastructure_configuration_arn ImagebuilderImage#infrastructure_configuration_arn}.'''
        result = self._values.get("infrastructure_configuration_arn")
        assert result is not None, "Required property 'infrastructure_configuration_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_recipe_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#container_recipe_arn ImagebuilderImage#container_recipe_arn}.'''
        result = self._values.get("container_recipe_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def distribution_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#distribution_configuration_arn ImagebuilderImage#distribution_configuration_arn}.'''
        result = self._values.get("distribution_configuration_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enhanced_image_metadata_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#enhanced_image_metadata_enabled ImagebuilderImage#enhanced_image_metadata_enabled}.'''
        result = self._values.get("enhanced_image_metadata_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#id ImagebuilderImage#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_recipe_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_recipe_arn ImagebuilderImage#image_recipe_arn}.'''
        result = self._values.get("image_recipe_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tests_configuration(
        self,
    ) -> typing.Optional["ImagebuilderImageImageTestsConfiguration"]:
        '''image_tests_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_configuration ImagebuilderImage#image_tests_configuration}
        '''
        result = self._values.get("image_tests_configuration")
        return typing.cast(typing.Optional["ImagebuilderImageImageTestsConfiguration"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags ImagebuilderImage#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#tags_all ImagebuilderImage#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ImagebuilderImageTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeouts ImagebuilderImage#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ImagebuilderImageTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageImageTestsConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "image_tests_enabled": "imageTestsEnabled",
        "timeout_minutes": "timeoutMinutes",
    },
)
class ImagebuilderImageImageTestsConfiguration:
    def __init__(
        self,
        *,
        image_tests_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param image_tests_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_enabled ImagebuilderImage#image_tests_enabled}.
        :param timeout_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeout_minutes ImagebuilderImage#timeout_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if image_tests_enabled is not None:
            self._values["image_tests_enabled"] = image_tests_enabled
        if timeout_minutes is not None:
            self._values["timeout_minutes"] = timeout_minutes

    @builtins.property
    def image_tests_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#image_tests_enabled ImagebuilderImage#image_tests_enabled}.'''
        result = self._values.get("image_tests_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#timeout_minutes ImagebuilderImage#timeout_minutes}.'''
        result = self._values.get("timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageImageTestsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageImageTestsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageImageTestsConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetImageTestsEnabled")
    def reset_image_tests_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageTestsEnabled", []))

    @jsii.member(jsii_name="resetTimeoutMinutes")
    def reset_timeout_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutMinutes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsEnabledInput")
    def image_tests_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "imageTestsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutesInput")
    def timeout_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsEnabled")
    def image_tests_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "imageTestsEnabled"))

    @image_tests_enabled.setter
    def image_tests_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "imageTestsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutes")
    def timeout_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutMinutes"))

    @timeout_minutes.setter
    def timeout_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderImageImageTestsConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderImageImageTestsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImageImageTestsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResources",
    jsii_struct_bases=[],
    name_mapping={},
)
class ImagebuilderImageOutputResources:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageOutputResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResourcesAmis",
    jsii_struct_bases=[],
    name_mapping={},
)
class ImagebuilderImageOutputResourcesAmis:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageOutputResourcesAmis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageOutputResourcesAmisList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResourcesAmisList",
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
    ) -> "ImagebuilderImageOutputResourcesAmisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderImageOutputResourcesAmisOutputReference", jsii.invoke(self, "get", [index]))

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


class ImagebuilderImageOutputResourcesAmisOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResourcesAmisOutputReference",
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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ImagebuilderImageOutputResourcesAmis]:
        return typing.cast(typing.Optional[ImagebuilderImageOutputResourcesAmis], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImageOutputResourcesAmis],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageOutputResourcesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResourcesList",
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
    ) -> "ImagebuilderImageOutputResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderImageOutputResourcesOutputReference", jsii.invoke(self, "get", [index]))

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


class ImagebuilderImageOutputResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageOutputResourcesOutputReference",
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
    @jsii.member(jsii_name="amis")
    def amis(self) -> ImagebuilderImageOutputResourcesAmisList:
        return typing.cast(ImagebuilderImageOutputResourcesAmisList, jsii.get(self, "amis"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ImagebuilderImageOutputResources]:
        return typing.cast(typing.Optional[ImagebuilderImageOutputResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImageOutputResources],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImagePipeline(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipeline",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline aws_imagebuilder_image_pipeline}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        infrastructure_configuration_arn: builtins.str,
        name: builtins.str,
        container_recipe_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        distribution_configuration_arn: typing.Optional[builtins.str] = None,
        enhanced_image_metadata_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        image_recipe_arn: typing.Optional[builtins.str] = None,
        image_tests_configuration: typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"] = None,
        schedule: typing.Optional["ImagebuilderImagePipelineSchedule"] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline aws_imagebuilder_image_pipeline} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param infrastructure_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#infrastructure_configuration_arn ImagebuilderImagePipeline#infrastructure_configuration_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#name ImagebuilderImagePipeline#name}.
        :param container_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#container_recipe_arn ImagebuilderImagePipeline#container_recipe_arn}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#description ImagebuilderImagePipeline#description}.
        :param distribution_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#distribution_configuration_arn ImagebuilderImagePipeline#distribution_configuration_arn}.
        :param enhanced_image_metadata_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#enhanced_image_metadata_enabled ImagebuilderImagePipeline#enhanced_image_metadata_enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#id ImagebuilderImagePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_recipe_arn ImagebuilderImagePipeline#image_recipe_arn}.
        :param image_tests_configuration: image_tests_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_configuration ImagebuilderImagePipeline#image_tests_configuration}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule ImagebuilderImagePipeline#schedule}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#status ImagebuilderImagePipeline#status}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags ImagebuilderImagePipeline#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags_all ImagebuilderImagePipeline#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderImagePipelineConfig(
            infrastructure_configuration_arn=infrastructure_configuration_arn,
            name=name,
            container_recipe_arn=container_recipe_arn,
            description=description,
            distribution_configuration_arn=distribution_configuration_arn,
            enhanced_image_metadata_enabled=enhanced_image_metadata_enabled,
            id=id,
            image_recipe_arn=image_recipe_arn,
            image_tests_configuration=image_tests_configuration,
            schedule=schedule,
            status=status,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putImageTestsConfiguration")
    def put_image_tests_configuration(
        self,
        *,
        image_tests_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param image_tests_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_enabled ImagebuilderImagePipeline#image_tests_enabled}.
        :param timeout_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timeout_minutes ImagebuilderImagePipeline#timeout_minutes}.
        '''
        value = ImagebuilderImagePipelineImageTestsConfiguration(
            image_tests_enabled=image_tests_enabled, timeout_minutes=timeout_minutes
        )

        return typing.cast(None, jsii.invoke(self, "putImageTestsConfiguration", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        schedule_expression: builtins.str,
        pipeline_execution_start_condition: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param schedule_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule_expression ImagebuilderImagePipeline#schedule_expression}.
        :param pipeline_execution_start_condition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#pipeline_execution_start_condition ImagebuilderImagePipeline#pipeline_execution_start_condition}.
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timezone ImagebuilderImagePipeline#timezone}.
        '''
        value = ImagebuilderImagePipelineSchedule(
            schedule_expression=schedule_expression,
            pipeline_execution_start_condition=pipeline_execution_start_condition,
            timezone=timezone,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetContainerRecipeArn")
    def reset_container_recipe_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerRecipeArn", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDistributionConfigurationArn")
    def reset_distribution_configuration_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDistributionConfigurationArn", []))

    @jsii.member(jsii_name="resetEnhancedImageMetadataEnabled")
    def reset_enhanced_image_metadata_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnhancedImageMetadataEnabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImageRecipeArn")
    def reset_image_recipe_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageRecipeArn", []))

    @jsii.member(jsii_name="resetImageTestsConfiguration")
    def reset_image_tests_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageTestsConfiguration", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateLastRun")
    def date_last_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateLastRun"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateNextRun")
    def date_next_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateNextRun"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfiguration")
    def image_tests_configuration(
        self,
    ) -> "ImagebuilderImagePipelineImageTestsConfigurationOutputReference":
        return typing.cast("ImagebuilderImagePipelineImageTestsConfigurationOutputReference", jsii.get(self, "imageTestsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "ImagebuilderImagePipelineScheduleOutputReference":
        return typing.cast("ImagebuilderImagePipelineScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArnInput")
    def container_recipe_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerRecipeArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArnInput")
    def distribution_configuration_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributionConfigurationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabledInput")
    def enhanced_image_metadata_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enhancedImageMetadataEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArnInput")
    def image_recipe_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageRecipeArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsConfigurationInput")
    def image_tests_configuration_input(
        self,
    ) -> typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"]:
        return typing.cast(typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"], jsii.get(self, "imageTestsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArnInput")
    def infrastructure_configuration_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infrastructureConfigurationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["ImagebuilderImagePipelineSchedule"]:
        return typing.cast(typing.Optional["ImagebuilderImagePipelineSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerRecipeArn")
    def container_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerRecipeArn"))

    @container_recipe_arn.setter
    def container_recipe_arn(self, value: builtins.str) -> None:
        jsii.set(self, "containerRecipeArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionConfigurationArn")
    def distribution_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributionConfigurationArn"))

    @distribution_configuration_arn.setter
    def distribution_configuration_arn(self, value: builtins.str) -> None:
        jsii.set(self, "distributionConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedImageMetadataEnabled")
    def enhanced_image_metadata_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enhancedImageMetadataEnabled"))

    @enhanced_image_metadata_enabled.setter
    def enhanced_image_metadata_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enhancedImageMetadataEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageRecipeArn")
    def image_recipe_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageRecipeArn"))

    @image_recipe_arn.setter
    def image_recipe_arn(self, value: builtins.str) -> None:
        jsii.set(self, "imageRecipeArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @infrastructure_configuration_arn.setter
    def infrastructure_configuration_arn(self, value: builtins.str) -> None:
        jsii.set(self, "infrastructureConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipelineConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "infrastructure_configuration_arn": "infrastructureConfigurationArn",
        "name": "name",
        "container_recipe_arn": "containerRecipeArn",
        "description": "description",
        "distribution_configuration_arn": "distributionConfigurationArn",
        "enhanced_image_metadata_enabled": "enhancedImageMetadataEnabled",
        "id": "id",
        "image_recipe_arn": "imageRecipeArn",
        "image_tests_configuration": "imageTestsConfiguration",
        "schedule": "schedule",
        "status": "status",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ImagebuilderImagePipelineConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        infrastructure_configuration_arn: builtins.str,
        name: builtins.str,
        container_recipe_arn: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        distribution_configuration_arn: typing.Optional[builtins.str] = None,
        enhanced_image_metadata_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        image_recipe_arn: typing.Optional[builtins.str] = None,
        image_tests_configuration: typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"] = None,
        schedule: typing.Optional["ImagebuilderImagePipelineSchedule"] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param infrastructure_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#infrastructure_configuration_arn ImagebuilderImagePipeline#infrastructure_configuration_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#name ImagebuilderImagePipeline#name}.
        :param container_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#container_recipe_arn ImagebuilderImagePipeline#container_recipe_arn}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#description ImagebuilderImagePipeline#description}.
        :param distribution_configuration_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#distribution_configuration_arn ImagebuilderImagePipeline#distribution_configuration_arn}.
        :param enhanced_image_metadata_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#enhanced_image_metadata_enabled ImagebuilderImagePipeline#enhanced_image_metadata_enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#id ImagebuilderImagePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_recipe_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_recipe_arn ImagebuilderImagePipeline#image_recipe_arn}.
        :param image_tests_configuration: image_tests_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_configuration ImagebuilderImagePipeline#image_tests_configuration}
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule ImagebuilderImagePipeline#schedule}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#status ImagebuilderImagePipeline#status}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags ImagebuilderImagePipeline#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags_all ImagebuilderImagePipeline#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(image_tests_configuration, dict):
            image_tests_configuration = ImagebuilderImagePipelineImageTestsConfiguration(**image_tests_configuration)
        if isinstance(schedule, dict):
            schedule = ImagebuilderImagePipelineSchedule(**schedule)
        self._values: typing.Dict[str, typing.Any] = {
            "infrastructure_configuration_arn": infrastructure_configuration_arn,
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
        if container_recipe_arn is not None:
            self._values["container_recipe_arn"] = container_recipe_arn
        if description is not None:
            self._values["description"] = description
        if distribution_configuration_arn is not None:
            self._values["distribution_configuration_arn"] = distribution_configuration_arn
        if enhanced_image_metadata_enabled is not None:
            self._values["enhanced_image_metadata_enabled"] = enhanced_image_metadata_enabled
        if id is not None:
            self._values["id"] = id
        if image_recipe_arn is not None:
            self._values["image_recipe_arn"] = image_recipe_arn
        if image_tests_configuration is not None:
            self._values["image_tests_configuration"] = image_tests_configuration
        if schedule is not None:
            self._values["schedule"] = schedule
        if status is not None:
            self._values["status"] = status
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def infrastructure_configuration_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#infrastructure_configuration_arn ImagebuilderImagePipeline#infrastructure_configuration_arn}.'''
        result = self._values.get("infrastructure_configuration_arn")
        assert result is not None, "Required property 'infrastructure_configuration_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#name ImagebuilderImagePipeline#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_recipe_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#container_recipe_arn ImagebuilderImagePipeline#container_recipe_arn}.'''
        result = self._values.get("container_recipe_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#description ImagebuilderImagePipeline#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def distribution_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#distribution_configuration_arn ImagebuilderImagePipeline#distribution_configuration_arn}.'''
        result = self._values.get("distribution_configuration_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enhanced_image_metadata_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#enhanced_image_metadata_enabled ImagebuilderImagePipeline#enhanced_image_metadata_enabled}.'''
        result = self._values.get("enhanced_image_metadata_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#id ImagebuilderImagePipeline#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_recipe_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_recipe_arn ImagebuilderImagePipeline#image_recipe_arn}.'''
        result = self._values.get("image_recipe_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tests_configuration(
        self,
    ) -> typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"]:
        '''image_tests_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_configuration ImagebuilderImagePipeline#image_tests_configuration}
        '''
        result = self._values.get("image_tests_configuration")
        return typing.cast(typing.Optional["ImagebuilderImagePipelineImageTestsConfiguration"], result)

    @builtins.property
    def schedule(self) -> typing.Optional["ImagebuilderImagePipelineSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule ImagebuilderImagePipeline#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["ImagebuilderImagePipelineSchedule"], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#status ImagebuilderImagePipeline#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags ImagebuilderImagePipeline#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#tags_all ImagebuilderImagePipeline#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImagePipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipelineImageTestsConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "image_tests_enabled": "imageTestsEnabled",
        "timeout_minutes": "timeoutMinutes",
    },
)
class ImagebuilderImagePipelineImageTestsConfiguration:
    def __init__(
        self,
        *,
        image_tests_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param image_tests_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_enabled ImagebuilderImagePipeline#image_tests_enabled}.
        :param timeout_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timeout_minutes ImagebuilderImagePipeline#timeout_minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if image_tests_enabled is not None:
            self._values["image_tests_enabled"] = image_tests_enabled
        if timeout_minutes is not None:
            self._values["timeout_minutes"] = timeout_minutes

    @builtins.property
    def image_tests_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#image_tests_enabled ImagebuilderImagePipeline#image_tests_enabled}.'''
        result = self._values.get("image_tests_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timeout_minutes ImagebuilderImagePipeline#timeout_minutes}.'''
        result = self._values.get("timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImagePipelineImageTestsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImagePipelineImageTestsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipelineImageTestsConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetImageTestsEnabled")
    def reset_image_tests_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageTestsEnabled", []))

    @jsii.member(jsii_name="resetTimeoutMinutes")
    def reset_timeout_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutMinutes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsEnabledInput")
    def image_tests_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "imageTestsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutesInput")
    def timeout_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageTestsEnabled")
    def image_tests_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "imageTestsEnabled"))

    @image_tests_enabled.setter
    def image_tests_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "imageTestsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutMinutes")
    def timeout_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutMinutes"))

    @timeout_minutes.setter
    def timeout_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderImagePipelineImageTestsConfiguration]:
        return typing.cast(typing.Optional[ImagebuilderImagePipelineImageTestsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImagePipelineImageTestsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipelineSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "schedule_expression": "scheduleExpression",
        "pipeline_execution_start_condition": "pipelineExecutionStartCondition",
        "timezone": "timezone",
    },
)
class ImagebuilderImagePipelineSchedule:
    def __init__(
        self,
        *,
        schedule_expression: builtins.str,
        pipeline_execution_start_condition: typing.Optional[builtins.str] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param schedule_expression: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule_expression ImagebuilderImagePipeline#schedule_expression}.
        :param pipeline_execution_start_condition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#pipeline_execution_start_condition ImagebuilderImagePipeline#pipeline_execution_start_condition}.
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timezone ImagebuilderImagePipeline#timezone}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "schedule_expression": schedule_expression,
        }
        if pipeline_execution_start_condition is not None:
            self._values["pipeline_execution_start_condition"] = pipeline_execution_start_condition
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def schedule_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#schedule_expression ImagebuilderImagePipeline#schedule_expression}.'''
        result = self._values.get("schedule_expression")
        assert result is not None, "Required property 'schedule_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline_execution_start_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#pipeline_execution_start_condition ImagebuilderImagePipeline#pipeline_execution_start_condition}.'''
        result = self._values.get("pipeline_execution_start_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_pipeline#timezone ImagebuilderImagePipeline#timezone}.'''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImagePipelineSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImagePipelineScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImagePipelineScheduleOutputReference",
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

    @jsii.member(jsii_name="resetPipelineExecutionStartCondition")
    def reset_pipeline_execution_start_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineExecutionStartCondition", []))

    @jsii.member(jsii_name="resetTimezone")
    def reset_timezone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezone", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineExecutionStartConditionInput")
    def pipeline_execution_start_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineExecutionStartConditionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleExpressionInput")
    def schedule_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduleExpressionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezoneInput")
    def timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineExecutionStartCondition")
    def pipeline_execution_start_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineExecutionStartCondition"))

    @pipeline_execution_start_condition.setter
    def pipeline_execution_start_condition(self, value: builtins.str) -> None:
        jsii.set(self, "pipelineExecutionStartCondition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleExpression")
    def schedule_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheduleExpression"))

    @schedule_expression.setter
    def schedule_expression(self, value: builtins.str) -> None:
        jsii.set(self, "scheduleExpression", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: builtins.str) -> None:
        jsii.set(self, "timezone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ImagebuilderImagePipelineSchedule]:
        return typing.cast(typing.Optional[ImagebuilderImagePipelineSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImagePipelineSchedule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageRecipe(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipe",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe aws_imagebuilder_image_recipe}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        component: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeComponent"]],
        name: builtins.str,
        parent_image: builtins.str,
        version: builtins.str,
        block_device_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeBlockDeviceMapping"]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        systems_manager_agent: typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        user_data_base64: typing.Optional[builtins.str] = None,
        working_directory: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe aws_imagebuilder_image_recipe} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param component: component block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#component ImagebuilderImageRecipe#component}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#name ImagebuilderImageRecipe#name}.
        :param parent_image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#parent_image ImagebuilderImageRecipe#parent_image}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#version ImagebuilderImageRecipe#version}.
        :param block_device_mapping: block_device_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#block_device_mapping ImagebuilderImageRecipe#block_device_mapping}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#description ImagebuilderImageRecipe#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#id ImagebuilderImageRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param systems_manager_agent: systems_manager_agent block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#systems_manager_agent ImagebuilderImageRecipe#systems_manager_agent}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags ImagebuilderImageRecipe#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags_all ImagebuilderImageRecipe#tags_all}.
        :param user_data_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#user_data_base64 ImagebuilderImageRecipe#user_data_base64}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#working_directory ImagebuilderImageRecipe#working_directory}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderImageRecipeConfig(
            component=component,
            name=name,
            parent_image=parent_image,
            version=version,
            block_device_mapping=block_device_mapping,
            description=description,
            id=id,
            systems_manager_agent=systems_manager_agent,
            tags=tags,
            tags_all=tags_all,
            user_data_base64=user_data_base64,
            working_directory=working_directory,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putBlockDeviceMapping")
    def put_block_device_mapping(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeBlockDeviceMapping"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putBlockDeviceMapping", [value]))

    @jsii.member(jsii_name="putComponent")
    def put_component(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeComponent"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putComponent", [value]))

    @jsii.member(jsii_name="putSystemsManagerAgent")
    def put_systems_manager_agent(
        self,
        *,
        uninstall_after_build: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param uninstall_after_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#uninstall_after_build ImagebuilderImageRecipe#uninstall_after_build}.
        '''
        value = ImagebuilderImageRecipeSystemsManagerAgent(
            uninstall_after_build=uninstall_after_build
        )

        return typing.cast(None, jsii.invoke(self, "putSystemsManagerAgent", [value]))

    @jsii.member(jsii_name="resetBlockDeviceMapping")
    def reset_block_device_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockDeviceMapping", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSystemsManagerAgent")
    def reset_systems_manager_agent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemsManagerAgent", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserDataBase64")
    def reset_user_data_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDataBase64", []))

    @jsii.member(jsii_name="resetWorkingDirectory")
    def reset_working_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDirectory", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockDeviceMapping")
    def block_device_mapping(self) -> "ImagebuilderImageRecipeBlockDeviceMappingList":
        return typing.cast("ImagebuilderImageRecipeBlockDeviceMappingList", jsii.get(self, "blockDeviceMapping"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="component")
    def component(self) -> "ImagebuilderImageRecipeComponentList":
        return typing.cast("ImagebuilderImageRecipeComponentList", jsii.get(self, "component"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemsManagerAgent")
    def systems_manager_agent(
        self,
    ) -> "ImagebuilderImageRecipeSystemsManagerAgentOutputReference":
        return typing.cast("ImagebuilderImageRecipeSystemsManagerAgentOutputReference", jsii.get(self, "systemsManagerAgent"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockDeviceMappingInput")
    def block_device_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeBlockDeviceMapping"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeBlockDeviceMapping"]]], jsii.get(self, "blockDeviceMappingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentInput")
    def component_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponent"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponent"]]], jsii.get(self, "componentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImageInput")
    def parent_image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentImageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemsManagerAgentInput")
    def systems_manager_agent_input(
        self,
    ) -> typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"]:
        return typing.cast(typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"], jsii.get(self, "systemsManagerAgentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataBase64Input")
    def user_data_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataBase64Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectoryInput")
    def working_directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentImage")
    def parent_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentImage"))

    @parent_image.setter
    def parent_image(self, value: builtins.str) -> None:
        jsii.set(self, "parentImage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataBase64")
    def user_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDataBase64"))

    @user_data_base64.setter
    def user_data_base64(self, value: builtins.str) -> None:
        jsii.set(self, "userDataBase64", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirectory")
    def working_directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDirectory"))

    @working_directory.setter
    def working_directory(self, value: builtins.str) -> None:
        jsii.set(self, "workingDirectory", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeBlockDeviceMapping",
    jsii_struct_bases=[],
    name_mapping={
        "device_name": "deviceName",
        "ebs": "ebs",
        "no_device": "noDevice",
        "virtual_name": "virtualName",
    },
)
class ImagebuilderImageRecipeBlockDeviceMapping:
    def __init__(
        self,
        *,
        device_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional["ImagebuilderImageRecipeBlockDeviceMappingEbs"] = None,
        no_device: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        virtual_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#device_name ImagebuilderImageRecipe#device_name}.
        :param ebs: ebs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#ebs ImagebuilderImageRecipe#ebs}
        :param no_device: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#no_device ImagebuilderImageRecipe#no_device}.
        :param virtual_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#virtual_name ImagebuilderImageRecipe#virtual_name}.
        '''
        if isinstance(ebs, dict):
            ebs = ImagebuilderImageRecipeBlockDeviceMappingEbs(**ebs)
        self._values: typing.Dict[str, typing.Any] = {}
        if device_name is not None:
            self._values["device_name"] = device_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if no_device is not None:
            self._values["no_device"] = no_device
        if virtual_name is not None:
            self._values["virtual_name"] = virtual_name

    @builtins.property
    def device_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#device_name ImagebuilderImageRecipe#device_name}.'''
        result = self._values.get("device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(self) -> typing.Optional["ImagebuilderImageRecipeBlockDeviceMappingEbs"]:
        '''ebs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#ebs ImagebuilderImageRecipe#ebs}
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional["ImagebuilderImageRecipeBlockDeviceMappingEbs"], result)

    @builtins.property
    def no_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#no_device ImagebuilderImageRecipe#no_device}.'''
        result = self._values.get("no_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def virtual_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#virtual_name ImagebuilderImageRecipe#virtual_name}.'''
        result = self._values.get("virtual_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeBlockDeviceMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeBlockDeviceMappingEbs",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "encrypted": "encrypted",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "snapshot_id": "snapshotId",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class ImagebuilderImageRecipeBlockDeviceMappingEbs:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#delete_on_termination ImagebuilderImageRecipe#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#encrypted ImagebuilderImageRecipe#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#iops ImagebuilderImageRecipe#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#kms_key_id ImagebuilderImageRecipe#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#snapshot_id ImagebuilderImageRecipe#snapshot_id}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_size ImagebuilderImageRecipe#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_type ImagebuilderImageRecipe#volume_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def delete_on_termination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#delete_on_termination ImagebuilderImageRecipe#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#encrypted ImagebuilderImageRecipe#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#iops ImagebuilderImageRecipe#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#kms_key_id ImagebuilderImageRecipe#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#snapshot_id ImagebuilderImageRecipe#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_size ImagebuilderImageRecipe#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_type ImagebuilderImageRecipe#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeBlockDeviceMappingEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference",
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

    @jsii.member(jsii_name="resetDeleteOnTermination")
    def reset_delete_on_termination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteOnTermination", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

    @jsii.member(jsii_name="resetVolumeSize")
    def reset_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeSize", []))

    @jsii.member(jsii_name="resetVolumeType")
    def reset_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteOnTerminationInput")
    def delete_on_termination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteOnTerminationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInput")
    def volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteOnTermination"))

    @delete_on_termination.setter
    def delete_on_termination(self, value: builtins.str) -> None:
        jsii.set(self, "deleteOnTermination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: builtins.str) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        jsii.set(self, "iops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @volume_size.setter
    def volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "volumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        jsii.set(self, "volumeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderImageRecipeBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[ImagebuilderImageRecipeBlockDeviceMappingEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImageRecipeBlockDeviceMappingEbs],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageRecipeBlockDeviceMappingList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeBlockDeviceMappingList",
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
    ) -> "ImagebuilderImageRecipeBlockDeviceMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderImageRecipeBlockDeviceMappingOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeBlockDeviceMapping]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeBlockDeviceMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeBlockDeviceMapping]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageRecipeBlockDeviceMappingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeBlockDeviceMappingOutputReference",
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

    @jsii.member(jsii_name="putEbs")
    def put_ebs(
        self,
        *,
        delete_on_termination: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#delete_on_termination ImagebuilderImageRecipe#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#encrypted ImagebuilderImageRecipe#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#iops ImagebuilderImageRecipe#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#kms_key_id ImagebuilderImageRecipe#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#snapshot_id ImagebuilderImageRecipe#snapshot_id}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_size ImagebuilderImageRecipe#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#volume_type ImagebuilderImageRecipe#volume_type}.
        '''
        value = ImagebuilderImageRecipeBlockDeviceMappingEbs(
            delete_on_termination=delete_on_termination,
            encrypted=encrypted,
            iops=iops,
            kms_key_id=kms_key_id,
            snapshot_id=snapshot_id,
            volume_size=volume_size,
            volume_type=volume_type,
        )

        return typing.cast(None, jsii.invoke(self, "putEbs", [value]))

    @jsii.member(jsii_name="resetDeviceName")
    def reset_device_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceName", []))

    @jsii.member(jsii_name="resetEbs")
    def reset_ebs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbs", []))

    @jsii.member(jsii_name="resetNoDevice")
    def reset_no_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoDevice", []))

    @jsii.member(jsii_name="resetVirtualName")
    def reset_virtual_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebs")
    def ebs(self) -> ImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference:
        return typing.cast(ImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference, jsii.get(self, "ebs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceNameInput")
    def device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsInput")
    def ebs_input(
        self,
    ) -> typing.Optional[ImagebuilderImageRecipeBlockDeviceMappingEbs]:
        return typing.cast(typing.Optional[ImagebuilderImageRecipeBlockDeviceMappingEbs], jsii.get(self, "ebsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDeviceInput")
    def no_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualNameInput")
    def virtual_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @device_name.setter
    def device_name(self, value: builtins.str) -> None:
        jsii.set(self, "deviceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noDevice")
    def no_device(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noDevice"))

    @no_device.setter
    def no_device(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualName")
    def virtual_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualName"))

    @virtual_name.setter
    def virtual_name(self, value: builtins.str) -> None:
        jsii.set(self, "virtualName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderImageRecipeBlockDeviceMapping, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderImageRecipeBlockDeviceMapping, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderImageRecipeBlockDeviceMapping, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponent",
    jsii_struct_bases=[],
    name_mapping={"component_arn": "componentArn", "parameter": "parameter"},
)
class ImagebuilderImageRecipeComponent:
    def __init__(
        self,
        *,
        component_arn: builtins.str,
        parameter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeComponentParameter"]]] = None,
    ) -> None:
        '''
        :param component_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#component_arn ImagebuilderImageRecipe#component_arn}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#parameter ImagebuilderImageRecipe#parameter}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "component_arn": component_arn,
        }
        if parameter is not None:
            self._values["parameter"] = parameter

    @builtins.property
    def component_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#component_arn ImagebuilderImageRecipe#component_arn}.'''
        result = self._values.get("component_arn")
        assert result is not None, "Required property 'component_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponentParameter"]]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#parameter ImagebuilderImageRecipe#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponentParameter"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeComponent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageRecipeComponentList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponentList",
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
    ) -> "ImagebuilderImageRecipeComponentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderImageRecipeComponentOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponent]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponent]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponent]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageRecipeComponentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponentOutputReference",
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

    @jsii.member(jsii_name="putParameter")
    def put_parameter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["ImagebuilderImageRecipeComponentParameter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putParameter", [value]))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> "ImagebuilderImageRecipeComponentParameterList":
        return typing.cast("ImagebuilderImageRecipeComponentParameterList", jsii.get(self, "parameter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentArnInput")
    def component_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "componentArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponentParameter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["ImagebuilderImageRecipeComponentParameter"]]], jsii.get(self, "parameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="componentArn")
    def component_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "componentArn"))

    @component_arn.setter
    def component_arn(self, value: builtins.str) -> None:
        jsii.set(self, "componentArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderImageRecipeComponent, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderImageRecipeComponent, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderImageRecipeComponent, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponentParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ImagebuilderImageRecipeComponentParameter:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#name ImagebuilderImageRecipe#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#value ImagebuilderImageRecipe#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#name ImagebuilderImageRecipe#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#value ImagebuilderImageRecipe#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeComponentParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageRecipeComponentParameterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponentParameterList",
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
    ) -> "ImagebuilderImageRecipeComponentParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("ImagebuilderImageRecipeComponentParameterOutputReference", jsii.invoke(self, "get", [index]))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponentParameter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponentParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponentParameter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderImageRecipeComponentParameterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeComponentParameterOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderImageRecipeComponentParameter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderImageRecipeComponentParameter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderImageRecipeComponentParameter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "component": "component",
        "name": "name",
        "parent_image": "parentImage",
        "version": "version",
        "block_device_mapping": "blockDeviceMapping",
        "description": "description",
        "id": "id",
        "systems_manager_agent": "systemsManagerAgent",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_data_base64": "userDataBase64",
        "working_directory": "workingDirectory",
    },
)
class ImagebuilderImageRecipeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        component: typing.Union[cdktf.IResolvable, typing.Sequence[ImagebuilderImageRecipeComponent]],
        name: builtins.str,
        parent_image: builtins.str,
        version: builtins.str,
        block_device_mapping: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[ImagebuilderImageRecipeBlockDeviceMapping]]] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        systems_manager_agent: typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        user_data_base64: typing.Optional[builtins.str] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param component: component block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#component ImagebuilderImageRecipe#component}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#name ImagebuilderImageRecipe#name}.
        :param parent_image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#parent_image ImagebuilderImageRecipe#parent_image}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#version ImagebuilderImageRecipe#version}.
        :param block_device_mapping: block_device_mapping block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#block_device_mapping ImagebuilderImageRecipe#block_device_mapping}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#description ImagebuilderImageRecipe#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#id ImagebuilderImageRecipe#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param systems_manager_agent: systems_manager_agent block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#systems_manager_agent ImagebuilderImageRecipe#systems_manager_agent}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags ImagebuilderImageRecipe#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags_all ImagebuilderImageRecipe#tags_all}.
        :param user_data_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#user_data_base64 ImagebuilderImageRecipe#user_data_base64}.
        :param working_directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#working_directory ImagebuilderImageRecipe#working_directory}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(systems_manager_agent, dict):
            systems_manager_agent = ImagebuilderImageRecipeSystemsManagerAgent(**systems_manager_agent)
        self._values: typing.Dict[str, typing.Any] = {
            "component": component,
            "name": name,
            "parent_image": parent_image,
            "version": version,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if block_device_mapping is not None:
            self._values["block_device_mapping"] = block_device_mapping
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if systems_manager_agent is not None:
            self._values["systems_manager_agent"] = systems_manager_agent
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_data_base64 is not None:
            self._values["user_data_base64"] = user_data_base64
        if working_directory is not None:
            self._values["working_directory"] = working_directory

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
    def component(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponent]]:
        '''component block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#component ImagebuilderImageRecipe#component}
        '''
        result = self._values.get("component")
        assert result is not None, "Required property 'component' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeComponent]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#name ImagebuilderImageRecipe#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_image(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#parent_image ImagebuilderImageRecipe#parent_image}.'''
        result = self._values.get("parent_image")
        assert result is not None, "Required property 'parent_image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#version ImagebuilderImageRecipe#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_device_mapping(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeBlockDeviceMapping]]]:
        '''block_device_mapping block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#block_device_mapping ImagebuilderImageRecipe#block_device_mapping}
        '''
        result = self._values.get("block_device_mapping")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[ImagebuilderImageRecipeBlockDeviceMapping]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#description ImagebuilderImageRecipe#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#id ImagebuilderImageRecipe#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def systems_manager_agent(
        self,
    ) -> typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"]:
        '''systems_manager_agent block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#systems_manager_agent ImagebuilderImageRecipe#systems_manager_agent}
        '''
        result = self._values.get("systems_manager_agent")
        return typing.cast(typing.Optional["ImagebuilderImageRecipeSystemsManagerAgent"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags ImagebuilderImageRecipe#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#tags_all ImagebuilderImageRecipe#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def user_data_base64(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#user_data_base64 ImagebuilderImageRecipe#user_data_base64}.'''
        result = self._values.get("user_data_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#working_directory ImagebuilderImageRecipe#working_directory}.'''
        result = self._values.get("working_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeSystemsManagerAgent",
    jsii_struct_bases=[],
    name_mapping={"uninstall_after_build": "uninstallAfterBuild"},
)
class ImagebuilderImageRecipeSystemsManagerAgent:
    def __init__(
        self,
        *,
        uninstall_after_build: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param uninstall_after_build: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#uninstall_after_build ImagebuilderImageRecipe#uninstall_after_build}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "uninstall_after_build": uninstall_after_build,
        }

    @builtins.property
    def uninstall_after_build(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image_recipe#uninstall_after_build ImagebuilderImageRecipe#uninstall_after_build}.'''
        result = self._values.get("uninstall_after_build")
        assert result is not None, "Required property 'uninstall_after_build' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageRecipeSystemsManagerAgent(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageRecipeSystemsManagerAgentOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageRecipeSystemsManagerAgentOutputReference",
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
    @jsii.member(jsii_name="uninstallAfterBuildInput")
    def uninstall_after_build_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "uninstallAfterBuildInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uninstallAfterBuild")
    def uninstall_after_build(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "uninstallAfterBuild"))

    @uninstall_after_build.setter
    def uninstall_after_build(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "uninstallAfterBuild", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderImageRecipeSystemsManagerAgent]:
        return typing.cast(typing.Optional[ImagebuilderImageRecipeSystemsManagerAgent], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderImageRecipeSystemsManagerAgent],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class ImagebuilderImageTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#create ImagebuilderImage#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_image#create ImagebuilderImage#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderImageTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderImageTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderImageTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[ImagebuilderImageTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[ImagebuilderImageTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[ImagebuilderImageTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ImagebuilderInfrastructureConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration aws_imagebuilder_infrastructure_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        instance_profile_name: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_metadata_options: typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_pair: typing.Optional[builtins.str] = None,
        logging: typing.Optional["ImagebuilderInfrastructureConfigurationLogging"] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        terminate_instance_on_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration aws_imagebuilder_infrastructure_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_profile_name ImagebuilderInfrastructureConfiguration#instance_profile_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#name ImagebuilderInfrastructureConfiguration#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#description ImagebuilderInfrastructureConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#id ImagebuilderInfrastructureConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_metadata_options: instance_metadata_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_metadata_options ImagebuilderInfrastructureConfiguration#instance_metadata_options}
        :param instance_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_types ImagebuilderInfrastructureConfiguration#instance_types}.
        :param key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#key_pair ImagebuilderInfrastructureConfiguration#key_pair}.
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#logging ImagebuilderInfrastructureConfiguration#logging}
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#resource_tags ImagebuilderInfrastructureConfiguration#resource_tags}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#security_group_ids ImagebuilderInfrastructureConfiguration#security_group_ids}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#sns_topic_arn ImagebuilderInfrastructureConfiguration#sns_topic_arn}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#subnet_id ImagebuilderInfrastructureConfiguration#subnet_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags ImagebuilderInfrastructureConfiguration#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags_all ImagebuilderInfrastructureConfiguration#tags_all}.
        :param terminate_instance_on_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#terminate_instance_on_failure ImagebuilderInfrastructureConfiguration#terminate_instance_on_failure}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImagebuilderInfrastructureConfigurationConfig(
            instance_profile_name=instance_profile_name,
            name=name,
            description=description,
            id=id,
            instance_metadata_options=instance_metadata_options,
            instance_types=instance_types,
            key_pair=key_pair,
            logging=logging,
            resource_tags=resource_tags,
            security_group_ids=security_group_ids,
            sns_topic_arn=sns_topic_arn,
            subnet_id=subnet_id,
            tags=tags,
            tags_all=tags_all,
            terminate_instance_on_failure=terminate_instance_on_failure,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putInstanceMetadataOptions")
    def put_instance_metadata_options(
        self,
        *,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_put_response_hop_limit ImagebuilderInfrastructureConfiguration#http_put_response_hop_limit}.
        :param http_tokens: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_tokens ImagebuilderInfrastructureConfiguration#http_tokens}.
        '''
        value = ImagebuilderInfrastructureConfigurationInstanceMetadataOptions(
            http_put_response_hop_limit=http_put_response_hop_limit,
            http_tokens=http_tokens,
        )

        return typing.cast(None, jsii.invoke(self, "putInstanceMetadataOptions", [value]))

    @jsii.member(jsii_name="putLogging")
    def put_logging(
        self,
        *,
        s3_logs: "ImagebuilderInfrastructureConfigurationLoggingS3Logs",
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_logs ImagebuilderInfrastructureConfiguration#s3_logs}
        '''
        value = ImagebuilderInfrastructureConfigurationLogging(s3_logs=s3_logs)

        return typing.cast(None, jsii.invoke(self, "putLogging", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceMetadataOptions")
    def reset_instance_metadata_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceMetadataOptions", []))

    @jsii.member(jsii_name="resetInstanceTypes")
    def reset_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypes", []))

    @jsii.member(jsii_name="resetKeyPair")
    def reset_key_pair(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPair", []))

    @jsii.member(jsii_name="resetLogging")
    def reset_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogging", []))

    @jsii.member(jsii_name="resetResourceTags")
    def reset_resource_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTags", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSnsTopicArn")
    def reset_sns_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsTopicArn", []))

    @jsii.member(jsii_name="resetSubnetId")
    def reset_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTerminateInstanceOnFailure")
    def reset_terminate_instance_on_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminateInstanceOnFailure", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateCreated")
    def date_created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateCreated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateUpdated")
    def date_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateUpdated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceMetadataOptions")
    def instance_metadata_options(
        self,
    ) -> "ImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference":
        return typing.cast("ImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference", jsii.get(self, "instanceMetadataOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logging")
    def logging(
        self,
    ) -> "ImagebuilderInfrastructureConfigurationLoggingOutputReference":
        return typing.cast("ImagebuilderInfrastructureConfigurationLoggingOutputReference", jsii.get(self, "logging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceMetadataOptionsInput")
    def instance_metadata_options_input(
        self,
    ) -> typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"]:
        return typing.cast(typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"], jsii.get(self, "instanceMetadataOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileNameInput")
    def instance_profile_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypesInput")
    def instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairInput")
    def key_pair_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPairInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInput")
    def logging_input(
        self,
    ) -> typing.Optional["ImagebuilderInfrastructureConfigurationLogging"]:
        return typing.cast(typing.Optional["ImagebuilderInfrastructureConfigurationLogging"], jsii.get(self, "loggingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTagsInput")
    def resource_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "resourceTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminateInstanceOnFailureInput")
    def terminate_instance_on_failure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "terminateInstanceOnFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileName")
    def instance_profile_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileName"))

    @instance_profile_name.setter
    def instance_profile_name(self, value: builtins.str) -> None:
        jsii.set(self, "instanceProfileName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "instanceTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPair")
    def key_pair(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyPair"))

    @key_pair.setter
    def key_pair(self, value: builtins.str) -> None:
        jsii.set(self, "keyPair", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTags")
    def resource_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "resourceTags"))

    @resource_tags.setter
    def resource_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "resourceTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "subnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terminateInstanceOnFailure")
    def terminate_instance_on_failure(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "terminateInstanceOnFailure"))

    @terminate_instance_on_failure.setter
    def terminate_instance_on_failure(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "terminateInstanceOnFailure", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_profile_name": "instanceProfileName",
        "name": "name",
        "description": "description",
        "id": "id",
        "instance_metadata_options": "instanceMetadataOptions",
        "instance_types": "instanceTypes",
        "key_pair": "keyPair",
        "logging": "logging",
        "resource_tags": "resourceTags",
        "security_group_ids": "securityGroupIds",
        "sns_topic_arn": "snsTopicArn",
        "subnet_id": "subnetId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "terminate_instance_on_failure": "terminateInstanceOnFailure",
    },
)
class ImagebuilderInfrastructureConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_profile_name: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_metadata_options: typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_pair: typing.Optional[builtins.str] = None,
        logging: typing.Optional["ImagebuilderInfrastructureConfigurationLogging"] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        terminate_instance_on_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Image Builder.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_profile_name ImagebuilderInfrastructureConfiguration#instance_profile_name}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#name ImagebuilderInfrastructureConfiguration#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#description ImagebuilderInfrastructureConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#id ImagebuilderInfrastructureConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_metadata_options: instance_metadata_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_metadata_options ImagebuilderInfrastructureConfiguration#instance_metadata_options}
        :param instance_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_types ImagebuilderInfrastructureConfiguration#instance_types}.
        :param key_pair: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#key_pair ImagebuilderInfrastructureConfiguration#key_pair}.
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#logging ImagebuilderInfrastructureConfiguration#logging}
        :param resource_tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#resource_tags ImagebuilderInfrastructureConfiguration#resource_tags}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#security_group_ids ImagebuilderInfrastructureConfiguration#security_group_ids}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#sns_topic_arn ImagebuilderInfrastructureConfiguration#sns_topic_arn}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#subnet_id ImagebuilderInfrastructureConfiguration#subnet_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags ImagebuilderInfrastructureConfiguration#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags_all ImagebuilderInfrastructureConfiguration#tags_all}.
        :param terminate_instance_on_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#terminate_instance_on_failure ImagebuilderInfrastructureConfiguration#terminate_instance_on_failure}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(instance_metadata_options, dict):
            instance_metadata_options = ImagebuilderInfrastructureConfigurationInstanceMetadataOptions(**instance_metadata_options)
        if isinstance(logging, dict):
            logging = ImagebuilderInfrastructureConfigurationLogging(**logging)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_profile_name": instance_profile_name,
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
        if id is not None:
            self._values["id"] = id
        if instance_metadata_options is not None:
            self._values["instance_metadata_options"] = instance_metadata_options
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if logging is not None:
            self._values["logging"] = logging
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if sns_topic_arn is not None:
            self._values["sns_topic_arn"] = sns_topic_arn
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if terminate_instance_on_failure is not None:
            self._values["terminate_instance_on_failure"] = terminate_instance_on_failure

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
    def instance_profile_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_profile_name ImagebuilderInfrastructureConfiguration#instance_profile_name}.'''
        result = self._values.get("instance_profile_name")
        assert result is not None, "Required property 'instance_profile_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#name ImagebuilderInfrastructureConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#description ImagebuilderInfrastructureConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#id ImagebuilderInfrastructureConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_metadata_options(
        self,
    ) -> typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"]:
        '''instance_metadata_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_metadata_options ImagebuilderInfrastructureConfiguration#instance_metadata_options}
        '''
        result = self._values.get("instance_metadata_options")
        return typing.cast(typing.Optional["ImagebuilderInfrastructureConfigurationInstanceMetadataOptions"], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#instance_types ImagebuilderInfrastructureConfiguration#instance_types}.'''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#key_pair ImagebuilderInfrastructureConfiguration#key_pair}.'''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging(
        self,
    ) -> typing.Optional["ImagebuilderInfrastructureConfigurationLogging"]:
        '''logging block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#logging ImagebuilderInfrastructureConfiguration#logging}
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional["ImagebuilderInfrastructureConfigurationLogging"], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#resource_tags ImagebuilderInfrastructureConfiguration#resource_tags}.'''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#security_group_ids ImagebuilderInfrastructureConfiguration#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#sns_topic_arn ImagebuilderInfrastructureConfiguration#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#subnet_id ImagebuilderInfrastructureConfiguration#subnet_id}.'''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags ImagebuilderInfrastructureConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#tags_all ImagebuilderInfrastructureConfiguration#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def terminate_instance_on_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#terminate_instance_on_failure ImagebuilderInfrastructureConfiguration#terminate_instance_on_failure}.'''
        result = self._values.get("terminate_instance_on_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderInfrastructureConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationInstanceMetadataOptions",
    jsii_struct_bases=[],
    name_mapping={
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
        "http_tokens": "httpTokens",
    },
)
class ImagebuilderInfrastructureConfigurationInstanceMetadataOptions:
    def __init__(
        self,
        *,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_put_response_hop_limit ImagebuilderInfrastructureConfiguration#http_put_response_hop_limit}.
        :param http_tokens: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_tokens ImagebuilderInfrastructureConfiguration#http_tokens}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit
        if http_tokens is not None:
            self._values["http_tokens"] = http_tokens

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_put_response_hop_limit ImagebuilderInfrastructureConfiguration#http_put_response_hop_limit}.'''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_tokens(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#http_tokens ImagebuilderInfrastructureConfiguration#http_tokens}.'''
        result = self._values.get("http_tokens")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderInfrastructureConfigurationInstanceMetadataOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference",
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

    @jsii.member(jsii_name="resetHttpPutResponseHopLimit")
    def reset_http_put_response_hop_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpPutResponseHopLimit", []))

    @jsii.member(jsii_name="resetHttpTokens")
    def reset_http_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpTokens", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpPutResponseHopLimitInput")
    def http_put_response_hop_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpPutResponseHopLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpTokensInput")
    def http_tokens_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpTokensInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpPutResponseHopLimit")
    def http_put_response_hop_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpPutResponseHopLimit"))

    @http_put_response_hop_limit.setter
    def http_put_response_hop_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "httpPutResponseHopLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpTokens")
    def http_tokens(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpTokens"))

    @http_tokens.setter
    def http_tokens(self, value: builtins.str) -> None:
        jsii.set(self, "httpTokens", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderInfrastructureConfigurationInstanceMetadataOptions]:
        return typing.cast(typing.Optional[ImagebuilderInfrastructureConfigurationInstanceMetadataOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderInfrastructureConfigurationInstanceMetadataOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationLogging",
    jsii_struct_bases=[],
    name_mapping={"s3_logs": "s3Logs"},
)
class ImagebuilderInfrastructureConfigurationLogging:
    def __init__(
        self,
        *,
        s3_logs: "ImagebuilderInfrastructureConfigurationLoggingS3Logs",
    ) -> None:
        '''
        :param s3_logs: s3_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_logs ImagebuilderInfrastructureConfiguration#s3_logs}
        '''
        if isinstance(s3_logs, dict):
            s3_logs = ImagebuilderInfrastructureConfigurationLoggingS3Logs(**s3_logs)
        self._values: typing.Dict[str, typing.Any] = {
            "s3_logs": s3_logs,
        }

    @builtins.property
    def s3_logs(self) -> "ImagebuilderInfrastructureConfigurationLoggingS3Logs":
        '''s3_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_logs ImagebuilderInfrastructureConfiguration#s3_logs}
        '''
        result = self._values.get("s3_logs")
        assert result is not None, "Required property 's3_logs' is missing"
        return typing.cast("ImagebuilderInfrastructureConfigurationLoggingS3Logs", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderInfrastructureConfigurationLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderInfrastructureConfigurationLoggingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationLoggingOutputReference",
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

    @jsii.member(jsii_name="putS3Logs")
    def put_s3_logs(
        self,
        *,
        s3_bucket_name: builtins.str,
        s3_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_bucket_name ImagebuilderInfrastructureConfiguration#s3_bucket_name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_key_prefix ImagebuilderInfrastructureConfiguration#s3_key_prefix}.
        '''
        value = ImagebuilderInfrastructureConfigurationLoggingS3Logs(
            s3_bucket_name=s3_bucket_name, s3_key_prefix=s3_key_prefix
        )

        return typing.cast(None, jsii.invoke(self, "putS3Logs", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Logs")
    def s3_logs(
        self,
    ) -> "ImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference":
        return typing.cast("ImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference", jsii.get(self, "s3Logs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LogsInput")
    def s3_logs_input(
        self,
    ) -> typing.Optional["ImagebuilderInfrastructureConfigurationLoggingS3Logs"]:
        return typing.cast(typing.Optional["ImagebuilderInfrastructureConfigurationLoggingS3Logs"], jsii.get(self, "s3LogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderInfrastructureConfigurationLogging]:
        return typing.cast(typing.Optional[ImagebuilderInfrastructureConfigurationLogging], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderInfrastructureConfigurationLogging],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationLoggingS3Logs",
    jsii_struct_bases=[],
    name_mapping={"s3_bucket_name": "s3BucketName", "s3_key_prefix": "s3KeyPrefix"},
)
class ImagebuilderInfrastructureConfigurationLoggingS3Logs:
    def __init__(
        self,
        *,
        s3_bucket_name: builtins.str,
        s3_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param s3_bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_bucket_name ImagebuilderInfrastructureConfiguration#s3_bucket_name}.
        :param s3_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_key_prefix ImagebuilderInfrastructureConfiguration#s3_key_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "s3_bucket_name": s3_bucket_name,
        }
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix

    @builtins.property
    def s3_bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_bucket_name ImagebuilderInfrastructureConfiguration#s3_bucket_name}.'''
        result = self._values.get("s3_bucket_name")
        assert result is not None, "Required property 's3_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/imagebuilder_infrastructure_configuration#s3_key_prefix ImagebuilderInfrastructureConfiguration#s3_key_prefix}.'''
        result = self._values.get("s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagebuilderInfrastructureConfigurationLoggingS3Logs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.imagebuilder.ImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference",
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

    @jsii.member(jsii_name="resetS3KeyPrefix")
    def reset_s3_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3KeyPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketNameInput")
    def s3_bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3BucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefixInput")
    def s3_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "s3KeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3BucketName"))

    @s3_bucket_name.setter
    def s3_bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "s3BucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3KeyPrefix"))

    @s3_key_prefix.setter
    def s3_key_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "s3KeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ImagebuilderInfrastructureConfigurationLoggingS3Logs]:
        return typing.cast(typing.Optional[ImagebuilderInfrastructureConfigurationLoggingS3Logs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ImagebuilderInfrastructureConfigurationLoggingS3Logs],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsImagebuilderComponent",
    "DataAwsImagebuilderComponentConfig",
    "DataAwsImagebuilderComponents",
    "DataAwsImagebuilderComponentsConfig",
    "DataAwsImagebuilderComponentsFilter",
    "DataAwsImagebuilderComponentsFilterList",
    "DataAwsImagebuilderComponentsFilterOutputReference",
    "DataAwsImagebuilderContainerRecipe",
    "DataAwsImagebuilderContainerRecipeComponent",
    "DataAwsImagebuilderContainerRecipeComponentList",
    "DataAwsImagebuilderContainerRecipeComponentOutputReference",
    "DataAwsImagebuilderContainerRecipeComponentParameter",
    "DataAwsImagebuilderContainerRecipeComponentParameterList",
    "DataAwsImagebuilderContainerRecipeComponentParameterOutputReference",
    "DataAwsImagebuilderContainerRecipeConfig",
    "DataAwsImagebuilderContainerRecipeInstanceConfiguration",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsList",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationList",
    "DataAwsImagebuilderContainerRecipeInstanceConfigurationOutputReference",
    "DataAwsImagebuilderContainerRecipeTargetRepository",
    "DataAwsImagebuilderContainerRecipeTargetRepositoryList",
    "DataAwsImagebuilderContainerRecipeTargetRepositoryOutputReference",
    "DataAwsImagebuilderContainerRecipes",
    "DataAwsImagebuilderContainerRecipesConfig",
    "DataAwsImagebuilderContainerRecipesFilter",
    "DataAwsImagebuilderContainerRecipesFilterList",
    "DataAwsImagebuilderContainerRecipesFilterOutputReference",
    "DataAwsImagebuilderDistributionConfiguration",
    "DataAwsImagebuilderDistributionConfigurationConfig",
    "DataAwsImagebuilderDistributionConfigurationDistribution",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionList",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationList",
    "DataAwsImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationList",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryList",
    "DataAwsImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference",
    "DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration",
    "DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList",
    "DataAwsImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference",
    "DataAwsImagebuilderDistributionConfigurationDistributionList",
    "DataAwsImagebuilderDistributionConfigurationDistributionOutputReference",
    "DataAwsImagebuilderDistributionConfigurations",
    "DataAwsImagebuilderDistributionConfigurationsConfig",
    "DataAwsImagebuilderDistributionConfigurationsFilter",
    "DataAwsImagebuilderDistributionConfigurationsFilterList",
    "DataAwsImagebuilderDistributionConfigurationsFilterOutputReference",
    "DataAwsImagebuilderImage",
    "DataAwsImagebuilderImageConfig",
    "DataAwsImagebuilderImageImageTestsConfiguration",
    "DataAwsImagebuilderImageImageTestsConfigurationList",
    "DataAwsImagebuilderImageImageTestsConfigurationOutputReference",
    "DataAwsImagebuilderImageOutputResources",
    "DataAwsImagebuilderImageOutputResourcesAmis",
    "DataAwsImagebuilderImageOutputResourcesAmisList",
    "DataAwsImagebuilderImageOutputResourcesAmisOutputReference",
    "DataAwsImagebuilderImageOutputResourcesList",
    "DataAwsImagebuilderImageOutputResourcesOutputReference",
    "DataAwsImagebuilderImagePipeline",
    "DataAwsImagebuilderImagePipelineConfig",
    "DataAwsImagebuilderImagePipelineImageTestsConfiguration",
    "DataAwsImagebuilderImagePipelineImageTestsConfigurationList",
    "DataAwsImagebuilderImagePipelineImageTestsConfigurationOutputReference",
    "DataAwsImagebuilderImagePipelineSchedule",
    "DataAwsImagebuilderImagePipelineScheduleList",
    "DataAwsImagebuilderImagePipelineScheduleOutputReference",
    "DataAwsImagebuilderImagePipelines",
    "DataAwsImagebuilderImagePipelinesConfig",
    "DataAwsImagebuilderImagePipelinesFilter",
    "DataAwsImagebuilderImagePipelinesFilterList",
    "DataAwsImagebuilderImagePipelinesFilterOutputReference",
    "DataAwsImagebuilderImageRecipe",
    "DataAwsImagebuilderImageRecipeBlockDeviceMapping",
    "DataAwsImagebuilderImageRecipeBlockDeviceMappingEbs",
    "DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsList",
    "DataAwsImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference",
    "DataAwsImagebuilderImageRecipeBlockDeviceMappingList",
    "DataAwsImagebuilderImageRecipeBlockDeviceMappingOutputReference",
    "DataAwsImagebuilderImageRecipeComponent",
    "DataAwsImagebuilderImageRecipeComponentList",
    "DataAwsImagebuilderImageRecipeComponentOutputReference",
    "DataAwsImagebuilderImageRecipeComponentParameter",
    "DataAwsImagebuilderImageRecipeComponentParameterList",
    "DataAwsImagebuilderImageRecipeComponentParameterOutputReference",
    "DataAwsImagebuilderImageRecipeConfig",
    "DataAwsImagebuilderImageRecipes",
    "DataAwsImagebuilderImageRecipesConfig",
    "DataAwsImagebuilderImageRecipesFilter",
    "DataAwsImagebuilderImageRecipesFilterList",
    "DataAwsImagebuilderImageRecipesFilterOutputReference",
    "DataAwsImagebuilderInfrastructureConfiguration",
    "DataAwsImagebuilderInfrastructureConfigurationConfig",
    "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptions",
    "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsList",
    "DataAwsImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference",
    "DataAwsImagebuilderInfrastructureConfigurationLogging",
    "DataAwsImagebuilderInfrastructureConfigurationLoggingList",
    "DataAwsImagebuilderInfrastructureConfigurationLoggingOutputReference",
    "DataAwsImagebuilderInfrastructureConfigurationLoggingS3Logs",
    "DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsList",
    "DataAwsImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference",
    "DataAwsImagebuilderInfrastructureConfigurations",
    "DataAwsImagebuilderInfrastructureConfigurationsConfig",
    "DataAwsImagebuilderInfrastructureConfigurationsFilter",
    "DataAwsImagebuilderInfrastructureConfigurationsFilterList",
    "DataAwsImagebuilderInfrastructureConfigurationsFilterOutputReference",
    "ImagebuilderComponent",
    "ImagebuilderComponentConfig",
    "ImagebuilderContainerRecipe",
    "ImagebuilderContainerRecipeComponent",
    "ImagebuilderContainerRecipeComponentList",
    "ImagebuilderContainerRecipeComponentOutputReference",
    "ImagebuilderContainerRecipeComponentParameter",
    "ImagebuilderContainerRecipeComponentParameterList",
    "ImagebuilderContainerRecipeComponentParameterOutputReference",
    "ImagebuilderContainerRecipeConfig",
    "ImagebuilderContainerRecipeInstanceConfiguration",
    "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMapping",
    "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbs",
    "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingEbsOutputReference",
    "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingList",
    "ImagebuilderContainerRecipeInstanceConfigurationBlockDeviceMappingOutputReference",
    "ImagebuilderContainerRecipeInstanceConfigurationOutputReference",
    "ImagebuilderContainerRecipeTargetRepository",
    "ImagebuilderContainerRecipeTargetRepositoryOutputReference",
    "ImagebuilderDistributionConfiguration",
    "ImagebuilderDistributionConfigurationConfig",
    "ImagebuilderDistributionConfigurationDistribution",
    "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfiguration",
    "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermission",
    "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationLaunchPermissionOutputReference",
    "ImagebuilderDistributionConfigurationDistributionAmiDistributionConfigurationOutputReference",
    "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfiguration",
    "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationOutputReference",
    "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepository",
    "ImagebuilderDistributionConfigurationDistributionContainerDistributionConfigurationTargetRepositoryOutputReference",
    "ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfiguration",
    "ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationList",
    "ImagebuilderDistributionConfigurationDistributionLaunchTemplateConfigurationOutputReference",
    "ImagebuilderDistributionConfigurationDistributionList",
    "ImagebuilderDistributionConfigurationDistributionOutputReference",
    "ImagebuilderImage",
    "ImagebuilderImageConfig",
    "ImagebuilderImageImageTestsConfiguration",
    "ImagebuilderImageImageTestsConfigurationOutputReference",
    "ImagebuilderImageOutputResources",
    "ImagebuilderImageOutputResourcesAmis",
    "ImagebuilderImageOutputResourcesAmisList",
    "ImagebuilderImageOutputResourcesAmisOutputReference",
    "ImagebuilderImageOutputResourcesList",
    "ImagebuilderImageOutputResourcesOutputReference",
    "ImagebuilderImagePipeline",
    "ImagebuilderImagePipelineConfig",
    "ImagebuilderImagePipelineImageTestsConfiguration",
    "ImagebuilderImagePipelineImageTestsConfigurationOutputReference",
    "ImagebuilderImagePipelineSchedule",
    "ImagebuilderImagePipelineScheduleOutputReference",
    "ImagebuilderImageRecipe",
    "ImagebuilderImageRecipeBlockDeviceMapping",
    "ImagebuilderImageRecipeBlockDeviceMappingEbs",
    "ImagebuilderImageRecipeBlockDeviceMappingEbsOutputReference",
    "ImagebuilderImageRecipeBlockDeviceMappingList",
    "ImagebuilderImageRecipeBlockDeviceMappingOutputReference",
    "ImagebuilderImageRecipeComponent",
    "ImagebuilderImageRecipeComponentList",
    "ImagebuilderImageRecipeComponentOutputReference",
    "ImagebuilderImageRecipeComponentParameter",
    "ImagebuilderImageRecipeComponentParameterList",
    "ImagebuilderImageRecipeComponentParameterOutputReference",
    "ImagebuilderImageRecipeConfig",
    "ImagebuilderImageRecipeSystemsManagerAgent",
    "ImagebuilderImageRecipeSystemsManagerAgentOutputReference",
    "ImagebuilderImageTimeouts",
    "ImagebuilderImageTimeoutsOutputReference",
    "ImagebuilderInfrastructureConfiguration",
    "ImagebuilderInfrastructureConfigurationConfig",
    "ImagebuilderInfrastructureConfigurationInstanceMetadataOptions",
    "ImagebuilderInfrastructureConfigurationInstanceMetadataOptionsOutputReference",
    "ImagebuilderInfrastructureConfigurationLogging",
    "ImagebuilderInfrastructureConfigurationLoggingOutputReference",
    "ImagebuilderInfrastructureConfigurationLoggingS3Logs",
    "ImagebuilderInfrastructureConfigurationLoggingS3LogsOutputReference",
]

publication.publish()
