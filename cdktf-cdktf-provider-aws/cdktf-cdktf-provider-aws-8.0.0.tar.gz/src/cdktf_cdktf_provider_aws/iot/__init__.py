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


class DataAwsIotEndpoint(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.DataAwsIotEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint aws_iot_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        endpoint_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint aws_iot_endpoint} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#endpoint_type DataAwsIotEndpoint#endpoint_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#id DataAwsIotEndpoint#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIotEndpointConfig(
            endpoint_type=endpoint_type,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetEndpointType")
    def reset_endpoint_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointType", []))

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
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointTypeInput")
    def endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.DataAwsIotEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "endpoint_type": "endpointType",
        "id": "id",
    },
)
class DataAwsIotEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        endpoint_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#endpoint_type DataAwsIotEndpoint#endpoint_type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#id DataAwsIotEndpoint#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
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
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
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
    def endpoint_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#endpoint_type DataAwsIotEndpoint#endpoint_type}.'''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iot_endpoint#id DataAwsIotEndpoint#id}.

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
        return "DataAwsIotEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotAuthorizer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotAuthorizer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer aws_iot_authorizer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        authorizer_function_arn: builtins.str,
        name: builtins.str,
        enable_caching_for_http: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        signing_disabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        status: typing.Optional[builtins.str] = None,
        token_key_name: typing.Optional[builtins.str] = None,
        token_signing_public_keys: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer aws_iot_authorizer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authorizer_function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#authorizer_function_arn IotAuthorizer#authorizer_function_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#name IotAuthorizer#name}.
        :param enable_caching_for_http: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#enable_caching_for_http IotAuthorizer#enable_caching_for_http}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#id IotAuthorizer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param signing_disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#signing_disabled IotAuthorizer#signing_disabled}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#status IotAuthorizer#status}.
        :param token_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_key_name IotAuthorizer#token_key_name}.
        :param token_signing_public_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_signing_public_keys IotAuthorizer#token_signing_public_keys}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotAuthorizerConfig(
            authorizer_function_arn=authorizer_function_arn,
            name=name,
            enable_caching_for_http=enable_caching_for_http,
            id=id,
            signing_disabled=signing_disabled,
            status=status,
            token_key_name=token_key_name,
            token_signing_public_keys=token_signing_public_keys,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetEnableCachingForHttp")
    def reset_enable_caching_for_http(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableCachingForHttp", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSigningDisabled")
    def reset_signing_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSigningDisabled", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetTokenKeyName")
    def reset_token_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenKeyName", []))

    @jsii.member(jsii_name="resetTokenSigningPublicKeys")
    def reset_token_signing_public_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenSigningPublicKeys", []))

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
    @jsii.member(jsii_name="authorizerFunctionArnInput")
    def authorizer_function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerFunctionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableCachingForHttpInput")
    def enable_caching_for_http_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableCachingForHttpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingDisabledInput")
    def signing_disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "signingDisabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenKeyNameInput")
    def token_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenKeyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenSigningPublicKeysInput")
    def token_signing_public_keys_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tokenSigningPublicKeysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerFunctionArn")
    def authorizer_function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizerFunctionArn"))

    @authorizer_function_arn.setter
    def authorizer_function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerFunctionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableCachingForHttp")
    def enable_caching_for_http(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableCachingForHttp"))

    @enable_caching_for_http.setter
    def enable_caching_for_http(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableCachingForHttp", value)

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
    @jsii.member(jsii_name="signingDisabled")
    def signing_disabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "signingDisabled"))

    @signing_disabled.setter
    def signing_disabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "signingDisabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenKeyName")
    def token_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenKeyName"))

    @token_key_name.setter
    def token_key_name(self, value: builtins.str) -> None:
        jsii.set(self, "tokenKeyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenSigningPublicKeys")
    def token_signing_public_keys(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tokenSigningPublicKeys"))

    @token_signing_public_keys.setter
    def token_signing_public_keys(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        jsii.set(self, "tokenSigningPublicKeys", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotAuthorizerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "authorizer_function_arn": "authorizerFunctionArn",
        "name": "name",
        "enable_caching_for_http": "enableCachingForHttp",
        "id": "id",
        "signing_disabled": "signingDisabled",
        "status": "status",
        "token_key_name": "tokenKeyName",
        "token_signing_public_keys": "tokenSigningPublicKeys",
    },
)
class IotAuthorizerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        authorizer_function_arn: builtins.str,
        name: builtins.str,
        enable_caching_for_http: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        signing_disabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        status: typing.Optional[builtins.str] = None,
        token_key_name: typing.Optional[builtins.str] = None,
        token_signing_public_keys: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param authorizer_function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#authorizer_function_arn IotAuthorizer#authorizer_function_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#name IotAuthorizer#name}.
        :param enable_caching_for_http: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#enable_caching_for_http IotAuthorizer#enable_caching_for_http}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#id IotAuthorizer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param signing_disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#signing_disabled IotAuthorizer#signing_disabled}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#status IotAuthorizer#status}.
        :param token_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_key_name IotAuthorizer#token_key_name}.
        :param token_signing_public_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_signing_public_keys IotAuthorizer#token_signing_public_keys}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "authorizer_function_arn": authorizer_function_arn,
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
        if enable_caching_for_http is not None:
            self._values["enable_caching_for_http"] = enable_caching_for_http
        if id is not None:
            self._values["id"] = id
        if signing_disabled is not None:
            self._values["signing_disabled"] = signing_disabled
        if status is not None:
            self._values["status"] = status
        if token_key_name is not None:
            self._values["token_key_name"] = token_key_name
        if token_signing_public_keys is not None:
            self._values["token_signing_public_keys"] = token_signing_public_keys

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
    def authorizer_function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#authorizer_function_arn IotAuthorizer#authorizer_function_arn}.'''
        result = self._values.get("authorizer_function_arn")
        assert result is not None, "Required property 'authorizer_function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#name IotAuthorizer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_caching_for_http(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#enable_caching_for_http IotAuthorizer#enable_caching_for_http}.'''
        result = self._values.get("enable_caching_for_http")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#id IotAuthorizer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signing_disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#signing_disabled IotAuthorizer#signing_disabled}.'''
        result = self._values.get("signing_disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#status IotAuthorizer#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_key_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_key_name IotAuthorizer#token_key_name}.'''
        result = self._values.get("token_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_signing_public_keys(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_authorizer#token_signing_public_keys IotAuthorizer#token_signing_public_keys}.'''
        result = self._values.get("token_signing_public_keys")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotAuthorizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotCertificate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate aws_iot_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        active: typing.Union[builtins.bool, cdktf.IResolvable],
        ca_pem: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        csr: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate aws_iot_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#active IotCertificate#active}.
        :param ca_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#ca_pem IotCertificate#ca_pem}.
        :param certificate_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#certificate_pem IotCertificate#certificate_pem}.
        :param csr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#csr IotCertificate#csr}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#id IotCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotCertificateConfig(
            active=active,
            ca_pem=ca_pem,
            certificate_pem=certificate_pem,
            csr=csr,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetCaPem")
    def reset_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPem", []))

    @jsii.member(jsii_name="resetCertificatePem")
    def reset_certificate_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificatePem", []))

    @jsii.member(jsii_name="resetCsr")
    def reset_csr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCsr", []))

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
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeInput")
    def active_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "activeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPemInput")
    def ca_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePemInput")
    def certificate_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csrInput")
    def csr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "csrInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="active")
    def active(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "active"))

    @active.setter
    def active(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "active", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPem")
    def ca_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPem"))

    @ca_pem.setter
    def ca_pem(self, value: builtins.str) -> None:
        jsii.set(self, "caPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificatePem"))

    @certificate_pem.setter
    def certificate_pem(self, value: builtins.str) -> None:
        jsii.set(self, "certificatePem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csr")
    def csr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csr"))

    @csr.setter
    def csr(self, value: builtins.str) -> None:
        jsii.set(self, "csr", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "active": "active",
        "ca_pem": "caPem",
        "certificate_pem": "certificatePem",
        "csr": "csr",
        "id": "id",
    },
)
class IotCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        active: typing.Union[builtins.bool, cdktf.IResolvable],
        ca_pem: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        csr: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param active: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#active IotCertificate#active}.
        :param ca_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#ca_pem IotCertificate#ca_pem}.
        :param certificate_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#certificate_pem IotCertificate#certificate_pem}.
        :param csr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#csr IotCertificate#csr}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#id IotCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "active": active,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ca_pem is not None:
            self._values["ca_pem"] = ca_pem
        if certificate_pem is not None:
            self._values["certificate_pem"] = certificate_pem
        if csr is not None:
            self._values["csr"] = csr
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
    def active(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#active IotCertificate#active}.'''
        result = self._values.get("active")
        assert result is not None, "Required property 'active' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def ca_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#ca_pem IotCertificate#ca_pem}.'''
        result = self._values.get("ca_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#certificate_pem IotCertificate#certificate_pem}.'''
        result = self._values.get("certificate_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def csr(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#csr IotCertificate#csr}.'''
        result = self._values.get("csr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_certificate#id IotCertificate#id}.

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
        return "IotCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotIndexingConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration aws_iot_indexing_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        thing_group_indexing_configuration: typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"] = None,
        thing_indexing_configuration: typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration aws_iot_indexing_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#id IotIndexingConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param thing_group_indexing_configuration: thing_group_indexing_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_configuration IotIndexingConfiguration#thing_group_indexing_configuration}
        :param thing_indexing_configuration: thing_indexing_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_configuration IotIndexingConfiguration#thing_indexing_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotIndexingConfigurationConfig(
            id=id,
            thing_group_indexing_configuration=thing_group_indexing_configuration,
            thing_indexing_configuration=thing_indexing_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putThingGroupIndexingConfiguration")
    def put_thing_group_indexing_configuration(
        self,
        *,
        thing_group_indexing_mode: builtins.str,
        custom_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingGroupIndexingConfigurationCustomField"]]] = None,
        managed_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingGroupIndexingConfigurationManagedField"]]] = None,
    ) -> None:
        '''
        :param thing_group_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_mode IotIndexingConfiguration#thing_group_indexing_mode}.
        :param custom_field: custom_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        :param managed_field: managed_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        '''
        value = IotIndexingConfigurationThingGroupIndexingConfiguration(
            thing_group_indexing_mode=thing_group_indexing_mode,
            custom_field=custom_field,
            managed_field=managed_field,
        )

        return typing.cast(None, jsii.invoke(self, "putThingGroupIndexingConfiguration", [value]))

    @jsii.member(jsii_name="putThingIndexingConfiguration")
    def put_thing_indexing_configuration(
        self,
        *,
        thing_indexing_mode: builtins.str,
        custom_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingIndexingConfigurationCustomField"]]] = None,
        device_defender_indexing_mode: typing.Optional[builtins.str] = None,
        managed_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingIndexingConfigurationManagedField"]]] = None,
        named_shadow_indexing_mode: typing.Optional[builtins.str] = None,
        thing_connectivity_indexing_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param thing_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_mode IotIndexingConfiguration#thing_indexing_mode}.
        :param custom_field: custom_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        :param device_defender_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#device_defender_indexing_mode IotIndexingConfiguration#device_defender_indexing_mode}.
        :param managed_field: managed_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        :param named_shadow_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#named_shadow_indexing_mode IotIndexingConfiguration#named_shadow_indexing_mode}.
        :param thing_connectivity_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_connectivity_indexing_mode IotIndexingConfiguration#thing_connectivity_indexing_mode}.
        '''
        value = IotIndexingConfigurationThingIndexingConfiguration(
            thing_indexing_mode=thing_indexing_mode,
            custom_field=custom_field,
            device_defender_indexing_mode=device_defender_indexing_mode,
            managed_field=managed_field,
            named_shadow_indexing_mode=named_shadow_indexing_mode,
            thing_connectivity_indexing_mode=thing_connectivity_indexing_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putThingIndexingConfiguration", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetThingGroupIndexingConfiguration")
    def reset_thing_group_indexing_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThingGroupIndexingConfiguration", []))

    @jsii.member(jsii_name="resetThingIndexingConfiguration")
    def reset_thing_indexing_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThingIndexingConfiguration", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupIndexingConfiguration")
    def thing_group_indexing_configuration(
        self,
    ) -> "IotIndexingConfigurationThingGroupIndexingConfigurationOutputReference":
        return typing.cast("IotIndexingConfigurationThingGroupIndexingConfigurationOutputReference", jsii.get(self, "thingGroupIndexingConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingIndexingConfiguration")
    def thing_indexing_configuration(
        self,
    ) -> "IotIndexingConfigurationThingIndexingConfigurationOutputReference":
        return typing.cast("IotIndexingConfigurationThingIndexingConfigurationOutputReference", jsii.get(self, "thingIndexingConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupIndexingConfigurationInput")
    def thing_group_indexing_configuration_input(
        self,
    ) -> typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"]:
        return typing.cast(typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"], jsii.get(self, "thingGroupIndexingConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingIndexingConfigurationInput")
    def thing_indexing_configuration_input(
        self,
    ) -> typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"]:
        return typing.cast(typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"], jsii.get(self, "thingIndexingConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "thing_group_indexing_configuration": "thingGroupIndexingConfiguration",
        "thing_indexing_configuration": "thingIndexingConfiguration",
    },
)
class IotIndexingConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: typing.Optional[builtins.str] = None,
        thing_group_indexing_configuration: typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"] = None,
        thing_indexing_configuration: typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#id IotIndexingConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param thing_group_indexing_configuration: thing_group_indexing_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_configuration IotIndexingConfiguration#thing_group_indexing_configuration}
        :param thing_indexing_configuration: thing_indexing_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_configuration IotIndexingConfiguration#thing_indexing_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(thing_group_indexing_configuration, dict):
            thing_group_indexing_configuration = IotIndexingConfigurationThingGroupIndexingConfiguration(**thing_group_indexing_configuration)
        if isinstance(thing_indexing_configuration, dict):
            thing_indexing_configuration = IotIndexingConfigurationThingIndexingConfiguration(**thing_indexing_configuration)
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
        if thing_group_indexing_configuration is not None:
            self._values["thing_group_indexing_configuration"] = thing_group_indexing_configuration
        if thing_indexing_configuration is not None:
            self._values["thing_indexing_configuration"] = thing_indexing_configuration

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#id IotIndexingConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thing_group_indexing_configuration(
        self,
    ) -> typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"]:
        '''thing_group_indexing_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_configuration IotIndexingConfiguration#thing_group_indexing_configuration}
        '''
        result = self._values.get("thing_group_indexing_configuration")
        return typing.cast(typing.Optional["IotIndexingConfigurationThingGroupIndexingConfiguration"], result)

    @builtins.property
    def thing_indexing_configuration(
        self,
    ) -> typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"]:
        '''thing_indexing_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_configuration IotIndexingConfiguration#thing_indexing_configuration}
        '''
        result = self._values.get("thing_indexing_configuration")
        return typing.cast(typing.Optional["IotIndexingConfigurationThingIndexingConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "thing_group_indexing_mode": "thingGroupIndexingMode",
        "custom_field": "customField",
        "managed_field": "managedField",
    },
)
class IotIndexingConfigurationThingGroupIndexingConfiguration:
    def __init__(
        self,
        *,
        thing_group_indexing_mode: builtins.str,
        custom_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingGroupIndexingConfigurationCustomField"]]] = None,
        managed_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingGroupIndexingConfigurationManagedField"]]] = None,
    ) -> None:
        '''
        :param thing_group_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_mode IotIndexingConfiguration#thing_group_indexing_mode}.
        :param custom_field: custom_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        :param managed_field: managed_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "thing_group_indexing_mode": thing_group_indexing_mode,
        }
        if custom_field is not None:
            self._values["custom_field"] = custom_field
        if managed_field is not None:
            self._values["managed_field"] = managed_field

    @builtins.property
    def thing_group_indexing_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_group_indexing_mode IotIndexingConfiguration#thing_group_indexing_mode}.'''
        result = self._values.get("thing_group_indexing_mode")
        assert result is not None, "Required property 'thing_group_indexing_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_field(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingGroupIndexingConfigurationCustomField"]]]:
        '''custom_field block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        '''
        result = self._values.get("custom_field")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingGroupIndexingConfigurationCustomField"]]], result)

    @builtins.property
    def managed_field(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingGroupIndexingConfigurationManagedField"]]]:
        '''managed_field block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        '''
        result = self._values.get("managed_field")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingGroupIndexingConfigurationManagedField"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingGroupIndexingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationCustomField",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class IotIndexingConfigurationThingGroupIndexingConfigurationCustomField:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingGroupIndexingConfigurationCustomField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldList",
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
    ) -> "IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldOutputReference",
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

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    ) -> typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationManagedField",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class IotIndexingConfigurationThingGroupIndexingConfigurationManagedField:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingGroupIndexingConfigurationManagedField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldList",
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
    ) -> "IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldOutputReference",
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

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    ) -> typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingGroupIndexingConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingGroupIndexingConfigurationOutputReference",
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

    @jsii.member(jsii_name="putCustomField")
    def put_custom_field(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCustomField", [value]))

    @jsii.member(jsii_name="putManagedField")
    def put_managed_field(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putManagedField", [value]))

    @jsii.member(jsii_name="resetCustomField")
    def reset_custom_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomField", []))

    @jsii.member(jsii_name="resetManagedField")
    def reset_managed_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedField", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customField")
    def custom_field(
        self,
    ) -> IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldList:
        return typing.cast(IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldList, jsii.get(self, "customField"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedField")
    def managed_field(
        self,
    ) -> IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldList:
        return typing.cast(IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldList, jsii.get(self, "managedField"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customFieldInput")
    def custom_field_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationCustomField]]], jsii.get(self, "customFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedFieldInput")
    def managed_field_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingGroupIndexingConfigurationManagedField]]], jsii.get(self, "managedFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupIndexingModeInput")
    def thing_group_indexing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingGroupIndexingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupIndexingMode")
    def thing_group_indexing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingGroupIndexingMode"))

    @thing_group_indexing_mode.setter
    def thing_group_indexing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "thingGroupIndexingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotIndexingConfigurationThingGroupIndexingConfiguration]:
        return typing.cast(typing.Optional[IotIndexingConfigurationThingGroupIndexingConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotIndexingConfigurationThingGroupIndexingConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "thing_indexing_mode": "thingIndexingMode",
        "custom_field": "customField",
        "device_defender_indexing_mode": "deviceDefenderIndexingMode",
        "managed_field": "managedField",
        "named_shadow_indexing_mode": "namedShadowIndexingMode",
        "thing_connectivity_indexing_mode": "thingConnectivityIndexingMode",
    },
)
class IotIndexingConfigurationThingIndexingConfiguration:
    def __init__(
        self,
        *,
        thing_indexing_mode: builtins.str,
        custom_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingIndexingConfigurationCustomField"]]] = None,
        device_defender_indexing_mode: typing.Optional[builtins.str] = None,
        managed_field: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotIndexingConfigurationThingIndexingConfigurationManagedField"]]] = None,
        named_shadow_indexing_mode: typing.Optional[builtins.str] = None,
        thing_connectivity_indexing_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param thing_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_mode IotIndexingConfiguration#thing_indexing_mode}.
        :param custom_field: custom_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        :param device_defender_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#device_defender_indexing_mode IotIndexingConfiguration#device_defender_indexing_mode}.
        :param managed_field: managed_field block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        :param named_shadow_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#named_shadow_indexing_mode IotIndexingConfiguration#named_shadow_indexing_mode}.
        :param thing_connectivity_indexing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_connectivity_indexing_mode IotIndexingConfiguration#thing_connectivity_indexing_mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "thing_indexing_mode": thing_indexing_mode,
        }
        if custom_field is not None:
            self._values["custom_field"] = custom_field
        if device_defender_indexing_mode is not None:
            self._values["device_defender_indexing_mode"] = device_defender_indexing_mode
        if managed_field is not None:
            self._values["managed_field"] = managed_field
        if named_shadow_indexing_mode is not None:
            self._values["named_shadow_indexing_mode"] = named_shadow_indexing_mode
        if thing_connectivity_indexing_mode is not None:
            self._values["thing_connectivity_indexing_mode"] = thing_connectivity_indexing_mode

    @builtins.property
    def thing_indexing_mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_indexing_mode IotIndexingConfiguration#thing_indexing_mode}.'''
        result = self._values.get("thing_indexing_mode")
        assert result is not None, "Required property 'thing_indexing_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_field(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingIndexingConfigurationCustomField"]]]:
        '''custom_field block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#custom_field IotIndexingConfiguration#custom_field}
        '''
        result = self._values.get("custom_field")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingIndexingConfigurationCustomField"]]], result)

    @builtins.property
    def device_defender_indexing_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#device_defender_indexing_mode IotIndexingConfiguration#device_defender_indexing_mode}.'''
        result = self._values.get("device_defender_indexing_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_field(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingIndexingConfigurationManagedField"]]]:
        '''managed_field block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#managed_field IotIndexingConfiguration#managed_field}
        '''
        result = self._values.get("managed_field")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotIndexingConfigurationThingIndexingConfigurationManagedField"]]], result)

    @builtins.property
    def named_shadow_indexing_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#named_shadow_indexing_mode IotIndexingConfiguration#named_shadow_indexing_mode}.'''
        result = self._values.get("named_shadow_indexing_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thing_connectivity_indexing_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#thing_connectivity_indexing_mode IotIndexingConfiguration#thing_connectivity_indexing_mode}.'''
        result = self._values.get("thing_connectivity_indexing_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingIndexingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationCustomField",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class IotIndexingConfigurationThingIndexingConfigurationCustomField:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingIndexingConfigurationCustomField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotIndexingConfigurationThingIndexingConfigurationCustomFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationCustomFieldList",
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
    ) -> "IotIndexingConfigurationThingIndexingConfigurationCustomFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotIndexingConfigurationThingIndexingConfigurationCustomFieldOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationCustomField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationCustomField]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationCustomField]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingIndexingConfigurationCustomFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationCustomFieldOutputReference",
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

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    ) -> typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationCustomField, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationCustomField, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationCustomField, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationManagedField",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class IotIndexingConfigurationThingIndexingConfigurationManagedField:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#name IotIndexingConfiguration#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_indexing_configuration#type IotIndexingConfiguration#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotIndexingConfigurationThingIndexingConfigurationManagedField(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotIndexingConfigurationThingIndexingConfigurationManagedFieldList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationManagedFieldList",
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
    ) -> "IotIndexingConfigurationThingIndexingConfigurationManagedFieldOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotIndexingConfigurationThingIndexingConfigurationManagedFieldOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationManagedField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationManagedField]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationManagedField]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingIndexingConfigurationManagedFieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationManagedFieldOutputReference",
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

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    ) -> typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationManagedField, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationManagedField, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotIndexingConfigurationThingIndexingConfigurationManagedField, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotIndexingConfigurationThingIndexingConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotIndexingConfigurationThingIndexingConfigurationOutputReference",
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

    @jsii.member(jsii_name="putCustomField")
    def put_custom_field(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotIndexingConfigurationThingIndexingConfigurationCustomField]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCustomField", [value]))

    @jsii.member(jsii_name="putManagedField")
    def put_managed_field(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotIndexingConfigurationThingIndexingConfigurationManagedField]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putManagedField", [value]))

    @jsii.member(jsii_name="resetCustomField")
    def reset_custom_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomField", []))

    @jsii.member(jsii_name="resetDeviceDefenderIndexingMode")
    def reset_device_defender_indexing_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceDefenderIndexingMode", []))

    @jsii.member(jsii_name="resetManagedField")
    def reset_managed_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedField", []))

    @jsii.member(jsii_name="resetNamedShadowIndexingMode")
    def reset_named_shadow_indexing_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamedShadowIndexingMode", []))

    @jsii.member(jsii_name="resetThingConnectivityIndexingMode")
    def reset_thing_connectivity_indexing_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThingConnectivityIndexingMode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customField")
    def custom_field(
        self,
    ) -> IotIndexingConfigurationThingIndexingConfigurationCustomFieldList:
        return typing.cast(IotIndexingConfigurationThingIndexingConfigurationCustomFieldList, jsii.get(self, "customField"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedField")
    def managed_field(
        self,
    ) -> IotIndexingConfigurationThingIndexingConfigurationManagedFieldList:
        return typing.cast(IotIndexingConfigurationThingIndexingConfigurationManagedFieldList, jsii.get(self, "managedField"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customFieldInput")
    def custom_field_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationCustomField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationCustomField]]], jsii.get(self, "customFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceDefenderIndexingModeInput")
    def device_defender_indexing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceDefenderIndexingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedFieldInput")
    def managed_field_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationManagedField]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotIndexingConfigurationThingIndexingConfigurationManagedField]]], jsii.get(self, "managedFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namedShadowIndexingModeInput")
    def named_shadow_indexing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namedShadowIndexingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingConnectivityIndexingModeInput")
    def thing_connectivity_indexing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingConnectivityIndexingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingIndexingModeInput")
    def thing_indexing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingIndexingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceDefenderIndexingMode")
    def device_defender_indexing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceDefenderIndexingMode"))

    @device_defender_indexing_mode.setter
    def device_defender_indexing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "deviceDefenderIndexingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namedShadowIndexingMode")
    def named_shadow_indexing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namedShadowIndexingMode"))

    @named_shadow_indexing_mode.setter
    def named_shadow_indexing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "namedShadowIndexingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingConnectivityIndexingMode")
    def thing_connectivity_indexing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingConnectivityIndexingMode"))

    @thing_connectivity_indexing_mode.setter
    def thing_connectivity_indexing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "thingConnectivityIndexingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingIndexingMode")
    def thing_indexing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingIndexingMode"))

    @thing_indexing_mode.setter
    def thing_indexing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "thingIndexingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotIndexingConfigurationThingIndexingConfiguration]:
        return typing.cast(typing.Optional[IotIndexingConfigurationThingIndexingConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotIndexingConfigurationThingIndexingConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotLoggingOptions(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotLoggingOptions",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options aws_iot_logging_options}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        default_log_level: builtins.str,
        role_arn: builtins.str,
        disable_all_logs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options aws_iot_logging_options} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#default_log_level IotLoggingOptions#default_log_level}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#role_arn IotLoggingOptions#role_arn}.
        :param disable_all_logs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#disable_all_logs IotLoggingOptions#disable_all_logs}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#id IotLoggingOptions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotLoggingOptionsConfig(
            default_log_level=default_log_level,
            role_arn=role_arn,
            disable_all_logs=disable_all_logs,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetDisableAllLogs")
    def reset_disable_all_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAllLogs", []))

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
    @jsii.member(jsii_name="defaultLogLevelInput")
    def default_log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultLogLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableAllLogsInput")
    def disable_all_logs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableAllLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultLogLevel")
    def default_log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultLogLevel"))

    @default_log_level.setter
    def default_log_level(self, value: builtins.str) -> None:
        jsii.set(self, "defaultLogLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableAllLogs")
    def disable_all_logs(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableAllLogs"))

    @disable_all_logs.setter
    def disable_all_logs(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "disableAllLogs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotLoggingOptionsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "default_log_level": "defaultLogLevel",
        "role_arn": "roleArn",
        "disable_all_logs": "disableAllLogs",
        "id": "id",
    },
)
class IotLoggingOptionsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        default_log_level: builtins.str,
        role_arn: builtins.str,
        disable_all_logs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param default_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#default_log_level IotLoggingOptions#default_log_level}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#role_arn IotLoggingOptions#role_arn}.
        :param disable_all_logs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#disable_all_logs IotLoggingOptions#disable_all_logs}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#id IotLoggingOptions#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "default_log_level": default_log_level,
            "role_arn": role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if disable_all_logs is not None:
            self._values["disable_all_logs"] = disable_all_logs
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
    def default_log_level(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#default_log_level IotLoggingOptions#default_log_level}.'''
        result = self._values.get("default_log_level")
        assert result is not None, "Required property 'default_log_level' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#role_arn IotLoggingOptions#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disable_all_logs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#disable_all_logs IotLoggingOptions#disable_all_logs}.'''
        result = self._values.get("disable_all_logs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_logging_options#id IotLoggingOptions#id}.

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
        return "IotLoggingOptionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_policy aws_iot_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        policy: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_policy aws_iot_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#name IotPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#policy IotPolicy#policy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#id IotPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotPolicyConfig(
            name=name,
            policy=policy,
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
    @jsii.member(jsii_name="defaultVersionId")
    def default_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

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
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


class IotPolicyAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotPolicyAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment aws_iot_policy_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        policy: builtins.str,
        target: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment aws_iot_policy_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#policy IotPolicyAttachment#policy}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#target IotPolicyAttachment#target}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#id IotPolicyAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotPolicyAttachmentConfig(
            policy=policy,
            target=target,
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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotPolicyAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "target": "target",
        "id": "id",
    },
)
class IotPolicyAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        target: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#policy IotPolicyAttachment#policy}.
        :param target: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#target IotPolicyAttachment#target}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#id IotPolicyAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "target": target,
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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#policy IotPolicyAttachment#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#target IotPolicyAttachment#target}.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy_attachment#id IotPolicyAttachment#id}.

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
        return "IotPolicyAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "policy": "policy",
        "id": "id",
    },
)
class IotPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        policy: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#name IotPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#policy IotPolicy#policy}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#id IotPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "policy": policy,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#name IotPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#policy IotPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_policy#id IotPolicy#id}.

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
        return "IotPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotProvisioningTemplate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotProvisioningTemplate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template aws_iot_provisioning_template}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        provisioning_role_arn: builtins.str,
        template_body: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        pre_provisioning_hook: typing.Optional["IotProvisioningTemplatePreProvisioningHook"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template aws_iot_provisioning_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#name IotProvisioningTemplate#name}.
        :param provisioning_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#provisioning_role_arn IotProvisioningTemplate#provisioning_role_arn}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#template_body IotProvisioningTemplate#template_body}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#description IotProvisioningTemplate#description}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#enabled IotProvisioningTemplate#enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#id IotProvisioningTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pre_provisioning_hook: pre_provisioning_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#pre_provisioning_hook IotProvisioningTemplate#pre_provisioning_hook}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags IotProvisioningTemplate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags_all IotProvisioningTemplate#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotProvisioningTemplateConfig(
            name=name,
            provisioning_role_arn=provisioning_role_arn,
            template_body=template_body,
            description=description,
            enabled=enabled,
            id=id,
            pre_provisioning_hook=pre_provisioning_hook,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putPreProvisioningHook")
    def put_pre_provisioning_hook(
        self,
        *,
        target_arn: builtins.str,
        payload_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#target_arn IotProvisioningTemplate#target_arn}.
        :param payload_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#payload_version IotProvisioningTemplate#payload_version}.
        '''
        value = IotProvisioningTemplatePreProvisioningHook(
            target_arn=target_arn, payload_version=payload_version
        )

        return typing.cast(None, jsii.invoke(self, "putPreProvisioningHook", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPreProvisioningHook")
    def reset_pre_provisioning_hook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreProvisioningHook", []))

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
    @jsii.member(jsii_name="defaultVersionId")
    def default_version_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preProvisioningHook")
    def pre_provisioning_hook(
        self,
    ) -> "IotProvisioningTemplatePreProvisioningHookOutputReference":
        return typing.cast("IotProvisioningTemplatePreProvisioningHookOutputReference", jsii.get(self, "preProvisioningHook"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preProvisioningHookInput")
    def pre_provisioning_hook_input(
        self,
    ) -> typing.Optional["IotProvisioningTemplatePreProvisioningHook"]:
        return typing.cast(typing.Optional["IotProvisioningTemplatePreProvisioningHook"], jsii.get(self, "preProvisioningHookInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisioningRoleArnInput")
    def provisioning_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provisioningRoleArnInput"))

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
    @jsii.member(jsii_name="templateBodyInput")
    def template_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

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
    @jsii.member(jsii_name="provisioningRoleArn")
    def provisioning_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningRoleArn"))

    @provisioning_role_arn.setter
    def provisioning_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "provisioningRoleArn", value)

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
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        jsii.set(self, "templateBody", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotProvisioningTemplateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "provisioning_role_arn": "provisioningRoleArn",
        "template_body": "templateBody",
        "description": "description",
        "enabled": "enabled",
        "id": "id",
        "pre_provisioning_hook": "preProvisioningHook",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IotProvisioningTemplateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        provisioning_role_arn: builtins.str,
        template_body: builtins.str,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        pre_provisioning_hook: typing.Optional["IotProvisioningTemplatePreProvisioningHook"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#name IotProvisioningTemplate#name}.
        :param provisioning_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#provisioning_role_arn IotProvisioningTemplate#provisioning_role_arn}.
        :param template_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#template_body IotProvisioningTemplate#template_body}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#description IotProvisioningTemplate#description}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#enabled IotProvisioningTemplate#enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#id IotProvisioningTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pre_provisioning_hook: pre_provisioning_hook block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#pre_provisioning_hook IotProvisioningTemplate#pre_provisioning_hook}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags IotProvisioningTemplate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags_all IotProvisioningTemplate#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(pre_provisioning_hook, dict):
            pre_provisioning_hook = IotProvisioningTemplatePreProvisioningHook(**pre_provisioning_hook)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "provisioning_role_arn": provisioning_role_arn,
            "template_body": template_body,
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
        if enabled is not None:
            self._values["enabled"] = enabled
        if id is not None:
            self._values["id"] = id
        if pre_provisioning_hook is not None:
            self._values["pre_provisioning_hook"] = pre_provisioning_hook
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#name IotProvisioningTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provisioning_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#provisioning_role_arn IotProvisioningTemplate#provisioning_role_arn}.'''
        result = self._values.get("provisioning_role_arn")
        assert result is not None, "Required property 'provisioning_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#template_body IotProvisioningTemplate#template_body}.'''
        result = self._values.get("template_body")
        assert result is not None, "Required property 'template_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#description IotProvisioningTemplate#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#enabled IotProvisioningTemplate#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#id IotProvisioningTemplate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_provisioning_hook(
        self,
    ) -> typing.Optional["IotProvisioningTemplatePreProvisioningHook"]:
        '''pre_provisioning_hook block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#pre_provisioning_hook IotProvisioningTemplate#pre_provisioning_hook}
        '''
        result = self._values.get("pre_provisioning_hook")
        return typing.cast(typing.Optional["IotProvisioningTemplatePreProvisioningHook"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags IotProvisioningTemplate#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#tags_all IotProvisioningTemplate#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotProvisioningTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotProvisioningTemplatePreProvisioningHook",
    jsii_struct_bases=[],
    name_mapping={"target_arn": "targetArn", "payload_version": "payloadVersion"},
)
class IotProvisioningTemplatePreProvisioningHook:
    def __init__(
        self,
        *,
        target_arn: builtins.str,
        payload_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#target_arn IotProvisioningTemplate#target_arn}.
        :param payload_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#payload_version IotProvisioningTemplate#payload_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_arn": target_arn,
        }
        if payload_version is not None:
            self._values["payload_version"] = payload_version

    @builtins.property
    def target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#target_arn IotProvisioningTemplate#target_arn}.'''
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def payload_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_provisioning_template#payload_version IotProvisioningTemplate#payload_version}.'''
        result = self._values.get("payload_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotProvisioningTemplatePreProvisioningHook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotProvisioningTemplatePreProvisioningHookOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotProvisioningTemplatePreProvisioningHookOutputReference",
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

    @jsii.member(jsii_name="resetPayloadVersion")
    def reset_payload_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadVersionInput")
    def payload_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArnInput")
    def target_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadVersion")
    def payload_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadVersion"))

    @payload_version.setter
    def payload_version(self, value: builtins.str) -> None:
        jsii.set(self, "payloadVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @target_arn.setter
    def target_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotProvisioningTemplatePreProvisioningHook]:
        return typing.cast(typing.Optional[IotProvisioningTemplatePreProvisioningHook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotProvisioningTemplatePreProvisioningHook],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotRoleAlias(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotRoleAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias aws_iot_role_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        alias: builtins.str,
        role_arn: builtins.str,
        credential_duration: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias aws_iot_role_alias} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#alias IotRoleAlias#alias}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#role_arn IotRoleAlias#role_arn}.
        :param credential_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#credential_duration IotRoleAlias#credential_duration}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#id IotRoleAlias#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotRoleAliasConfig(
            alias=alias,
            role_arn=role_arn,
            credential_duration=credential_duration,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetCredentialDuration")
    def reset_credential_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialDuration", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialDurationInput")
    def credential_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "credentialDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialDuration")
    def credential_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "credentialDuration"))

    @credential_duration.setter
    def credential_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "credentialDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotRoleAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alias": "alias",
        "role_arn": "roleArn",
        "credential_duration": "credentialDuration",
        "id": "id",
    },
)
class IotRoleAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alias: builtins.str,
        role_arn: builtins.str,
        credential_duration: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#alias IotRoleAlias#alias}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#role_arn IotRoleAlias#role_arn}.
        :param credential_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#credential_duration IotRoleAlias#credential_duration}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#id IotRoleAlias#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "alias": alias,
            "role_arn": role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if credential_duration is not None:
            self._values["credential_duration"] = credential_duration
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
    def alias(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#alias IotRoleAlias#alias}.'''
        result = self._values.get("alias")
        assert result is not None, "Required property 'alias' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#role_arn IotRoleAlias#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def credential_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#credential_duration IotRoleAlias#credential_duration}.'''
        result = self._values.get("credential_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_role_alias#id IotRoleAlias#id}.

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
        return "IotRoleAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThing(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThing",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_thing aws_iot_thing}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        thing_type_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_thing aws_iot_thing} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#name IotThing#name}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#attributes IotThing#attributes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#id IotThing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param thing_type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#thing_type_name IotThing#thing_type_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotThingConfig(
            name=name,
            attributes=attributes,
            id=id,
            thing_type_name=thing_type_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAttributes")
    def reset_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetThingTypeName")
    def reset_thing_type_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThingTypeName", []))

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
    @jsii.member(jsii_name="defaultClientId")
    def default_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultClientId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingTypeNameInput")
    def thing_type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingTypeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "attributes", value)

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
    @jsii.member(jsii_name="thingTypeName")
    def thing_type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingTypeName"))

    @thing_type_name.setter
    def thing_type_name(self, value: builtins.str) -> None:
        jsii.set(self, "thingTypeName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "attributes": "attributes",
        "id": "id",
        "thing_type_name": "thingTypeName",
    },
)
class IotThingConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        thing_type_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#name IotThing#name}.
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#attributes IotThing#attributes}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#id IotThing#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param thing_type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#thing_type_name IotThing#thing_type_name}.
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
        if attributes is not None:
            self._values["attributes"] = attributes
        if id is not None:
            self._values["id"] = id
        if thing_type_name is not None:
            self._values["thing_type_name"] = thing_type_name

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#name IotThing#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attributes(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#attributes IotThing#attributes}.'''
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#id IotThing#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thing_type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing#thing_type_name IotThing#thing_type_name}.'''
        result = self._values.get("thing_type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group aws_iot_thing_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        parent_group_name: typing.Optional[builtins.str] = None,
        properties: typing.Optional["IotThingGroupProperties"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group aws_iot_thing_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#name IotThingGroup#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#id IotThingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parent_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#parent_group_name IotThingGroup#parent_group_name}.
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#properties IotThingGroup#properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags IotThingGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags_all IotThingGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotThingGroupConfig(
            name=name,
            id=id,
            parent_group_name=parent_group_name,
            properties=properties,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        attribute_payload: typing.Optional["IotThingGroupPropertiesAttributePayload"] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attribute_payload: attribute_payload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attribute_payload IotThingGroup#attribute_payload}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#description IotThingGroup#description}.
        '''
        value = IotThingGroupProperties(
            attribute_payload=attribute_payload, description=description
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetParentGroupName")
    def reset_parent_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentGroupName", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

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
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> "IotThingGroupMetadataList":
        return typing.cast("IotThingGroupMetadataList", jsii.get(self, "metadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="properties")
    def properties(self) -> "IotThingGroupPropertiesOutputReference":
        return typing.cast("IotThingGroupPropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentGroupNameInput")
    def parent_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional["IotThingGroupProperties"]:
        return typing.cast(typing.Optional["IotThingGroupProperties"], jsii.get(self, "propertiesInput"))

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
    @jsii.member(jsii_name="parentGroupName")
    def parent_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentGroupName"))

    @parent_group_name.setter
    def parent_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parentGroupName", value)

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
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
        "parent_group_name": "parentGroupName",
        "properties": "properties",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IotThingGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        parent_group_name: typing.Optional[builtins.str] = None,
        properties: typing.Optional["IotThingGroupProperties"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#name IotThingGroup#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#id IotThingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param parent_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#parent_group_name IotThingGroup#parent_group_name}.
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#properties IotThingGroup#properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags IotThingGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags_all IotThingGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = IotThingGroupProperties(**properties)
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
        if parent_group_name is not None:
            self._values["parent_group_name"] = parent_group_name
        if properties is not None:
            self._values["properties"] = properties
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#name IotThingGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#id IotThingGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#parent_group_name IotThingGroup#parent_group_name}.'''
        result = self._values.get("parent_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional["IotThingGroupProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#properties IotThingGroup#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["IotThingGroupProperties"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags IotThingGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#tags_all IotThingGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingGroupMembership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership aws_iot_thing_group_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        thing_group_name: builtins.str,
        thing_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        override_dynamic_group: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership aws_iot_thing_group_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param thing_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_group_name IotThingGroupMembership#thing_group_name}.
        :param thing_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_name IotThingGroupMembership#thing_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#id IotThingGroupMembership#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param override_dynamic_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#override_dynamic_group IotThingGroupMembership#override_dynamic_group}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotThingGroupMembershipConfig(
            thing_group_name=thing_group_name,
            thing_name=thing_name,
            id=id,
            override_dynamic_group=override_dynamic_group,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOverrideDynamicGroup")
    def reset_override_dynamic_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideDynamicGroup", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideDynamicGroupInput")
    def override_dynamic_group_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideDynamicGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupNameInput")
    def thing_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingNameInput")
    def thing_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideDynamicGroup")
    def override_dynamic_group(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "overrideDynamicGroup"))

    @override_dynamic_group.setter
    def override_dynamic_group(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "overrideDynamicGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingGroupName")
    def thing_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingGroupName"))

    @thing_group_name.setter
    def thing_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "thingGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thingName"))

    @thing_name.setter
    def thing_name(self, value: builtins.str) -> None:
        jsii.set(self, "thingName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "thing_group_name": "thingGroupName",
        "thing_name": "thingName",
        "id": "id",
        "override_dynamic_group": "overrideDynamicGroup",
    },
)
class IotThingGroupMembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        thing_group_name: builtins.str,
        thing_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        override_dynamic_group: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param thing_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_group_name IotThingGroupMembership#thing_group_name}.
        :param thing_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_name IotThingGroupMembership#thing_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#id IotThingGroupMembership#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param override_dynamic_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#override_dynamic_group IotThingGroupMembership#override_dynamic_group}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "thing_group_name": thing_group_name,
            "thing_name": thing_name,
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
        if override_dynamic_group is not None:
            self._values["override_dynamic_group"] = override_dynamic_group

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
    def thing_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_group_name IotThingGroupMembership#thing_group_name}.'''
        result = self._values.get("thing_group_name")
        assert result is not None, "Required property 'thing_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def thing_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#thing_name IotThingGroupMembership#thing_name}.'''
        result = self._values.get("thing_name")
        assert result is not None, "Required property 'thing_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#id IotThingGroupMembership#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def override_dynamic_group(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group_membership#override_dynamic_group IotThingGroupMembership#override_dynamic_group}.'''
        result = self._values.get("override_dynamic_group")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadata",
    jsii_struct_bases=[],
    name_mapping={},
)
class IotThingGroupMetadata:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingGroupMetadataList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadataList",
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
    def get(self, index: jsii.Number) -> "IotThingGroupMetadataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotThingGroupMetadataOutputReference", jsii.invoke(self, "get", [index]))

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


class IotThingGroupMetadataOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadataOutputReference",
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
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentGroupName")
    def parent_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootToParentGroups")
    def root_to_parent_groups(self) -> "IotThingGroupMetadataRootToParentGroupsList":
        return typing.cast("IotThingGroupMetadataRootToParentGroupsList", jsii.get(self, "rootToParentGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotThingGroupMetadata]:
        return typing.cast(typing.Optional[IotThingGroupMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[IotThingGroupMetadata]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadataRootToParentGroups",
    jsii_struct_bases=[],
    name_mapping={},
)
class IotThingGroupMetadataRootToParentGroups:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupMetadataRootToParentGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingGroupMetadataRootToParentGroupsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadataRootToParentGroupsList",
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
    ) -> "IotThingGroupMetadataRootToParentGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotThingGroupMetadataRootToParentGroupsOutputReference", jsii.invoke(self, "get", [index]))

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


class IotThingGroupMetadataRootToParentGroupsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupMetadataRootToParentGroupsOutputReference",
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
    @jsii.member(jsii_name="groupArn")
    def group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotThingGroupMetadataRootToParentGroups]:
        return typing.cast(typing.Optional[IotThingGroupMetadataRootToParentGroups], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotThingGroupMetadataRootToParentGroups],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupProperties",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_payload": "attributePayload",
        "description": "description",
    },
)
class IotThingGroupProperties:
    def __init__(
        self,
        *,
        attribute_payload: typing.Optional["IotThingGroupPropertiesAttributePayload"] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attribute_payload: attribute_payload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attribute_payload IotThingGroup#attribute_payload}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#description IotThingGroup#description}.
        '''
        if isinstance(attribute_payload, dict):
            attribute_payload = IotThingGroupPropertiesAttributePayload(**attribute_payload)
        self._values: typing.Dict[str, typing.Any] = {}
        if attribute_payload is not None:
            self._values["attribute_payload"] = attribute_payload
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def attribute_payload(
        self,
    ) -> typing.Optional["IotThingGroupPropertiesAttributePayload"]:
        '''attribute_payload block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attribute_payload IotThingGroup#attribute_payload}
        '''
        result = self._values.get("attribute_payload")
        return typing.cast(typing.Optional["IotThingGroupPropertiesAttributePayload"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#description IotThingGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupPropertiesAttributePayload",
    jsii_struct_bases=[],
    name_mapping={"attributes": "attributes"},
)
class IotThingGroupPropertiesAttributePayload:
    def __init__(
        self,
        *,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attributes IotThingGroup#attributes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if attributes is not None:
            self._values["attributes"] = attributes

    @builtins.property
    def attributes(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attributes IotThingGroup#attributes}.'''
        result = self._values.get("attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingGroupPropertiesAttributePayload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingGroupPropertiesAttributePayloadOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupPropertiesAttributePayloadOutputReference",
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

    @jsii.member(jsii_name="resetAttributes")
    def reset_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributesInput")
    def attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "attributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributes")
    def attributes(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "attributes"))

    @attributes.setter
    def attributes(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "attributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotThingGroupPropertiesAttributePayload]:
        return typing.cast(typing.Optional[IotThingGroupPropertiesAttributePayload], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotThingGroupPropertiesAttributePayload],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotThingGroupPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingGroupPropertiesOutputReference",
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

    @jsii.member(jsii_name="putAttributePayload")
    def put_attribute_payload(
        self,
        *,
        attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_group#attributes IotThingGroup#attributes}.
        '''
        value = IotThingGroupPropertiesAttributePayload(attributes=attributes)

        return typing.cast(None, jsii.invoke(self, "putAttributePayload", [value]))

    @jsii.member(jsii_name="resetAttributePayload")
    def reset_attribute_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttributePayload", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributePayload")
    def attribute_payload(
        self,
    ) -> IotThingGroupPropertiesAttributePayloadOutputReference:
        return typing.cast(IotThingGroupPropertiesAttributePayloadOutputReference, jsii.get(self, "attributePayload"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributePayloadInput")
    def attribute_payload_input(
        self,
    ) -> typing.Optional[IotThingGroupPropertiesAttributePayload]:
        return typing.cast(typing.Optional[IotThingGroupPropertiesAttributePayload], jsii.get(self, "attributePayloadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotThingGroupProperties]:
        return typing.cast(typing.Optional[IotThingGroupProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[IotThingGroupProperties]) -> None:
        jsii.set(self, "internalValue", value)


class IotThingPrincipalAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingPrincipalAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment aws_iot_thing_principal_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        principal: builtins.str,
        thing: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment aws_iot_thing_principal_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#principal IotThingPrincipalAttachment#principal}.
        :param thing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#thing IotThingPrincipalAttachment#thing}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#id IotThingPrincipalAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotThingPrincipalAttachmentConfig(
            principal=principal,
            thing=thing,
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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalInput")
    def principal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingInput")
    def thing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingInput"))

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
    @jsii.member(jsii_name="thing")
    def thing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thing"))

    @thing.setter
    def thing(self, value: builtins.str) -> None:
        jsii.set(self, "thing", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingPrincipalAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "principal": "principal",
        "thing": "thing",
        "id": "id",
    },
)
class IotThingPrincipalAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        principal: builtins.str,
        thing: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param principal: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#principal IotThingPrincipalAttachment#principal}.
        :param thing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#thing IotThingPrincipalAttachment#thing}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#id IotThingPrincipalAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "principal": principal,
            "thing": thing,
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
    def principal(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#principal IotThingPrincipalAttachment#principal}.'''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def thing(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#thing IotThingPrincipalAttachment#thing}.'''
        result = self._values.get("thing")
        assert result is not None, "Required property 'thing' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_principal_attachment#id IotThingPrincipalAttachment#id}.

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
        return "IotThingPrincipalAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingType(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingType",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type aws_iot_thing_type}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        deprecated: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        properties: typing.Optional["IotThingTypeProperties"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type aws_iot_thing_type} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#name IotThingType#name}.
        :param deprecated: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#deprecated IotThingType#deprecated}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#id IotThingType#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#properties IotThingType#properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags IotThingType#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags_all IotThingType#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotThingTypeConfig(
            name=name,
            deprecated=deprecated,
            id=id,
            properties=properties,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putProperties")
    def put_properties(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        searchable_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#description IotThingType#description}.
        :param searchable_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#searchable_attributes IotThingType#searchable_attributes}.
        '''
        value = IotThingTypeProperties(
            description=description, searchable_attributes=searchable_attributes
        )

        return typing.cast(None, jsii.invoke(self, "putProperties", [value]))

    @jsii.member(jsii_name="resetDeprecated")
    def reset_deprecated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecated", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

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
    @jsii.member(jsii_name="properties")
    def properties(self) -> "IotThingTypePropertiesOutputReference":
        return typing.cast("IotThingTypePropertiesOutputReference", jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deprecatedInput")
    def deprecated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deprecatedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(self) -> typing.Optional["IotThingTypeProperties"]:
        return typing.cast(typing.Optional["IotThingTypeProperties"], jsii.get(self, "propertiesInput"))

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
    @jsii.member(jsii_name="deprecated")
    def deprecated(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deprecated"))

    @deprecated.setter
    def deprecated(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "deprecated", value)

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
    jsii_type="@cdktf/provider-aws.iot.IotThingTypeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "deprecated": "deprecated",
        "id": "id",
        "properties": "properties",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IotThingTypeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        deprecated: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        properties: typing.Optional["IotThingTypeProperties"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#name IotThingType#name}.
        :param deprecated: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#deprecated IotThingType#deprecated}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#id IotThingType#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param properties: properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#properties IotThingType#properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags IotThingType#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags_all IotThingType#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(properties, dict):
            properties = IotThingTypeProperties(**properties)
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
        if deprecated is not None:
            self._values["deprecated"] = deprecated
        if id is not None:
            self._values["id"] = id
        if properties is not None:
            self._values["properties"] = properties
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#name IotThingType#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deprecated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#deprecated IotThingType#deprecated}.'''
        result = self._values.get("deprecated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#id IotThingType#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Optional["IotThingTypeProperties"]:
        '''properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#properties IotThingType#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["IotThingTypeProperties"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags IotThingType#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#tags_all IotThingType#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotThingTypeProperties",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "searchable_attributes": "searchableAttributes",
    },
)
class IotThingTypeProperties:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        searchable_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#description IotThingType#description}.
        :param searchable_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#searchable_attributes IotThingType#searchable_attributes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if searchable_attributes is not None:
            self._values["searchable_attributes"] = searchable_attributes

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#description IotThingType#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def searchable_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_thing_type#searchable_attributes IotThingType#searchable_attributes}.'''
        result = self._values.get("searchable_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotThingTypeProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotThingTypePropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotThingTypePropertiesOutputReference",
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

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetSearchableAttributes")
    def reset_searchable_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchableAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="searchableAttributesInput")
    def searchable_attributes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "searchableAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="searchableAttributes")
    def searchable_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "searchableAttributes"))

    @searchable_attributes.setter
    def searchable_attributes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "searchableAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotThingTypeProperties]:
        return typing.cast(typing.Optional[IotThingTypeProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[IotThingTypeProperties]) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule aws_iot_topic_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        sql: builtins.str,
        sql_version: builtins.str,
        cloudwatch_alarm: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchAlarm"]]] = None,
        cloudwatch_logs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchLogs"]]] = None,
        cloudwatch_metric: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchMetric"]]] = None,
        description: typing.Optional[builtins.str] = None,
        dynamodb: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodb"]]] = None,
        dynamodbv2: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodbv2"]]] = None,
        elasticsearch: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleElasticsearch"]]] = None,
        error_action: typing.Optional["IotTopicRuleErrorAction"] = None,
        firehose: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleFirehose"]]] = None,
        http: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleHttp"]]] = None,
        id: typing.Optional[builtins.str] = None,
        iot_analytics: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotAnalytics"]]] = None,
        iot_events: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotEvents"]]] = None,
        kafka: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKafka"]]] = None,
        kinesis: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKinesis"]]] = None,
        lambda_: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleLambda"]]] = None,
        republish: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleRepublish"]]] = None,
        s3: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleS3"]]] = None,
        sns: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSns"]]] = None,
        sqs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSqs"]]] = None,
        step_functions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleStepFunctions"]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timestream: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleTimestream"]]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule aws_iot_topic_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#enabled IotTopicRule#enabled}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.
        :param sql: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql IotTopicRule#sql}.
        :param sql_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql_version IotTopicRule#sql_version}.
        :param cloudwatch_alarm: cloudwatch_alarm block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        :param cloudwatch_metric: cloudwatch_metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#description IotTopicRule#description}.
        :param dynamodb: dynamodb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        :param dynamodbv2: dynamodbv2 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        :param error_action: error_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#error_action IotTopicRule#error_action}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        :param http: http block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param iot_analytics: iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        :param iot_events: iot_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        :param kafka: kafka block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        :param kinesis: kinesis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        :param lambda_: lambda block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        :param republish: republish block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        :param sns: sns block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        :param sqs: sqs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        :param step_functions: step_functions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags IotTopicRule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags_all IotTopicRule#tags_all}.
        :param timestream: timestream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotTopicRuleConfig(
            enabled=enabled,
            name=name,
            sql=sql,
            sql_version=sql_version,
            cloudwatch_alarm=cloudwatch_alarm,
            cloudwatch_logs=cloudwatch_logs,
            cloudwatch_metric=cloudwatch_metric,
            description=description,
            dynamodb=dynamodb,
            dynamodbv2=dynamodbv2,
            elasticsearch=elasticsearch,
            error_action=error_action,
            firehose=firehose,
            http=http,
            id=id,
            iot_analytics=iot_analytics,
            iot_events=iot_events,
            kafka=kafka,
            kinesis=kinesis,
            lambda_=lambda_,
            republish=republish,
            s3=s3,
            sns=sns,
            sqs=sqs,
            step_functions=step_functions,
            tags=tags,
            tags_all=tags_all,
            timestream=timestream,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putCloudwatchAlarm")
    def put_cloudwatch_alarm(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchAlarm"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCloudwatchAlarm", [value]))

    @jsii.member(jsii_name="putCloudwatchLogs")
    def put_cloudwatch_logs(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchLogs"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCloudwatchLogs", [value]))

    @jsii.member(jsii_name="putCloudwatchMetric")
    def put_cloudwatch_metric(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleCloudwatchMetric"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCloudwatchMetric", [value]))

    @jsii.member(jsii_name="putDynamodb")
    def put_dynamodb(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodb"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putDynamodb", [value]))

    @jsii.member(jsii_name="putDynamodbv2")
    def put_dynamodbv2(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodbv2"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putDynamodbv2", [value]))

    @jsii.member(jsii_name="putElasticsearch")
    def put_elasticsearch(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleElasticsearch"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putElasticsearch", [value]))

    @jsii.member(jsii_name="putErrorAction")
    def put_error_action(
        self,
        *,
        cloudwatch_alarm: typing.Optional["IotTopicRuleErrorActionCloudwatchAlarm"] = None,
        cloudwatch_logs: typing.Optional["IotTopicRuleErrorActionCloudwatchLogs"] = None,
        cloudwatch_metric: typing.Optional["IotTopicRuleErrorActionCloudwatchMetric"] = None,
        dynamodb: typing.Optional["IotTopicRuleErrorActionDynamodb"] = None,
        dynamodbv2: typing.Optional["IotTopicRuleErrorActionDynamodbv2"] = None,
        elasticsearch: typing.Optional["IotTopicRuleErrorActionElasticsearch"] = None,
        firehose: typing.Optional["IotTopicRuleErrorActionFirehose"] = None,
        http: typing.Optional["IotTopicRuleErrorActionHttp"] = None,
        iot_analytics: typing.Optional["IotTopicRuleErrorActionIotAnalytics"] = None,
        iot_events: typing.Optional["IotTopicRuleErrorActionIotEvents"] = None,
        kafka: typing.Optional["IotTopicRuleErrorActionKafka"] = None,
        kinesis: typing.Optional["IotTopicRuleErrorActionKinesis"] = None,
        lambda_: typing.Optional["IotTopicRuleErrorActionLambda"] = None,
        republish: typing.Optional["IotTopicRuleErrorActionRepublish"] = None,
        s3: typing.Optional["IotTopicRuleErrorActionS3"] = None,
        sns: typing.Optional["IotTopicRuleErrorActionSns"] = None,
        sqs: typing.Optional["IotTopicRuleErrorActionSqs"] = None,
        step_functions: typing.Optional["IotTopicRuleErrorActionStepFunctions"] = None,
        timestream: typing.Optional["IotTopicRuleErrorActionTimestream"] = None,
    ) -> None:
        '''
        :param cloudwatch_alarm: cloudwatch_alarm block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        :param cloudwatch_metric: cloudwatch_metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        :param dynamodb: dynamodb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        :param dynamodbv2: dynamodbv2 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        :param http: http block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        :param iot_analytics: iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        :param iot_events: iot_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        :param kafka: kafka block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        :param kinesis: kinesis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        :param lambda_: lambda block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        :param republish: republish block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        :param sns: sns block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        :param sqs: sqs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        :param step_functions: step_functions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        :param timestream: timestream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        '''
        value = IotTopicRuleErrorAction(
            cloudwatch_alarm=cloudwatch_alarm,
            cloudwatch_logs=cloudwatch_logs,
            cloudwatch_metric=cloudwatch_metric,
            dynamodb=dynamodb,
            dynamodbv2=dynamodbv2,
            elasticsearch=elasticsearch,
            firehose=firehose,
            http=http,
            iot_analytics=iot_analytics,
            iot_events=iot_events,
            kafka=kafka,
            kinesis=kinesis,
            lambda_=lambda_,
            republish=republish,
            s3=s3,
            sns=sns,
            sqs=sqs,
            step_functions=step_functions,
            timestream=timestream,
        )

        return typing.cast(None, jsii.invoke(self, "putErrorAction", [value]))

    @jsii.member(jsii_name="putFirehose")
    def put_firehose(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleFirehose"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFirehose", [value]))

    @jsii.member(jsii_name="putHttp")
    def put_http(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleHttp"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putHttp", [value]))

    @jsii.member(jsii_name="putIotAnalytics")
    def put_iot_analytics(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotAnalytics"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putIotAnalytics", [value]))

    @jsii.member(jsii_name="putIotEvents")
    def put_iot_events(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotEvents"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putIotEvents", [value]))

    @jsii.member(jsii_name="putKafka")
    def put_kafka(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKafka"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putKafka", [value]))

    @jsii.member(jsii_name="putKinesis")
    def put_kinesis(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKinesis"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putKinesis", [value]))

    @jsii.member(jsii_name="putLambda")
    def put_lambda(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleLambda"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putLambda", [value]))

    @jsii.member(jsii_name="putRepublish")
    def put_republish(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleRepublish"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putRepublish", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleS3"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putSns")
    def put_sns(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSns"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putSns", [value]))

    @jsii.member(jsii_name="putSqs")
    def put_sqs(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSqs"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putSqs", [value]))

    @jsii.member(jsii_name="putStepFunctions")
    def put_step_functions(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleStepFunctions"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putStepFunctions", [value]))

    @jsii.member(jsii_name="putTimestream")
    def put_timestream(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleTimestream"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putTimestream", [value]))

    @jsii.member(jsii_name="resetCloudwatchAlarm")
    def reset_cloudwatch_alarm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchAlarm", []))

    @jsii.member(jsii_name="resetCloudwatchLogs")
    def reset_cloudwatch_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogs", []))

    @jsii.member(jsii_name="resetCloudwatchMetric")
    def reset_cloudwatch_metric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchMetric", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDynamodb")
    def reset_dynamodb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamodb", []))

    @jsii.member(jsii_name="resetDynamodbv2")
    def reset_dynamodbv2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamodbv2", []))

    @jsii.member(jsii_name="resetElasticsearch")
    def reset_elasticsearch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearch", []))

    @jsii.member(jsii_name="resetErrorAction")
    def reset_error_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorAction", []))

    @jsii.member(jsii_name="resetFirehose")
    def reset_firehose(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehose", []))

    @jsii.member(jsii_name="resetHttp")
    def reset_http(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIotAnalytics")
    def reset_iot_analytics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIotAnalytics", []))

    @jsii.member(jsii_name="resetIotEvents")
    def reset_iot_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIotEvents", []))

    @jsii.member(jsii_name="resetKafka")
    def reset_kafka(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKafka", []))

    @jsii.member(jsii_name="resetKinesis")
    def reset_kinesis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKinesis", []))

    @jsii.member(jsii_name="resetLambda")
    def reset_lambda(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambda", []))

    @jsii.member(jsii_name="resetRepublish")
    def reset_republish(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepublish", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetSns")
    def reset_sns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSns", []))

    @jsii.member(jsii_name="resetSqs")
    def reset_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqs", []))

    @jsii.member(jsii_name="resetStepFunctions")
    def reset_step_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepFunctions", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimestream")
    def reset_timestream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimestream", []))

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
    @jsii.member(jsii_name="cloudwatchAlarm")
    def cloudwatch_alarm(self) -> "IotTopicRuleCloudwatchAlarmList":
        return typing.cast("IotTopicRuleCloudwatchAlarmList", jsii.get(self, "cloudwatchAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogs")
    def cloudwatch_logs(self) -> "IotTopicRuleCloudwatchLogsList":
        return typing.cast("IotTopicRuleCloudwatchLogsList", jsii.get(self, "cloudwatchLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchMetric")
    def cloudwatch_metric(self) -> "IotTopicRuleCloudwatchMetricList":
        return typing.cast("IotTopicRuleCloudwatchMetricList", jsii.get(self, "cloudwatchMetric"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodb")
    def dynamodb(self) -> "IotTopicRuleDynamodbList":
        return typing.cast("IotTopicRuleDynamodbList", jsii.get(self, "dynamodb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbv2")
    def dynamodbv2(self) -> "IotTopicRuleDynamodbv2List":
        return typing.cast("IotTopicRuleDynamodbv2List", jsii.get(self, "dynamodbv2"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearch")
    def elasticsearch(self) -> "IotTopicRuleElasticsearchList":
        return typing.cast("IotTopicRuleElasticsearchList", jsii.get(self, "elasticsearch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorAction")
    def error_action(self) -> "IotTopicRuleErrorActionOutputReference":
        return typing.cast("IotTopicRuleErrorActionOutputReference", jsii.get(self, "errorAction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehose")
    def firehose(self) -> "IotTopicRuleFirehoseList":
        return typing.cast("IotTopicRuleFirehoseList", jsii.get(self, "firehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="http")
    def http(self) -> "IotTopicRuleHttpList":
        return typing.cast("IotTopicRuleHttpList", jsii.get(self, "http"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotAnalytics")
    def iot_analytics(self) -> "IotTopicRuleIotAnalyticsList":
        return typing.cast("IotTopicRuleIotAnalyticsList", jsii.get(self, "iotAnalytics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotEvents")
    def iot_events(self) -> "IotTopicRuleIotEventsList":
        return typing.cast("IotTopicRuleIotEventsList", jsii.get(self, "iotEvents"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafka")
    def kafka(self) -> "IotTopicRuleKafkaList":
        return typing.cast("IotTopicRuleKafkaList", jsii.get(self, "kafka"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesis")
    def kinesis(self) -> "IotTopicRuleKinesisList":
        return typing.cast("IotTopicRuleKinesisList", jsii.get(self, "kinesis"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> "IotTopicRuleLambdaList":
        return typing.cast("IotTopicRuleLambdaList", jsii.get(self, "lambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="republish")
    def republish(self) -> "IotTopicRuleRepublishList":
        return typing.cast("IotTopicRuleRepublishList", jsii.get(self, "republish"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IotTopicRuleS3List":
        return typing.cast("IotTopicRuleS3List", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sns")
    def sns(self) -> "IotTopicRuleSnsList":
        return typing.cast("IotTopicRuleSnsList", jsii.get(self, "sns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqs")
    def sqs(self) -> "IotTopicRuleSqsList":
        return typing.cast("IotTopicRuleSqsList", jsii.get(self, "sqs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepFunctions")
    def step_functions(self) -> "IotTopicRuleStepFunctionsList":
        return typing.cast("IotTopicRuleStepFunctionsList", jsii.get(self, "stepFunctions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestream")
    def timestream(self) -> "IotTopicRuleTimestreamList":
        return typing.cast("IotTopicRuleTimestreamList", jsii.get(self, "timestream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarmInput")
    def cloudwatch_alarm_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchAlarm"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchAlarm"]]], jsii.get(self, "cloudwatchAlarmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsInput")
    def cloudwatch_logs_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchLogs"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchLogs"]]], jsii.get(self, "cloudwatchLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchMetricInput")
    def cloudwatch_metric_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchMetric"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleCloudwatchMetric"]]], jsii.get(self, "cloudwatchMetricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbInput")
    def dynamodb_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodb"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodb"]]], jsii.get(self, "dynamodbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbv2Input")
    def dynamodbv2_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodbv2"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodbv2"]]], jsii.get(self, "dynamodbv2Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchInput")
    def elasticsearch_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleElasticsearch"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleElasticsearch"]]], jsii.get(self, "elasticsearchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorActionInput")
    def error_action_input(self) -> typing.Optional["IotTopicRuleErrorAction"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorAction"], jsii.get(self, "errorActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseInput")
    def firehose_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleFirehose"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleFirehose"]]], jsii.get(self, "firehoseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpInput")
    def http_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttp"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttp"]]], jsii.get(self, "httpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotAnalyticsInput")
    def iot_analytics_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotAnalytics"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotAnalytics"]]], jsii.get(self, "iotAnalyticsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotEventsInput")
    def iot_events_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotEvents"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotEvents"]]], jsii.get(self, "iotEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaInput")
    def kafka_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKafka"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKafka"]]], jsii.get(self, "kafkaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisInput")
    def kinesis_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKinesis"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKinesis"]]], jsii.get(self, "kinesisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaInput")
    def lambda_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleLambda"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleLambda"]]], jsii.get(self, "lambdaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="republishInput")
    def republish_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleRepublish"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleRepublish"]]], jsii.get(self, "republishInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleS3"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleS3"]]], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsInput")
    def sns_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSns"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSns"]]], jsii.get(self, "snsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlInput")
    def sql_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlVersionInput")
    def sql_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsInput")
    def sqs_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSqs"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSqs"]]], jsii.get(self, "sqsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepFunctionsInput")
    def step_functions_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleStepFunctions"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleStepFunctions"]]], jsii.get(self, "stepFunctionsInput"))

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
    @jsii.member(jsii_name="timestreamInput")
    def timestream_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestream"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestream"]]], jsii.get(self, "timestreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

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
    @jsii.member(jsii_name="sql")
    def sql(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sql"))

    @sql.setter
    def sql(self, value: builtins.str) -> None:
        jsii.set(self, "sql", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqlVersion")
    def sql_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlVersion"))

    @sql_version.setter
    def sql_version(self, value: builtins.str) -> None:
        jsii.set(self, "sqlVersion", value)

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
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchAlarm",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_name": "alarmName",
        "role_arn": "roleArn",
        "state_reason": "stateReason",
        "state_value": "stateValue",
    },
)
class IotTopicRuleCloudwatchAlarm:
    def __init__(
        self,
        *,
        alarm_name: builtins.str,
        role_arn: builtins.str,
        state_reason: builtins.str,
        state_value: builtins.str,
    ) -> None:
        '''
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#alarm_name IotTopicRule#alarm_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_reason IotTopicRule#state_reason}.
        :param state_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_value IotTopicRule#state_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_name": alarm_name,
            "role_arn": role_arn,
            "state_reason": state_reason,
            "state_value": state_value,
        }

    @builtins.property
    def alarm_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#alarm_name IotTopicRule#alarm_name}.'''
        result = self._values.get("alarm_name")
        assert result is not None, "Required property 'alarm_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_reason(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_reason IotTopicRule#state_reason}.'''
        result = self._values.get("state_reason")
        assert result is not None, "Required property 'state_reason' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_value IotTopicRule#state_value}.'''
        result = self._values.get("state_value")
        assert result is not None, "Required property 'state_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleCloudwatchAlarm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleCloudwatchAlarmList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchAlarmList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleCloudwatchAlarmOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleCloudwatchAlarmOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchAlarm]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchAlarm]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchAlarm]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleCloudwatchAlarmOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchAlarmOutputReference",
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
    @jsii.member(jsii_name="alarmNameInput")
    def alarm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateReasonInput")
    def state_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateReasonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateValueInput")
    def state_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmName"))

    @alarm_name.setter
    def alarm_name(self, value: builtins.str) -> None:
        jsii.set(self, "alarmName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateReason")
    def state_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateReason"))

    @state_reason.setter
    def state_reason(self, value: builtins.str) -> None:
        jsii.set(self, "stateReason", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateValue")
    def state_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateValue"))

    @state_value.setter
    def state_value(self, value: builtins.str) -> None:
        jsii.set(self, "stateValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleCloudwatchAlarm, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleCloudwatchAlarm, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleCloudwatchAlarm, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchLogs",
    jsii_struct_bases=[],
    name_mapping={"log_group_name": "logGroupName", "role_arn": "roleArn"},
)
class IotTopicRuleCloudwatchLogs:
    def __init__(self, *, log_group_name: builtins.str, role_arn: builtins.str) -> None:
        '''
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#log_group_name IotTopicRule#log_group_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
            "role_arn": role_arn,
        }

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#log_group_name IotTopicRule#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleCloudwatchLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleCloudwatchLogsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchLogsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleCloudwatchLogsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleCloudwatchLogsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchLogs]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchLogs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchLogs]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleCloudwatchLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchLogsOutputReference",
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
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleCloudwatchLogs, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleCloudwatchLogs, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleCloudwatchLogs, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchMetric",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "metric_namespace": "metricNamespace",
        "metric_unit": "metricUnit",
        "metric_value": "metricValue",
        "role_arn": "roleArn",
        "metric_timestamp": "metricTimestamp",
    },
)
class IotTopicRuleCloudwatchMetric:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        metric_namespace: builtins.str,
        metric_unit: builtins.str,
        metric_value: builtins.str,
        role_arn: builtins.str,
        metric_timestamp: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_name IotTopicRule#metric_name}.
        :param metric_namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_namespace IotTopicRule#metric_namespace}.
        :param metric_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_unit IotTopicRule#metric_unit}.
        :param metric_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_value IotTopicRule#metric_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param metric_timestamp: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_timestamp IotTopicRule#metric_timestamp}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metric_name": metric_name,
            "metric_namespace": metric_namespace,
            "metric_unit": metric_unit,
            "metric_value": metric_value,
            "role_arn": role_arn,
        }
        if metric_timestamp is not None:
            self._values["metric_timestamp"] = metric_timestamp

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_name IotTopicRule#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_namespace IotTopicRule#metric_namespace}.'''
        result = self._values.get("metric_namespace")
        assert result is not None, "Required property 'metric_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_unit IotTopicRule#metric_unit}.'''
        result = self._values.get("metric_unit")
        assert result is not None, "Required property 'metric_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_value IotTopicRule#metric_value}.'''
        result = self._values.get("metric_value")
        assert result is not None, "Required property 'metric_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_timestamp(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_timestamp IotTopicRule#metric_timestamp}.'''
        result = self._values.get("metric_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleCloudwatchMetric(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleCloudwatchMetricList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchMetricList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleCloudwatchMetricOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleCloudwatchMetricOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchMetric]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchMetric]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchMetric]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleCloudwatchMetricOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleCloudwatchMetricOutputReference",
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

    @jsii.member(jsii_name="resetMetricTimestamp")
    def reset_metric_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricTimestamp", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNamespaceInput")
    def metric_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNamespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTimestampInput")
    def metric_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricTimestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricUnitInput")
    def metric_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricValueInput")
    def metric_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @metric_namespace.setter
    def metric_namespace(self, value: builtins.str) -> None:
        jsii.set(self, "metricNamespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTimestamp")
    def metric_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricTimestamp"))

    @metric_timestamp.setter
    def metric_timestamp(self, value: builtins.str) -> None:
        jsii.set(self, "metricTimestamp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricUnit")
    def metric_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricUnit"))

    @metric_unit.setter
    def metric_unit(self, value: builtins.str) -> None:
        jsii.set(self, "metricUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricValue")
    def metric_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricValue"))

    @metric_value.setter
    def metric_value(self, value: builtins.str) -> None:
        jsii.set(self, "metricValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleCloudwatchMetric, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleCloudwatchMetric, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleCloudwatchMetric, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "enabled": "enabled",
        "name": "name",
        "sql": "sql",
        "sql_version": "sqlVersion",
        "cloudwatch_alarm": "cloudwatchAlarm",
        "cloudwatch_logs": "cloudwatchLogs",
        "cloudwatch_metric": "cloudwatchMetric",
        "description": "description",
        "dynamodb": "dynamodb",
        "dynamodbv2": "dynamodbv2",
        "elasticsearch": "elasticsearch",
        "error_action": "errorAction",
        "firehose": "firehose",
        "http": "http",
        "id": "id",
        "iot_analytics": "iotAnalytics",
        "iot_events": "iotEvents",
        "kafka": "kafka",
        "kinesis": "kinesis",
        "lambda_": "lambda",
        "republish": "republish",
        "s3": "s3",
        "sns": "sns",
        "sqs": "sqs",
        "step_functions": "stepFunctions",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timestream": "timestream",
    },
)
class IotTopicRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        name: builtins.str,
        sql: builtins.str,
        sql_version: builtins.str,
        cloudwatch_alarm: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleCloudwatchAlarm]]] = None,
        cloudwatch_logs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleCloudwatchLogs]]] = None,
        cloudwatch_metric: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleCloudwatchMetric]]] = None,
        description: typing.Optional[builtins.str] = None,
        dynamodb: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodb"]]] = None,
        dynamodbv2: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleDynamodbv2"]]] = None,
        elasticsearch: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleElasticsearch"]]] = None,
        error_action: typing.Optional["IotTopicRuleErrorAction"] = None,
        firehose: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleFirehose"]]] = None,
        http: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleHttp"]]] = None,
        id: typing.Optional[builtins.str] = None,
        iot_analytics: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotAnalytics"]]] = None,
        iot_events: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleIotEvents"]]] = None,
        kafka: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKafka"]]] = None,
        kinesis: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleKinesis"]]] = None,
        lambda_: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleLambda"]]] = None,
        republish: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleRepublish"]]] = None,
        s3: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleS3"]]] = None,
        sns: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSns"]]] = None,
        sqs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleSqs"]]] = None,
        step_functions: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleStepFunctions"]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timestream: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleTimestream"]]] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#enabled IotTopicRule#enabled}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.
        :param sql: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql IotTopicRule#sql}.
        :param sql_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql_version IotTopicRule#sql_version}.
        :param cloudwatch_alarm: cloudwatch_alarm block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        :param cloudwatch_metric: cloudwatch_metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#description IotTopicRule#description}.
        :param dynamodb: dynamodb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        :param dynamodbv2: dynamodbv2 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        :param error_action: error_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#error_action IotTopicRule#error_action}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        :param http: http block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param iot_analytics: iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        :param iot_events: iot_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        :param kafka: kafka block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        :param kinesis: kinesis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        :param lambda_: lambda block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        :param republish: republish block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        :param sns: sns block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        :param sqs: sqs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        :param step_functions: step_functions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags IotTopicRule#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags_all IotTopicRule#tags_all}.
        :param timestream: timestream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(error_action, dict):
            error_action = IotTopicRuleErrorAction(**error_action)
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
            "name": name,
            "sql": sql,
            "sql_version": sql_version,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if cloudwatch_alarm is not None:
            self._values["cloudwatch_alarm"] = cloudwatch_alarm
        if cloudwatch_logs is not None:
            self._values["cloudwatch_logs"] = cloudwatch_logs
        if cloudwatch_metric is not None:
            self._values["cloudwatch_metric"] = cloudwatch_metric
        if description is not None:
            self._values["description"] = description
        if dynamodb is not None:
            self._values["dynamodb"] = dynamodb
        if dynamodbv2 is not None:
            self._values["dynamodbv2"] = dynamodbv2
        if elasticsearch is not None:
            self._values["elasticsearch"] = elasticsearch
        if error_action is not None:
            self._values["error_action"] = error_action
        if firehose is not None:
            self._values["firehose"] = firehose
        if http is not None:
            self._values["http"] = http
        if id is not None:
            self._values["id"] = id
        if iot_analytics is not None:
            self._values["iot_analytics"] = iot_analytics
        if iot_events is not None:
            self._values["iot_events"] = iot_events
        if kafka is not None:
            self._values["kafka"] = kafka
        if kinesis is not None:
            self._values["kinesis"] = kinesis
        if lambda_ is not None:
            self._values["lambda_"] = lambda_
        if republish is not None:
            self._values["republish"] = republish
        if s3 is not None:
            self._values["s3"] = s3
        if sns is not None:
            self._values["sns"] = sns
        if sqs is not None:
            self._values["sqs"] = sqs
        if step_functions is not None:
            self._values["step_functions"] = step_functions
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timestream is not None:
            self._values["timestream"] = timestream

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
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#enabled IotTopicRule#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sql(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql IotTopicRule#sql}.'''
        result = self._values.get("sql")
        assert result is not None, "Required property 'sql' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sql_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sql_version IotTopicRule#sql_version}.'''
        result = self._values.get("sql_version")
        assert result is not None, "Required property 'sql_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudwatch_alarm(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchAlarm]]]:
        '''cloudwatch_alarm block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        '''
        result = self._values.get("cloudwatch_alarm")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchAlarm]]], result)

    @builtins.property
    def cloudwatch_logs(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchLogs]]]:
        '''cloudwatch_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        '''
        result = self._values.get("cloudwatch_logs")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchLogs]]], result)

    @builtins.property
    def cloudwatch_metric(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchMetric]]]:
        '''cloudwatch_metric block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        '''
        result = self._values.get("cloudwatch_metric")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleCloudwatchMetric]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#description IotTopicRule#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dynamodb(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodb"]]]:
        '''dynamodb block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        '''
        result = self._values.get("dynamodb")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodb"]]], result)

    @builtins.property
    def dynamodbv2(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodbv2"]]]:
        '''dynamodbv2 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        '''
        result = self._values.get("dynamodbv2")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleDynamodbv2"]]], result)

    @builtins.property
    def elasticsearch(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleElasticsearch"]]]:
        '''elasticsearch block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        '''
        result = self._values.get("elasticsearch")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleElasticsearch"]]], result)

    @builtins.property
    def error_action(self) -> typing.Optional["IotTopicRuleErrorAction"]:
        '''error_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#error_action IotTopicRule#error_action}
        '''
        result = self._values.get("error_action")
        return typing.cast(typing.Optional["IotTopicRuleErrorAction"], result)

    @builtins.property
    def firehose(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleFirehose"]]]:
        '''firehose block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleFirehose"]]], result)

    @builtins.property
    def http(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttp"]]]:
        '''http block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        '''
        result = self._values.get("http")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttp"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iot_analytics(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotAnalytics"]]]:
        '''iot_analytics block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        '''
        result = self._values.get("iot_analytics")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotAnalytics"]]], result)

    @builtins.property
    def iot_events(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotEvents"]]]:
        '''iot_events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        '''
        result = self._values.get("iot_events")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleIotEvents"]]], result)

    @builtins.property
    def kafka(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKafka"]]]:
        '''kafka block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        '''
        result = self._values.get("kafka")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKafka"]]], result)

    @builtins.property
    def kinesis(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKinesis"]]]:
        '''kinesis block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        '''
        result = self._values.get("kinesis")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleKinesis"]]], result)

    @builtins.property
    def lambda_(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleLambda"]]]:
        '''lambda block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        '''
        result = self._values.get("lambda_")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleLambda"]]], result)

    @builtins.property
    def republish(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleRepublish"]]]:
        '''republish block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        '''
        result = self._values.get("republish")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleRepublish"]]], result)

    @builtins.property
    def s3(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleS3"]]]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleS3"]]], result)

    @builtins.property
    def sns(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSns"]]]:
        '''sns block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        '''
        result = self._values.get("sns")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSns"]]], result)

    @builtins.property
    def sqs(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSqs"]]]:
        '''sqs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        '''
        result = self._values.get("sqs")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleSqs"]]], result)

    @builtins.property
    def step_functions(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleStepFunctions"]]]:
        '''step_functions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        '''
        result = self._values.get("step_functions")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleStepFunctions"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags IotTopicRule#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#tags_all IotTopicRule#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timestream(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestream"]]]:
        '''timestream block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        '''
        result = self._values.get("timestream")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestream"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDestination(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestination",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination aws_iot_topic_rule_destination}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        vpc_configuration: "IotTopicRuleDestinationVpcConfiguration",
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["IotTopicRuleDestinationTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination aws_iot_topic_rule_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param vpc_configuration: vpc_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_configuration IotTopicRuleDestination#vpc_configuration}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#enabled IotTopicRuleDestination#enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#id IotTopicRuleDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#timeouts IotTopicRuleDestination#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IotTopicRuleDestinationConfig(
            vpc_configuration=vpc_configuration,
            enabled=enabled,
            id=id,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#create IotTopicRuleDestination#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#delete IotTopicRuleDestination#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#update IotTopicRuleDestination#update}.
        '''
        value = IotTopicRuleDestinationTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putVpcConfiguration")
    def put_vpc_configuration(
        self,
        *,
        role_arn: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#role_arn IotTopicRuleDestination#role_arn}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#subnet_ids IotTopicRuleDestination#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_id IotTopicRuleDestination#vpc_id}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#security_groups IotTopicRuleDestination#security_groups}.
        '''
        value = IotTopicRuleDestinationVpcConfiguration(
            role_arn=role_arn,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
            security_groups=security_groups,
        )

        return typing.cast(None, jsii.invoke(self, "putVpcConfiguration", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

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
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "IotTopicRuleDestinationTimeoutsOutputReference":
        return typing.cast("IotTopicRuleDestinationTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(
        self,
    ) -> "IotTopicRuleDestinationVpcConfigurationOutputReference":
        return typing.cast("IotTopicRuleDestinationVpcConfigurationOutputReference", jsii.get(self, "vpcConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["IotTopicRuleDestinationTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["IotTopicRuleDestinationTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfigurationInput")
    def vpc_configuration_input(
        self,
    ) -> typing.Optional["IotTopicRuleDestinationVpcConfiguration"]:
        return typing.cast(typing.Optional["IotTopicRuleDestinationVpcConfiguration"], jsii.get(self, "vpcConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestinationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "vpc_configuration": "vpcConfiguration",
        "enabled": "enabled",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class IotTopicRuleDestinationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        vpc_configuration: "IotTopicRuleDestinationVpcConfiguration",
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["IotTopicRuleDestinationTimeouts"] = None,
    ) -> None:
        '''AWS IoT.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param vpc_configuration: vpc_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_configuration IotTopicRuleDestination#vpc_configuration}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#enabled IotTopicRuleDestination#enabled}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#id IotTopicRuleDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#timeouts IotTopicRuleDestination#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = IotTopicRuleDestinationVpcConfiguration(**vpc_configuration)
        if isinstance(timeouts, dict):
            timeouts = IotTopicRuleDestinationTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc_configuration": vpc_configuration,
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
    def vpc_configuration(self) -> "IotTopicRuleDestinationVpcConfiguration":
        '''vpc_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_configuration IotTopicRuleDestination#vpc_configuration}
        '''
        result = self._values.get("vpc_configuration")
        assert result is not None, "Required property 'vpc_configuration' is missing"
        return typing.cast("IotTopicRuleDestinationVpcConfiguration", result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#enabled IotTopicRuleDestination#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#id IotTopicRuleDestination#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["IotTopicRuleDestinationTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#timeouts IotTopicRuleDestination#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["IotTopicRuleDestinationTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestinationTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class IotTopicRuleDestinationTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#create IotTopicRuleDestination#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#delete IotTopicRuleDestination#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#update IotTopicRuleDestination#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#create IotTopicRuleDestination#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#delete IotTopicRuleDestination#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#update IotTopicRuleDestination#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDestinationTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDestinationTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestinationTimeoutsOutputReference",
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
    ) -> typing.Optional[typing.Union[IotTopicRuleDestinationTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleDestinationTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleDestinationTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestinationVpcConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "subnet_ids": "subnetIds",
        "vpc_id": "vpcId",
        "security_groups": "securityGroups",
    },
)
class IotTopicRuleDestinationVpcConfiguration:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#role_arn IotTopicRuleDestination#role_arn}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#subnet_ids IotTopicRuleDestination#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_id IotTopicRuleDestination#vpc_id}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#security_groups IotTopicRuleDestination#security_groups}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "subnet_ids": subnet_ids,
            "vpc_id": vpc_id,
        }
        if security_groups is not None:
            self._values["security_groups"] = security_groups

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#role_arn IotTopicRuleDestination#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#subnet_ids IotTopicRuleDestination#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#vpc_id IotTopicRuleDestination#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule_destination#security_groups IotTopicRuleDestination#security_groups}.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDestinationVpcConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDestinationVpcConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDestinationVpcConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetSecurityGroups")
    def reset_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroups", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotTopicRuleDestinationVpcConfiguration]:
        return typing.cast(typing.Optional[IotTopicRuleDestinationVpcConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleDestinationVpcConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodb",
    jsii_struct_bases=[],
    name_mapping={
        "hash_key_field": "hashKeyField",
        "hash_key_value": "hashKeyValue",
        "role_arn": "roleArn",
        "table_name": "tableName",
        "hash_key_type": "hashKeyType",
        "operation": "operation",
        "payload_field": "payloadField",
        "range_key_field": "rangeKeyField",
        "range_key_type": "rangeKeyType",
        "range_key_value": "rangeKeyValue",
    },
)
class IotTopicRuleDynamodb:
    def __init__(
        self,
        *,
        hash_key_field: builtins.str,
        hash_key_value: builtins.str,
        role_arn: builtins.str,
        table_name: builtins.str,
        hash_key_type: typing.Optional[builtins.str] = None,
        operation: typing.Optional[builtins.str] = None,
        payload_field: typing.Optional[builtins.str] = None,
        range_key_field: typing.Optional[builtins.str] = None,
        range_key_type: typing.Optional[builtins.str] = None,
        range_key_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hash_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_field IotTopicRule#hash_key_field}.
        :param hash_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_value IotTopicRule#hash_key_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param hash_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_type IotTopicRule#hash_key_type}.
        :param operation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#operation IotTopicRule#operation}.
        :param payload_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#payload_field IotTopicRule#payload_field}.
        :param range_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_field IotTopicRule#range_key_field}.
        :param range_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_type IotTopicRule#range_key_type}.
        :param range_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_value IotTopicRule#range_key_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hash_key_field": hash_key_field,
            "hash_key_value": hash_key_value,
            "role_arn": role_arn,
            "table_name": table_name,
        }
        if hash_key_type is not None:
            self._values["hash_key_type"] = hash_key_type
        if operation is not None:
            self._values["operation"] = operation
        if payload_field is not None:
            self._values["payload_field"] = payload_field
        if range_key_field is not None:
            self._values["range_key_field"] = range_key_field
        if range_key_type is not None:
            self._values["range_key_type"] = range_key_type
        if range_key_value is not None:
            self._values["range_key_value"] = range_key_value

    @builtins.property
    def hash_key_field(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_field IotTopicRule#hash_key_field}.'''
        result = self._values.get("hash_key_field")
        assert result is not None, "Required property 'hash_key_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hash_key_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_value IotTopicRule#hash_key_value}.'''
        result = self._values.get("hash_key_value")
        assert result is not None, "Required property 'hash_key_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hash_key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_type IotTopicRule#hash_key_type}.'''
        result = self._values.get("hash_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#operation IotTopicRule#operation}.'''
        result = self._values.get("operation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload_field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#payload_field IotTopicRule#payload_field}.'''
        result = self._values.get("payload_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_field IotTopicRule#range_key_field}.'''
        result = self._values.get("range_key_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_type IotTopicRule#range_key_type}.'''
        result = self._values.get("range_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_value IotTopicRule#range_key_value}.'''
        result = self._values.get("range_key_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDynamodb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDynamodbList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleDynamodbOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleDynamodbOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodb]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodb]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodb]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleDynamodbOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbOutputReference",
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

    @jsii.member(jsii_name="resetHashKeyType")
    def reset_hash_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashKeyType", []))

    @jsii.member(jsii_name="resetOperation")
    def reset_operation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperation", []))

    @jsii.member(jsii_name="resetPayloadField")
    def reset_payload_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadField", []))

    @jsii.member(jsii_name="resetRangeKeyField")
    def reset_range_key_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyField", []))

    @jsii.member(jsii_name="resetRangeKeyType")
    def reset_range_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyType", []))

    @jsii.member(jsii_name="resetRangeKeyValue")
    def reset_range_key_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyFieldInput")
    def hash_key_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyTypeInput")
    def hash_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyValueInput")
    def hash_key_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationInput")
    def operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFieldInput")
    def payload_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyFieldInput")
    def range_key_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyTypeInput")
    def range_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyValueInput")
    def range_key_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyField")
    def hash_key_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyField"))

    @hash_key_field.setter
    def hash_key_field(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyType")
    def hash_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyType"))

    @hash_key_type.setter
    def hash_key_type(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyValue")
    def hash_key_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyValue"))

    @hash_key_value.setter
    def hash_key_value(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operation")
    def operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operation"))

    @operation.setter
    def operation(self, value: builtins.str) -> None:
        jsii.set(self, "operation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadField")
    def payload_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadField"))

    @payload_field.setter
    def payload_field(self, value: builtins.str) -> None:
        jsii.set(self, "payloadField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyField")
    def range_key_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyField"))

    @range_key_field.setter
    def range_key_field(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyType")
    def range_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyType"))

    @range_key_type.setter
    def range_key_type(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyValue")
    def range_key_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyValue"))

    @range_key_value.setter
    def range_key_value(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleDynamodb, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleDynamodb, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleDynamodb, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbv2",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "put_item": "putItem"},
)
class IotTopicRuleDynamodbv2:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        put_item: typing.Optional["IotTopicRuleDynamodbv2PutItem"] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param put_item: put_item block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#put_item IotTopicRule#put_item}
        '''
        if isinstance(put_item, dict):
            put_item = IotTopicRuleDynamodbv2PutItem(**put_item)
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if put_item is not None:
            self._values["put_item"] = put_item

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def put_item(self) -> typing.Optional["IotTopicRuleDynamodbv2PutItem"]:
        '''put_item block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#put_item IotTopicRule#put_item}
        '''
        result = self._values.get("put_item")
        return typing.cast(typing.Optional["IotTopicRuleDynamodbv2PutItem"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDynamodbv2(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDynamodbv2List(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbv2List",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleDynamodbv2OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleDynamodbv2OutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodbv2]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodbv2]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleDynamodbv2]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleDynamodbv2OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbv2OutputReference",
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

    @jsii.member(jsii_name="putPutItem")
    def put_put_item(self, *, table_name: builtins.str) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        '''
        value = IotTopicRuleDynamodbv2PutItem(table_name=table_name)

        return typing.cast(None, jsii.invoke(self, "putPutItem", [value]))

    @jsii.member(jsii_name="resetPutItem")
    def reset_put_item(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPutItem", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="putItem")
    def put_item(self) -> "IotTopicRuleDynamodbv2PutItemOutputReference":
        return typing.cast("IotTopicRuleDynamodbv2PutItemOutputReference", jsii.get(self, "putItem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="putItemInput")
    def put_item_input(self) -> typing.Optional["IotTopicRuleDynamodbv2PutItem"]:
        return typing.cast(typing.Optional["IotTopicRuleDynamodbv2PutItem"], jsii.get(self, "putItemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleDynamodbv2, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleDynamodbv2, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleDynamodbv2, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbv2PutItem",
    jsii_struct_bases=[],
    name_mapping={"table_name": "tableName"},
)
class IotTopicRuleDynamodbv2PutItem:
    def __init__(self, *, table_name: builtins.str) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "table_name": table_name,
        }

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleDynamodbv2PutItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleDynamodbv2PutItemOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleDynamodbv2PutItemOutputReference",
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
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleDynamodbv2PutItem]:
        return typing.cast(typing.Optional[IotTopicRuleDynamodbv2PutItem], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleDynamodbv2PutItem],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleElasticsearch",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint": "endpoint",
        "id": "id",
        "index": "index",
        "role_arn": "roleArn",
        "type": "type",
    },
)
class IotTopicRuleElasticsearch:
    def __init__(
        self,
        *,
        endpoint: builtins.str,
        id: builtins.str,
        index: builtins.str,
        role_arn: builtins.str,
        type: builtins.str,
    ) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#endpoint IotTopicRule#endpoint}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#index IotTopicRule#index}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#type IotTopicRule#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
            "id": id,
            "index": index,
            "role_arn": role_arn,
            "type": type,
        }

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#endpoint IotTopicRule#endpoint}.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#index IotTopicRule#index}.'''
        result = self._values.get("index")
        assert result is not None, "Required property 'index' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#type IotTopicRule#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleElasticsearch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleElasticsearchList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleElasticsearchList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleElasticsearchOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleElasticsearchOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleElasticsearch]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleElasticsearch]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleElasticsearch]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleElasticsearchOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleElasticsearchOutputReference",
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
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexInput")
    def index_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="index")
    def index(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "index"))

    @index.setter
    def index(self, value: builtins.str) -> None:
        jsii.set(self, "index", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

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
    ) -> typing.Optional[typing.Union[IotTopicRuleElasticsearch, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleElasticsearch, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleElasticsearch, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorAction",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_alarm": "cloudwatchAlarm",
        "cloudwatch_logs": "cloudwatchLogs",
        "cloudwatch_metric": "cloudwatchMetric",
        "dynamodb": "dynamodb",
        "dynamodbv2": "dynamodbv2",
        "elasticsearch": "elasticsearch",
        "firehose": "firehose",
        "http": "http",
        "iot_analytics": "iotAnalytics",
        "iot_events": "iotEvents",
        "kafka": "kafka",
        "kinesis": "kinesis",
        "lambda_": "lambda",
        "republish": "republish",
        "s3": "s3",
        "sns": "sns",
        "sqs": "sqs",
        "step_functions": "stepFunctions",
        "timestream": "timestream",
    },
)
class IotTopicRuleErrorAction:
    def __init__(
        self,
        *,
        cloudwatch_alarm: typing.Optional["IotTopicRuleErrorActionCloudwatchAlarm"] = None,
        cloudwatch_logs: typing.Optional["IotTopicRuleErrorActionCloudwatchLogs"] = None,
        cloudwatch_metric: typing.Optional["IotTopicRuleErrorActionCloudwatchMetric"] = None,
        dynamodb: typing.Optional["IotTopicRuleErrorActionDynamodb"] = None,
        dynamodbv2: typing.Optional["IotTopicRuleErrorActionDynamodbv2"] = None,
        elasticsearch: typing.Optional["IotTopicRuleErrorActionElasticsearch"] = None,
        firehose: typing.Optional["IotTopicRuleErrorActionFirehose"] = None,
        http: typing.Optional["IotTopicRuleErrorActionHttp"] = None,
        iot_analytics: typing.Optional["IotTopicRuleErrorActionIotAnalytics"] = None,
        iot_events: typing.Optional["IotTopicRuleErrorActionIotEvents"] = None,
        kafka: typing.Optional["IotTopicRuleErrorActionKafka"] = None,
        kinesis: typing.Optional["IotTopicRuleErrorActionKinesis"] = None,
        lambda_: typing.Optional["IotTopicRuleErrorActionLambda"] = None,
        republish: typing.Optional["IotTopicRuleErrorActionRepublish"] = None,
        s3: typing.Optional["IotTopicRuleErrorActionS3"] = None,
        sns: typing.Optional["IotTopicRuleErrorActionSns"] = None,
        sqs: typing.Optional["IotTopicRuleErrorActionSqs"] = None,
        step_functions: typing.Optional["IotTopicRuleErrorActionStepFunctions"] = None,
        timestream: typing.Optional["IotTopicRuleErrorActionTimestream"] = None,
    ) -> None:
        '''
        :param cloudwatch_alarm: cloudwatch_alarm block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        :param cloudwatch_logs: cloudwatch_logs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        :param cloudwatch_metric: cloudwatch_metric block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        :param dynamodb: dynamodb block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        :param dynamodbv2: dynamodbv2 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        :param firehose: firehose block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        :param http: http block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        :param iot_analytics: iot_analytics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        :param iot_events: iot_events block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        :param kafka: kafka block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        :param kinesis: kinesis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        :param lambda_: lambda block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        :param republish: republish block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        :param s3: s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        :param sns: sns block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        :param sqs: sqs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        :param step_functions: step_functions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        :param timestream: timestream block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        '''
        if isinstance(cloudwatch_alarm, dict):
            cloudwatch_alarm = IotTopicRuleErrorActionCloudwatchAlarm(**cloudwatch_alarm)
        if isinstance(cloudwatch_logs, dict):
            cloudwatch_logs = IotTopicRuleErrorActionCloudwatchLogs(**cloudwatch_logs)
        if isinstance(cloudwatch_metric, dict):
            cloudwatch_metric = IotTopicRuleErrorActionCloudwatchMetric(**cloudwatch_metric)
        if isinstance(dynamodb, dict):
            dynamodb = IotTopicRuleErrorActionDynamodb(**dynamodb)
        if isinstance(dynamodbv2, dict):
            dynamodbv2 = IotTopicRuleErrorActionDynamodbv2(**dynamodbv2)
        if isinstance(elasticsearch, dict):
            elasticsearch = IotTopicRuleErrorActionElasticsearch(**elasticsearch)
        if isinstance(firehose, dict):
            firehose = IotTopicRuleErrorActionFirehose(**firehose)
        if isinstance(http, dict):
            http = IotTopicRuleErrorActionHttp(**http)
        if isinstance(iot_analytics, dict):
            iot_analytics = IotTopicRuleErrorActionIotAnalytics(**iot_analytics)
        if isinstance(iot_events, dict):
            iot_events = IotTopicRuleErrorActionIotEvents(**iot_events)
        if isinstance(kafka, dict):
            kafka = IotTopicRuleErrorActionKafka(**kafka)
        if isinstance(kinesis, dict):
            kinesis = IotTopicRuleErrorActionKinesis(**kinesis)
        if isinstance(lambda_, dict):
            lambda_ = IotTopicRuleErrorActionLambda(**lambda_)
        if isinstance(republish, dict):
            republish = IotTopicRuleErrorActionRepublish(**republish)
        if isinstance(s3, dict):
            s3 = IotTopicRuleErrorActionS3(**s3)
        if isinstance(sns, dict):
            sns = IotTopicRuleErrorActionSns(**sns)
        if isinstance(sqs, dict):
            sqs = IotTopicRuleErrorActionSqs(**sqs)
        if isinstance(step_functions, dict):
            step_functions = IotTopicRuleErrorActionStepFunctions(**step_functions)
        if isinstance(timestream, dict):
            timestream = IotTopicRuleErrorActionTimestream(**timestream)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloudwatch_alarm is not None:
            self._values["cloudwatch_alarm"] = cloudwatch_alarm
        if cloudwatch_logs is not None:
            self._values["cloudwatch_logs"] = cloudwatch_logs
        if cloudwatch_metric is not None:
            self._values["cloudwatch_metric"] = cloudwatch_metric
        if dynamodb is not None:
            self._values["dynamodb"] = dynamodb
        if dynamodbv2 is not None:
            self._values["dynamodbv2"] = dynamodbv2
        if elasticsearch is not None:
            self._values["elasticsearch"] = elasticsearch
        if firehose is not None:
            self._values["firehose"] = firehose
        if http is not None:
            self._values["http"] = http
        if iot_analytics is not None:
            self._values["iot_analytics"] = iot_analytics
        if iot_events is not None:
            self._values["iot_events"] = iot_events
        if kafka is not None:
            self._values["kafka"] = kafka
        if kinesis is not None:
            self._values["kinesis"] = kinesis
        if lambda_ is not None:
            self._values["lambda_"] = lambda_
        if republish is not None:
            self._values["republish"] = republish
        if s3 is not None:
            self._values["s3"] = s3
        if sns is not None:
            self._values["sns"] = sns
        if sqs is not None:
            self._values["sqs"] = sqs
        if step_functions is not None:
            self._values["step_functions"] = step_functions
        if timestream is not None:
            self._values["timestream"] = timestream

    @builtins.property
    def cloudwatch_alarm(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionCloudwatchAlarm"]:
        '''cloudwatch_alarm block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_alarm IotTopicRule#cloudwatch_alarm}
        '''
        result = self._values.get("cloudwatch_alarm")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionCloudwatchAlarm"], result)

    @builtins.property
    def cloudwatch_logs(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionCloudwatchLogs"]:
        '''cloudwatch_logs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_logs IotTopicRule#cloudwatch_logs}
        '''
        result = self._values.get("cloudwatch_logs")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionCloudwatchLogs"], result)

    @builtins.property
    def cloudwatch_metric(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionCloudwatchMetric"]:
        '''cloudwatch_metric block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#cloudwatch_metric IotTopicRule#cloudwatch_metric}
        '''
        result = self._values.get("cloudwatch_metric")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionCloudwatchMetric"], result)

    @builtins.property
    def dynamodb(self) -> typing.Optional["IotTopicRuleErrorActionDynamodb"]:
        '''dynamodb block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodb IotTopicRule#dynamodb}
        '''
        result = self._values.get("dynamodb")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionDynamodb"], result)

    @builtins.property
    def dynamodbv2(self) -> typing.Optional["IotTopicRuleErrorActionDynamodbv2"]:
        '''dynamodbv2 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dynamodbv2 IotTopicRule#dynamodbv2}
        '''
        result = self._values.get("dynamodbv2")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionDynamodbv2"], result)

    @builtins.property
    def elasticsearch(self) -> typing.Optional["IotTopicRuleErrorActionElasticsearch"]:
        '''elasticsearch block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#elasticsearch IotTopicRule#elasticsearch}
        '''
        result = self._values.get("elasticsearch")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionElasticsearch"], result)

    @builtins.property
    def firehose(self) -> typing.Optional["IotTopicRuleErrorActionFirehose"]:
        '''firehose block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#firehose IotTopicRule#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionFirehose"], result)

    @builtins.property
    def http(self) -> typing.Optional["IotTopicRuleErrorActionHttp"]:
        '''http block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http IotTopicRule#http}
        '''
        result = self._values.get("http")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionHttp"], result)

    @builtins.property
    def iot_analytics(self) -> typing.Optional["IotTopicRuleErrorActionIotAnalytics"]:
        '''iot_analytics block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_analytics IotTopicRule#iot_analytics}
        '''
        result = self._values.get("iot_analytics")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionIotAnalytics"], result)

    @builtins.property
    def iot_events(self) -> typing.Optional["IotTopicRuleErrorActionIotEvents"]:
        '''iot_events block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#iot_events IotTopicRule#iot_events}
        '''
        result = self._values.get("iot_events")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionIotEvents"], result)

    @builtins.property
    def kafka(self) -> typing.Optional["IotTopicRuleErrorActionKafka"]:
        '''kafka block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kafka IotTopicRule#kafka}
        '''
        result = self._values.get("kafka")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionKafka"], result)

    @builtins.property
    def kinesis(self) -> typing.Optional["IotTopicRuleErrorActionKinesis"]:
        '''kinesis block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#kinesis IotTopicRule#kinesis}
        '''
        result = self._values.get("kinesis")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionKinesis"], result)

    @builtins.property
    def lambda_(self) -> typing.Optional["IotTopicRuleErrorActionLambda"]:
        '''lambda block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#lambda IotTopicRule#lambda}
        '''
        result = self._values.get("lambda_")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionLambda"], result)

    @builtins.property
    def republish(self) -> typing.Optional["IotTopicRuleErrorActionRepublish"]:
        '''republish block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#republish IotTopicRule#republish}
        '''
        result = self._values.get("republish")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionRepublish"], result)

    @builtins.property
    def s3(self) -> typing.Optional["IotTopicRuleErrorActionS3"]:
        '''s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#s3 IotTopicRule#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionS3"], result)

    @builtins.property
    def sns(self) -> typing.Optional["IotTopicRuleErrorActionSns"]:
        '''sns block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sns IotTopicRule#sns}
        '''
        result = self._values.get("sns")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionSns"], result)

    @builtins.property
    def sqs(self) -> typing.Optional["IotTopicRuleErrorActionSqs"]:
        '''sqs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#sqs IotTopicRule#sqs}
        '''
        result = self._values.get("sqs")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionSqs"], result)

    @builtins.property
    def step_functions(self) -> typing.Optional["IotTopicRuleErrorActionStepFunctions"]:
        '''step_functions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#step_functions IotTopicRule#step_functions}
        '''
        result = self._values.get("step_functions")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionStepFunctions"], result)

    @builtins.property
    def timestream(self) -> typing.Optional["IotTopicRuleErrorActionTimestream"]:
        '''timestream block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestream IotTopicRule#timestream}
        '''
        result = self._values.get("timestream")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionTimestream"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchAlarm",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_name": "alarmName",
        "role_arn": "roleArn",
        "state_reason": "stateReason",
        "state_value": "stateValue",
    },
)
class IotTopicRuleErrorActionCloudwatchAlarm:
    def __init__(
        self,
        *,
        alarm_name: builtins.str,
        role_arn: builtins.str,
        state_reason: builtins.str,
        state_value: builtins.str,
    ) -> None:
        '''
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#alarm_name IotTopicRule#alarm_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_reason IotTopicRule#state_reason}.
        :param state_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_value IotTopicRule#state_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_name": alarm_name,
            "role_arn": role_arn,
            "state_reason": state_reason,
            "state_value": state_value,
        }

    @builtins.property
    def alarm_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#alarm_name IotTopicRule#alarm_name}.'''
        result = self._values.get("alarm_name")
        assert result is not None, "Required property 'alarm_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_reason(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_reason IotTopicRule#state_reason}.'''
        result = self._values.get("state_reason")
        assert result is not None, "Required property 'state_reason' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_value IotTopicRule#state_value}.'''
        result = self._values.get("state_value")
        assert result is not None, "Required property 'state_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionCloudwatchAlarm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionCloudwatchAlarmOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchAlarmOutputReference",
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
    @jsii.member(jsii_name="alarmNameInput")
    def alarm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alarmNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateReasonInput")
    def state_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateReasonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateValueInput")
    def state_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alarmName")
    def alarm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alarmName"))

    @alarm_name.setter
    def alarm_name(self, value: builtins.str) -> None:
        jsii.set(self, "alarmName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateReason")
    def state_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateReason"))

    @state_reason.setter
    def state_reason(self, value: builtins.str) -> None:
        jsii.set(self, "stateReason", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateValue")
    def state_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateValue"))

    @state_value.setter
    def state_value(self, value: builtins.str) -> None:
        jsii.set(self, "stateValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionCloudwatchAlarm]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchAlarm], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionCloudwatchAlarm],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchLogs",
    jsii_struct_bases=[],
    name_mapping={"log_group_name": "logGroupName", "role_arn": "roleArn"},
)
class IotTopicRuleErrorActionCloudwatchLogs:
    def __init__(self, *, log_group_name: builtins.str, role_arn: builtins.str) -> None:
        '''
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#log_group_name IotTopicRule#log_group_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_group_name": log_group_name,
            "role_arn": role_arn,
        }

    @builtins.property
    def log_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#log_group_name IotTopicRule#log_group_name}.'''
        result = self._values.get("log_group_name")
        assert result is not None, "Required property 'log_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionCloudwatchLogs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionCloudwatchLogsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchLogsOutputReference",
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
    @jsii.member(jsii_name="logGroupNameInput")
    def log_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logGroupName"))

    @log_group_name.setter
    def log_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "logGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionCloudwatchLogs]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchLogs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionCloudwatchLogs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchMetric",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "metric_namespace": "metricNamespace",
        "metric_unit": "metricUnit",
        "metric_value": "metricValue",
        "role_arn": "roleArn",
        "metric_timestamp": "metricTimestamp",
    },
)
class IotTopicRuleErrorActionCloudwatchMetric:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        metric_namespace: builtins.str,
        metric_unit: builtins.str,
        metric_value: builtins.str,
        role_arn: builtins.str,
        metric_timestamp: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_name IotTopicRule#metric_name}.
        :param metric_namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_namespace IotTopicRule#metric_namespace}.
        :param metric_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_unit IotTopicRule#metric_unit}.
        :param metric_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_value IotTopicRule#metric_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param metric_timestamp: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_timestamp IotTopicRule#metric_timestamp}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metric_name": metric_name,
            "metric_namespace": metric_namespace,
            "metric_unit": metric_unit,
            "metric_value": metric_value,
            "role_arn": role_arn,
        }
        if metric_timestamp is not None:
            self._values["metric_timestamp"] = metric_timestamp

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_name IotTopicRule#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_namespace IotTopicRule#metric_namespace}.'''
        result = self._values.get("metric_namespace")
        assert result is not None, "Required property 'metric_namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_unit IotTopicRule#metric_unit}.'''
        result = self._values.get("metric_unit")
        assert result is not None, "Required property 'metric_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_value IotTopicRule#metric_value}.'''
        result = self._values.get("metric_value")
        assert result is not None, "Required property 'metric_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metric_timestamp(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_timestamp IotTopicRule#metric_timestamp}.'''
        result = self._values.get("metric_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionCloudwatchMetric(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionCloudwatchMetricOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionCloudwatchMetricOutputReference",
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

    @jsii.member(jsii_name="resetMetricTimestamp")
    def reset_metric_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricTimestamp", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNamespaceInput")
    def metric_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNamespaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTimestampInput")
    def metric_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricTimestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricUnitInput")
    def metric_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricValueInput")
    def metric_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricNamespace")
    def metric_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricNamespace"))

    @metric_namespace.setter
    def metric_namespace(self, value: builtins.str) -> None:
        jsii.set(self, "metricNamespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricTimestamp")
    def metric_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricTimestamp"))

    @metric_timestamp.setter
    def metric_timestamp(self, value: builtins.str) -> None:
        jsii.set(self, "metricTimestamp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricUnit")
    def metric_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricUnit"))

    @metric_unit.setter
    def metric_unit(self, value: builtins.str) -> None:
        jsii.set(self, "metricUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricValue")
    def metric_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricValue"))

    @metric_value.setter
    def metric_value(self, value: builtins.str) -> None:
        jsii.set(self, "metricValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionCloudwatchMetric]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchMetric], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionCloudwatchMetric],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodb",
    jsii_struct_bases=[],
    name_mapping={
        "hash_key_field": "hashKeyField",
        "hash_key_value": "hashKeyValue",
        "role_arn": "roleArn",
        "table_name": "tableName",
        "hash_key_type": "hashKeyType",
        "operation": "operation",
        "payload_field": "payloadField",
        "range_key_field": "rangeKeyField",
        "range_key_type": "rangeKeyType",
        "range_key_value": "rangeKeyValue",
    },
)
class IotTopicRuleErrorActionDynamodb:
    def __init__(
        self,
        *,
        hash_key_field: builtins.str,
        hash_key_value: builtins.str,
        role_arn: builtins.str,
        table_name: builtins.str,
        hash_key_type: typing.Optional[builtins.str] = None,
        operation: typing.Optional[builtins.str] = None,
        payload_field: typing.Optional[builtins.str] = None,
        range_key_field: typing.Optional[builtins.str] = None,
        range_key_type: typing.Optional[builtins.str] = None,
        range_key_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hash_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_field IotTopicRule#hash_key_field}.
        :param hash_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_value IotTopicRule#hash_key_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param hash_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_type IotTopicRule#hash_key_type}.
        :param operation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#operation IotTopicRule#operation}.
        :param payload_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#payload_field IotTopicRule#payload_field}.
        :param range_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_field IotTopicRule#range_key_field}.
        :param range_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_type IotTopicRule#range_key_type}.
        :param range_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_value IotTopicRule#range_key_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hash_key_field": hash_key_field,
            "hash_key_value": hash_key_value,
            "role_arn": role_arn,
            "table_name": table_name,
        }
        if hash_key_type is not None:
            self._values["hash_key_type"] = hash_key_type
        if operation is not None:
            self._values["operation"] = operation
        if payload_field is not None:
            self._values["payload_field"] = payload_field
        if range_key_field is not None:
            self._values["range_key_field"] = range_key_field
        if range_key_type is not None:
            self._values["range_key_type"] = range_key_type
        if range_key_value is not None:
            self._values["range_key_value"] = range_key_value

    @builtins.property
    def hash_key_field(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_field IotTopicRule#hash_key_field}.'''
        result = self._values.get("hash_key_field")
        assert result is not None, "Required property 'hash_key_field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hash_key_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_value IotTopicRule#hash_key_value}.'''
        result = self._values.get("hash_key_value")
        assert result is not None, "Required property 'hash_key_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hash_key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_type IotTopicRule#hash_key_type}.'''
        result = self._values.get("hash_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#operation IotTopicRule#operation}.'''
        result = self._values.get("operation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload_field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#payload_field IotTopicRule#payload_field}.'''
        result = self._values.get("payload_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_field IotTopicRule#range_key_field}.'''
        result = self._values.get("range_key_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_type IotTopicRule#range_key_type}.'''
        result = self._values.get("range_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def range_key_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_value IotTopicRule#range_key_value}.'''
        result = self._values.get("range_key_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionDynamodb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionDynamodbOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodbOutputReference",
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

    @jsii.member(jsii_name="resetHashKeyType")
    def reset_hash_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashKeyType", []))

    @jsii.member(jsii_name="resetOperation")
    def reset_operation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperation", []))

    @jsii.member(jsii_name="resetPayloadField")
    def reset_payload_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayloadField", []))

    @jsii.member(jsii_name="resetRangeKeyField")
    def reset_range_key_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyField", []))

    @jsii.member(jsii_name="resetRangeKeyType")
    def reset_range_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyType", []))

    @jsii.member(jsii_name="resetRangeKeyValue")
    def reset_range_key_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKeyValue", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyFieldInput")
    def hash_key_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyTypeInput")
    def hash_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyValueInput")
    def hash_key_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operationInput")
    def operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFieldInput")
    def payload_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyFieldInput")
    def range_key_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyFieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyTypeInput")
    def range_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyValueInput")
    def range_key_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyField")
    def hash_key_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyField"))

    @hash_key_field.setter
    def hash_key_field(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyType")
    def hash_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyType"))

    @hash_key_type.setter
    def hash_key_type(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyValue")
    def hash_key_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKeyValue"))

    @hash_key_value.setter
    def hash_key_value(self, value: builtins.str) -> None:
        jsii.set(self, "hashKeyValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operation")
    def operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operation"))

    @operation.setter
    def operation(self, value: builtins.str) -> None:
        jsii.set(self, "operation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadField")
    def payload_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payloadField"))

    @payload_field.setter
    def payload_field(self, value: builtins.str) -> None:
        jsii.set(self, "payloadField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyField")
    def range_key_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyField"))

    @range_key_field.setter
    def range_key_field(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyType")
    def range_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyType"))

    @range_key_type.setter
    def range_key_type(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyValue")
    def range_key_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKeyValue"))

    @range_key_value.setter
    def range_key_value(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKeyValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionDynamodb]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionDynamodb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionDynamodb],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodbv2",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "put_item": "putItem"},
)
class IotTopicRuleErrorActionDynamodbv2:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        put_item: typing.Optional["IotTopicRuleErrorActionDynamodbv2PutItem"] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param put_item: put_item block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#put_item IotTopicRule#put_item}
        '''
        if isinstance(put_item, dict):
            put_item = IotTopicRuleErrorActionDynamodbv2PutItem(**put_item)
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if put_item is not None:
            self._values["put_item"] = put_item

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def put_item(self) -> typing.Optional["IotTopicRuleErrorActionDynamodbv2PutItem"]:
        '''put_item block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#put_item IotTopicRule#put_item}
        '''
        result = self._values.get("put_item")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionDynamodbv2PutItem"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionDynamodbv2(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionDynamodbv2OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodbv2OutputReference",
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

    @jsii.member(jsii_name="putPutItem")
    def put_put_item(self, *, table_name: builtins.str) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        '''
        value = IotTopicRuleErrorActionDynamodbv2PutItem(table_name=table_name)

        return typing.cast(None, jsii.invoke(self, "putPutItem", [value]))

    @jsii.member(jsii_name="resetPutItem")
    def reset_put_item(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPutItem", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="putItem")
    def put_item(self) -> "IotTopicRuleErrorActionDynamodbv2PutItemOutputReference":
        return typing.cast("IotTopicRuleErrorActionDynamodbv2PutItemOutputReference", jsii.get(self, "putItem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="putItemInput")
    def put_item_input(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionDynamodbv2PutItem"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionDynamodbv2PutItem"], jsii.get(self, "putItemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionDynamodbv2]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionDynamodbv2], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionDynamodbv2],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodbv2PutItem",
    jsii_struct_bases=[],
    name_mapping={"table_name": "tableName"},
)
class IotTopicRuleErrorActionDynamodbv2PutItem:
    def __init__(self, *, table_name: builtins.str) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "table_name": table_name,
        }

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionDynamodbv2PutItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionDynamodbv2PutItemOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionDynamodbv2PutItemOutputReference",
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
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionDynamodbv2PutItem]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionDynamodbv2PutItem], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionDynamodbv2PutItem],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionElasticsearch",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint": "endpoint",
        "id": "id",
        "index": "index",
        "role_arn": "roleArn",
        "type": "type",
    },
)
class IotTopicRuleErrorActionElasticsearch:
    def __init__(
        self,
        *,
        endpoint: builtins.str,
        id: builtins.str,
        index: builtins.str,
        role_arn: builtins.str,
        type: builtins.str,
    ) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#endpoint IotTopicRule#endpoint}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#index IotTopicRule#index}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#type IotTopicRule#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
            "id": id,
            "index": index,
            "role_arn": role_arn,
            "type": type,
        }

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#endpoint IotTopicRule#endpoint}.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#index IotTopicRule#index}.'''
        result = self._values.get("index")
        assert result is not None, "Required property 'index' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#type IotTopicRule#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionElasticsearch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionElasticsearchOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionElasticsearchOutputReference",
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
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexInput")
    def index_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="index")
    def index(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "index"))

    @index.setter
    def index(self, value: builtins.str) -> None:
        jsii.set(self, "index", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionElasticsearch]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionElasticsearch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionElasticsearch],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionFirehose",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_name": "deliveryStreamName",
        "role_arn": "roleArn",
        "separator": "separator",
    },
)
class IotTopicRuleErrorActionFirehose:
    def __init__(
        self,
        *,
        delivery_stream_name: builtins.str,
        role_arn: builtins.str,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delivery_stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#delivery_stream_name IotTopicRule#delivery_stream_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param separator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#separator IotTopicRule#separator}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "delivery_stream_name": delivery_stream_name,
            "role_arn": role_arn,
        }
        if separator is not None:
            self._values["separator"] = separator

    @builtins.property
    def delivery_stream_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#delivery_stream_name IotTopicRule#delivery_stream_name}.'''
        result = self._values.get("delivery_stream_name")
        assert result is not None, "Required property 'delivery_stream_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#separator IotTopicRule#separator}.'''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionFirehoseOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionFirehoseOutputReference",
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

    @jsii.member(jsii_name="resetSeparator")
    def reset_separator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeparator", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamNameInput")
    def delivery_stream_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separatorInput")
    def separator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "separatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @delivery_stream_name.setter
    def delivery_stream_name(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStreamName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        jsii.set(self, "separator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionFirehose]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionFirehose], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionFirehose],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionHttp",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "confirmation_url": "confirmationUrl",
        "http_header": "httpHeader",
    },
)
class IotTopicRuleErrorActionHttp:
    def __init__(
        self,
        *,
        url: builtins.str,
        confirmation_url: typing.Optional[builtins.str] = None,
        http_header: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleErrorActionHttpHttpHeader"]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#url IotTopicRule#url}.
        :param confirmation_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#confirmation_url IotTopicRule#confirmation_url}.
        :param http_header: http_header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http_header IotTopicRule#http_header}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if confirmation_url is not None:
            self._values["confirmation_url"] = confirmation_url
        if http_header is not None:
            self._values["http_header"] = http_header

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#url IotTopicRule#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def confirmation_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#confirmation_url IotTopicRule#confirmation_url}.'''
        result = self._values.get("confirmation_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_header(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleErrorActionHttpHttpHeader"]]]:
        '''http_header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http_header IotTopicRule#http_header}
        '''
        result = self._values.get("http_header")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleErrorActionHttpHttpHeader"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionHttp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionHttpHttpHeader",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class IotTopicRuleErrorActionHttpHttpHeader:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionHttpHttpHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionHttpHttpHeaderList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionHttpHttpHeaderList",
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
    ) -> "IotTopicRuleErrorActionHttpHttpHeaderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleErrorActionHttpHttpHeaderOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionHttpHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionHttpHttpHeader]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionHttpHttpHeader]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleErrorActionHttpHttpHeaderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionHttpHttpHeaderOutputReference",
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
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

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
    ) -> typing.Optional[typing.Union[IotTopicRuleErrorActionHttpHttpHeader, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleErrorActionHttpHttpHeader, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleErrorActionHttpHttpHeader, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleErrorActionHttpOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionHttpOutputReference",
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

    @jsii.member(jsii_name="putHttpHeader")
    def put_http_header(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleErrorActionHttpHttpHeader]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putHttpHeader", [value]))

    @jsii.member(jsii_name="resetConfirmationUrl")
    def reset_confirmation_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfirmationUrl", []))

    @jsii.member(jsii_name="resetHttpHeader")
    def reset_http_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpHeader", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeader")
    def http_header(self) -> IotTopicRuleErrorActionHttpHttpHeaderList:
        return typing.cast(IotTopicRuleErrorActionHttpHttpHeaderList, jsii.get(self, "httpHeader"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationUrlInput")
    def confirmation_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confirmationUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeaderInput")
    def http_header_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionHttpHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionHttpHttpHeader]]], jsii.get(self, "httpHeaderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationUrl")
    def confirmation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confirmationUrl"))

    @confirmation_url.setter
    def confirmation_url(self, value: builtins.str) -> None:
        jsii.set(self, "confirmationUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionHttp]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionHttp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionHttp],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionIotAnalytics",
    jsii_struct_bases=[],
    name_mapping={"channel_name": "channelName", "role_arn": "roleArn"},
)
class IotTopicRuleErrorActionIotAnalytics:
    def __init__(self, *, channel_name: builtins.str, role_arn: builtins.str) -> None:
        '''
        :param channel_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#channel_name IotTopicRule#channel_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel_name": channel_name,
            "role_arn": role_arn,
        }

    @builtins.property
    def channel_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#channel_name IotTopicRule#channel_name}.'''
        result = self._values.get("channel_name")
        assert result is not None, "Required property 'channel_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionIotAnalytics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionIotAnalyticsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionIotAnalyticsOutputReference",
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
    @jsii.member(jsii_name="channelNameInput")
    def channel_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelName"))

    @channel_name.setter
    def channel_name(self, value: builtins.str) -> None:
        jsii.set(self, "channelName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionIotAnalytics]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionIotAnalytics], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionIotAnalytics],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionIotEvents",
    jsii_struct_bases=[],
    name_mapping={
        "input_name": "inputName",
        "role_arn": "roleArn",
        "message_id": "messageId",
    },
)
class IotTopicRuleErrorActionIotEvents:
    def __init__(
        self,
        *,
        input_name: builtins.str,
        role_arn: builtins.str,
        message_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#input_name IotTopicRule#input_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param message_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_id IotTopicRule#message_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input_name": input_name,
            "role_arn": role_arn,
        }
        if message_id is not None:
            self._values["message_id"] = message_id

    @builtins.property
    def input_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#input_name IotTopicRule#input_name}.'''
        result = self._values.get("input_name")
        assert result is not None, "Required property 'input_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def message_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_id IotTopicRule#message_id}.'''
        result = self._values.get("message_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionIotEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionIotEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionIotEventsOutputReference",
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

    @jsii.member(jsii_name="resetMessageId")
    def reset_message_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputNameInput")
    def input_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageIdInput")
    def message_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputName"))

    @input_name.setter
    def input_name(self, value: builtins.str) -> None:
        jsii.set(self, "inputName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageId")
    def message_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageId"))

    @message_id.setter
    def message_id(self, value: builtins.str) -> None:
        jsii.set(self, "messageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionIotEvents]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionIotEvents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionIotEvents],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionKafka",
    jsii_struct_bases=[],
    name_mapping={
        "client_properties": "clientProperties",
        "destination_arn": "destinationArn",
        "topic": "topic",
        "key": "key",
        "partition": "partition",
    },
)
class IotTopicRuleErrorActionKafka:
    def __init__(
        self,
        *,
        client_properties: typing.Mapping[builtins.str, builtins.str],
        destination_arn: builtins.str,
        topic: builtins.str,
        key: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#client_properties IotTopicRule#client_properties}.
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#destination_arn IotTopicRule#destination_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param partition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition IotTopicRule#partition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_properties": client_properties,
            "destination_arn": destination_arn,
            "topic": topic,
        }
        if key is not None:
            self._values["key"] = key
        if partition is not None:
            self._values["partition"] = partition

    @builtins.property
    def client_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#client_properties IotTopicRule#client_properties}.'''
        result = self._values.get("client_properties")
        assert result is not None, "Required property 'client_properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#destination_arn IotTopicRule#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.'''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition IotTopicRule#partition}.'''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionKafka(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionKafkaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionKafkaOutputReference",
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

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientPropertiesInput")
    def client_properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "clientPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArnInput")
    def destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientProperties")
    def client_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "clientProperties"))

    @client_properties.setter
    def client_properties(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        jsii.set(self, "clientProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        jsii.set(self, "partition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        jsii.set(self, "topic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionKafka]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionKafka], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionKafka],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionKinesis",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "stream_name": "streamName",
        "partition_key": "partitionKey",
    },
)
class IotTopicRuleErrorActionKinesis:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        stream_name: builtins.str,
        partition_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#stream_name IotTopicRule#stream_name}.
        :param partition_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition_key IotTopicRule#partition_key}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "stream_name": stream_name,
        }
        if partition_key is not None:
            self._values["partition_key"] = partition_key

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#stream_name IotTopicRule#stream_name}.'''
        result = self._values.get("stream_name")
        assert result is not None, "Required property 'stream_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partition_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition_key IotTopicRule#partition_key}.'''
        result = self._values.get("partition_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionKinesis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionKinesisOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionKinesisOutputReference",
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

    @jsii.member(jsii_name="resetPartitionKey")
    def reset_partition_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKeyInput")
    def partition_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamNameInput")
    def stream_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKey")
    def partition_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partitionKey"))

    @partition_key.setter
    def partition_key(self, value: builtins.str) -> None:
        jsii.set(self, "partitionKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamName")
    def stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamName"))

    @stream_name.setter
    def stream_name(self, value: builtins.str) -> None:
        jsii.set(self, "streamName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionKinesis]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionKinesis], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionKinesis],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionLambda",
    jsii_struct_bases=[],
    name_mapping={"function_arn": "functionArn"},
)
class IotTopicRuleErrorActionLambda:
    def __init__(self, *, function_arn: builtins.str) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#function_arn IotTopicRule#function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
        }

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#function_arn IotTopicRule#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionLambda(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionLambdaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionLambdaOutputReference",
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
    @jsii.member(jsii_name="functionArnInput")
    def function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @function_arn.setter
    def function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "functionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionLambda]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionLambda], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionLambda],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleErrorActionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionOutputReference",
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

    @jsii.member(jsii_name="putCloudwatchAlarm")
    def put_cloudwatch_alarm(
        self,
        *,
        alarm_name: builtins.str,
        role_arn: builtins.str,
        state_reason: builtins.str,
        state_value: builtins.str,
    ) -> None:
        '''
        :param alarm_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#alarm_name IotTopicRule#alarm_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_reason: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_reason IotTopicRule#state_reason}.
        :param state_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_value IotTopicRule#state_value}.
        '''
        value = IotTopicRuleErrorActionCloudwatchAlarm(
            alarm_name=alarm_name,
            role_arn=role_arn,
            state_reason=state_reason,
            state_value=state_value,
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchAlarm", [value]))

    @jsii.member(jsii_name="putCloudwatchLogs")
    def put_cloudwatch_logs(
        self,
        *,
        log_group_name: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''
        :param log_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#log_group_name IotTopicRule#log_group_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        value = IotTopicRuleErrorActionCloudwatchLogs(
            log_group_name=log_group_name, role_arn=role_arn
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchLogs", [value]))

    @jsii.member(jsii_name="putCloudwatchMetric")
    def put_cloudwatch_metric(
        self,
        *,
        metric_name: builtins.str,
        metric_namespace: builtins.str,
        metric_unit: builtins.str,
        metric_value: builtins.str,
        role_arn: builtins.str,
        metric_timestamp: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_name IotTopicRule#metric_name}.
        :param metric_namespace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_namespace IotTopicRule#metric_namespace}.
        :param metric_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_unit IotTopicRule#metric_unit}.
        :param metric_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_value IotTopicRule#metric_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param metric_timestamp: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#metric_timestamp IotTopicRule#metric_timestamp}.
        '''
        value = IotTopicRuleErrorActionCloudwatchMetric(
            metric_name=metric_name,
            metric_namespace=metric_namespace,
            metric_unit=metric_unit,
            metric_value=metric_value,
            role_arn=role_arn,
            metric_timestamp=metric_timestamp,
        )

        return typing.cast(None, jsii.invoke(self, "putCloudwatchMetric", [value]))

    @jsii.member(jsii_name="putDynamodb")
    def put_dynamodb(
        self,
        *,
        hash_key_field: builtins.str,
        hash_key_value: builtins.str,
        role_arn: builtins.str,
        table_name: builtins.str,
        hash_key_type: typing.Optional[builtins.str] = None,
        operation: typing.Optional[builtins.str] = None,
        payload_field: typing.Optional[builtins.str] = None,
        range_key_field: typing.Optional[builtins.str] = None,
        range_key_type: typing.Optional[builtins.str] = None,
        range_key_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hash_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_field IotTopicRule#hash_key_field}.
        :param hash_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_value IotTopicRule#hash_key_value}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param hash_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#hash_key_type IotTopicRule#hash_key_type}.
        :param operation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#operation IotTopicRule#operation}.
        :param payload_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#payload_field IotTopicRule#payload_field}.
        :param range_key_field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_field IotTopicRule#range_key_field}.
        :param range_key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_type IotTopicRule#range_key_type}.
        :param range_key_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#range_key_value IotTopicRule#range_key_value}.
        '''
        value = IotTopicRuleErrorActionDynamodb(
            hash_key_field=hash_key_field,
            hash_key_value=hash_key_value,
            role_arn=role_arn,
            table_name=table_name,
            hash_key_type=hash_key_type,
            operation=operation,
            payload_field=payload_field,
            range_key_field=range_key_field,
            range_key_type=range_key_type,
            range_key_value=range_key_value,
        )

        return typing.cast(None, jsii.invoke(self, "putDynamodb", [value]))

    @jsii.member(jsii_name="putDynamodbv2")
    def put_dynamodbv2(
        self,
        *,
        role_arn: builtins.str,
        put_item: typing.Optional[IotTopicRuleErrorActionDynamodbv2PutItem] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param put_item: put_item block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#put_item IotTopicRule#put_item}
        '''
        value = IotTopicRuleErrorActionDynamodbv2(role_arn=role_arn, put_item=put_item)

        return typing.cast(None, jsii.invoke(self, "putDynamodbv2", [value]))

    @jsii.member(jsii_name="putElasticsearch")
    def put_elasticsearch(
        self,
        *,
        endpoint: builtins.str,
        id: builtins.str,
        index: builtins.str,
        role_arn: builtins.str,
        type: builtins.str,
    ) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#endpoint IotTopicRule#endpoint}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#id IotTopicRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#index IotTopicRule#index}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#type IotTopicRule#type}.
        '''
        value = IotTopicRuleErrorActionElasticsearch(
            endpoint=endpoint, id=id, index=index, role_arn=role_arn, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putElasticsearch", [value]))

    @jsii.member(jsii_name="putFirehose")
    def put_firehose(
        self,
        *,
        delivery_stream_name: builtins.str,
        role_arn: builtins.str,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delivery_stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#delivery_stream_name IotTopicRule#delivery_stream_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param separator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#separator IotTopicRule#separator}.
        '''
        value = IotTopicRuleErrorActionFirehose(
            delivery_stream_name=delivery_stream_name,
            role_arn=role_arn,
            separator=separator,
        )

        return typing.cast(None, jsii.invoke(self, "putFirehose", [value]))

    @jsii.member(jsii_name="putHttp")
    def put_http(
        self,
        *,
        url: builtins.str,
        confirmation_url: typing.Optional[builtins.str] = None,
        http_header: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleErrorActionHttpHttpHeader]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#url IotTopicRule#url}.
        :param confirmation_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#confirmation_url IotTopicRule#confirmation_url}.
        :param http_header: http_header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http_header IotTopicRule#http_header}
        '''
        value = IotTopicRuleErrorActionHttp(
            url=url, confirmation_url=confirmation_url, http_header=http_header
        )

        return typing.cast(None, jsii.invoke(self, "putHttp", [value]))

    @jsii.member(jsii_name="putIotAnalytics")
    def put_iot_analytics(
        self,
        *,
        channel_name: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''
        :param channel_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#channel_name IotTopicRule#channel_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        value = IotTopicRuleErrorActionIotAnalytics(
            channel_name=channel_name, role_arn=role_arn
        )

        return typing.cast(None, jsii.invoke(self, "putIotAnalytics", [value]))

    @jsii.member(jsii_name="putIotEvents")
    def put_iot_events(
        self,
        *,
        input_name: builtins.str,
        role_arn: builtins.str,
        message_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#input_name IotTopicRule#input_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param message_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_id IotTopicRule#message_id}.
        '''
        value = IotTopicRuleErrorActionIotEvents(
            input_name=input_name, role_arn=role_arn, message_id=message_id
        )

        return typing.cast(None, jsii.invoke(self, "putIotEvents", [value]))

    @jsii.member(jsii_name="putKafka")
    def put_kafka(
        self,
        *,
        client_properties: typing.Mapping[builtins.str, builtins.str],
        destination_arn: builtins.str,
        topic: builtins.str,
        key: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#client_properties IotTopicRule#client_properties}.
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#destination_arn IotTopicRule#destination_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param partition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition IotTopicRule#partition}.
        '''
        value = IotTopicRuleErrorActionKafka(
            client_properties=client_properties,
            destination_arn=destination_arn,
            topic=topic,
            key=key,
            partition=partition,
        )

        return typing.cast(None, jsii.invoke(self, "putKafka", [value]))

    @jsii.member(jsii_name="putKinesis")
    def put_kinesis(
        self,
        *,
        role_arn: builtins.str,
        stream_name: builtins.str,
        partition_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#stream_name IotTopicRule#stream_name}.
        :param partition_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition_key IotTopicRule#partition_key}.
        '''
        value = IotTopicRuleErrorActionKinesis(
            role_arn=role_arn, stream_name=stream_name, partition_key=partition_key
        )

        return typing.cast(None, jsii.invoke(self, "putKinesis", [value]))

    @jsii.member(jsii_name="putLambda")
    def put_lambda(self, *, function_arn: builtins.str) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#function_arn IotTopicRule#function_arn}.
        '''
        value = IotTopicRuleErrorActionLambda(function_arn=function_arn)

        return typing.cast(None, jsii.invoke(self, "putLambda", [value]))

    @jsii.member(jsii_name="putRepublish")
    def put_republish(
        self,
        *,
        role_arn: builtins.str,
        topic: builtins.str,
        qos: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param qos: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#qos IotTopicRule#qos}.
        '''
        value = IotTopicRuleErrorActionRepublish(
            role_arn=role_arn, topic=topic, qos=qos
        )

        return typing.cast(None, jsii.invoke(self, "putRepublish", [value]))

    @jsii.member(jsii_name="putS3")
    def put_s3(
        self,
        *,
        bucket_name: builtins.str,
        key: builtins.str,
        role_arn: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#bucket_name IotTopicRule#bucket_name}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param canned_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#canned_acl IotTopicRule#canned_acl}.
        '''
        value = IotTopicRuleErrorActionS3(
            bucket_name=bucket_name, key=key, role_arn=role_arn, canned_acl=canned_acl
        )

        return typing.cast(None, jsii.invoke(self, "putS3", [value]))

    @jsii.member(jsii_name="putSns")
    def put_sns(
        self,
        *,
        role_arn: builtins.str,
        target_arn: builtins.str,
        message_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#target_arn IotTopicRule#target_arn}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_format IotTopicRule#message_format}.
        '''
        value = IotTopicRuleErrorActionSns(
            role_arn=role_arn, target_arn=target_arn, message_format=message_format
        )

        return typing.cast(None, jsii.invoke(self, "putSns", [value]))

    @jsii.member(jsii_name="putSqs")
    def put_sqs(
        self,
        *,
        queue_url: builtins.str,
        role_arn: builtins.str,
        use_base64: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#queue_url IotTopicRule#queue_url}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param use_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#use_base64 IotTopicRule#use_base64}.
        '''
        value = IotTopicRuleErrorActionSqs(
            queue_url=queue_url, role_arn=role_arn, use_base64=use_base64
        )

        return typing.cast(None, jsii.invoke(self, "putSqs", [value]))

    @jsii.member(jsii_name="putStepFunctions")
    def put_step_functions(
        self,
        *,
        role_arn: builtins.str,
        state_machine_name: builtins.str,
        execution_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_machine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_machine_name IotTopicRule#state_machine_name}.
        :param execution_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#execution_name_prefix IotTopicRule#execution_name_prefix}.
        '''
        value = IotTopicRuleErrorActionStepFunctions(
            role_arn=role_arn,
            state_machine_name=state_machine_name,
            execution_name_prefix=execution_name_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putStepFunctions", [value]))

    @jsii.member(jsii_name="putTimestream")
    def put_timestream(
        self,
        *,
        database_name: builtins.str,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleErrorActionTimestreamDimension"]],
        role_arn: builtins.str,
        table_name: builtins.str,
        timestamp: typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"] = None,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#database_name IotTopicRule#database_name}.
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dimension IotTopicRule#dimension}
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param timestamp: timestamp block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestamp IotTopicRule#timestamp}
        '''
        value = IotTopicRuleErrorActionTimestream(
            database_name=database_name,
            dimension=dimension,
            role_arn=role_arn,
            table_name=table_name,
            timestamp=timestamp,
        )

        return typing.cast(None, jsii.invoke(self, "putTimestream", [value]))

    @jsii.member(jsii_name="resetCloudwatchAlarm")
    def reset_cloudwatch_alarm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchAlarm", []))

    @jsii.member(jsii_name="resetCloudwatchLogs")
    def reset_cloudwatch_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogs", []))

    @jsii.member(jsii_name="resetCloudwatchMetric")
    def reset_cloudwatch_metric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchMetric", []))

    @jsii.member(jsii_name="resetDynamodb")
    def reset_dynamodb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamodb", []))

    @jsii.member(jsii_name="resetDynamodbv2")
    def reset_dynamodbv2(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamodbv2", []))

    @jsii.member(jsii_name="resetElasticsearch")
    def reset_elasticsearch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearch", []))

    @jsii.member(jsii_name="resetFirehose")
    def reset_firehose(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirehose", []))

    @jsii.member(jsii_name="resetHttp")
    def reset_http(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttp", []))

    @jsii.member(jsii_name="resetIotAnalytics")
    def reset_iot_analytics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIotAnalytics", []))

    @jsii.member(jsii_name="resetIotEvents")
    def reset_iot_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIotEvents", []))

    @jsii.member(jsii_name="resetKafka")
    def reset_kafka(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKafka", []))

    @jsii.member(jsii_name="resetKinesis")
    def reset_kinesis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKinesis", []))

    @jsii.member(jsii_name="resetLambda")
    def reset_lambda(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambda", []))

    @jsii.member(jsii_name="resetRepublish")
    def reset_republish(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepublish", []))

    @jsii.member(jsii_name="resetS3")
    def reset_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3", []))

    @jsii.member(jsii_name="resetSns")
    def reset_sns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSns", []))

    @jsii.member(jsii_name="resetSqs")
    def reset_sqs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqs", []))

    @jsii.member(jsii_name="resetStepFunctions")
    def reset_step_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepFunctions", []))

    @jsii.member(jsii_name="resetTimestream")
    def reset_timestream(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimestream", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarm")
    def cloudwatch_alarm(self) -> IotTopicRuleErrorActionCloudwatchAlarmOutputReference:
        return typing.cast(IotTopicRuleErrorActionCloudwatchAlarmOutputReference, jsii.get(self, "cloudwatchAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogs")
    def cloudwatch_logs(self) -> IotTopicRuleErrorActionCloudwatchLogsOutputReference:
        return typing.cast(IotTopicRuleErrorActionCloudwatchLogsOutputReference, jsii.get(self, "cloudwatchLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchMetric")
    def cloudwatch_metric(
        self,
    ) -> IotTopicRuleErrorActionCloudwatchMetricOutputReference:
        return typing.cast(IotTopicRuleErrorActionCloudwatchMetricOutputReference, jsii.get(self, "cloudwatchMetric"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodb")
    def dynamodb(self) -> IotTopicRuleErrorActionDynamodbOutputReference:
        return typing.cast(IotTopicRuleErrorActionDynamodbOutputReference, jsii.get(self, "dynamodb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbv2")
    def dynamodbv2(self) -> IotTopicRuleErrorActionDynamodbv2OutputReference:
        return typing.cast(IotTopicRuleErrorActionDynamodbv2OutputReference, jsii.get(self, "dynamodbv2"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearch")
    def elasticsearch(self) -> IotTopicRuleErrorActionElasticsearchOutputReference:
        return typing.cast(IotTopicRuleErrorActionElasticsearchOutputReference, jsii.get(self, "elasticsearch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehose")
    def firehose(self) -> IotTopicRuleErrorActionFirehoseOutputReference:
        return typing.cast(IotTopicRuleErrorActionFirehoseOutputReference, jsii.get(self, "firehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="http")
    def http(self) -> IotTopicRuleErrorActionHttpOutputReference:
        return typing.cast(IotTopicRuleErrorActionHttpOutputReference, jsii.get(self, "http"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotAnalytics")
    def iot_analytics(self) -> IotTopicRuleErrorActionIotAnalyticsOutputReference:
        return typing.cast(IotTopicRuleErrorActionIotAnalyticsOutputReference, jsii.get(self, "iotAnalytics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotEvents")
    def iot_events(self) -> IotTopicRuleErrorActionIotEventsOutputReference:
        return typing.cast(IotTopicRuleErrorActionIotEventsOutputReference, jsii.get(self, "iotEvents"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafka")
    def kafka(self) -> IotTopicRuleErrorActionKafkaOutputReference:
        return typing.cast(IotTopicRuleErrorActionKafkaOutputReference, jsii.get(self, "kafka"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesis")
    def kinesis(self) -> IotTopicRuleErrorActionKinesisOutputReference:
        return typing.cast(IotTopicRuleErrorActionKinesisOutputReference, jsii.get(self, "kinesis"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> IotTopicRuleErrorActionLambdaOutputReference:
        return typing.cast(IotTopicRuleErrorActionLambdaOutputReference, jsii.get(self, "lambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="republish")
    def republish(self) -> "IotTopicRuleErrorActionRepublishOutputReference":
        return typing.cast("IotTopicRuleErrorActionRepublishOutputReference", jsii.get(self, "republish"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IotTopicRuleErrorActionS3OutputReference":
        return typing.cast("IotTopicRuleErrorActionS3OutputReference", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sns")
    def sns(self) -> "IotTopicRuleErrorActionSnsOutputReference":
        return typing.cast("IotTopicRuleErrorActionSnsOutputReference", jsii.get(self, "sns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqs")
    def sqs(self) -> "IotTopicRuleErrorActionSqsOutputReference":
        return typing.cast("IotTopicRuleErrorActionSqsOutputReference", jsii.get(self, "sqs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepFunctions")
    def step_functions(self) -> "IotTopicRuleErrorActionStepFunctionsOutputReference":
        return typing.cast("IotTopicRuleErrorActionStepFunctionsOutputReference", jsii.get(self, "stepFunctions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestream")
    def timestream(self) -> "IotTopicRuleErrorActionTimestreamOutputReference":
        return typing.cast("IotTopicRuleErrorActionTimestreamOutputReference", jsii.get(self, "timestream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarmInput")
    def cloudwatch_alarm_input(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionCloudwatchAlarm]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchAlarm], jsii.get(self, "cloudwatchAlarmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsInput")
    def cloudwatch_logs_input(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionCloudwatchLogs]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchLogs], jsii.get(self, "cloudwatchLogsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchMetricInput")
    def cloudwatch_metric_input(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionCloudwatchMetric]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionCloudwatchMetric], jsii.get(self, "cloudwatchMetricInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbInput")
    def dynamodb_input(self) -> typing.Optional[IotTopicRuleErrorActionDynamodb]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionDynamodb], jsii.get(self, "dynamodbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbv2Input")
    def dynamodbv2_input(self) -> typing.Optional[IotTopicRuleErrorActionDynamodbv2]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionDynamodbv2], jsii.get(self, "dynamodbv2Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchInput")
    def elasticsearch_input(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionElasticsearch]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionElasticsearch], jsii.get(self, "elasticsearchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firehoseInput")
    def firehose_input(self) -> typing.Optional[IotTopicRuleErrorActionFirehose]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionFirehose], jsii.get(self, "firehoseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpInput")
    def http_input(self) -> typing.Optional[IotTopicRuleErrorActionHttp]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionHttp], jsii.get(self, "httpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotAnalyticsInput")
    def iot_analytics_input(
        self,
    ) -> typing.Optional[IotTopicRuleErrorActionIotAnalytics]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionIotAnalytics], jsii.get(self, "iotAnalyticsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iotEventsInput")
    def iot_events_input(self) -> typing.Optional[IotTopicRuleErrorActionIotEvents]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionIotEvents], jsii.get(self, "iotEventsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaInput")
    def kafka_input(self) -> typing.Optional[IotTopicRuleErrorActionKafka]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionKafka], jsii.get(self, "kafkaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisInput")
    def kinesis_input(self) -> typing.Optional[IotTopicRuleErrorActionKinesis]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionKinesis], jsii.get(self, "kinesisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaInput")
    def lambda_input(self) -> typing.Optional[IotTopicRuleErrorActionLambda]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionLambda], jsii.get(self, "lambdaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="republishInput")
    def republish_input(self) -> typing.Optional["IotTopicRuleErrorActionRepublish"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionRepublish"], jsii.get(self, "republishInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Input")
    def s3_input(self) -> typing.Optional["IotTopicRuleErrorActionS3"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionS3"], jsii.get(self, "s3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsInput")
    def sns_input(self) -> typing.Optional["IotTopicRuleErrorActionSns"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionSns"], jsii.get(self, "snsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsInput")
    def sqs_input(self) -> typing.Optional["IotTopicRuleErrorActionSqs"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionSqs"], jsii.get(self, "sqsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stepFunctionsInput")
    def step_functions_input(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionStepFunctions"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionStepFunctions"], jsii.get(self, "stepFunctionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestreamInput")
    def timestream_input(self) -> typing.Optional["IotTopicRuleErrorActionTimestream"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionTimestream"], jsii.get(self, "timestreamInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorAction]:
        return typing.cast(typing.Optional[IotTopicRuleErrorAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[IotTopicRuleErrorAction]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionRepublish",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "topic": "topic", "qos": "qos"},
)
class IotTopicRuleErrorActionRepublish:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        topic: builtins.str,
        qos: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param qos: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#qos IotTopicRule#qos}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "topic": topic,
        }
        if qos is not None:
            self._values["qos"] = qos

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.'''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def qos(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#qos IotTopicRule#qos}.'''
        result = self._values.get("qos")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionRepublish(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionRepublishOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionRepublishOutputReference",
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

    @jsii.member(jsii_name="resetQos")
    def reset_qos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQos", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qosInput")
    def qos_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "qosInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qos")
    def qos(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "qos"))

    @qos.setter
    def qos(self, value: jsii.Number) -> None:
        jsii.set(self, "qos", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        jsii.set(self, "topic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionRepublish]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionRepublish], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionRepublish],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionS3",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "key": "key",
        "role_arn": "roleArn",
        "canned_acl": "cannedAcl",
    },
)
class IotTopicRuleErrorActionS3:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        key: builtins.str,
        role_arn: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#bucket_name IotTopicRule#bucket_name}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param canned_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#canned_acl IotTopicRule#canned_acl}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "key": key,
            "role_arn": role_arn,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#bucket_name IotTopicRule#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#canned_acl IotTopicRule#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionS3OutputReference",
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

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        jsii.set(self, "cannedAcl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionS3]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[IotTopicRuleErrorActionS3]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionSns",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "target_arn": "targetArn",
        "message_format": "messageFormat",
    },
)
class IotTopicRuleErrorActionSns:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        target_arn: builtins.str,
        message_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#target_arn IotTopicRule#target_arn}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_format IotTopicRule#message_format}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "target_arn": target_arn,
        }
        if message_format is not None:
            self._values["message_format"] = message_format

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#target_arn IotTopicRule#target_arn}.'''
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def message_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_format IotTopicRule#message_format}.'''
        result = self._values.get("message_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionSns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionSnsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionSnsOutputReference",
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

    @jsii.member(jsii_name="resetMessageFormat")
    def reset_message_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFormat", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormatInput")
    def message_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArnInput")
    def target_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormat")
    def message_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFormat"))

    @message_format.setter
    def message_format(self, value: builtins.str) -> None:
        jsii.set(self, "messageFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @target_arn.setter
    def target_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionSns]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionSns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionSns],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionSqs",
    jsii_struct_bases=[],
    name_mapping={
        "queue_url": "queueUrl",
        "role_arn": "roleArn",
        "use_base64": "useBase64",
    },
)
class IotTopicRuleErrorActionSqs:
    def __init__(
        self,
        *,
        queue_url: builtins.str,
        role_arn: builtins.str,
        use_base64: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#queue_url IotTopicRule#queue_url}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param use_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#use_base64 IotTopicRule#use_base64}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "queue_url": queue_url,
            "role_arn": role_arn,
            "use_base64": use_base64,
        }

    @builtins.property
    def queue_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#queue_url IotTopicRule#queue_url}.'''
        result = self._values.get("queue_url")
        assert result is not None, "Required property 'queue_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def use_base64(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#use_base64 IotTopicRule#use_base64}.'''
        result = self._values.get("use_base64")
        assert result is not None, "Required property 'use_base64' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionSqsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionSqsOutputReference",
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
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBase64Input")
    def use_base64_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useBase64Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        jsii.set(self, "queueUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBase64")
    def use_base64(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useBase64"))

    @use_base64.setter
    def use_base64(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "useBase64", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionSqs]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionSqs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionSqs],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionStepFunctions",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "state_machine_name": "stateMachineName",
        "execution_name_prefix": "executionNamePrefix",
    },
)
class IotTopicRuleErrorActionStepFunctions:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        state_machine_name: builtins.str,
        execution_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_machine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_machine_name IotTopicRule#state_machine_name}.
        :param execution_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#execution_name_prefix IotTopicRule#execution_name_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "state_machine_name": state_machine_name,
        }
        if execution_name_prefix is not None:
            self._values["execution_name_prefix"] = execution_name_prefix

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_machine_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_machine_name IotTopicRule#state_machine_name}.'''
        result = self._values.get("state_machine_name")
        assert result is not None, "Required property 'state_machine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#execution_name_prefix IotTopicRule#execution_name_prefix}.'''
        result = self._values.get("execution_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionStepFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionStepFunctionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionStepFunctionsOutputReference",
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

    @jsii.member(jsii_name="resetExecutionNamePrefix")
    def reset_execution_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionNamePrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionNamePrefixInput")
    def execution_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionNamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineNameInput")
    def state_machine_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMachineNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionNamePrefix")
    def execution_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionNamePrefix"))

    @execution_name_prefix.setter
    def execution_name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "executionNamePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateMachineName"))

    @state_machine_name.setter
    def state_machine_name(self, value: builtins.str) -> None:
        jsii.set(self, "stateMachineName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionStepFunctions]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionStepFunctions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionStepFunctions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestream",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "dimension": "dimension",
        "role_arn": "roleArn",
        "table_name": "tableName",
        "timestamp": "timestamp",
    },
)
class IotTopicRuleErrorActionTimestream:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleErrorActionTimestreamDimension"]],
        role_arn: builtins.str,
        table_name: builtins.str,
        timestamp: typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"] = None,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#database_name IotTopicRule#database_name}.
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dimension IotTopicRule#dimension}
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param timestamp: timestamp block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestamp IotTopicRule#timestamp}
        '''
        if isinstance(timestamp, dict):
            timestamp = IotTopicRuleErrorActionTimestreamTimestamp(**timestamp)
        self._values: typing.Dict[str, typing.Any] = {
            "database_name": database_name,
            "dimension": dimension,
            "role_arn": role_arn,
            "table_name": table_name,
        }
        if timestamp is not None:
            self._values["timestamp"] = timestamp

    @builtins.property
    def database_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#database_name IotTopicRule#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimension(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleErrorActionTimestreamDimension"]]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dimension IotTopicRule#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleErrorActionTimestreamDimension"]], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"]:
        '''timestamp block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestamp IotTopicRule#timestamp}
        '''
        result = self._values.get("timestamp")
        return typing.cast(typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionTimestream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamDimension",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class IotTopicRuleErrorActionTimestreamDimension:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionTimestreamDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionTimestreamDimensionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamDimensionList",
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
    ) -> "IotTopicRuleErrorActionTimestreamDimensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleErrorActionTimestreamDimensionOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionTimestreamDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionTimestreamDimension]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionTimestreamDimension]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleErrorActionTimestreamDimensionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamDimensionOutputReference",
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
    ) -> typing.Optional[typing.Union[IotTopicRuleErrorActionTimestreamDimension, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleErrorActionTimestreamDimension, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleErrorActionTimestreamDimension, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleErrorActionTimestreamOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamOutputReference",
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

    @jsii.member(jsii_name="putDimension")
    def put_dimension(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleErrorActionTimestreamDimension]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putDimension", [value]))

    @jsii.member(jsii_name="putTimestamp")
    def put_timestamp(self, *, unit: builtins.str, value: builtins.str) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        value_ = IotTopicRuleErrorActionTimestreamTimestamp(unit=unit, value=value)

        return typing.cast(None, jsii.invoke(self, "putTimestamp", [value_]))

    @jsii.member(jsii_name="resetTimestamp")
    def reset_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimestamp", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(self) -> IotTopicRuleErrorActionTimestreamDimensionList:
        return typing.cast(IotTopicRuleErrorActionTimestreamDimensionList, jsii.get(self, "dimension"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> "IotTopicRuleErrorActionTimestreamTimestampOutputReference":
        return typing.cast("IotTopicRuleErrorActionTimestreamTimestampOutputReference", jsii.get(self, "timestamp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionTimestreamDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleErrorActionTimestreamDimension]]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestampInput")
    def timestamp_input(
        self,
    ) -> typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"]:
        return typing.cast(typing.Optional["IotTopicRuleErrorActionTimestreamTimestamp"], jsii.get(self, "timestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleErrorActionTimestream]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionTimestream], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionTimestream],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamTimestamp",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class IotTopicRuleErrorActionTimestreamTimestamp:
    def __init__(self, *, unit: builtins.str, value: builtins.str) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleErrorActionTimestreamTimestamp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleErrorActionTimestreamTimestampOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleErrorActionTimestreamTimestampOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

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
    ) -> typing.Optional[IotTopicRuleErrorActionTimestreamTimestamp]:
        return typing.cast(typing.Optional[IotTopicRuleErrorActionTimestreamTimestamp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleErrorActionTimestreamTimestamp],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleFirehose",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_name": "deliveryStreamName",
        "role_arn": "roleArn",
        "separator": "separator",
    },
)
class IotTopicRuleFirehose:
    def __init__(
        self,
        *,
        delivery_stream_name: builtins.str,
        role_arn: builtins.str,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delivery_stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#delivery_stream_name IotTopicRule#delivery_stream_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param separator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#separator IotTopicRule#separator}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "delivery_stream_name": delivery_stream_name,
            "role_arn": role_arn,
        }
        if separator is not None:
            self._values["separator"] = separator

    @builtins.property
    def delivery_stream_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#delivery_stream_name IotTopicRule#delivery_stream_name}.'''
        result = self._values.get("delivery_stream_name")
        assert result is not None, "Required property 'delivery_stream_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#separator IotTopicRule#separator}.'''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleFirehose(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleFirehoseList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleFirehoseList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleFirehoseOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleFirehoseOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleFirehose]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleFirehose]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleFirehose]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleFirehoseOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleFirehoseOutputReference",
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

    @jsii.member(jsii_name="resetSeparator")
    def reset_separator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeparator", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamNameInput")
    def delivery_stream_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separatorInput")
    def separator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "separatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @delivery_stream_name.setter
    def delivery_stream_name(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryStreamName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        jsii.set(self, "separator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleFirehose, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleFirehose, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleFirehose, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttp",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "confirmation_url": "confirmationUrl",
        "http_header": "httpHeader",
    },
)
class IotTopicRuleHttp:
    def __init__(
        self,
        *,
        url: builtins.str,
        confirmation_url: typing.Optional[builtins.str] = None,
        http_header: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleHttpHttpHeader"]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#url IotTopicRule#url}.
        :param confirmation_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#confirmation_url IotTopicRule#confirmation_url}.
        :param http_header: http_header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http_header IotTopicRule#http_header}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if confirmation_url is not None:
            self._values["confirmation_url"] = confirmation_url
        if http_header is not None:
            self._values["http_header"] = http_header

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#url IotTopicRule#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def confirmation_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#confirmation_url IotTopicRule#confirmation_url}.'''
        result = self._values.get("confirmation_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_header(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttpHttpHeader"]]]:
        '''http_header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#http_header IotTopicRule#http_header}
        '''
        result = self._values.get("http_header")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleHttpHttpHeader"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleHttp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttpHttpHeader",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class IotTopicRuleHttpHttpHeader:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleHttpHttpHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleHttpHttpHeaderList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttpHttpHeaderList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleHttpHttpHeaderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleHttpHttpHeaderOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttpHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttpHttpHeader]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttpHttpHeader]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleHttpHttpHeaderOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttpHttpHeaderOutputReference",
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
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

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
    ) -> typing.Optional[typing.Union[IotTopicRuleHttpHttpHeader, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleHttpHttpHeader, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleHttpHttpHeader, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleHttpList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttpList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleHttpOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleHttpOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttp]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttp]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttp]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleHttpOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleHttpOutputReference",
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

    @jsii.member(jsii_name="putHttpHeader")
    def put_http_header(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleHttpHttpHeader]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putHttpHeader", [value]))

    @jsii.member(jsii_name="resetConfirmationUrl")
    def reset_confirmation_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfirmationUrl", []))

    @jsii.member(jsii_name="resetHttpHeader")
    def reset_http_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpHeader", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeader")
    def http_header(self) -> IotTopicRuleHttpHttpHeaderList:
        return typing.cast(IotTopicRuleHttpHttpHeaderList, jsii.get(self, "httpHeader"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationUrlInput")
    def confirmation_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confirmationUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeaderInput")
    def http_header_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttpHttpHeader]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleHttpHttpHeader]]], jsii.get(self, "httpHeaderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confirmationUrl")
    def confirmation_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confirmationUrl"))

    @confirmation_url.setter
    def confirmation_url(self, value: builtins.str) -> None:
        jsii.set(self, "confirmationUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleHttp, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleHttp, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleHttp, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotAnalytics",
    jsii_struct_bases=[],
    name_mapping={"channel_name": "channelName", "role_arn": "roleArn"},
)
class IotTopicRuleIotAnalytics:
    def __init__(self, *, channel_name: builtins.str, role_arn: builtins.str) -> None:
        '''
        :param channel_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#channel_name IotTopicRule#channel_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel_name": channel_name,
            "role_arn": role_arn,
        }

    @builtins.property
    def channel_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#channel_name IotTopicRule#channel_name}.'''
        result = self._values.get("channel_name")
        assert result is not None, "Required property 'channel_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleIotAnalytics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleIotAnalyticsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotAnalyticsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleIotAnalyticsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleIotAnalyticsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotAnalytics]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotAnalytics]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotAnalytics]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleIotAnalyticsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotAnalyticsOutputReference",
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
    @jsii.member(jsii_name="channelNameInput")
    def channel_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelName"))

    @channel_name.setter
    def channel_name(self, value: builtins.str) -> None:
        jsii.set(self, "channelName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleIotAnalytics, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleIotAnalytics, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleIotAnalytics, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotEvents",
    jsii_struct_bases=[],
    name_mapping={
        "input_name": "inputName",
        "role_arn": "roleArn",
        "message_id": "messageId",
    },
)
class IotTopicRuleIotEvents:
    def __init__(
        self,
        *,
        input_name: builtins.str,
        role_arn: builtins.str,
        message_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#input_name IotTopicRule#input_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param message_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_id IotTopicRule#message_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input_name": input_name,
            "role_arn": role_arn,
        }
        if message_id is not None:
            self._values["message_id"] = message_id

    @builtins.property
    def input_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#input_name IotTopicRule#input_name}.'''
        result = self._values.get("input_name")
        assert result is not None, "Required property 'input_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def message_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_id IotTopicRule#message_id}.'''
        result = self._values.get("message_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleIotEvents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleIotEventsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotEventsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleIotEventsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleIotEventsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotEvents]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotEvents]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleIotEvents]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleIotEventsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleIotEventsOutputReference",
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

    @jsii.member(jsii_name="resetMessageId")
    def reset_message_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputNameInput")
    def input_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageIdInput")
    def message_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inputName"))

    @input_name.setter
    def input_name(self, value: builtins.str) -> None:
        jsii.set(self, "inputName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageId")
    def message_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageId"))

    @message_id.setter
    def message_id(self, value: builtins.str) -> None:
        jsii.set(self, "messageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleIotEvents, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleIotEvents, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleIotEvents, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKafka",
    jsii_struct_bases=[],
    name_mapping={
        "client_properties": "clientProperties",
        "destination_arn": "destinationArn",
        "topic": "topic",
        "key": "key",
        "partition": "partition",
    },
)
class IotTopicRuleKafka:
    def __init__(
        self,
        *,
        client_properties: typing.Mapping[builtins.str, builtins.str],
        destination_arn: builtins.str,
        topic: builtins.str,
        key: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_properties: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#client_properties IotTopicRule#client_properties}.
        :param destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#destination_arn IotTopicRule#destination_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param partition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition IotTopicRule#partition}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_properties": client_properties,
            "destination_arn": destination_arn,
            "topic": topic,
        }
        if key is not None:
            self._values["key"] = key
        if partition is not None:
            self._values["partition"] = partition

    @builtins.property
    def client_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#client_properties IotTopicRule#client_properties}.'''
        result = self._values.get("client_properties")
        assert result is not None, "Required property 'client_properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def destination_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#destination_arn IotTopicRule#destination_arn}.'''
        result = self._values.get("destination_arn")
        assert result is not None, "Required property 'destination_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.'''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition IotTopicRule#partition}.'''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleKafka(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleKafkaList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKafkaList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleKafkaOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleKafkaOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKafka]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKafka]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKafka]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleKafkaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKafkaOutputReference",
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

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientPropertiesInput")
    def client_properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "clientPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArnInput")
    def destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientProperties")
    def client_properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "clientProperties"))

    @client_properties.setter
    def client_properties(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        jsii.set(self, "clientProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationArn")
    def destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationArn"))

    @destination_arn.setter
    def destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "destinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        jsii.set(self, "partition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        jsii.set(self, "topic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleKafka, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleKafka, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleKafka, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKinesis",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "stream_name": "streamName",
        "partition_key": "partitionKey",
    },
)
class IotTopicRuleKinesis:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        stream_name: builtins.str,
        partition_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param stream_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#stream_name IotTopicRule#stream_name}.
        :param partition_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition_key IotTopicRule#partition_key}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "stream_name": stream_name,
        }
        if partition_key is not None:
            self._values["partition_key"] = partition_key

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#stream_name IotTopicRule#stream_name}.'''
        result = self._values.get("stream_name")
        assert result is not None, "Required property 'stream_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def partition_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#partition_key IotTopicRule#partition_key}.'''
        result = self._values.get("partition_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleKinesis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleKinesisList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKinesisList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleKinesisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleKinesisOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKinesis]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKinesis]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleKinesis]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleKinesisOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleKinesisOutputReference",
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

    @jsii.member(jsii_name="resetPartitionKey")
    def reset_partition_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKeyInput")
    def partition_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamNameInput")
    def stream_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionKey")
    def partition_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partitionKey"))

    @partition_key.setter
    def partition_key(self, value: builtins.str) -> None:
        jsii.set(self, "partitionKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamName")
    def stream_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamName"))

    @stream_name.setter
    def stream_name(self, value: builtins.str) -> None:
        jsii.set(self, "streamName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleKinesis, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleKinesis, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleKinesis, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleLambda",
    jsii_struct_bases=[],
    name_mapping={"function_arn": "functionArn"},
)
class IotTopicRuleLambda:
    def __init__(self, *, function_arn: builtins.str) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#function_arn IotTopicRule#function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
        }

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#function_arn IotTopicRule#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleLambda(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleLambdaList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleLambdaList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleLambdaOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleLambdaOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleLambda]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleLambda]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleLambda]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleLambdaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleLambdaOutputReference",
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
    @jsii.member(jsii_name="functionArnInput")
    def function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @function_arn.setter
    def function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "functionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleLambda, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleLambda, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleLambda, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleRepublish",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "topic": "topic", "qos": "qos"},
)
class IotTopicRuleRepublish:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        topic: builtins.str,
        qos: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.
        :param qos: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#qos IotTopicRule#qos}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "topic": topic,
        }
        if qos is not None:
            self._values["qos"] = qos

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#topic IotTopicRule#topic}.'''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def qos(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#qos IotTopicRule#qos}.'''
        result = self._values.get("qos")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleRepublish(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleRepublishList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleRepublishList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleRepublishOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleRepublishOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleRepublish]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleRepublish]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleRepublish]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleRepublishOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleRepublishOutputReference",
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

    @jsii.member(jsii_name="resetQos")
    def reset_qos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQos", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qosInput")
    def qos_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "qosInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="qos")
    def qos(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "qos"))

    @qos.setter
    def qos(self, value: jsii.Number) -> None:
        jsii.set(self, "qos", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        jsii.set(self, "topic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleRepublish, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleRepublish, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleRepublish, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleS3",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "key": "key",
        "role_arn": "roleArn",
        "canned_acl": "cannedAcl",
    },
)
class IotTopicRuleS3:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        key: builtins.str,
        role_arn: builtins.str,
        canned_acl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#bucket_name IotTopicRule#bucket_name}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param canned_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#canned_acl IotTopicRule#canned_acl}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "key": key,
            "role_arn": role_arn,
        }
        if canned_acl is not None:
            self._values["canned_acl"] = canned_acl

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#bucket_name IotTopicRule#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#key IotTopicRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canned_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#canned_acl IotTopicRule#canned_acl}.'''
        result = self._values.get("canned_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleS3List(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleS3List",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleS3OutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleS3OutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleS3]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleS3]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleS3]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleS3OutputReference",
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

    @jsii.member(jsii_name="resetCannedAcl")
    def reset_canned_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCannedAcl", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cannedAclInput")
    def canned_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cannedAclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cannedAcl")
    def canned_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cannedAcl"))

    @canned_acl.setter
    def canned_acl(self, value: builtins.str) -> None:
        jsii.set(self, "cannedAcl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleS3, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleS3, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleS3, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSns",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "target_arn": "targetArn",
        "message_format": "messageFormat",
    },
)
class IotTopicRuleSns:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        target_arn: builtins.str,
        message_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param target_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#target_arn IotTopicRule#target_arn}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_format IotTopicRule#message_format}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "target_arn": target_arn,
        }
        if message_format is not None:
            self._values["message_format"] = message_format

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#target_arn IotTopicRule#target_arn}.'''
        result = self._values.get("target_arn")
        assert result is not None, "Required property 'target_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def message_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#message_format IotTopicRule#message_format}.'''
        result = self._values.get("message_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleSns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleSnsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSnsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleSnsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleSnsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSns]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSns]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSns]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleSnsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSnsOutputReference",
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

    @jsii.member(jsii_name="resetMessageFormat")
    def reset_message_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFormat", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormatInput")
    def message_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArnInput")
    def target_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormat")
    def message_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFormat"))

    @message_format.setter
    def message_format(self, value: builtins.str) -> None:
        jsii.set(self, "messageFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @target_arn.setter
    def target_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleSns, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleSns, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleSns, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSqs",
    jsii_struct_bases=[],
    name_mapping={
        "queue_url": "queueUrl",
        "role_arn": "roleArn",
        "use_base64": "useBase64",
    },
)
class IotTopicRuleSqs:
    def __init__(
        self,
        *,
        queue_url: builtins.str,
        role_arn: builtins.str,
        use_base64: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param queue_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#queue_url IotTopicRule#queue_url}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param use_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#use_base64 IotTopicRule#use_base64}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "queue_url": queue_url,
            "role_arn": role_arn,
            "use_base64": use_base64,
        }

    @builtins.property
    def queue_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#queue_url IotTopicRule#queue_url}.'''
        result = self._values.get("queue_url")
        assert result is not None, "Required property 'queue_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def use_base64(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#use_base64 IotTopicRule#use_base64}.'''
        result = self._values.get("use_base64")
        assert result is not None, "Required property 'use_base64' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleSqs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleSqsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSqsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleSqsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleSqsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSqs]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSqs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleSqs]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleSqsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleSqsOutputReference",
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
    @jsii.member(jsii_name="queueUrlInput")
    def queue_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queueUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBase64Input")
    def use_base64_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useBase64Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queueUrl")
    def queue_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queueUrl"))

    @queue_url.setter
    def queue_url(self, value: builtins.str) -> None:
        jsii.set(self, "queueUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBase64")
    def use_base64(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useBase64"))

    @use_base64.setter
    def use_base64(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "useBase64", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleSqs, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleSqs, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleSqs, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleStepFunctions",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "state_machine_name": "stateMachineName",
        "execution_name_prefix": "executionNamePrefix",
    },
)
class IotTopicRuleStepFunctions:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        state_machine_name: builtins.str,
        execution_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param state_machine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_machine_name IotTopicRule#state_machine_name}.
        :param execution_name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#execution_name_prefix IotTopicRule#execution_name_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "state_machine_name": state_machine_name,
        }
        if execution_name_prefix is not None:
            self._values["execution_name_prefix"] = execution_name_prefix

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def state_machine_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#state_machine_name IotTopicRule#state_machine_name}.'''
        result = self._values.get("state_machine_name")
        assert result is not None, "Required property 'state_machine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#execution_name_prefix IotTopicRule#execution_name_prefix}.'''
        result = self._values.get("execution_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleStepFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleStepFunctionsList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleStepFunctionsList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleStepFunctionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleStepFunctionsOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleStepFunctions]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleStepFunctions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleStepFunctions]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleStepFunctionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleStepFunctionsOutputReference",
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

    @jsii.member(jsii_name="resetExecutionNamePrefix")
    def reset_execution_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionNamePrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionNamePrefixInput")
    def execution_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionNamePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineNameInput")
    def state_machine_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMachineNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionNamePrefix")
    def execution_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionNamePrefix"))

    @execution_name_prefix.setter
    def execution_name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "executionNamePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateMachineName"))

    @state_machine_name.setter
    def state_machine_name(self, value: builtins.str) -> None:
        jsii.set(self, "stateMachineName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleStepFunctions, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleStepFunctions, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleStepFunctions, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestream",
    jsii_struct_bases=[],
    name_mapping={
        "database_name": "databaseName",
        "dimension": "dimension",
        "role_arn": "roleArn",
        "table_name": "tableName",
        "timestamp": "timestamp",
    },
)
class IotTopicRuleTimestream:
    def __init__(
        self,
        *,
        database_name: builtins.str,
        dimension: typing.Union[cdktf.IResolvable, typing.Sequence["IotTopicRuleTimestreamDimension"]],
        role_arn: builtins.str,
        table_name: builtins.str,
        timestamp: typing.Optional["IotTopicRuleTimestreamTimestamp"] = None,
    ) -> None:
        '''
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#database_name IotTopicRule#database_name}.
        :param dimension: dimension block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dimension IotTopicRule#dimension}
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.
        :param timestamp: timestamp block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestamp IotTopicRule#timestamp}
        '''
        if isinstance(timestamp, dict):
            timestamp = IotTopicRuleTimestreamTimestamp(**timestamp)
        self._values: typing.Dict[str, typing.Any] = {
            "database_name": database_name,
            "dimension": dimension,
            "role_arn": role_arn,
            "table_name": table_name,
        }
        if timestamp is not None:
            self._values["timestamp"] = timestamp

    @builtins.property
    def database_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#database_name IotTopicRule#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimension(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestreamDimension"]]:
        '''dimension block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#dimension IotTopicRule#dimension}
        '''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["IotTopicRuleTimestreamDimension"]], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#role_arn IotTopicRule#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#table_name IotTopicRule#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timestamp(self) -> typing.Optional["IotTopicRuleTimestreamTimestamp"]:
        '''timestamp block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#timestamp IotTopicRule#timestamp}
        '''
        result = self._values.get("timestamp")
        return typing.cast(typing.Optional["IotTopicRuleTimestreamTimestamp"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleTimestream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamDimension",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class IotTopicRuleTimestreamDimension:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#name IotTopicRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleTimestreamDimension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleTimestreamDimensionList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamDimensionList",
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
    ) -> "IotTopicRuleTimestreamDimensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleTimestreamDimensionOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestreamDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestreamDimension]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestreamDimension]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleTimestreamDimensionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamDimensionOutputReference",
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
    ) -> typing.Optional[typing.Union[IotTopicRuleTimestreamDimension, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleTimestreamDimension, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleTimestreamDimension, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleTimestreamList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamList",
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
    def get(self, index: jsii.Number) -> "IotTopicRuleTimestreamOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("IotTopicRuleTimestreamOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestream]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestream]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestream]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class IotTopicRuleTimestreamOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamOutputReference",
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

    @jsii.member(jsii_name="putDimension")
    def put_dimension(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[IotTopicRuleTimestreamDimension]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putDimension", [value]))

    @jsii.member(jsii_name="putTimestamp")
    def put_timestamp(self, *, unit: builtins.str, value: builtins.str) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        value_ = IotTopicRuleTimestreamTimestamp(unit=unit, value=value)

        return typing.cast(None, jsii.invoke(self, "putTimestamp", [value_]))

    @jsii.member(jsii_name="resetTimestamp")
    def reset_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimestamp", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimension")
    def dimension(self) -> IotTopicRuleTimestreamDimensionList:
        return typing.cast(IotTopicRuleTimestreamDimensionList, jsii.get(self, "dimension"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> "IotTopicRuleTimestreamTimestampOutputReference":
        return typing.cast("IotTopicRuleTimestreamTimestampOutputReference", jsii.get(self, "timestamp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dimensionInput")
    def dimension_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestreamDimension]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[IotTopicRuleTimestreamDimension]]], jsii.get(self, "dimensionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timestampInput")
    def timestamp_input(self) -> typing.Optional["IotTopicRuleTimestreamTimestamp"]:
        return typing.cast(typing.Optional["IotTopicRuleTimestreamTimestamp"], jsii.get(self, "timestampInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[IotTopicRuleTimestream, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[IotTopicRuleTimestream, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[IotTopicRuleTimestream, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamTimestamp",
    jsii_struct_bases=[],
    name_mapping={"unit": "unit", "value": "value"},
)
class IotTopicRuleTimestreamTimestamp:
    def __init__(self, *, unit: builtins.str, value: builtins.str) -> None:
        '''
        :param unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "unit": unit,
            "value": value,
        }

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#unit IotTopicRule#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iot_topic_rule#value IotTopicRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IotTopicRuleTimestreamTimestamp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IotTopicRuleTimestreamTimestampOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iot.IotTopicRuleTimestreamTimestampOutputReference",
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
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        jsii.set(self, "unit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[IotTopicRuleTimestreamTimestamp]:
        return typing.cast(typing.Optional[IotTopicRuleTimestreamTimestamp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[IotTopicRuleTimestreamTimestamp],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsIotEndpoint",
    "DataAwsIotEndpointConfig",
    "IotAuthorizer",
    "IotAuthorizerConfig",
    "IotCertificate",
    "IotCertificateConfig",
    "IotIndexingConfiguration",
    "IotIndexingConfigurationConfig",
    "IotIndexingConfigurationThingGroupIndexingConfiguration",
    "IotIndexingConfigurationThingGroupIndexingConfigurationCustomField",
    "IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldList",
    "IotIndexingConfigurationThingGroupIndexingConfigurationCustomFieldOutputReference",
    "IotIndexingConfigurationThingGroupIndexingConfigurationManagedField",
    "IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldList",
    "IotIndexingConfigurationThingGroupIndexingConfigurationManagedFieldOutputReference",
    "IotIndexingConfigurationThingGroupIndexingConfigurationOutputReference",
    "IotIndexingConfigurationThingIndexingConfiguration",
    "IotIndexingConfigurationThingIndexingConfigurationCustomField",
    "IotIndexingConfigurationThingIndexingConfigurationCustomFieldList",
    "IotIndexingConfigurationThingIndexingConfigurationCustomFieldOutputReference",
    "IotIndexingConfigurationThingIndexingConfigurationManagedField",
    "IotIndexingConfigurationThingIndexingConfigurationManagedFieldList",
    "IotIndexingConfigurationThingIndexingConfigurationManagedFieldOutputReference",
    "IotIndexingConfigurationThingIndexingConfigurationOutputReference",
    "IotLoggingOptions",
    "IotLoggingOptionsConfig",
    "IotPolicy",
    "IotPolicyAttachment",
    "IotPolicyAttachmentConfig",
    "IotPolicyConfig",
    "IotProvisioningTemplate",
    "IotProvisioningTemplateConfig",
    "IotProvisioningTemplatePreProvisioningHook",
    "IotProvisioningTemplatePreProvisioningHookOutputReference",
    "IotRoleAlias",
    "IotRoleAliasConfig",
    "IotThing",
    "IotThingConfig",
    "IotThingGroup",
    "IotThingGroupConfig",
    "IotThingGroupMembership",
    "IotThingGroupMembershipConfig",
    "IotThingGroupMetadata",
    "IotThingGroupMetadataList",
    "IotThingGroupMetadataOutputReference",
    "IotThingGroupMetadataRootToParentGroups",
    "IotThingGroupMetadataRootToParentGroupsList",
    "IotThingGroupMetadataRootToParentGroupsOutputReference",
    "IotThingGroupProperties",
    "IotThingGroupPropertiesAttributePayload",
    "IotThingGroupPropertiesAttributePayloadOutputReference",
    "IotThingGroupPropertiesOutputReference",
    "IotThingPrincipalAttachment",
    "IotThingPrincipalAttachmentConfig",
    "IotThingType",
    "IotThingTypeConfig",
    "IotThingTypeProperties",
    "IotThingTypePropertiesOutputReference",
    "IotTopicRule",
    "IotTopicRuleCloudwatchAlarm",
    "IotTopicRuleCloudwatchAlarmList",
    "IotTopicRuleCloudwatchAlarmOutputReference",
    "IotTopicRuleCloudwatchLogs",
    "IotTopicRuleCloudwatchLogsList",
    "IotTopicRuleCloudwatchLogsOutputReference",
    "IotTopicRuleCloudwatchMetric",
    "IotTopicRuleCloudwatchMetricList",
    "IotTopicRuleCloudwatchMetricOutputReference",
    "IotTopicRuleConfig",
    "IotTopicRuleDestination",
    "IotTopicRuleDestinationConfig",
    "IotTopicRuleDestinationTimeouts",
    "IotTopicRuleDestinationTimeoutsOutputReference",
    "IotTopicRuleDestinationVpcConfiguration",
    "IotTopicRuleDestinationVpcConfigurationOutputReference",
    "IotTopicRuleDynamodb",
    "IotTopicRuleDynamodbList",
    "IotTopicRuleDynamodbOutputReference",
    "IotTopicRuleDynamodbv2",
    "IotTopicRuleDynamodbv2List",
    "IotTopicRuleDynamodbv2OutputReference",
    "IotTopicRuleDynamodbv2PutItem",
    "IotTopicRuleDynamodbv2PutItemOutputReference",
    "IotTopicRuleElasticsearch",
    "IotTopicRuleElasticsearchList",
    "IotTopicRuleElasticsearchOutputReference",
    "IotTopicRuleErrorAction",
    "IotTopicRuleErrorActionCloudwatchAlarm",
    "IotTopicRuleErrorActionCloudwatchAlarmOutputReference",
    "IotTopicRuleErrorActionCloudwatchLogs",
    "IotTopicRuleErrorActionCloudwatchLogsOutputReference",
    "IotTopicRuleErrorActionCloudwatchMetric",
    "IotTopicRuleErrorActionCloudwatchMetricOutputReference",
    "IotTopicRuleErrorActionDynamodb",
    "IotTopicRuleErrorActionDynamodbOutputReference",
    "IotTopicRuleErrorActionDynamodbv2",
    "IotTopicRuleErrorActionDynamodbv2OutputReference",
    "IotTopicRuleErrorActionDynamodbv2PutItem",
    "IotTopicRuleErrorActionDynamodbv2PutItemOutputReference",
    "IotTopicRuleErrorActionElasticsearch",
    "IotTopicRuleErrorActionElasticsearchOutputReference",
    "IotTopicRuleErrorActionFirehose",
    "IotTopicRuleErrorActionFirehoseOutputReference",
    "IotTopicRuleErrorActionHttp",
    "IotTopicRuleErrorActionHttpHttpHeader",
    "IotTopicRuleErrorActionHttpHttpHeaderList",
    "IotTopicRuleErrorActionHttpHttpHeaderOutputReference",
    "IotTopicRuleErrorActionHttpOutputReference",
    "IotTopicRuleErrorActionIotAnalytics",
    "IotTopicRuleErrorActionIotAnalyticsOutputReference",
    "IotTopicRuleErrorActionIotEvents",
    "IotTopicRuleErrorActionIotEventsOutputReference",
    "IotTopicRuleErrorActionKafka",
    "IotTopicRuleErrorActionKafkaOutputReference",
    "IotTopicRuleErrorActionKinesis",
    "IotTopicRuleErrorActionKinesisOutputReference",
    "IotTopicRuleErrorActionLambda",
    "IotTopicRuleErrorActionLambdaOutputReference",
    "IotTopicRuleErrorActionOutputReference",
    "IotTopicRuleErrorActionRepublish",
    "IotTopicRuleErrorActionRepublishOutputReference",
    "IotTopicRuleErrorActionS3",
    "IotTopicRuleErrorActionS3OutputReference",
    "IotTopicRuleErrorActionSns",
    "IotTopicRuleErrorActionSnsOutputReference",
    "IotTopicRuleErrorActionSqs",
    "IotTopicRuleErrorActionSqsOutputReference",
    "IotTopicRuleErrorActionStepFunctions",
    "IotTopicRuleErrorActionStepFunctionsOutputReference",
    "IotTopicRuleErrorActionTimestream",
    "IotTopicRuleErrorActionTimestreamDimension",
    "IotTopicRuleErrorActionTimestreamDimensionList",
    "IotTopicRuleErrorActionTimestreamDimensionOutputReference",
    "IotTopicRuleErrorActionTimestreamOutputReference",
    "IotTopicRuleErrorActionTimestreamTimestamp",
    "IotTopicRuleErrorActionTimestreamTimestampOutputReference",
    "IotTopicRuleFirehose",
    "IotTopicRuleFirehoseList",
    "IotTopicRuleFirehoseOutputReference",
    "IotTopicRuleHttp",
    "IotTopicRuleHttpHttpHeader",
    "IotTopicRuleHttpHttpHeaderList",
    "IotTopicRuleHttpHttpHeaderOutputReference",
    "IotTopicRuleHttpList",
    "IotTopicRuleHttpOutputReference",
    "IotTopicRuleIotAnalytics",
    "IotTopicRuleIotAnalyticsList",
    "IotTopicRuleIotAnalyticsOutputReference",
    "IotTopicRuleIotEvents",
    "IotTopicRuleIotEventsList",
    "IotTopicRuleIotEventsOutputReference",
    "IotTopicRuleKafka",
    "IotTopicRuleKafkaList",
    "IotTopicRuleKafkaOutputReference",
    "IotTopicRuleKinesis",
    "IotTopicRuleKinesisList",
    "IotTopicRuleKinesisOutputReference",
    "IotTopicRuleLambda",
    "IotTopicRuleLambdaList",
    "IotTopicRuleLambdaOutputReference",
    "IotTopicRuleRepublish",
    "IotTopicRuleRepublishList",
    "IotTopicRuleRepublishOutputReference",
    "IotTopicRuleS3",
    "IotTopicRuleS3List",
    "IotTopicRuleS3OutputReference",
    "IotTopicRuleSns",
    "IotTopicRuleSnsList",
    "IotTopicRuleSnsOutputReference",
    "IotTopicRuleSqs",
    "IotTopicRuleSqsList",
    "IotTopicRuleSqsOutputReference",
    "IotTopicRuleStepFunctions",
    "IotTopicRuleStepFunctionsList",
    "IotTopicRuleStepFunctionsOutputReference",
    "IotTopicRuleTimestream",
    "IotTopicRuleTimestreamDimension",
    "IotTopicRuleTimestreamDimensionList",
    "IotTopicRuleTimestreamDimensionOutputReference",
    "IotTopicRuleTimestreamList",
    "IotTopicRuleTimestreamOutputReference",
    "IotTopicRuleTimestreamTimestamp",
    "IotTopicRuleTimestreamTimestampOutputReference",
]

publication.publish()
