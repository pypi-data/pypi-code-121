'''
Construct as part of the IDP processing suite.

Takes a reference to an object on S3 and analyzes it and outputs a manifest definition for the IDP process.

# Input

```javascript
{
  "s3_bucket": "somebucket",
  "s3_key": "someprefix/someobject"
}
```

# Output

Manifest definition example

```javascript
{
  "manifest": {
    "S3Path": "s3://my-stack-dev-documentbucket04c71448-19ew04s4uhy8t/uploads"
  },
  "mime": "application/pdf",
  "classification": null,
  "numberOfPages": 12
}
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

import aws_cdk.aws_stepfunctions
import constructs


@jsii.data_type(
    jsii_type="schadem-cdk-construct-sfn-idp-decider.TextractDPPOCDeciderProps",
    jsii_struct_bases=[],
    name_mapping={
        "default_classification": "defaultClassification",
        "lambda_memory_mb": "lambdaMemoryMB",
    },
)
class TextractDPPOCDeciderProps:
    def __init__(
        self,
        *,
        default_classification: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param default_classification: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default_classification is not None:
            self._values["default_classification"] = default_classification
        if lambda_memory_mb is not None:
            self._values["lambda_memory_mb"] = lambda_memory_mb

    @builtins.property
    def default_classification(self) -> typing.Optional[builtins.str]:
        result = self._values.get("default_classification")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_memory_mb(self) -> typing.Optional[jsii.Number]:
        '''memory of Lambda function (may need to increase for larger documents).'''
        result = self._values.get("lambda_memory_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TextractDPPOCDeciderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TextractPOCDecider(
    aws_cdk.aws_stepfunctions.StateMachineFragment,
    metaclass=jsii.JSIIMeta,
    jsii_type="schadem-cdk-construct-sfn-idp-decider.TextractPOCDecider",
):
    def __init__(
        self,
        parent: constructs.Construct,
        id: builtins.str,
        *,
        default_classification: typing.Optional[builtins.str] = None,
        lambda_memory_mb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: -
        :param default_classification: 
        :param lambda_memory_mb: memory of Lambda function (may need to increase for larger documents).
        '''
        props = TextractDPPOCDeciderProps(
            default_classification=default_classification,
            lambda_memory_mb=lambda_memory_mb,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[aws_cdk.aws_stepfunctions.INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[aws_cdk.aws_stepfunctions.INextable], jsii.get(self, "endStates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startState")
    def start_state(self) -> aws_cdk.aws_stepfunctions.State:
        '''The start state of this state machine fragment.'''
        return typing.cast(aws_cdk.aws_stepfunctions.State, jsii.get(self, "startState"))


__all__ = [
    "TextractDPPOCDeciderProps",
    "TextractPOCDecider",
]

publication.publish()
