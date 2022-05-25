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


class DataAwsDatapipelinePipeline(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipeline",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline aws_datapipeline_pipeline}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        pipeline_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline aws_datapipeline_pipeline} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#pipeline_id DataAwsDatapipelinePipeline#pipeline_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#id DataAwsDatapipelinePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#tags DataAwsDatapipelinePipeline#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDatapipelinePipelineConfig(
            pipeline_id=pipeline_id,
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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineIdInput")
    def pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @pipeline_id.setter
    def pipeline_id(self, value: builtins.str) -> None:
        jsii.set(self, "pipelineId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pipeline_id": "pipelineId",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsDatapipelinePipelineConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pipeline_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Data Pipeline.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#pipeline_id DataAwsDatapipelinePipeline#pipeline_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#id DataAwsDatapipelinePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#tags DataAwsDatapipelinePipeline#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pipeline_id": pipeline_id,
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
    def pipeline_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#pipeline_id DataAwsDatapipelinePipeline#pipeline_id}.'''
        result = self._values.get("pipeline_id")
        assert result is not None, "Required property 'pipeline_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#id DataAwsDatapipelinePipeline#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline#tags DataAwsDatapipelinePipeline#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDatapipelinePipelineDefinition(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition aws_datapipeline_pipeline_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        pipeline_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        parameter_value: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsDatapipelinePipelineDefinitionParameterValue"]]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition aws_datapipeline_pipeline_definition} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#pipeline_id DataAwsDatapipelinePipelineDefinition#pipeline_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#id DataAwsDatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter_value: parameter_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#parameter_value DataAwsDatapipelinePipelineDefinition#parameter_value}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDatapipelinePipelineDefinitionConfig(
            pipeline_id=pipeline_id,
            id=id,
            parameter_value=parameter_value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putParameterValue")
    def put_parameter_value(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsDatapipelinePipelineDefinitionParameterValue"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putParameterValue", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParameterValue")
    def reset_parameter_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterValue", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterObject")
    def parameter_object(
        self,
    ) -> "DataAwsDatapipelinePipelineDefinitionParameterObjectList":
        return typing.cast("DataAwsDatapipelinePipelineDefinitionParameterObjectList", jsii.get(self, "parameterObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(
        self,
    ) -> "DataAwsDatapipelinePipelineDefinitionParameterValueList":
        return typing.cast("DataAwsDatapipelinePipelineDefinitionParameterValueList", jsii.get(self, "parameterValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineObject")
    def pipeline_object(
        self,
    ) -> "DataAwsDatapipelinePipelineDefinitionPipelineObjectList":
        return typing.cast("DataAwsDatapipelinePipelineDefinitionPipelineObjectList", jsii.get(self, "pipelineObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValueInput")
    def parameter_value_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsDatapipelinePipelineDefinitionParameterValue"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsDatapipelinePipelineDefinitionParameterValue"]]], jsii.get(self, "parameterValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineIdInput")
    def pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @pipeline_id.setter
    def pipeline_id(self, value: builtins.str) -> None:
        jsii.set(self, "pipelineId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pipeline_id": "pipelineId",
        "id": "id",
        "parameter_value": "parameterValue",
    },
)
class DataAwsDatapipelinePipelineDefinitionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pipeline_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        parameter_value: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DataAwsDatapipelinePipelineDefinitionParameterValue"]]] = None,
    ) -> None:
        '''AWS Data Pipeline.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#pipeline_id DataAwsDatapipelinePipelineDefinition#pipeline_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#id DataAwsDatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter_value: parameter_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#parameter_value DataAwsDatapipelinePipelineDefinition#parameter_value}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pipeline_id": pipeline_id,
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
        if parameter_value is not None:
            self._values["parameter_value"] = parameter_value

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
    def pipeline_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#pipeline_id DataAwsDatapipelinePipelineDefinition#pipeline_id}.'''
        result = self._values.get("pipeline_id")
        assert result is not None, "Required property 'pipeline_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#id DataAwsDatapipelinePipelineDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsDatapipelinePipelineDefinitionParameterValue"]]]:
        '''parameter_value block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/datapipeline_pipeline_definition#parameter_value DataAwsDatapipelinePipelineDefinition#parameter_value}
        '''
        result = self._values.get("parameter_value")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DataAwsDatapipelinePipelineDefinitionParameterValue"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObject",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDatapipelinePipelineDefinitionParameterObject:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionParameterObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeList",
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
    ) -> "DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeOutputReference",
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
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute]:
        return typing.cast(typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsDatapipelinePipelineDefinitionParameterObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObjectList",
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
    ) -> "DataAwsDatapipelinePipelineDefinitionParameterObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsDatapipelinePipelineDefinitionParameterObjectOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsDatapipelinePipelineDefinitionParameterObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterObjectOutputReference",
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
    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
    ) -> DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeList:
        return typing.cast(DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeList, jsii.get(self, "attribute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObject]:
        return typing.cast(typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsDatapipelinePipelineDefinitionParameterObject],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterValue",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDatapipelinePipelineDefinitionParameterValue:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionParameterValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDatapipelinePipelineDefinitionParameterValueList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterValueList",
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
    ) -> "DataAwsDatapipelinePipelineDefinitionParameterValueOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsDatapipelinePipelineDefinitionParameterValueOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsDatapipelinePipelineDefinitionParameterValue]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsDatapipelinePipelineDefinitionParameterValue]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DataAwsDatapipelinePipelineDefinitionParameterValue]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsDatapipelinePipelineDefinitionParameterValueOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionParameterValueOutputReference",
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
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DataAwsDatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DataAwsDatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DataAwsDatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObject",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDatapipelinePipelineDefinitionPipelineObject:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionPipelineObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObjectField",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDatapipelinePipelineDefinitionPipelineObjectField:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDatapipelinePipelineDefinitionPipelineObjectField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldList",
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
    ) -> "DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldOutputReference",
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
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refValue")
    def ref_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObjectField]:
        return typing.cast(typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObjectField], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObjectField],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsDatapipelinePipelineDefinitionPipelineObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObjectList",
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
    ) -> "DataAwsDatapipelinePipelineDefinitionPipelineObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsDatapipelinePipelineDefinitionPipelineObjectOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsDatapipelinePipelineDefinitionPipelineObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DataAwsDatapipelinePipelineDefinitionPipelineObjectOutputReference",
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
    @jsii.member(jsii_name="field")
    def field(self) -> DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldList:
        return typing.cast(DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldList, jsii.get(self, "field"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObject]:
        return typing.cast(typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsDatapipelinePipelineDefinitionPipelineObject],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipeline(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipeline",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline aws_datapipeline_pipeline}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline aws_datapipeline_pipeline} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#name DatapipelinePipeline#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#description DatapipelinePipeline#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#id DatapipelinePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags DatapipelinePipeline#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags_all DatapipelinePipeline#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatapipelinePipelineConfig(
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
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DatapipelinePipelineConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Data Pipeline.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#name DatapipelinePipeline#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#description DatapipelinePipeline#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#id DatapipelinePipeline#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags DatapipelinePipeline#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags_all DatapipelinePipeline#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#name DatapipelinePipeline#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#description DatapipelinePipeline#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#id DatapipelinePipeline#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags DatapipelinePipeline#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline#tags_all DatapipelinePipeline#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatapipelinePipelineDefinition(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinition",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition aws_datapipeline_pipeline_definition}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        pipeline_id: builtins.str,
        pipeline_object: typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionPipelineObject"]],
        id: typing.Optional[builtins.str] = None,
        parameter_object: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterObject"]]] = None,
        parameter_value: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterValue"]]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition aws_datapipeline_pipeline_definition} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_id DatapipelinePipelineDefinition#pipeline_id}.
        :param pipeline_object: pipeline_object block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_object DatapipelinePipelineDefinition#pipeline_object}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter_object: parameter_object block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_object DatapipelinePipelineDefinition#parameter_object}
        :param parameter_value: parameter_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_value DatapipelinePipelineDefinition#parameter_value}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DatapipelinePipelineDefinitionConfig(
            pipeline_id=pipeline_id,
            pipeline_object=pipeline_object,
            id=id,
            parameter_object=parameter_object,
            parameter_value=parameter_value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putParameterObject")
    def put_parameter_object(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterObject"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putParameterObject", [value]))

    @jsii.member(jsii_name="putParameterValue")
    def put_parameter_value(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterValue"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putParameterValue", [value]))

    @jsii.member(jsii_name="putPipelineObject")
    def put_pipeline_object(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionPipelineObject"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putPipelineObject", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParameterObject")
    def reset_parameter_object(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterObject", []))

    @jsii.member(jsii_name="resetParameterValue")
    def reset_parameter_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterValue", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterObject")
    def parameter_object(self) -> "DatapipelinePipelineDefinitionParameterObjectList":
        return typing.cast("DatapipelinePipelineDefinitionParameterObjectList", jsii.get(self, "parameterObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> "DatapipelinePipelineDefinitionParameterValueList":
        return typing.cast("DatapipelinePipelineDefinitionParameterValueList", jsii.get(self, "parameterValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineObject")
    def pipeline_object(self) -> "DatapipelinePipelineDefinitionPipelineObjectList":
        return typing.cast("DatapipelinePipelineDefinitionPipelineObjectList", jsii.get(self, "pipelineObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterObjectInput")
    def parameter_object_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObject"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObject"]]], jsii.get(self, "parameterObjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterValueInput")
    def parameter_value_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterValue"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterValue"]]], jsii.get(self, "parameterValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineIdInput")
    def pipeline_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineObjectInput")
    def pipeline_object_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObject"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObject"]]], jsii.get(self, "pipelineObjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineId")
    def pipeline_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineId"))

    @pipeline_id.setter
    def pipeline_id(self, value: builtins.str) -> None:
        jsii.set(self, "pipelineId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pipeline_id": "pipelineId",
        "pipeline_object": "pipelineObject",
        "id": "id",
        "parameter_object": "parameterObject",
        "parameter_value": "parameterValue",
    },
)
class DatapipelinePipelineDefinitionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pipeline_id: builtins.str,
        pipeline_object: typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionPipelineObject"]],
        id: typing.Optional[builtins.str] = None,
        parameter_object: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterObject"]]] = None,
        parameter_value: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterValue"]]] = None,
    ) -> None:
        '''AWS Data Pipeline.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pipeline_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_id DatapipelinePipelineDefinition#pipeline_id}.
        :param pipeline_object: pipeline_object block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_object DatapipelinePipelineDefinition#pipeline_object}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parameter_object: parameter_object block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_object DatapipelinePipelineDefinition#parameter_object}
        :param parameter_value: parameter_value block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_value DatapipelinePipelineDefinition#parameter_value}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pipeline_id": pipeline_id,
            "pipeline_object": pipeline_object,
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
        if parameter_object is not None:
            self._values["parameter_object"] = parameter_object
        if parameter_value is not None:
            self._values["parameter_value"] = parameter_value

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
    def pipeline_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_id DatapipelinePipelineDefinition#pipeline_id}.'''
        result = self._values.get("pipeline_id")
        assert result is not None, "Required property 'pipeline_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline_object(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObject"]]:
        '''pipeline_object block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#pipeline_object DatapipelinePipelineDefinition#pipeline_object}
        '''
        result = self._values.get("pipeline_object")
        assert result is not None, "Required property 'pipeline_object' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObject"]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_object(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObject"]]]:
        '''parameter_object block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_object DatapipelinePipelineDefinition#parameter_object}
        '''
        result = self._values.get("parameter_object")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObject"]]], result)

    @builtins.property
    def parameter_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterValue"]]]:
        '''parameter_value block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#parameter_value DatapipelinePipelineDefinition#parameter_value}
        '''
        result = self._values.get("parameter_value")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterValue"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObject",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "attribute": "attribute"},
)
class DatapipelinePipelineDefinitionParameterObject:
    def __init__(
        self,
        *,
        id: builtins.str,
        attribute: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionParameterObjectAttribute"]]] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param attribute: attribute block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#attribute DatapipelinePipelineDefinition#attribute}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if attribute is not None:
            self._values["attribute"] = attribute

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObjectAttribute"]]]:
        '''attribute block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#attribute DatapipelinePipelineDefinition#attribute}
        '''
        result = self._values.get("attribute")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionParameterObjectAttribute"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionParameterObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObjectAttribute",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "string_value": "stringValue"},
)
class DatapipelinePipelineDefinitionParameterObjectAttribute:
    def __init__(self, *, key: builtins.str, string_value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#key DatapipelinePipelineDefinition#key}.
        :param string_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "string_value": string_value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#key DatapipelinePipelineDefinition#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def string_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.'''
        result = self._values.get("string_value")
        assert result is not None, "Required property 'string_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionParameterObjectAttribute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatapipelinePipelineDefinitionParameterObjectAttributeList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObjectAttributeList",
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
    ) -> "DatapipelinePipelineDefinitionParameterObjectAttributeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DatapipelinePipelineDefinitionParameterObjectAttributeOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObjectAttribute]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObjectAttribute]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObjectAttribute]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionParameterObjectAttributeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObjectAttributeOutputReference",
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
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValueInput")
    def string_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stringValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        jsii.set(self, "stringValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObjectAttribute, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObjectAttribute, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObjectAttribute, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionParameterObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObjectList",
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
    ) -> "DatapipelinePipelineDefinitionParameterObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DatapipelinePipelineDefinitionParameterObjectOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObject]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObject]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObject]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionParameterObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterObjectOutputReference",
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

    @jsii.member(jsii_name="putAttribute")
    def put_attribute(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[DatapipelinePipelineDefinitionParameterObjectAttribute]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putAttribute", [value]))

    @jsii.member(jsii_name="resetAttribute")
    def reset_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttribute", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attribute")
    def attribute(self) -> DatapipelinePipelineDefinitionParameterObjectAttributeList:
        return typing.cast(DatapipelinePipelineDefinitionParameterObjectAttributeList, jsii.get(self, "attribute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeInput")
    def attribute_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObjectAttribute]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterObjectAttribute]]], jsii.get(self, "attributeInput"))

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
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObject, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObject, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterObject, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterValue",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "string_value": "stringValue"},
)
class DatapipelinePipelineDefinitionParameterValue:
    def __init__(self, *, id: builtins.str, string_value: builtins.str) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param string_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "string_value": string_value,
        }

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def string_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.'''
        result = self._values.get("string_value")
        assert result is not None, "Required property 'string_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionParameterValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatapipelinePipelineDefinitionParameterValueList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterValueList",
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
    ) -> "DatapipelinePipelineDefinitionParameterValueOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DatapipelinePipelineDefinitionParameterValueOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterValue]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterValue]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionParameterValue]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionParameterValueOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionParameterValueOutputReference",
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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValueInput")
    def string_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stringValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        jsii.set(self, "stringValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DatapipelinePipelineDefinitionParameterValue, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObject",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "name": "name", "field": "field"},
)
class DatapipelinePipelineDefinitionPipelineObject:
    def __init__(
        self,
        *,
        id: builtins.str,
        name: builtins.str,
        field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["DatapipelinePipelineDefinitionPipelineObjectField"]]] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#name DatapipelinePipelineDefinition#name}.
        :param field: field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#field DatapipelinePipelineDefinition#field}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "name": name,
        }
        if field is not None:
            self._values["field"] = field

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#id DatapipelinePipelineDefinition#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#name DatapipelinePipelineDefinition#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObjectField"]]]:
        '''field block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#field DatapipelinePipelineDefinition#field}
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["DatapipelinePipelineDefinitionPipelineObjectField"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionPipelineObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObjectField",
    jsii_struct_bases=[],
    name_mapping={
        "key": "key",
        "ref_value": "refValue",
        "string_value": "stringValue",
    },
)
class DatapipelinePipelineDefinitionPipelineObjectField:
    def __init__(
        self,
        *,
        key: builtins.str,
        ref_value: typing.Optional[builtins.str] = None,
        string_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#key DatapipelinePipelineDefinition#key}.
        :param ref_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#ref_value DatapipelinePipelineDefinition#ref_value}.
        :param string_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
        }
        if ref_value is not None:
            self._values["ref_value"] = ref_value
        if string_value is not None:
            self._values["string_value"] = string_value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#key DatapipelinePipelineDefinition#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ref_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#ref_value DatapipelinePipelineDefinition#ref_value}.'''
        result = self._values.get("ref_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/datapipeline_pipeline_definition#string_value DatapipelinePipelineDefinition#string_value}.'''
        result = self._values.get("string_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatapipelinePipelineDefinitionPipelineObjectField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatapipelinePipelineDefinitionPipelineObjectFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObjectFieldList",
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
    ) -> "DatapipelinePipelineDefinitionPipelineObjectFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DatapipelinePipelineDefinitionPipelineObjectFieldOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObjectField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObjectField]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObjectField]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionPipelineObjectFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObjectFieldOutputReference",
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

    @jsii.member(jsii_name="resetRefValue")
    def reset_ref_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRefValue", []))

    @jsii.member(jsii_name="resetStringValue")
    def reset_string_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStringValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refValueInput")
    def ref_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "refValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValueInput")
    def string_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stringValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refValue")
    def ref_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "refValue"))

    @ref_value.setter
    def ref_value(self, value: builtins.str) -> None:
        jsii.set(self, "refValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValue")
    def string_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stringValue"))

    @string_value.setter
    def string_value(self, value: builtins.str) -> None:
        jsii.set(self, "stringValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObjectField, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObjectField, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObjectField, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionPipelineObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObjectList",
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
    ) -> "DatapipelinePipelineDefinitionPipelineObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DatapipelinePipelineDefinitionPipelineObjectOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObject]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObject]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObject]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DatapipelinePipelineDefinitionPipelineObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.datapipeline.DatapipelinePipelineDefinitionPipelineObjectOutputReference",
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

    @jsii.member(jsii_name="putField")
    def put_field(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[DatapipelinePipelineDefinitionPipelineObjectField]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putField", [value]))

    @jsii.member(jsii_name="resetField")
    def reset_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetField", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="field")
    def field(self) -> DatapipelinePipelineDefinitionPipelineObjectFieldList:
        return typing.cast(DatapipelinePipelineDefinitionPipelineObjectFieldList, jsii.get(self, "field"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldInput")
    def field_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObjectField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[DatapipelinePipelineDefinitionPipelineObjectField]]], jsii.get(self, "fieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObject, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObject, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DatapipelinePipelineDefinitionPipelineObject, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsDatapipelinePipeline",
    "DataAwsDatapipelinePipelineConfig",
    "DataAwsDatapipelinePipelineDefinition",
    "DataAwsDatapipelinePipelineDefinitionConfig",
    "DataAwsDatapipelinePipelineDefinitionParameterObject",
    "DataAwsDatapipelinePipelineDefinitionParameterObjectAttribute",
    "DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeList",
    "DataAwsDatapipelinePipelineDefinitionParameterObjectAttributeOutputReference",
    "DataAwsDatapipelinePipelineDefinitionParameterObjectList",
    "DataAwsDatapipelinePipelineDefinitionParameterObjectOutputReference",
    "DataAwsDatapipelinePipelineDefinitionParameterValue",
    "DataAwsDatapipelinePipelineDefinitionParameterValueList",
    "DataAwsDatapipelinePipelineDefinitionParameterValueOutputReference",
    "DataAwsDatapipelinePipelineDefinitionPipelineObject",
    "DataAwsDatapipelinePipelineDefinitionPipelineObjectField",
    "DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldList",
    "DataAwsDatapipelinePipelineDefinitionPipelineObjectFieldOutputReference",
    "DataAwsDatapipelinePipelineDefinitionPipelineObjectList",
    "DataAwsDatapipelinePipelineDefinitionPipelineObjectOutputReference",
    "DatapipelinePipeline",
    "DatapipelinePipelineConfig",
    "DatapipelinePipelineDefinition",
    "DatapipelinePipelineDefinitionConfig",
    "DatapipelinePipelineDefinitionParameterObject",
    "DatapipelinePipelineDefinitionParameterObjectAttribute",
    "DatapipelinePipelineDefinitionParameterObjectAttributeList",
    "DatapipelinePipelineDefinitionParameterObjectAttributeOutputReference",
    "DatapipelinePipelineDefinitionParameterObjectList",
    "DatapipelinePipelineDefinitionParameterObjectOutputReference",
    "DatapipelinePipelineDefinitionParameterValue",
    "DatapipelinePipelineDefinitionParameterValueList",
    "DatapipelinePipelineDefinitionParameterValueOutputReference",
    "DatapipelinePipelineDefinitionPipelineObject",
    "DatapipelinePipelineDefinitionPipelineObjectField",
    "DatapipelinePipelineDefinitionPipelineObjectFieldList",
    "DatapipelinePipelineDefinitionPipelineObjectFieldOutputReference",
    "DatapipelinePipelineDefinitionPipelineObjectList",
    "DatapipelinePipelineDefinitionPipelineObjectOutputReference",
]

publication.publish()
