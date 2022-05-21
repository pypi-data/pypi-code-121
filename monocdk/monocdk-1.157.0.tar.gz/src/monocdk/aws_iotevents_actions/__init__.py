'''
# Actions for AWS::IoTEvents Detector Model

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
import monocdk as iotevents
import monocdk as actions

# input: iotevents.IInput


state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.aws_iotevents.Event(
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
# Example automatically generated from non-compiling source. May contain errors.
import monocdk as iotevents
import monocdk as actions
import monocdk as lambda_

# input: iotevents.IInput
# func: lambda.IFunction


state = iotevents.State(
    state_name="MyState",
    on_enter=[iotevents.aws_iotevents.Event(
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

from .._jsii import *

import constructs
from ..aws_iam import IRole as _IRole_59af6f50
from ..aws_iotevents import (
    ActionBindOptions as _ActionBindOptions_0c945204,
    ActionConfig as _ActionConfig_f562c03c,
    Expression as _Expression_40d1cdd7,
    IAction as _IAction_79ea629c,
)
from ..aws_lambda import IFunction as _IFunction_6e14f09e


@jsii.implements(_IAction_79ea629c)
class LambdaInvokeAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_iotevents_actions.LambdaInvokeAction",
):
    '''(experimental) The action to write the data to an AWS Lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as iotevents
        import monocdk as actions
        import monocdk as lambda_
        
        # func: lambda.IFunction
        
        
        input = iotevents.Input(self, "MyInput",
            input_name="my_input",  # optional
            attribute_json_paths=["payload.deviceId", "payload.temperature"]
        )
        
        warm_state = iotevents.State(
            state_name="warm",
            on_enter=[iotevents.aws_iotevents.Event(
                event_name="test-enter-event",
                condition=iotevents.Expression.current_input(input),
                actions=[actions.LambdaInvokeAction(func)]
            )],
            on_input=[iotevents.aws_iotevents.Event( # optional
                event_name="test-input-event",
                actions=[actions.LambdaInvokeAction(func)])],
            on_exit=[iotevents.aws_iotevents.Event( # optional
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

    def __init__(self, func: _IFunction_6e14f09e) -> None:
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
        role: _IRole_59af6f50,
    ) -> _ActionConfig_f562c03c:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        options = _ActionBindOptions_0c945204(role=role)

        return typing.cast(_ActionConfig_f562c03c, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(_IAction_79ea629c)
class SetVariableAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_iotevents_actions.SetVariableAction",
):
    '''(experimental) The action to create a variable with a specified value.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import monocdk as iotevents
        import monocdk as actions
        
        # input: iotevents.IInput
        
        
        state = iotevents.State(
            state_name="MyState",
            on_enter=[iotevents.aws_iotevents.Event(
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
        value: _Expression_40d1cdd7,
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
        role: _IRole_59af6f50,
    ) -> _ActionConfig_f562c03c:
        '''(experimental) Returns the AWS IoT Events action specification.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by IoT Events to perform the action.

        :stability: experimental
        '''
        _options = _ActionBindOptions_0c945204(role=role)

        return typing.cast(_ActionConfig_f562c03c, jsii.invoke(self, "bind", [_scope, _options]))


__all__ = [
    "LambdaInvokeAction",
    "SetVariableAction",
]

publication.publish()
