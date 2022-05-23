'''
# cdk-amazon-chime-resources

![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

An AWS Cloud Development Kit (AWS CDK) construct library that allows you to provision Amazon Chime resources with npm and pypi

## Background

Amazon Chime resources (Amazon Chime Messaging and Amazon Chime PSTN resources) are not natively available in AWS CloudFormation or AWS CDK. Therefore, in order to create these resources with AWS CDK, an AWS Lambda backed custom resource must be used. In an effort to simplify that process, this AWS CDK construct has been created. This AWS CDK construct will create a custom resource and associated Lambda and expose constructs that can be used to create corresponding resources. This construct includes resources for both Amazon Chime Messaging and Amazon Chime PSTN.

## Resources

* [Amazon Chime PSTN Resources](PSTNRESOURCES.MD)
* [Amazon Chime Messaging Resources](MESSAGINGRESOURCES.MD)

## Installing

To add to your AWS CDK package.json file:

```
yarn add cdk-amazon-chime-resources
```

## Not Supported Yet

This is a work in progress.

Features that are not supported yet:

* [ ] Amazon Chime Voice Connector Groups
* [ ] Amazon Chime Voice Connector Logging
* [ ] Amazon Chime Voice Connector Emergency Calling
* [ ] Updates to created resources

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License.
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
import aws_cdk.aws_lambda
import aws_cdk.custom_resources
import constructs


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.AppInstanceAdminProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_instance_admin_arn": "appInstanceAdminArn",
        "app_instance_arn": "appInstanceArn",
    },
)
class AppInstanceAdminProps:
    def __init__(
        self,
        *,
        app_instance_admin_arn: builtins.str,
        app_instance_arn: builtins.str,
    ) -> None:
        '''Props for ``AppInstance``.

        :param app_instance_admin_arn: The name of the app instance. Default: - None
        :param app_instance_arn: The name of the app instance. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_instance_admin_arn": app_instance_admin_arn,
            "app_instance_arn": app_instance_arn,
        }

    @builtins.property
    def app_instance_admin_arn(self) -> builtins.str:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("app_instance_admin_arn")
        assert result is not None, "Required property 'app_instance_admin_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_instance_arn(self) -> builtins.str:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("app_instance_arn")
        assert result is not None, "Required property 'app_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstanceAdminProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.AppInstanceDataType")
class AppInstanceDataType(enum.Enum):
    CHANNEL = "CHANNEL"
    CHANNELMESSAGE = "CHANNELMESSAGE"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.AppInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "client_request_token": "clientRequestToken",
        "metadata": "metadata",
        "name": "name",
    },
)
class AppInstanceProps:
    def __init__(
        self,
        *,
        client_request_token: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``AppInstance``.

        :param client_request_token: The ClientRequestToken of the app instance. This field is autopopulated if not provided. Default: - None
        :param metadata: The metadata of the app instance. Limited to a 1KB string in UTF-8. Default: - None
        :param name: The name of the app instance. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_request_token is not None:
            self._values["client_request_token"] = client_request_token
        if metadata is not None:
            self._values["metadata"] = metadata
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def client_request_token(self) -> typing.Optional[builtins.str]:
        '''The ClientRequestToken of the app instance.

        This field is autopopulated if not provided.

        :default: - None
        '''
        result = self._values.get("client_request_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the app instance.

        Limited to a 1KB string in UTF-8.

        :default: - None
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.AppInstanceUserProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_instance_arn": "appInstanceArn",
        "app_instance_user_id": "appInstanceUserId",
        "client_request_token": "clientRequestToken",
        "metadata": "metadata",
        "name": "name",
    },
)
class AppInstanceUserProps:
    def __init__(
        self,
        *,
        app_instance_arn: builtins.str,
        app_instance_user_id: builtins.str,
        client_request_token: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``AppInstance``.

        :param app_instance_arn: The name of the app instance. Default: - None
        :param app_instance_user_id: The name of the app instance. Default: - None
        :param client_request_token: The ClientRequestToken of the app instance. This field is autopopulated if not provided. Default: - None
        :param metadata: The metadata of the app instance. Limited to a 1KB string in UTF-8. Default: - None
        :param name: The name of the app instance. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_instance_arn": app_instance_arn,
            "app_instance_user_id": app_instance_user_id,
        }
        if client_request_token is not None:
            self._values["client_request_token"] = client_request_token
        if metadata is not None:
            self._values["metadata"] = metadata
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def app_instance_arn(self) -> builtins.str:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("app_instance_arn")
        assert result is not None, "Required property 'app_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_instance_user_id(self) -> builtins.str:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("app_instance_user_id")
        assert result is not None, "Required property 'app_instance_user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_request_token(self) -> typing.Optional[builtins.str]:
        '''The ClientRequestToken of the app instance.

        This field is autopopulated if not provided.

        :default: - None
        '''
        result = self._values.get("client_request_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the app instance.

        Limited to a 1KB string in UTF-8.

        :default: - None
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the app instance.

        :default: - None
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstanceUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ChannelFlow(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.ChannelFlow",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_instance_arn: builtins.str,
        client_request_token: builtins.str,
        processors: typing.Sequence["Processors"],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence["Tags"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_instance_arn: The ARN of the App Instance. Default: - None
        :param client_request_token: The client token for the request. An Idempotency token. Default: - None
        :param processors: Information about the processor Lambda functions. Default: - None
        :param name: The name of the channel flow. Default: - None
        :param tags: The tags for the creation request. Default: - None
        '''
        props = ChannelFlowProps(
            app_instance_arn=app_instance_arn,
            client_request_token=client_request_token,
            processors=processors,
            name=name,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelFlowArn")
    def channel_flow_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelFlowArn"))


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.ChannelFlowProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_instance_arn": "appInstanceArn",
        "client_request_token": "clientRequestToken",
        "processors": "processors",
        "name": "name",
        "tags": "tags",
    },
)
class ChannelFlowProps:
    def __init__(
        self,
        *,
        app_instance_arn: builtins.str,
        client_request_token: builtins.str,
        processors: typing.Sequence["Processors"],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence["Tags"]] = None,
    ) -> None:
        '''Props for ``AppInstance``.

        See: https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_messaging-chime_CreateChannelFlow.html

        :param app_instance_arn: The ARN of the App Instance. Default: - None
        :param client_request_token: The client token for the request. An Idempotency token. Default: - None
        :param processors: Information about the processor Lambda functions. Default: - None
        :param name: The name of the channel flow. Default: - None
        :param tags: The tags for the creation request. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_instance_arn": app_instance_arn,
            "client_request_token": client_request_token,
            "processors": processors,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def app_instance_arn(self) -> builtins.str:
        '''The ARN of the App Instance.

        :default: - None
        '''
        result = self._values.get("app_instance_arn")
        assert result is not None, "Required property 'app_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_request_token(self) -> builtins.str:
        '''The client token for the request.

        An Idempotency token.

        :default: - None
        '''
        result = self._values.get("client_request_token")
        assert result is not None, "Required property 'client_request_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def processors(self) -> typing.List["Processors"]:
        '''Information about the processor Lambda functions.

        :default: - None
        '''
        result = self._values.get("processors")
        assert result is not None, "Required property 'processors' is missing"
        return typing.cast(typing.List["Processors"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the channel flow.

        :default: - None
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["Tags"]]:
        '''The tags for the creation request.

        :default: - None
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["Tags"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ChannelFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ChimePhoneNumber(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.ChimePhoneNumber",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        phone_product_type: "PhoneProductType",
        phone_area_code: typing.Optional[jsii.Number] = None,
        phone_city: typing.Optional[builtins.str] = None,
        phone_country: typing.Optional["PhoneCountry"] = None,
        phone_number_toll_free_prefix: typing.Optional[jsii.Number] = None,
        phone_number_type: typing.Optional["PhoneNumberType"] = None,
        phone_state: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param phone_product_type: Phone Product Type (required) - SipMediaApplicationDialIn or VoiceConnector. Default: - None
        :param phone_area_code: Area Code for phone number request (optional) - Usable only with US Country. Default: - None
        :param phone_city: City for phone number request (optional) - Usable only with US Country. Default: - None
        :param phone_country: Country for phone number request (optional) - See https://docs.aws.amazon.com/chime/latest/ag/phone-country-reqs.html for more details. Default: - US
        :param phone_number_toll_free_prefix: Toll Free Prefix for phone number request (optional). Default: - None
        :param phone_number_type: Phone Number Type for phone number request (optional) - Local or TollFree - Required with non-US country. Default: - None
        :param phone_state: State for phone number request (optional) - Usable only with US Country. Default: - None
        '''
        props = PhoneNumberProps(
            phone_product_type=phone_product_type,
            phone_area_code=phone_area_code,
            phone_city=phone_city,
            phone_country=phone_country,
            phone_number_toll_free_prefix=phone_number_toll_free_prefix,
            phone_number_type=phone_number_type,
            phone_state=phone_state,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="associateWithVoiceConnector")
    def associate_with_voice_connector(
        self,
        voice_connector_id: "ChimeVoiceConnector",
    ) -> "PhoneAssociation":
        '''
        :param voice_connector_id: -
        '''
        return typing.cast("PhoneAssociation", jsii.invoke(self, "associateWithVoiceConnector", [voice_connector_id]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="phoneNumber")
    def phone_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phoneNumber"))


class ChimeSipMediaApp(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.ChimeSipMediaApp",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint: builtins.str,
        name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param endpoint: endpoint for SipMediaApplication(required). Default: - none
        :param name: name for SipMediaApplication (optional). Default: - unique ID for resource
        :param region: region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler. Default: - same region as stack deployment
        '''
        props = SipMediaAppProps(endpoint=endpoint, name=name, region=region)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sipMediaAppId")
    def sip_media_app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sipMediaAppId"))


class ChimeSipRule(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.ChimeSipRule",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        target_applications: typing.Sequence["TargetApplications"],
        trigger_type: "TriggerType",
        trigger_value: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param target_applications: 
        :param trigger_type: Trigger Type for SipRule (required) - TO_PHONE_NUMBER or REQUEST_URI_HOSTNAME. Default: - none
        :param trigger_value: Trigger Value for SipRule (required) - EE.164 Phone Number or Voice Connector URI. Default: - none
        :param name: name for SipRule (optional). Default: - unique ID for resource
        '''
        props = SipRuleProps(
            target_applications=target_applications,
            trigger_type=trigger_type,
            trigger_value=trigger_value,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sipRuleId")
    def sip_rule_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sipRuleId"))


class ChimeVoiceConnector(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.ChimeVoiceConnector",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encryption: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        origination: typing.Optional[typing.Sequence["Routes"]] = None,
        region: typing.Optional[builtins.str] = None,
        streaming: typing.Optional["Streaming"] = None,
        termination: typing.Optional["Termination"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param encryption: Encryption boolean for VoiceConnector. Default: - False
        :param name: name for VoiceConnector. Default: - unique ID for resource
        :param origination: 
        :param region: region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler. Default: - same region as stack deployment
        :param streaming: 
        :param termination: 
        '''
        props = VoiceConnectorProps(
            encryption=encryption,
            name=name,
            origination=origination,
            region=region,
            streaming=streaming,
            termination=termination,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="voiceConnectorId")
    def voice_connector_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "voiceConnectorId"))


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Configuration",
    jsii_struct_bases=[],
    name_mapping={"lambda_": "lambda"},
)
class Configuration:
    def __init__(self, *, lambda_: "Lambda") -> None:
        '''Props for ``Configuration``.

        See: https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_messaging-chime_ProcessorConfiguration.html

        :param lambda_: Indicates that the processor is of type Lambda. Default: - None
        '''
        if isinstance(lambda_, dict):
            lambda_ = Lambda(**lambda_)
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_": lambda_,
        }

    @builtins.property
    def lambda_(self) -> "Lambda":
        '''Indicates that the processor is of type Lambda.

        :default: - None
        '''
        result = self._values.get("lambda_")
        assert result is not None, "Required property 'lambda_' is missing"
        return typing.cast("Lambda", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.FallbackAction")
class FallbackAction(enum.Enum):
    CONTINUE = "CONTINUE"
    ABORT = "ABORT"


@jsii.enum(jsii_type="cdk-amazon-chime-resources.InvocationType")
class InvocationType(enum.Enum):
    ASYNC = "ASYNC"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Lambda",
    jsii_struct_bases=[],
    name_mapping={"invocation_type": "invocationType", "resource_arn": "resourceArn"},
)
class Lambda:
    def __init__(
        self,
        *,
        invocation_type: InvocationType,
        resource_arn: builtins.str,
    ) -> None:
        '''Props for ``LambdaConfiguration``.

        See: https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_messaging-chime_LambdaConfiguration.html

        :param invocation_type: Controls how the Lambda function is invoked. Default: - None
        :param resource_arn: The ARN of the Lambda message processing function. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "invocation_type": invocation_type,
            "resource_arn": resource_arn,
        }

    @builtins.property
    def invocation_type(self) -> InvocationType:
        '''Controls how the Lambda function is invoked.

        :default: - None
        '''
        result = self._values.get("invocation_type")
        assert result is not None, "Required property 'invocation_type' is missing"
        return typing.cast(InvocationType, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''The ARN of the Lambda message processing function.

        :default: - None
        '''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Lambda(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MessagingAppInstance(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.MessagingAppInstance",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        client_request_token: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param client_request_token: The ClientRequestToken of the app instance. This field is autopopulated if not provided. Default: - None
        :param metadata: The metadata of the app instance. Limited to a 1KB string in UTF-8. Default: - None
        :param name: The name of the app instance. Default: - None
        '''
        props = AppInstanceProps(
            client_request_token=client_request_token, metadata=metadata, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="retention")
    def retention(self, days: jsii.Number) -> "MessagingResources":
        '''
        :param days: -
        '''
        return typing.cast("MessagingResources", jsii.invoke(self, "retention", [days]))

    @jsii.member(jsii_name="streaming")
    def streaming(
        self,
        streaming_configs: typing.Sequence["StreamingConfig"],
    ) -> "MessagingResources":
        '''
        :param streaming_configs: -
        '''
        return typing.cast("MessagingResources", jsii.invoke(self, "streaming", [streaming_configs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appInstanceArn")
    def app_instance_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appInstanceArn"))


class MessagingAppInstanceAdmin(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.MessagingAppInstanceAdmin",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_instance_admin_arn: builtins.str,
        app_instance_arn: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_instance_admin_arn: The name of the app instance. Default: - None
        :param app_instance_arn: The name of the app instance. Default: - None
        '''
        props = AppInstanceAdminProps(
            app_instance_admin_arn=app_instance_admin_arn,
            app_instance_arn=app_instance_arn,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appInstanceAdminArn")
    def app_instance_admin_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appInstanceAdminArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appInstanceAdminName")
    def app_instance_admin_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appInstanceAdminName"))


class MessagingAppInstanceUser(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.MessagingAppInstanceUser",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_instance_arn: builtins.str,
        app_instance_user_id: builtins.str,
        client_request_token: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_instance_arn: The name of the app instance. Default: - None
        :param app_instance_user_id: The name of the app instance. Default: - None
        :param client_request_token: The ClientRequestToken of the app instance. This field is autopopulated if not provided. Default: - None
        :param metadata: The metadata of the app instance. Limited to a 1KB string in UTF-8. Default: - None
        :param name: The name of the app instance. Default: - None
        '''
        props = AppInstanceUserProps(
            app_instance_arn=app_instance_arn,
            app_instance_user_id=app_instance_user_id,
            client_request_token=client_request_token,
            metadata=metadata,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appInstanceUserArn")
    def app_instance_user_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appInstanceUserArn"))


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.MessagingResourceProps",
    jsii_struct_bases=[aws_cdk.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "properties": "properties",
        "resource_type": "resourceType",
        "uid": "uid",
    },
)
class MessagingResourceProps(aws_cdk.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        uid: builtins.str,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param properties: 
        :param resource_type: 
        :param uid: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "properties": properties,
            "resource_type": resource_type,
            "uid": uid,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        result = self._values.get("properties")
        assert result is not None, "Required property 'properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def resource_type(self) -> builtins.str:
        result = self._values.get("resource_type")
        assert result is not None, "Required property 'resource_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MessagingResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MessagingResources(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.MessagingResources",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        uid: builtins.str,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param properties: 
        :param resource_type: 
        :param uid: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = MessagingResourceProps(
            properties=properties,
            resource_type=resource_type,
            uid=uid,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messagingCustomResource")
    def messaging_custom_resource(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "messagingCustomResource"))


@jsii.enum(jsii_type="cdk-amazon-chime-resources.NotificationTargetType")
class NotificationTargetType(enum.Enum):
    EVENTBRIDGE = "EVENTBRIDGE"
    SNS = "SNS"
    SQS = "SQS"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.PSTNResourceProps",
    jsii_struct_bases=[aws_cdk.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "properties": "properties",
        "resource_type": "resourceType",
        "uid": "uid",
    },
)
class PSTNResourceProps(aws_cdk.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        uid: builtins.str,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param properties: 
        :param resource_type: 
        :param uid: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "properties": properties,
            "resource_type": resource_type,
            "uid": uid,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        result = self._values.get("properties")
        assert result is not None, "Required property 'properties' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def resource_type(self) -> builtins.str:
        result = self._values.get("resource_type")
        assert result is not None, "Required property 'resource_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PSTNResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PSTNResources(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.PSTNResources",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        properties: typing.Mapping[builtins.str, typing.Any],
        resource_type: builtins.str,
        uid: builtins.str,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param properties: 
        :param resource_type: 
        :param uid: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = PSTNResourceProps(
            properties=properties,
            resource_type=resource_type,
            uid=uid,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pstnCustomResource")
    def pstn_custom_resource(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "pstnCustomResource"))


class PhoneAssociation(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-amazon-chime-resources.PhoneAssociation",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        e164_phone_number: builtins.str,
        voice_connector_id: builtins.str,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param e164_phone_number: 
        :param voice_connector_id: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = PhoneAssociationProps(
            e164_phone_number=e164_phone_number,
            voice_connector_id=voice_connector_id,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="phoneAssociationResource")
    def phone_association_resource(self) -> aws_cdk.custom_resources.AwsCustomResource:
        return typing.cast(aws_cdk.custom_resources.AwsCustomResource, jsii.get(self, "phoneAssociationResource"))


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.PhoneAssociationProps",
    jsii_struct_bases=[aws_cdk.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "e164_phone_number": "e164PhoneNumber",
        "voice_connector_id": "voiceConnectorId",
    },
)
class PhoneAssociationProps(aws_cdk.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        e164_phone_number: builtins.str,
        voice_connector_id: builtins.str,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param e164_phone_number: 
        :param voice_connector_id: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "e164_phone_number": e164_phone_number,
            "voice_connector_id": voice_connector_id,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def e164_phone_number(self) -> builtins.str:
        result = self._values.get("e164_phone_number")
        assert result is not None, "Required property 'e164_phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def voice_connector_id(self) -> builtins.str:
        result = self._values.get("voice_connector_id")
        assert result is not None, "Required property 'voice_connector_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PhoneAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.PhoneCountry")
class PhoneCountry(enum.Enum):
    AU = "AU"
    AT = "AT"
    CA = "CA"
    DK = "DK"
    DE = "DE"
    IE = "IE"
    IT = "IT"
    NZ = "NZ"
    NG = "NG"
    PR = "PR"
    KR = "KR"
    SE = "SE"
    CH = "CH"
    UK = "UK"
    US = "US"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.PhoneNumberProps",
    jsii_struct_bases=[],
    name_mapping={
        "phone_product_type": "phoneProductType",
        "phone_area_code": "phoneAreaCode",
        "phone_city": "phoneCity",
        "phone_country": "phoneCountry",
        "phone_number_toll_free_prefix": "phoneNumberTollFreePrefix",
        "phone_number_type": "phoneNumberType",
        "phone_state": "phoneState",
    },
)
class PhoneNumberProps:
    def __init__(
        self,
        *,
        phone_product_type: "PhoneProductType",
        phone_area_code: typing.Optional[jsii.Number] = None,
        phone_city: typing.Optional[builtins.str] = None,
        phone_country: typing.Optional[PhoneCountry] = None,
        phone_number_toll_free_prefix: typing.Optional[jsii.Number] = None,
        phone_number_type: typing.Optional["PhoneNumberType"] = None,
        phone_state: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``PhoneNumber``.

        :param phone_product_type: Phone Product Type (required) - SipMediaApplicationDialIn or VoiceConnector. Default: - None
        :param phone_area_code: Area Code for phone number request (optional) - Usable only with US Country. Default: - None
        :param phone_city: City for phone number request (optional) - Usable only with US Country. Default: - None
        :param phone_country: Country for phone number request (optional) - See https://docs.aws.amazon.com/chime/latest/ag/phone-country-reqs.html for more details. Default: - US
        :param phone_number_toll_free_prefix: Toll Free Prefix for phone number request (optional). Default: - None
        :param phone_number_type: Phone Number Type for phone number request (optional) - Local or TollFree - Required with non-US country. Default: - None
        :param phone_state: State for phone number request (optional) - Usable only with US Country. Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "phone_product_type": phone_product_type,
        }
        if phone_area_code is not None:
            self._values["phone_area_code"] = phone_area_code
        if phone_city is not None:
            self._values["phone_city"] = phone_city
        if phone_country is not None:
            self._values["phone_country"] = phone_country
        if phone_number_toll_free_prefix is not None:
            self._values["phone_number_toll_free_prefix"] = phone_number_toll_free_prefix
        if phone_number_type is not None:
            self._values["phone_number_type"] = phone_number_type
        if phone_state is not None:
            self._values["phone_state"] = phone_state

    @builtins.property
    def phone_product_type(self) -> "PhoneProductType":
        '''Phone Product Type (required) - SipMediaApplicationDialIn or VoiceConnector.

        :default: - None
        '''
        result = self._values.get("phone_product_type")
        assert result is not None, "Required property 'phone_product_type' is missing"
        return typing.cast("PhoneProductType", result)

    @builtins.property
    def phone_area_code(self) -> typing.Optional[jsii.Number]:
        '''Area Code for phone number request (optional)  - Usable only with US Country.

        :default: - None
        '''
        result = self._values.get("phone_area_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def phone_city(self) -> typing.Optional[builtins.str]:
        '''City for phone number request (optional) - Usable only with US Country.

        :default: - None
        '''
        result = self._values.get("phone_city")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def phone_country(self) -> typing.Optional[PhoneCountry]:
        '''Country for phone number request (optional) - See https://docs.aws.amazon.com/chime/latest/ag/phone-country-reqs.html for more details.

        :default: - US
        '''
        result = self._values.get("phone_country")
        return typing.cast(typing.Optional[PhoneCountry], result)

    @builtins.property
    def phone_number_toll_free_prefix(self) -> typing.Optional[jsii.Number]:
        '''Toll Free Prefix for phone number request (optional).

        :default: - None
        '''
        result = self._values.get("phone_number_toll_free_prefix")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def phone_number_type(self) -> typing.Optional["PhoneNumberType"]:
        '''Phone Number Type for phone number request (optional) - Local or TollFree - Required with non-US country.

        :default: - None
        '''
        result = self._values.get("phone_number_type")
        return typing.cast(typing.Optional["PhoneNumberType"], result)

    @builtins.property
    def phone_state(self) -> typing.Optional[builtins.str]:
        '''State for phone number request (optional) - Usable only with US Country.

        :default: - None
        '''
        result = self._values.get("phone_state")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PhoneNumberProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.PhoneNumberType")
class PhoneNumberType(enum.Enum):
    LOCAL = "LOCAL"
    TOLLFREE = "TOLLFREE"


@jsii.enum(jsii_type="cdk-amazon-chime-resources.PhoneProductType")
class PhoneProductType(enum.Enum):
    SMA = "SMA"
    VC = "VC"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Processors",
    jsii_struct_bases=[],
    name_mapping={
        "configuration": "configuration",
        "execution_order": "executionOrder",
        "fallback_action": "fallbackAction",
        "name": "name",
    },
)
class Processors:
    def __init__(
        self,
        *,
        configuration: Configuration,
        execution_order: jsii.Number,
        fallback_action: FallbackAction,
        name: builtins.str,
    ) -> None:
        '''Props for ``Processors``.

        See: https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_messaging-chime_Processor.html

        :param configuration: The information about the type of processor and its identifier. Default: - None
        :param execution_order: The sequence in which processors run. If you have multiple processors in a channel flow, message processing goes through each processor in the sequence. The value determines the sequence. At this point, we support only 1 processor within a flow. Default: - None
        :param fallback_action: Determines whether to continue with message processing or stop it in cases where communication with a processor fails. If a processor has a fallback action of ABORT and communication with it fails, the processor sets the message status to FAILED and does not send the message to any recipients. Note that if the last processor in the channel flow sequence has a fallback action of CONTINUE and communication with the processor fails, then the message is considered processed and sent to recipients of the channel. Default: - None
        :param name: The name of the Channel Flow Processor. Default: - None
        '''
        if isinstance(configuration, dict):
            configuration = Configuration(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration": configuration,
            "execution_order": execution_order,
            "fallback_action": fallback_action,
            "name": name,
        }

    @builtins.property
    def configuration(self) -> Configuration:
        '''The information about the type of processor and its identifier.

        :default: - None
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(Configuration, result)

    @builtins.property
    def execution_order(self) -> jsii.Number:
        '''The sequence in which processors run.

        If you have multiple processors in a channel flow, message processing goes through each processor in the sequence. The value determines the sequence. At this point, we support only 1 processor within a flow.

        :default: - None
        '''
        result = self._values.get("execution_order")
        assert result is not None, "Required property 'execution_order' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def fallback_action(self) -> FallbackAction:
        '''Determines whether to continue with message processing or stop it in cases where communication with a processor fails.

        If a processor has a fallback action of ABORT and communication with it fails, the processor sets the message status to FAILED and does not send the message to any recipients. Note that if the last processor in the channel flow sequence has a fallback action of CONTINUE and communication with the processor fails, then the message is considered processed and sent to recipients of the channel.

        :default: - None
        '''
        result = self._values.get("fallback_action")
        assert result is not None, "Required property 'fallback_action' is missing"
        return typing.cast(FallbackAction, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Channel Flow Processor.

        :default: - None
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Processors(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.Protocol")
class Protocol(enum.Enum):
    TCP = "TCP"
    UDP = "UDP"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Routes",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "port": "port",
        "priority": "priority",
        "protocol": "protocol",
        "weight": "weight",
    },
)
class Routes:
    def __init__(
        self,
        *,
        host: builtins.str,
        port: jsii.Number,
        priority: jsii.Number,
        protocol: Protocol,
        weight: jsii.Number,
    ) -> None:
        '''
        :param host: 
        :param port: 
        :param priority: 
        :param protocol: 
        :param weight: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "port": port,
            "priority": priority,
            "protocol": protocol,
            "weight": weight,
        }

    @builtins.property
    def host(self) -> builtins.str:
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def priority(self) -> jsii.Number:
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def protocol(self) -> Protocol:
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(Protocol, result)

    @builtins.property
    def weight(self) -> jsii.Number:
        result = self._values.get("weight")
        assert result is not None, "Required property 'weight' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Routes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.SipMediaAppProps",
    jsii_struct_bases=[],
    name_mapping={"endpoint": "endpoint", "name": "name", "region": "region"},
)
class SipMediaAppProps:
    def __init__(
        self,
        *,
        endpoint: builtins.str,
        name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``SipMediaApplication``.

        :param endpoint: endpoint for SipMediaApplication(required). Default: - none
        :param name: name for SipMediaApplication (optional). Default: - unique ID for resource
        :param region: region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler. Default: - same region as stack deployment
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
        }
        if name is not None:
            self._values["name"] = name
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''endpoint for SipMediaApplication(required).

        :default: - none
        '''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''name for SipMediaApplication (optional).

        :default: - unique ID for resource
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler.

        :default: - same region as stack deployment
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SipMediaAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.SipRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "target_applications": "targetApplications",
        "trigger_type": "triggerType",
        "trigger_value": "triggerValue",
        "name": "name",
    },
)
class SipRuleProps:
    def __init__(
        self,
        *,
        target_applications: typing.Sequence["TargetApplications"],
        trigger_type: "TriggerType",
        trigger_value: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``SipRule``.

        :param target_applications: 
        :param trigger_type: Trigger Type for SipRule (required) - TO_PHONE_NUMBER or REQUEST_URI_HOSTNAME. Default: - none
        :param trigger_value: Trigger Value for SipRule (required) - EE.164 Phone Number or Voice Connector URI. Default: - none
        :param name: name for SipRule (optional). Default: - unique ID for resource
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_applications": target_applications,
            "trigger_type": trigger_type,
            "trigger_value": trigger_value,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def target_applications(self) -> typing.List["TargetApplications"]:
        result = self._values.get("target_applications")
        assert result is not None, "Required property 'target_applications' is missing"
        return typing.cast(typing.List["TargetApplications"], result)

    @builtins.property
    def trigger_type(self) -> "TriggerType":
        '''Trigger Type for SipRule (required) - TO_PHONE_NUMBER or REQUEST_URI_HOSTNAME.

        :default: - none
        '''
        result = self._values.get("trigger_type")
        assert result is not None, "Required property 'trigger_type' is missing"
        return typing.cast("TriggerType", result)

    @builtins.property
    def trigger_value(self) -> builtins.str:
        '''Trigger Value for SipRule (required) - EE.164 Phone Number or Voice Connector URI.

        :default: - none
        '''
        result = self._values.get("trigger_value")
        assert result is not None, "Required property 'trigger_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''name for SipRule (optional).

        :default: - unique ID for resource
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SipRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Streaming",
    jsii_struct_bases=[],
    name_mapping={
        "data_retention": "dataRetention",
        "enabled": "enabled",
        "notification_targets": "notificationTargets",
    },
)
class Streaming:
    def __init__(
        self,
        *,
        data_retention: jsii.Number,
        enabled: builtins.bool,
        notification_targets: typing.Sequence[NotificationTargetType],
    ) -> None:
        '''
        :param data_retention: Streaming data retention for VoiceConnector. Default: - 0
        :param enabled: 
        :param notification_targets: Streaming data retention for VoiceConnector. Default: - 0
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "data_retention": data_retention,
            "enabled": enabled,
            "notification_targets": notification_targets,
        }

    @builtins.property
    def data_retention(self) -> jsii.Number:
        '''Streaming data retention for VoiceConnector.

        :default: - 0
        '''
        result = self._values.get("data_retention")
        assert result is not None, "Required property 'data_retention' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def enabled(self) -> builtins.bool:
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def notification_targets(self) -> typing.List[NotificationTargetType]:
        '''Streaming data retention for VoiceConnector.

        :default: - 0
        '''
        result = self._values.get("notification_targets")
        assert result is not None, "Required property 'notification_targets' is missing"
        return typing.cast(typing.List[NotificationTargetType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Streaming(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.StreamingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "app_instance_data_type": "appInstanceDataType",
        "resource_arn": "resourceArn",
    },
)
class StreamingConfig:
    def __init__(
        self,
        *,
        app_instance_data_type: AppInstanceDataType,
        resource_arn: builtins.str,
    ) -> None:
        '''
        :param app_instance_data_type: The type of data to be streamed.
        :param resource_arn: The resource ARN of a Kinesis Stream.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_instance_data_type": app_instance_data_type,
            "resource_arn": resource_arn,
        }

    @builtins.property
    def app_instance_data_type(self) -> AppInstanceDataType:
        '''The type of data to be streamed.'''
        result = self._values.get("app_instance_data_type")
        assert result is not None, "Required property 'app_instance_data_type' is missing"
        return typing.cast(AppInstanceDataType, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''The resource ARN of a Kinesis Stream.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Tags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class Tags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: 
        :param value: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Tags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.TargetApplications",
    jsii_struct_bases=[],
    name_mapping={
        "priority": "priority",
        "sip_media_application_id": "sipMediaApplicationId",
        "region": "region",
    },
)
class TargetApplications:
    def __init__(
        self,
        *,
        priority: jsii.Number,
        sip_media_application_id: builtins.str,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param priority: Priority for SipRule (required) - 1 to 25. Default: - none
        :param sip_media_application_id: SipMediaApplicationId for SipRule (required). Default: - none
        :param region: Region for SipRule (optional). Default: - same region as stack deployment
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "sip_media_application_id": sip_media_application_id,
        }
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def priority(self) -> jsii.Number:
        '''Priority for SipRule (required) - 1 to 25.

        :default: - none
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def sip_media_application_id(self) -> builtins.str:
        '''SipMediaApplicationId for SipRule (required).

        :default: - none
        '''
        result = self._values.get("sip_media_application_id")
        assert result is not None, "Required property 'sip_media_application_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region for SipRule (optional).

        :default: - same region as stack deployment
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetApplications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.Termination",
    jsii_struct_bases=[],
    name_mapping={
        "calling_regions": "callingRegions",
        "termination_cidrs": "terminationCidrs",
    },
)
class Termination:
    def __init__(
        self,
        *,
        calling_regions: typing.Sequence[builtins.str],
        termination_cidrs: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param calling_regions: Calling Regions for VoiceConnector (optional). Default: - ['US']
        :param termination_cidrs: termination IP for VoiceConnector (optional). Default: - none
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "calling_regions": calling_regions,
            "termination_cidrs": termination_cidrs,
        }

    @builtins.property
    def calling_regions(self) -> typing.List[builtins.str]:
        '''Calling Regions for VoiceConnector (optional).

        :default: - ['US']
        '''
        result = self._values.get("calling_regions")
        assert result is not None, "Required property 'calling_regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def termination_cidrs(self) -> typing.List[builtins.str]:
        '''termination IP for VoiceConnector (optional).

        :default: - none
        '''
        result = self._values.get("termination_cidrs")
        assert result is not None, "Required property 'termination_cidrs' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Termination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-amazon-chime-resources.TriggerType")
class TriggerType(enum.Enum):
    TO_PHONE_NUMBER = "TO_PHONE_NUMBER"
    REQUEST_URI_HOSTNAME = "REQUEST_URI_HOSTNAME"


@jsii.data_type(
    jsii_type="cdk-amazon-chime-resources.VoiceConnectorProps",
    jsii_struct_bases=[],
    name_mapping={
        "encryption": "encryption",
        "name": "name",
        "origination": "origination",
        "region": "region",
        "streaming": "streaming",
        "termination": "termination",
    },
)
class VoiceConnectorProps:
    def __init__(
        self,
        *,
        encryption: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        origination: typing.Optional[typing.Sequence[Routes]] = None,
        region: typing.Optional[builtins.str] = None,
        streaming: typing.Optional[Streaming] = None,
        termination: typing.Optional[Termination] = None,
    ) -> None:
        '''Props for ``SipMediaApplication``.

        :param encryption: Encryption boolean for VoiceConnector. Default: - False
        :param name: name for VoiceConnector. Default: - unique ID for resource
        :param origination: 
        :param region: region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler. Default: - same region as stack deployment
        :param streaming: 
        :param termination: 
        '''
        if isinstance(streaming, dict):
            streaming = Streaming(**streaming)
        if isinstance(termination, dict):
            termination = Termination(**termination)
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption is not None:
            self._values["encryption"] = encryption
        if name is not None:
            self._values["name"] = name
        if origination is not None:
            self._values["origination"] = origination
        if region is not None:
            self._values["region"] = region
        if streaming is not None:
            self._values["streaming"] = streaming
        if termination is not None:
            self._values["termination"] = termination

    @builtins.property
    def encryption(self) -> typing.Optional[builtins.bool]:
        '''Encryption boolean for VoiceConnector.

        :default: - False
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''name for VoiceConnector.

        :default: - unique ID for resource
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origination(self) -> typing.Optional[typing.List[Routes]]:
        result = self._values.get("origination")
        return typing.cast(typing.Optional[typing.List[Routes]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''region for SipMediaApplication(required) - Must us-east-1 or us-west-2 and in the same region as the SipMediaApplication Lambda handler.

        :default: - same region as stack deployment
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def streaming(self) -> typing.Optional[Streaming]:
        result = self._values.get("streaming")
        return typing.cast(typing.Optional[Streaming], result)

    @builtins.property
    def termination(self) -> typing.Optional[Termination]:
        result = self._values.get("termination")
        return typing.cast(typing.Optional[Termination], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VoiceConnectorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AppInstanceAdminProps",
    "AppInstanceDataType",
    "AppInstanceProps",
    "AppInstanceUserProps",
    "ChannelFlow",
    "ChannelFlowProps",
    "ChimePhoneNumber",
    "ChimeSipMediaApp",
    "ChimeSipRule",
    "ChimeVoiceConnector",
    "Configuration",
    "FallbackAction",
    "InvocationType",
    "Lambda",
    "MessagingAppInstance",
    "MessagingAppInstanceAdmin",
    "MessagingAppInstanceUser",
    "MessagingResourceProps",
    "MessagingResources",
    "NotificationTargetType",
    "PSTNResourceProps",
    "PSTNResources",
    "PhoneAssociation",
    "PhoneAssociationProps",
    "PhoneCountry",
    "PhoneNumberProps",
    "PhoneNumberType",
    "PhoneProductType",
    "Processors",
    "Protocol",
    "Routes",
    "SipMediaAppProps",
    "SipRuleProps",
    "Streaming",
    "StreamingConfig",
    "Tags",
    "TargetApplications",
    "Termination",
    "TriggerType",
    "VoiceConnectorProps",
]

publication.publish()
