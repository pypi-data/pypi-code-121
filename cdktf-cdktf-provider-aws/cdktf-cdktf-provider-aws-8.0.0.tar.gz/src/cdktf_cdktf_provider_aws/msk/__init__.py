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


class DataAwsMskBrokerNodes(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodes",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes aws_msk_broker_nodes}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        cluster_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes aws_msk_broker_nodes} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#id DataAwsMskBrokerNodes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskBrokerNodesConfig(
            cluster_arn=cluster_arn,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="nodeInfoList")
    def node_info_list(self) -> "DataAwsMskBrokerNodesNodeInfoListList":
        return typing.cast("DataAwsMskBrokerNodesNodeInfoListList", jsii.get(self, "nodeInfoList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArnInput")
    def cluster_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @cluster_arn.setter
    def cluster_arn(self, value: builtins.str) -> None:
        jsii.set(self, "clusterArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_arn": "clusterArn",
        "id": "id",
    },
)
class DataAwsMskBrokerNodesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_arn: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#id DataAwsMskBrokerNodes#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_arn": cluster_arn,
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
    def cluster_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#cluster_arn DataAwsMskBrokerNodes#cluster_arn}.'''
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_broker_nodes#id DataAwsMskBrokerNodes#id}.

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
        return "DataAwsMskBrokerNodesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesNodeInfoList",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsMskBrokerNodesNodeInfoList:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskBrokerNodesNodeInfoList(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskBrokerNodesNodeInfoListList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesNodeInfoListList",
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
    ) -> "DataAwsMskBrokerNodesNodeInfoListOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsMskBrokerNodesNodeInfoListOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsMskBrokerNodesNodeInfoListOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskBrokerNodesNodeInfoListOutputReference",
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
    @jsii.member(jsii_name="attachedEniId")
    def attached_eni_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachedEniId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerId")
    def broker_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "brokerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnet")
    def client_subnet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSubnet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientVpcIpAddress")
    def client_vpc_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientVpcIpAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "endpoints"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeArn")
    def node_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsMskBrokerNodesNodeInfoList]:
        return typing.cast(typing.Optional[DataAwsMskBrokerNodesNodeInfoList], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsMskBrokerNodesNodeInfoList],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsMskCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster aws_msk_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        cluster_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster aws_msk_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#id DataAwsMskCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskClusterConfig(
            cluster_name=cluster_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokers")
    def bootstrap_brokers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicSaslIam")
    def bootstrap_brokers_public_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicSaslScram")
    def bootstrap_brokers_public_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicTls")
    def bootstrap_brokers_public_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslIam")
    def bootstrap_brokers_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslScram")
    def bootstrap_brokers_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersTls")
    def bootstrap_brokers_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kafkaVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfBrokerNodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectString")
    def zookeeper_connect_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectString"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectStringTls")
    def zookeeper_connect_string_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectStringTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

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
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_name": "clusterName",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsMskClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#id DataAwsMskCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#cluster_name DataAwsMskCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#id DataAwsMskCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_cluster#tags DataAwsMskCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration aws_msk_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration aws_msk_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#id DataAwsMskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskConfigurationConfig(
            name=name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersions")
    def kafka_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "kafkaVersions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProperties")
    def server_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverProperties"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
    },
)
class DataAwsMskConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#id DataAwsMskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#name DataAwsMskConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_configuration#id DataAwsMskConfiguration#id}.

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
        return "DataAwsMskConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskKafkaVersion(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskKafkaVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version aws_msk_kafka_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version aws_msk_kafka_version} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#id DataAwsMskKafkaVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskKafkaVersionConfig(
            id=id,
            preferred_versions=preferred_versions,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPreferredVersions")
    def reset_preferred_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredVersions", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredVersionsInput")
    def preferred_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredVersions")
    def preferred_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredVersions"))

    @preferred_versions.setter
    def preferred_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskKafkaVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "preferred_versions": "preferredVersions",
        "version": "version",
    },
)
class DataAwsMskKafkaVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#id DataAwsMskKafkaVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.
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
        if id is not None:
            self._values["id"] = id
        if preferred_versions is not None:
            self._values["preferred_versions"] = preferred_versions
        if version is not None:
            self._values["version"] = version

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#id DataAwsMskKafkaVersion#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#preferred_versions DataAwsMskKafkaVersion#preferred_versions}.'''
        result = self._values.get("preferred_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/msk_kafka_version#version DataAwsMskKafkaVersion#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsMskKafkaVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskconnectConnector(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectConnector",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector aws_mskconnect_connector}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector aws_mskconnect_connector} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#name DataAwsMskconnectConnector#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#id DataAwsMskconnectConnector#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskconnectConnectorConfig(
            name=name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectConnectorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
    },
)
class DataAwsMskconnectConnectorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#name DataAwsMskconnectConnector#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#id DataAwsMskconnectConnector#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#name DataAwsMskconnectConnector#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_connector#id DataAwsMskconnectConnector#id}.

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
        return "DataAwsMskconnectConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskconnectCustomPlugin(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectCustomPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin aws_mskconnect_custom_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin aws_mskconnect_custom_plugin} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#id DataAwsMskconnectCustomPlugin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskconnectCustomPluginConfig(
            name=name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectCustomPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
    },
)
class DataAwsMskconnectCustomPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#id DataAwsMskconnectCustomPlugin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#name DataAwsMskconnectCustomPlugin#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_custom_plugin#id DataAwsMskconnectCustomPlugin#id}.

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
        return "DataAwsMskconnectCustomPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsMskconnectWorkerConfiguration(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectWorkerConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration aws_mskconnect_worker_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration aws_mskconnect_worker_configuration} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#id DataAwsMskconnectWorkerConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsMskconnectWorkerConfigurationConfig(
            name=name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesFileContent")
    def properties_file_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propertiesFileContent"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.DataAwsMskconnectWorkerConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
    },
)
class DataAwsMskconnectWorkerConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#id DataAwsMskconnectWorkerConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#name DataAwsMskconnectWorkerConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/mskconnect_worker_configuration#id DataAwsMskconnectWorkerConfiguration#id}.

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
        return "DataAwsMskconnectWorkerConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster aws_msk_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        broker_node_group_info: "MskClusterBrokerNodeGroupInfo",
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional["MskClusterClientAuthentication"] = None,
        configuration_info: typing.Optional["MskClusterConfigurationInfo"] = None,
        encryption_info: typing.Optional["MskClusterEncryptionInfo"] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional["MskClusterLoggingInfo"] = None,
        open_monitoring: typing.Optional["MskClusterOpenMonitoring"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["MskClusterTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster aws_msk_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param broker_node_group_info: broker_node_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.
        :param kafka_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.
        :param number_of_broker_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.
        :param client_authentication: client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        :param configuration_info: configuration_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        :param encryption_info: encryption_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        :param enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#id MskCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param logging_info: logging_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        :param open_monitoring: open_monitoring block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskClusterConfig(
            broker_node_group_info=broker_node_group_info,
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            client_authentication=client_authentication,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            id=id,
            logging_info=logging_info,
            open_monitoring=open_monitoring,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putBrokerNodeGroupInfo")
    def put_broker_node_group_info(
        self,
        *,
        client_subnets: typing.Sequence[builtins.str],
        instance_type: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        az_distribution: typing.Optional[builtins.str] = None,
        connectivity_info: typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfo"] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        storage_info: typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"] = None,
    ) -> None:
        '''
        :param client_subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.
        :param az_distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.
        :param connectivity_info: connectivity_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#connectivity_info MskCluster#connectivity_info}
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.
        :param storage_info: storage_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#storage_info MskCluster#storage_info}
        '''
        value = MskClusterBrokerNodeGroupInfo(
            client_subnets=client_subnets,
            instance_type=instance_type,
            security_groups=security_groups,
            az_distribution=az_distribution,
            connectivity_info=connectivity_info,
            ebs_volume_size=ebs_volume_size,
            storage_info=storage_info,
        )

        return typing.cast(None, jsii.invoke(self, "putBrokerNodeGroupInfo", [value]))

    @jsii.member(jsii_name="putClientAuthentication")
    def put_client_authentication(
        self,
        *,
        sasl: typing.Optional["MskClusterClientAuthenticationSasl"] = None,
        tls: typing.Optional["MskClusterClientAuthenticationTls"] = None,
        unauthenticated: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param sasl: sasl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        :param tls: tls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        :param unauthenticated: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#unauthenticated MskCluster#unauthenticated}.
        '''
        value = MskClusterClientAuthentication(
            sasl=sasl, tls=tls, unauthenticated=unauthenticated
        )

        return typing.cast(None, jsii.invoke(self, "putClientAuthentication", [value]))

    @jsii.member(jsii_name="putConfigurationInfo")
    def put_configuration_info(
        self,
        *,
        arn: builtins.str,
        revision: jsii.Number,
    ) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.
        '''
        value = MskClusterConfigurationInfo(arn=arn, revision=revision)

        return typing.cast(None, jsii.invoke(self, "putConfigurationInfo", [value]))

    @jsii.member(jsii_name="putEncryptionInfo")
    def put_encryption_info(
        self,
        *,
        encryption_at_rest_kms_key_arn: typing.Optional[builtins.str] = None,
        encryption_in_transit: typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"] = None,
    ) -> None:
        '''
        :param encryption_at_rest_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.
        :param encryption_in_transit: encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        value = MskClusterEncryptionInfo(
            encryption_at_rest_kms_key_arn=encryption_at_rest_kms_key_arn,
            encryption_in_transit=encryption_in_transit,
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionInfo", [value]))

    @jsii.member(jsii_name="putLoggingInfo")
    def put_logging_info(
        self,
        *,
        broker_logs: "MskClusterLoggingInfoBrokerLogs",
    ) -> None:
        '''
        :param broker_logs: broker_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        value = MskClusterLoggingInfo(broker_logs=broker_logs)

        return typing.cast(None, jsii.invoke(self, "putLoggingInfo", [value]))

    @jsii.member(jsii_name="putOpenMonitoring")
    def put_open_monitoring(
        self,
        *,
        prometheus: "MskClusterOpenMonitoringPrometheus",
    ) -> None:
        '''
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        value = MskClusterOpenMonitoring(prometheus=prometheus)

        return typing.cast(None, jsii.invoke(self, "putOpenMonitoring", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.
        '''
        value = MskClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetClientAuthentication")
    def reset_client_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientAuthentication", []))

    @jsii.member(jsii_name="resetConfigurationInfo")
    def reset_configuration_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationInfo", []))

    @jsii.member(jsii_name="resetEncryptionInfo")
    def reset_encryption_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionInfo", []))

    @jsii.member(jsii_name="resetEnhancedMonitoring")
    def reset_enhanced_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnhancedMonitoring", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLoggingInfo")
    def reset_logging_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingInfo", []))

    @jsii.member(jsii_name="resetOpenMonitoring")
    def reset_open_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenMonitoring", []))

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
    @jsii.member(jsii_name="bootstrapBrokers")
    def bootstrap_brokers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicSaslIam")
    def bootstrap_brokers_public_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicSaslScram")
    def bootstrap_brokers_public_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersPublicTls")
    def bootstrap_brokers_public_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersPublicTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslIam")
    def bootstrap_brokers_sasl_iam(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslIam"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslScram")
    def bootstrap_brokers_sasl_scram(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersTls")
    def bootstrap_brokers_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerNodeGroupInfo")
    def broker_node_group_info(self) -> "MskClusterBrokerNodeGroupInfoOutputReference":
        return typing.cast("MskClusterBrokerNodeGroupInfoOutputReference", jsii.get(self, "brokerNodeGroupInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientAuthentication")
    def client_authentication(self) -> "MskClusterClientAuthenticationOutputReference":
        return typing.cast("MskClusterClientAuthenticationOutputReference", jsii.get(self, "clientAuthentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInfo")
    def configuration_info(self) -> "MskClusterConfigurationInfoOutputReference":
        return typing.cast("MskClusterConfigurationInfoOutputReference", jsii.get(self, "configurationInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="currentVersion")
    def current_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "currentVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInfo")
    def encryption_info(self) -> "MskClusterEncryptionInfoOutputReference":
        return typing.cast("MskClusterEncryptionInfoOutputReference", jsii.get(self, "encryptionInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInfo")
    def logging_info(self) -> "MskClusterLoggingInfoOutputReference":
        return typing.cast("MskClusterLoggingInfoOutputReference", jsii.get(self, "loggingInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openMonitoring")
    def open_monitoring(self) -> "MskClusterOpenMonitoringOutputReference":
        return typing.cast("MskClusterOpenMonitoringOutputReference", jsii.get(self, "openMonitoring"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MskClusterTimeoutsOutputReference":
        return typing.cast("MskClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectString")
    def zookeeper_connect_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectString"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectStringTls")
    def zookeeper_connect_string_tls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectStringTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerNodeGroupInfoInput")
    def broker_node_group_info_input(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfo"]:
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfo"], jsii.get(self, "brokerNodeGroupInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientAuthenticationInput")
    def client_authentication_input(
        self,
    ) -> typing.Optional["MskClusterClientAuthentication"]:
        return typing.cast(typing.Optional["MskClusterClientAuthentication"], jsii.get(self, "clientAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInfoInput")
    def configuration_info_input(
        self,
    ) -> typing.Optional["MskClusterConfigurationInfo"]:
        return typing.cast(typing.Optional["MskClusterConfigurationInfo"], jsii.get(self, "configurationInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInfoInput")
    def encryption_info_input(self) -> typing.Optional["MskClusterEncryptionInfo"]:
        return typing.cast(typing.Optional["MskClusterEncryptionInfo"], jsii.get(self, "encryptionInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedMonitoringInput")
    def enhanced_monitoring_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enhancedMonitoringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersionInput")
    def kafka_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kafkaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInfoInput")
    def logging_info_input(self) -> typing.Optional["MskClusterLoggingInfo"]:
        return typing.cast(typing.Optional["MskClusterLoggingInfo"], jsii.get(self, "loggingInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodesInput")
    def number_of_broker_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfBrokerNodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openMonitoringInput")
    def open_monitoring_input(self) -> typing.Optional["MskClusterOpenMonitoring"]:
        return typing.cast(typing.Optional["MskClusterOpenMonitoring"], jsii.get(self, "openMonitoringInput"))

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
    ) -> typing.Optional[typing.Union["MskClusterTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["MskClusterTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enhancedMonitoring")
    def enhanced_monitoring(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enhancedMonitoring"))

    @enhanced_monitoring.setter
    def enhanced_monitoring(self, value: builtins.str) -> None:
        jsii.set(self, "enhancedMonitoring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersion")
    def kafka_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kafkaVersion"))

    @kafka_version.setter
    def kafka_version(self, value: builtins.str) -> None:
        jsii.set(self, "kafkaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfBrokerNodes")
    def number_of_broker_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfBrokerNodes"))

    @number_of_broker_nodes.setter
    def number_of_broker_nodes(self, value: jsii.Number) -> None:
        jsii.set(self, "numberOfBrokerNodes", value)

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
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfo",
    jsii_struct_bases=[],
    name_mapping={
        "client_subnets": "clientSubnets",
        "instance_type": "instanceType",
        "security_groups": "securityGroups",
        "az_distribution": "azDistribution",
        "connectivity_info": "connectivityInfo",
        "ebs_volume_size": "ebsVolumeSize",
        "storage_info": "storageInfo",
    },
)
class MskClusterBrokerNodeGroupInfo:
    def __init__(
        self,
        *,
        client_subnets: typing.Sequence[builtins.str],
        instance_type: builtins.str,
        security_groups: typing.Sequence[builtins.str],
        az_distribution: typing.Optional[builtins.str] = None,
        connectivity_info: typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfo"] = None,
        ebs_volume_size: typing.Optional[jsii.Number] = None,
        storage_info: typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"] = None,
    ) -> None:
        '''
        :param client_subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.
        :param az_distribution: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.
        :param connectivity_info: connectivity_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#connectivity_info MskCluster#connectivity_info}
        :param ebs_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.
        :param storage_info: storage_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#storage_info MskCluster#storage_info}
        '''
        if isinstance(connectivity_info, dict):
            connectivity_info = MskClusterBrokerNodeGroupInfoConnectivityInfo(**connectivity_info)
        if isinstance(storage_info, dict):
            storage_info = MskClusterBrokerNodeGroupInfoStorageInfo(**storage_info)
        self._values: typing.Dict[str, typing.Any] = {
            "client_subnets": client_subnets,
            "instance_type": instance_type,
            "security_groups": security_groups,
        }
        if az_distribution is not None:
            self._values["az_distribution"] = az_distribution
        if connectivity_info is not None:
            self._values["connectivity_info"] = connectivity_info
        if ebs_volume_size is not None:
            self._values["ebs_volume_size"] = ebs_volume_size
        if storage_info is not None:
            self._values["storage_info"] = storage_info

    @builtins.property
    def client_subnets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_subnets MskCluster#client_subnets}.'''
        result = self._values.get("client_subnets")
        assert result is not None, "Required property 'client_subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#instance_type MskCluster#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#security_groups MskCluster#security_groups}.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def az_distribution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#az_distribution MskCluster#az_distribution}.'''
        result = self._values.get("az_distribution")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connectivity_info(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfo"]:
        '''connectivity_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#connectivity_info MskCluster#connectivity_info}
        '''
        result = self._values.get("connectivity_info")
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfo"], result)

    @builtins.property
    def ebs_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_volume_size MskCluster#ebs_volume_size}.'''
        result = self._values.get("ebs_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_info(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"]:
        '''storage_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#storage_info MskCluster#storage_info}
        '''
        result = self._values.get("storage_info")
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoConnectivityInfo",
    jsii_struct_bases=[],
    name_mapping={"public_access": "publicAccess"},
)
class MskClusterBrokerNodeGroupInfoConnectivityInfo:
    def __init__(
        self,
        *,
        public_access: typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess"] = None,
    ) -> None:
        '''
        :param public_access: public_access block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#public_access MskCluster#public_access}
        '''
        if isinstance(public_access, dict):
            public_access = MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess(**public_access)
        self._values: typing.Dict[str, typing.Any] = {}
        if public_access is not None:
            self._values["public_access"] = public_access

    @builtins.property
    def public_access(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess"]:
        '''public_access block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#public_access MskCluster#public_access}
        '''
        result = self._values.get("public_access")
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfoConnectivityInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterBrokerNodeGroupInfoConnectivityInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoConnectivityInfoOutputReference",
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

    @jsii.member(jsii_name="putPublicAccess")
    def put_public_access(self, *, type: typing.Optional[builtins.str] = None) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#type MskCluster#type}.
        '''
        value = MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess(type=type)

        return typing.cast(None, jsii.invoke(self, "putPublicAccess", [value]))

    @jsii.member(jsii_name="resetPublicAccess")
    def reset_public_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccess", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccess")
    def public_access(
        self,
    ) -> "MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccessOutputReference":
        return typing.cast("MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccessOutputReference", jsii.get(self, "publicAccess"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessInput")
    def public_access_input(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess"]:
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess"], jsii.get(self, "publicAccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess",
    jsii_struct_bases=[],
    name_mapping={"type": "type"},
)
class MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess:
    def __init__(self, *, type: typing.Optional[builtins.str] = None) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#type MskCluster#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#type MskCluster#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccessOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccessOutputReference",
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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterBrokerNodeGroupInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoOutputReference",
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

    @jsii.member(jsii_name="putConnectivityInfo")
    def put_connectivity_info(
        self,
        *,
        public_access: typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess] = None,
    ) -> None:
        '''
        :param public_access: public_access block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#public_access MskCluster#public_access}
        '''
        value = MskClusterBrokerNodeGroupInfoConnectivityInfo(
            public_access=public_access
        )

        return typing.cast(None, jsii.invoke(self, "putConnectivityInfo", [value]))

    @jsii.member(jsii_name="putStorageInfo")
    def put_storage_info(
        self,
        *,
        ebs_storage_info: typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo"] = None,
    ) -> None:
        '''
        :param ebs_storage_info: ebs_storage_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_storage_info MskCluster#ebs_storage_info}
        '''
        value = MskClusterBrokerNodeGroupInfoStorageInfo(
            ebs_storage_info=ebs_storage_info
        )

        return typing.cast(None, jsii.invoke(self, "putStorageInfo", [value]))

    @jsii.member(jsii_name="resetAzDistribution")
    def reset_az_distribution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzDistribution", []))

    @jsii.member(jsii_name="resetConnectivityInfo")
    def reset_connectivity_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectivityInfo", []))

    @jsii.member(jsii_name="resetEbsVolumeSize")
    def reset_ebs_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolumeSize", []))

    @jsii.member(jsii_name="resetStorageInfo")
    def reset_storage_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageInfo", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectivityInfo")
    def connectivity_info(
        self,
    ) -> MskClusterBrokerNodeGroupInfoConnectivityInfoOutputReference:
        return typing.cast(MskClusterBrokerNodeGroupInfoConnectivityInfoOutputReference, jsii.get(self, "connectivityInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageInfo")
    def storage_info(self) -> "MskClusterBrokerNodeGroupInfoStorageInfoOutputReference":
        return typing.cast("MskClusterBrokerNodeGroupInfoStorageInfoOutputReference", jsii.get(self, "storageInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azDistributionInput")
    def az_distribution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azDistributionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnetsInput")
    def client_subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clientSubnetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectivityInfoInput")
    def connectivity_info_input(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoConnectivityInfo], jsii.get(self, "connectivityInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeSizeInput")
    def ebs_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsVolumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageInfoInput")
    def storage_info_input(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"]:
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfo"], jsii.get(self, "storageInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="azDistribution")
    def az_distribution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azDistribution"))

    @az_distribution.setter
    def az_distribution(self, value: builtins.str) -> None:
        jsii.set(self, "azDistribution", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSubnets")
    def client_subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientSubnets"))

    @client_subnets.setter
    def client_subnets(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clientSubnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeSize")
    def ebs_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsVolumeSize"))

    @ebs_volume_size.setter
    def ebs_volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "ebsVolumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterBrokerNodeGroupInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfo",
    jsii_struct_bases=[],
    name_mapping={"ebs_storage_info": "ebsStorageInfo"},
)
class MskClusterBrokerNodeGroupInfoStorageInfo:
    def __init__(
        self,
        *,
        ebs_storage_info: typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo"] = None,
    ) -> None:
        '''
        :param ebs_storage_info: ebs_storage_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_storage_info MskCluster#ebs_storage_info}
        '''
        if isinstance(ebs_storage_info, dict):
            ebs_storage_info = MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo(**ebs_storage_info)
        self._values: typing.Dict[str, typing.Any] = {}
        if ebs_storage_info is not None:
            self._values["ebs_storage_info"] = ebs_storage_info

    @builtins.property
    def ebs_storage_info(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo"]:
        '''ebs_storage_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#ebs_storage_info MskCluster#ebs_storage_info}
        '''
        result = self._values.get("ebs_storage_info")
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfoStorageInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo",
    jsii_struct_bases=[],
    name_mapping={
        "provisioned_throughput": "provisionedThroughput",
        "volume_size": "volumeSize",
    },
)
class MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo:
    def __init__(
        self,
        *,
        provisioned_throughput: typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput"] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param provisioned_throughput: provisioned_throughput block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#provisioned_throughput MskCluster#provisioned_throughput}
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_size MskCluster#volume_size}.
        '''
        if isinstance(provisioned_throughput, dict):
            provisioned_throughput = MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput(**provisioned_throughput)
        self._values: typing.Dict[str, typing.Any] = {}
        if provisioned_throughput is not None:
            self._values["provisioned_throughput"] = provisioned_throughput
        if volume_size is not None:
            self._values["volume_size"] = volume_size

    @builtins.property
    def provisioned_throughput(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput"]:
        '''provisioned_throughput block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#provisioned_throughput MskCluster#provisioned_throughput}
        '''
        result = self._values.get("provisioned_throughput")
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput"], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_size MskCluster#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoOutputReference",
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

    @jsii.member(jsii_name="putProvisionedThroughput")
    def put_provisioned_throughput(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        volume_throughput: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param volume_throughput: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_throughput MskCluster#volume_throughput}.
        '''
        value = MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput(
            enabled=enabled, volume_throughput=volume_throughput
        )

        return typing.cast(None, jsii.invoke(self, "putProvisionedThroughput", [value]))

    @jsii.member(jsii_name="resetProvisionedThroughput")
    def reset_provisioned_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisionedThroughput", []))

    @jsii.member(jsii_name="resetVolumeSize")
    def reset_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeSize", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedThroughput")
    def provisioned_throughput(
        self,
    ) -> "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughputOutputReference":
        return typing.cast("MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughputOutputReference", jsii.get(self, "provisionedThroughput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedThroughputInput")
    def provisioned_throughput_input(
        self,
    ) -> typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput"]:
        return typing.cast(typing.Optional["MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput"], jsii.get(self, "provisionedThroughputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInput")
    def volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @volume_size.setter
    def volume_size(self, value: jsii.Number) -> None:
        jsii.set(self, "volumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "volume_throughput": "volumeThroughput"},
)
class MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        volume_throughput: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param volume_throughput: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_throughput MskCluster#volume_throughput}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if volume_throughput is not None:
            self._values["volume_throughput"] = volume_throughput

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def volume_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_throughput MskCluster#volume_throughput}.'''
        result = self._values.get("volume_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughputOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughputOutputReference",
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

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetVolumeThroughput")
    def reset_volume_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeThroughput", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeThroughputInput")
    def volume_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeThroughputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeThroughput")
    def volume_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeThroughput"))

    @volume_throughput.setter
    def volume_throughput(self, value: jsii.Number) -> None:
        jsii.set(self, "volumeThroughput", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterBrokerNodeGroupInfoStorageInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterBrokerNodeGroupInfoStorageInfoOutputReference",
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

    @jsii.member(jsii_name="putEbsStorageInfo")
    def put_ebs_storage_info(
        self,
        *,
        provisioned_throughput: typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param provisioned_throughput: provisioned_throughput block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#provisioned_throughput MskCluster#provisioned_throughput}
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#volume_size MskCluster#volume_size}.
        '''
        value = MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo(
            provisioned_throughput=provisioned_throughput, volume_size=volume_size
        )

        return typing.cast(None, jsii.invoke(self, "putEbsStorageInfo", [value]))

    @jsii.member(jsii_name="resetEbsStorageInfo")
    def reset_ebs_storage_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsStorageInfo", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsStorageInfo")
    def ebs_storage_info(
        self,
    ) -> MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoOutputReference:
        return typing.cast(MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoOutputReference, jsii.get(self, "ebsStorageInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsStorageInfoInput")
    def ebs_storage_info_input(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo], jsii.get(self, "ebsStorageInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfo]:
        return typing.cast(typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterBrokerNodeGroupInfoStorageInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthentication",
    jsii_struct_bases=[],
    name_mapping={"sasl": "sasl", "tls": "tls", "unauthenticated": "unauthenticated"},
)
class MskClusterClientAuthentication:
    def __init__(
        self,
        *,
        sasl: typing.Optional["MskClusterClientAuthenticationSasl"] = None,
        tls: typing.Optional["MskClusterClientAuthenticationTls"] = None,
        unauthenticated: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param sasl: sasl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        :param tls: tls block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        :param unauthenticated: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#unauthenticated MskCluster#unauthenticated}.
        '''
        if isinstance(sasl, dict):
            sasl = MskClusterClientAuthenticationSasl(**sasl)
        if isinstance(tls, dict):
            tls = MskClusterClientAuthenticationTls(**tls)
        self._values: typing.Dict[str, typing.Any] = {}
        if sasl is not None:
            self._values["sasl"] = sasl
        if tls is not None:
            self._values["tls"] = tls
        if unauthenticated is not None:
            self._values["unauthenticated"] = unauthenticated

    @builtins.property
    def sasl(self) -> typing.Optional["MskClusterClientAuthenticationSasl"]:
        '''sasl block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#sasl MskCluster#sasl}
        '''
        result = self._values.get("sasl")
        return typing.cast(typing.Optional["MskClusterClientAuthenticationSasl"], result)

    @builtins.property
    def tls(self) -> typing.Optional["MskClusterClientAuthenticationTls"]:
        '''tls block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tls MskCluster#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional["MskClusterClientAuthenticationTls"], result)

    @builtins.property
    def unauthenticated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#unauthenticated MskCluster#unauthenticated}.'''
        result = self._values.get("unauthenticated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationOutputReference",
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

    @jsii.member(jsii_name="putSasl")
    def put_sasl(
        self,
        *,
        iam: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        scram: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param iam: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.
        :param scram: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.
        '''
        value = MskClusterClientAuthenticationSasl(iam=iam, scram=scram)

        return typing.cast(None, jsii.invoke(self, "putSasl", [value]))

    @jsii.member(jsii_name="putTls")
    def put_tls(
        self,
        *,
        certificate_authority_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param certificate_authority_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.
        '''
        value = MskClusterClientAuthenticationTls(
            certificate_authority_arns=certificate_authority_arns
        )

        return typing.cast(None, jsii.invoke(self, "putTls", [value]))

    @jsii.member(jsii_name="resetSasl")
    def reset_sasl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSasl", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @jsii.member(jsii_name="resetUnauthenticated")
    def reset_unauthenticated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnauthenticated", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sasl")
    def sasl(self) -> "MskClusterClientAuthenticationSaslOutputReference":
        return typing.cast("MskClusterClientAuthenticationSaslOutputReference", jsii.get(self, "sasl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tls")
    def tls(self) -> "MskClusterClientAuthenticationTlsOutputReference":
        return typing.cast("MskClusterClientAuthenticationTlsOutputReference", jsii.get(self, "tls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslInput")
    def sasl_input(self) -> typing.Optional["MskClusterClientAuthenticationSasl"]:
        return typing.cast(typing.Optional["MskClusterClientAuthenticationSasl"], jsii.get(self, "saslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsInput")
    def tls_input(self) -> typing.Optional["MskClusterClientAuthenticationTls"]:
        return typing.cast(typing.Optional["MskClusterClientAuthenticationTls"], jsii.get(self, "tlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unauthenticatedInput")
    def unauthenticated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "unauthenticatedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unauthenticated")
    def unauthenticated(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "unauthenticated"))

    @unauthenticated.setter
    def unauthenticated(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "unauthenticated", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthentication]:
        return typing.cast(typing.Optional[MskClusterClientAuthentication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthentication],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationSasl",
    jsii_struct_bases=[],
    name_mapping={"iam": "iam", "scram": "scram"},
)
class MskClusterClientAuthenticationSasl:
    def __init__(
        self,
        *,
        iam: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        scram: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param iam: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.
        :param scram: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam
        if scram is not None:
            self._values["scram"] = scram

    @builtins.property
    def iam(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#iam MskCluster#iam}.'''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def scram(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#scram MskCluster#scram}.'''
        result = self._values.get("scram")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthenticationSasl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationSaslOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationSaslOutputReference",
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

    @jsii.member(jsii_name="resetIam")
    def reset_iam(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIam", []))

    @jsii.member(jsii_name="resetScram")
    def reset_scram(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScram", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamInput")
    def iam_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "iamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scramInput")
    def scram_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "scramInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iam")
    def iam(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "iam"))

    @iam.setter
    def iam(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "iam", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scram")
    def scram(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "scram"))

    @scram.setter
    def scram(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "scram", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthenticationSasl]:
        return typing.cast(typing.Optional[MskClusterClientAuthenticationSasl], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthenticationSasl],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationTls",
    jsii_struct_bases=[],
    name_mapping={"certificate_authority_arns": "certificateAuthorityArns"},
)
class MskClusterClientAuthenticationTls:
    def __init__(
        self,
        *,
        certificate_authority_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param certificate_authority_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if certificate_authority_arns is not None:
            self._values["certificate_authority_arns"] = certificate_authority_arns

    @builtins.property
    def certificate_authority_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#certificate_authority_arns MskCluster#certificate_authority_arns}.'''
        result = self._values.get("certificate_authority_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterClientAuthenticationTls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterClientAuthenticationTlsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterClientAuthenticationTlsOutputReference",
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

    @jsii.member(jsii_name="resetCertificateAuthorityArns")
    def reset_certificate_authority_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateAuthorityArns", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateAuthorityArnsInput")
    def certificate_authority_arns_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "certificateAuthorityArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateAuthorityArns")
    def certificate_authority_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "certificateAuthorityArns"))

    @certificate_authority_arns.setter
    def certificate_authority_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "certificateAuthorityArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterClientAuthenticationTls]:
        return typing.cast(typing.Optional[MskClusterClientAuthenticationTls], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterClientAuthenticationTls],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "broker_node_group_info": "brokerNodeGroupInfo",
        "cluster_name": "clusterName",
        "kafka_version": "kafkaVersion",
        "number_of_broker_nodes": "numberOfBrokerNodes",
        "client_authentication": "clientAuthentication",
        "configuration_info": "configurationInfo",
        "encryption_info": "encryptionInfo",
        "enhanced_monitoring": "enhancedMonitoring",
        "id": "id",
        "logging_info": "loggingInfo",
        "open_monitoring": "openMonitoring",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class MskClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        broker_node_group_info: MskClusterBrokerNodeGroupInfo,
        cluster_name: builtins.str,
        kafka_version: builtins.str,
        number_of_broker_nodes: jsii.Number,
        client_authentication: typing.Optional[MskClusterClientAuthentication] = None,
        configuration_info: typing.Optional["MskClusterConfigurationInfo"] = None,
        encryption_info: typing.Optional["MskClusterEncryptionInfo"] = None,
        enhanced_monitoring: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        logging_info: typing.Optional["MskClusterLoggingInfo"] = None,
        open_monitoring: typing.Optional["MskClusterOpenMonitoring"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["MskClusterTimeouts"] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param broker_node_group_info: broker_node_group_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.
        :param kafka_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.
        :param number_of_broker_nodes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.
        :param client_authentication: client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        :param configuration_info: configuration_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        :param encryption_info: encryption_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        :param enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#id MskCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param logging_info: logging_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        :param open_monitoring: open_monitoring block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(broker_node_group_info, dict):
            broker_node_group_info = MskClusterBrokerNodeGroupInfo(**broker_node_group_info)
        if isinstance(client_authentication, dict):
            client_authentication = MskClusterClientAuthentication(**client_authentication)
        if isinstance(configuration_info, dict):
            configuration_info = MskClusterConfigurationInfo(**configuration_info)
        if isinstance(encryption_info, dict):
            encryption_info = MskClusterEncryptionInfo(**encryption_info)
        if isinstance(logging_info, dict):
            logging_info = MskClusterLoggingInfo(**logging_info)
        if isinstance(open_monitoring, dict):
            open_monitoring = MskClusterOpenMonitoring(**open_monitoring)
        if isinstance(timeouts, dict):
            timeouts = MskClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "broker_node_group_info": broker_node_group_info,
            "cluster_name": cluster_name,
            "kafka_version": kafka_version,
            "number_of_broker_nodes": number_of_broker_nodes,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if client_authentication is not None:
            self._values["client_authentication"] = client_authentication
        if configuration_info is not None:
            self._values["configuration_info"] = configuration_info
        if encryption_info is not None:
            self._values["encryption_info"] = encryption_info
        if enhanced_monitoring is not None:
            self._values["enhanced_monitoring"] = enhanced_monitoring
        if id is not None:
            self._values["id"] = id
        if logging_info is not None:
            self._values["logging_info"] = logging_info
        if open_monitoring is not None:
            self._values["open_monitoring"] = open_monitoring
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
    def broker_node_group_info(self) -> MskClusterBrokerNodeGroupInfo:
        '''broker_node_group_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_node_group_info MskCluster#broker_node_group_info}
        '''
        result = self._values.get("broker_node_group_info")
        assert result is not None, "Required property 'broker_node_group_info' is missing"
        return typing.cast(MskClusterBrokerNodeGroupInfo, result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cluster_name MskCluster#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kafka_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#kafka_version MskCluster#kafka_version}.'''
        result = self._values.get("kafka_version")
        assert result is not None, "Required property 'kafka_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_broker_nodes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#number_of_broker_nodes MskCluster#number_of_broker_nodes}.'''
        result = self._values.get("number_of_broker_nodes")
        assert result is not None, "Required property 'number_of_broker_nodes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def client_authentication(self) -> typing.Optional[MskClusterClientAuthentication]:
        '''client_authentication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_authentication MskCluster#client_authentication}
        '''
        result = self._values.get("client_authentication")
        return typing.cast(typing.Optional[MskClusterClientAuthentication], result)

    @builtins.property
    def configuration_info(self) -> typing.Optional["MskClusterConfigurationInfo"]:
        '''configuration_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#configuration_info MskCluster#configuration_info}
        '''
        result = self._values.get("configuration_info")
        return typing.cast(typing.Optional["MskClusterConfigurationInfo"], result)

    @builtins.property
    def encryption_info(self) -> typing.Optional["MskClusterEncryptionInfo"]:
        '''encryption_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_info MskCluster#encryption_info}
        '''
        result = self._values.get("encryption_info")
        return typing.cast(typing.Optional["MskClusterEncryptionInfo"], result)

    @builtins.property
    def enhanced_monitoring(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enhanced_monitoring MskCluster#enhanced_monitoring}.'''
        result = self._values.get("enhanced_monitoring")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#id MskCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging_info(self) -> typing.Optional["MskClusterLoggingInfo"]:
        '''logging_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#logging_info MskCluster#logging_info}
        '''
        result = self._values.get("logging_info")
        return typing.cast(typing.Optional["MskClusterLoggingInfo"], result)

    @builtins.property
    def open_monitoring(self) -> typing.Optional["MskClusterOpenMonitoring"]:
        '''open_monitoring block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#open_monitoring MskCluster#open_monitoring}
        '''
        result = self._values.get("open_monitoring")
        return typing.cast(typing.Optional["MskClusterOpenMonitoring"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags MskCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#tags_all MskCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MskClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#timeouts MskCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MskClusterTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfigurationInfo",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class MskClusterConfigurationInfo:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#arn MskCluster#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#revision MskCluster#revision}.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterConfigurationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterConfigurationInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterConfigurationInfoOutputReference",
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
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revisionInput")
    def revision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "revisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @revision.setter
    def revision(self, value: jsii.Number) -> None:
        jsii.set(self, "revision", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterConfigurationInfo]:
        return typing.cast(typing.Optional[MskClusterConfigurationInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterConfigurationInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfo",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_at_rest_kms_key_arn": "encryptionAtRestKmsKeyArn",
        "encryption_in_transit": "encryptionInTransit",
    },
)
class MskClusterEncryptionInfo:
    def __init__(
        self,
        *,
        encryption_at_rest_kms_key_arn: typing.Optional[builtins.str] = None,
        encryption_in_transit: typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"] = None,
    ) -> None:
        '''
        :param encryption_at_rest_kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.
        :param encryption_in_transit: encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        if isinstance(encryption_in_transit, dict):
            encryption_in_transit = MskClusterEncryptionInfoEncryptionInTransit(**encryption_in_transit)
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_at_rest_kms_key_arn is not None:
            self._values["encryption_at_rest_kms_key_arn"] = encryption_at_rest_kms_key_arn
        if encryption_in_transit is not None:
            self._values["encryption_in_transit"] = encryption_in_transit

    @builtins.property
    def encryption_at_rest_kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_at_rest_kms_key_arn MskCluster#encryption_at_rest_kms_key_arn}.'''
        result = self._values.get("encryption_at_rest_kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_in_transit(
        self,
    ) -> typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"]:
        '''encryption_in_transit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#encryption_in_transit MskCluster#encryption_in_transit}
        '''
        result = self._values.get("encryption_in_transit")
        return typing.cast(typing.Optional["MskClusterEncryptionInfoEncryptionInTransit"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterEncryptionInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoEncryptionInTransit",
    jsii_struct_bases=[],
    name_mapping={"client_broker": "clientBroker", "in_cluster": "inCluster"},
)
class MskClusterEncryptionInfoEncryptionInTransit:
    def __init__(
        self,
        *,
        client_broker: typing.Optional[builtins.str] = None,
        in_cluster: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.
        :param in_cluster: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_broker is not None:
            self._values["client_broker"] = client_broker
        if in_cluster is not None:
            self._values["in_cluster"] = in_cluster

    @builtins.property
    def client_broker(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.'''
        result = self._values.get("client_broker")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def in_cluster(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.'''
        result = self._values.get("in_cluster")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterEncryptionInfoEncryptionInTransit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterEncryptionInfoEncryptionInTransitOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoEncryptionInTransitOutputReference",
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

    @jsii.member(jsii_name="resetClientBroker")
    def reset_client_broker(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientBroker", []))

    @jsii.member(jsii_name="resetInCluster")
    def reset_in_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInCluster", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientBrokerInput")
    def client_broker_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inClusterInput")
    def in_cluster_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "inClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientBroker")
    def client_broker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientBroker"))

    @client_broker.setter
    def client_broker(self, value: builtins.str) -> None:
        jsii.set(self, "clientBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inCluster")
    def in_cluster(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "inCluster"))

    @in_cluster.setter
    def in_cluster(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "inCluster", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterEncryptionInfoEncryptionInTransit]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfoEncryptionInTransit], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterEncryptionInfoEncryptionInTransit],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterEncryptionInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterEncryptionInfoOutputReference",
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

    @jsii.member(jsii_name="putEncryptionInTransit")
    def put_encryption_in_transit(
        self,
        *,
        client_broker: typing.Optional[builtins.str] = None,
        in_cluster: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param client_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#client_broker MskCluster#client_broker}.
        :param in_cluster: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#in_cluster MskCluster#in_cluster}.
        '''
        value = MskClusterEncryptionInfoEncryptionInTransit(
            client_broker=client_broker, in_cluster=in_cluster
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionInTransit", [value]))

    @jsii.member(jsii_name="resetEncryptionAtRestKmsKeyArn")
    def reset_encryption_at_rest_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAtRestKmsKeyArn", []))

    @jsii.member(jsii_name="resetEncryptionInTransit")
    def reset_encryption_in_transit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionInTransit", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInTransit")
    def encryption_in_transit(
        self,
    ) -> MskClusterEncryptionInfoEncryptionInTransitOutputReference:
        return typing.cast(MskClusterEncryptionInfoEncryptionInTransitOutputReference, jsii.get(self, "encryptionInTransit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionAtRestKmsKeyArnInput")
    def encryption_at_rest_kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionAtRestKmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInTransitInput")
    def encryption_in_transit_input(
        self,
    ) -> typing.Optional[MskClusterEncryptionInfoEncryptionInTransit]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfoEncryptionInTransit], jsii.get(self, "encryptionInTransitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionAtRestKmsKeyArn")
    def encryption_at_rest_kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAtRestKmsKeyArn"))

    @encryption_at_rest_kms_key_arn.setter
    def encryption_at_rest_kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionAtRestKmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterEncryptionInfo]:
        return typing.cast(typing.Optional[MskClusterEncryptionInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterEncryptionInfo]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfo",
    jsii_struct_bases=[],
    name_mapping={"broker_logs": "brokerLogs"},
)
class MskClusterLoggingInfo:
    def __init__(self, *, broker_logs: "MskClusterLoggingInfoBrokerLogs") -> None:
        '''
        :param broker_logs: broker_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        if isinstance(broker_logs, dict):
            broker_logs = MskClusterLoggingInfoBrokerLogs(**broker_logs)
        self._values: typing.Dict[str, typing.Any] = {
            "broker_logs": broker_logs,
        }

    @builtins.property
    def broker_logs(self) -> "MskClusterLoggingInfoBrokerLogs":
        '''broker_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#broker_logs MskCluster#broker_logs}
        '''
        result = self._values.get("broker_logs")
        assert result is not None, "Required property 'broker_logs' is missing"
        return typing.cast("MskClusterLoggingInfoBrokerLogs", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogs",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_logs": "cloudwatchLogs",
        "firehose": "firehose",
        "s3": "s3",
    },
)
class MskClusterLoggingInfoBrokerLogs:
    def __init__(
        self,
        *,
        cloudwatch_logs: typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"] = None,
        firehose: typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"] = None,
        s3: typing.Optional["MskClusterLoggingInfoBrokerLogsS3"] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        if isinstance(cloudwatch_logs, dict):
            cloudwatch_logs = MskClusterLoggingInfoBrokerLogsCloudwatchLogs(**cloudwatch_logs)
        if isinstance(firehose, dict):
            firehose = MskClusterLoggingInfoBrokerLogsFirehose(**firehose)
        if isinstance(s3, dict):
            s3 = MskClusterLoggingInfoBrokerLogsS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloudwatch_logs is not None:
            self._values["cloudwatch_logs"] = cloudwatch_logs
        if firehose is not None:
            self._values["firehose"] = firehose
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloudwatch_logs(
        self,
    ) -> typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"]:
        '''cloudwatch_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        '''
        result = self._values.get("cloudwatch_logs")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsCloudwatchLogs"], result)

    @builtins.property
    def firehose(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"]:
        '''firehose block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsFirehose"], result)

    @builtins.property
    def s3(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsS3"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsCloudwatchLogs",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "log_group": "logGroup"},
)
class MskClusterLoggingInfoBrokerLogsCloudwatchLogs:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if log_group is not None:
            self._values["log_group"] = log_group

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def log_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.'''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsCloudwatchLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference",
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

    @jsii.member(jsii_name="resetLogGroup")
    def reset_log_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogGroup", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupInput")
    def log_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: builtins.str) -> None:
        jsii.set(self, "logGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsFirehose",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "delivery_stream": "deliveryStream"},
)
class MskClusterLoggingInfoBrokerLogsFirehose:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if delivery_stream is not None:
            self._values["delivery_stream"] = delivery_stream

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def delivery_stream(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.'''
        result = self._values.get("delivery_stream")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsFirehoseOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsFirehoseOutputReference",
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

    @jsii.member(jsii_name="resetDeliveryStream")
    def reset_delivery_stream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryStream", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamInput")
    def delivery_stream_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStream"))

    @delivery_stream.setter
    def delivery_stream(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStream", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterLoggingInfoBrokerLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsOutputReference",
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

    @jsii.member(jsii_name="putCloudwatchLogs")
    def put_cloudwatch_logs(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#log_group MskCluster#log_group}.
        '''
        value = MskClusterLoggingInfoBrokerLogsCloudwatchLogs(
            enabled=enabled, log_group=log_group
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchLogs", [value]))

    @jsii.member(jsii_name="putFirehose")
    def put_firehose(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delivery_stream MskCluster#delivery_stream}.
        '''
        value = MskClusterLoggingInfoBrokerLogsFirehose(
            enabled=enabled, delivery_stream=delivery_stream
        )

        return typing.cast(None, jsii.invoke(self, "putFirehose", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.
        '''
        value = MskClusterLoggingInfoBrokerLogsS3(
            enabled=enabled, bucket=bucket, prefix=prefix
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="resetCloudwatchLogs")
    def reset_cloudwatch_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogs", []))

    @jsii.member(jsii_name="resetFirehose")
    def reset_firehose(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehose", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogs")
    def cloudwatch_logs(
        self,
    ) -> MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference, jsii.get(self, "cloudwatchLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehose")
    def firehose(self) -> MskClusterLoggingInfoBrokerLogsFirehoseOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsFirehoseOutputReference, jsii.get(self, "firehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "MskClusterLoggingInfoBrokerLogsS3OutputReference":
        return typing.cast("MskClusterLoggingInfoBrokerLogsS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsInput")
    def cloudwatch_logs_input(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs], jsii.get(self, "cloudwatchLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseInput")
    def firehose_input(
        self,
    ) -> typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose], jsii.get(self, "firehoseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["MskClusterLoggingInfoBrokerLogsS3"]:
        return typing.cast(typing.Optional["MskClusterLoggingInfoBrokerLogsS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsS3",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "bucket": "bucket", "prefix": "prefix"},
)
class MskClusterLoggingInfoBrokerLogsS3:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled MskCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#bucket MskCluster#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prefix MskCluster#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterLoggingInfoBrokerLogsS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterLoggingInfoBrokerLogsS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoBrokerLogsS3OutputReference",
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

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogsS3]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogsS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterLoggingInfoBrokerLogsS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterLoggingInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterLoggingInfoOutputReference",
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

    @jsii.member(jsii_name="putBrokerLogs")
    def put_broker_logs(
        self,
        *,
        cloudwatch_logs: typing.Optional[MskClusterLoggingInfoBrokerLogsCloudwatchLogs] = None,
        firehose: typing.Optional[MskClusterLoggingInfoBrokerLogsFirehose] = None,
        s3: typing.Optional[MskClusterLoggingInfoBrokerLogsS3] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#cloudwatch_logs MskCluster#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#firehose MskCluster#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#s3 MskCluster#s3}
        '''
        value = MskClusterLoggingInfoBrokerLogs(
            cloudwatch_logs=cloudwatch_logs, firehose=firehose, s3=s3
        )

        return typing.cast(None, jsii.invoke(self, "putBrokerLogs", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerLogs")
    def broker_logs(self) -> MskClusterLoggingInfoBrokerLogsOutputReference:
        return typing.cast(MskClusterLoggingInfoBrokerLogsOutputReference, jsii.get(self, "brokerLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerLogsInput")
    def broker_logs_input(self) -> typing.Optional[MskClusterLoggingInfoBrokerLogs]:
        return typing.cast(typing.Optional[MskClusterLoggingInfoBrokerLogs], jsii.get(self, "brokerLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterLoggingInfo]:
        return typing.cast(typing.Optional[MskClusterLoggingInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterLoggingInfo]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoring",
    jsii_struct_bases=[],
    name_mapping={"prometheus": "prometheus"},
)
class MskClusterOpenMonitoring:
    def __init__(self, *, prometheus: "MskClusterOpenMonitoringPrometheus") -> None:
        '''
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        if isinstance(prometheus, dict):
            prometheus = MskClusterOpenMonitoringPrometheus(**prometheus)
        self._values: typing.Dict[str, typing.Any] = {
            "prometheus": prometheus,
        }

    @builtins.property
    def prometheus(self) -> "MskClusterOpenMonitoringPrometheus":
        '''prometheus block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#prometheus MskCluster#prometheus}
        '''
        result = self._values.get("prometheus")
        assert result is not None, "Required property 'prometheus' is missing"
        return typing.cast("MskClusterOpenMonitoringPrometheus", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoring(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringOutputReference",
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

    @jsii.member(jsii_name="putPrometheus")
    def put_prometheus(
        self,
        *,
        jmx_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"] = None,
        node_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"] = None,
    ) -> None:
        '''
        :param jmx_exporter: jmx_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        :param node_exporter: node_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        value = MskClusterOpenMonitoringPrometheus(
            jmx_exporter=jmx_exporter, node_exporter=node_exporter
        )

        return typing.cast(None, jsii.invoke(self, "putPrometheus", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prometheus")
    def prometheus(self) -> "MskClusterOpenMonitoringPrometheusOutputReference":
        return typing.cast("MskClusterOpenMonitoringPrometheusOutputReference", jsii.get(self, "prometheus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prometheusInput")
    def prometheus_input(self) -> typing.Optional["MskClusterOpenMonitoringPrometheus"]:
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheus"], jsii.get(self, "prometheusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterOpenMonitoring]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoring], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MskClusterOpenMonitoring]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheus",
    jsii_struct_bases=[],
    name_mapping={"jmx_exporter": "jmxExporter", "node_exporter": "nodeExporter"},
)
class MskClusterOpenMonitoringPrometheus:
    def __init__(
        self,
        *,
        jmx_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"] = None,
        node_exporter: typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"] = None,
    ) -> None:
        '''
        :param jmx_exporter: jmx_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        :param node_exporter: node_exporter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        if isinstance(jmx_exporter, dict):
            jmx_exporter = MskClusterOpenMonitoringPrometheusJmxExporter(**jmx_exporter)
        if isinstance(node_exporter, dict):
            node_exporter = MskClusterOpenMonitoringPrometheusNodeExporter(**node_exporter)
        self._values: typing.Dict[str, typing.Any] = {}
        if jmx_exporter is not None:
            self._values["jmx_exporter"] = jmx_exporter
        if node_exporter is not None:
            self._values["node_exporter"] = node_exporter

    @builtins.property
    def jmx_exporter(
        self,
    ) -> typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"]:
        '''jmx_exporter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#jmx_exporter MskCluster#jmx_exporter}
        '''
        result = self._values.get("jmx_exporter")
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheusJmxExporter"], result)

    @builtins.property
    def node_exporter(
        self,
    ) -> typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"]:
        '''node_exporter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#node_exporter MskCluster#node_exporter}
        '''
        result = self._values.get("node_exporter")
        return typing.cast(typing.Optional["MskClusterOpenMonitoringPrometheusNodeExporter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusJmxExporter",
    jsii_struct_bases=[],
    name_mapping={"enabled_in_broker": "enabledInBroker"},
)
class MskClusterOpenMonitoringPrometheusJmxExporter:
    def __init__(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled_in_broker": enabled_in_broker,
        }

    @builtins.property
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.'''
        result = self._values.get("enabled_in_broker")
        assert result is not None, "Required property 'enabled_in_broker' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheusJmxExporter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringPrometheusJmxExporterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusJmxExporterOutputReference",
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
    @jsii.member(jsii_name="enabledInBrokerInput")
    def enabled_in_broker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInBroker")
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabledInBroker"))

    @enabled_in_broker.setter
    def enabled_in_broker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enabledInBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusNodeExporter",
    jsii_struct_bases=[],
    name_mapping={"enabled_in_broker": "enabledInBroker"},
)
class MskClusterOpenMonitoringPrometheusNodeExporter:
    def __init__(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled_in_broker": enabled_in_broker,
        }

    @builtins.property
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.'''
        result = self._values.get("enabled_in_broker")
        assert result is not None, "Required property 'enabled_in_broker' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterOpenMonitoringPrometheusNodeExporter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterOpenMonitoringPrometheusNodeExporterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusNodeExporterOutputReference",
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
    @jsii.member(jsii_name="enabledInBrokerInput")
    def enabled_in_broker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInBrokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInBroker")
    def enabled_in_broker(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabledInBroker"))

    @enabled_in_broker.setter
    def enabled_in_broker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enabledInBroker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskClusterOpenMonitoringPrometheusOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterOpenMonitoringPrometheusOutputReference",
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

    @jsii.member(jsii_name="putJmxExporter")
    def put_jmx_exporter(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        value = MskClusterOpenMonitoringPrometheusJmxExporter(
            enabled_in_broker=enabled_in_broker
        )

        return typing.cast(None, jsii.invoke(self, "putJmxExporter", [value]))

    @jsii.member(jsii_name="putNodeExporter")
    def put_node_exporter(
        self,
        *,
        enabled_in_broker: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled_in_broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#enabled_in_broker MskCluster#enabled_in_broker}.
        '''
        value = MskClusterOpenMonitoringPrometheusNodeExporter(
            enabled_in_broker=enabled_in_broker
        )

        return typing.cast(None, jsii.invoke(self, "putNodeExporter", [value]))

    @jsii.member(jsii_name="resetJmxExporter")
    def reset_jmx_exporter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJmxExporter", []))

    @jsii.member(jsii_name="resetNodeExporter")
    def reset_node_exporter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeExporter", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jmxExporter")
    def jmx_exporter(
        self,
    ) -> MskClusterOpenMonitoringPrometheusJmxExporterOutputReference:
        return typing.cast(MskClusterOpenMonitoringPrometheusJmxExporterOutputReference, jsii.get(self, "jmxExporter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeExporter")
    def node_exporter(
        self,
    ) -> MskClusterOpenMonitoringPrometheusNodeExporterOutputReference:
        return typing.cast(MskClusterOpenMonitoringPrometheusNodeExporterOutputReference, jsii.get(self, "nodeExporter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jmxExporterInput")
    def jmx_exporter_input(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusJmxExporter], jsii.get(self, "jmxExporterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeExporterInput")
    def node_exporter_input(
        self,
    ) -> typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheusNodeExporter], jsii.get(self, "nodeExporterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskClusterOpenMonitoringPrometheus]:
        return typing.cast(typing.Optional[MskClusterOpenMonitoringPrometheus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskClusterOpenMonitoringPrometheus],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class MskClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#create MskCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#delete MskCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_cluster#update MskCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskClusterTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MskClusterTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MskClusterTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MskClusterTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration aws_msk_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        server_properties: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kafka_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration aws_msk_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.
        :param server_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#id MskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kafka_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskConfigurationConfig(
            name=name,
            server_properties=server_properties,
            description=description,
            id=id,
            kafka_versions=kafka_versions,
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

    @jsii.member(jsii_name="resetKafkaVersions")
    def reset_kafka_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKafkaVersions", []))

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
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaVersionsInput")
    def kafka_versions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "kafkaVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverPropertiesInput")
    def server_properties_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverPropertiesInput"))

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
    @jsii.member(jsii_name="kafkaVersions")
    def kafka_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "kafkaVersions"))

    @kafka_versions.setter
    def kafka_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "kafkaVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverProperties")
    def server_properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverProperties"))

    @server_properties.setter
    def server_properties(self, value: builtins.str) -> None:
        jsii.set(self, "serverProperties", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "server_properties": "serverProperties",
        "description": "description",
        "id": "id",
        "kafka_versions": "kafkaVersions",
    },
)
class MskConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        server_properties: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kafka_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.
        :param server_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#id MskConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kafka_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "server_properties": server_properties,
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
        if kafka_versions is not None:
            self._values["kafka_versions"] = kafka_versions

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#name MskConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_properties(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#server_properties MskConfiguration#server_properties}.'''
        result = self._values.get("server_properties")
        assert result is not None, "Required property 'server_properties' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#description MskConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#id MskConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafka_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_configuration#kafka_versions MskConfiguration#kafka_versions}.'''
        result = self._values.get("kafka_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskScramSecretAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskScramSecretAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association aws_msk_scram_secret_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        cluster_arn: builtins.str,
        secret_arn_list: typing.Sequence[builtins.str],
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association aws_msk_scram_secret_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.
        :param secret_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#id MskScramSecretAssociation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskScramSecretAssociationConfig(
            cluster_arn=cluster_arn,
            secret_arn_list=secret_arn_list,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

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
    @jsii.member(jsii_name="clusterArnInput")
    def cluster_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArnListInput")
    def secret_arn_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secretArnListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @cluster_arn.setter
    def cluster_arn(self, value: builtins.str) -> None:
        jsii.set(self, "clusterArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArnList")
    def secret_arn_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secretArnList"))

    @secret_arn_list.setter
    def secret_arn_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "secretArnList", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskScramSecretAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_arn": "clusterArn",
        "secret_arn_list": "secretArnList",
        "id": "id",
    },
)
class MskScramSecretAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_arn: builtins.str,
        secret_arn_list: typing.Sequence[builtins.str],
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.
        :param secret_arn_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#id MskScramSecretAssociation#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_arn": cluster_arn,
            "secret_arn_list": secret_arn_list,
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
    def cluster_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#cluster_arn MskScramSecretAssociation#cluster_arn}.'''
        result = self._values.get("cluster_arn")
        assert result is not None, "Required property 'cluster_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_arn_list(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#secret_arn_list MskScramSecretAssociation#secret_arn_list}.'''
        result = self._values.get("secret_arn_list")
        assert result is not None, "Required property 'secret_arn_list' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/msk_scram_secret_association#id MskScramSecretAssociation#id}.

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
        return "MskScramSecretAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnector(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnector",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector aws_mskconnect_connector}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        capacity: "MskconnectConnectorCapacity",
        connector_configuration: typing.Mapping[builtins.str, builtins.str],
        kafka_cluster: "MskconnectConnectorKafkaCluster",
        kafka_cluster_client_authentication: "MskconnectConnectorKafkaClusterClientAuthentication",
        kafka_cluster_encryption_in_transit: "MskconnectConnectorKafkaClusterEncryptionInTransit",
        kafkaconnect_version: builtins.str,
        name: builtins.str,
        plugin: typing.Union[cdktf.IResolvable, typing.Sequence["MskconnectConnectorPlugin"]],
        service_execution_role_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        log_delivery: typing.Optional["MskconnectConnectorLogDelivery"] = None,
        timeouts: typing.Optional["MskconnectConnectorTimeouts"] = None,
        worker_configuration: typing.Optional["MskconnectConnectorWorkerConfiguration"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector aws_mskconnect_connector} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capacity: capacity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#capacity MskconnectConnector#capacity}
        :param connector_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#connector_configuration MskconnectConnector#connector_configuration}.
        :param kafka_cluster: kafka_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster MskconnectConnector#kafka_cluster}
        :param kafka_cluster_client_authentication: kafka_cluster_client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_client_authentication MskconnectConnector#kafka_cluster_client_authentication}
        :param kafka_cluster_encryption_in_transit: kafka_cluster_encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_encryption_in_transit MskconnectConnector#kafka_cluster_encryption_in_transit}
        :param kafkaconnect_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafkaconnect_version MskconnectConnector#kafkaconnect_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#name MskconnectConnector#name}.
        :param plugin: plugin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#plugin MskconnectConnector#plugin}
        :param service_execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#service_execution_role_arn MskconnectConnector#service_execution_role_arn}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#description MskconnectConnector#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#id MskconnectConnector#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_delivery: log_delivery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_delivery MskconnectConnector#log_delivery}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#timeouts MskconnectConnector#timeouts}
        :param worker_configuration: worker_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_configuration MskconnectConnector#worker_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskconnectConnectorConfig(
            capacity=capacity,
            connector_configuration=connector_configuration,
            kafka_cluster=kafka_cluster,
            kafka_cluster_client_authentication=kafka_cluster_client_authentication,
            kafka_cluster_encryption_in_transit=kafka_cluster_encryption_in_transit,
            kafkaconnect_version=kafkaconnect_version,
            name=name,
            plugin=plugin,
            service_execution_role_arn=service_execution_role_arn,
            description=description,
            id=id,
            log_delivery=log_delivery,
            timeouts=timeouts,
            worker_configuration=worker_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putCapacity")
    def put_capacity(
        self,
        *,
        autoscaling: typing.Optional["MskconnectConnectorCapacityAutoscaling"] = None,
        provisioned_capacity: typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"] = None,
    ) -> None:
        '''
        :param autoscaling: autoscaling block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#autoscaling MskconnectConnector#autoscaling}
        :param provisioned_capacity: provisioned_capacity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#provisioned_capacity MskconnectConnector#provisioned_capacity}
        '''
        value = MskconnectConnectorCapacity(
            autoscaling=autoscaling, provisioned_capacity=provisioned_capacity
        )

        return typing.cast(None, jsii.invoke(self, "putCapacity", [value]))

    @jsii.member(jsii_name="putKafkaCluster")
    def put_kafka_cluster(
        self,
        *,
        apache_kafka_cluster: "MskconnectConnectorKafkaClusterApacheKafkaCluster",
    ) -> None:
        '''
        :param apache_kafka_cluster: apache_kafka_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#apache_kafka_cluster MskconnectConnector#apache_kafka_cluster}
        '''
        value = MskconnectConnectorKafkaCluster(
            apache_kafka_cluster=apache_kafka_cluster
        )

        return typing.cast(None, jsii.invoke(self, "putKafkaCluster", [value]))

    @jsii.member(jsii_name="putKafkaClusterClientAuthentication")
    def put_kafka_cluster_client_authentication(
        self,
        *,
        authentication_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#authentication_type MskconnectConnector#authentication_type}.
        '''
        value = MskconnectConnectorKafkaClusterClientAuthentication(
            authentication_type=authentication_type
        )

        return typing.cast(None, jsii.invoke(self, "putKafkaClusterClientAuthentication", [value]))

    @jsii.member(jsii_name="putKafkaClusterEncryptionInTransit")
    def put_kafka_cluster_encryption_in_transit(
        self,
        *,
        encryption_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#encryption_type MskconnectConnector#encryption_type}.
        '''
        value = MskconnectConnectorKafkaClusterEncryptionInTransit(
            encryption_type=encryption_type
        )

        return typing.cast(None, jsii.invoke(self, "putKafkaClusterEncryptionInTransit", [value]))

    @jsii.member(jsii_name="putLogDelivery")
    def put_log_delivery(
        self,
        *,
        worker_log_delivery: "MskconnectConnectorLogDeliveryWorkerLogDelivery",
    ) -> None:
        '''
        :param worker_log_delivery: worker_log_delivery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_log_delivery MskconnectConnector#worker_log_delivery}
        '''
        value = MskconnectConnectorLogDelivery(worker_log_delivery=worker_log_delivery)

        return typing.cast(None, jsii.invoke(self, "putLogDelivery", [value]))

    @jsii.member(jsii_name="putPlugin")
    def put_plugin(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["MskconnectConnectorPlugin"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putPlugin", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#create MskconnectConnector#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delete MskconnectConnector#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#update MskconnectConnector#update}.
        '''
        value = MskconnectConnectorTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putWorkerConfiguration")
    def put_worker_configuration(
        self,
        *,
        arn: builtins.str,
        revision: jsii.Number,
    ) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.
        '''
        value = MskconnectConnectorWorkerConfiguration(arn=arn, revision=revision)

        return typing.cast(None, jsii.invoke(self, "putWorkerConfiguration", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLogDelivery")
    def reset_log_delivery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogDelivery", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWorkerConfiguration")
    def reset_worker_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkerConfiguration", []))

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
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> "MskconnectConnectorCapacityOutputReference":
        return typing.cast("MskconnectConnectorCapacityOutputReference", jsii.get(self, "capacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaCluster")
    def kafka_cluster(self) -> "MskconnectConnectorKafkaClusterOutputReference":
        return typing.cast("MskconnectConnectorKafkaClusterOutputReference", jsii.get(self, "kafkaCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaClusterClientAuthentication")
    def kafka_cluster_client_authentication(
        self,
    ) -> "MskconnectConnectorKafkaClusterClientAuthenticationOutputReference":
        return typing.cast("MskconnectConnectorKafkaClusterClientAuthenticationOutputReference", jsii.get(self, "kafkaClusterClientAuthentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaClusterEncryptionInTransit")
    def kafka_cluster_encryption_in_transit(
        self,
    ) -> "MskconnectConnectorKafkaClusterEncryptionInTransitOutputReference":
        return typing.cast("MskconnectConnectorKafkaClusterEncryptionInTransitOutputReference", jsii.get(self, "kafkaClusterEncryptionInTransit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDelivery")
    def log_delivery(self) -> "MskconnectConnectorLogDeliveryOutputReference":
        return typing.cast("MskconnectConnectorLogDeliveryOutputReference", jsii.get(self, "logDelivery"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plugin")
    def plugin(self) -> "MskconnectConnectorPluginList":
        return typing.cast("MskconnectConnectorPluginList", jsii.get(self, "plugin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MskconnectConnectorTimeoutsOutputReference":
        return typing.cast("MskconnectConnectorTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerConfiguration")
    def worker_configuration(
        self,
    ) -> "MskconnectConnectorWorkerConfigurationOutputReference":
        return typing.cast("MskconnectConnectorWorkerConfigurationOutputReference", jsii.get(self, "workerConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional["MskconnectConnectorCapacity"]:
        return typing.cast(typing.Optional["MskconnectConnectorCapacity"], jsii.get(self, "capacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectorConfigurationInput")
    def connector_configuration_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "connectorConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaClusterClientAuthenticationInput")
    def kafka_cluster_client_authentication_input(
        self,
    ) -> typing.Optional["MskconnectConnectorKafkaClusterClientAuthentication"]:
        return typing.cast(typing.Optional["MskconnectConnectorKafkaClusterClientAuthentication"], jsii.get(self, "kafkaClusterClientAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaClusterEncryptionInTransitInput")
    def kafka_cluster_encryption_in_transit_input(
        self,
    ) -> typing.Optional["MskconnectConnectorKafkaClusterEncryptionInTransit"]:
        return typing.cast(typing.Optional["MskconnectConnectorKafkaClusterEncryptionInTransit"], jsii.get(self, "kafkaClusterEncryptionInTransitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaClusterInput")
    def kafka_cluster_input(self) -> typing.Optional["MskconnectConnectorKafkaCluster"]:
        return typing.cast(typing.Optional["MskconnectConnectorKafkaCluster"], jsii.get(self, "kafkaClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaconnectVersionInput")
    def kafkaconnect_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kafkaconnectVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDeliveryInput")
    def log_delivery_input(self) -> typing.Optional["MskconnectConnectorLogDelivery"]:
        return typing.cast(typing.Optional["MskconnectConnectorLogDelivery"], jsii.get(self, "logDeliveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginInput")
    def plugin_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["MskconnectConnectorPlugin"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["MskconnectConnectorPlugin"]]], jsii.get(self, "pluginInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceExecutionRoleArnInput")
    def service_execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceExecutionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["MskconnectConnectorTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["MskconnectConnectorTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerConfigurationInput")
    def worker_configuration_input(
        self,
    ) -> typing.Optional["MskconnectConnectorWorkerConfiguration"]:
        return typing.cast(typing.Optional["MskconnectConnectorWorkerConfiguration"], jsii.get(self, "workerConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectorConfiguration")
    def connector_configuration(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "connectorConfiguration"))

    @connector_configuration.setter
    def connector_configuration(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        jsii.set(self, "connectorConfiguration", value)

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
    @jsii.member(jsii_name="kafkaconnectVersion")
    def kafkaconnect_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kafkaconnectVersion"))

    @kafkaconnect_version.setter
    def kafkaconnect_version(self, value: builtins.str) -> None:
        jsii.set(self, "kafkaconnectVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceExecutionRoleArn")
    def service_execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceExecutionRoleArn"))

    @service_execution_role_arn.setter
    def service_execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceExecutionRoleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacity",
    jsii_struct_bases=[],
    name_mapping={
        "autoscaling": "autoscaling",
        "provisioned_capacity": "provisionedCapacity",
    },
)
class MskconnectConnectorCapacity:
    def __init__(
        self,
        *,
        autoscaling: typing.Optional["MskconnectConnectorCapacityAutoscaling"] = None,
        provisioned_capacity: typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"] = None,
    ) -> None:
        '''
        :param autoscaling: autoscaling block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#autoscaling MskconnectConnector#autoscaling}
        :param provisioned_capacity: provisioned_capacity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#provisioned_capacity MskconnectConnector#provisioned_capacity}
        '''
        if isinstance(autoscaling, dict):
            autoscaling = MskconnectConnectorCapacityAutoscaling(**autoscaling)
        if isinstance(provisioned_capacity, dict):
            provisioned_capacity = MskconnectConnectorCapacityProvisionedCapacity(**provisioned_capacity)
        self._values: typing.Dict[str, typing.Any] = {}
        if autoscaling is not None:
            self._values["autoscaling"] = autoscaling
        if provisioned_capacity is not None:
            self._values["provisioned_capacity"] = provisioned_capacity

    @builtins.property
    def autoscaling(self) -> typing.Optional["MskconnectConnectorCapacityAutoscaling"]:
        '''autoscaling block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#autoscaling MskconnectConnector#autoscaling}
        '''
        result = self._values.get("autoscaling")
        return typing.cast(typing.Optional["MskconnectConnectorCapacityAutoscaling"], result)

    @builtins.property
    def provisioned_capacity(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"]:
        '''provisioned_capacity block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#provisioned_capacity MskconnectConnector#provisioned_capacity}
        '''
        result = self._values.get("provisioned_capacity")
        return typing.cast(typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorCapacity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscaling",
    jsii_struct_bases=[],
    name_mapping={
        "max_worker_count": "maxWorkerCount",
        "min_worker_count": "minWorkerCount",
        "mcu_count": "mcuCount",
        "scale_in_policy": "scaleInPolicy",
        "scale_out_policy": "scaleOutPolicy",
    },
)
class MskconnectConnectorCapacityAutoscaling:
    def __init__(
        self,
        *,
        max_worker_count: jsii.Number,
        min_worker_count: jsii.Number,
        mcu_count: typing.Optional[jsii.Number] = None,
        scale_in_policy: typing.Optional["MskconnectConnectorCapacityAutoscalingScaleInPolicy"] = None,
        scale_out_policy: typing.Optional["MskconnectConnectorCapacityAutoscalingScaleOutPolicy"] = None,
    ) -> None:
        '''
        :param max_worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#max_worker_count MskconnectConnector#max_worker_count}.
        :param min_worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#min_worker_count MskconnectConnector#min_worker_count}.
        :param mcu_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.
        :param scale_in_policy: scale_in_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_in_policy MskconnectConnector#scale_in_policy}
        :param scale_out_policy: scale_out_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_out_policy MskconnectConnector#scale_out_policy}
        '''
        if isinstance(scale_in_policy, dict):
            scale_in_policy = MskconnectConnectorCapacityAutoscalingScaleInPolicy(**scale_in_policy)
        if isinstance(scale_out_policy, dict):
            scale_out_policy = MskconnectConnectorCapacityAutoscalingScaleOutPolicy(**scale_out_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "max_worker_count": max_worker_count,
            "min_worker_count": min_worker_count,
        }
        if mcu_count is not None:
            self._values["mcu_count"] = mcu_count
        if scale_in_policy is not None:
            self._values["scale_in_policy"] = scale_in_policy
        if scale_out_policy is not None:
            self._values["scale_out_policy"] = scale_out_policy

    @builtins.property
    def max_worker_count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#max_worker_count MskconnectConnector#max_worker_count}.'''
        result = self._values.get("max_worker_count")
        assert result is not None, "Required property 'max_worker_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_worker_count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#min_worker_count MskconnectConnector#min_worker_count}.'''
        result = self._values.get("min_worker_count")
        assert result is not None, "Required property 'min_worker_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mcu_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.'''
        result = self._values.get("mcu_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scale_in_policy(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityAutoscalingScaleInPolicy"]:
        '''scale_in_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_in_policy MskconnectConnector#scale_in_policy}
        '''
        result = self._values.get("scale_in_policy")
        return typing.cast(typing.Optional["MskconnectConnectorCapacityAutoscalingScaleInPolicy"], result)

    @builtins.property
    def scale_out_policy(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityAutoscalingScaleOutPolicy"]:
        '''scale_out_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_out_policy MskconnectConnector#scale_out_policy}
        '''
        result = self._values.get("scale_out_policy")
        return typing.cast(typing.Optional["MskconnectConnectorCapacityAutoscalingScaleOutPolicy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorCapacityAutoscaling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorCapacityAutoscalingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscalingOutputReference",
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

    @jsii.member(jsii_name="putScaleInPolicy")
    def put_scale_in_policy(
        self,
        *,
        cpu_utilization_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_utilization_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.
        '''
        value = MskconnectConnectorCapacityAutoscalingScaleInPolicy(
            cpu_utilization_percentage=cpu_utilization_percentage
        )

        return typing.cast(None, jsii.invoke(self, "putScaleInPolicy", [value]))

    @jsii.member(jsii_name="putScaleOutPolicy")
    def put_scale_out_policy(
        self,
        *,
        cpu_utilization_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_utilization_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.
        '''
        value = MskconnectConnectorCapacityAutoscalingScaleOutPolicy(
            cpu_utilization_percentage=cpu_utilization_percentage
        )

        return typing.cast(None, jsii.invoke(self, "putScaleOutPolicy", [value]))

    @jsii.member(jsii_name="resetMcuCount")
    def reset_mcu_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMcuCount", []))

    @jsii.member(jsii_name="resetScaleInPolicy")
    def reset_scale_in_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleInPolicy", []))

    @jsii.member(jsii_name="resetScaleOutPolicy")
    def reset_scale_out_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleOutPolicy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleInPolicy")
    def scale_in_policy(
        self,
    ) -> "MskconnectConnectorCapacityAutoscalingScaleInPolicyOutputReference":
        return typing.cast("MskconnectConnectorCapacityAutoscalingScaleInPolicyOutputReference", jsii.get(self, "scaleInPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleOutPolicy")
    def scale_out_policy(
        self,
    ) -> "MskconnectConnectorCapacityAutoscalingScaleOutPolicyOutputReference":
        return typing.cast("MskconnectConnectorCapacityAutoscalingScaleOutPolicyOutputReference", jsii.get(self, "scaleOutPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWorkerCountInput")
    def max_worker_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkerCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mcuCountInput")
    def mcu_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mcuCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minWorkerCountInput")
    def min_worker_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minWorkerCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleInPolicyInput")
    def scale_in_policy_input(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityAutoscalingScaleInPolicy"]:
        return typing.cast(typing.Optional["MskconnectConnectorCapacityAutoscalingScaleInPolicy"], jsii.get(self, "scaleInPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleOutPolicyInput")
    def scale_out_policy_input(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityAutoscalingScaleOutPolicy"]:
        return typing.cast(typing.Optional["MskconnectConnectorCapacityAutoscalingScaleOutPolicy"], jsii.get(self, "scaleOutPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxWorkerCount")
    def max_worker_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkerCount"))

    @max_worker_count.setter
    def max_worker_count(self, value: jsii.Number) -> None:
        jsii.set(self, "maxWorkerCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mcuCount")
    def mcu_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mcuCount"))

    @mcu_count.setter
    def mcu_count(self, value: jsii.Number) -> None:
        jsii.set(self, "mcuCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minWorkerCount")
    def min_worker_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minWorkerCount"))

    @min_worker_count.setter
    def min_worker_count(self, value: jsii.Number) -> None:
        jsii.set(self, "minWorkerCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorCapacityAutoscaling]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacityAutoscaling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorCapacityAutoscaling],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscalingScaleInPolicy",
    jsii_struct_bases=[],
    name_mapping={"cpu_utilization_percentage": "cpuUtilizationPercentage"},
)
class MskconnectConnectorCapacityAutoscalingScaleInPolicy:
    def __init__(
        self,
        *,
        cpu_utilization_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_utilization_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cpu_utilization_percentage is not None:
            self._values["cpu_utilization_percentage"] = cpu_utilization_percentage

    @builtins.property
    def cpu_utilization_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.'''
        result = self._values.get("cpu_utilization_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorCapacityAutoscalingScaleInPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorCapacityAutoscalingScaleInPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscalingScaleInPolicyOutputReference",
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

    @jsii.member(jsii_name="resetCpuUtilizationPercentage")
    def reset_cpu_utilization_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuUtilizationPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuUtilizationPercentageInput")
    def cpu_utilization_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuUtilizationPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuUtilizationPercentage")
    def cpu_utilization_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuUtilizationPercentage"))

    @cpu_utilization_percentage.setter
    def cpu_utilization_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuUtilizationPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorCapacityAutoscalingScaleInPolicy]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacityAutoscalingScaleInPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorCapacityAutoscalingScaleInPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscalingScaleOutPolicy",
    jsii_struct_bases=[],
    name_mapping={"cpu_utilization_percentage": "cpuUtilizationPercentage"},
)
class MskconnectConnectorCapacityAutoscalingScaleOutPolicy:
    def __init__(
        self,
        *,
        cpu_utilization_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_utilization_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cpu_utilization_percentage is not None:
            self._values["cpu_utilization_percentage"] = cpu_utilization_percentage

    @builtins.property
    def cpu_utilization_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cpu_utilization_percentage MskconnectConnector#cpu_utilization_percentage}.'''
        result = self._values.get("cpu_utilization_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorCapacityAutoscalingScaleOutPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorCapacityAutoscalingScaleOutPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityAutoscalingScaleOutPolicyOutputReference",
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

    @jsii.member(jsii_name="resetCpuUtilizationPercentage")
    def reset_cpu_utilization_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuUtilizationPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuUtilizationPercentageInput")
    def cpu_utilization_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuUtilizationPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuUtilizationPercentage")
    def cpu_utilization_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuUtilizationPercentage"))

    @cpu_utilization_percentage.setter
    def cpu_utilization_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuUtilizationPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorCapacityAutoscalingScaleOutPolicy]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacityAutoscalingScaleOutPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorCapacityAutoscalingScaleOutPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectConnectorCapacityOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityOutputReference",
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

    @jsii.member(jsii_name="putAutoscaling")
    def put_autoscaling(
        self,
        *,
        max_worker_count: jsii.Number,
        min_worker_count: jsii.Number,
        mcu_count: typing.Optional[jsii.Number] = None,
        scale_in_policy: typing.Optional[MskconnectConnectorCapacityAutoscalingScaleInPolicy] = None,
        scale_out_policy: typing.Optional[MskconnectConnectorCapacityAutoscalingScaleOutPolicy] = None,
    ) -> None:
        '''
        :param max_worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#max_worker_count MskconnectConnector#max_worker_count}.
        :param min_worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#min_worker_count MskconnectConnector#min_worker_count}.
        :param mcu_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.
        :param scale_in_policy: scale_in_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_in_policy MskconnectConnector#scale_in_policy}
        :param scale_out_policy: scale_out_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#scale_out_policy MskconnectConnector#scale_out_policy}
        '''
        value = MskconnectConnectorCapacityAutoscaling(
            max_worker_count=max_worker_count,
            min_worker_count=min_worker_count,
            mcu_count=mcu_count,
            scale_in_policy=scale_in_policy,
            scale_out_policy=scale_out_policy,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaling", [value]))

    @jsii.member(jsii_name="putProvisionedCapacity")
    def put_provisioned_capacity(
        self,
        *,
        worker_count: jsii.Number,
        mcu_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_count MskconnectConnector#worker_count}.
        :param mcu_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.
        '''
        value = MskconnectConnectorCapacityProvisionedCapacity(
            worker_count=worker_count, mcu_count=mcu_count
        )

        return typing.cast(None, jsii.invoke(self, "putProvisionedCapacity", [value]))

    @jsii.member(jsii_name="resetAutoscaling")
    def reset_autoscaling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaling", []))

    @jsii.member(jsii_name="resetProvisionedCapacity")
    def reset_provisioned_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisionedCapacity", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscaling")
    def autoscaling(self) -> MskconnectConnectorCapacityAutoscalingOutputReference:
        return typing.cast(MskconnectConnectorCapacityAutoscalingOutputReference, jsii.get(self, "autoscaling"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedCapacity")
    def provisioned_capacity(
        self,
    ) -> "MskconnectConnectorCapacityProvisionedCapacityOutputReference":
        return typing.cast("MskconnectConnectorCapacityProvisionedCapacityOutputReference", jsii.get(self, "provisionedCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingInput")
    def autoscaling_input(
        self,
    ) -> typing.Optional[MskconnectConnectorCapacityAutoscaling]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacityAutoscaling], jsii.get(self, "autoscalingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedCapacityInput")
    def provisioned_capacity_input(
        self,
    ) -> typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"]:
        return typing.cast(typing.Optional["MskconnectConnectorCapacityProvisionedCapacity"], jsii.get(self, "provisionedCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorCapacity]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorCapacity],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityProvisionedCapacity",
    jsii_struct_bases=[],
    name_mapping={"worker_count": "workerCount", "mcu_count": "mcuCount"},
)
class MskconnectConnectorCapacityProvisionedCapacity:
    def __init__(
        self,
        *,
        worker_count: jsii.Number,
        mcu_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param worker_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_count MskconnectConnector#worker_count}.
        :param mcu_count: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "worker_count": worker_count,
        }
        if mcu_count is not None:
            self._values["mcu_count"] = mcu_count

    @builtins.property
    def worker_count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_count MskconnectConnector#worker_count}.'''
        result = self._values.get("worker_count")
        assert result is not None, "Required property 'worker_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def mcu_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#mcu_count MskconnectConnector#mcu_count}.'''
        result = self._values.get("mcu_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorCapacityProvisionedCapacity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorCapacityProvisionedCapacityOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorCapacityProvisionedCapacityOutputReference",
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

    @jsii.member(jsii_name="resetMcuCount")
    def reset_mcu_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMcuCount", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mcuCountInput")
    def mcu_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mcuCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerCountInput")
    def worker_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workerCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mcuCount")
    def mcu_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mcuCount"))

    @mcu_count.setter
    def mcu_count(self, value: jsii.Number) -> None:
        jsii.set(self, "mcuCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerCount")
    def worker_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workerCount"))

    @worker_count.setter
    def worker_count(self, value: jsii.Number) -> None:
        jsii.set(self, "workerCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorCapacityProvisionedCapacity]:
        return typing.cast(typing.Optional[MskconnectConnectorCapacityProvisionedCapacity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorCapacityProvisionedCapacity],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "capacity": "capacity",
        "connector_configuration": "connectorConfiguration",
        "kafka_cluster": "kafkaCluster",
        "kafka_cluster_client_authentication": "kafkaClusterClientAuthentication",
        "kafka_cluster_encryption_in_transit": "kafkaClusterEncryptionInTransit",
        "kafkaconnect_version": "kafkaconnectVersion",
        "name": "name",
        "plugin": "plugin",
        "service_execution_role_arn": "serviceExecutionRoleArn",
        "description": "description",
        "id": "id",
        "log_delivery": "logDelivery",
        "timeouts": "timeouts",
        "worker_configuration": "workerConfiguration",
    },
)
class MskconnectConnectorConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        capacity: MskconnectConnectorCapacity,
        connector_configuration: typing.Mapping[builtins.str, builtins.str],
        kafka_cluster: "MskconnectConnectorKafkaCluster",
        kafka_cluster_client_authentication: "MskconnectConnectorKafkaClusterClientAuthentication",
        kafka_cluster_encryption_in_transit: "MskconnectConnectorKafkaClusterEncryptionInTransit",
        kafkaconnect_version: builtins.str,
        name: builtins.str,
        plugin: typing.Union[cdktf.IResolvable, typing.Sequence["MskconnectConnectorPlugin"]],
        service_execution_role_arn: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        log_delivery: typing.Optional["MskconnectConnectorLogDelivery"] = None,
        timeouts: typing.Optional["MskconnectConnectorTimeouts"] = None,
        worker_configuration: typing.Optional["MskconnectConnectorWorkerConfiguration"] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param capacity: capacity block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#capacity MskconnectConnector#capacity}
        :param connector_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#connector_configuration MskconnectConnector#connector_configuration}.
        :param kafka_cluster: kafka_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster MskconnectConnector#kafka_cluster}
        :param kafka_cluster_client_authentication: kafka_cluster_client_authentication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_client_authentication MskconnectConnector#kafka_cluster_client_authentication}
        :param kafka_cluster_encryption_in_transit: kafka_cluster_encryption_in_transit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_encryption_in_transit MskconnectConnector#kafka_cluster_encryption_in_transit}
        :param kafkaconnect_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafkaconnect_version MskconnectConnector#kafkaconnect_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#name MskconnectConnector#name}.
        :param plugin: plugin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#plugin MskconnectConnector#plugin}
        :param service_execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#service_execution_role_arn MskconnectConnector#service_execution_role_arn}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#description MskconnectConnector#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#id MskconnectConnector#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_delivery: log_delivery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_delivery MskconnectConnector#log_delivery}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#timeouts MskconnectConnector#timeouts}
        :param worker_configuration: worker_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_configuration MskconnectConnector#worker_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(capacity, dict):
            capacity = MskconnectConnectorCapacity(**capacity)
        if isinstance(kafka_cluster, dict):
            kafka_cluster = MskconnectConnectorKafkaCluster(**kafka_cluster)
        if isinstance(kafka_cluster_client_authentication, dict):
            kafka_cluster_client_authentication = MskconnectConnectorKafkaClusterClientAuthentication(**kafka_cluster_client_authentication)
        if isinstance(kafka_cluster_encryption_in_transit, dict):
            kafka_cluster_encryption_in_transit = MskconnectConnectorKafkaClusterEncryptionInTransit(**kafka_cluster_encryption_in_transit)
        if isinstance(log_delivery, dict):
            log_delivery = MskconnectConnectorLogDelivery(**log_delivery)
        if isinstance(timeouts, dict):
            timeouts = MskconnectConnectorTimeouts(**timeouts)
        if isinstance(worker_configuration, dict):
            worker_configuration = MskconnectConnectorWorkerConfiguration(**worker_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "capacity": capacity,
            "connector_configuration": connector_configuration,
            "kafka_cluster": kafka_cluster,
            "kafka_cluster_client_authentication": kafka_cluster_client_authentication,
            "kafka_cluster_encryption_in_transit": kafka_cluster_encryption_in_transit,
            "kafkaconnect_version": kafkaconnect_version,
            "name": name,
            "plugin": plugin,
            "service_execution_role_arn": service_execution_role_arn,
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
        if log_delivery is not None:
            self._values["log_delivery"] = log_delivery
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if worker_configuration is not None:
            self._values["worker_configuration"] = worker_configuration

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
    def capacity(self) -> MskconnectConnectorCapacity:
        '''capacity block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#capacity MskconnectConnector#capacity}
        '''
        result = self._values.get("capacity")
        assert result is not None, "Required property 'capacity' is missing"
        return typing.cast(MskconnectConnectorCapacity, result)

    @builtins.property
    def connector_configuration(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#connector_configuration MskconnectConnector#connector_configuration}.'''
        result = self._values.get("connector_configuration")
        assert result is not None, "Required property 'connector_configuration' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def kafka_cluster(self) -> "MskconnectConnectorKafkaCluster":
        '''kafka_cluster block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster MskconnectConnector#kafka_cluster}
        '''
        result = self._values.get("kafka_cluster")
        assert result is not None, "Required property 'kafka_cluster' is missing"
        return typing.cast("MskconnectConnectorKafkaCluster", result)

    @builtins.property
    def kafka_cluster_client_authentication(
        self,
    ) -> "MskconnectConnectorKafkaClusterClientAuthentication":
        '''kafka_cluster_client_authentication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_client_authentication MskconnectConnector#kafka_cluster_client_authentication}
        '''
        result = self._values.get("kafka_cluster_client_authentication")
        assert result is not None, "Required property 'kafka_cluster_client_authentication' is missing"
        return typing.cast("MskconnectConnectorKafkaClusterClientAuthentication", result)

    @builtins.property
    def kafka_cluster_encryption_in_transit(
        self,
    ) -> "MskconnectConnectorKafkaClusterEncryptionInTransit":
        '''kafka_cluster_encryption_in_transit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafka_cluster_encryption_in_transit MskconnectConnector#kafka_cluster_encryption_in_transit}
        '''
        result = self._values.get("kafka_cluster_encryption_in_transit")
        assert result is not None, "Required property 'kafka_cluster_encryption_in_transit' is missing"
        return typing.cast("MskconnectConnectorKafkaClusterEncryptionInTransit", result)

    @builtins.property
    def kafkaconnect_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#kafkaconnect_version MskconnectConnector#kafkaconnect_version}.'''
        result = self._values.get("kafkaconnect_version")
        assert result is not None, "Required property 'kafkaconnect_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#name MskconnectConnector#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["MskconnectConnectorPlugin"]]:
        '''plugin block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#plugin MskconnectConnector#plugin}
        '''
        result = self._values.get("plugin")
        assert result is not None, "Required property 'plugin' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["MskconnectConnectorPlugin"]], result)

    @builtins.property
    def service_execution_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#service_execution_role_arn MskconnectConnector#service_execution_role_arn}.'''
        result = self._values.get("service_execution_role_arn")
        assert result is not None, "Required property 'service_execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#description MskconnectConnector#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#id MskconnectConnector#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_delivery(self) -> typing.Optional["MskconnectConnectorLogDelivery"]:
        '''log_delivery block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_delivery MskconnectConnector#log_delivery}
        '''
        result = self._values.get("log_delivery")
        return typing.cast(typing.Optional["MskconnectConnectorLogDelivery"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MskconnectConnectorTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#timeouts MskconnectConnector#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MskconnectConnectorTimeouts"], result)

    @builtins.property
    def worker_configuration(
        self,
    ) -> typing.Optional["MskconnectConnectorWorkerConfiguration"]:
        '''worker_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_configuration MskconnectConnector#worker_configuration}
        '''
        result = self._values.get("worker_configuration")
        return typing.cast(typing.Optional["MskconnectConnectorWorkerConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaCluster",
    jsii_struct_bases=[],
    name_mapping={"apache_kafka_cluster": "apacheKafkaCluster"},
)
class MskconnectConnectorKafkaCluster:
    def __init__(
        self,
        *,
        apache_kafka_cluster: "MskconnectConnectorKafkaClusterApacheKafkaCluster",
    ) -> None:
        '''
        :param apache_kafka_cluster: apache_kafka_cluster block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#apache_kafka_cluster MskconnectConnector#apache_kafka_cluster}
        '''
        if isinstance(apache_kafka_cluster, dict):
            apache_kafka_cluster = MskconnectConnectorKafkaClusterApacheKafkaCluster(**apache_kafka_cluster)
        self._values: typing.Dict[str, typing.Any] = {
            "apache_kafka_cluster": apache_kafka_cluster,
        }

    @builtins.property
    def apache_kafka_cluster(
        self,
    ) -> "MskconnectConnectorKafkaClusterApacheKafkaCluster":
        '''apache_kafka_cluster block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#apache_kafka_cluster MskconnectConnector#apache_kafka_cluster}
        '''
        result = self._values.get("apache_kafka_cluster")
        assert result is not None, "Required property 'apache_kafka_cluster' is missing"
        return typing.cast("MskconnectConnectorKafkaClusterApacheKafkaCluster", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorKafkaCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterApacheKafkaCluster",
    jsii_struct_bases=[],
    name_mapping={"bootstrap_servers": "bootstrapServers", "vpc": "vpc"},
)
class MskconnectConnectorKafkaClusterApacheKafkaCluster:
    def __init__(
        self,
        *,
        bootstrap_servers: builtins.str,
        vpc: "MskconnectConnectorKafkaClusterApacheKafkaClusterVpc",
    ) -> None:
        '''
        :param bootstrap_servers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bootstrap_servers MskconnectConnector#bootstrap_servers}.
        :param vpc: vpc block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#vpc MskconnectConnector#vpc}
        '''
        if isinstance(vpc, dict):
            vpc = MskconnectConnectorKafkaClusterApacheKafkaClusterVpc(**vpc)
        self._values: typing.Dict[str, typing.Any] = {
            "bootstrap_servers": bootstrap_servers,
            "vpc": vpc,
        }

    @builtins.property
    def bootstrap_servers(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bootstrap_servers MskconnectConnector#bootstrap_servers}.'''
        result = self._values.get("bootstrap_servers")
        assert result is not None, "Required property 'bootstrap_servers' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> "MskconnectConnectorKafkaClusterApacheKafkaClusterVpc":
        '''vpc block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#vpc MskconnectConnector#vpc}
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast("MskconnectConnectorKafkaClusterApacheKafkaClusterVpc", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorKafkaClusterApacheKafkaCluster(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorKafkaClusterApacheKafkaClusterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterApacheKafkaClusterOutputReference",
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

    @jsii.member(jsii_name="putVpc")
    def put_vpc(
        self,
        *,
        security_groups: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#security_groups MskconnectConnector#security_groups}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#subnets MskconnectConnector#subnets}.
        '''
        value = MskconnectConnectorKafkaClusterApacheKafkaClusterVpc(
            security_groups=security_groups, subnets=subnets
        )

        return typing.cast(None, jsii.invoke(self, "putVpc", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(
        self,
    ) -> "MskconnectConnectorKafkaClusterApacheKafkaClusterVpcOutputReference":
        return typing.cast("MskconnectConnectorKafkaClusterApacheKafkaClusterVpcOutputReference", jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapServersInput")
    def bootstrap_servers_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bootstrapServersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcInput")
    def vpc_input(
        self,
    ) -> typing.Optional["MskconnectConnectorKafkaClusterApacheKafkaClusterVpc"]:
        return typing.cast(typing.Optional["MskconnectConnectorKafkaClusterApacheKafkaClusterVpc"], jsii.get(self, "vpcInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapServers")
    def bootstrap_servers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapServers"))

    @bootstrap_servers.setter
    def bootstrap_servers(self, value: builtins.str) -> None:
        jsii.set(self, "bootstrapServers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaCluster]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaCluster],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterApacheKafkaClusterVpc",
    jsii_struct_bases=[],
    name_mapping={"security_groups": "securityGroups", "subnets": "subnets"},
)
class MskconnectConnectorKafkaClusterApacheKafkaClusterVpc:
    def __init__(
        self,
        *,
        security_groups: typing.Sequence[builtins.str],
        subnets: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#security_groups MskconnectConnector#security_groups}.
        :param subnets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#subnets MskconnectConnector#subnets}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "security_groups": security_groups,
            "subnets": subnets,
        }

    @builtins.property
    def security_groups(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#security_groups MskconnectConnector#security_groups}.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def subnets(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#subnets MskconnectConnector#subnets}.'''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorKafkaClusterApacheKafkaClusterVpc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorKafkaClusterApacheKafkaClusterVpcOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterApacheKafkaClusterVpcOutputReference",
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
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetsInput")
    def subnets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnets")
    def subnets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnets"))

    @subnets.setter
    def subnets(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaClusterVpc]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaClusterVpc], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaClusterVpc],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterClientAuthentication",
    jsii_struct_bases=[],
    name_mapping={"authentication_type": "authenticationType"},
)
class MskconnectConnectorKafkaClusterClientAuthentication:
    def __init__(
        self,
        *,
        authentication_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#authentication_type MskconnectConnector#authentication_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authentication_type is not None:
            self._values["authentication_type"] = authentication_type

    @builtins.property
    def authentication_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#authentication_type MskconnectConnector#authentication_type}.'''
        result = self._values.get("authentication_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorKafkaClusterClientAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorKafkaClusterClientAuthenticationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterClientAuthenticationOutputReference",
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

    @jsii.member(jsii_name="resetAuthenticationType")
    def reset_authentication_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationTypeInput")
    def authentication_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationType"))

    @authentication_type.setter
    def authentication_type(self, value: builtins.str) -> None:
        jsii.set(self, "authenticationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorKafkaClusterClientAuthentication]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaClusterClientAuthentication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorKafkaClusterClientAuthentication],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterEncryptionInTransit",
    jsii_struct_bases=[],
    name_mapping={"encryption_type": "encryptionType"},
)
class MskconnectConnectorKafkaClusterEncryptionInTransit:
    def __init__(
        self,
        *,
        encryption_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#encryption_type MskconnectConnector#encryption_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_type is not None:
            self._values["encryption_type"] = encryption_type

    @builtins.property
    def encryption_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#encryption_type MskconnectConnector#encryption_type}.'''
        result = self._values.get("encryption_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorKafkaClusterEncryptionInTransit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorKafkaClusterEncryptionInTransitOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterEncryptionInTransitOutputReference",
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

    @jsii.member(jsii_name="resetEncryptionType")
    def reset_encryption_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionTypeInput")
    def encryption_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionType")
    def encryption_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionType"))

    @encryption_type.setter
    def encryption_type(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorKafkaClusterEncryptionInTransit]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaClusterEncryptionInTransit], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorKafkaClusterEncryptionInTransit],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectConnectorKafkaClusterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorKafkaClusterOutputReference",
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

    @jsii.member(jsii_name="putApacheKafkaCluster")
    def put_apache_kafka_cluster(
        self,
        *,
        bootstrap_servers: builtins.str,
        vpc: MskconnectConnectorKafkaClusterApacheKafkaClusterVpc,
    ) -> None:
        '''
        :param bootstrap_servers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bootstrap_servers MskconnectConnector#bootstrap_servers}.
        :param vpc: vpc block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#vpc MskconnectConnector#vpc}
        '''
        value = MskconnectConnectorKafkaClusterApacheKafkaCluster(
            bootstrap_servers=bootstrap_servers, vpc=vpc
        )

        return typing.cast(None, jsii.invoke(self, "putApacheKafkaCluster", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apacheKafkaCluster")
    def apache_kafka_cluster(
        self,
    ) -> MskconnectConnectorKafkaClusterApacheKafkaClusterOutputReference:
        return typing.cast(MskconnectConnectorKafkaClusterApacheKafkaClusterOutputReference, jsii.get(self, "apacheKafkaCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apacheKafkaClusterInput")
    def apache_kafka_cluster_input(
        self,
    ) -> typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaCluster]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaClusterApacheKafkaCluster], jsii.get(self, "apacheKafkaClusterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorKafkaCluster]:
        return typing.cast(typing.Optional[MskconnectConnectorKafkaCluster], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorKafkaCluster],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDelivery",
    jsii_struct_bases=[],
    name_mapping={"worker_log_delivery": "workerLogDelivery"},
)
class MskconnectConnectorLogDelivery:
    def __init__(
        self,
        *,
        worker_log_delivery: "MskconnectConnectorLogDeliveryWorkerLogDelivery",
    ) -> None:
        '''
        :param worker_log_delivery: worker_log_delivery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_log_delivery MskconnectConnector#worker_log_delivery}
        '''
        if isinstance(worker_log_delivery, dict):
            worker_log_delivery = MskconnectConnectorLogDeliveryWorkerLogDelivery(**worker_log_delivery)
        self._values: typing.Dict[str, typing.Any] = {
            "worker_log_delivery": worker_log_delivery,
        }

    @builtins.property
    def worker_log_delivery(self) -> "MskconnectConnectorLogDeliveryWorkerLogDelivery":
        '''worker_log_delivery block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#worker_log_delivery MskconnectConnector#worker_log_delivery}
        '''
        result = self._values.get("worker_log_delivery")
        assert result is not None, "Required property 'worker_log_delivery' is missing"
        return typing.cast("MskconnectConnectorLogDeliveryWorkerLogDelivery", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorLogDelivery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorLogDeliveryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryOutputReference",
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

    @jsii.member(jsii_name="putWorkerLogDelivery")
    def put_worker_log_delivery(
        self,
        *,
        cloudwatch_logs: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs"] = None,
        firehose: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose"] = None,
        s3: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cloudwatch_logs MskconnectConnector#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#firehose MskconnectConnector#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#s3 MskconnectConnector#s3}
        '''
        value = MskconnectConnectorLogDeliveryWorkerLogDelivery(
            cloudwatch_logs=cloudwatch_logs, firehose=firehose, s3=s3
        )

        return typing.cast(None, jsii.invoke(self, "putWorkerLogDelivery", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerLogDelivery")
    def worker_log_delivery(
        self,
    ) -> "MskconnectConnectorLogDeliveryWorkerLogDeliveryOutputReference":
        return typing.cast("MskconnectConnectorLogDeliveryWorkerLogDeliveryOutputReference", jsii.get(self, "workerLogDelivery"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workerLogDeliveryInput")
    def worker_log_delivery_input(
        self,
    ) -> typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDelivery"]:
        return typing.cast(typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDelivery"], jsii.get(self, "workerLogDeliveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorLogDelivery]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDelivery], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorLogDelivery],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDelivery",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_logs": "cloudwatchLogs",
        "firehose": "firehose",
        "s3": "s3",
    },
)
class MskconnectConnectorLogDeliveryWorkerLogDelivery:
    def __init__(
        self,
        *,
        cloudwatch_logs: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs"] = None,
        firehose: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose"] = None,
        s3: typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"] = None,
    ) -> None:
        '''
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cloudwatch_logs MskconnectConnector#cloudwatch_logs}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#firehose MskconnectConnector#firehose}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#s3 MskconnectConnector#s3}
        '''
        if isinstance(cloudwatch_logs, dict):
            cloudwatch_logs = MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs(**cloudwatch_logs)
        if isinstance(firehose, dict):
            firehose = MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose(**firehose)
        if isinstance(s3, dict):
            s3 = MskconnectConnectorLogDeliveryWorkerLogDeliveryS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloudwatch_logs is not None:
            self._values["cloudwatch_logs"] = cloudwatch_logs
        if firehose is not None:
            self._values["firehose"] = firehose
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloudwatch_logs(
        self,
    ) -> typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs"]:
        '''cloudwatch_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#cloudwatch_logs MskconnectConnector#cloudwatch_logs}
        '''
        result = self._values.get("cloudwatch_logs")
        return typing.cast(typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs"], result)

    @builtins.property
    def firehose(
        self,
    ) -> typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose"]:
        '''firehose block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#firehose MskconnectConnector#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose"], result)

    @builtins.property
    def s3(
        self,
    ) -> typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#s3 MskconnectConnector#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorLogDeliveryWorkerLogDelivery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "log_group": "logGroup"},
)
class MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_group MskconnectConnector#log_group}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if log_group is not None:
            self._values["log_group"] = log_group

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def log_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_group MskconnectConnector#log_group}.'''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogsOutputReference",
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

    @jsii.member(jsii_name="resetLogGroup")
    def reset_log_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogGroup", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupInput")
    def log_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: builtins.str) -> None:
        jsii.set(self, "logGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "delivery_stream": "deliveryStream"},
)
class MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delivery_stream MskconnectConnector#delivery_stream}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if delivery_stream is not None:
            self._values["delivery_stream"] = delivery_stream

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def delivery_stream(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delivery_stream MskconnectConnector#delivery_stream}.'''
        result = self._values.get("delivery_stream")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehoseOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehoseOutputReference",
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

    @jsii.member(jsii_name="resetDeliveryStream")
    def reset_delivery_stream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryStream", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamInput")
    def delivery_stream_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStream")
    def delivery_stream(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStream"))

    @delivery_stream.setter
    def delivery_stream(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStream", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectConnectorLogDeliveryWorkerLogDeliveryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryOutputReference",
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

    @jsii.member(jsii_name="putCloudwatchLogs")
    def put_cloudwatch_logs(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        log_group: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param log_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#log_group MskconnectConnector#log_group}.
        '''
        value = MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs(
            enabled=enabled, log_group=log_group
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchLogs", [value]))

    @jsii.member(jsii_name="putFirehose")
    def put_firehose(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        delivery_stream: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param delivery_stream: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delivery_stream MskconnectConnector#delivery_stream}.
        '''
        value = MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose(
            enabled=enabled, delivery_stream=delivery_stream
        )

        return typing.cast(None, jsii.invoke(self, "putFirehose", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bucket MskconnectConnector#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#prefix MskconnectConnector#prefix}.
        '''
        value = MskconnectConnectorLogDeliveryWorkerLogDeliveryS3(
            enabled=enabled, bucket=bucket, prefix=prefix
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="resetCloudwatchLogs")
    def reset_cloudwatch_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogs", []))

    @jsii.member(jsii_name="resetFirehose")
    def reset_firehose(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehose", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogs")
    def cloudwatch_logs(
        self,
    ) -> MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogsOutputReference:
        return typing.cast(MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogsOutputReference, jsii.get(self, "cloudwatchLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehose")
    def firehose(
        self,
    ) -> MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehoseOutputReference:
        return typing.cast(MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehoseOutputReference, jsii.get(self, "firehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "MskconnectConnectorLogDeliveryWorkerLogDeliveryS3OutputReference":
        return typing.cast("MskconnectConnectorLogDeliveryWorkerLogDeliveryS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsInput")
    def cloudwatch_logs_input(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs], jsii.get(self, "cloudwatchLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseInput")
    def firehose_input(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose], jsii.get(self, "firehoseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"]:
        return typing.cast(typing.Optional["MskconnectConnectorLogDeliveryWorkerLogDeliveryS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDelivery]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDelivery], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDelivery],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryS3",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "bucket": "bucket", "prefix": "prefix"},
)
class MskconnectConnectorLogDeliveryWorkerLogDeliveryS3:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        bucket: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bucket MskconnectConnector#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#prefix MskconnectConnector#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#enabled MskconnectConnector#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#bucket MskconnectConnector#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#prefix MskconnectConnector#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorLogDeliveryWorkerLogDeliveryS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorLogDeliveryWorkerLogDeliveryS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorLogDeliveryWorkerLogDeliveryS3OutputReference",
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

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryS3]:
        return typing.cast(typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorLogDeliveryWorkerLogDeliveryS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorPlugin",
    jsii_struct_bases=[],
    name_mapping={"custom_plugin": "customPlugin"},
)
class MskconnectConnectorPlugin:
    def __init__(
        self,
        *,
        custom_plugin: "MskconnectConnectorPluginCustomPlugin",
    ) -> None:
        '''
        :param custom_plugin: custom_plugin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#custom_plugin MskconnectConnector#custom_plugin}
        '''
        if isinstance(custom_plugin, dict):
            custom_plugin = MskconnectConnectorPluginCustomPlugin(**custom_plugin)
        self._values: typing.Dict[str, typing.Any] = {
            "custom_plugin": custom_plugin,
        }

    @builtins.property
    def custom_plugin(self) -> "MskconnectConnectorPluginCustomPlugin":
        '''custom_plugin block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#custom_plugin MskconnectConnector#custom_plugin}
        '''
        result = self._values.get("custom_plugin")
        assert result is not None, "Required property 'custom_plugin' is missing"
        return typing.cast("MskconnectConnectorPluginCustomPlugin", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorPlugin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorPluginCustomPlugin",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class MskconnectConnectorPluginCustomPlugin:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorPluginCustomPlugin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorPluginCustomPluginOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorPluginCustomPluginOutputReference",
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
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revisionInput")
    def revision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "revisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @revision.setter
    def revision(self, value: jsii.Number) -> None:
        jsii.set(self, "revision", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorPluginCustomPlugin]:
        return typing.cast(typing.Optional[MskconnectConnectorPluginCustomPlugin], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorPluginCustomPlugin],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectConnectorPluginList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorPluginList",
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
    def get(self, index: jsii.Number) -> "MskconnectConnectorPluginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("MskconnectConnectorPluginOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[MskconnectConnectorPlugin]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[MskconnectConnectorPlugin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[MskconnectConnectorPlugin]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectConnectorPluginOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorPluginOutputReference",
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

    @jsii.member(jsii_name="putCustomPlugin")
    def put_custom_plugin(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.
        '''
        value = MskconnectConnectorPluginCustomPlugin(arn=arn, revision=revision)

        return typing.cast(None, jsii.invoke(self, "putCustomPlugin", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customPlugin")
    def custom_plugin(self) -> MskconnectConnectorPluginCustomPluginOutputReference:
        return typing.cast(MskconnectConnectorPluginCustomPluginOutputReference, jsii.get(self, "customPlugin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customPluginInput")
    def custom_plugin_input(
        self,
    ) -> typing.Optional[MskconnectConnectorPluginCustomPlugin]:
        return typing.cast(typing.Optional[MskconnectConnectorPluginCustomPlugin], jsii.get(self, "customPluginInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MskconnectConnectorPlugin, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MskconnectConnectorPlugin, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MskconnectConnectorPlugin, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class MskconnectConnectorTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#create MskconnectConnector#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delete MskconnectConnector#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#update MskconnectConnector#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#create MskconnectConnector#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#delete MskconnectConnector#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#update MskconnectConnector#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MskconnectConnectorTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MskconnectConnectorTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MskconnectConnectorTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorWorkerConfiguration",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class MskconnectConnectorWorkerConfiguration:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#arn MskconnectConnector#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_connector#revision MskconnectConnector#revision}.'''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectConnectorWorkerConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectConnectorWorkerConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectConnectorWorkerConfigurationOutputReference",
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
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revisionInput")
    def revision_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "revisionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revision")
    def revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "revision"))

    @revision.setter
    def revision(self, value: jsii.Number) -> None:
        jsii.set(self, "revision", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectConnectorWorkerConfiguration]:
        return typing.cast(typing.Optional[MskconnectConnectorWorkerConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectConnectorWorkerConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectCustomPlugin(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin aws_mskconnect_custom_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        content_type: builtins.str,
        location: "MskconnectCustomPluginLocation",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["MskconnectCustomPluginTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin aws_mskconnect_custom_plugin} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#id MskconnectCustomPlugin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskconnectCustomPluginConfig(
            content_type=content_type,
            location=location,
            name=name,
            description=description,
            id=id,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putLocation")
    def put_location(self, *, s3: "MskconnectCustomPluginLocationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        value = MskconnectCustomPluginLocation(s3=s3)

        return typing.cast(None, jsii.invoke(self, "putLocation", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#delete MskconnectCustomPlugin#delete}.
        '''
        value = MskconnectCustomPluginTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> "MskconnectCustomPluginLocationOutputReference":
        return typing.cast("MskconnectCustomPluginLocationOutputReference", jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MskconnectCustomPluginTimeoutsOutputReference":
        return typing.cast("MskconnectCustomPluginTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional["MskconnectCustomPluginLocation"]:
        return typing.cast(typing.Optional["MskconnectCustomPluginLocation"], jsii.get(self, "locationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["MskconnectCustomPluginTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["MskconnectCustomPluginTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        jsii.set(self, "contentType", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content_type": "contentType",
        "location": "location",
        "name": "name",
        "description": "description",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class MskconnectCustomPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content_type: builtins.str,
        location: "MskconnectCustomPluginLocation",
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["MskconnectCustomPluginTimeouts"] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.
        :param location: location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#id MskconnectCustomPlugin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(location, dict):
            location = MskconnectCustomPluginLocation(**location)
        if isinstance(timeouts, dict):
            timeouts = MskconnectCustomPluginTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "content_type": content_type,
            "location": location,
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
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#content_type MskconnectCustomPlugin#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> "MskconnectCustomPluginLocation":
        '''location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#location MskconnectCustomPlugin#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast("MskconnectCustomPluginLocation", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#name MskconnectCustomPlugin#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#description MskconnectCustomPlugin#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#id MskconnectCustomPlugin#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MskconnectCustomPluginTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#timeouts MskconnectCustomPlugin#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MskconnectCustomPluginTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocation",
    jsii_struct_bases=[],
    name_mapping={"s3": "s3"},
)
class MskconnectCustomPluginLocation:
    def __init__(self, *, s3: "MskconnectCustomPluginLocationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        if isinstance(s3, dict):
            s3 = MskconnectCustomPluginLocationS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {
            "s3": s3,
        }

    @builtins.property
    def s3(self) -> "MskconnectCustomPluginLocationS3":
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#s3 MskconnectCustomPlugin#s3}
        '''
        result = self._values.get("s3")
        assert result is not None, "Required property 's3' is missing"
        return typing.cast("MskconnectCustomPluginLocationS3", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationOutputReference",
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

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        bucket_arn: builtins.str,
        file_key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.
        :param file_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.
        :param object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.
        '''
        value = MskconnectCustomPluginLocationS3(
            bucket_arn=bucket_arn, file_key=file_key, object_version=object_version
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "MskconnectCustomPluginLocationS3OutputReference":
        return typing.cast("MskconnectCustomPluginLocationS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["MskconnectCustomPluginLocationS3"]:
        return typing.cast(typing.Optional["MskconnectCustomPluginLocationS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectCustomPluginLocation]:
        return typing.cast(typing.Optional[MskconnectCustomPluginLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectCustomPluginLocation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationS3",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "file_key": "fileKey",
        "object_version": "objectVersion",
    },
)
class MskconnectCustomPluginLocationS3:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        file_key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.
        :param file_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.
        :param object_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "file_key": file_key,
        }
        if object_version is not None:
            self._values["object_version"] = object_version

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#bucket_arn MskconnectCustomPlugin#bucket_arn}.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#file_key MskconnectCustomPlugin#file_key}.'''
        result = self._values.get("file_key")
        assert result is not None, "Required property 'file_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#object_version MskconnectCustomPlugin#object_version}.'''
        result = self._values.get("object_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginLocationS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginLocationS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginLocationS3OutputReference",
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

    @jsii.member(jsii_name="resetObjectVersion")
    def reset_object_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArnInput")
    def bucket_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileKeyInput")
    def file_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectVersionInput")
    def object_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketArn"))

    @bucket_arn.setter
    def bucket_arn(self, value: builtins.str) -> None:
        jsii.set(self, "bucketArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileKey")
    def file_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileKey"))

    @file_key.setter
    def file_key(self, value: builtins.str) -> None:
        jsii.set(self, "fileKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectVersion")
    def object_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectVersion"))

    @object_version.setter
    def object_version(self, value: builtins.str) -> None:
        jsii.set(self, "objectVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MskconnectCustomPluginLocationS3]:
        return typing.cast(typing.Optional[MskconnectCustomPluginLocationS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MskconnectCustomPluginLocationS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class MskconnectCustomPluginTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#delete MskconnectCustomPlugin#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#create MskconnectCustomPlugin#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_custom_plugin#delete MskconnectCustomPlugin#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MskconnectCustomPluginTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MskconnectCustomPluginTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectCustomPluginTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[MskconnectCustomPluginTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[MskconnectCustomPluginTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[MskconnectCustomPluginTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class MskconnectWorkerConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.msk.MskconnectWorkerConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration aws_mskconnect_worker_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        properties_file_content: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration aws_mskconnect_worker_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.
        :param properties_file_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#id MskconnectWorkerConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MskconnectWorkerConfigurationConfig(
            name=name,
            properties_file_content=properties_file_content,
            description=description,
            id=id,
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
    @jsii.member(jsii_name="latestRevision")
    def latest_revision(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestRevision"))

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
    @jsii.member(jsii_name="propertiesFileContentInput")
    def properties_file_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propertiesFileContentInput"))

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
    @jsii.member(jsii_name="propertiesFileContent")
    def properties_file_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propertiesFileContent"))

    @properties_file_content.setter
    def properties_file_content(self, value: builtins.str) -> None:
        jsii.set(self, "propertiesFileContent", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.msk.MskconnectWorkerConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "properties_file_content": "propertiesFileContent",
        "description": "description",
        "id": "id",
    },
)
class MskconnectWorkerConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        properties_file_content: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Managed Streaming for Kafka.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.
        :param properties_file_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#id MskconnectWorkerConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "properties_file_content": properties_file_content,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#name MskconnectWorkerConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def properties_file_content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#properties_file_content MskconnectWorkerConfiguration#properties_file_content}.'''
        result = self._values.get("properties_file_content")
        assert result is not None, "Required property 'properties_file_content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#description MskconnectWorkerConfiguration#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/mskconnect_worker_configuration#id MskconnectWorkerConfiguration#id}.

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
        return "MskconnectWorkerConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsMskBrokerNodes",
    "DataAwsMskBrokerNodesConfig",
    "DataAwsMskBrokerNodesNodeInfoList",
    "DataAwsMskBrokerNodesNodeInfoListList",
    "DataAwsMskBrokerNodesNodeInfoListOutputReference",
    "DataAwsMskCluster",
    "DataAwsMskClusterConfig",
    "DataAwsMskConfiguration",
    "DataAwsMskConfigurationConfig",
    "DataAwsMskKafkaVersion",
    "DataAwsMskKafkaVersionConfig",
    "DataAwsMskconnectConnector",
    "DataAwsMskconnectConnectorConfig",
    "DataAwsMskconnectCustomPlugin",
    "DataAwsMskconnectCustomPluginConfig",
    "DataAwsMskconnectWorkerConfiguration",
    "DataAwsMskconnectWorkerConfigurationConfig",
    "MskCluster",
    "MskClusterBrokerNodeGroupInfo",
    "MskClusterBrokerNodeGroupInfoConnectivityInfo",
    "MskClusterBrokerNodeGroupInfoConnectivityInfoOutputReference",
    "MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccess",
    "MskClusterBrokerNodeGroupInfoConnectivityInfoPublicAccessOutputReference",
    "MskClusterBrokerNodeGroupInfoOutputReference",
    "MskClusterBrokerNodeGroupInfoStorageInfo",
    "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfo",
    "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoOutputReference",
    "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughput",
    "MskClusterBrokerNodeGroupInfoStorageInfoEbsStorageInfoProvisionedThroughputOutputReference",
    "MskClusterBrokerNodeGroupInfoStorageInfoOutputReference",
    "MskClusterClientAuthentication",
    "MskClusterClientAuthenticationOutputReference",
    "MskClusterClientAuthenticationSasl",
    "MskClusterClientAuthenticationSaslOutputReference",
    "MskClusterClientAuthenticationTls",
    "MskClusterClientAuthenticationTlsOutputReference",
    "MskClusterConfig",
    "MskClusterConfigurationInfo",
    "MskClusterConfigurationInfoOutputReference",
    "MskClusterEncryptionInfo",
    "MskClusterEncryptionInfoEncryptionInTransit",
    "MskClusterEncryptionInfoEncryptionInTransitOutputReference",
    "MskClusterEncryptionInfoOutputReference",
    "MskClusterLoggingInfo",
    "MskClusterLoggingInfoBrokerLogs",
    "MskClusterLoggingInfoBrokerLogsCloudwatchLogs",
    "MskClusterLoggingInfoBrokerLogsCloudwatchLogsOutputReference",
    "MskClusterLoggingInfoBrokerLogsFirehose",
    "MskClusterLoggingInfoBrokerLogsFirehoseOutputReference",
    "MskClusterLoggingInfoBrokerLogsOutputReference",
    "MskClusterLoggingInfoBrokerLogsS3",
    "MskClusterLoggingInfoBrokerLogsS3OutputReference",
    "MskClusterLoggingInfoOutputReference",
    "MskClusterOpenMonitoring",
    "MskClusterOpenMonitoringOutputReference",
    "MskClusterOpenMonitoringPrometheus",
    "MskClusterOpenMonitoringPrometheusJmxExporter",
    "MskClusterOpenMonitoringPrometheusJmxExporterOutputReference",
    "MskClusterOpenMonitoringPrometheusNodeExporter",
    "MskClusterOpenMonitoringPrometheusNodeExporterOutputReference",
    "MskClusterOpenMonitoringPrometheusOutputReference",
    "MskClusterTimeouts",
    "MskClusterTimeoutsOutputReference",
    "MskConfiguration",
    "MskConfigurationConfig",
    "MskScramSecretAssociation",
    "MskScramSecretAssociationConfig",
    "MskconnectConnector",
    "MskconnectConnectorCapacity",
    "MskconnectConnectorCapacityAutoscaling",
    "MskconnectConnectorCapacityAutoscalingOutputReference",
    "MskconnectConnectorCapacityAutoscalingScaleInPolicy",
    "MskconnectConnectorCapacityAutoscalingScaleInPolicyOutputReference",
    "MskconnectConnectorCapacityAutoscalingScaleOutPolicy",
    "MskconnectConnectorCapacityAutoscalingScaleOutPolicyOutputReference",
    "MskconnectConnectorCapacityOutputReference",
    "MskconnectConnectorCapacityProvisionedCapacity",
    "MskconnectConnectorCapacityProvisionedCapacityOutputReference",
    "MskconnectConnectorConfig",
    "MskconnectConnectorKafkaCluster",
    "MskconnectConnectorKafkaClusterApacheKafkaCluster",
    "MskconnectConnectorKafkaClusterApacheKafkaClusterOutputReference",
    "MskconnectConnectorKafkaClusterApacheKafkaClusterVpc",
    "MskconnectConnectorKafkaClusterApacheKafkaClusterVpcOutputReference",
    "MskconnectConnectorKafkaClusterClientAuthentication",
    "MskconnectConnectorKafkaClusterClientAuthenticationOutputReference",
    "MskconnectConnectorKafkaClusterEncryptionInTransit",
    "MskconnectConnectorKafkaClusterEncryptionInTransitOutputReference",
    "MskconnectConnectorKafkaClusterOutputReference",
    "MskconnectConnectorLogDelivery",
    "MskconnectConnectorLogDeliveryOutputReference",
    "MskconnectConnectorLogDeliveryWorkerLogDelivery",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogs",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryCloudwatchLogsOutputReference",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehose",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryFirehoseOutputReference",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryOutputReference",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryS3",
    "MskconnectConnectorLogDeliveryWorkerLogDeliveryS3OutputReference",
    "MskconnectConnectorPlugin",
    "MskconnectConnectorPluginCustomPlugin",
    "MskconnectConnectorPluginCustomPluginOutputReference",
    "MskconnectConnectorPluginList",
    "MskconnectConnectorPluginOutputReference",
    "MskconnectConnectorTimeouts",
    "MskconnectConnectorTimeoutsOutputReference",
    "MskconnectConnectorWorkerConfiguration",
    "MskconnectConnectorWorkerConfigurationOutputReference",
    "MskconnectCustomPlugin",
    "MskconnectCustomPluginConfig",
    "MskconnectCustomPluginLocation",
    "MskconnectCustomPluginLocationOutputReference",
    "MskconnectCustomPluginLocationS3",
    "MskconnectCustomPluginLocationS3OutputReference",
    "MskconnectCustomPluginTimeouts",
    "MskconnectCustomPluginTimeoutsOutputReference",
    "MskconnectWorkerConfiguration",
    "MskconnectWorkerConfigurationConfig",
]

publication.publish()
