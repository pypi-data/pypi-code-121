'''
# Actions for AWS::IoTEvents Detector Model

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This library contains integration classes to specify actions of state events of Detector Model in `@aws-cdk/aws-iotevents`.
Instances of these classes should be passed to `State` defined in `@aws-cdk/aws-iotevents`
You can define built-in actions to use a timer or set a variable, or send data to other AWS resources.

This library contains integration classes to use a timer or set a variable, or send data to other AWS resources.
AWS IoT Events can trigger actions when it detects a specified event or transition event.

Currently supported are:

* Set variable to detector instanse
* Invoke a Lambda function

## Set variable to detector instanse

The code snippet below creates an Action that set variable to detector instanse
when it is triggered.

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_iotevents as iotevents
import aws_cdk.aws_iotevents_actions as actions

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
```

## Invoke a Lambda function

The code snippet below creates an Action that invoke a Lambda function
when it is triggered.

```python
import aws_cdk.aws_iotevents as iotevents
import aws_cdk.aws_iotevents_actions as actions
import aws_cdk.aws_lambda as lambda_

# input: iotevents.IInput
# func: lambda.IFunction

state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.Event(
        event_name="test-event",
        condition=iotevents.Expression.current_input(input),
        actions=[actions.LambdaInvokeAction(func)]
    )]
)
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

import aws_cdk.aws_iam
import aws_cdk.aws_iotevents
import aws_cdk.aws_lambda
import constructs


@jsii.implements(aws_cdk.aws_iotevents.IAction)
class LambdaInvokeAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions.LambdaInvokeAction",
):
    '''(experimental) The action to write the data to an AWS Lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iotevents as iotevents
        import aws_cdk.aws_iotevents_actions as actions
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

    def __init__(self, func: aws_cdk.aws_lambda.IFunction) -> None:
        '''
        :param func: the AWS Lambda function to be invoked by this action.

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [func])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> aws_cdk.aws_iotevents.ActionConfig:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        options = aws_cdk.aws_iotevents.ActionBindOptions(role=role)

        return typing.cast(aws_cdk.aws_iotevents.ActionConfig, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(aws_cdk.aws_iotevents.IAction)
class SetVariableAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-actions.SetVariableAction",
):
    '''(experimental) The action to create a variable with a specified value.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_iotevents as iotevents
        import aws_cdk.aws_iotevents_actions as actions
        
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
        variable_name: builtins.str,
        value: aws_cdk.aws_iotevents.Expression,
    ) -> None:
        '''
        :param variable_name: the name of the variable.
        :param value: the new value of the variable.

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [variable_name, value])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> aws_cdk.aws_iotevents.ActionConfig:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        _options = aws_cdk.aws_iotevents.ActionBindOptions(role=role)

        return typing.cast(aws_cdk.aws_iotevents.ActionConfig, jsii.invoke(self, "bind", [_scope, _options]))


__all__ = [
    "LambdaInvokeAction",
    "SetVariableAction",
]

publication.publish()
