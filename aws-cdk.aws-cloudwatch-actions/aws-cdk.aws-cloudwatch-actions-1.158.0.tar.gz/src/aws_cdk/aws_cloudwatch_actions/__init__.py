'''
# CloudWatch Alarm Actions library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains a set of classes which can be used as CloudWatch Alarm actions.

The currently implemented actions are: EC2 Actions, SNS Actions, SSM OpsCenter Actions, Autoscaling Actions and Application Autoscaling Actions

## EC2 Action Example

```python
# Alarm must be configured with an EC2 per-instance metric
# alarm: cloudwatch.Alarm

# Attach a reboot when alarm triggers
alarm.add_alarm_action(
    actions.Ec2Action(actions.Ec2InstanceAction.REBOOT))
```

## SSM OpsCenter Action Example

```python
# alarm: cloudwatch.Alarm

# Create an OpsItem with specific severity and category when alarm triggers
alarm.add_alarm_action(
    actions.SsmAction(actions.OpsItemSeverity.CRITICAL, actions.OpsItemCategory.PERFORMANCE))
```

See `@aws-cdk/aws-cloudwatch` for more information.
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

import aws_cdk.aws_applicationautoscaling
import aws_cdk.aws_autoscaling
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_sns
import aws_cdk.core


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class ApplicationScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-cloudwatch-actions.ApplicationScalingAction",
):
    '''Use an ApplicationAutoScaling StepScalingAction as an Alarm Action.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_applicationautoscaling as appscaling
        import aws_cdk.aws_cloudwatch_actions as cloudwatch_actions
        
        # step_scaling_action: appscaling.StepScalingAction
        
        application_scaling_action = cloudwatch_actions.ApplicationScalingAction(step_scaling_action)
    '''

    def __init__(
        self,
        step_scaling_action: aws_cdk.aws_applicationautoscaling.StepScalingAction,
    ) -> None:
        '''
        :param step_scaling_action: -
        '''
        jsii.create(self.__class__, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _alarm: aws_cdk.aws_cloudwatch.IAlarm,
    ) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        '''Returns an alarm action configuration to use an ApplicationScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.AlarmActionConfig, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class AutoScalingAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-cloudwatch-actions.AutoScalingAction",
):
    '''Use an AutoScaling StepScalingAction as an Alarm Action.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling as autoscaling
        import aws_cdk.aws_cloudwatch_actions as cloudwatch_actions
        
        # step_scaling_action: autoscaling.StepScalingAction
        
        auto_scaling_action = cloudwatch_actions.AutoScalingAction(step_scaling_action)
    '''

    def __init__(
        self,
        step_scaling_action: aws_cdk.aws_autoscaling.StepScalingAction,
    ) -> None:
        '''
        :param step_scaling_action: -
        '''
        jsii.create(self.__class__, self, [step_scaling_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _alarm: aws_cdk.aws_cloudwatch.IAlarm,
    ) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        '''Returns an alarm action configuration to use an AutoScaling StepScalingAction as an alarm action.

        :param _scope: -
        :param _alarm: -
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.AlarmActionConfig, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class Ec2Action(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-cloudwatch-actions.Ec2Action",
):
    '''Use an EC2 action as an Alarm action.

    :exampleMetadata: infused

    Example::

        # Alarm must be configured with an EC2 per-instance metric
        # alarm: cloudwatch.Alarm
        
        # Attach a reboot when alarm triggers
        alarm.add_alarm_action(
            actions.Ec2Action(actions.Ec2InstanceAction.REBOOT))
    '''

    def __init__(self, instance_action: "Ec2InstanceAction") -> None:
        '''
        :param instance_action: -
        '''
        jsii.create(self.__class__, self, [instance_action])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _alarm: aws_cdk.aws_cloudwatch.IAlarm,
    ) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        '''Returns an alarm action configuration to use an EC2 action as an alarm action.

        :param _scope: -
        :param _alarm: -
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.AlarmActionConfig, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch-actions.Ec2InstanceAction")
class Ec2InstanceAction(enum.Enum):
    '''Types of EC2 actions available.

    :exampleMetadata: infused

    Example::

        # Alarm must be configured with an EC2 per-instance metric
        # alarm: cloudwatch.Alarm
        
        # Attach a reboot when alarm triggers
        alarm.add_alarm_action(
            actions.Ec2Action(actions.Ec2InstanceAction.REBOOT))
    '''

    STOP = "STOP"
    '''Stop the instance.'''
    TERMINATE = "TERMINATE"
    '''Terminatethe instance.'''
    RECOVER = "RECOVER"
    '''Recover the instance.'''
    REBOOT = "REBOOT"
    '''Reboot the instance.'''


@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch-actions.OpsItemCategory")
class OpsItemCategory(enum.Enum):
    '''Types of OpsItem category available.

    :exampleMetadata: infused

    Example::

        # alarm: cloudwatch.Alarm
        
        # Create an OpsItem with specific severity and category when alarm triggers
        alarm.add_alarm_action(
            actions.SsmAction(actions.OpsItemSeverity.CRITICAL, actions.OpsItemCategory.PERFORMANCE))
    '''

    AVAILABILITY = "AVAILABILITY"
    '''Set the category to availability.'''
    COST = "COST"
    '''Set the category to cost.'''
    PERFORMANCE = "PERFORMANCE"
    '''Set the category to performance.'''
    RECOVERY = "RECOVERY"
    '''Set the category to recovery.'''
    SECURITY = "SECURITY"
    '''Set the category to security.'''


@jsii.enum(jsii_type="@aws-cdk/aws-cloudwatch-actions.OpsItemSeverity")
class OpsItemSeverity(enum.Enum):
    '''Types of OpsItem severity available.

    :exampleMetadata: infused

    Example::

        # alarm: cloudwatch.Alarm
        
        # Create an OpsItem with specific severity and category when alarm triggers
        alarm.add_alarm_action(
            actions.SsmAction(actions.OpsItemSeverity.CRITICAL, actions.OpsItemCategory.PERFORMANCE))
    '''

    CRITICAL = "CRITICAL"
    '''Set the severity to critical.'''
    HIGH = "HIGH"
    '''Set the severity to high.'''
    MEDIUM = "MEDIUM"
    '''Set the severity to medium.'''
    LOW = "LOW"
    '''Set the severity to low.'''


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class SnsAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-cloudwatch-actions.SnsAction",
):
    '''Use an SNS topic as an alarm action.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_cloudwatch_actions as cw_actions
        # alarm: cloudwatch.Alarm
        
        
        topic = sns.Topic(self, "Topic")
        alarm.add_alarm_action(cw_actions.SnsAction(topic))
    '''

    def __init__(self, topic: aws_cdk.aws_sns.ITopic) -> None:
        '''
        :param topic: -
        '''
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _alarm: aws_cdk.aws_cloudwatch.IAlarm,
    ) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        '''Returns an alarm action configuration to use an SNS topic as an alarm action.

        :param _scope: -
        :param _alarm: -
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.AlarmActionConfig, jsii.invoke(self, "bind", [_scope, _alarm]))


@jsii.implements(aws_cdk.aws_cloudwatch.IAlarmAction)
class SsmAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-cloudwatch-actions.SsmAction",
):
    '''Use an SSM OpsItem action as an Alarm action.

    :exampleMetadata: infused

    Example::

        # alarm: cloudwatch.Alarm
        
        # Create an OpsItem with specific severity and category when alarm triggers
        alarm.add_alarm_action(
            actions.SsmAction(actions.OpsItemSeverity.CRITICAL, actions.OpsItemCategory.PERFORMANCE))
    '''

    def __init__(
        self,
        severity: OpsItemSeverity,
        category: typing.Optional[OpsItemCategory] = None,
    ) -> None:
        '''
        :param severity: -
        :param category: -
        '''
        jsii.create(self.__class__, self, [severity, category])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: aws_cdk.core.Construct,
        _alarm: aws_cdk.aws_cloudwatch.IAlarm,
    ) -> aws_cdk.aws_cloudwatch.AlarmActionConfig:
        '''Returns an alarm action configuration to use an SSM OpsItem action as an alarm action.

        :param _scope: -
        :param _alarm: -
        '''
        return typing.cast(aws_cdk.aws_cloudwatch.AlarmActionConfig, jsii.invoke(self, "bind", [_scope, _alarm]))


__all__ = [
    "ApplicationScalingAction",
    "AutoScalingAction",
    "Ec2Action",
    "Ec2InstanceAction",
    "OpsItemCategory",
    "OpsItemSeverity",
    "SnsAction",
    "SsmAction",
]

publication.publish()
