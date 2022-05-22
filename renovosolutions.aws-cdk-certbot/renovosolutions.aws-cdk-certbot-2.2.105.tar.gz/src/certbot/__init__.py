'''
# cdk-library-certbot

[![build](https://github.com/RenovoSolutions/cdk-library-certbot/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-library-certbotactions/workflows/build.yml)

A CDK Construct Library to automate the creation and renewal of Let's Encrypt certificates.

## Features

* Creates a lambda function that utilizes Certbot to request a certificate from Let's Encrypt
* Uploads the resulting certificate data to S3 for later retrieval
* Imports the certificate to AWS Certificate Manager for tracking expiration
* Creates a trigger to re-run and re-new if the cert will expire in the next 30 days (customizable)

## API Doc

See [API](API.md)

## References

Original [gist](# Modified from original gist https://gist.github.com/arkadiyt/5d764c32baa43fc486ca16cb8488169a) that was modified for the Lambda code

## Examples

This construct utilizes a Route 53 hosted zone lookup so it will require that your stack has [environment variables set for account and region](See https://docs.aws.amazon.com/cdk/latest/guide/environments.html for more details.).

### Typescript

```
import * as cdk from '@aws-cdk/core';
import { Certbot } from '@renovosolutions/cdk-library-certbot';
import { Architecture } from '@aws-cdk/aws-lambda';

export class CdkExampleCertsStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    let domains = [
      'example.com',
      'www.example.com'
    ]

    new Certbot(this, 'cert', {
      letsencryptDomains: domains.join(','),
      letsencryptEmail: 'webmaster+letsencrypt@example.com',
      hostedZoneNames: [
        'example.com'
      ]
    })
  }
}

```

## Python

```
from aws_cdk import (
    core as cdk
)
from certbot import Certbot

class CdkExampleCertsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Certbot(self, "certbot",
            letsencrypt_email="webmaster+letsencrypt@example.com",
            letsencrypt_domains="example.com",
            hosted_zone_names=["example.com"]
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

import aws_cdk
import aws_cdk.aws_events
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_sns
import constructs


class Certbot(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-certbot.Certbot",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hosted_zone_names: typing.Sequence[builtins.str],
        letsencrypt_domains: builtins.str,
        letsencrypt_email: builtins.str,
        bucket: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        enable_insights: typing.Optional[builtins.bool] = None,
        enable_object_deletion: typing.Optional[builtins.bool] = None,
        function_description: typing.Optional[builtins.str] = None,
        function_name: typing.Optional[builtins.str] = None,
        insights_arn: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        object_prefix: typing.Optional[builtins.str] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        re_issue_days: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        run_on_deploy: typing.Optional[builtins.bool] = None,
        run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.Topic] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone_names: Hosted zone names that will be required for DNS verification with certbot.
        :param letsencrypt_domains: The comma delimited list of domains for which the Let's Encrypt certificate will be valid. Primary domain should be first.
        :param letsencrypt_email: The email to associate with the Let's Encrypt certificate request.
        :param bucket: The S3 bucket to place the resulting certificates in. If no bucket is given one will be created automatically.
        :param enable_insights: Whether or not to enable Lambda Insights. Default: false
        :param enable_object_deletion: Whether or not to enable automatic object deletion if the provided bucket is deleted. Has no effect if a bucket is given as a property Default: false
        :param function_description: The description for the resulting Lambda function.
        :param function_name: The name of the resulting Lambda function.
        :param insights_arn: Insights layer ARN for your region. Defaults to layer for US-EAST-1
        :param layers: Any additional Lambda layers to use with the created function. For example Lambda Extensions
        :param object_prefix: The prefix to apply to the final S3 key name for the certificates. Default is no prefix.
        :param preferred_chain: Set the preferred certificate chain. Default: 'None'
        :param re_issue_days: The numbers of days left until the prior cert expires before issuing a new one. Default: 30
        :param removal_policy: The removal policy for the S3 bucket that is automatically created. Has no effect if a bucket is given as a property Default: RemovalPolicy.RETAIN
        :param run_on_deploy: Whether or not to schedule a trigger to run the function after each deployment. Default: true
        :param run_on_deploy_wait_minutes: How many minutes to wait before running the post deployment Lambda trigger. Default: 10
        :param schedule: The schedule for the certificate check trigger. Default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        :param sns_topic: The SNS topic to notify when a new cert is issued. If no topic is given one will be created automatically.
        :param timeout: The timeout duration for Lambda function. Default: Duraction.seconds(180)
        '''
        props = CertbotProps(
            hosted_zone_names=hosted_zone_names,
            letsencrypt_domains=letsencrypt_domains,
            letsencrypt_email=letsencrypt_email,
            bucket=bucket,
            enable_insights=enable_insights,
            enable_object_deletion=enable_object_deletion,
            function_description=function_description,
            function_name=function_name,
            insights_arn=insights_arn,
            layers=layers,
            object_prefix=object_prefix,
            preferred_chain=preferred_chain,
            re_issue_days=re_issue_days,
            removal_policy=removal_policy,
            run_on_deploy=run_on_deploy,
            run_on_deploy_wait_minutes=run_on_deploy_wait_minutes,
            schedule=schedule,
            sns_topic=sns_topic,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-certbot.CertbotProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone_names": "hostedZoneNames",
        "letsencrypt_domains": "letsencryptDomains",
        "letsencrypt_email": "letsencryptEmail",
        "bucket": "bucket",
        "enable_insights": "enableInsights",
        "enable_object_deletion": "enableObjectDeletion",
        "function_description": "functionDescription",
        "function_name": "functionName",
        "insights_arn": "insightsARN",
        "layers": "layers",
        "object_prefix": "objectPrefix",
        "preferred_chain": "preferredChain",
        "re_issue_days": "reIssueDays",
        "removal_policy": "removalPolicy",
        "run_on_deploy": "runOnDeploy",
        "run_on_deploy_wait_minutes": "runOnDeployWaitMinutes",
        "schedule": "schedule",
        "sns_topic": "snsTopic",
        "timeout": "timeout",
    },
)
class CertbotProps:
    def __init__(
        self,
        *,
        hosted_zone_names: typing.Sequence[builtins.str],
        letsencrypt_domains: builtins.str,
        letsencrypt_email: builtins.str,
        bucket: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        enable_insights: typing.Optional[builtins.bool] = None,
        enable_object_deletion: typing.Optional[builtins.bool] = None,
        function_description: typing.Optional[builtins.str] = None,
        function_name: typing.Optional[builtins.str] = None,
        insights_arn: typing.Optional[builtins.str] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        object_prefix: typing.Optional[builtins.str] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        re_issue_days: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        run_on_deploy: typing.Optional[builtins.bool] = None,
        run_on_deploy_wait_minutes: typing.Optional[jsii.Number] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.Topic] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param hosted_zone_names: Hosted zone names that will be required for DNS verification with certbot.
        :param letsencrypt_domains: The comma delimited list of domains for which the Let's Encrypt certificate will be valid. Primary domain should be first.
        :param letsencrypt_email: The email to associate with the Let's Encrypt certificate request.
        :param bucket: The S3 bucket to place the resulting certificates in. If no bucket is given one will be created automatically.
        :param enable_insights: Whether or not to enable Lambda Insights. Default: false
        :param enable_object_deletion: Whether or not to enable automatic object deletion if the provided bucket is deleted. Has no effect if a bucket is given as a property Default: false
        :param function_description: The description for the resulting Lambda function.
        :param function_name: The name of the resulting Lambda function.
        :param insights_arn: Insights layer ARN for your region. Defaults to layer for US-EAST-1
        :param layers: Any additional Lambda layers to use with the created function. For example Lambda Extensions
        :param object_prefix: The prefix to apply to the final S3 key name for the certificates. Default is no prefix.
        :param preferred_chain: Set the preferred certificate chain. Default: 'None'
        :param re_issue_days: The numbers of days left until the prior cert expires before issuing a new one. Default: 30
        :param removal_policy: The removal policy for the S3 bucket that is automatically created. Has no effect if a bucket is given as a property Default: RemovalPolicy.RETAIN
        :param run_on_deploy: Whether or not to schedule a trigger to run the function after each deployment. Default: true
        :param run_on_deploy_wait_minutes: How many minutes to wait before running the post deployment Lambda trigger. Default: 10
        :param schedule: The schedule for the certificate check trigger. Default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        :param sns_topic: The SNS topic to notify when a new cert is issued. If no topic is given one will be created automatically.
        :param timeout: The timeout duration for Lambda function. Default: Duraction.seconds(180)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone_names": hosted_zone_names,
            "letsencrypt_domains": letsencrypt_domains,
            "letsencrypt_email": letsencrypt_email,
        }
        if bucket is not None:
            self._values["bucket"] = bucket
        if enable_insights is not None:
            self._values["enable_insights"] = enable_insights
        if enable_object_deletion is not None:
            self._values["enable_object_deletion"] = enable_object_deletion
        if function_description is not None:
            self._values["function_description"] = function_description
        if function_name is not None:
            self._values["function_name"] = function_name
        if insights_arn is not None:
            self._values["insights_arn"] = insights_arn
        if layers is not None:
            self._values["layers"] = layers
        if object_prefix is not None:
            self._values["object_prefix"] = object_prefix
        if preferred_chain is not None:
            self._values["preferred_chain"] = preferred_chain
        if re_issue_days is not None:
            self._values["re_issue_days"] = re_issue_days
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if run_on_deploy is not None:
            self._values["run_on_deploy"] = run_on_deploy
        if run_on_deploy_wait_minutes is not None:
            self._values["run_on_deploy_wait_minutes"] = run_on_deploy_wait_minutes
        if schedule is not None:
            self._values["schedule"] = schedule
        if sns_topic is not None:
            self._values["sns_topic"] = sns_topic
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def hosted_zone_names(self) -> typing.List[builtins.str]:
        '''Hosted zone names that will be required for DNS verification with certbot.'''
        result = self._values.get("hosted_zone_names")
        assert result is not None, "Required property 'hosted_zone_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def letsencrypt_domains(self) -> builtins.str:
        '''The comma delimited list of domains for which the Let's Encrypt certificate will be valid.

        Primary domain should be first.
        '''
        result = self._values.get("letsencrypt_domains")
        assert result is not None, "Required property 'letsencrypt_domains' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def letsencrypt_email(self) -> builtins.str:
        '''The email to associate with the Let's Encrypt certificate request.'''
        result = self._values.get("letsencrypt_email")
        assert result is not None, "Required property 'letsencrypt_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        '''The S3 bucket to place the resulting certificates in.

        If no bucket is given one will be created automatically.
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], result)

    @builtins.property
    def enable_insights(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable Lambda Insights.

        :default: false
        '''
        result = self._values.get("enable_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_object_deletion(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable automatic object deletion if the provided bucket is deleted.

        Has no effect if a bucket is given as a property

        :default: false
        '''
        result = self._values.get("enable_object_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def function_description(self) -> typing.Optional[builtins.str]:
        '''The description for the resulting Lambda function.'''
        result = self._values.get("function_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''The name of the resulting Lambda function.'''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insights_arn(self) -> typing.Optional[builtins.str]:
        '''Insights layer ARN for your region.

        Defaults to layer for US-EAST-1
        '''
        result = self._values.get("insights_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def layers(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]]:
        '''Any additional Lambda layers to use with the created function.

        For example Lambda Extensions
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]], result)

    @builtins.property
    def object_prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix to apply to the final S3 key name for the certificates.

        Default is no prefix.
        '''
        result = self._values.get("object_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_chain(self) -> typing.Optional[builtins.str]:
        '''Set the preferred certificate chain.

        :default: 'None'
        '''
        result = self._values.get("preferred_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def re_issue_days(self) -> typing.Optional[jsii.Number]:
        '''The numbers of days left until the prior cert expires before issuing a new one.

        :default: 30
        '''
        result = self._values.get("re_issue_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''The removal policy for the S3 bucket that is automatically created.

        Has no effect if a bucket is given as a property

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def run_on_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to schedule a trigger to run the function after each deployment.

        :default: true
        '''
        result = self._values.get("run_on_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def run_on_deploy_wait_minutes(self) -> typing.Optional[jsii.Number]:
        '''How many minutes to wait before running the post deployment Lambda trigger.

        :default: 10
        '''
        result = self._values.get("run_on_deploy_wait_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''The schedule for the certificate check trigger.

        :default: events.Schedule.cron({ minute: '0', hour: '0', weekDay: '1' })
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    @builtins.property
    def sns_topic(self) -> typing.Optional[aws_cdk.aws_sns.Topic]:
        '''The SNS topic to notify when a new cert is issued.

        If no topic is given one will be created automatically.
        '''
        result = self._values.get("sns_topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.Topic], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The timeout duration for Lambda function.

        :default: Duraction.seconds(180)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Certbot",
    "CertbotProps",
]

publication.publish()
