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


class DataAwsResourcegroupstaggingapiResources(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResources",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources aws_resourcegroupstaggingapi_resources}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        exclude_compliant_resources: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        include_compliance_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_arn_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        resource_type_filters: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources aws_resourcegroupstaggingapi_resources} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param exclude_compliant_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#exclude_compliant_resources DataAwsResourcegroupstaggingapiResources#exclude_compliant_resources}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#id DataAwsResourcegroupstaggingapiResources#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param include_compliance_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#include_compliance_details DataAwsResourcegroupstaggingapiResources#include_compliance_details}.
        :param resource_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_arn_list DataAwsResourcegroupstaggingapiResources#resource_arn_list}.
        :param resource_type_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_type_filters DataAwsResourcegroupstaggingapiResources#resource_type_filters}.
        :param tag_filter: tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#tag_filter DataAwsResourcegroupstaggingapiResources#tag_filter}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsResourcegroupstaggingapiResourcesConfig(
            exclude_compliant_resources=exclude_compliant_resources,
            id=id,
            include_compliance_details=include_compliance_details,
            resource_arn_list=resource_arn_list,
            resource_type_filters=resource_type_filters,
            tag_filter=tag_filter,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putTagFilter")
    def put_tag_filter(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsResourcegroupstaggingapiResourcesTagFilter"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putTagFilter", [value]))

    @jsii.member(jsii_name="resetExcludeCompliantResources")
    def reset_exclude_compliant_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeCompliantResources", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIncludeComplianceDetails")
    def reset_include_compliance_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeComplianceDetails", []))

    @jsii.member(jsii_name="resetResourceArnList")
    def reset_resource_arn_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceArnList", []))

    @jsii.member(jsii_name="resetResourceTypeFilters")
    def reset_resource_type_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTypeFilters", []))

    @jsii.member(jsii_name="resetTagFilter")
    def reset_tag_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagFilter", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTagMappingList")
    def resource_tag_mapping_list(
        self,
    ) -> "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListList":
        return typing.cast("DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListList", jsii.get(self, "resourceTagMappingList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagFilter")
    def tag_filter(self) -> "DataAwsResourcegroupstaggingapiResourcesTagFilterList":
        return typing.cast("DataAwsResourcegroupstaggingapiResourcesTagFilterList", jsii.get(self, "tagFilter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeCompliantResourcesInput")
    def exclude_compliant_resources_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "excludeCompliantResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeComplianceDetailsInput")
    def include_compliance_details_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeComplianceDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnListInput")
    def resource_arn_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceArnListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeFiltersInput")
    def resource_type_filters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypeFiltersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagFilterInput")
    def tag_filter_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]], jsii.get(self, "tagFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeCompliantResources")
    def exclude_compliant_resources(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "excludeCompliantResources"))

    @exclude_compliant_resources.setter
    def exclude_compliant_resources(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "excludeCompliantResources", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeComplianceDetails")
    def include_compliance_details(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeComplianceDetails"))

    @include_compliance_details.setter
    def include_compliance_details(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeComplianceDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnList")
    def resource_arn_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceArnList"))

    @resource_arn_list.setter
    def resource_arn_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceArnList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceTypeFilters")
    def resource_type_filters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypeFilters"))

    @resource_type_filters.setter
    def resource_type_filters(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "resourceTypeFilters", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "exclude_compliant_resources": "excludeCompliantResources",
        "id": "id",
        "include_compliance_details": "includeComplianceDetails",
        "resource_arn_list": "resourceArnList",
        "resource_type_filters": "resourceTypeFilters",
        "tag_filter": "tagFilter",
    },
)
class DataAwsResourcegroupstaggingapiResourcesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        exclude_compliant_resources: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        include_compliance_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        resource_arn_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        resource_type_filters: typing.Optional[typing.Sequence[builtins.str]] = None,
        tag_filter: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]] = None,
    ) -> None:
        '''AWS Resource Groups.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param exclude_compliant_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#exclude_compliant_resources DataAwsResourcegroupstaggingapiResources#exclude_compliant_resources}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#id DataAwsResourcegroupstaggingapiResources#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param include_compliance_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#include_compliance_details DataAwsResourcegroupstaggingapiResources#include_compliance_details}.
        :param resource_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_arn_list DataAwsResourcegroupstaggingapiResources#resource_arn_list}.
        :param resource_type_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_type_filters DataAwsResourcegroupstaggingapiResources#resource_type_filters}.
        :param tag_filter: tag_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#tag_filter DataAwsResourcegroupstaggingapiResources#tag_filter}
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
        if exclude_compliant_resources is not None:
            self._values["exclude_compliant_resources"] = exclude_compliant_resources
        if id is not None:
            self._values["id"] = id
        if include_compliance_details is not None:
            self._values["include_compliance_details"] = include_compliance_details
        if resource_arn_list is not None:
            self._values["resource_arn_list"] = resource_arn_list
        if resource_type_filters is not None:
            self._values["resource_type_filters"] = resource_type_filters
        if tag_filter is not None:
            self._values["tag_filter"] = tag_filter

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
    def exclude_compliant_resources(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#exclude_compliant_resources DataAwsResourcegroupstaggingapiResources#exclude_compliant_resources}.'''
        result = self._values.get("exclude_compliant_resources")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#id DataAwsResourcegroupstaggingapiResources#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_compliance_details(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#include_compliance_details DataAwsResourcegroupstaggingapiResources#include_compliance_details}.'''
        result = self._values.get("include_compliance_details")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def resource_arn_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_arn_list DataAwsResourcegroupstaggingapiResources#resource_arn_list}.'''
        result = self._values.get("resource_arn_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def resource_type_filters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#resource_type_filters DataAwsResourcegroupstaggingapiResources#resource_type_filters}.'''
        result = self._values.get("resource_type_filters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tag_filter(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]]:
        '''tag_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#tag_filter DataAwsResourcegroupstaggingapiResources#tag_filter}
        '''
        result = self._values.get("tag_filter")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsResourcegroupstaggingapiResourcesTagFilter"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourcegroupstaggingapiResourcesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsList",
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
    ) -> "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsOutputReference",
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
    @jsii.member(jsii_name="complianceStatus")
    def compliance_status(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "complianceStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keysWithNoncompliantValues")
    def keys_with_noncompliant_values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keysWithNoncompliantValues"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nonCompliantKeys")
    def non_compliant_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nonCompliantKeys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails]:
        return typing.cast(typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListList",
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
    ) -> "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListOutputReference",
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
    @jsii.member(jsii_name="complianceDetails")
    def compliance_details(
        self,
    ) -> DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsList:
        return typing.cast(DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsList, jsii.get(self, "complianceDetails"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> cdktf.StringMap:
        return typing.cast(cdktf.StringMap, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList]:
        return typing.cast(typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesTagFilter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "values": "values"},
)
class DataAwsResourcegroupstaggingapiResourcesTagFilter:
    def __init__(
        self,
        *,
        key: builtins.str,
        values: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#key DataAwsResourcegroupstaggingapiResources#key}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#values DataAwsResourcegroupstaggingapiResources#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
        }
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#key DataAwsResourcegroupstaggingapiResources#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/resourcegroupstaggingapi_resources#values DataAwsResourcegroupstaggingapiResources#values}.'''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourcegroupstaggingapiResourcesTagFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsResourcegroupstaggingapiResourcesTagFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesTagFilterList",
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
    ) -> "DataAwsResourcegroupstaggingapiResourcesTagFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsResourcegroupstaggingapiResourcesTagFilterOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsResourcegroupstaggingapiResourcesTagFilter]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsResourcegroupstaggingapiResourcesTagFilter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsResourcegroupstaggingapiResourcesTagFilter]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsResourcegroupstaggingapiResourcesTagFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.DataAwsResourcegroupstaggingapiResourcesTagFilterOutputReference",
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

    @jsii.member(jsii_name="resetValues")
    def reset_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValues", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

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
    ) -> typing.Optional[typing.Union[DataAwsResourcegroupstaggingapiResourcesTagFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsResourcegroupstaggingapiResourcesTagFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsResourcegroupstaggingapiResourcesTagFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ResourcegroupsGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.ResourcegroupsGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group aws_resourcegroups_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        resource_query: "ResourcegroupsGroupResourceQuery",
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group aws_resourcegroups_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#name ResourcegroupsGroup#name}.
        :param resource_query: resource_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#resource_query ResourcegroupsGroup#resource_query}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#description ResourcegroupsGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#id ResourcegroupsGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags ResourcegroupsGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags_all ResourcegroupsGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ResourcegroupsGroupConfig(
            name=name,
            resource_query=resource_query,
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

    @jsii.member(jsii_name="putResourceQuery")
    def put_resource_query(
        self,
        *,
        query: builtins.str,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#query ResourcegroupsGroup#query}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#type ResourcegroupsGroup#type}.
        '''
        value = ResourcegroupsGroupResourceQuery(query=query, type=type)

        return typing.cast(None, jsii.invoke(self, "putResourceQuery", [value]))

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
    @jsii.member(jsii_name="resourceQuery")
    def resource_query(self) -> "ResourcegroupsGroupResourceQueryOutputReference":
        return typing.cast("ResourcegroupsGroupResourceQueryOutputReference", jsii.get(self, "resourceQuery"))

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
    @jsii.member(jsii_name="resourceQueryInput")
    def resource_query_input(
        self,
    ) -> typing.Optional["ResourcegroupsGroupResourceQuery"]:
        return typing.cast(typing.Optional["ResourcegroupsGroupResourceQuery"], jsii.get(self, "resourceQueryInput"))

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
    jsii_type="@cdktf/provider-aws.resourcegroups.ResourcegroupsGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "resource_query": "resourceQuery",
        "description": "description",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class ResourcegroupsGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        resource_query: "ResourcegroupsGroupResourceQuery",
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Resource Groups.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#name ResourcegroupsGroup#name}.
        :param resource_query: resource_query block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#resource_query ResourcegroupsGroup#resource_query}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#description ResourcegroupsGroup#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#id ResourcegroupsGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags ResourcegroupsGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags_all ResourcegroupsGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(resource_query, dict):
            resource_query = ResourcegroupsGroupResourceQuery(**resource_query)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "resource_query": resource_query,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#name ResourcegroupsGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_query(self) -> "ResourcegroupsGroupResourceQuery":
        '''resource_query block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#resource_query ResourcegroupsGroup#resource_query}
        '''
        result = self._values.get("resource_query")
        assert result is not None, "Required property 'resource_query' is missing"
        return typing.cast("ResourcegroupsGroupResourceQuery", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#description ResourcegroupsGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#id ResourcegroupsGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags ResourcegroupsGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#tags_all ResourcegroupsGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourcegroupsGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.resourcegroups.ResourcegroupsGroupResourceQuery",
    jsii_struct_bases=[],
    name_mapping={"query": "query", "type": "type"},
)
class ResourcegroupsGroupResourceQuery:
    def __init__(
        self,
        *,
        query: builtins.str,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#query ResourcegroupsGroup#query}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#type ResourcegroupsGroup#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "query": query,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#query ResourcegroupsGroup#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/resourcegroups_group#type ResourcegroupsGroup#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourcegroupsGroupResourceQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResourcegroupsGroupResourceQueryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.resourcegroups.ResourcegroupsGroupResourceQueryOutputReference",
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

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ResourcegroupsGroupResourceQuery]:
        return typing.cast(typing.Optional[ResourcegroupsGroupResourceQuery], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ResourcegroupsGroupResourceQuery],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsResourcegroupstaggingapiResources",
    "DataAwsResourcegroupstaggingapiResourcesConfig",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingList",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetails",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsList",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListComplianceDetailsOutputReference",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListList",
    "DataAwsResourcegroupstaggingapiResourcesResourceTagMappingListOutputReference",
    "DataAwsResourcegroupstaggingapiResourcesTagFilter",
    "DataAwsResourcegroupstaggingapiResourcesTagFilterList",
    "DataAwsResourcegroupstaggingapiResourcesTagFilterOutputReference",
    "ResourcegroupsGroup",
    "ResourcegroupsGroupConfig",
    "ResourcegroupsGroupResourceQuery",
    "ResourcegroupsGroupResourceQueryOutputReference",
]

publication.publish()
