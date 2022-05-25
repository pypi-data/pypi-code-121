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


class DataAwsSignerSigningJob(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJob",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job aws_signer_signing_job}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        job_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job aws_signer_signing_job} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param job_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#job_id DataAwsSignerSigningJob#job_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#id DataAwsSignerSigningJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSignerSigningJobConfig(
            job_id=job_id,
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
    @jsii.member(jsii_name="completedAt")
    def completed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "completedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobInvoker")
    def job_invoker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobInvoker"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobOwner")
    def job_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobOwner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformDisplayName")
    def platform_display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformDisplayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformId")
    def platform_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileName")
    def profile_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileVersion")
    def profile_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestedBy")
    def requested_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revocationRecord")
    def revocation_record(self) -> "DataAwsSignerSigningJobRevocationRecordList":
        return typing.cast("DataAwsSignerSigningJobRevocationRecordList", jsii.get(self, "revocationRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureExpiresAt")
    def signature_expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureExpiresAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signedObject")
    def signed_object(self) -> "DataAwsSignerSigningJobSignedObjectList":
        return typing.cast("DataAwsSignerSigningJobSignedObjectList", jsii.get(self, "signedObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "DataAwsSignerSigningJobSourceList":
        return typing.cast("DataAwsSignerSigningJobSourceList", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobIdInput")
    def job_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobId"))

    @job_id.setter
    def job_id(self, value: builtins.str) -> None:
        jsii.set(self, "jobId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "job_id": "jobId",
        "id": "id",
    },
)
class DataAwsSignerSigningJobConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        job_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Signer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param job_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#job_id DataAwsSignerSigningJob#job_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#id DataAwsSignerSigningJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "job_id": job_id,
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
    def job_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#job_id DataAwsSignerSigningJob#job_id}.'''
        result = self._values.get("job_id")
        assert result is not None, "Required property 'job_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_job#id DataAwsSignerSigningJob#id}.

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
        return "DataAwsSignerSigningJobConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobRevocationRecord",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningJobRevocationRecord:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningJobRevocationRecord(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningJobRevocationRecordList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobRevocationRecordList",
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
    ) -> "DataAwsSignerSigningJobRevocationRecordOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningJobRevocationRecordOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningJobRevocationRecordOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobRevocationRecordOutputReference",
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
    @jsii.member(jsii_name="reason")
    def reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedAt")
    def revoked_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedBy")
    def revoked_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsSignerSigningJobRevocationRecord]:
        return typing.cast(typing.Optional[DataAwsSignerSigningJobRevocationRecord], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningJobRevocationRecord],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObject",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningJobSignedObject:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningJobSignedObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningJobSignedObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObjectList",
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
    ) -> "DataAwsSignerSigningJobSignedObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningJobSignedObjectOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningJobSignedObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObjectOutputReference",
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
    @jsii.member(jsii_name="s3")
    def s3(self) -> "DataAwsSignerSigningJobSignedObjectS3List":
        return typing.cast("DataAwsSignerSigningJobSignedObjectS3List", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsSignerSigningJobSignedObject]:
        return typing.cast(typing.Optional[DataAwsSignerSigningJobSignedObject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningJobSignedObject],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObjectS3",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningJobSignedObjectS3:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningJobSignedObjectS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningJobSignedObjectS3List(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObjectS3List",
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
    ) -> "DataAwsSignerSigningJobSignedObjectS3OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningJobSignedObjectS3OutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningJobSignedObjectS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSignedObjectS3OutputReference",
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
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsSignerSigningJobSignedObjectS3]:
        return typing.cast(typing.Optional[DataAwsSignerSigningJobSignedObjectS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningJobSignedObjectS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSource",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningJobSource:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningJobSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningJobSourceList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSourceList",
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
    def get(self, index: jsii.Number) -> "DataAwsSignerSigningJobSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningJobSourceOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningJobSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSourceOutputReference",
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
    @jsii.member(jsii_name="s3")
    def s3(self) -> "DataAwsSignerSigningJobSourceS3List":
        return typing.cast("DataAwsSignerSigningJobSourceS3List", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsSignerSigningJobSource]:
        return typing.cast(typing.Optional[DataAwsSignerSigningJobSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningJobSource],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSourceS3",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningJobSourceS3:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningJobSourceS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningJobSourceS3List(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSourceS3List",
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
    ) -> "DataAwsSignerSigningJobSourceS3OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningJobSourceS3OutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningJobSourceS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningJobSourceS3OutputReference",
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
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataAwsSignerSigningJobSourceS3]:
        return typing.cast(typing.Optional[DataAwsSignerSigningJobSourceS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningJobSourceS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsSignerSigningProfile(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile aws_signer_signing_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile aws_signer_signing_profile} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#name DataAwsSignerSigningProfile#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#id DataAwsSignerSigningProfile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#tags DataAwsSignerSigningProfile#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSignerSigningProfileConfig(
            name=name,
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
    @jsii.member(jsii_name="platformDisplayName")
    def platform_display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformDisplayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformId")
    def platform_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revocationRecord")
    def revocation_record(self) -> "DataAwsSignerSigningProfileRevocationRecordList":
        return typing.cast("DataAwsSignerSigningProfileRevocationRecordList", jsii.get(self, "revocationRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureValidityPeriod")
    def signature_validity_period(
        self,
    ) -> "DataAwsSignerSigningProfileSignatureValidityPeriodList":
        return typing.cast("DataAwsSignerSigningProfileSignatureValidityPeriodList", jsii.get(self, "signatureValidityPeriod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionArn")
    def version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsSignerSigningProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Signer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#name DataAwsSignerSigningProfile#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#id DataAwsSignerSigningProfile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#tags DataAwsSignerSigningProfile#tags}.
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#name DataAwsSignerSigningProfile#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#id DataAwsSignerSigningProfile#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/signer_signing_profile#tags DataAwsSignerSigningProfile#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileRevocationRecord",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningProfileRevocationRecord:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningProfileRevocationRecord(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningProfileRevocationRecordList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileRevocationRecordList",
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
    ) -> "DataAwsSignerSigningProfileRevocationRecordOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningProfileRevocationRecordOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningProfileRevocationRecordOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileRevocationRecordOutputReference",
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
    @jsii.member(jsii_name="revocationEffectiveFrom")
    def revocation_effective_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revocationEffectiveFrom"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedAt")
    def revoked_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedBy")
    def revoked_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsSignerSigningProfileRevocationRecord]:
        return typing.cast(typing.Optional[DataAwsSignerSigningProfileRevocationRecord], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningProfileRevocationRecord],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileSignatureValidityPeriod",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsSignerSigningProfileSignatureValidityPeriod:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSignerSigningProfileSignatureValidityPeriod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSignerSigningProfileSignatureValidityPeriodList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileSignatureValidityPeriodList",
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
    ) -> "DataAwsSignerSigningProfileSignatureValidityPeriodOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataAwsSignerSigningProfileSignatureValidityPeriodOutputReference", jsii.invoke(self, "get", [index]))

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


class DataAwsSignerSigningProfileSignatureValidityPeriodOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.DataAwsSignerSigningProfileSignatureValidityPeriodOutputReference",
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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsSignerSigningProfileSignatureValidityPeriod]:
        return typing.cast(typing.Optional[DataAwsSignerSigningProfileSignatureValidityPeriod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsSignerSigningProfileSignatureValidityPeriod],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SignerSigningJob(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJob",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job aws_signer_signing_job}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        destination: "SignerSigningJobDestination",
        profile_name: builtins.str,
        source: "SignerSigningJobSource",
        id: typing.Optional[builtins.str] = None,
        ignore_signing_job_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job aws_signer_signing_job} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#destination SignerSigningJob#destination}
        :param profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#profile_name SignerSigningJob#profile_name}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#source SignerSigningJob#source}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#id SignerSigningJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_signing_job_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#ignore_signing_job_failure SignerSigningJob#ignore_signing_job_failure}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SignerSigningJobConfig(
            destination=destination,
            profile_name=profile_name,
            source=source,
            id=id,
            ignore_signing_job_failure=ignore_signing_job_failure,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putDestination")
    def put_destination(self, *, s3: "SignerSigningJobDestinationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        value = SignerSigningJobDestination(s3=s3)

        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putSource")
    def put_source(self, *, s3: "SignerSigningJobSourceS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        value = SignerSigningJobSource(s3=s3)

        return typing.cast(None, jsii.invoke(self, "putSource", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIgnoreSigningJobFailure")
    def reset_ignore_signing_job_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreSigningJobFailure", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="completedAt")
    def completed_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "completedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> "SignerSigningJobDestinationOutputReference":
        return typing.cast("SignerSigningJobDestinationOutputReference", jsii.get(self, "destination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobInvoker")
    def job_invoker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobInvoker"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobOwner")
    def job_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobOwner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformDisplayName")
    def platform_display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformDisplayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformId")
    def platform_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileVersion")
    def profile_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestedBy")
    def requested_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revocationRecord")
    def revocation_record(self) -> "SignerSigningJobRevocationRecordList":
        return typing.cast("SignerSigningJobRevocationRecordList", jsii.get(self, "revocationRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureExpiresAt")
    def signature_expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureExpiresAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signedObject")
    def signed_object(self) -> "SignerSigningJobSignedObjectList":
        return typing.cast("SignerSigningJobSignedObjectList", jsii.get(self, "signedObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "SignerSigningJobSourceOutputReference":
        return typing.cast("SignerSigningJobSourceOutputReference", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional["SignerSigningJobDestination"]:
        return typing.cast(typing.Optional["SignerSigningJobDestination"], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreSigningJobFailureInput")
    def ignore_signing_job_failure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignoreSigningJobFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileNameInput")
    def profile_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional["SignerSigningJobSource"]:
        return typing.cast(typing.Optional["SignerSigningJobSource"], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreSigningJobFailure")
    def ignore_signing_job_failure(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignoreSigningJobFailure"))

    @ignore_signing_job_failure.setter
    def ignore_signing_job_failure(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignoreSigningJobFailure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileName")
    def profile_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileName"))

    @profile_name.setter
    def profile_name(self, value: builtins.str) -> None:
        jsii.set(self, "profileName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "destination": "destination",
        "profile_name": "profileName",
        "source": "source",
        "id": "id",
        "ignore_signing_job_failure": "ignoreSigningJobFailure",
    },
)
class SignerSigningJobConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        destination: "SignerSigningJobDestination",
        profile_name: builtins.str,
        source: "SignerSigningJobSource",
        id: typing.Optional[builtins.str] = None,
        ignore_signing_job_failure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Signer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#destination SignerSigningJob#destination}
        :param profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#profile_name SignerSigningJob#profile_name}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#source SignerSigningJob#source}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#id SignerSigningJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_signing_job_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#ignore_signing_job_failure SignerSigningJob#ignore_signing_job_failure}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(destination, dict):
            destination = SignerSigningJobDestination(**destination)
        if isinstance(source, dict):
            source = SignerSigningJobSource(**source)
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "profile_name": profile_name,
            "source": source,
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
        if ignore_signing_job_failure is not None:
            self._values["ignore_signing_job_failure"] = ignore_signing_job_failure

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
    def destination(self) -> "SignerSigningJobDestination":
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#destination SignerSigningJob#destination}
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("SignerSigningJobDestination", result)

    @builtins.property
    def profile_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#profile_name SignerSigningJob#profile_name}.'''
        result = self._values.get("profile_name")
        assert result is not None, "Required property 'profile_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> "SignerSigningJobSource":
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#source SignerSigningJob#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("SignerSigningJobSource", result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#id SignerSigningJob#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_signing_job_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#ignore_signing_job_failure SignerSigningJob#ignore_signing_job_failure}.'''
        result = self._values.get("ignore_signing_job_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobDestination",
    jsii_struct_bases=[],
    name_mapping={"s3": "s3"},
)
class SignerSigningJobDestination:
    def __init__(self, *, s3: "SignerSigningJobDestinationS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        if isinstance(s3, dict):
            s3 = SignerSigningJobDestinationS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {
            "s3": s3,
        }

    @builtins.property
    def s3(self) -> "SignerSigningJobDestinationS3":
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        result = self._values.get("s3")
        assert result is not None, "Required property 's3' is missing"
        return typing.cast("SignerSigningJobDestinationS3", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobDestinationOutputReference",
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
        bucket: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#prefix SignerSigningJob#prefix}.
        '''
        value = SignerSigningJobDestinationS3(bucket=bucket, prefix=prefix)

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "SignerSigningJobDestinationS3OutputReference":
        return typing.cast("SignerSigningJobDestinationS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["SignerSigningJobDestinationS3"]:
        return typing.cast(typing.Optional["SignerSigningJobDestinationS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobDestination]:
        return typing.cast(typing.Optional[SignerSigningJobDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningJobDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobDestinationS3",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "prefix": "prefix"},
)
class SignerSigningJobDestinationS3:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#prefix SignerSigningJob#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#prefix SignerSigningJob#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobDestinationS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobDestinationS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobDestinationS3OutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

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
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobDestinationS3]:
        return typing.cast(typing.Optional[SignerSigningJobDestinationS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningJobDestinationS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobRevocationRecord",
    jsii_struct_bases=[],
    name_mapping={},
)
class SignerSigningJobRevocationRecord:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobRevocationRecord(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobRevocationRecordList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobRevocationRecordList",
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
    ) -> "SignerSigningJobRevocationRecordOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("SignerSigningJobRevocationRecordOutputReference", jsii.invoke(self, "get", [index]))

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


class SignerSigningJobRevocationRecordOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobRevocationRecordOutputReference",
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
    @jsii.member(jsii_name="reason")
    def reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reason"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedAt")
    def revoked_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedBy")
    def revoked_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobRevocationRecord]:
        return typing.cast(typing.Optional[SignerSigningJobRevocationRecord], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningJobRevocationRecord],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObject",
    jsii_struct_bases=[],
    name_mapping={},
)
class SignerSigningJobSignedObject:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobSignedObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobSignedObjectList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObjectList",
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
    def get(self, index: jsii.Number) -> "SignerSigningJobSignedObjectOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("SignerSigningJobSignedObjectOutputReference", jsii.invoke(self, "get", [index]))

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


class SignerSigningJobSignedObjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObjectOutputReference",
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
    @jsii.member(jsii_name="s3")
    def s3(self) -> "SignerSigningJobSignedObjectS3List":
        return typing.cast("SignerSigningJobSignedObjectS3List", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobSignedObject]:
        return typing.cast(typing.Optional[SignerSigningJobSignedObject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningJobSignedObject],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObjectS3",
    jsii_struct_bases=[],
    name_mapping={},
)
class SignerSigningJobSignedObjectS3:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobSignedObjectS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobSignedObjectS3List(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObjectS3List",
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
    ) -> "SignerSigningJobSignedObjectS3OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("SignerSigningJobSignedObjectS3OutputReference", jsii.invoke(self, "get", [index]))

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


class SignerSigningJobSignedObjectS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSignedObjectS3OutputReference",
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
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobSignedObjectS3]:
        return typing.cast(typing.Optional[SignerSigningJobSignedObjectS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningJobSignedObjectS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSource",
    jsii_struct_bases=[],
    name_mapping={"s3": "s3"},
)
class SignerSigningJobSource:
    def __init__(self, *, s3: "SignerSigningJobSourceS3") -> None:
        '''
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        if isinstance(s3, dict):
            s3 = SignerSigningJobSourceS3(**s3)
        self._values: typing.Dict[str, typing.Any] = {
            "s3": s3,
        }

    @builtins.property
    def s3(self) -> "SignerSigningJobSourceS3":
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#s3 SignerSigningJob#s3}
        '''
        result = self._values.get("s3")
        assert result is not None, "Required property 's3' is missing"
        return typing.cast("SignerSigningJobSourceS3", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobSourceOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSourceOutputReference",
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
        bucket: builtins.str,
        key: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#key SignerSigningJob#key}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#version SignerSigningJob#version}.
        '''
        value = SignerSigningJobSourceS3(bucket=bucket, key=key, version=version)

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "SignerSigningJobSourceS3OutputReference":
        return typing.cast("SignerSigningJobSourceS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["SignerSigningJobSourceS3"]:
        return typing.cast(typing.Optional["SignerSigningJobSourceS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobSource]:
        return typing.cast(typing.Optional[SignerSigningJobSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SignerSigningJobSource]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSourceS3",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key", "version": "version"},
)
class SignerSigningJobSourceS3:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        key: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#key SignerSigningJob#key}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#version SignerSigningJob#version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
            "version": version,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#bucket SignerSigningJob#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#key SignerSigningJob#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_job#version SignerSigningJob#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningJobSourceS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningJobSourceS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningJobSourceS3OutputReference",
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningJobSourceS3]:
        return typing.cast(typing.Optional[SignerSigningJobSourceS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SignerSigningJobSourceS3]) -> None:
        jsii.set(self, "internalValue", value)


class SignerSigningProfile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile aws_signer_signing_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        platform_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        signature_validity_period: typing.Optional["SignerSigningProfileSignatureValidityPeriod"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile aws_signer_signing_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param platform_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#platform_id SignerSigningProfile#platform_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#id SignerSigningProfile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name SignerSigningProfile#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name_prefix SignerSigningProfile#name_prefix}.
        :param signature_validity_period: signature_validity_period block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#signature_validity_period SignerSigningProfile#signature_validity_period}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags SignerSigningProfile#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags_all SignerSigningProfile#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SignerSigningProfileConfig(
            platform_id=platform_id,
            id=id,
            name=name,
            name_prefix=name_prefix,
            signature_validity_period=signature_validity_period,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putSignatureValidityPeriod")
    def put_signature_validity_period(
        self,
        *,
        type: builtins.str,
        value: jsii.Number,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#type SignerSigningProfile#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#value SignerSigningProfile#value}.
        '''
        value_ = SignerSigningProfileSignatureValidityPeriod(type=type, value=value)

        return typing.cast(None, jsii.invoke(self, "putSignatureValidityPeriod", [value_]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetSignatureValidityPeriod")
    def reset_signature_validity_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureValidityPeriod", []))

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
    @jsii.member(jsii_name="platformDisplayName")
    def platform_display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformDisplayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revocationRecord")
    def revocation_record(self) -> "SignerSigningProfileRevocationRecordList":
        return typing.cast("SignerSigningProfileRevocationRecordList", jsii.get(self, "revocationRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureValidityPeriod")
    def signature_validity_period(
        self,
    ) -> "SignerSigningProfileSignatureValidityPeriodOutputReference":
        return typing.cast("SignerSigningProfileSignatureValidityPeriodOutputReference", jsii.get(self, "signatureValidityPeriod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionArn")
    def version_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformIdInput")
    def platform_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureValidityPeriodInput")
    def signature_validity_period_input(
        self,
    ) -> typing.Optional["SignerSigningProfileSignatureValidityPeriod"]:
        return typing.cast(typing.Optional["SignerSigningProfileSignatureValidityPeriod"], jsii.get(self, "signatureValidityPeriodInput"))

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
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformId")
    def platform_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platformId"))

    @platform_id.setter
    def platform_id(self, value: builtins.str) -> None:
        jsii.set(self, "platformId", value)

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
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "platform_id": "platformId",
        "id": "id",
        "name": "name",
        "name_prefix": "namePrefix",
        "signature_validity_period": "signatureValidityPeriod",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class SignerSigningProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        platform_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        signature_validity_period: typing.Optional["SignerSigningProfileSignatureValidityPeriod"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS Signer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param platform_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#platform_id SignerSigningProfile#platform_id}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#id SignerSigningProfile#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name SignerSigningProfile#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name_prefix SignerSigningProfile#name_prefix}.
        :param signature_validity_period: signature_validity_period block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#signature_validity_period SignerSigningProfile#signature_validity_period}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags SignerSigningProfile#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags_all SignerSigningProfile#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(signature_validity_period, dict):
            signature_validity_period = SignerSigningProfileSignatureValidityPeriod(**signature_validity_period)
        self._values: typing.Dict[str, typing.Any] = {
            "platform_id": platform_id,
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
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if signature_validity_period is not None:
            self._values["signature_validity_period"] = signature_validity_period
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
    def platform_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#platform_id SignerSigningProfile#platform_id}.'''
        result = self._values.get("platform_id")
        assert result is not None, "Required property 'platform_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#id SignerSigningProfile#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name SignerSigningProfile#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#name_prefix SignerSigningProfile#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_validity_period(
        self,
    ) -> typing.Optional["SignerSigningProfileSignatureValidityPeriod"]:
        '''signature_validity_period block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#signature_validity_period SignerSigningProfile#signature_validity_period}
        '''
        result = self._values.get("signature_validity_period")
        return typing.cast(typing.Optional["SignerSigningProfileSignatureValidityPeriod"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags SignerSigningProfile#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#tags_all SignerSigningProfile#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningProfilePermission(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfilePermission",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission aws_signer_signing_profile_permission}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        action: builtins.str,
        principal: builtins.str,
        profile_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        profile_version: typing.Optional[builtins.str] = None,
        statement_id: typing.Optional[builtins.str] = None,
        statement_id_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission aws_signer_signing_profile_permission} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#action SignerSigningProfilePermission#action}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#principal SignerSigningProfilePermission#principal}.
        :param profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_name SignerSigningProfilePermission#profile_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#id SignerSigningProfilePermission#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param profile_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_version SignerSigningProfilePermission#profile_version}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id SignerSigningProfilePermission#statement_id}.
        :param statement_id_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id_prefix SignerSigningProfilePermission#statement_id_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SignerSigningProfilePermissionConfig(
            action=action,
            principal=principal,
            profile_name=profile_name,
            id=id,
            profile_version=profile_version,
            statement_id=statement_id,
            statement_id_prefix=statement_id_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProfileVersion")
    def reset_profile_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfileVersion", []))

    @jsii.member(jsii_name="resetStatementId")
    def reset_statement_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatementId", []))

    @jsii.member(jsii_name="resetStatementIdPrefix")
    def reset_statement_id_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatementIdPrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileNameInput")
    def profile_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileVersionInput")
    def profile_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdInput")
    def statement_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statementIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdPrefixInput")
    def statement_id_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statementIdPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        jsii.set(self, "action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        jsii.set(self, "principal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileName")
    def profile_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileName"))

    @profile_name.setter
    def profile_name(self, value: builtins.str) -> None:
        jsii.set(self, "profileName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileVersion")
    def profile_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profileVersion"))

    @profile_version.setter
    def profile_version(self, value: builtins.str) -> None:
        jsii.set(self, "profileVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementId")
    def statement_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statementId"))

    @statement_id.setter
    def statement_id(self, value: builtins.str) -> None:
        jsii.set(self, "statementId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementIdPrefix")
    def statement_id_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statementIdPrefix"))

    @statement_id_prefix.setter
    def statement_id_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "statementIdPrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfilePermissionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action": "action",
        "principal": "principal",
        "profile_name": "profileName",
        "id": "id",
        "profile_version": "profileVersion",
        "statement_id": "statementId",
        "statement_id_prefix": "statementIdPrefix",
    },
)
class SignerSigningProfilePermissionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action: builtins.str,
        principal: builtins.str,
        profile_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        profile_version: typing.Optional[builtins.str] = None,
        statement_id: typing.Optional[builtins.str] = None,
        statement_id_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Signer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#action SignerSigningProfilePermission#action}.
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#principal SignerSigningProfilePermission#principal}.
        :param profile_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_name SignerSigningProfilePermission#profile_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#id SignerSigningProfilePermission#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param profile_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_version SignerSigningProfilePermission#profile_version}.
        :param statement_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id SignerSigningProfilePermission#statement_id}.
        :param statement_id_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id_prefix SignerSigningProfilePermission#statement_id_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "principal": principal,
            "profile_name": profile_name,
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
        if profile_version is not None:
            self._values["profile_version"] = profile_version
        if statement_id is not None:
            self._values["statement_id"] = statement_id
        if statement_id_prefix is not None:
            self._values["statement_id_prefix"] = statement_id_prefix

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
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#action SignerSigningProfilePermission#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#principal SignerSigningProfilePermission#principal}.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_name SignerSigningProfilePermission#profile_name}.'''
        result = self._values.get("profile_name")
        assert result is not None, "Required property 'profile_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#id SignerSigningProfilePermission#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def profile_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#profile_version SignerSigningProfilePermission#profile_version}.'''
        result = self._values.get("profile_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statement_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id SignerSigningProfilePermission#statement_id}.'''
        result = self._values.get("statement_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statement_id_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile_permission#statement_id_prefix SignerSigningProfilePermission#statement_id_prefix}.'''
        result = self._values.get("statement_id_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningProfilePermissionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileRevocationRecord",
    jsii_struct_bases=[],
    name_mapping={},
)
class SignerSigningProfileRevocationRecord:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningProfileRevocationRecord(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningProfileRevocationRecordList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileRevocationRecordList",
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
    ) -> "SignerSigningProfileRevocationRecordOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("SignerSigningProfileRevocationRecordOutputReference", jsii.invoke(self, "get", [index]))

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


class SignerSigningProfileRevocationRecordOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileRevocationRecordOutputReference",
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
    @jsii.member(jsii_name="revocationEffectiveFrom")
    def revocation_effective_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revocationEffectiveFrom"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedAt")
    def revoked_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="revokedBy")
    def revoked_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SignerSigningProfileRevocationRecord]:
        return typing.cast(typing.Optional[SignerSigningProfileRevocationRecord], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningProfileRevocationRecord],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileSignatureValidityPeriod",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "value": "value"},
)
class SignerSigningProfileSignatureValidityPeriod:
    def __init__(self, *, type: builtins.str, value: jsii.Number) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#type SignerSigningProfile#type}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#value SignerSigningProfile#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "value": value,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#type SignerSigningProfile#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/signer_signing_profile#value SignerSigningProfile#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignerSigningProfileSignatureValidityPeriod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignerSigningProfileSignatureValidityPeriodOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.signer.SignerSigningProfileSignatureValidityPeriodOutputReference",
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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[SignerSigningProfileSignatureValidityPeriod]:
        return typing.cast(typing.Optional[SignerSigningProfileSignatureValidityPeriod], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SignerSigningProfileSignatureValidityPeriod],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsSignerSigningJob",
    "DataAwsSignerSigningJobConfig",
    "DataAwsSignerSigningJobRevocationRecord",
    "DataAwsSignerSigningJobRevocationRecordList",
    "DataAwsSignerSigningJobRevocationRecordOutputReference",
    "DataAwsSignerSigningJobSignedObject",
    "DataAwsSignerSigningJobSignedObjectList",
    "DataAwsSignerSigningJobSignedObjectOutputReference",
    "DataAwsSignerSigningJobSignedObjectS3",
    "DataAwsSignerSigningJobSignedObjectS3List",
    "DataAwsSignerSigningJobSignedObjectS3OutputReference",
    "DataAwsSignerSigningJobSource",
    "DataAwsSignerSigningJobSourceList",
    "DataAwsSignerSigningJobSourceOutputReference",
    "DataAwsSignerSigningJobSourceS3",
    "DataAwsSignerSigningJobSourceS3List",
    "DataAwsSignerSigningJobSourceS3OutputReference",
    "DataAwsSignerSigningProfile",
    "DataAwsSignerSigningProfileConfig",
    "DataAwsSignerSigningProfileRevocationRecord",
    "DataAwsSignerSigningProfileRevocationRecordList",
    "DataAwsSignerSigningProfileRevocationRecordOutputReference",
    "DataAwsSignerSigningProfileSignatureValidityPeriod",
    "DataAwsSignerSigningProfileSignatureValidityPeriodList",
    "DataAwsSignerSigningProfileSignatureValidityPeriodOutputReference",
    "SignerSigningJob",
    "SignerSigningJobConfig",
    "SignerSigningJobDestination",
    "SignerSigningJobDestinationOutputReference",
    "SignerSigningJobDestinationS3",
    "SignerSigningJobDestinationS3OutputReference",
    "SignerSigningJobRevocationRecord",
    "SignerSigningJobRevocationRecordList",
    "SignerSigningJobRevocationRecordOutputReference",
    "SignerSigningJobSignedObject",
    "SignerSigningJobSignedObjectList",
    "SignerSigningJobSignedObjectOutputReference",
    "SignerSigningJobSignedObjectS3",
    "SignerSigningJobSignedObjectS3List",
    "SignerSigningJobSignedObjectS3OutputReference",
    "SignerSigningJobSource",
    "SignerSigningJobSourceOutputReference",
    "SignerSigningJobSourceS3",
    "SignerSigningJobSourceS3OutputReference",
    "SignerSigningProfile",
    "SignerSigningProfileConfig",
    "SignerSigningProfilePermission",
    "SignerSigningProfilePermissionConfig",
    "SignerSigningProfileRevocationRecord",
    "SignerSigningProfileRevocationRecordList",
    "SignerSigningProfileRevocationRecordOutputReference",
    "SignerSigningProfileSignatureValidityPeriod",
    "SignerSigningProfileSignatureValidityPeriodOutputReference",
]

publication.publish()
