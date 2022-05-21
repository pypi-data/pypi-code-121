'''
# AWS::IoTEvents Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

AWS IoT Events enables you to monitor your equipment or device fleets for
failures or changes in operation, and to trigger actions when such events
occur.

## Installation

Install the module:

```console
$ npm i @aws-cdk/aws-iotevents
```

Import it into your code:

```python
import aws_cdk.aws_iotevents_alpha as iotevents
```

## `DetectorModel`

The following example creates an AWS IoT Events detector model to your stack.
The detector model need a reference to at least one AWS IoT Events input.
AWS IoT Events inputs enable the detector to get MQTT payload values from IoT Core rules.

You can define built-in actions to use a timer or set a variable, or send data to other AWS resources.
See also [@aws-cdk/aws-iotevents-actions](https://docs.aws.amazon.com/cdk/api/v1/docs/aws-iotevents-actions-readme.html) for other actions.

```python
import aws_cdk.aws_iotevents_alpha as iotevents
import aws_cdk.aws_iotevents_actions_alpha as actions
import aws_cdk.aws_lambda as lambda_

# func: lambda.IFunction


input = iotevents.Input(self, "MyInput",
    input_name="my_input",  # optional
    attribute_json_paths=["payload.deviceId", "payload.temperature"]
)

warm_state = iotevents.State(
    state_name="warm",
    on_enter=[iotevents.Event(
        event_name="test-enter-event",
        condition=iotevents.Expression.current_input(input),
        actions=[actions.LambdaInvokeAction(func)]
    )],
    on_input=[iotevents.Event( # optional
        event_name="test-input-event",
        actions=[actions.LambdaInvokeAction(func)])],
    on_exit=[iotevents.Event( # optional
        event_name="test-exit-event",
        actions=[actions.LambdaInvokeAction(func)])]
)
cold_state = iotevents.State(
    state_name="cold"
)

# transit to coldState when temperature is less than 15
warm_state.transition_to(cold_state,
    event_name="to_coldState",  # optional property, default by combining the names of the States
    when=iotevents.Expression.lt(
        iotevents.Expression.input_attribute(input, "payload.temperature"),
        iotevents.Expression.from_string("15")),
    executing=[actions.LambdaInvokeAction(func)]
)
# transit to warmState when temperature is greater than or equal to 15
cold_state.transition_to(warm_state,
    when=iotevents.Expression.gte(
        iotevents.Expression.input_attribute(input, "payload.temperature"),
        iotevents.Expression.from_string("15"))
)

iotevents.DetectorModel(self, "MyDetectorModel",
    detector_model_name="test-detector-model",  # optional
    description="test-detector-model-description",  # optional property, default is none
    evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
    detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
    initial_state=warm_state
)
```

To grant permissions to put messages in the input,
you can use the `grantWrite()` method:

```python
import aws_cdk.aws_iam as iam
import aws_cdk.aws_iotevents_alpha as iotevents

# grantable: iam.IGrantable

input = iotevents.Input.from_input_name(self, "MyInput", "my_input")

input.grant_write(grantable)
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
import aws_cdk.aws_iam
import aws_cdk.aws_iotevents
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.ActionBindOptions",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class ActionBindOptions:
    def __init__(self, *, role: aws_cdk.aws_iam.IRole) -> None:
        '''(experimental) Options when binding a Action to a detector model.

        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iotevents_alpha as iotevents_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            action_bind_options = iotevents_alpha.ActionBindOptions(
                role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
        }

    @builtins.property
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''(experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.ActionConfig",
    jsii_struct_bases=[],
    name_mapping={"configuration": "configuration"},
)
class ActionConfig:
    def __init__(
        self,
        *,
        configuration: aws_cdk.aws_iotevents.CfnDetectorModel.ActionProperty,
    ) -> None:
        '''(experimental) Properties for a AWS IoT Events action.

        :param configuration: (experimental) The configuration for this action.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iotevents_alpha as iotevents_alpha
            
            action_config = iotevents_alpha.ActionConfig(
                configuration=ActionProperty(
                    clear_timer=ClearTimerProperty(
                        timer_name="timerName"
                    ),
                    dynamo_db=DynamoDBProperty(
                        hash_key_field="hashKeyField",
                        hash_key_value="hashKeyValue",
                        table_name="tableName",
            
                        # the properties below are optional
                        hash_key_type="hashKeyType",
                        operation="operation",
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        payload_field="payloadField",
                        range_key_field="rangeKeyField",
                        range_key_type="rangeKeyType",
                        range_key_value="rangeKeyValue"
                    ),
                    dynamo_dBv2=DynamoDBv2Property(
                        table_name="tableName",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    firehose=FirehoseProperty(
                        delivery_stream_name="deliveryStreamName",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        separator="separator"
                    ),
                    iot_events=IotEventsProperty(
                        input_name="inputName",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    iot_site_wise=IotSiteWiseProperty(
                        property_value=AssetPropertyValueProperty(
                            value=AssetPropertyVariantProperty(
                                boolean_value="booleanValue",
                                double_value="doubleValue",
                                integer_value="integerValue",
                                string_value="stringValue"
                            ),
            
                            # the properties below are optional
                            quality="quality",
                            timestamp=AssetPropertyTimestampProperty(
                                time_in_seconds="timeInSeconds",
            
                                # the properties below are optional
                                offset_in_nanos="offsetInNanos"
                            )
                        ),
            
                        # the properties below are optional
                        asset_id="assetId",
                        entry_id="entryId",
                        property_alias="propertyAlias",
                        property_id="propertyId"
                    ),
                    iot_topic_publish=IotTopicPublishProperty(
                        mqtt_topic="mqttTopic",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    lambda_=LambdaProperty(
                        function_arn="functionArn",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    reset_timer=ResetTimerProperty(
                        timer_name="timerName"
                    ),
                    set_timer=SetTimerProperty(
                        timer_name="timerName",
            
                        # the properties below are optional
                        duration_expression="durationExpression",
                        seconds=123
                    ),
                    set_variable=SetVariableProperty(
                        value="value",
                        variable_name="variableName"
                    ),
                    sns=SnsProperty(
                        target_arn="targetArn",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    sqs=SqsProperty(
                        queue_url="queueUrl",
            
                        # the properties below are optional
                        payload=PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        use_base64=False
                    )
                )
            )
        '''
        if isinstance(configuration, dict):
            configuration = aws_cdk.aws_iotevents.CfnDetectorModel.ActionProperty(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration": configuration,
        }

    @builtins.property
    def configuration(self) -> aws_cdk.aws_iotevents.CfnDetectorModel.ActionProperty:
        '''(experimental) The configuration for this action.

        :stability: experimental
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(aws_cdk.aws_iotevents.CfnDetectorModel.ActionProperty, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.DetectorModelProps",
    jsii_struct_bases=[],
    name_mapping={
        "initial_state": "initialState",
        "description": "description",
        "detector_key": "detectorKey",
        "detector_model_name": "detectorModelName",
        "evaluation_method": "evaluationMethod",
        "role": "role",
    },
)
class DetectorModelProps:
    def __init__(
        self,
        *,
        initial_state: "State",
        description: typing.Optional[builtins.str] = None,
        detector_key: typing.Optional[builtins.str] = None,
        detector_model_name: typing.Optional[builtins.str] = None,
        evaluation_method: typing.Optional["EventEvaluation"] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) Properties for defining an AWS IoT Events detector model.

        :param initial_state: (experimental) The state that is entered at the creation of each detector.
        :param description: (experimental) A brief description of the detector model. Default: none
        :param detector_key: (experimental) The value used to identify a detector instance. When a device or system sends input, a new detector instance with a unique key value is created. AWS IoT Events can continue to route input to its corresponding detector instance based on this identifying information. This parameter uses a JSON-path expression to select the attribute-value pair in the message payload that is used for identification. To route the message to the correct detector instance, the device must send a message payload that contains the same attribute-value. Default: - none (single detector instance will be created and all inputs will be routed to it)
        :param detector_model_name: (experimental) The name of the detector model. Default: - CloudFormation will generate a unique name of the detector model
        :param evaluation_method: (experimental) Information about the order in which events are evaluated and how actions are executed. When setting to SERIAL, variables are updated and event conditions are evaluated in the order that the events are defined. When setting to BATCH, variables within a state are updated and events within a state are performed only after all event conditions are evaluated. Default: EventEvaluation.BATCH
        :param role: (experimental) The role that grants permission to AWS IoT Events to perform its operations. Default: - a role will be created with default permissions

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_iotevents_alpha as iotevents
            import aws_cdk.aws_iotevents_actions_alpha as actions
            import aws_cdk.aws_lambda as lambda_
            
            # func: lambda.IFunction
            
            
            input = iotevents.Input(self, "MyInput",
                input_name="my_input",  # optional
                attribute_json_paths=["payload.deviceId", "payload.temperature"]
            )
            
            warm_state = iotevents.State(
                state_name="warm",
                on_enter=[iotevents.Event(
                    event_name="test-enter-event",
                    condition=iotevents.Expression.current_input(input),
                    actions=[actions.LambdaInvokeAction(func)]
                )],
                on_input=[iotevents.Event( # optional
                    event_name="test-input-event",
                    actions=[actions.LambdaInvokeAction(func)])],
                on_exit=[iotevents.Event( # optional
                    event_name="test-exit-event",
                    actions=[actions.LambdaInvokeAction(func)])]
            )
            cold_state = iotevents.State(
                state_name="cold"
            )
            
            # transit to coldState when temperature is less than 15
            warm_state.transition_to(cold_state,
                event_name="to_coldState",  # optional property, default by combining the names of the States
                when=iotevents.Expression.lt(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15")),
                executing=[actions.LambdaInvokeAction(func)]
            )
            # transit to warmState when temperature is greater than or equal to 15
            cold_state.transition_to(warm_state,
                when=iotevents.Expression.gte(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15"))
            )
            
            iotevents.DetectorModel(self, "MyDetectorModel",
                detector_model_name="test-detector-model",  # optional
                description="test-detector-model-description",  # optional property, default is none
                evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
                detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
                initial_state=warm_state
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "initial_state": initial_state,
        }
        if description is not None:
            self._values["description"] = description
        if detector_key is not None:
            self._values["detector_key"] = detector_key
        if detector_model_name is not None:
            self._values["detector_model_name"] = detector_model_name
        if evaluation_method is not None:
            self._values["evaluation_method"] = evaluation_method
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def initial_state(self) -> "State":
        '''(experimental) The state that is entered at the creation of each detector.

        :stability: experimental
        '''
        result = self._values.get("initial_state")
        assert result is not None, "Required property 'initial_state' is missing"
        return typing.cast("State", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A brief description of the detector model.

        :default: none

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detector_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) The value used to identify a detector instance.

        When a device or system sends input, a new
        detector instance with a unique key value is created. AWS IoT Events can continue to route
        input to its corresponding detector instance based on this identifying information.

        This parameter uses a JSON-path expression to select the attribute-value pair in the message
        payload that is used for identification. To route the message to the correct detector instance,
        the device must send a message payload that contains the same attribute-value.

        :default: - none (single detector instance will be created and all inputs will be routed to it)

        :stability: experimental
        '''
        result = self._values.get("detector_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detector_model_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the detector model.

        :default: - CloudFormation will generate a unique name of the detector model

        :stability: experimental
        '''
        result = self._values.get("detector_model_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def evaluation_method(self) -> typing.Optional["EventEvaluation"]:
        '''(experimental) Information about the order in which events are evaluated and how actions are executed.

        When setting to SERIAL, variables are updated and event conditions are evaluated in the order
        that the events are defined.
        When setting to BATCH, variables within a state are updated and events within a state are
        performed only after all event conditions are evaluated.

        :default: EventEvaluation.BATCH

        :stability: experimental
        '''
        result = self._values.get("evaluation_method")
        return typing.cast(typing.Optional["EventEvaluation"], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The role that grants permission to AWS IoT Events to perform its operations.

        :default: - a role will be created with default permissions

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DetectorModelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.Event",
    jsii_struct_bases=[],
    name_mapping={
        "event_name": "eventName",
        "actions": "actions",
        "condition": "condition",
    },
)
class Event:
    def __init__(
        self,
        *,
        event_name: builtins.str,
        actions: typing.Optional[typing.Sequence["IAction"]] = None,
        condition: typing.Optional["Expression"] = None,
    ) -> None:
        '''(experimental) Specifies the actions to be performed when the condition evaluates to ``true``.

        :param event_name: (experimental) The name of the event.
        :param actions: (experimental) The actions to be performed. Default: - no actions will be performed
        :param condition: (experimental) The Boolean expression that, when ``true``, causes the actions to be performed. Default: - none (the actions are always executed)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iotevents_alpha as iotevents_alpha
            
            # action: iotevents_alpha.IAction
            # expression: iotevents_alpha.Expression
            
            event = iotevents_alpha.Event(
                event_name="eventName",
            
                # the properties below are optional
                actions=[action],
                condition=expression
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_name": event_name,
        }
        if actions is not None:
            self._values["actions"] = actions
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def event_name(self) -> builtins.str:
        '''(experimental) The name of the event.

        :stability: experimental
        '''
        result = self._values.get("event_name")
        assert result is not None, "Required property 'event_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List["IAction"]]:
        '''(experimental) The actions to be performed.

        :default: - no actions will be performed

        :stability: experimental
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List["IAction"]], result)

    @builtins.property
    def condition(self) -> typing.Optional["Expression"]:
        '''(experimental) The Boolean expression that, when ``true``, causes the actions to be performed.

        :default: - none (the actions are always executed)

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional["Expression"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Event(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-iotevents-alpha.EventEvaluation")
class EventEvaluation(enum.Enum):
    '''(experimental) Information about the order in which events are evaluated and how actions are executed.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        import aws_cdk.aws_lambda as lambda_
        
        # func: lambda.IFunction
        
        
        input = iotevents.Input(self, "MyInput",
            input_name="my_input",  # optional
            attribute_json_paths=["payload.deviceId", "payload.temperature"]
        )
        
        warm_state = iotevents.State(
            state_name="warm",
            on_enter=[iotevents.Event(
                event_name="test-enter-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions.LambdaInvokeAction(func)]
            )],
            on_input=[iotevents.Event( # optional
                event_name="test-input-event",
                actions=[actions.LambdaInvokeAction(func)])],
            on_exit=[iotevents.Event( # optional
                event_name="test-exit-event",
                actions=[actions.LambdaInvokeAction(func)])]
        )
        cold_state = iotevents.State(
            state_name="cold"
        )
        
        # transit to coldState when temperature is less than 15
        warm_state.transition_to(cold_state,
            event_name="to_coldState",  # optional property, default by combining the names of the States
            when=iotevents.Expression.lt(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15")),
            executing=[actions.LambdaInvokeAction(func)]
        )
        # transit to warmState when temperature is greater than or equal to 15
        cold_state.transition_to(warm_state,
            when=iotevents.Expression.gte(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15"))
        )
        
        iotevents.DetectorModel(self, "MyDetectorModel",
            detector_model_name="test-detector-model",  # optional
            description="test-detector-model-description",  # optional property, default is none
            evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
            detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
            initial_state=warm_state
        )
    '''

    BATCH = "BATCH"
    '''(experimental) When setting to BATCH, variables within a state are updated and events within a state are performed only after all event conditions are evaluated.

    :stability: experimental
    '''
    SERIAL = "SERIAL"
    '''(experimental) When setting to SERIAL, variables are updated and event conditions are evaluated in the order that the events are defined.

    :stability: experimental
    '''


class Expression(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-iotevents-alpha.Expression",
):
    '''(experimental) Expression for events in Detector Model state.

    :see: https://docs.aws.amazon.com/iotevents/latest/developerguide/iotevents-expressions.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        
        # input: iotevents.IInput
        
        state = iotevents.State(
            state_name="MyState",
            on_enter=[iotevents.Event(
                event_name="test-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions, [
                    actions.SetVariableAction("MyVariable",
                        iotevents.Expression.input_attribute(input, "payload.temperature"))
                ]
                ]
            )]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="and") # type: ignore[misc]
    @builtins.classmethod
    def and_(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the AND operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "and", [left, right]))

    @jsii.member(jsii_name="currentInput") # type: ignore[misc]
    @builtins.classmethod
    def current_input(cls, input: "IInput") -> "Expression":
        '''(experimental) Create a expression for function ``currentInput()``.

        It is evaluated to true if the specified input message was received.

        :param input: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "currentInput", [input]))

    @jsii.member(jsii_name="eq") # type: ignore[misc]
    @builtins.classmethod
    def eq(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Equal operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "eq", [left, right]))

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, value: builtins.str) -> "Expression":
        '''(experimental) Create a expression from the given string.

        :param value: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "fromString", [value]))

    @jsii.member(jsii_name="gt") # type: ignore[misc]
    @builtins.classmethod
    def gt(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Greater Than operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "gt", [left, right]))

    @jsii.member(jsii_name="gte") # type: ignore[misc]
    @builtins.classmethod
    def gte(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Greater Than Or Equal operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "gte", [left, right]))

    @jsii.member(jsii_name="inputAttribute") # type: ignore[misc]
    @builtins.classmethod
    def input_attribute(cls, input: "IInput", path: builtins.str) -> "Expression":
        '''(experimental) Create a expression for get an input attribute as ``$input.TemperatureInput.temperatures[2]``.

        :param input: -
        :param path: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "inputAttribute", [input, path]))

    @jsii.member(jsii_name="lt") # type: ignore[misc]
    @builtins.classmethod
    def lt(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Less Than operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "lt", [left, right]))

    @jsii.member(jsii_name="lte") # type: ignore[misc]
    @builtins.classmethod
    def lte(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Less Than Or Equal operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "lte", [left, right]))

    @jsii.member(jsii_name="neq") # type: ignore[misc]
    @builtins.classmethod
    def neq(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the Not Equal operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "neq", [left, right]))

    @jsii.member(jsii_name="or") # type: ignore[misc]
    @builtins.classmethod
    def or_(cls, left: "Expression", right: "Expression") -> "Expression":
        '''(experimental) Create a expression for the OR operator.

        :param left: -
        :param right: -

        :stability: experimental
        '''
        return typing.cast("Expression", jsii.sinvoke(cls, "or", [left, right]))

    @jsii.member(jsii_name="evaluate") # type: ignore[misc]
    @abc.abstractmethod
    def evaluate(
        self,
        parent_priority: typing.Optional[jsii.Number] = None,
    ) -> builtins.str:
        '''(experimental) This is called to evaluate the expression.

        :param parent_priority: priority of the parent of this expression, used for determining whether or not to add parenthesis around the expression. This is intended to be set according to MDN rules, see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence#table for details

        :stability: experimental
        '''
        ...


class _ExpressionProxy(Expression):
    @jsii.member(jsii_name="evaluate")
    def evaluate(
        self,
        parent_priority: typing.Optional[jsii.Number] = None,
    ) -> builtins.str:
        '''(experimental) This is called to evaluate the expression.

        :param parent_priority: priority of the parent of this expression, used for determining whether or not to add parenthesis around the expression. This is intended to be set according to MDN rules, see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence#table for details

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "evaluate", [parent_priority]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Expression).__jsii_proxy_class__ = lambda : _ExpressionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-iotevents-alpha.IAction")
class IAction(typing_extensions.Protocol):
    '''(experimental) An abstract action for DetectorModel.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> ActionConfig:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        ...


class _IActionProxy:
    '''(experimental) An abstract action for DetectorModel.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-iotevents-alpha.IAction"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> ActionConfig:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        options = ActionBindOptions(role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAction).__jsii_proxy_class__ = lambda : _IActionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-iotevents-alpha.IDetectorModel")
class IDetectorModel(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an AWS IoT Events detector model.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorModelName")
    def detector_model_name(self) -> builtins.str:
        '''(experimental) The name of the detector model.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IDetectorModelProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an AWS IoT Events detector model.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-iotevents-alpha.IDetectorModel"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorModelName")
    def detector_model_name(self) -> builtins.str:
        '''(experimental) The name of the detector model.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "detectorModelName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDetectorModel).__jsii_proxy_class__ = lambda : _IDetectorModelProxy


@jsii.interface(jsii_type="@aws-cdk/aws-iotevents-alpha.IInput")
class IInput(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an AWS IoT Events input.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputArn")
    def input_arn(self) -> builtins.str:
        '''(experimental) The ARN of the input.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the indicated permissions on this input to the given IAM principal (Role/Group/User).

        :param grantee: the principal.
        :param actions: the set of actions to allow (i.e. "iotevents:BatchPutMessage").

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant write permissions on this input and its contents to an IAM principal (Role/Group/User).

        :param grantee: the principal.

        :stability: experimental
        '''
        ...


class _IInputProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an AWS IoT Events input.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-iotevents-alpha.IInput"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputArn")
    def input_arn(self) -> builtins.str:
        '''(experimental) The ARN of the input.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the indicated permissions on this input to the given IAM principal (Role/Group/User).

        :param grantee: the principal.
        :param actions: the set of actions to allow (i.e. "iotevents:BatchPutMessage").

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant write permissions on this input and its contents to an IAM principal (Role/Group/User).

        :param grantee: the principal.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantWrite", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInput).__jsii_proxy_class__ = lambda : _IInputProxy


@jsii.implements(IInput)
class Input(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-alpha.Input",
):
    '''(experimental) Defines an AWS IoT Events input in this stack.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        import aws_cdk.aws_lambda as lambda_
        
        # func: lambda.IFunction
        
        
        input = iotevents.Input(self, "MyInput",
            input_name="my_input",  # optional
            attribute_json_paths=["payload.deviceId", "payload.temperature"]
        )
        
        warm_state = iotevents.State(
            state_name="warm",
            on_enter=[iotevents.Event(
                event_name="test-enter-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions.LambdaInvokeAction(func)]
            )],
            on_input=[iotevents.Event( # optional
                event_name="test-input-event",
                actions=[actions.LambdaInvokeAction(func)])],
            on_exit=[iotevents.Event( # optional
                event_name="test-exit-event",
                actions=[actions.LambdaInvokeAction(func)])]
        )
        cold_state = iotevents.State(
            state_name="cold"
        )
        
        # transit to coldState when temperature is less than 15
        warm_state.transition_to(cold_state,
            event_name="to_coldState",  # optional property, default by combining the names of the States
            when=iotevents.Expression.lt(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15")),
            executing=[actions.LambdaInvokeAction(func)]
        )
        # transit to warmState when temperature is greater than or equal to 15
        cold_state.transition_to(warm_state,
            when=iotevents.Expression.gte(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15"))
        )
        
        iotevents.DetectorModel(self, "MyDetectorModel",
            detector_model_name="test-detector-model",  # optional
            description="test-detector-model-description",  # optional property, default is none
            evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
            detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
            initial_state=warm_state
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        attribute_json_paths: typing.Sequence[builtins.str],
        input_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param attribute_json_paths: (experimental) An expression that specifies an attribute-value pair in a JSON structure. Use this to specify an attribute from the JSON payload that is made available by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage). Each such message contains a JSON payload. The attribute (and its paired value) specified here are available for use in the condition expressions used by detectors.
        :param input_name: (experimental) The name of the input. Default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        '''
        props = InputProps(
            attribute_json_paths=attribute_json_paths, input_name=input_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromInputName") # type: ignore[misc]
    @builtins.classmethod
    def from_input_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        input_name: builtins.str,
    ) -> IInput:
        '''(experimental) Import an existing input.

        :param scope: -
        :param id: -
        :param input_name: -

        :stability: experimental
        '''
        return typing.cast(IInput, jsii.sinvoke(cls, "fromInputName", [scope, id, input_name]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the indicated permissions on this input to the given IAM principal (Role/Group/User).

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant write permissions on this input and its contents to an IAM principal (Role/Group/User).

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputArn")
    def input_arn(self) -> builtins.str:
        '''(experimental) The ARN of the input.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.InputProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_json_paths": "attributeJsonPaths",
        "input_name": "inputName",
    },
)
class InputProps:
    def __init__(
        self,
        *,
        attribute_json_paths: typing.Sequence[builtins.str],
        input_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for defining an AWS IoT Events input.

        :param attribute_json_paths: (experimental) An expression that specifies an attribute-value pair in a JSON structure. Use this to specify an attribute from the JSON payload that is made available by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage). Each such message contains a JSON payload. The attribute (and its paired value) specified here are available for use in the condition expressions used by detectors.
        :param input_name: (experimental) The name of the input. Default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_iotevents_alpha as iotevents
            import aws_cdk.aws_iotevents_actions_alpha as actions
            import aws_cdk.aws_lambda as lambda_
            
            # func: lambda.IFunction
            
            
            input = iotevents.Input(self, "MyInput",
                input_name="my_input",  # optional
                attribute_json_paths=["payload.deviceId", "payload.temperature"]
            )
            
            warm_state = iotevents.State(
                state_name="warm",
                on_enter=[iotevents.Event(
                    event_name="test-enter-event",
                    condition=iotevents.Expression.current_input(input),
                    actions=[actions.LambdaInvokeAction(func)]
                )],
                on_input=[iotevents.Event( # optional
                    event_name="test-input-event",
                    actions=[actions.LambdaInvokeAction(func)])],
                on_exit=[iotevents.Event( # optional
                    event_name="test-exit-event",
                    actions=[actions.LambdaInvokeAction(func)])]
            )
            cold_state = iotevents.State(
                state_name="cold"
            )
            
            # transit to coldState when temperature is less than 15
            warm_state.transition_to(cold_state,
                event_name="to_coldState",  # optional property, default by combining the names of the States
                when=iotevents.Expression.lt(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15")),
                executing=[actions.LambdaInvokeAction(func)]
            )
            # transit to warmState when temperature is greater than or equal to 15
            cold_state.transition_to(warm_state,
                when=iotevents.Expression.gte(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15"))
            )
            
            iotevents.DetectorModel(self, "MyDetectorModel",
                detector_model_name="test-detector-model",  # optional
                description="test-detector-model-description",  # optional property, default is none
                evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
                detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
                initial_state=warm_state
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_json_paths": attribute_json_paths,
        }
        if input_name is not None:
            self._values["input_name"] = input_name

    @builtins.property
    def attribute_json_paths(self) -> typing.List[builtins.str]:
        '''(experimental) An expression that specifies an attribute-value pair in a JSON structure.

        Use this to specify an attribute from the JSON payload that is made available
        by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage).
        Each such message contains a JSON payload. The attribute (and its paired value)
        specified here are available for use in the condition expressions used by detectors.

        :stability: experimental
        '''
        result = self._values.get("attribute_json_paths")
        assert result is not None, "Required property 'attribute_json_paths' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def input_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the input.

        :default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        '''
        result = self._values.get("input_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class State(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-iotevents-alpha.State"):
    '''(experimental) Defines a state of a detector.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        
        # input: iotevents.IInput
        
        state = iotevents.State(
            state_name="MyState",
            on_enter=[iotevents.Event(
                event_name="test-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions, [
                    actions.SetVariableAction("MyVariable",
                        iotevents.Expression.input_attribute(input, "payload.temperature"))
                ]
                ]
            )]
        )
    '''

    def __init__(
        self,
        *,
        state_name: builtins.str,
        on_enter: typing.Optional[typing.Sequence[Event]] = None,
        on_exit: typing.Optional[typing.Sequence[Event]] = None,
        on_input: typing.Optional[typing.Sequence[Event]] = None,
    ) -> None:
        '''
        :param state_name: (experimental) The name of the state.
        :param on_enter: (experimental) Specifies the events on enter. The conditions of the events will be evaluated when entering this state. If the condition of the event evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on entering this state
        :param on_exit: (experimental) Specifies the events on exit. The conditions of the events are evaluated when an exiting this state. If the condition evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on exiting this state
        :param on_input: (experimental) Specifies the events on input. The conditions of the events will be evaluated when any input is received. If the condition of the event evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on input in this state

        :stability: experimental
        '''
        props = StateProps(
            state_name=state_name,
            on_enter=on_enter,
            on_exit=on_exit,
            on_input=on_input,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="transitionTo")
    def transition_to(
        self,
        target_state: "State",
        *,
        when: Expression,
        event_name: typing.Optional[builtins.str] = None,
        executing: typing.Optional[typing.Sequence[IAction]] = None,
    ) -> None:
        '''(experimental) Add a transition event to the state.

        The transition event will be triggered if condition is evaluated to ``true``.

        :param target_state: the state that will be transit to when the event triggered.
        :param when: (experimental) The condition that is used to determine to cause the state transition and the actions. When this was evaluated to ``true``, the state transition and the actions are triggered.
        :param event_name: (experimental) The name of the event. Default: string combining the names of the States as ``${originStateName}_to_${targetStateName}``
        :param executing: (experimental) The actions to be performed with the transition. Default: - no actions will be performed

        :stability: experimental
        '''
        options = TransitionOptions(
            when=when, event_name=event_name, executing=executing
        )

        return typing.cast(None, jsii.invoke(self, "transitionTo", [target_state, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateName")
    def state_name(self) -> builtins.str:
        '''(experimental) The name of the state.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "stateName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.StateProps",
    jsii_struct_bases=[],
    name_mapping={
        "state_name": "stateName",
        "on_enter": "onEnter",
        "on_exit": "onExit",
        "on_input": "onInput",
    },
)
class StateProps:
    def __init__(
        self,
        *,
        state_name: builtins.str,
        on_enter: typing.Optional[typing.Sequence[Event]] = None,
        on_exit: typing.Optional[typing.Sequence[Event]] = None,
        on_input: typing.Optional[typing.Sequence[Event]] = None,
    ) -> None:
        '''(experimental) Properties for defining a state of a detector.

        :param state_name: (experimental) The name of the state.
        :param on_enter: (experimental) Specifies the events on enter. The conditions of the events will be evaluated when entering this state. If the condition of the event evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on entering this state
        :param on_exit: (experimental) Specifies the events on exit. The conditions of the events are evaluated when an exiting this state. If the condition evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on exiting this state
        :param on_input: (experimental) Specifies the events on input. The conditions of the events will be evaluated when any input is received. If the condition of the event evaluates to ``true``, the actions of the event will be executed. Default: - no events will trigger on input in this state

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            import aws_cdk.aws_iotevents_alpha as iotevents
            import aws_cdk.aws_iotevents_actions_alpha as actions
            
            # input: iotevents.IInput
            
            state = iotevents.State(
                state_name="MyState",
                on_enter=[iotevents.Event(
                    event_name="test-event",
                    condition=iotevents.Expression.current_input(input),
                    actions=[actions, [
                        actions.SetVariableAction("MyVariable",
                            iotevents.Expression.input_attribute(input, "payload.temperature"))
                    ]
                    ]
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "state_name": state_name,
        }
        if on_enter is not None:
            self._values["on_enter"] = on_enter
        if on_exit is not None:
            self._values["on_exit"] = on_exit
        if on_input is not None:
            self._values["on_input"] = on_input

    @builtins.property
    def state_name(self) -> builtins.str:
        '''(experimental) The name of the state.

        :stability: experimental
        '''
        result = self._values.get("state_name")
        assert result is not None, "Required property 'state_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def on_enter(self) -> typing.Optional[typing.List[Event]]:
        '''(experimental) Specifies the events on enter.

        The conditions of the events will be evaluated when entering this state.
        If the condition of the event evaluates to ``true``, the actions of the event will be executed.

        :default: - no events will trigger on entering this state

        :stability: experimental
        '''
        result = self._values.get("on_enter")
        return typing.cast(typing.Optional[typing.List[Event]], result)

    @builtins.property
    def on_exit(self) -> typing.Optional[typing.List[Event]]:
        '''(experimental) Specifies the events on exit.

        The conditions of the events are evaluated when an exiting this state.
        If the condition evaluates to ``true``, the actions of the event will be executed.

        :default: - no events will trigger on exiting this state

        :stability: experimental
        '''
        result = self._values.get("on_exit")
        return typing.cast(typing.Optional[typing.List[Event]], result)

    @builtins.property
    def on_input(self) -> typing.Optional[typing.List[Event]]:
        '''(experimental) Specifies the events on input.

        The conditions of the events will be evaluated when any input is received.
        If the condition of the event evaluates to ``true``, the actions of the event will be executed.

        :default: - no events will trigger on input in this state

        :stability: experimental
        '''
        result = self._values.get("on_input")
        return typing.cast(typing.Optional[typing.List[Event]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.TransitionOptions",
    jsii_struct_bases=[],
    name_mapping={"when": "when", "event_name": "eventName", "executing": "executing"},
)
class TransitionOptions:
    def __init__(
        self,
        *,
        when: Expression,
        event_name: typing.Optional[builtins.str] = None,
        executing: typing.Optional[typing.Sequence[IAction]] = None,
    ) -> None:
        '''(experimental) Properties for options of state transition.

        :param when: (experimental) The condition that is used to determine to cause the state transition and the actions. When this was evaluated to ``true``, the state transition and the actions are triggered.
        :param event_name: (experimental) The name of the event. Default: string combining the names of the States as ``${originStateName}_to_${targetStateName}``
        :param executing: (experimental) The actions to be performed with the transition. Default: - no actions will be performed

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_iotevents_alpha as iotevents
            import aws_cdk.aws_iotevents_actions_alpha as actions
            import aws_cdk.aws_lambda as lambda_
            
            # func: lambda.IFunction
            
            
            input = iotevents.Input(self, "MyInput",
                input_name="my_input",  # optional
                attribute_json_paths=["payload.deviceId", "payload.temperature"]
            )
            
            warm_state = iotevents.State(
                state_name="warm",
                on_enter=[iotevents.Event(
                    event_name="test-enter-event",
                    condition=iotevents.Expression.current_input(input),
                    actions=[actions.LambdaInvokeAction(func)]
                )],
                on_input=[iotevents.Event( # optional
                    event_name="test-input-event",
                    actions=[actions.LambdaInvokeAction(func)])],
                on_exit=[iotevents.Event( # optional
                    event_name="test-exit-event",
                    actions=[actions.LambdaInvokeAction(func)])]
            )
            cold_state = iotevents.State(
                state_name="cold"
            )
            
            # transit to coldState when temperature is less than 15
            warm_state.transition_to(cold_state,
                event_name="to_coldState",  # optional property, default by combining the names of the States
                when=iotevents.Expression.lt(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15")),
                executing=[actions.LambdaInvokeAction(func)]
            )
            # transit to warmState when temperature is greater than or equal to 15
            cold_state.transition_to(warm_state,
                when=iotevents.Expression.gte(
                    iotevents.Expression.input_attribute(input, "payload.temperature"),
                    iotevents.Expression.from_string("15"))
            )
            
            iotevents.DetectorModel(self, "MyDetectorModel",
                detector_model_name="test-detector-model",  # optional
                description="test-detector-model-description",  # optional property, default is none
                evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
                detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
                initial_state=warm_state
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "when": when,
        }
        if event_name is not None:
            self._values["event_name"] = event_name
        if executing is not None:
            self._values["executing"] = executing

    @builtins.property
    def when(self) -> Expression:
        '''(experimental) The condition that is used to determine to cause the state transition and the actions.

        When this was evaluated to ``true``, the state transition and the actions are triggered.

        :stability: experimental
        '''
        result = self._values.get("when")
        assert result is not None, "Required property 'when' is missing"
        return typing.cast(Expression, result)

    @builtins.property
    def event_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the event.

        :default: string combining the names of the States as ``${originStateName}_to_${targetStateName}``

        :stability: experimental
        '''
        result = self._values.get("event_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def executing(self) -> typing.Optional[typing.List[IAction]]:
        '''(experimental) The actions to be performed with the transition.

        :default: - no actions will be performed

        :stability: experimental
        '''
        result = self._values.get("executing")
        return typing.cast(typing.Optional[typing.List[IAction]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransitionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IDetectorModel)
class DetectorModel(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-alpha.DetectorModel",
):
    '''(experimental) Defines an AWS IoT Events detector model in this stack.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iotevents_alpha as iotevents
        import aws_cdk.aws_iotevents_actions_alpha as actions
        import aws_cdk.aws_lambda as lambda_
        
        # func: lambda.IFunction
        
        
        input = iotevents.Input(self, "MyInput",
            input_name="my_input",  # optional
            attribute_json_paths=["payload.deviceId", "payload.temperature"]
        )
        
        warm_state = iotevents.State(
            state_name="warm",
            on_enter=[iotevents.Event(
                event_name="test-enter-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions.LambdaInvokeAction(func)]
            )],
            on_input=[iotevents.Event( # optional
                event_name="test-input-event",
                actions=[actions.LambdaInvokeAction(func)])],
            on_exit=[iotevents.Event( # optional
                event_name="test-exit-event",
                actions=[actions.LambdaInvokeAction(func)])]
        )
        cold_state = iotevents.State(
            state_name="cold"
        )
        
        # transit to coldState when temperature is less than 15
        warm_state.transition_to(cold_state,
            event_name="to_coldState",  # optional property, default by combining the names of the States
            when=iotevents.Expression.lt(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15")),
            executing=[actions.LambdaInvokeAction(func)]
        )
        # transit to warmState when temperature is greater than or equal to 15
        cold_state.transition_to(warm_state,
            when=iotevents.Expression.gte(
                iotevents.Expression.input_attribute(input, "payload.temperature"),
                iotevents.Expression.from_string("15"))
        )
        
        iotevents.DetectorModel(self, "MyDetectorModel",
            detector_model_name="test-detector-model",  # optional
            description="test-detector-model-description",  # optional property, default is none
            evaluation_method=iotevents.EventEvaluation.SERIAL,  # optional property, default is iotevents.EventEvaluation.BATCH
            detector_key="payload.deviceId",  # optional property, default is none and single detector instance will be created and all inputs will be routed to it
            initial_state=warm_state
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_state: State,
        description: typing.Optional[builtins.str] = None,
        detector_key: typing.Optional[builtins.str] = None,
        detector_model_name: typing.Optional[builtins.str] = None,
        evaluation_method: typing.Optional[EventEvaluation] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param initial_state: (experimental) The state that is entered at the creation of each detector.
        :param description: (experimental) A brief description of the detector model. Default: none
        :param detector_key: (experimental) The value used to identify a detector instance. When a device or system sends input, a new detector instance with a unique key value is created. AWS IoT Events can continue to route input to its corresponding detector instance based on this identifying information. This parameter uses a JSON-path expression to select the attribute-value pair in the message payload that is used for identification. To route the message to the correct detector instance, the device must send a message payload that contains the same attribute-value. Default: - none (single detector instance will be created and all inputs will be routed to it)
        :param detector_model_name: (experimental) The name of the detector model. Default: - CloudFormation will generate a unique name of the detector model
        :param evaluation_method: (experimental) Information about the order in which events are evaluated and how actions are executed. When setting to SERIAL, variables are updated and event conditions are evaluated in the order that the events are defined. When setting to BATCH, variables within a state are updated and events within a state are performed only after all event conditions are evaluated. Default: EventEvaluation.BATCH
        :param role: (experimental) The role that grants permission to AWS IoT Events to perform its operations. Default: - a role will be created with default permissions

        :stability: experimental
        '''
        props = DetectorModelProps(
            initial_state=initial_state,
            description=description,
            detector_key=detector_key,
            detector_model_name=detector_model_name,
            evaluation_method=evaluation_method,
            role=role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDetectorModelName") # type: ignore[misc]
    @builtins.classmethod
    def from_detector_model_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        detector_model_name: builtins.str,
    ) -> IDetectorModel:
        '''(experimental) Import an existing detector model.

        :param scope: -
        :param id: -
        :param detector_model_name: -

        :stability: experimental
        '''
        return typing.cast(IDetectorModel, jsii.sinvoke(cls, "fromDetectorModelName", [scope, id, detector_model_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorModelName")
    def detector_model_name(self) -> builtins.str:
        '''(experimental) The name of the detector model.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "detectorModelName"))


__all__ = [
    "ActionBindOptions",
    "ActionConfig",
    "DetectorModel",
    "DetectorModelProps",
    "Event",
    "EventEvaluation",
    "Expression",
    "IAction",
    "IDetectorModel",
    "IInput",
    "Input",
    "InputProps",
    "State",
    "StateProps",
    "TransitionOptions",
]

publication.publish()
